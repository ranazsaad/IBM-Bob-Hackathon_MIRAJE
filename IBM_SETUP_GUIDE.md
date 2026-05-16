# 🚀 IBM DevPilot AI - Complete Setup Guide

## 📋 Overview

DevPilot AI now uses **100% IBM stack** for the IBM Bob Hackathon:
- ✅ IBM watsonx.ai (Granite models)
- ✅ IBM Cloud APIs
- ✅ IBM Watson Speech-to-Text (optional)
- ✅ IBM Slate embeddings

**No OpenAI, No Cline, No external APIs - Pure IBM!**

---

## 🎯 Quick Start (20 Minutes)

### Prerequisites
- Python 3.12+
- Node.js 18+
- IBM Cloud account
- Git

### Step 1: Get IBM Credentials (15 minutes)

**Follow the detailed guide:** `IBM_CREDENTIALS_GUIDE.md`

**Quick checklist:**
- [ ] IBM Cloud API Key
- [ ] watsonx.ai Project ID
- [ ] watsonx.ai URL (based on region)
- [ ] Watson STT credentials (optional)

### Step 2: Clone & Configure (2 minutes)

```powershell
# Navigate to project
cd C:\Users\Janaa\Desktop\devpilot-ai

# Update backend/.env with your IBM credentials
# See IBM_CREDENTIALS_GUIDE.md for details
```

### Step 3: Install Dependencies (2 minutes)

**Backend:**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend:**
```powershell
cd frontend
npm install
```

### Step 4: Test & Run (1 minute)

```powershell
# Test IBM connection
cd backend
.\venv\Scripts\activate
python test_ibm_api.py

# Start backend
uvicorn app.main:app --reload --port 8000

# Start frontend (new terminal)
cd frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 📚 Detailed Setup

### 1. IBM Cloud Setup

#### 1.1 Create IBM Cloud Account

1. Go to https://cloud.ibm.com/registration
2. Sign up with email
3. Verify email
4. Complete profile

#### 1.2 Get IBM Cloud API Key

1. Log in to https://cloud.ibm.com
2. Click profile → **Profile and settings**
3. Go to **API keys**
4. Click **Create an IBM Cloud API key**
5. Name: "DevPilot AI Hackathon"
6. **Copy and save the key immediately!**

**Your key looks like:**
```
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### 1.3 Choose Region

**Available regions:**
- `us-south` (Dallas) - Recommended
- `us-east` (Washington DC)
- `eu-de` (Frankfurt)
- `eu-gb` (London)
- `jp-tok` (Tokyo)

**Use the same region for all services!**

---

### 2. watsonx.ai Setup

#### 2.1 Access watsonx.ai

1. Go to https://dataplatform.cloud.ibm.com
2. Sign in with IBM Cloud account
3. Accept terms if prompted

#### 2.2 Create Project

1. Click **"Create a project"** or **"New project"**
2. Select **"Create an empty project"**
3. **Name:** "DevPilot AI"
4. **Description:** "AI-powered developer workspace for IBM Hackathon"
5. **Storage:** Select or create Cloud Object Storage
6. Click **"Create"**

#### 2.3 Get Project ID

1. In your project, click **"Manage"** tab
2. Go to **"General"** section
3. **Copy the Project ID**

**Format:** `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

#### 2.4 Associate Watson Machine Learning

1. In project, go to **"Manage"** → **"Services & integrations"**
2. Click **"Associate service"**
3. Select **"Watson Machine Learning"**
4. Choose existing or create new
5. Click **"Associate"**

#### 2.5 Test Granite Models

1. In project, go to **"Prompt Lab"**
2. Select model: **"ibm/granite-3-8b-instruct"**
3. Enter test prompt: "Hello, how are you?"
4. Click **"Generate"**
5. Verify response

**If it works, you're ready!**

---

### 3. Watson Speech-to-Text (Optional)

#### 3.1 Create Service

1. Go to https://cloud.ibm.com/catalog/services/speech-to-text
2. **Select region:** Same as watsonx.ai
3. **Select plan:** Lite (free) or Standard
4. **Name:** "DevPilot STT"
5. Click **"Create"**

#### 3.2 Get Credentials

1. In service page, click **"Manage"**
2. **Copy:**
   - API Key
   - URL

**Save both values!**

---

### 4. Configure DevPilot AI

#### 4.1 Update .env File

**Open:** `C:\Users\Janaa\Desktop\devpilot-ai\backend\.env`

**Fill in your credentials:**

```env
# ============================================================
# IBM CLOUD CREDENTIALS — REQUIRED
# ============================================================
IBM_CLOUD_API_KEY=your_ibm_cloud_api_key_here
IBM_CLOUD_REGION=us-south

