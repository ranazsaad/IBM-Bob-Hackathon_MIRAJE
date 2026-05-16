# 🚀 Push DevPilot AI to GitHub Repository

## 📋 Prerequisites

Before starting, you need:
- ✅ Git installed on your computer
- ✅ GitHub account
- ✅ The empty repository URL from your teammate
- ✅ Access permissions to the repository

---

## 🎯 Quick Push (5 Minutes)

### Step 1: Get Repository URL

Ask your teammate for the repository URL. It should look like:
```
https://github.com/username/devpilot-ai.git
```
or
```
git@github.com:username/devpilot-ai.git
```

### Step 2: Initialize Git (if not already done)

Open PowerShell in your project directory:

```powershell
cd C:\Users\Janaa\Desktop\devpilot-ai

# Check if git is already initialized
git status
```

**If you see "fatal: not a git repository"**, initialize it:
```powershell
git init
```

### Step 3: Add All Files

```powershell
# Add all files to git
git add .

# Check what will be committed
git status
```

### Step 4: Create First Commit

```powershell
git commit -m "Initial commit: DevPilot AI - Complete implementation with backend, frontend, and AI services"
```

### Step 5: Add Remote Repository

Replace `YOUR_REPO_URL` with the actual URL from your teammate:

```powershell
git remote add origin YOUR_REPO_URL
```

**Example:**
```powershell
git remote add origin https://github.com/yourteam/devpilot-ai.git
```

### Step 6: Push to GitHub

```powershell
# Push to main branch
git push -u origin main
```

**If you get an error about "master" vs "main":**
```powershell
# Rename branch to main
git branch -M main

# Push again
git push -u origin main
```

---

## 📝 Detailed Step-by-Step Guide

### 1. Check Git Installation

```powershell
# Check if git is installed
git --version
```

**Expected output:**
```
git version 2.x.x
```

**If not installed:**
- Download from: https://git-scm.com/download/win
- Install with default settings
- Restart PowerShell

---

### 2. Configure Git (First Time Only)

```powershell
# Set your name
git config --global user.name "Your Name"

# Set your email
git config --global user.email "your.email@example.com"

# Verify
git config --global --list
```

---

### 3. Navigate to Project

```powershell
cd C:\Users\Janaa\Desktop\devpilot-ai
```

---

### 4. Check Current Git Status

```powershell
git status
```

**Scenario A: "fatal: not a git repository"**
```powershell
# Initialize git
git init

# Verify
git status
```

**Scenario B: Already initialized**
```powershell
# You'll see current branch and file status
# Continue to next step
```

---

### 5. Review Files to Commit

```powershell
# See all files
git status

# See what's in .gitignore
Get-Content .gitignore
```

**Important files that SHOULD be committed:**
- ✅ All source code (`backend/app/`, `frontend/app/`)
- ✅ Configuration files (`package.json`, `requirements.txt`)
- ✅ Documentation (`.md` files)
- ✅ Docker files
- ✅ `.gitignore`

**Files that should NOT be committed (already in .gitignore):**
- ❌ `backend/venv/` (virtual environment)
- ❌ `backend/.env` (contains API keys!)
- ❌ `frontend/node_modules/` (dependencies)
- ❌ `frontend/.next/` (build files)
- ❌ `backend/devpilot.db` (database)
- ❌ `backend/chroma_data/` (vector store)

---

### 6. Create .gitignore (if missing)

```powershell
# Check if .gitignore exists
Test-Path .gitignore
```

**If False, create it:**

```powershell
# Create .gitignore
New-Item .gitignore -ItemType File
```

Then add this content to `.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
*.egg-info/
.pytest_cache/
.coverage

# Environment variables
.env
.env.local
.env.*.local

# Database
*.db
*.sqlite
*.sqlite3

# Vector Store
chroma_data/

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*

# Next.js
.next/
out/
build/
dist/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log
```

---

### 7. Add Files to Git

```powershell
# Add all files
git add .

# Check what was added
git status
```

