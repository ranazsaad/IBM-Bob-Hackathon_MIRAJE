# 🔧 Configuration Guide

## Quick Setup (3 Steps)

### 1. Configure Bob/Cline API Key

Edit `backend/.env` and add your Bob API key:

```bash
OPENAI_API_KEY=bob_prod_bob-user_YOUR_KEY_HERE
```

**Where to get your Bob API key:**
- Go to Bob/Cline settings in VS Code
- Copy your API key
- Paste it in the `.env` file

### 2. (Optional) Configure IBM Watson for Speech-to-Text

If you want to use the Live Meeting feature with real-time transcription:

```bash
WATSON_STT_API_KEY=your_watson_stt_api_key
IBM_CLOUD_API_KEY=your_ibm_cloud_api_key
WATSONX_PROJECT_ID=your_watsonx_project_id
```

**Where to get IBM credentials:**
- Sign up at https://cloud.ibm.com
- Create a Watson Speech-to-Text service
- Copy the API key and URL

### 3. (Optional) Configure GitHub Token

For better GitHub API rate limits:

```bash
GITHUB_TOKEN=ghp_your_github_token_here
```

**Where to get GitHub token:**
- Go to https://github.com/settings/tokens
- Generate a new token (classic)
- Select `repo` scope
- Copy and paste in `.env`

---

## Current Configuration Status

### ✅ Working Without API Keys:
- **Illustration Mode**: ✅ Works with repository metadata (no API needed)
- **GitHub Analysis**: ✅ Works with public repos (60 requests/hour limit)
- **Workspace Management**: ✅ Fully functional

### ⚠️ Requires Bob API Key:
- **AI-Powered Explanations**: Needs Bob/Cline API key
- **Code Analysis**: Needs Bob/Cline API key
- **Smart Suggestions**: Needs Bob/Cline API key

### ⚠️ Requires IBM Watson:
- **Live Meeting Transcription**: Needs Watson STT API key
- **Real-time Speech-to-Text**: Needs Watson STT API key

---

## Testing Your Configuration

### Test 1: Check if backend is running
```bash
curl http://localhost:8000/
```
Expected: `{"message":"DevPilot AI Backend","version":"1.0.0"}`

### Test 2: Test GitHub Analysis (No API key needed)
```bash
curl -X POST http://localhost:8000/api/analyze/github \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/torvalds/linux"}'
```
Expected: Returns workspace_id and metadata

### Test 3: Test Illustration Mode (Works with metadata)
```bash
curl -X POST http://localhost:8000/api/modes/illustration/query \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "YOUR_WORKSPACE_ID",
    "query": "Explain the architecture"
  }'
```
Expected: Returns Mermaid diagram and explanation

---

## Troubleshooting

### "Bob API Not configured"
- **Solution**: Add your Bob/Cline API key to `backend/.env`
- **File**: `backend/.env`
- **Line**: `OPENAI_API_KEY=bob_prod_bob-user_YOUR_KEY_HERE`

### "GitHub rate limit exceeded"
- **Solution**: Add a GitHub token to `backend/.env`
- **File**: `backend/.env`
- **Line**: `GITHUB_TOKEN=ghp_your_token_here`

### "Watson STT not available"
- **Solution**: Add Watson credentials to `backend/.env`
- **File**: `backend/.env`
- **Lines**: 
  ```
  WATSON_STT_API_KEY=your_key
  IBM_CLOUD_API_KEY=your_key
  ```

---

## What Works Without Configuration?

### ✅ Fully Functional (No API Keys Needed):
1. **Repository Analysis**: Fetch GitHub repo metadata
2. **Illustration Mode**: Generate diagrams from metadata
3. **Workspace Management**: Create and manage workspaces
4. **File Structure**: View repository structure
5. **Basic Explanations**: Metadata-based explanations

### 🔑 Requires API Keys:
1. **AI-Powered Analysis**: Deep code analysis (needs Bob API)
2. **Smart Suggestions**: AI-generated suggestions (needs Bob API)
3. **Live Transcription**: Real-time speech-to-text (needs Watson)
4. **Code Embeddings**: Vector search (needs Bob/IBM API)

---

## Next Steps

1. **Add Bob API Key** → Get AI-powered features
2. **Add GitHub Token** → Avoid rate limits
3. **Add Watson Keys** → Enable live meeting transcription

**Need help?** Check `API_TROUBLESHOOTING_GUIDE.md`