# ============================================================
# IBM WATSONX.AI — REQUIRED
# ============================================================
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Granite Model Configuration
WATSONX_MODEL_ID=ibm/granite-3-8b-instruct
WATSONX_EMBEDDING_MODEL=ibm/slate-125m-english-rtrvr

# Model Parameters
MAX_TOKENS=4096
TEMPERATURE=0.7
TOP_P=1.0
TOP_K=50
REPETITION_PENALTY=1.0

# ============================================================
# IBM WATSON SPEECH TO TEXT — OPTIONAL
# ============================================================
WATSON_STT_API_KEY=your_watson_stt_api_key_here
WATSON_STT_URL=https://api.us-south.speech-to-text.watson.cloud.ibm.com

# ============================================================
# DATABASE & SERVER — ALREADY CONFIGURED
# ============================================================
DATABASE_URL=sqlite:///./devpilot.db
CHROMA_PERSIST_DIRECTORY=./chroma_data
HOST=0.0.0.0
PORT=8000
RELOAD=true
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# ============================================================
# GITHUB — OPTIONAL
# ============================================================
GITHUB_TOKEN=

# ============================================================
# APPLICATION
# ============================================================
APP_NAME=DevPilot AI
APP_VERSION=1.0.0
DEBUG=true

# ============================================================
# RAG CONFIGURATION
# ============================================================
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=5
CACHE_TTL=3600
```

**⚠️ REQUIRED FIELDS:**
- `IBM_CLOUD_API_KEY`
- `WATSONX_PROJECT_ID`
- `WATSONX_URL`

**Optional fields:**
- `WATSON_STT_API_KEY` (for audio transcription)
- `WATSON_STT_URL`
- `GITHUB_TOKEN` (for higher rate limits)

#### 4.2 Verify Configuration

```powershell
cd C:\Users\Janaa\Desktop\devpilot-ai\backend
.\venv\Scripts\activate
python -c "from app.config import settings; print(f'IBM Key: {settings.IBM_CLOUD_API_KEY[:10]}...'); print(f'Project ID: {settings.WATSONX_PROJECT_ID[:8]}...'); print('Config OK!')"
```

**Expected output:**
```
IBM Key: xxxxxxxxxx...
Project ID: xxxxxxxx...
Config OK!
```

---

### 5. Install Dependencies

#### 5.1 Backend Dependencies

```powershell
cd C:\Users\Janaa\Desktop\devpilot-ai\backend

# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

**Key IBM packages installed:**
- `ibm-watson` - IBM Watson SDK
- `ibm-watsonx-ai` - watsonx.ai SDK
- `ibm-cloud-sdk-core` - IBM Cloud core SDK

**Other packages:**
- `fastapi` - Web framework
- `chromadb` - Vector database
- `langchain` - AI orchestration
- `sqlalchemy` - Database ORM

#### 5.2 Frontend Dependencies

```powershell
cd C:\Users\Janaa\Desktop\devpilot-ai\frontend

# Install dependencies
npm install

# Verify installation
npm list next react
```

---

### 6. Test IBM Integration

#### 6.1 Test IBM API Connection

```powershell
cd C:\Users\Janaa\Desktop\devpilot-ai\backend
.\venv\Scripts\activate
python test_ibm_api.py
```

**Expected output:**
```
============================================================
Testing IBM watsonx.ai Connection
============================================================

[OK] IBM Cloud API Key: xxxxxxxxxx...
[OK] Project ID: xxxxxxxx-xxxx-...
[OK] watsonx URL: https://us-south.ml.cloud.ibm.com
[OK] Model: ibm/granite-3-8b-instruct

[OK] IBM watsonx client created successfully

[...] Getting IAM access token...
[OK] Access token obtained

[...] Sending test request to Granite model...

[SUCCESS] IBM watsonx.ai is working!

[Response] Hello from DevPilot AI! I'm powered by IBM Granite.

============================================================
```

#### 6.2 Test Backend Startup

```powershell
cd C:\Users\Janaa\Desktop\devpilot-ai\backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Will watch for changes in these directories: ['C:\\Users\\Janaa\\Desktop\\devpilot-ai\\backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

#### 6.3 Test Health Endpoint

**Open browser:** http://localhost:8000/api/health

**Expected response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "database": "connected",
    "vector_store": "ready",
    "ibm_watsonx": "available"
  }
}
```