**You should see:**
```
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        new file:   backend/app/main.py
        new file:   frontend/package.json
        ... (many more files)
```

---

### 8. Create Initial Commit

```powershell
git commit -m "Initial commit: DevPilot AI - Complete hackathon project

- Backend: FastAPI with 5 AI modes (Illustration, Development, Testing, Deployment, Documentation)
- Frontend: Next.js 14 with landing page and workspace UI
- AI Integration: Bob/Cline API with Claude 3.5 Sonnet
- Database: SQLite + ChromaDB vector store
- Features: GitHub repo analysis, meeting transcript processing, RAG pipeline
- Documentation: Complete setup and debugging guides
- Docker: Containerization configs for deployment"
```

**Verify commit:**
```powershell
git log --oneline
```

---

### 9. Add Remote Repository

**Get the repository URL from your teammate.**

**Format 1: HTTPS (Recommended for beginners)**
```
https://github.com/username/devpilot-ai.git
```

**Format 2: SSH (Requires SSH key setup)**
```
git@github.com:username/devpilot-ai.git
```

**Add the remote:**
```powershell
git remote add origin https://github.com/username/devpilot-ai.git
```

**Verify:**
```powershell
git remote -v
```

**Expected output:**
```
origin  https://github.com/username/devpilot-ai.git (fetch)
origin  https://github.com/username/devpilot-ai.git (push)
```

---

### 10. Push to GitHub

```powershell
# Push to main branch
git push -u origin main
```

**If you get "branch main does not exist" error:**
```powershell
# Rename current branch to main
git branch -M main

# Push again
git push -u origin main
```

**You'll be prompted for GitHub credentials:**
- Username: Your GitHub username
- Password: Your GitHub Personal Access Token (NOT your password!)

---

### 11. Verify on GitHub

1. Open your browser
2. Go to the repository URL
3. You should see all your files!

---

## 🔐 GitHub Authentication

### Option 1: Personal Access Token (Recommended)

**Create a token:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name: "DevPilot AI Push"
4. Select scopes: `repo` (full control)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again!)

**Use the token:**
```powershell
# When prompted for password, paste the token
Username: your-github-username
Password: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Option 2: GitHub CLI (Alternative)

```powershell
# Install GitHub CLI
winget install --id GitHub.cli

# Authenticate
gh auth login

# Follow the prompts
```

---

## 🐛 Common Issues & Solutions

### Issue 1: "fatal: remote origin already exists"

**Solution:**
```powershell
# Remove existing remote
git remote remove origin

# Add correct remote
git remote add origin YOUR_REPO_URL
```

---

### Issue 2: "failed to push some refs"

**Cause:** Remote has commits you don't have locally

**Solution:**
```powershell
# Pull first (if remote is not empty)
git pull origin main --allow-unrelated-histories

# Then push
git push -u origin main
```

---

### Issue 3: "Support for password authentication was removed"

**Cause:** GitHub no longer accepts passwords

**Solution:** Use Personal Access Token (see Authentication section above)

---

### Issue 4: Large files rejected

**Error:**
```
remote: error: File is too large
```

**Solution:**
```powershell
# Check file sizes
Get-ChildItem -Recurse | Where-Object {$_.Length -gt 50MB} | Select-Object FullName, Length

# Add large files to .gitignore
# Remove from git if already added
git rm --cached path/to/large/file
```

---

### Issue 5: .env file accidentally committed

**⚠️ CRITICAL: If you committed .env with API keys:**

```powershell
# Remove from git history
git rm --cached backend/.env

# Add to .gitignore
echo "backend/.env" >> .gitignore

# Commit the change
git commit -m "Remove .env file from git"

# Force push (⚠️ only if you haven't shared the repo yet)
git push -f origin main

# IMPORTANT: Rotate your API keys immediately!
# The old keys are now exposed in git history
```

---

## 📋 Complete Command Sequence

**Copy and paste this (replace YOUR_REPO_URL):**

```powershell
# Navigate to project
cd C:\Users\Janaa\Desktop\devpilot-ai

# Initialize git (if needed)
git init

