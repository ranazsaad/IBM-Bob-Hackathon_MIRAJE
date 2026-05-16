# DevPilot AI - Complete Local Setup Guide

**Last Updated:** May 15, 2026  
**Estimated Setup Time:** 15-20 minutes  
**Difficulty:** Beginner-Friendly

---

## 📋 Prerequisites

Before starting, ensure you have:

### Required Software
- ✅ **Python 3.11+** - [Download](https://www.python.org/downloads/)
- ✅ **Node.js 18+** - [Download](https://nodejs.org/)
- ✅ **Git** - [Download](https://git-scm.com/)
- ✅ **OpenAI API Key** - [Get one here](https://platform.openai.com/api-keys)

### Optional (Recommended)
- 🔧 **VS Code** - [Download](https://code.visualstudio.com/)
- 🐳 **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop/)

### Verify Installations
Open a terminal and run:
```bash
python --version    # Should show 3.11 or higher
node --version      # Should show 18 or higher
npm --version       # Should show 9 or higher
git --version       # Should show any version
```

---

## 🚀 STEP-BY-STEP SETUP

### Step 1: Navigate to Project Directory (1 minute)

Open a terminal and navigate to where you created the project:

```bash
cd C:/Users/Janaa/Desktop/devpilot-ai
```

Verify you're in the right place:
```bash
dir  # Windows
# OR
ls   # Mac/Linux
```

You should see:
```
backend/
frontend/
README.md
docker-compose.yml
...
```

---

### Step 2: Backend Setup (5-7 minutes)

#### 2.1 Navigate to Backend Directory
```bash
cd backend
```

#### 2.2 Create Virtual Environment
**Windows:**
```bash
python -m venv venv
```

**Mac/Linux:**
```bash
python3 -m venv venv
```

You should see a new `venv` folder created.

#### 2.3 Activate Virtual Environment
**Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```bash
venv\Scripts\activate.bat
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

✅ **Success Check:** Your terminal prompt should now show `(venv)` at the beginning.

#### 2.4 Install Python Dependencies
```bash
pip install -r requirements.txt
```

This will take 2-3 minutes. You'll see packages being installed.

⚠️ **If you get errors:**
- Try: `pip install --upgrade pip` first
- Then retry: `pip install -r requirements.txt`

#### 2.5 Configure Environment Variables
**Windows:**
```bash
copy .env.example .env
```

**Mac/Linux:**
```bash
cp .env.example .env
```

#### 2.6 Add Your OpenAI API Key
Open the `.env` file in a text editor:

**Windows:**
```bash
notepad .env
```

**Mac/Linux:**
```bash
nano .env
# OR
code .env  # If using VS Code
```

Replace `your_openai_api_key_here` with your actual API key:
```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
```

Save and close the file.

#### 2.7 Test Backend
Start the backend server:
```bash
uvicorn app.main:app --reload --port 8000
```

✅ **Success Check:** You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

#### 2.8 Verify Backend is Working
Open a web browser and go to:
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health

You should see the Swagger UI documentation page.

**Keep this terminal open!** The backend needs to keep running.

---

### Step 3: Frontend Setup (5-7 minutes)

#### 3.1 Open a NEW Terminal
**Important:** Don't close the backend terminal. Open a new one.

Navigate to the frontend directory:
```bash
cd C:/Users/Janaa/Desktop/devpilot-ai/frontend
```

#### 3.2 Install Node Dependencies
```bash
npm install
```

This will take 3-5 minutes. You'll see a progress bar.

⚠️ **If you get errors:**
- Try: `npm cache clean --force`
- Then retry: `npm install`

#### 3.3 Configure Environment Variables
**Windows:**
```bash
copy .env.local.example .env.local
```

**Mac/Linux:**
```bash
cp .env.local.example .env.local
```

The default values should work, but you can verify:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

#### 3.4 Start Frontend Development Server
```bash
npm run dev
```

✅ **Success Check:** You should see:
```
- ready started server on 0.0.0.0:3000
- Local:        http://localhost:3000
```

#### 3.5 Open the Application
Open a web browser and go to:
- **Frontend:** http://localhost:3000

You should see the DevPilot AI landing page with a beautiful gradient design!

**Keep this terminal open too!** The frontend needs to keep running.

---

## 🎉 YOU'RE DONE! Verification Steps

### Quick Test Checklist

1. **Backend Health Check**
   - Go to: http://localhost:8000/api/health
   - Should see: `{"status":"healthy","version":"1.0.0",...}`

2. **API Documentation**
   - Go to: http://localhost:8000/docs
   - Should see: Interactive Swagger UI with all endpoints

3. **Frontend Landing Page**
   - Go to: http://localhost:3000
   - Should see: Beautiful landing page with "DevPilot AI" header

4. **Test GitHub Input**
   - On the landing page, enter: `https://github.com/facebook/react`
   - Click "Analyze Repository"
   - Should navigate to workspace page (even if not fully functional yet)

---

## 🔧 Common Issues & Solutions

### Issue 1: "Port 8000 already in use"
**Solution:**
```bash
# Find and kill the process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F

# Mac/Linux:
lsof -ti:8000 | xargs kill -9

# OR use a different port:
uvicorn app.main:app --reload --port 8001
# Then update frontend .env.local: NEXT_PUBLIC_API_URL=http://localhost:8001/api
```

### Issue 2: "Port 3000 already in use"
**Solution:**
```bash
# Use a different port:
npm run dev -- -p 3001
# Then access at: http://localhost:3001
```

### Issue 3: "Module not found" errors in backend
**Solution:**
```bash
# Make sure virtual environment is activated (you should see (venv))
# If not, activate it again:
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Reinstall dependencies:
pip install -r requirements.txt
```

### Issue 4: "Cannot find module" errors in frontend
**Solution:**
```bash
# Delete node_modules and reinstall:
rm -rf node_modules package-lock.json  # Mac/Linux
# OR
rmdir /s node_modules & del package-lock.json  # Windows

npm install
```

### Issue 5: OpenAI API errors
**Solution:**
- Verify your API key is correct in `backend/.env`
- Check you have credits: https://platform.openai.com/account/usage
- Ensure no extra spaces in the .env file
- Try regenerating your API key

### Issue 6: Database errors
**Solution:**
```bash
# Delete the database and let it recreate:
cd backend
rm devpilot.db  # Mac/Linux
del devpilot.db  # Windows

# Restart the backend server
```

---

## 📱 Using the Application

### Test GitHub Repository Analysis

1. Go to http://localhost:3000
2. Make sure "GitHub Repository" tab is selected
3. Enter a repository URL: `https://github.com/facebook/react`
4. Leave branch as "main"
5. Select "Shallow (Fast)" for analysis depth
6. Click "Analyze Repository"

**What happens:**
- Backend fetches repo metadata from GitHub API
- Extracts file structure and languages
- Indexes key files in vector database
- Creates a workspace

**Check the backend terminal** - you'll see logs of the analysis process.

### Test Meeting Transcript Processing

1. Go to http://localhost:3000
2. Click "Meeting Transcript" tab
3. Paste sample meeting notes:
```
Sprint Planning Meeting - Q2 2026

Discussed new features for the dashboard:
- Add real-time analytics
- Implement user authentication with OAuth
- Create mobile responsive design
- Add export to PDF functionality

Timeline: Complete by end of Q2
Team: 3 developers, 1 designer
```
4. Add context: "Sprint planning for Q2"
5. Click "Process Transcript"

**What happens:**
- AI extracts requirements
- Generates user stories
- Creates engineering tickets
- Produces executive summary

---

## 🐳 Alternative: Docker Setup (Optional)

If you prefer Docker:

### Prerequisites
- Docker Desktop installed and running

### Steps
```bash
# Navigate to project root
cd C:/Users/Janaa/Desktop/devpilot-ai

# Create backend .env file
cd backend
copy .env.example .env  # Windows
# OR
cp .env.example .env    # Mac/Linux

# Add your OpenAI API key to backend/.env

# Go back to root
cd ..

# Start everything with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

### Stop Docker
```bash
docker-compose down
```

---

## 🎯 Next Steps After Setup

### 1. Explore the API Documentation
- Go to: http://localhost:8000/docs
- Try the "Health Check" endpoint
- Expand other endpoints to see request/response schemas

### 2. Test Backend Endpoints Directly
Using the Swagger UI at http://localhost:8000/docs:

**Test Health Check:**
1. Click on `/api/health`
2. Click "Try it out"
3. Click "Execute"
4. See the response

**Test GitHub Analysis:**
1. Click on `/api/analyze/github`
2. Click "Try it out"
3. Enter request body:
```json
{
  "repo_url": "https://github.com/facebook/react",
  "branch": "main",
  "depth": "shallow"
}
```
4. Click "Execute"
5. Wait 10-30 seconds for analysis
6. Copy the `workspace_id` from response

**Test AI Mode Query:**
1. Click on `/api/modes/illustration/query`
2. Click "Try it out"
3. Enter request body (use workspace_id from previous step):
```json
{
  "workspace_id": "your-workspace-id-here",
  "query": "Show me the architecture diagram"
}
```
4. Click "Execute"
5. See the AI-generated Mermaid diagram!

### 3. Check Database
```bash
cd backend

# View database (if you have sqlite3 installed)
sqlite3 devpilot.db
.tables
SELECT * FROM workspaces;
.quit
```

### 4. Monitor Logs
**Backend logs:** Check the terminal where uvicorn is running  
**Frontend logs:** Check the terminal where npm dev is running  
**Browser logs:** Open browser DevTools (F12) → Console tab

---

## 📊 System Requirements

### Minimum
- **RAM:** 4GB
- **Storage:** 2GB free space
- **CPU:** Dual-core processor
- **Internet:** Required for OpenAI API calls

### Recommended
- **RAM:** 8GB+
- **Storage:** 5GB free space
- **CPU:** Quad-core processor
- **Internet:** Stable broadband connection

---

## 🔐 Security Notes

### API Keys
- ⚠️ Never commit `.env` files to Git
- ⚠️ Never share your OpenAI API key
- ⚠️ Add `.env` to `.gitignore` (already done)

### Local Development
- ✅ Backend runs on localhost only
- ✅ No external access by default
- ✅ CORS configured for localhost:3000

---

## 📞 Getting Help

### Check Logs
**Backend errors:**
```bash
# Check the terminal where uvicorn is running
# Look for red error messages
```

**Frontend errors:**
```bash
# Check the terminal where npm dev is running
# Also check browser console (F12)
```

### Restart Everything
If things aren't working:
```bash
# Stop both terminals (Ctrl+C)

# Backend:
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal):
cd frontend
npm run dev
```

### Clean Restart
If you need to start fresh:
```bash
# Backend
cd backend
rm -rf venv devpilot.db chroma_data  # Mac/Linux
# OR
rmdir /s venv & del devpilot.db & rmdir /s chroma_data  # Windows

# Then redo backend setup from Step 2

# Frontend
cd frontend
rm -rf node_modules .next  # Mac/Linux
# OR
rmdir /s node_modules & rmdir /s .next  # Windows

# Then redo frontend setup from Step 3
```

---

## ✅ Success Indicators

You know everything is working when:

1. ✅ Backend terminal shows: "Application startup complete"
2. ✅ Frontend terminal shows: "ready started server"
3. ✅ http://localhost:8000/docs loads Swagger UI
4. ✅ http://localhost:8000/api/health returns JSON
5. ✅ http://localhost:3000 shows landing page
6. ✅ No red errors in either terminal
7. ✅ Browser console (F12) shows no errors

---

## 🎉 You're Ready to Build!

Your development environment is now fully set up and running. You can:

- ✅ Analyze GitHub repositories
- ✅ Process meeting transcripts
- ✅ Query AI modes for insights
- ✅ View API documentation
- ✅ Develop new features

**Happy coding! 🚀**

---

## 📚 Additional Resources

- **Architecture:** See `DEVPILOT_AI_ARCHITECTURE.md`
- **Implementation Status:** See `IMPLEMENTATION_STATUS.md`
- **API Reference:** http://localhost:8000/docs (when running)
- **OpenAI Docs:** https://platform.openai.com/docs
- **Next.js Docs:** https://nextjs.org/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com/