#### 6.4 Test API Docs

**Open browser:** http://localhost:8000/docs

**You should see:**
- Interactive API documentation
- All endpoints listed
- "Try it out" buttons

#### 6.5 Test AI Mode

**In API docs:**
1. Find `/api/modes/illustration/query`
2. Click **"Try it out"**
3. Enter:
   ```json
   {
     "workspace_id": "test-123",
     "query": "Explain what a REST API is"
   }
   ```
4. Click **"Execute"**

**Expected:** Response from IBM Granite model!

---

### 7. Run the Application

#### 7.1 Start Backend

**Terminal 1:**
```powershell
cd C:\Users\Janaa\Desktop\devpilot-ai\backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

**Keep this terminal open!**

#### 7.2 Start Frontend

**Terminal 2:**
```powershell
cd C:\Users\Janaa\Desktop\devpilot-ai\frontend
npm run dev
```

**Keep this terminal open!**

#### 7.3 Access Application

**Open browser:**
- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 🎯 Features & Usage

### 1. GitHub Repository Analysis

**Via API:**
```bash
curl -X POST http://localhost:8000/api/analyze/github \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/facebook/react",
    "workspace_id": "react-analysis"
  }'
```

**What it does:**
- Clones repository
- Analyzes code structure
- Extracts metadata
- Generates embeddings using IBM Slate
- Stores in vector database

### 2. AI Modes

#### Illustration Mode
**Generate architecture diagrams:**
```json
{
  "workspace_id": "my-workspace",
  "query": "Show me the system architecture"
}
```

**Returns:** Mermaid diagrams powered by Granite

#### Development Mode
**Code review and improvements:**
```json
{
  "workspace_id": "my-workspace",
  "query": "Review this authentication code for security issues"
}
```

**Returns:** Security analysis by Granite

#### Testing Mode
**Generate unit tests:**
```json
{
  "workspace_id": "my-workspace",
  "query": "Generate tests for the user service"
}
```

**Returns:** Complete test code by Granite

#### Deployment Mode
**Generate infrastructure configs:**
```json
{
  "workspace_id": "my-workspace",
  "query": "Create a Dockerfile for this Python app"
}
```

**Returns:** Production-ready configs by Granite

#### Documentation Mode
**Generate documentation:**
```json
{
  "workspace_id": "my-workspace",
  "query": "Write a README for this project"
}
```

**Returns:** Comprehensive docs by Granite

### 3. Meeting Transcript Processing

**Upload transcript:**
```json
{
  "transcript": "We need to build a user authentication system...",
  "workspace_id": "new-project"
}
```

**Returns:**
- Requirements extracted by Granite
- User stories generated
- Engineering tickets created
- Implementation plan

---

## 🐛 Troubleshooting

### Issue 1: "IBM Cloud API Key invalid"

**Error:**
```
[ERROR] 401 Unauthorized
```

**Solutions:**
1. **Verify API key:**
   ```powershell
   curl -X POST "https://iam.cloud.ibm.com/identity/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=YOUR_KEY"
   ```

2. **Check key format:**
   - Should be 44 characters
   - No spaces before/after
   - Not expired

3. **Create new key:**
   - IBM Cloud → Profile → API Keys
   - Create new key
   - Update `.env`

### Issue 2: "Project not found"

**Error:**
```
[ERROR] Project ID not found
```

**Solutions:**
1. **Verify Project ID:**
   - Go to watsonx.ai project
   - Manage → General
   - Copy exact Project ID

2. **Check permissions:**
   - Ensure you have access to project
   - Check Watson ML service is associated

3. **Verify region:**
   - Project and API key in same region
   - Update `WATSONX_URL` to match

### Issue 3: "Model not available"

**Error:**
```
[ERROR] Model ibm/granite-3-8b-instruct not found
```

**Solutions:**
1. **Test in Prompt Lab:**
   - Go to watsonx.ai project
   - Open Prompt Lab
   - Try the model there first

2. **Check model ID:**
   - Verify spelling: `ibm/granite-3-8b-instruct`
   - Try alternative: `ibm/granite-3-2b-instruct`

3. **Check region availability:**
   - Some models only in certain regions
   - Use `us-south` for best availability

### Issue 4: "Dependencies installation failed"

**Error:**
```
ERROR: Could not find a version that satisfies the requirement ibm-watsonx-ai
```

**Solutions:**
1. **Update pip:**
   ```powershell
   python -m pip install --upgrade pip
   ```

2. **Install individually:**
   ```powershell
   pip install ibm-watson
   pip install ibm-watsonx-ai
   pip install ibm-cloud-sdk-core
   ```

3. **Check Python version:**
   ```powershell
   python --version  # Should be 3.12+
   ```

### Issue 5: "Port already in use"

**Error:**
```
ERROR: [Errno 10048] error while attempting to bind on address
```

**Solutions:**
1. **Kill process:**
   ```powershell
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```

2. **Use different port:**
   ```powershell
   uvicorn app.main:app --reload --port 8001
   ```

---

## 📊 Architecture Overview

### IBM Stack Components

```
┌─────────────────────────────────────────────────────────┐
│                    DevPilot AI                          │
│                  (IBM Hackathon)                        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Frontend (Next.js)                     │
│  - Landing Page                                         │
│  - Workspace UI                                         │
│  - Monaco Editor                                        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼ HTTP/REST
┌─────────────────────────────────────────────────────────┐
│                Backend (FastAPI)                        │
│  - API Routes                                           │
│  - AI Orchestrator                                      │
│  - RAG Engine                                           │
│  - GitHub Analyzer                                      │
└─────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ IBM watsonx  │  │   ChromaDB   │  │   SQLite     │
│   Granite    │  │   (Vectors)  │  │  (Metadata)  │
│   Models     │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│           IBM Cloud Services                         │
│  - IAM (Authentication)                              │
│  - Watson ML (Model Inference)                       │
│  - Watson STT (Speech-to-Text)                       │
│  - Slate Embeddings                                  │
└──────────────────────────────────────────────────────┘
```

### Data Flow

```
1. User Query
   ↓
