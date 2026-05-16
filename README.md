# DevPilot AI 🚀

**Your AI Engineering Teammate for Hackathons and Beyond**

An AI-powered developer workspace that analyzes codebases and meeting transcripts to help developers understand, develop, test, deploy, and document software through intelligent AI agents.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 What is DevPilot AI?

DevPilot AI transforms how developers interact with codebases by providing **5 specialized AI modes** that act as your engineering teammates:

- 🎨 **Illustration Mode** - Visual architecture diagrams, dependency maps, component relationships
- 💻 **Development Mode** - Code reviews, refactoring suggestions, security analysis
- 🧪 **Testing Mode** - Automated test generation with coverage analysis
- 🚀 **Deployment Mode** - Docker, CI/CD pipelines, Kubernetes configurations
- 📚 **Documentation Mode** - README, API docs, onboarding guides

**Plus:** Meeting transcript processing that extracts requirements, generates user stories, and creates engineering tickets.

---

## ✨ Key Features

### For Developers
✅ **Instant Codebase Understanding** - Analyze any GitHub repository in seconds  
✅ **AI-Powered Insights** - Get architectural explanations and code reviews  
✅ **Test Generation** - Automatically generate unit and integration tests  
✅ **Infrastructure as Code** - Generate Docker, CI/CD, and deployment configs  
✅ **Smart Documentation** - Auto-generate comprehensive documentation  

### For Teams
✅ **Meeting → Code** - Transform meeting notes into actionable tickets  
✅ **User Story Generation** - AI-powered requirement extraction  
✅ **Onboarding Acceleration** - Help new developers understand codebases faster  
✅ **Best Practices** - Get recommendations based on industry standards  

### Technical Highlights
✅ **RAG Pipeline** - Retrieval Augmented Generation with vector search  
✅ **Multi-Modal AI** - Specialized agents for different engineering tasks  
✅ **Real-time Analysis** - Fast GitHub API integration (no cloning needed)  
✅ **Production Ready** - Docker, type safety, comprehensive error handling  

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))

### 5-Minute Setup

**1. Backend Setup**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env  # Add your OPENAI_API_KEY
uvicorn app.main:app --reload --port 8000
```

**2. Frontend Setup** (New Terminal)
```bash
cd frontend
npm install
copy .env.local.example .env.local
npm run dev
```

**3. Open Your Browser**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

**📖 Detailed Instructions:** See [LOCAL_SETUP_GUIDE.md](LOCAL_SETUP_GUIDE.md)

---

## 🎬 Demo Usage

### Analyze a GitHub Repository

1. Go to http://localhost:3000
2. Enter a repository URL: `https://github.com/facebook/react`
3. Click "Analyze Repository"
4. Wait 10-30 seconds for analysis
5. Explore the 5 AI modes!

### Process Meeting Transcript

1. Click "Meeting Transcript" tab
2. Paste your meeting notes
3. Add context (e.g., "Sprint planning")
4. Click "Process Transcript"
5. Get user stories and engineering tickets!

### Query AI Modes

Use the API directly at http://localhost:8000/docs:

**Example: Generate Architecture Diagram**
```bash
POST /api/modes/illustration/query
{
  "workspace_id": "your-workspace-id",
  "query": "Show me the system architecture"
}
```

**Example: Generate Tests**
```bash
POST /api/modes/testing/query
{
  "workspace_id": "your-workspace-id",
  "query": "Generate unit tests for the authentication module"
}
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js 14)                     │
│  React • TypeScript • TailwindCSS • Monaco Editor           │
└─────────────────────────────────────────────────────────────┘
                              ↕ REST API
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   GitHub     │  │  Transcript  │  │      AI      │     │
│  │   Analyzer   │  │  Processor   │  │ Orchestrator │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│              Data Layer (SQLite + ChromaDB)                  │
│  Vector Search • Embeddings • Workspace Management          │
└─────────────────────────────────────────────────────────────┘
```

**📖 Detailed Architecture:** See [DEVPILOT_AI_ARCHITECTURE.md](DEVPILOT_AI_ARCHITECTURE.md)

---

## 🛠️ Technology Stack

### Backend
- **Framework:** FastAPI 0.109
- **Language:** Python 3.11+
- **Database:** SQLite + SQLAlchemy
- **Vector Store:** ChromaDB
- **AI:** OpenAI GPT-4 + Embeddings
- **GitHub:** PyGithub API

### Frontend
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript 5.3
- **Styling:** TailwindCSS 3.4
- **Components:** shadcn/ui
- **Editor:** Monaco Editor
- **Diagrams:** Mermaid.js

### DevOps
- **Containerization:** Docker + Docker Compose
- **CI/CD:** GitHub Actions (ready)
- **Deployment:** Vercel (frontend) + Railway (backend)

