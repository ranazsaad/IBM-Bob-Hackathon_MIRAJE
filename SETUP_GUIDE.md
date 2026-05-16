# DevPilot AI - Quick Setup Guide

## Backend Setup (5 minutes)

### 1. Navigate to backend directory
```bash
cd devpilot-ai/backend
```

### 2. Create virtual environment
```bash
python -m venv venv
```

### 3. Activate virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Set up environment variables
```bash
# Copy example env file
copy .env.example .env  # Windows
# OR
cp .env.example .env    # Mac/Linux
```

### 6. Edit .env file
Open `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-key-here
```

### 7. Run the backend
```bash
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

---

## Frontend Setup (5 minutes)

### 1. Navigate to frontend directory
```bash
cd devpilot-ai/frontend
```

### 2. Install dependencies
```bash
npm install
```

### 3. Set up environment variables
```bash
# Copy example env file
copy .env.local.example .env.local  # Windows
# OR
cp .env.local.example .env.local    # Mac/Linux
```

### 4. Run the frontend
```bash
npm run dev
```

Frontend will be available at: `http://localhost:3000`

---

## Quick Test

1. Open `http://localhost:3000` in your browser
2. Enter a GitHub repository URL (e.g., `https://github.com/facebook/react`)
3. Click "Analyze Repository"
4. Wait for analysis to complete
5. Try different AI modes!

---

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
uvicorn app.main:app --reload --port 8001
```
Then update frontend `.env.local`: `NEXT_PUBLIC_API_URL=http://localhost:8001`

**OpenAI API errors:**
- Verify your API key is correct
- Check you have credits in your OpenAI account
- Ensure no extra spaces in the .env file

**Database errors:**
- Delete `devpilot.db` and restart the backend
- Check file permissions in the backend directory

### Frontend Issues

**Port 3000 already in use:**
```bash
npm run dev -- -p 3001
```

**API connection errors:**
- Verify backend is running on port 8000
- Check CORS settings in backend
- Verify `.env.local` has correct API URL

---

## Development Tips

### Backend Hot Reload
The backend automatically reloads when you save Python files (thanks to `--reload` flag)

### Frontend Hot Reload
Next.js automatically reloads when you save files

### View Logs
- Backend: Check terminal where uvicorn is running
- Frontend: Check browser console (F12)

### Database Inspection
Use SQLite browser or:
```bash
sqlite3 devpilot.db
.tables
SELECT * FROM workspaces;
```

---

## Next Steps

1. ✅ Backend running
2. ✅ Frontend running
3. ✅ Test with a repository
4. 🚀 Start building features!

Refer to `DEVPILOT_AI_ARCHITECTURE.md` for detailed architecture and implementation guide.