2. Frontend → Backend API
   ↓
3. RAG Engine retrieves context from ChromaDB
   ↓
4. AI Orchestrator formats prompt
   ↓
5. IBM watsonx client gets IAM token
   ↓
6. Request sent to Granite model
   ↓
7. Granite generates response
   ↓
8. Response formatted and returned
   ↓
9. Frontend displays result
```

---

## ✅ Verification Checklist

### Before Demo

- [ ] IBM Cloud API key configured
- [ ] watsonx.ai project created
- [ ] Project ID in `.env`
- [ ] `test_ibm_api.py` shows SUCCESS
- [ ] Backend starts without errors
- [ ] Frontend loads at localhost:3000
- [ ] Health endpoint returns 200 OK
- [ ] Can query Granite model via API docs
- [ ] All 5 AI modes working
- [ ] GitHub analysis works
- [ ] No errors in browser console
- [ ] No errors in backend logs

### Test Each Feature

- [ ] **Illustration Mode:** Generates Mermaid diagrams
- [ ] **Development Mode:** Provides code reviews
- [ ] **Testing Mode:** Generates test code
- [ ] **Deployment Mode:** Creates Docker configs
- [ ] **Documentation Mode:** Writes documentation
- [ ] **GitHub Analysis:** Analyzes repositories
- [ ] **RAG Pipeline:** Retrieves relevant context
- [ ] **Embeddings:** Uses IBM Slate models

---

## 🎉 You're Ready!

Once all checks pass:
- ✅ 100% IBM stack
- ✅ Granite models working
- ✅ All features functional
- ✅ Ready for hackathon demo!

**Next Steps:**
1. Test with real repositories
2. Prepare demo script
3. Practice presentation
4. Show off to judges!

---

## 📚 Additional Resources

### IBM Documentation
- **watsonx.ai:** https://dataplatform.cloud.ibm.com/docs
- **Granite Models:** https://www.ibm.com/products/watsonx-ai/foundation-models
- **IBM Cloud:** https://cloud.ibm.com/docs
- **Watson STT:** https://cloud.ibm.com/docs/speech-to-text

### DevPilot AI Docs
- `IBM_CREDENTIALS_GUIDE.md` - Get API credentials
- `COMPLETE_SETUP_AND_DEBUG_GUIDE.md` - Detailed debugging
- `GIT_PUSH_GUIDE.md` - Push to GitHub

### Support
- **IBM Cloud Support:** https://cloud.ibm.com/unifiedsupport
- **Hackathon Discord:** (Check your materials)
- **IBM Developer:** https://developer.ibm.com

---

**Last Updated:** 2024-01-15  
**For:** IBM Bob Hackathon  
**Stack:** 100% IBM (watsonx.ai + Granite + Watson)  
**Status:** Production Ready 🚀