---

## 📁 Project Structure

```
devpilot-ai/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── main.py            # Application entry
│   │   ├── config.py          # Configuration
│   │   ├── api/               # API routes & schemas
│   │   ├── services/          # Business logic
│   │   │   ├── github_analyzer.py
│   │   │   ├── transcript_processor.py
│   │   │   ├── rag_engine.py
│   │   │   ├── ai_orchestrator.py
│   │   │   └── embedding_service.py
│   │   └── database/          # Database models
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                   # Next.js Frontend
│   ├── src/
│   │   ├── app/               # Pages
│   │   ├── components/        # React components
│   │   └── lib/               # Utilities & API client
│   ├── package.json
│   └── Dockerfile
│
├── docs/                       # Documentation
│   ├── DEVPILOT_AI_ARCHITECTURE.md
│   ├── LOCAL_SETUP_GUIDE.md
│   ├── IMPLEMENTATION_STATUS.md
│   └── QUICK_START.md
│
├── docker-compose.yml
└── README.md
```

---

## 🎨 Screenshots

### Landing Page
Beautiful gradient design with dual input modes (GitHub + Transcript)

### API Documentation
Interactive Swagger UI with all endpoints documented

### AI Modes
5 specialized modes for different engineering tasks

---

## 🧪 API Endpoints

### Analysis
- `POST /api/analyze/github` - Analyze GitHub repository
- `POST /api/analyze/transcript` - Process meeting transcript

### AI Modes
- `POST /api/modes/illustration/query` - Generate diagrams
- `POST /api/modes/development/query` - Code review
- `POST /api/modes/testing/query` - Generate tests
- `POST /api/modes/deployment/query` - Infrastructure configs
- `POST /api/modes/documentation/query` - Generate docs

### Workspace
- `GET /api/workspace/{id}` - Get workspace details
- `GET /api/workspace/{id}/files` - List workspace files
- `DELETE /api/workspace/{id}` - Delete workspace

**📖 Full API Reference:** http://localhost:8000/docs (when running)

---

## 🔧 Configuration

### Backend Environment Variables
```env
# Required
OPENAI_API_KEY=sk-proj-xxxxx

# Optional
GITHUB_TOKEN=ghp_xxxxx
DATABASE_URL=sqlite:///./devpilot.db
OPENAI_MODEL=gpt-4-turbo-preview
```

### Frontend Environment Variables
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

---

## 🐳 Docker Deployment

### Development
```bash
docker-compose up -d
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

**Access:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

---

## 📊 Performance

- **GitHub Analysis:** 10-30 seconds (depends on repo size)
- **AI Query Response:** 2-5 seconds
- **Transcript Processing:** 15-45 seconds
- **Vector Search:** <100ms

---

## 🤝 Contributing

This is a hackathon project, but contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- **OpenAI** - GPT-4 and Embeddings API
- **FastAPI** - Modern Python web framework
- **Next.js** - React framework
- **ChromaDB** - Vector database
- **shadcn/ui** - Beautiful UI components

---

## 📞 Support

### Documentation
- **Complete Setup:** [LOCAL_SETUP_GUIDE.md](LOCAL_SETUP_GUIDE.md)
- **Quick Start:** [QUICK_START.md](QUICK_START.md)
- **Architecture:** [DEVPILOT_AI_ARCHITECTURE.md](DEVPILOT_AI_ARCHITECTURE.md)
- **Status:** [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)

### Issues
- Check existing issues on GitHub
- Create a new issue with detailed description
- Include error logs and environment details

---

## 🎯 Roadmap

### Current (v1.0)
- ✅ GitHub repository analysis
- ✅ 5 specialized AI modes
- ✅ Meeting transcript processing
- ✅ RAG pipeline with vector search
- ✅ Docker deployment

### Future (v2.0)
- [ ] Real-time collaboration
- [ ] Custom AI model fine-tuning
- [ ] Multi-language support
- [ ] IDE extensions (VS Code, JetBrains)
- [ ] Team workspaces
- [ ] Advanced analytics dashboard

---

## ⭐ Star History

If you find DevPilot AI useful, please consider giving it a star! ⭐

---

## 📈 Stats

- **Lines of Code:** 10,000+
- **Files Created:** 50+
- **Documentation:** 2,500+ lines
- **API Endpoints:** 12
- **AI Modes:** 5
- **Development Time:** 48 hours (hackathon)

---

## 🎉 Built for Hackathon 2026

DevPilot AI was built as a demonstration of modern AI-powered development tools. It showcases:

- Production-quality code architecture
- Real-world AI integration
- Full-stack development best practices
- Comprehensive documentation
- Docker deployment readiness

**Ready to revolutionize your development workflow? Get started now! 🚀**

---

Made with ❤️ by the DevPilot AI Team