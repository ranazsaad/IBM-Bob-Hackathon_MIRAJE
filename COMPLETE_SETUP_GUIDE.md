# 🚀 DevPilot AI - Complete Setup Guide (From Scratch)

**Estimated Time:** 30-40 minutes  
**Difficulty:** Beginner-Friendly  
**Last Updated:** May 16, 2026

---

## 📋 Table of Contents

1. [Prerequisites Check](#prerequisites-check)
2. [Backend Setup (15-20 min)](#backend-setup)
3. [Frontend Setup (10-15 min)](#frontend-setup)
4. [Testing & Verification](#testing--verification)
5. [Troubleshooting](#troubleshooting)

---

## ✅ Prerequisites Check

Before starting, verify you have:

### Required Software
```bash
# Check Python version (need 3.11+)
python --version
# or
python3 --version

# Check Node.js version (need 18+)
node --version

# Check npm version (need 9+)
npm --version

# Check Git
git --version
```

### Required Accounts & Keys
- ✅ Bob/Cline API key (starts with `bob_prod_`)
- ✅ GitHub account (optional, for higher rate limits)

---

## 🔧 Backend Setup

### Step 1: Navigate to Backend Directory

```bash
cd backend
```

### Step 2: Create Environment File

**Windows:**
```bash
copy .env.example .env
```

**Mac/Linux:**
```bash
cp .env.example .env
```

### Step 3: Configure Bob/Cline API Key

Open `backend/.env` in your text editor and update line 2:

```env
# BEFORE:
OPENAI_API_KEY=your_openai_api_key_here

# AFTER:
OPENAI_API_KEY=bob_prod_YOUR_ACTUAL_KEY_HERE
```

**Important:** Replace `bob_prod_YOUR_ACTUAL_KEY_HERE` with your real Bob API key.

### Step 4: Create Python Virtual Environment

**Windows (PowerShell):**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```bash
python -m venv venv
venv\Scripts\activate.bat
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

✅ **Success Check:** Your terminal prompt should now show `(venv)` at the beginning.

### Step 5: Upgrade pip and Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all dependencies (this takes 2-3 minutes)
pip install -r requirements.txt
```

**Expected:** ~45 packages will be installed including:
- FastAPI, Uvicorn
- OpenAI SDK
- ChromaDB (vector database)
- SQLAlchemy (database ORM)
- LangChain (AI orchestration)
- PyGithub (GitHub API)

### Step 6: Test Bob API Connection

```bash
python test_api.py
```

**Expected Output:**
```
============================================================
Testing Bob API Connection
============================================================

[OK] API Key: bob_prod_bob-user_...
[OK] API Base: https://api.cline.bot/v1
[OK] Model: claude-3-5-sonnet-20241022

[OK] OpenAI client created successfully

[...] Sending test request to Bob API...

[SUCCESS] Bob API is working!

[Response] Hello from DevPilot AI!

============================================================
```

❌ **If you see errors:**
- `401 Unauthorized` → API key is invalid or expired
- `Connection Error` → Check internet connection
- See [Troubleshooting](#troubleshooting) section below

### Step 7: Start Backend Server

```bash
uvicorn app.main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Will watch for changes in these directories: ['/path/to/backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
[DevPilot] Starting DevPilot AI Backend...
[DevPilot] Database initialized
INFO:     Application startup complete.
```

### Step 8: Verify Backend is Running

**Open in browser:** http://localhost:8000/docs

You should see:
- ✅ Swagger UI with API documentation
- ✅ Multiple endpoints listed (health, analyze, modes, workspace)
- ✅ Interactive API testing interface

**Test the health endpoint:**
1. Click on `GET /api/health`
2. Click "Try it out"
3. Click "Execute"
4. You should see: `{"status": "healthy", "version": "1.0.0", ...}`

✅ **Backend is now running!** Keep this terminal open.

---

## 🎨 Frontend Setup

### Step 1: Open New Terminal

**Important:** Keep the backend terminal running. Open a NEW terminal window.

### Step 2: Navigate to Frontend Directory

```bash
cd frontend
```

### Step 3: Create Environment File

**Windows:**
```bash
copy .env.local.example .env.local
```

**Mac/Linux:**
```bash
cp .env.local.example .env.local
```

The default configuration should work:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_APP_NAME=DevPilot AI
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### Step 4: Install Node.js Dependencies

```bash
npm install
```

**Expected:** This takes 2-3 minutes and installs:
- Next.js 14
- React 18
- TailwindCSS
- Monaco Editor
- Mermaid.js
- shadcn/ui components
- ~200+ packages total

### Step 5: Start Frontend Development Server

```bash
npm run dev
```

**Expected Output:**
```
   ▲ Next.js 14.2.18
   - Local:        http://localhost:3000
   - Environments: .env.local

 ✓ Ready in 2.5s
```

### Step 6: Open Frontend in Browser

**Open:** http://localhost:3000

You should see:
- ✅ Beautiful landing page with gradient design
- ✅ "DevPilot AI" logo and title
- ✅ Two input tabs: "GitHub Repository" and "Meeting Transcript"
- ✅ Feature cards showcasing the 5 AI modes

✅ **Frontend is now running!**

---

## 🧪 Testing & Verification

### Test 1: GitHub Repository Analysis

1. Go to http://localhost:3000
2. Make sure "GitHub Repository" tab is selected
3. Enter a test repository URL:
   ```
   https://github.com/facebook/react
   ```
4. Click "Analyze Repository"
5. Wait 10-30 seconds (watch backend terminal for logs)
6. You should be redirected to the workspace page

**Expected:**
- ✅ Workspace page loads with 5 mode tabs on the left
- ✅ Repository name appears in header
- ✅ Language and file count displayed
- ✅ No errors in browser console

### Test 2: Illustration Mode (Architecture Diagrams)

1. Click on "Illustration" mode (blue icon)
2. Try a sample prompt:
   ```
   Generate an architecture diagram of this codebase
   ```
3. Click Send or press Enter
4. Wait 5-10 seconds

**Expected:**
- ✅ Loading animation appears
- ✅ Mermaid diagram renders
- ✅ Copy and Download buttons work
- ✅ Suggestions appear below result

### Test 3: Development Mode (Code Review)

1. Click on "Development" mode (purple icon)
2. Try:
   ```
   Review the code quality and suggest improvements
   ```
3. Wait for response

**Expected:**
- ✅ Detailed code review appears
- ✅ Markdown formatting renders correctly
- ✅ Suggestions are actionable

### Test 4: Testing Mode (Test Generation)

1. Click on "Testing" mode (green icon)
2. Try:
   ```
   Generate unit tests for the main module
   ```

**Expected:**
- ✅ Test code appears in Monaco Editor
- ✅ Syntax highlighting works
- ✅ Can toggle between rendered and raw view

### Test 5: Deployment Mode (Infrastructure)

1. Click on "Deployment" mode (orange icon)
2. Try:
   ```
   Generate a production Dockerfile
   ```

**Expected:**
- ✅ Dockerfile content appears
- ✅ Proper syntax and best practices
- ✅ Can copy and download

### Test 6: Documentation Mode (README)

1. Click on "Documentation" mode (pink icon)
2. Try:
   ```
   Generate a comprehensive README
   ```

**Expected:**
- ✅ Well-formatted README appears
- ✅ Includes all standard sections
- ✅ Markdown renders properly

### Test 7: Meeting Transcript Processing

1. Go back to home page (click back arrow)
2. Click "Meeting Transcript" tab
3. Paste sample transcript:
   ```
   Meeting Notes - Sprint Planning
   
   We need to build a user authentication system with:
   - Email/password login
   - OAuth integration (Google, GitHub)
   - Password reset functionality
   - Two-factor authentication
   - Session management
   
   Priority: High
   Timeline: 2 weeks
   ```
4. Add context: "Sprint planning for authentication feature"
5. Click "Process Transcript"

**Expected:**
- ✅ Requirements extracted
- ✅ Engineering tickets generated
- ✅ Can click "Implement" on any requirement
- ✅ Switches to Development mode with pre-filled query

---

## ✅ Final Verification Checklist

- [ ] Backend server running on http://localhost:8000
- [ ] Backend API docs accessible at http://localhost:8000/docs
- [ ] Frontend running on http://localhost:3000
- [ ] Can analyze GitHub repositories
- [ ] All 5 AI modes respond correctly
- [ ] Mermaid diagrams render
- [ ] Monaco Editor displays code
- [ ] Meeting transcript processing works
- [ ] No errors in browser console
- [ ] No errors in backend terminal

---

## 🐛 Troubleshooting

### Backend Issues

#### Error: "401 Unauthorized" from Bob API

**Cause:** Invalid or expired API key

**Solution:**
1. Get a fresh API key from Cline extension:
   - Open VS Code
   - Click Cline icon in sidebar
   - Click ⚙️ Settings
   - Copy your API key
2. Update `backend/.env` file
3. Restart backend server

#### Error: "Module not found"

**Cause:** Dependencies not installed

**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

#### Error: "Port 8000 already in use"

**Solution:**
```bash
# Use different port
uvicorn app.main:app --reload --port 8001

# Update frontend .env.local:
NEXT_PUBLIC_API_URL=http://localhost:8001/api
```

### Frontend Issues

#### Error: "Cannot connect to backend"

**Cause:** Backend not running or wrong URL

**Solution:**
1. Verify backend is running: http://localhost:8000/docs
2. Check `frontend/.env.local` has correct URL
3. Restart frontend: `npm run dev`

#### Error: "Module not found" or build errors

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### Error: "Port 3000 already in use"

**Solution:**
```bash
# Use different port
npm run dev -- -p 3001
```

### API Issues

#### Slow responses or timeouts

**Possible causes:**
- Large repository (>100 files)
- Network latency
- Bob API rate limits

**Solutions:**
- Try smaller repositories first
- Check internet connection
- Wait a few seconds between requests

#### "Rate limit exceeded"

**Solution:**
- Wait 60 seconds
- Add GitHub token to `backend/.env`:
  ```env
  GITHUB_TOKEN=ghp_your_token_here
  ```

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js 14)                     │
│  React • TypeScript • TailwindCSS • Monaco Editor           │
│  Port: 3000                                                  │
└─────────────────────────────────────────────────────────────┘
                              ↕ REST API
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   GitHub     │  │  Transcript  │  │      AI      │     │
│  │   Analyzer   │  │  Processor   │  │ Orchestrator │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  Port: 8000                                                  │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│              Data Layer (SQLite + ChromaDB)                  │
│  Vector Search • Embeddings • Workspace Management          │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                   Bob/Cline AI API                           │
│  Claude 3.5 Sonnet • Embeddings • RAG Pipeline             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 What's Next?

After successful setup, you can:

1. **Analyze Your Own Repositories**
   - Try your personal projects
   - Analyze open-source codebases
   - Get architectural insights

2. **Process Meeting Notes**
   - Convert discussions to tickets
   - Extract requirements
   - Generate implementation plans

3. **Explore AI Modes**
   - Generate tests for your code
   - Create deployment configs
   - Write documentation

4. **Customize & Extend**
   - Add new AI modes
   - Customize prompts
   - Integrate with your workflow

---

## 📚 Additional Resources

- **Architecture Details:** [DEVPILOT_AI_ARCHITECTURE.md](DEVPILOT_AI_ARCHITECTURE.md)
- **Implementation Status:** [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)
- **Quick Start:** [QUICK_START.md](QUICK_START.md)
- **API Documentation:** http://localhost:8000/docs (when running)

---

## 🎉 Success!

If you've completed all steps and tests pass, congratulations! 🎊

DevPilot AI is now running and ready to help you:
- ✅ Understand codebases faster
- ✅ Generate tests automatically
- ✅ Create deployment configs
- ✅ Write comprehensive documentation
- ✅ Transform meetings into actionable tickets

**Happy coding with your AI teammate! 🚀**

---

## 📞 Need Help?

If you encounter issues not covered here:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review backend terminal logs for errors
3. Check browser console for frontend errors
4. Verify API key is valid and not expired
5. Ensure all prerequisites are met

**Common Success Indicators:**
- Backend shows: `[DevPilot] Database initialized`
- Frontend shows: `✓ Ready in X.Xs`
- API docs load at http://localhost:8000/docs
- Landing page loads at http://localhost:3000
- No red errors in terminals or browser console

---

Made with ❤️ by DevPilot AI Team