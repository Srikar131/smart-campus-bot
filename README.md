# Smart Campus Bot 🎓

An intelligent AI-powered chatbot for academic institutions that allows users to upload documents and ask questions about their content. Built with **React** frontend and **FastAPI** backend, utilizing **RAG (Retrieval-Augmented Generation)** architecture for accurate, context-aware responses.

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture Overview](#-architecture-overview)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [Usage Guide](#-usage-guide)
- [API Endpoints](#-api-endpoints)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Features

- **Document Upload**: Upload PDF and DOCX files for processing
- **Intelligent Q&A**: Ask questions about uploaded documents and get AI-powered answers
- **Source Citations**: Responses include references to source documents
- **Dark/Light Mode**: Toggle between themes for comfortable viewing
- **Chat History**: Conversation history is maintained per session
- **Real-time Processing**: Documents are chunked and indexed for fast retrieval
- **Modern UI**: Beautiful, responsive interface with glassmorphism effects

---

## 🏗 Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  React Frontend │────▶│  FastAPI Server │────▶│    MongoDB      │
│  (Port 3000)    │     │  (Port 8000)    │     │  (Port 27017)   │
│                 │     │                 │     │                 │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
                    ▼            ▼            ▼
              ┌──────────┐ ┌──────────┐ ┌──────────┐
              │  FAISS   │ │ Sentence │ │  OpenAI  │
              │  Vector  │ │Transformer│ │  GPT-4o  │
              │  Store   │ │ Embeddings│ │   API    │
              └──────────┘ └──────────┘ └──────────┘
```

### How It Works (RAG Pipeline)

1. **Document Upload**: User uploads PDF/DOCX files
2. **Text Extraction**: Text is extracted from documents
3. **Chunking**: Text is split into smaller overlapping chunks (500 words, 50 word overlap)
4. **Embedding**: Each chunk is converted to a vector using Sentence Transformers
5. **Indexing**: Vectors are stored in FAISS for fast similarity search
6. **Query Processing**: User question is converted to a vector
7. **Retrieval**: Most similar document chunks are retrieved from FAISS
8. **Generation**: Retrieved context + question is sent to GPT-4o for answer generation
9. **Response**: AI-generated answer with source citations is returned

---

## 🛠 Tech Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| React 18 | UI Framework |
| Tailwind CSS | Styling |
| Lucide React | Icons |
| Sonner | Toast Notifications |
| UUID | Session ID Generation |

### Backend
| Technology | Purpose |
|------------|---------|
| FastAPI | Web Framework |
| Uvicorn | ASGI Server |
| Motor | Async MongoDB Driver |
| PyPDF2 | PDF Text Extraction |
| python-docx | DOCX Text Extraction |
| Sentence Transformers | Text Embeddings (all-MiniLM-L6-v2) |
| FAISS | Vector Similarity Search |
| OpenAI API | GPT-4o for Response Generation |
| Pydantic | Data Validation |

### Database
| Technology | Purpose |
|------------|---------|
| MongoDB | Document Storage, Chat History |

---

## 📦 Prerequisites

Before running this application, ensure you have the following installed:

### Required Software

| Software | Version | Download Link |
|----------|---------|---------------|
| **Node.js** | 18.x or higher | https://nodejs.org/ |
| **Python** | 3.10 or higher | https://python.org/ |
| **MongoDB** | 6.0 or higher | https://www.mongodb.com/try/download/community |
| **Git** | Latest | https://git-scm.com/ |

### Required Accounts

| Service | Purpose | Sign Up |
|---------|---------|---------|
| **OpenAI** | GPT-4o API Access | https://platform.openai.com/ |

### System Requirements

- **RAM**: Minimum 8GB (16GB recommended)
- **Storage**: At least 5GB free space
- **OS**: Windows 10/11, macOS, or Linux

---

## 📁 Project Structure

```
smart-campus-bot/
├── backend/                    # FastAPI Backend
│   ├── server.py              # Main server file with all API endpoints
│   ├── requirements.txt       # Python dependencies
│   ├── requirements_local.txt # Clean local dependencies
│   ├── .env                   # Environment variables (create this)
│   └── __pycache__/           # Python cache (auto-generated)
│
├── frontend/                   # React Frontend
│   ├── public/
│   │   └── index.html         # HTML template
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/            # Reusable UI components
│   │   │   │   ├── button.jsx
│   │   │   │   ├── card.jsx
│   │   │   │   └── input.jsx
│   │   │   ├── ChatInterface.jsx    # Chat UI component
│   │   │   ├── DocumentManager.jsx  # Document upload/manage component
│   │   │   └── Sidebar.jsx          # Navigation sidebar
│   │   ├── lib/
│   │   │   └── utils.js       # Utility functions
│   │   ├── App.js             # Main React component
│   │   ├── index.js           # React entry point
│   │   └── index.css          # Global styles with Tailwind
│   ├── package.json           # Node.js dependencies
│   ├── tailwind.config.js     # Tailwind CSS configuration
│   ├── postcss.config.js      # PostCSS configuration
│   ├── craco.config.js        # Create React App configuration override
│   └── .env                   # Frontend environment variables
│
├── tests/                      # Test files
├── test_reports/              # Test result reports
├── .venv/                     # Python virtual environment
└── README.md                  # This file
```

---

## 🚀 Installation

### Step 1: Clone or Navigate to Project

```bash
cd "C:\Users\YourUsername\Downloads\smart campus bot"
```

### Step 2: Set Up Python Virtual Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate virtual environment (Windows CMD)
.\.venv\Scripts\activate.bat

# Activate virtual environment (macOS/Linux)
source .venv/bin/activate
```

### Step 3: Install Backend Dependencies

```powershell
# Navigate to backend folder
cd backend

# Install dependencies
pip install -r requirements_local.txt

# Or install manually
pip install fastapi uvicorn python-dotenv python-multipart motor pymongo PyPDF2 python-docx openai sentence-transformers faiss-cpu numpy pydantic
```

### Step 4: Install Frontend Dependencies

```powershell
# Navigate to frontend folder
cd ..\frontend

# Install dependencies
npm install
```

---

## ⚙️ Configuration

### Backend Configuration

Create or edit the file `backend/.env`:

```env
# MongoDB Connection
MONGO_URL="mongodb://localhost:27017"
DB_NAME="smart_campus_bot"

# CORS Settings
CORS_ORIGINS="*"

# OpenAI API Key (Required)
OPENAI_API_KEY="sk-proj-your-api-key-here"
```

### Getting Your OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Click **"Create new secret key"**
3. Copy the key (starts with `sk-...`)
4. **Important**: Add billing/credits at https://platform.openai.com/account/billing
5. Paste the key in `backend/.env`

### Frontend Configuration (Optional)

The frontend `.env` file is pre-configured for local development:

```env
REACT_APP_BACKEND_URL=http://localhost:8000
```

---

## ▶️ Running the Application

### Step 1: Start MongoDB

MongoDB should run automatically as a Windows service after installation. Verify it's running:

```powershell
# Check MongoDB service status
Get-Service MongoDB

# If not running, start it
Start-Service MongoDB
```

Expected output:
```
Status   Name               DisplayName
------   ----               -----------
Running  MongoDB            MongoDB Server (MongoDB)
```

### Step 2: Start the Backend Server

Open a new terminal:

```powershell
# Navigate to project root
cd "C:\Users\YourUsername\Downloads\smart campus bot"

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Navigate to backend
cd backend

# Start the server
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process using StatReload
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Smart Campus Bot started successfully
INFO:     Application startup complete.
```

### Step 3: Start the Frontend Server

Open another new terminal:

```powershell
# Navigate to frontend
cd "C:\Users\YourUsername\Downloads\smart campus bot\frontend"

# Start the development server
npm start
```

Expected output:
```
Compiled successfully!

You can now view smart-campus-bot in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

### Step 4: Access the Application

Open your browser and go to:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## 📖 Usage Guide

### Uploading Documents

1. Click **"DOCUMENTS"** in the sidebar
2. Drag and drop PDF or DOCX files into the upload area
   - Or click the upload area to browse files
3. Wait for processing (documents are chunked and indexed)
4. You'll see the document appear in the list with chunk count

### Chatting with Documents

1. Click **"CHAT"** in the sidebar
2. Type your question in the input field
3. Press Enter or click the send button
4. The bot will:
   - Search for relevant document chunks
   - Generate an answer using GPT-4o
   - Display the response with source citations

### Managing Documents

- **View Documents**: Go to Documents tab to see all uploaded files
- **Delete Documents**: Click the trash icon on any document to remove it
- **Stats**: View total document and chunk counts

### Theme Toggle

- Click **"LIGHT MODE"** / **"DARK MODE"** button at the bottom of the sidebar

---

## 🔌 API Endpoints

### Base URL: `http://localhost:8000/api`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/documents/upload` | Upload a PDF or DOCX file |
| GET | `/documents` | List all uploaded documents |
| DELETE | `/documents/{doc_id}` | Delete a specific document |
| POST | `/chat` | Send a chat message |
| GET | `/chat/history/{session_id}` | Get chat history for a session |

### Example API Calls

#### Upload Document
```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

#### Send Chat Message
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this document about?", "session_id": "your-session-id"}'
```

#### List Documents
```bash
curl "http://localhost:8000/api/documents"
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. "MongoDB connection failed"
```
Error: ServerSelectionTimeoutError
```
**Solution:**
- Ensure MongoDB is installed and running
- Run `Get-Service MongoDB` to check status
- Run `Start-Service MongoDB` if stopped

#### 2. "OpenAI API billing issue"
```
Error: You exceeded your current quota
```
**Solution:**
- Go to https://platform.openai.com/account/billing
- Add a payment method
- Add credits to your account

#### 3. "Invalid API key"
```
Error: Incorrect API key provided
```
**Solution:**
- Check your API key in `backend/.env`
- Ensure there are no extra spaces or quotes
- Generate a new key if needed

#### 4. "Module not found" (Python)
```
ModuleNotFoundError: No module named 'xxx'
```
**Solution:**
```powershell
# Activate virtual environment first
.\.venv\Scripts\Activate.ps1

# Install missing module
pip install xxx
```

#### 5. "npm start fails"
```
Error: Cannot find module
```
**Solution:**
```powershell
cd frontend
rm -r node_modules
npm install
npm start
```

#### 6. "Port already in use"
```
Error: Address already in use :::8000
```
**Solution:**
```powershell
# Find process using the port
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

#### 7. "CORS error in browser"
```
Access to fetch has been blocked by CORS policy
```
**Solution:**
- Ensure backend is running on port 8000
- Check `CORS_ORIGINS="*"` is set in `backend/.env`
- Restart the backend server

---

## 🛑 Stopping the Application

1. **Stop Frontend**: Press `Ctrl+C` in the frontend terminal
2. **Stop Backend**: Press `Ctrl+C` in the backend terminal
3. **Stop MongoDB** (optional): `Stop-Service MongoDB`

---

## 📝 Environment Variables Reference

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MONGO_URL` | Yes | `mongodb://localhost:27017` | MongoDB connection string |
| `DB_NAME` | Yes | `smart_campus_bot` | Database name |
| `CORS_ORIGINS` | No | `*` | Allowed CORS origins |
| `OPENAI_API_KEY` | Yes | - | Your OpenAI API key |

---

## 🔒 Security Notes

- **Never commit** your `.env` file with API keys to version control
- Add `.env` to your `.gitignore` file
- Use environment-specific keys for development and production
- Rotate API keys periodically

---

## 📄 License

This project is for educational and demonstration purposes.

---

## 🤝 Support

If you encounter any issues:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Ensure all prerequisites are installed
3. Verify your API key has credits
4. Check that all services (MongoDB, Backend, Frontend) are running

---

**Happy Learning! 🎓**