# Configure git (first time only)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Add all files
git add .

# Create commit
git commit -m "Initial commit: DevPilot AI - Complete implementation"

# Add remote
git remote add origin YOUR_REPO_URL

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

---

## 🎯 After Pushing

### 1. Verify on GitHub
- Check all files are there
- Verify .env is NOT there
- Check README.md displays correctly

### 2. Add README.md to Root (if missing)

Create `devpilot-ai/README.md`:

```markdown
# 🚀 DevPilot AI

AI-powered developer workspace for code analysis, development, testing, deployment, and documentation.

## 🌟 Features

- **5 AI Modes**: Illustration, Development, Testing, Deployment, Documentation
- **GitHub Analysis**: Analyze any public repository
- **Meeting Transcripts**: Convert meetings to engineering tickets
- **RAG Pipeline**: Intelligent code search with embeddings
- **Modern Stack**: FastAPI + Next.js 14 + Claude 3.5 Sonnet

## 🚀 Quick Start

See [COMPLETE_SETUP_AND_DEBUG_GUIDE.md](./COMPLETE_SETUP_AND_DEBUG_GUIDE.md)

## 📚 Documentation

- [Complete Setup Guide](./COMPLETE_SETUP_AND_DEBUG_GUIDE.md)
- [Quick Fix Checklist](./QUICK_FIX_CHECKLIST.md)
- [Bob API Setup](./BOB_API_SETUP_GUIDE.md)

## 🛠️ Tech Stack

**Backend:** FastAPI, Python 3.12, SQLite, ChromaDB  
**Frontend:** Next.js 14, React 18, TailwindCSS  
**AI:** Bob/Cline API (Claude 3.5 Sonnet)

## 📄 License

MIT License - See LICENSE file for details
```

Then commit and push:
```powershell
git add README.md
git commit -m "Add README.md"
git push origin main
```

### 3. Set Up Branch Protection (Optional)

On GitHub:
1. Go to repository Settings
2. Branches → Add rule
3. Branch name pattern: `main`
4. Enable: "Require pull request reviews before merging"

### 4. Add Collaborators

On GitHub:
1. Go to repository Settings
2. Collaborators → Add people
3. Add your teammates

---

## 🔄 Future Updates

**To push changes later:**

```powershell
# Make your changes to files

# Check what changed
git status

# Add changes
git add .

# Commit
git commit -m "Description of changes"

# Push
git push origin main
```

---

## 📊 Git Workflow Summary

```
Local Changes → git add → git commit → git push → GitHub
     ↓              ↓           ↓            ↓          ↓
  Edit files   Stage files  Save locally  Upload   Visible online
```

---

## ✅ Checklist

Before pushing:
- [ ] Git installed and configured
- [ ] Repository URL from teammate
- [ ] .gitignore file exists
- [ ] .env file is in .gitignore
- [ ] No sensitive data in code
- [ ] All files added with `git add .`
- [ ] Commit created
- [ ] Remote added
- [ ] Ready to push!

After pushing:
- [ ] Verified files on GitHub
- [ ] .env is NOT visible
- [ ] README.md displays correctly
- [ ] Teammates can access
- [ ] Documentation is readable

---

## 🎉 You're Done!

Your DevPilot AI project is now on GitHub and your team can:
- ✅ Clone the repository
- ✅ Collaborate on code
- ✅ Track changes
- ✅ Deploy from GitHub

**Next steps:**
1. Share repository URL with team
2. Set up CI/CD (optional)
3. Deploy to production (optional)

---

## 📞 Need Help?

**Common Git commands:**
```powershell
git status          # Check current state
git log             # View commit history
git branch          # List branches
git remote -v       # View remotes
git pull            # Get latest changes
git push            # Upload changes
```

**Undo commands:**
```powershell
git restore <file>          # Undo changes to file
git reset HEAD~1            # Undo last commit (keep changes)
git reset --hard HEAD~1     # Undo last commit (delete changes)
```

**Get help:**
```powershell
git help <command>    # Get help for any command
git --help            # General help