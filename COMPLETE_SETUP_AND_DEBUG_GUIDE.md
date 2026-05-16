# 🚀 DevPilot AI - Complete Setup & Debug Guide

## 📋 Table of Contents
1. [System Requirements](#system-requirements)
2. [Quick Start (5 Minutes)](#quick-start-5-minutes)
3. [Detailed Setup Instructions](#detailed-setup-instructions)
4. [Common Errors & Solutions](#common-errors--solutions)
5. [Testing & Verification](#testing--verification)
6. [Troubleshooting](#troubleshooting)

---

## ✅ System Requirements

### Required Software
- **Python 3.12+** (Check: `python --version`)
- **Node.js 18+** (Check: `node --version`)
- **npm 9+** (Check: `npm --version`)
- **Git** (Check: `git --version`)

### Required Accounts
- **Cline/Bob Account** - For AI API access
- **GitHub Account** (optional) - For repository analysis

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Get Your Bob API Key (2 minutes)

**Option A: From Cline Extension (Recommended)**
1. Open VS Code
2. Click on **Cline** extension icon in sidebar
3. Click the **⚙️ Settings/Gear** icon
4. Look for **"API Key"** or **"Authentication"**
5. Copy your API key (starts with `bob_prod_`)

**Option B: From Cline Web Dashboard**
1. Go to https://app.cline.bot
2. Sign in with your account
3. Navigate to **Settings** → **API Keys**
4. Copy your production API key

**⚠️ IMPORTANT:** Your API key should look like:
```
bob_prod_bob-user_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Step 2: Update Backend Configuration (1 minute)

1. **Open the `.env` file:**
   ```
   C:\Users\Janaa\Desktop\devpilot-ai\backend\.env
   ```

2. **Find line 6:**
   ```env
   OPENAI_API_KEY=bob_prod_bob-user_44Er6d67wHFCVCY4C7YsV2V3akkwRYA9fD5nfugUfZRdFz7ZDuvFEKYGL9fswiyttRD4tgjzzPgm6R3X6GLBaHSi_HsHgYNbepQUhB3zPzMwLP8br7hoESeP64Eo5A2RVLZef
   ```

3. **Replace with YOUR API key:**
   ```env
   OPENAI_API_KEY=bob_prod_YOUR_ACTUAL_KEY_HERE
   ```

4. **Save the file** (Ctrl+S)

### Step 3: Test the Connection (2 minutes)

**Open PowerShell/Terminal and run:**

```powershell
# Navigate to backend
cd C:\Users\Janaa\Desktop\devpilot-ai\backend

# Activate virtual environment
.\venv\Scripts\activate

# Test Bob API
python test_api.py
```

**Expected Output:**
```
============================================================
Testing Bob API Connection
============================================================

[OK] API Key: bob_prod_bob-user_44...
[OK] API Base: https://api.cline.bot/v1
[OK] Model: claude-3-5-sonnet-20241022

[OK] OpenAI client created successfully

[...] Sending test request to Bob API...

[SUCCESS] Bob API is working!

[Response] Hello from DevPilot AI!

============================================================
```

**If you see `[SUCCESS]`** → You're ready! Skip to [Running the Application](#running-the-application)

**If you see `[ERROR]`** → Continue to [Common Errors](#common-errors--solutions)

---

## 📖 Detailed Setup Instructions

### 1. Backend Setup

#### 1.1 Create Virtual Environment (First Time Only)

```powershell
cd C:\Users\Janaa\Desktop\devpilot-ai\backend
python -m venv venv
```

#### 1.2 Activate Virtual Environment

**Windows PowerShell:**
```powershell
.\venv\Scripts\activate
```

**Windows CMD:**
```cmd
venv\Scripts\activate.bat
```

**You should see `(venv)` in your terminal prompt**

#### 1.3 Install Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

**This installs:**
- FastAPI (web framework)
- OpenAI SDK (for Bob API)
- ChromaDB (vector database)
- SQLAlchemy (database ORM)
- And more...

#### 1.4 Configure Environment Variables

**Edit `backend/.env`:**

```env
# ============================================================
# BOB (Cline) API — REQUIRED
# ============================================================
OPENAI_API_KEY=bob_prod_YOUR_KEY_HERE  # ← CHANGE THIS!
OPENAI_API_BASE=https://api.cline.bot/v1
OPENAI_MODEL=claude-3-5-sonnet-20241022

# ============================================================
# Database Configuration — Already Set
# ============================================================
DATABASE_URL=sqlite:///./devpilot.db
CHROMA_PERSIST_DIRECTORY=./chroma_data

# ============================================================
# Server Configuration — Already Set
# ============================================================
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# ============================================================
# Optional: IBM Watson (for advanced features)
# ============================================================
IBM_CLOUD_API_KEY=  # Leave empty for now
WATSON_STT_API_KEY=  # Leave empty for now
WATSONX_PROJECT_ID=  # Leave empty for now
USE_IBM_EMBEDDINGS=false  # Set to false to use Bob for embeddings
```

**⚠️ ONLY CHANGE:** `OPENAI_API_KEY` - Everything else is pre-configured!

#### 1.5 Test Backend

```powershell
# Test API connection
python test_api.py

# Start the server
uvicorn app.main:app --reload --port 8000
```

**Server should start at:** http://localhost:8000

**Check health:** http://localhost:8000/api/health

**API Docs:** http://localhost:8000/docs

---

### 2. Frontend Setup

#### 2.1 Install Dependencies

**Open a NEW terminal (keep backend running):**

```powershell
cd C:\Users\Janaa\Desktop\devpilot-ai\frontend
npm install
```

**This installs:**
- Next.js 14
- React 18
- TailwindCSS
- shadcn/ui components
- Monaco Editor

#### 2.2 Configure Environment

**Create `frontend/.env.local`:**

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### 2.3 Start Frontend

```powershell
npm run dev
```

**Frontend should start at:** http://localhost:3000

---

## 🐛 Common Errors & Solutions

### Error 1: 401 Unauthorized - Bob API

**Error Message:**
```
[ERROR] Error code: 401 - {'error': "Unauthorized: Please make sure you're using the latest version of Cline and re-authenticate your Cline account."}
```

**Causes:**
1. ❌ API key is expired
2. ❌ API key is invalid
3. ❌ Cline account needs re-authentication
4. ❌ Using old/cached API key

**Solutions:**

**Solution 1: Get Fresh API Key**
```powershell
# 1. Open Cline extension in VS Code
# 2. Click Settings (gear icon)
# 3. Click "Sign Out"
# 4. Click "Sign In" again
# 5. Copy the NEW API key
# 6. Update backend/.env with new key
```

**Solution 2: Update Cline Extension**
```powershell
# 1. Open VS Code
# 2. Go to Extensions (Ctrl+Shift+X)
# 3. Search for "Cline"
# 4. Click "Update" if available
# 5. Restart VS Code
# 6. Get new API key from Cline settings
```

**Solution 3: Verify API Key Format**
```powershell
# Your API key should look like this:
bob_prod_bob-user_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# NOT like this:
sk-XXXXXXXX  # This is OpenAI format, not Bob!
```

**Solution 4: Test with curl**
```powershell
# Test if your API key works:
curl -X POST https://api.cline.bot/v1/chat/completions `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer YOUR_BOB_API_KEY" `
  -d '{
    "model": "claude-3-5-sonnet-20241022",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 10
  }'
```

---

### Error 2: Missing Dependencies

**Error Message:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```powershell
cd C:\Users\Janaa\Desktop\devpilot-ai\backend
.\venv\Scripts\activate
pip install -r requirements.txt
```

---

### Error 3: Port Already in Use

**Error Message:**
```
ERROR: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000): only one usage of each socket address
```

**Solution 1: Kill Process on Port 8000**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F
```

**Solution 2: Use Different Port**
```powershell
uvicorn app.main:app --reload --port 8001
```

---

### Error 4: CORS Error in Frontend

**Error Message:**
```
Access to fetch at 'http://localhost:8000/api/...' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solution:**

**Check `backend/.env`:**
```env
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

**Restart backend after changing:**
```powershell
# Stop server (Ctrl+C)
# Start again
uvicorn app.main:app --reload --port 8000
```

---

### Error 5: Database Locked

**Error Message:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
```powershell
# Stop all running servers
# Delete database file
cd C:\Users\Janaa\Desktop\devpilot-ai\backend
Remove-Item devpilot.db -Force

# Restart server (database will be recreated)
uvicorn app.main:app --reload --port 8000
```

---

### Error 6: npm Install Fails

**Error Message:**
```
npm ERR! code ENOENT
npm ERR! syscall open
```

**Solution:**
```powershell
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
cd C:\Users\Janaa\Desktop\devpilot-ai\frontend
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json

# Reinstall
npm install
```

---

## ✅ Testing & Verification

### 1. Test Backend API

#### Test 1: Health Check
```powershell
curl http://localhost:8000/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Test 2: Bob API Connection
```powershell
cd C:\Users\Janaa\Desktop\devpilot-ai\backend
.\venv\Scripts\activate
python test_api.py
```

#### Test 3: GitHub Analysis
```powershell
# Using curl
curl -X POST http://localhost:8000/api/analyze/github `
  -H "Content-Type: application/json" `
  -d '{
    "repo_url": "https://github.com/facebook/react",
    "workspace_id": "test-123"
  }'
```

#### Test 4: AI Modes (via API Docs)

1. Go to http://localhost:8000/docs
2. Find `/api/modes/illustration/query`
3. Click "Try it out"
4. Enter:
   ```json
   {
     "workspace_id": "test-123",
     "query": "Explain what a REST API is"
   }
   ```
5. Click "Execute"
6. Should see Claude's response!

---

### 2. Test Frontend

#### Test 1: Landing Page
1. Go to http://localhost:3000
2. Should see DevPilot AI landing page
3. Check for:
   - ✅ Hero section
   - ✅ Features section
   - ✅ "Get Started" button

#### Test 2: API Integration
1. Open browser console (F12)
2. Check for errors
3. Should see no CORS errors

---

## 🔧 Troubleshooting

### Issue: "API key not working"

**Checklist:**
- [ ] API key starts with `bob_prod_`
- [ ] No extra spaces before/after key in `.env`
- [ ] `.env` file is in `backend/` folder
- [ ] Restarted backend after changing `.env`
- [ ] Cline extension is up to date
- [ ] Signed out and back into Cline

**Debug Steps:**
```powershell
# 1. Check if .env is loaded
cd C:\Users\Janaa\Desktop\devpilot-ai\backend
.\venv\Scripts\activate
python -c "from app.config import settings; print(f'Key: {settings.OPENAI_API_KEY[:20]}...')"

# 2. Test API key directly
python test_api.py

# 3. Check Cline status
# Open Cline extension → Check if signed in
```

---

### Issue: "Backend won't start"

**Checklist:**
- [ ] Virtual environment activated (`(venv)` in prompt)
- [ ] Dependencies installed (`pip list | findstr fastapi`)
- [ ] Port 8000 is free (`netstat -ano | findstr :8000`)
- [ ] No syntax errors in code

**Debug Steps:**
```powershell
# 1. Check Python version
python --version  # Should be 3.12+

# 2. Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Try different port
uvicorn app.main:app --reload --port 8001

# 4. Check for errors
python -c "from app.main import app; print('App loaded successfully')"
```

---

### Issue: "Frontend won't start"

**Checklist:**
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Dependencies installed (`npm list next`)
- [ ] Port 3000 is free
- [ ] `.env.local` exists with correct API URL

**Debug Steps:**
```powershell
# 1. Check Node version
node --version  # Should be 18+

# 2. Clear cache and reinstall
npm cache clean --force
Remove-Item -Recurse node_modules
npm install

# 3. Try different port
$env:PORT=3001; npm run dev

# 4. Check for errors
npm run build
```

---

## 🎯 Running the Application

### Full Startup Sequence

**Terminal 1 - Backend:**
```powershell
cd C:\Users\Janaa\Desktop\devpilot-ai\backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```powershell
cd C:\Users\Janaa\Desktop\devpilot-ai\frontend
npm run dev
```

**Access Points:**
- 🌐 Frontend: http://localhost:3000
- 🔧 Backend API: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs
- ❤️ Health Check: http://localhost:8000/api/health

---

## 📊 Verification Checklist

### Before Demo/Presentation

- [ ] **Backend Health Check** - http://localhost:8000/api/health returns 200
- [ ] **Bob API Working** - `python test_api.py` shows SUCCESS
- [ ] **Frontend Loading** - http://localhost:3000 shows landing page
- [ ] **No Console Errors** - Browser console (F12) is clean
- [ ] **API Docs Accessible** - http://localhost:8000/docs loads
- [ ] **CORS Working** - No CORS errors in browser console
- [ ] **Database Created** - `devpilot.db` exists in backend folder
- [ ] **Vector Store Ready** - `chroma_data/` folder exists

### Test Each Feature

- [ ] **GitHub Analysis** - Can analyze a public repo
- [ ] **Illustration Mode** - Returns Mermaid diagrams
- [ ] **Development Mode** - Provides code reviews
- [ ] **Testing Mode** - Generates test cases
- [ ] **Deployment Mode** - Creates Docker configs
- [ ] **Documentation Mode** - Writes documentation

---

## 🚨 Emergency Fixes

### "Nothing Works!"

**Nuclear Option - Fresh Start:**

```powershell
# 1. Stop all servers (Ctrl+C in all terminals)

# 2. Backend reset
cd C:\Users\Janaa\Desktop\devpilot-ai\backend
Remove-Item -Recurse -Force venv
Remove-Item devpilot.db -Force
Remove-Item -Recurse -Force chroma_data
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# 3. Frontend reset
cd C:\Users\Janaa\Desktop\devpilot-ai\frontend
Remove-Item -Recurse -Force node_modules
Remove-Item -Recurse -Force .next
Remove-Item package-lock.json
npm install

# 4. Update .env with fresh Bob API key

# 5. Test
cd C:\Users\Janaa\Desktop\devpilot-ai\backend
.\venv\Scripts\activate
python test_api.py

# 6. Start servers
# Terminal 1: uvicorn app.main:app --reload --port 8000
# Terminal 2: npm run dev
```

---

## 📞 Getting Help

### Check Logs

**Backend Logs:**
```powershell
# Server logs appear in terminal where uvicorn is running
# Look for ERROR or WARNING messages
```

**Frontend Logs:**
```powershell
# Browser console (F12) → Console tab
# Terminal where npm run dev is running
```

### Common Log Messages

**✅ Good:**
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**❌ Bad:**
```
ERROR:    [Errno 10048] error while attempting to bind
ERROR:    ModuleNotFoundError: No module named 'fastapi'
```

---

## 🎓 Understanding the Stack

### Backend (FastAPI)
- **Framework:** FastAPI (Python web framework)
- **AI:** Bob/Cline API (Claude 3.5 Sonnet)
- **Database:** SQLite (file-based SQL database)
- **Vector Store:** ChromaDB (for code embeddings)
- **Server:** Uvicorn (ASGI server)

### Frontend (Next.js)
- **Framework:** Next.js 14 (React framework)
- **Styling:** TailwindCSS + shadcn/ui
- **Code Editor:** Monaco Editor
- **HTTP Client:** Fetch API

### Data Flow
```
User → Frontend (Next.js) → Backend API (FastAPI) → Bob API (Claude) → Response
                                ↓
                          Database (SQLite)
                          Vector Store (ChromaDB)
```

---

## 🎉 Success Indicators

### You're Ready When:

1. ✅ `python test_api.py` shows `[SUCCESS]`
2. ✅ Backend health check returns 200 OK
3. ✅ Frontend loads without errors
4. ✅ API docs are accessible
5. ✅ No CORS errors in browser console
6. ✅ Can query AI modes successfully

### Demo-Ready Checklist:

- [ ] Both servers running (backend + frontend)
- [ ] Bob API key is valid and working
- [ ] Sample GitHub repo ready to analyze
- [ ] Browser tabs prepared:
  - Frontend: http://localhost:3000
  - API Docs: http://localhost:8000/docs
- [ ] No errors in any console/terminal
- [ ] Tested at least one AI mode successfully

---

## 📚 Additional Resources

### Documentation Files
- `SETUP_GUIDE.md` - Original setup guide
- `BOB_API_SETUP_GUIDE.md` - Bob API specific guide
- `QUICK_START.md` - Quick start guide
- `LOCAL_SETUP_GUIDE.md` - Local development guide

### API Documentation
- Interactive API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Useful Commands

**Backend:**
```powershell
# Activate venv
.\venv\Scripts\activate

# Install deps
pip install -r requirements.txt

# Start server
uvicorn app.main:app --reload --port 8000

# Test API
python test_api.py

# Check config
python -c "from app.config import settings; print(settings.OPENAI_API_KEY[:20])"
```

**Frontend:**
```powershell
# Install deps
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

---

## 🔐 Security Notes

### API Keys
- ⚠️ **NEVER** commit `.env` files to Git
- ⚠️ **NEVER** share your Bob API key
- ⚠️ `.env` is already in `.gitignore`
- ⚠️ Rotate keys if accidentally exposed

### Best Practices
- Keep dependencies updated
- Use environment variables for secrets
- Don't hardcode API keys in code
- Review `.gitignore` before committing

---

## 🎯 Next Steps

### After Setup Works:

1. **Explore Features:**
   - Try each AI mode
   - Analyze different GitHub repos
   - Test with various queries

2. **Customize:**
   - Modify prompts in `backend/app/services/`
   - Update UI in `frontend/app/`
   - Add new features

3. **Deploy:**
   - Use Docker for containerization
   - Deploy to cloud (Vercel, Railway, etc.)
   - Set up CI/CD with GitHub Actions

4. **Optimize:**
   - Add caching
   - Implement rate limiting
   - Add authentication

---

## ✨ You're All Set!

If you followed this guide and everything works:
- ✅ Backend is running on port 8000
- ✅ Frontend is running on port 3000
- ✅ Bob API is connected and working
- ✅ All tests pass

**You're ready to build amazing things with DevPilot AI! 🚀**

---

**Last Updated:** 2024-01-15  
**Version:** 1.0.0  
**Tested On:** Windows 11, Python 3.12, Node.js 18