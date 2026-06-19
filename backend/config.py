"""Application configuration loaded from environment variables."""
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

# --- OpenAI ---
OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "").strip()
CHAT_MODEL: str = os.environ.get("CHAT_MODEL", "gpt-4o-mini").strip()
EMBEDDING_MODEL: str = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small").strip()

# --- Storage ---
DATA_DIR = Path(os.environ.get("DATA_DIR", ROOT_DIR / "data"))
DB_PATH = DATA_DIR / "campus_bot.db"

# --- Server ---
CORS_ORIGINS = [
    o.strip()
    for o in os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
    if o.strip()
]

# --- RAG tuning ---
CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "500"))          # words per chunk
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", "60"))     # words of overlap
TOP_K = int(os.environ.get("TOP_K", "4"))                      # chunks retrieved per query
EMBED_BATCH = int(os.environ.get("EMBED_BATCH", "96"))         # texts per embedding request

# --- Limits ---
MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", "50"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024

DATA_DIR.mkdir(parents=True, exist_ok=True)
