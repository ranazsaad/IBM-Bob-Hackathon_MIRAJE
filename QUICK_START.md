# 🚀 DevPilot AI - Quick Start (5 Minutes)

**For experienced developers who want to get running FAST.**

---

## ⚡ Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API Key

---

## 🏃 Quick Setup

### 1. Backend (2 minutes)

```bash
# Navigate to backend
cd devpilot-ai/backend

# Setup Python environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env  # Windows
# cp .env.example .env  # Mac/Linux

# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=sk-proj-xxxxx

# Start backend
uvicorn app.main:app --reload --port 8000
```

**✅ Backend running at:** http://localhost:8000  
**✅ API Docs at:** http://localhost:8000/docs

---

### 2. Frontend (2 minutes)

**Open a NEW terminal:**

```bash
# Navigate to frontend
cd devpilot-ai/frontend

# Install dependencies
npm install

# Configure environment
copy .env.local.example .env.local  # Windows
# cp .env.local.example .env.local  # Mac/Linux

# Start frontend
npm run dev
```

**✅ Frontend running at:** http://localhost:3000

---

## 🧪 Quick Test

### Test 1: Health Check
```bash
curl http://localhost:8000/api/health
```

Expected: `{"status":"healthy","version":"1.0.0",...}`

### Test 2: API Docs
Open: http://localhost:8000/docs

### Test 3: Frontend
Open: http://localhost:3000

### Test 4: GitHub Analysis
1. Go to http://localhost:3000
2. Enter: `https://github.com/facebook/react`
3. Click "Analyze Repository"
4. Check backend terminal for logs

---

## 🐳 Docker Alternative (1 minute)

```bash
cd devpilot-ai

# Setup backend env
cd backend
copy .env.example .env  # Add your OpenAI API key
cd ..

# Start everything
docker-compose up -d

# View logs
docker-compose logs -f
```

**Access:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

**Stop:**
```bash
docker-compose down
```

---

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Backend - use different port
uvicorn app.main:app --reload --port 8001

# Frontend - use different port
npm run dev -- -p 3001
```

### Module Not Found
```bash
# Backend
pip install -r requirements.txt

# Frontend
rm -rf node_modules && npm install
```

### OpenAI API Errors
- Check API key in `backend/.env`
- Verify credits at: https://platform.openai.com/account/usage

---

## 📚 Full Documentation

For detailed setup instructions, see:
- **Complete Guide:** `LOCAL_SETUP_GUIDE.md`
- **Architecture:** `DEVPILOT_AI_ARCHITECTURE.md`
- **Status:** `IMPLEMENTATION_STATUS.md`

---

## ✅ You're Ready!

Both servers running? Great! Now you can:

1. **Test API:** http://localhost:8000/docs
2. **Use Frontend:** http://localhost:3000
3. **Analyze Repos:** Enter any GitHub URL
4. **Query AI Modes:** Use the 5 specialized modes

**Happy hacking! 🎉**