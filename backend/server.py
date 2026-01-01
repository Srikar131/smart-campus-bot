from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import PyPDF2
from docx import Document
import io
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from openai import AsyncOpenAI
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize sentence transformer model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Global FAISS index and document chunks
faiss_index = None
document_chunks = []
chunk_metadata = []  # Store doc_id and chunk_index for each vector

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class DocumentModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    file_type: str
    upload_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    text_content: str
    chunk_count: int

class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    upload_date: str
    chunk_count: int

class ChatMessageModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    role: str  # 'user' or 'assistant'
    content: str
    sources: Optional[List[str]] = []
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatRequest(BaseModel):
    query: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    sources: List[str]

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logging.error(f"Error extracting PDF text: {e}")
        raise HTTPException(status_code=400, detail="Failed to extract text from PDF")

def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file"""
    try:
        docx_file = io.BytesIO(file_content)
        doc = Document(docx_file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        logging.error(f"Error extracting DOCX text: {e}")
        raise HTTPException(status_code=400, detail="Failed to extract text from DOCX")

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into semantic chunks with overlap"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    
    return chunks

def rebuild_faiss_index():
    """Rebuild FAISS index from document chunks"""
    global faiss_index, document_chunks, chunk_metadata
    
    if len(document_chunks) == 0:
        faiss_index = None
        return
    
    # Generate embeddings for all chunks
    embeddings = embedding_model.encode(document_chunks, show_progress_bar=False)
    embeddings = np.array(embeddings).astype('float32')
    
    # Create FAISS index
    dimension = embeddings.shape[1]
    faiss_index = faiss.IndexFlatL2(dimension)
    faiss_index.add(embeddings)

async def load_documents_on_startup():
    """Load all documents from DB and rebuild FAISS index on startup"""
    global document_chunks, chunk_metadata
    
    try:
        documents = await db.documents.find({}, {"_id": 0}).to_list(1000)
        
        for doc in documents:
            text_content = doc.get('text_content', '')
            doc_id = doc.get('id')
            chunks = chunk_text(text_content)
            
            for idx, chunk in enumerate(chunks):
                document_chunks.append(chunk)
                chunk_metadata.append({'doc_id': doc_id, 'chunk_index': idx, 'filename': doc.get('filename')})
        
        if document_chunks:
            rebuild_faiss_index()
            logging.info(f"Loaded {len(documents)} documents with {len(document_chunks)} chunks")
    except Exception as e:
        logging.error(f"Error loading documents: {e}")

@api_router.get("/")
async def root():
    return {"message": "Smart Campus Bot API"}

@api_router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process PDF or DOCX document"""
    global document_chunks, chunk_metadata
    
    # Validate file type
    allowed_types = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Extract text based on file type
        if file.content_type == 'application/pdf':
            text = extract_text_from_pdf(file_content)
            file_type = 'pdf'
        else:
            text = extract_text_from_docx(file_content)
            file_type = 'docx'
        
        if not text:
            raise HTTPException(status_code=400, detail="No text content found in document")
        
        # Create chunks
        chunks = chunk_text(text)
        
        # Create document model
        doc = DocumentModel(
            filename=file.filename,
            file_type=file_type,
            text_content=text,
            chunk_count=len(chunks)
        )
        
        # Save to database
        doc_dict = doc.model_dump()
        doc_dict['upload_date'] = doc_dict['upload_date'].isoformat()
        await db.documents.insert_one(doc_dict)
        
        # Add chunks to global list and rebuild index
        for idx, chunk in enumerate(chunks):
            document_chunks.append(chunk)
            chunk_metadata.append({'doc_id': doc.id, 'chunk_index': idx, 'filename': file.filename})
        
        rebuild_faiss_index()
        
        return {
            "id": doc.id,
            "filename": doc.filename,
            "file_type": doc.file_type,
            "chunk_count": len(chunks),
            "upload_date": doc.upload_date.isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/documents", response_model=List[DocumentResponse])
async def get_documents():
    """Get all uploaded documents"""
    try:
        documents = await db.documents.find({}, {"_id": 0, "text_content": 0}).to_list(1000)
        
        # Convert datetime strings if needed
        for doc in documents:
            if isinstance(doc.get('upload_date'), str):
                doc['upload_date'] = doc['upload_date']
            else:
                doc['upload_date'] = doc.get('upload_date', datetime.now(timezone.utc)).isoformat()
        
        return documents
    except Exception as e:
        logging.error(f"Error fetching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document and rebuild FAISS index"""
    global document_chunks, chunk_metadata
    
    try:
        # Delete from database
        result = await db.documents.delete_one({"id": doc_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Remove chunks from global lists
        indices_to_remove = [i for i, meta in enumerate(chunk_metadata) if meta['doc_id'] == doc_id]
        
        for idx in sorted(indices_to_remove, reverse=True):
            del document_chunks[idx]
            del chunk_metadata[idx]
        
        # Rebuild FAISS index
        rebuild_faiss_index()
        
        return {"message": "Document deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat query using RAG"""
    try:
        query = request.query
        session_id = request.session_id
        
        # Check if we have documents
        if faiss_index is None or len(document_chunks) == 0:
            return ChatResponse(
                response="I don't have any documents to search through yet. Please upload some documents first.",
                sources=[]
            )
        
        # Generate query embedding
        query_embedding = embedding_model.encode([query])[0].astype('float32')
        
        # Search FAISS index for top 3 relevant chunks
        k = min(3, len(document_chunks))
        distances, indices = faiss_index.search(np.array([query_embedding]), k)
        
        # Get relevant chunks and sources
        context_chunks = []
        sources = set()
        
        for idx in indices[0]:
            if idx < len(document_chunks):
                context_chunks.append(document_chunks[idx])
                sources.add(chunk_metadata[idx]['filename'])
        
        context = "\n\n".join(context_chunks)
        sources_list = list(sources)
        
        # Get OpenAI API key
        openai_key = os.environ.get('OPENAI_API_KEY')
        if not openai_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        # Generate response using LLM
        system_message = """You are a Smart Campus Bot, an AI assistant for academic institutions. 
You help students, faculty, and administrators find information from institutional documents.
Use the provided context to answer questions accurately. If the answer is not in the context, say so.
Always cite the source documents when providing information."""
        
        user_prompt = f"""Context from documents:
{context}

Question: {query}

Provide a clear, accurate answer based on the context above. If the information is not in the context, politely say so."""
        
        # Initialize OpenAI client
        client = AsyncOpenAI(api_key=openai_key)
        
        # Send message to GPT-4o
        completion = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ]
        )
        response_text = completion.choices[0].message.content
        
        # Save user message to database
        user_msg = ChatMessageModel(
            session_id=session_id,
            role="user",
            content=query,
            sources=[]
        )
        user_msg_dict = user_msg.model_dump()
        user_msg_dict['timestamp'] = user_msg_dict['timestamp'].isoformat()
        await db.chat_messages.insert_one(user_msg_dict)
        
        # Save assistant message to database
        assistant_msg = ChatMessageModel(
            session_id=session_id,
            role="assistant",
            content=response_text,
            sources=sources_list
        )
        assistant_msg_dict = assistant_msg.model_dump()
        assistant_msg_dict['timestamp'] = assistant_msg_dict['timestamp'].isoformat()
        await db.chat_messages.insert_one(assistant_msg_dict)
        
        return ChatResponse(
            response=response_text,
            sources=sources_list
        )
    
    except HTTPException:
        raise
    except Exception as e:
        error_str = str(e).lower()
        logging.error(f"Error processing chat: {e}")
        
        # Check for OpenAI billing/quota errors
        if 'insufficient_quota' in error_str or 'billing' in error_str or 'exceeded' in error_str or 'quota' in error_str:
            raise HTTPException(
                status_code=402, 
                detail="OpenAI API billing issue: Your API key has insufficient quota. Please add credits at https://platform.openai.com/account/billing"
            )
        elif 'invalid_api_key' in error_str or 'incorrect api key' in error_str:
            raise HTTPException(
                status_code=401, 
                detail="Invalid OpenAI API key. Please check your OPENAI_API_KEY in the .env file."
            )
        elif 'rate_limit' in error_str or 'rate limit' in error_str:
            raise HTTPException(
                status_code=429, 
                detail="Rate limit exceeded. Please wait a moment and try again."
            )
        
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    try:
        messages = await db.chat_messages.find(
            {"session_id": session_id},
            {"_id": 0}
        ).sort("timestamp", 1).to_list(1000)
        
        return messages
    except Exception as e:
        logging.error(f"Error fetching chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    await load_documents_on_startup()
    logger.info("Smart Campus Bot started successfully")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()