# Smart Campus Bot 🎓

An AI-powered assistant for academic institutions. Upload your campus documents (PDF / DOCX) and ask questions in natural language — the bot retrieves the most relevant passages and generates grounded, cited answers using **Retrieval-Augmented Generation (RAG)**.

Built with a **React** frontend and a **FastAPI** backend on a deliberately lightweight stack: no MongoDB, no GPU, no multi-gigabyte ML downloads.

---

## ✨ Features

- **Document upload** — PDF and DOCX, with drag-and-drop and a 50 MB limit
- **Grounded Q&A** — answers are generated only from your documents, with source citations
- **Streaming responses** — answers appear token-by-token as they're generated
- **Markdown rendering** — lists, tables, code, and emphasis render cleanly
- **Persistent chat** — your session and history survive page reloads
- **Light / dark mode** — modern, responsive interface
- **Zero-install storage** — everything persists to a local SQLite file

---

## 🏗 Architecture

```
┌──────────────┐      ┌──────────────────┐      ┌──────────────┐
│ React (3000) │ ───▶ │ FastAPI (8000)   │ ───▶ │ SQLite file  │
│  streaming   │ ◀─── │  RAG pipeline    │      │ docs+vectors │
└──────────────┘      └────────┬─────────┘      └──────────────┘
                               │
                               ▼
                      ┌──────────────────┐
                      │ OpenAI API       │
                      │ embeddings + chat│
                      └──────────────────┘
```

### RAG pipeline

1. **Upload** → text is extracted from the PDF/DOCX
2. **Chunk** → text is split into overlapping word windows (500 words, 60 overlap)
3. **Embed** → each chunk is embedded via OpenAI `text-embedding-3-small`
4. **Store** → chunks + embeddings are saved to SQLite and held in memory
5. **Retrieve** → the question is embedded and matched by cosine similarity (top-k)
6. **Generate** → retrieved context + question are sent to `gpt-4o-mini`, streamed back with citations

> Why no FAISS / Sentence-Transformers? Since OpenAI already provides embeddings, an
> in-memory cosine search over a normalized matrix is instant at campus-document scale and
> removes ~2 GB of native/ML dependencies — making the app trivial to install on any machine.

---

## 🛠 Tech Stack

| Layer    | Technology |
|----------|------------|
| Frontend | React 18, Tailwind CSS, lucide-react, react-markdown, sonner |
| Backend  | FastAPI, Uvicorn, Pydantic |
| Storage  | SQLite (via aiosqlite) |
| Docs     | pypdf, python-docx |
| AI       | OpenAI (`text-embedding-3-small`, `gpt-4o-mini`), NumPy |

---

## 📦 Prerequisites

| Software | Version |
|----------|---------|
| Node.js  | 18+     |
| Python   | 3.10+   |
| OpenAI API key | with a small amount of credit |

No database server and no GPU required.

---

## 🚀 Setup

### 1. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# Configure your API key
copy .env.example .env                # macOS/Linux: cp .env.example .env
# then edit .env and set OPENAI_API_KEY
```

### 2. Frontend

```powershell
cd frontend
npm install
```

---

## ▶️ Running

**Terminal 1 — backend**
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn server:app --reload --port 8000
```

**Terminal 2 — frontend**
```powershell
cd frontend
npm start
```

Then open **http://localhost:3000**. API docs are at **http://localhost:8000/docs**.

> The frontend dev server proxies `/api` to the backend (see `proxy` in `package.json`),
> so no extra configuration is needed locally. For a production build, set
> `REACT_APP_BACKEND_URL` to your deployed backend origin.

---

## ⚙️ Configuration (`backend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ✅ | — | Your OpenAI API key |
| `CHAT_MODEL` | | `gpt-4o-mini` | Chat completion model |
| `EMBEDDING_MODEL` | | `text-embedding-3-small` | Embedding model |
| `CORS_ORIGINS` | | `http://localhost:3000` | Comma-separated allowed origins |
| `MAX_UPLOAD_MB` | | `50` | Max upload size |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` / `TOP_K` | | `500` / `60` / `4` | RAG tuning |

---

## 🔌 API Endpoints

Base URL: `http://localhost:8000/api`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/` | Health check + status |
| POST   | `/documents/upload` | Upload a PDF or DOCX |
| GET    | `/documents` | List documents |
| DELETE | `/documents/{doc_id}` | Delete a document |
| POST   | `/chat` | Ask a question (streams Server-Sent Events) |
| GET    | `/chat/history/{session_id}` | Get chat history |
| DELETE | `/chat/history/{session_id}` | Clear chat history |

---

## 🔧 Troubleshooting

| Symptom | Fix |
|---------|-----|
| `OPENAI_API_KEY is not set` | Create `backend/.env` from `.env.example` and add your key |
| Billing / quota error | Add credits at https://platform.openai.com/account/billing |
| Frontend can't reach backend | Ensure the backend is running on port 8000 |
| Port 8000 in use | `netstat -ano \| findstr :8000` then `taskkill /PID <PID> /F` |

---

## 🔒 Security Notes

- Never commit `backend/.env` — it's already in `.gitignore`
- This build has no authentication; add access control before any public deployment
- `CORS_ORIGINS` defaults to localhost only — set it explicitly in production

---

**Happy Learning! 🎓**
