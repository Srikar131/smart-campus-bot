"""Smart Campus Bot — FastAPI backend (SQLite + OpenAI RAG, streaming)."""
import json
import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import config
import database as db
import rag

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("smart_campus_bot")


@asynccontextmanager
async def lifespan(_: FastAPI):
    await db.connect()
    await rag.store.load()
    if not config.OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY is not set — chat and uploads will fail.")
    logger.info("Smart Campus Bot started (model=%s, chunks=%d)",
                config.CHAT_MODEL, rag.store.size)
    yield
    await db.close()
    logger.info("Smart Campus Bot stopped")


app = FastAPI(title="Smart Campus Bot", version="2.0.0", lifespan=lifespan)
api = APIRouter(prefix="/api")


# --- Schemas -----------------------------------------------------------------

class ChatRequest(BaseModel):
    query: str
    session_id: str


# --- Routes ------------------------------------------------------------------

@api.get("/")
async def root():
    return {
        "message": "Smart Campus Bot API",
        "model": config.CHAT_MODEL,
        "documents_indexed": rag.store.size,
        "openai_configured": bool(config.OPENAI_API_KEY),
    }


ALLOWED = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
}


def _resolve_file_type(file: UploadFile) -> str | None:
    """Determine pdf/docx from MIME type, falling back to the filename extension."""
    ct = (file.content_type or "").lower()
    if ct in ALLOWED:
        return ALLOWED[ct]
    name = (file.filename or "").lower()
    if name.endswith(".pdf"):
        return "pdf"
    if name.endswith(".docx"):
        return "docx"
    return None


@api.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    file_type = _resolve_file_type(file)
    if not file_type:
        raise HTTPException(400, "Only PDF and DOCX files are supported.")

    content = await file.read()
    if len(content) > config.MAX_UPLOAD_BYTES:
        mb = len(content) / (1024 * 1024)
        raise HTTPException(
            413,
            f"This file is {mb:.1f} MB, over the {config.MAX_UPLOAD_MB} MB limit. "
            f"Increase MAX_UPLOAD_MB in backend/.env to allow larger files.",
        )

    try:
        text = rag.extract_text(content, file_type)
    except Exception as e:
        logger.error("Extraction failed for %s: %s", file.filename, e)
        raise HTTPException(400, f"Could not read text from this {file_type.upper()} file.")

    if not text.strip():
        hint = (
            " This PDF looks scanned/image-only — it has no selectable text, so it "
            "can't be indexed without OCR." if file_type == "pdf" else ""
        )
        raise HTTPException(400, "No readable text found in the document." + hint)

    chunks = rag.chunk_text(text)
    if not chunks:
        raise HTTPException(400, "Document produced no indexable content.")

    doc_id = str(uuid.uuid4())
    try:
        record = await db.insert_document(
            doc_id, file.filename, file_type, len(text), len(chunks)
        )
        await rag.store.add_document(doc_id, file.filename, chunks)
    except Exception as e:
        # Roll back the document row if embedding/indexing failed.
        await db.delete_document(doc_id)
        logger.error("Indexing failed for %s: %s", file.filename, e)
        raise HTTPException(502, _openai_message(e))

    return record


@api.get("/documents")
async def get_documents():
    return await db.list_documents()


@api.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    deleted = await db.delete_document(doc_id)
    if not deleted:
        raise HTTPException(404, "Document not found.")
    await rag.store.remove_document(doc_id)
    return {"message": "Document deleted", "id": doc_id}


@api.post("/chat")
async def chat(request: ChatRequest):
    query = request.query.strip()
    if not query:
        raise HTTPException(400, "Query cannot be empty.")

    async def event_stream():
        try:
            contexts = await rag.retrieve(query)
            sources = list(dict.fromkeys(c["filename"] for c in contexts))
            yield _sse("sources", {"sources": sources})

            if rag.store.size == 0:
                msg = ("I don't have any documents to search yet. "
                       "Upload a PDF or DOCX from the **Documents** tab to get started.")
                yield _sse("token", {"content": msg})
                await _persist(request.session_id, query, msg, [])
                yield _sse("done", {})
                return

            answer_parts = []
            async for token in rag.stream_answer(query, contexts):
                answer_parts.append(token)
                yield _sse("token", {"content": token})

            answer = "".join(answer_parts)
            await _persist(request.session_id, query, answer, sources)
            yield _sse("done", {})
        except Exception as e:
            logger.error("Chat error: %s", e)
            yield _sse("error", {"message": _openai_message(e)})

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@api.get("/chat/history/{session_id}")
async def get_history(session_id: str):
    return await db.get_history(session_id)


@api.delete("/chat/history/{session_id}")
async def clear_history(session_id: str):
    removed = await db.clear_history(session_id)
    return {"message": "History cleared", "removed": removed}


# --- Helpers -----------------------------------------------------------------

def _sse(event_type: str, data: dict) -> str:
    return f"data: {json.dumps({'type': event_type, **data})}\n\n"


async def _persist(session_id: str, query: str, answer: str, sources: list[str]) -> None:
    await db.insert_message(str(uuid.uuid4()), session_id, "user", query, [])
    await db.insert_message(str(uuid.uuid4()), session_id, "assistant", answer, sources)


def _openai_message(e: Exception) -> str:
    s = str(e).lower()
    if any(t in s for t in ("insufficient_quota", "billing", "exceeded", "quota")):
        return ("OpenAI billing issue: your API key has insufficient quota. "
                "Add credits at https://platform.openai.com/account/billing")
    if "invalid_api_key" in s or "incorrect api key" in s:
        return "Invalid OpenAI API key. Check OPENAI_API_KEY in backend/.env"
    if "rate" in s and "limit" in s:
        return "OpenAI rate limit reached. Please wait a moment and try again."
    if "openai_api_key is not set" in s:
        return "OpenAI API key is not configured. Add it to backend/.env"
    return f"Something went wrong: {e}"


app.include_router(api)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
