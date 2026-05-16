# 🤖 DevPilot AI - Bob/Cline API Integration Guide

**Complete Step-by-Step Guide to Use Bob Instead of OpenAI**

---

## 🎯 What Changed

DevPilot AI now uses **Bob (Cline's API)** instead of OpenAI for all 5 AI modes:
- 🎨 Illustration Mode
- 💻 Development Mode  
- 🧪 Testing Mode
- 🚀 Deployment Mode
- 📚 Documentation Mode

**Model:** Claude 3.5 Sonnet (via Bob's API)

---

## 📝 STEP-BY-STEP SETUP

### Step 1: Get Your Bob API Key

1. **Open Cline Extension** in VS Code
2. **Go to Settings** (gear icon)
3. **Find your API Key** - It should look like: `sk-...` or similar
4. **Copy the API key**

**OR** if you need to generate a new one:
- Go to Bob's dashboard/settings
- Generate a new API key
- Copy it immediately (you won't see it again)

---

### Step 2: Update Backend Configuration

#### 2.1 Open the `.env` File

Navigate to:
```
C:\Users\Janaa\Desktop\devpilot-ai\backend\.env
```

Open it with any text editor (Notepad, VS Code, etc.)

#### 2.2 Replace the API Key

Find this line:
```env
OPENAI_API_KEY=PUT_YOUR_BOB_API_KEY_HERE
```

Replace `PUT_YOUR_BOB_API_KEY_HERE` with your actual Bob API key:
```env
OPENAI_API_KEY=sk-your-actual-bob-api-key-here
```

**Example:**
```env
OPENAI_API_KEY=sk-bob-1234567890abcdef
```

#### 2.3 Verify Other Settings

Make sure these lines are present and correct:
```env
# Bob/Cline AI Configuration
OPENAI_API_KEY=sk-your-actual-bob-api-key-here
OPENAI_API_BASE=https://api.cline.bot/v1

# AI Model Configuration
OPENAI_MODEL=claude-3-5-sonnet-20241022
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

#### 2.4 Save the File

**Important:** Save the `.env` file after making changes!

---

### Step 3: Restart the Backend

If your backend is already running, you need to restart it to load the new configuration.

#### 3.1 Stop the Backend

In the terminal where the backend is running:
- Press `Ctrl+C` to stop the server

#### 3.2 Start the Backend Again

```bash
cd C:\Users\Janaa\Desktop\devpilot-ai\backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

**✅ Success Check:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

---

### Step 4: Test Bob Integration

#### 4.1 Test Health Check

Open browser: http://localhost:8000/api/health

Should see:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "..."
}
```

#### 4.2 Test AI Mode (via API Docs)

1. Go to: http://localhost:8000/docs
2. Find `/api/modes/illustration/query`
3. Click "Try it out"
4. Enter test data:
```json
{
  "workspace_id": "test-123",
  "query": "Explain what a REST API is"
}
```
5. Click "Execute"

**✅ Expected:** You should get a response from Claude (Bob's API)!

---

## 🔍 WHAT EACH PLACEHOLDER MEANS

### In `.env` File:

```env
# This is YOUR Bob API key from Cline
OPENAI_API_KEY=PUT_YOUR_BOB_API_KEY_HERE

# This is Bob's API endpoint (already correct)
OPENAI_API_BASE=https://api.cline.bot/v1

# This is the Claude model Bob uses (already correct)
OPENAI_MODEL=claude-3-5-sonnet-20241022

# This is for embeddings (may still use OpenAI)
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

### What You Need to Change:

**ONLY THIS LINE:**
```env
OPENAI_API_KEY=PUT_YOUR_BOB_API_KEY_HERE
```

**Replace with your actual Bob API key:**
```env
OPENAI_API_KEY=sk-your-real-key-here
```

---

## 🎨 HOW IT WORKS NOW

### All 5 AI Modes Use Bob:

1. **Illustration Mode** → Bob generates Mermaid diagrams
2. **Development Mode** → Bob reviews code
3. **Testing Mode** → Bob generates tests
4. **Deployment Mode** → Bob creates Docker configs
5. **Documentation Mode** → Bob writes documentation

### API Flow:

```
Your Request
    ↓
DevPilot Backend
    ↓
Bob's API (https://api.cline.bot/v1)
    ↓
Claude 3.5 Sonnet
    ↓
Response back to you
```

---

## 🧪 TESTING EACH MODE

### Test 1: Illustration Mode

**API Endpoint:** `/api/modes/illustration/query`

**Request:**
```json
{
  "workspace_id": "test-workspace",
  "query": "Create an architecture diagram for a REST API"
}
```

**Expected:** Mermaid diagram code

---

### Test 2: Development Mode

**API Endpoint:** `/api/modes/development/query`

**Request:**
```json
{
  "workspace_id": "test-workspace",
  "query": "Review this code for best practices: def add(a, b): return a + b"
}
```

**Expected:** Code review and suggestions

---

### Test 3: Testing Mode

**API Endpoint:** `/api/modes/testing/query`

**Request:**
```json
{
  "workspace_id": "test-workspace",
  "query": "Generate unit tests for a login function"
}
```

**Expected:** Test code (pytest format)

---

### Test 4: Deployment Mode

**API Endpoint:** `/api/modes/deployment/query`

**Request:**
```json
{
  "workspace_id": "test-workspace",
  "query": "Create a Dockerfile for a Python FastAPI application"
}
```

**Expected:** Dockerfile content

---

### Test 5: Documentation Mode

**API Endpoint:** `/api/modes/documentation/query`

**Request:**
```json
{
  "workspace_id": "test-workspace",
  "query": "Write a README for a REST API project"
}
```

**Expected:** Markdown documentation

---

## ⚠️ IMPORTANT NOTES

### About Embeddings

**Embeddings** (for vector search) may still use OpenAI's API because:
- Bob/Cline might not support embedding models
- OpenAI's `text-embedding-3-small` is specifically for embeddings

**If you want to use Bob for embeddings too:**
1. Check if Bob supports embeddings
2. Update `embedding_service.py` to use Bob's base URL
3. Update the embedding model name

### About API Keys

- **Keep your Bob API key secret!**
- Don't commit `.env` files to Git (already in .gitignore)
- Regenerate keys if exposed

### Rate Limits

- Check Bob's rate limits in Cline settings
- May be different from OpenAI's limits
- Monitor usage in Bob's dashboard

---

## 🔧 TROUBLESHOOTING

### Error: "Bad credentials"

**Problem:** Bob API key is wrong or expired

**Solution:**
1. Check your Bob API key in Cline settings
2. Copy the correct key
3. Update `.env` file
4. Restart backend

---

### Error: "Connection refused"

**Problem:** Bob's API endpoint is wrong

**Solution:**
Verify this line in `.env`:
```env
OPENAI_API_BASE=https://api.cline.bot/v1
```

If Bob uses a different endpoint, update it.

---

### Error: "Model not found"

**Problem:** Model name is wrong

**Solution:**
Check what models Bob supports and update:
```env
OPENAI_MODEL=claude-3-5-sonnet-20241022
```

---

### No Response from AI

**Problem:** Backend not using Bob's API

**Solution:**
1. Check `.env` file has correct values
2. Restart backend completely
3. Check backend logs for errors

---

## ✅ VERIFICATION CHECKLIST

Before testing, verify:

- [ ] Bob API key is in `.env` file
- [ ] `OPENAI_API_BASE` is set to Bob's endpoint
- [ ] `OPENAI_MODEL` is set to Claude model
- [ ] Backend is restarted after changes
- [ ] No errors in backend terminal
- [ ] Health check endpoint works
- [ ] API docs page loads

---

## 🎉 YOU'RE READY!

Once you've:
1. ✅ Added your Bob API key to `.env`
2. ✅ Restarted the backend
3. ✅ Tested the health check

**All 5 AI modes will now use Bob (Claude 3.5 Sonnet)!**

---

## 📞 QUICK REFERENCE

### Your `.env` File Should Look Like:

```env
# Bob/Cline AI Configuration
OPENAI_API_KEY=sk-your-actual-bob-key-here
OPENAI_API_BASE=https://api.cline.bot/v1

# Database Configuration
DATABASE_URL=sqlite:///./devpilot.db

# Vector Store Configuration
CHROMA_PERSIST_DIRECTORY=./chroma_data

# Server Configuration
HOST=0.0.0.0
PORT=8000
RELOAD=true

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# GitHub Configuration (Optional)
GITHUB_TOKEN=

# Application Settings
APP_NAME=DevPilot AI
APP_VERSION=1.0.0
DEBUG=true

# AI Model Configuration
OPENAI_MODEL=claude-3-5-sonnet-20241022
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
MAX_TOKENS=4096
TEMPERATURE=0.7

# RAG Configuration
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=5

# Cache Configuration
CACHE_TTL=3600
```

**Only change:** `OPENAI_API_KEY=sk-your-actual-bob-key-here`

---

## 🚀 START USING BOB!

Your DevPilot AI is now powered by Bob (Claude 3.5 Sonnet) for all AI operations!

**Happy coding! 🎉**