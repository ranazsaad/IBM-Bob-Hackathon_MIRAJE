# 🚀 DevPilot AI - Quick Reference Card

## ⚡ Quick Start Commands

### Backend (Terminal 1)
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python test_api.py  # Test API connection
uvicorn app.main:app --reload --port 8000
```

### Frontend (Terminal 2)
```bash
cd frontend
npm install
npm run dev
```

### Access Points
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 🔑 Configuration Files

### Backend: `backend/.env`
```env
OPENAI_API_KEY=bob_prod_YOUR_KEY_HERE
OPENAI_API_BASE=https://api.cline.bot/v1
OPENAI_MODEL=claude-3-5-sonnet-20241022
DATABASE_URL=sqlite:///./devpilot.db
```

### Frontend: `frontend/.env.local`
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

---

## 🎯 Test Repositories

Quick test URLs for GitHub analysis:
- Small: `https://github.com/pallets/flask`
- Medium: `https://github.com/facebook/react`
- Large: `https://github.com/microsoft/vscode`

---

## 🧪 Sample Queries by Mode

### 🎨 Illustration Mode
- "Generate an architecture diagram"
- "Show me the data flow"
- "Create a dependency map"

### 💻 Development Mode
- "Review code quality"
- "Find security vulnerabilities"
- "Suggest refactoring improvements"

### 🧪 Testing Mode
- "Generate unit tests for main module"
- "Create integration test scenarios"
- "Identify untested edge cases"

### 🚀 Deployment Mode
- "Generate a production Dockerfile"
- "Create GitHub Actions CI/CD pipeline"
- "Generate Kubernetes manifests"

### 📚 Documentation Mode
- "Generate comprehensive README"
- "Create API documentation"
- "Write onboarding guide"

---

## 🐛 Common Issues & Quick Fixes

### Backend won't start
```bash
# Check if port is in use
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Use different port
uvicorn app.main:app --reload --port 8001
```

### Frontend won't start
```bash
# Clear and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### API 401 Error
```bash
# Get fresh API key from Cline
# Update backend/.env
# Restart backend server
```

### Can't connect to backend
```bash
# Verify backend is running
curl http://localhost:8000/api/health

# Check frontend .env.local has correct URL
```

---

## 📊 Health Check Commands

### Backend Health
```bash
curl http://localhost:8000/api/health
```

Expected: `{"status":"healthy","version":"1.0.0"}`

### Test Bob API
```bash
cd backend
python test_api.py
```

Expected: `[SUCCESS] Bob API is working!`

---

## 🔄 Restart Everything

### Stop All
```bash
# Press Ctrl+C in both terminals
```

### Start Fresh
```bash
# Terminal 1 - Backend
cd backend
venv\Scripts\activate  # or source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

---

## 📁 Key Files to Know

### Backend
- [`backend/app/main.py`](backend/app/main.py) - Application entry point
- [`backend/app/config.py`](backend/app/config.py) - Configuration
- [`backend/app/services/ai_orchestrator.py`](backend/app/services/ai_orchestrator.py) - AI modes
- [`backend/.env`](backend/.env) - Environment variables

### Frontend
- [`frontend/src/app/page.tsx`](frontend/src/app/page.tsx) - Landing page
- [`frontend/src/app/workspace/page.tsx`](frontend/src/app/workspace/page.tsx) - Main workspace
- [`frontend/src/lib/api.ts`](frontend/src/lib/api.ts) - API client
- [`frontend/.env.local`](frontend/.env.local) - Environment variables

---

## 🎯 Success Indicators

✅ Backend terminal shows:
```
[DevPilot] Starting DevPilot AI Backend...
[DevPilot] Database initialized
INFO: Application startup complete.
```

✅ Frontend terminal shows:
```
✓ Ready in 2.5s
```

✅ Browser shows:
- Landing page loads at http://localhost:3000
- API docs load at http://localhost:8000/docs
- No errors in console

---

## 📚 Documentation

- **Complete Setup:** [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)
- **Quick Start:** [QUICK_START.md](QUICK_START.md)
- **Architecture:** [README.md](README.md)
- **Status:** [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)

---

## 🆘 Emergency Reset

If everything is broken:

```bash
# Backend
cd backend
rm -rf venv __pycache__ *.db chroma_data
python -m venv venv
# Activate venv
pip install -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules .next package-lock.json
npm install

# Restart both servers
```

---

**Need detailed help?** See [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)