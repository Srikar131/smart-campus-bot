"""RAG pipeline: text extraction, chunking, embeddings, retrieval, generation."""
import io
import logging
import uuid
from typing import AsyncIterator, Optional

import numpy as np
from openai import AsyncOpenAI
from pypdf import PdfReader
from docx import Document as DocxDocument

import config
import database as db

logger = logging.getLogger(__name__)

_client: Optional[AsyncOpenAI] = None


def client() -> AsyncOpenAI:
    """Lazily create and reuse a single OpenAI client."""
    global _client
    if not config.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set. Add it to backend/.env")
    if _client is None:
        _client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
    return _client


# --- Text extraction ---------------------------------------------------------

def extract_text(file_bytes: bytes, file_type: str) -> str:
    if file_type == "pdf":
        reader = PdfReader(io.BytesIO(file_bytes))
        return "\n".join((page.extract_text() or "") for page in reader.pages).strip()
    if file_type == "docx":
        doc = DocxDocument(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs).strip()
    raise ValueError(f"Unsupported file type: {file_type}")


def chunk_text(text: str) -> list[str]:
    """Split text into overlapping word windows."""
    words = text.split()
    if not words:
        return []
    size, overlap = config.CHUNK_SIZE, config.CHUNK_OVERLAP
    step = max(1, size - overlap)
    chunks = []
    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i + size]).strip()
        if chunk:
            chunks.append(chunk)
        if i + size >= len(words):
            break
    return chunks


# --- Embeddings --------------------------------------------------------------

async def embed_texts(texts: list[str]) -> np.ndarray:
    """Return an (N, D) float32 matrix of L2-normalized embeddings."""
    vectors: list[list[float]] = []
    for start in range(0, len(texts), config.EMBED_BATCH):
        batch = texts[start:start + config.EMBED_BATCH]
        resp = await client().embeddings.create(model=config.EMBEDDING_MODEL, input=batch)
        vectors.extend(item.embedding for item in resp.data)
    arr = np.asarray(vectors, dtype="float32")
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return arr / norms


# --- In-memory vector store (backed by SQLite) -------------------------------

class VectorStore:
    """Brute-force cosine search over normalized embeddings held in memory."""

    def __init__(self) -> None:
        self.matrix: Optional[np.ndarray] = None   # (N, D) normalized
        self.meta: list[dict] = []                 # parallel: filename, content, doc_id

    async def load(self) -> None:
        rows = await db.all_chunks()
        self.meta = []
        vecs = []
        for r in rows:
            vecs.append(np.frombuffer(r["embedding"], dtype="float32"))
            self.meta.append({
                "doc_id": r["doc_id"],
                "filename": r["filename"],
                "content": r["content"],
            })
        self.matrix = np.vstack(vecs).astype("float32") if vecs else None
        logger.info("Vector store loaded: %d chunks", len(self.meta))

    @property
    def size(self) -> int:
        return len(self.meta)

    async def add_document(self, doc_id: str, filename: str, chunks: list[str]) -> None:
        embeddings = await embed_texts(chunks)
        rows = [
            (str(uuid.uuid4()), doc_id, idx, chunk, embeddings[idx].tobytes())
            for idx, chunk in enumerate(chunks)
        ]
        await db.insert_chunks(rows)
        # Reload to keep memory and disk perfectly in sync.
        await self.load()

    async def remove_document(self, doc_id: str) -> None:
        await self.load()

    def search(self, query_vec: np.ndarray, k: int) -> list[dict]:
        if self.matrix is None or self.size == 0:
            return []
        scores = self.matrix @ query_vec
        k = min(k, len(scores))
        top = np.argpartition(-scores, k - 1)[:k]
        top = top[np.argsort(-scores[top])]
        return [{**self.meta[i], "score": float(scores[i])} for i in top]


store = VectorStore()


# --- Generation --------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are Smart Campus Bot, an AI assistant for an academic institution. "
    "You answer questions for students, faculty, and staff using the provided "
    "document context. Ground every answer in the context. If the answer is not "
    "present in the context, say so clearly and do not invent facts. "
    "Use concise, well-structured Markdown."
)


def _build_prompt(query: str, contexts: list[dict]) -> str:
    blocks = []
    for i, c in enumerate(contexts, 1):
        blocks.append(f"[Source {i}: {c['filename']}]\n{c['content']}")
    context = "\n\n".join(blocks) if blocks else "(no relevant context found)"
    return (
        f"Context from institutional documents:\n\n{context}\n\n"
        f"Question: {query}\n\n"
        "Answer using only the context above. Cite source filenames where relevant."
    )


async def retrieve(query: str) -> list[dict]:
    if store.size == 0:
        return []
    qvec = (await embed_texts([query]))[0]
    return store.search(qvec, config.TOP_K)


async def stream_answer(query: str, contexts: list[dict]) -> AsyncIterator[str]:
    """Yield answer tokens from the chat model as they arrive."""
    stream = await client().chat.completions.create(
        model=config.CHAT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_prompt(query, contexts)},
        ],
        temperature=0.2,
        stream=True,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
