# 🔑 IBM Hackathon - Complete API Credentials Guide

## 📋 Overview

This guide shows you how to get ALL the IBM API credentials needed for DevPilot AI.

**Required IBM Services:**
1. ✅ IBM Cloud Account
2. ✅ IBM watsonx.ai (Granite models)
3. ✅ IBM Watson Speech to Text (optional)
4. ✅ IBM Cloud API Key

**Time Required:** 15-20 minutes

---

## 🚀 Step 1: Create IBM Cloud Account (5 minutes)

### 1.1 Sign Up

1. Go to https://cloud.ibm.com/registration
2. Fill in your details:
   - Email address
   - First and last name
   - Country/Region
   - Password
3. Verify your email
4. Complete account setup

**✅ You now have an IBM Cloud account!**

---

## 🔑 Step 2: Get IBM Cloud API Key (2 minutes)

### 2.1 Create API Key

1. **Log in to IBM Cloud:** https://cloud.ibm.com
2. **Click your profile** (top right) → **Profile and settings**
3. **Go to:** API keys section
4. **Click:** "Create an IBM Cloud API key"
5. **Name it:** "DevPilot AI Hackathon"
6. **Click:** "Create"
7. **IMPORTANT:** Copy and save the API key immediately!

**Your API key looks like:**
```
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**⚠️ Save this key securely - you won't see it again!**

### 2.2 Verify API Key

```bash
# Test your API key
curl -X POST "https://iam.cloud.ibm.com/identity/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=YOUR_API_KEY"
```

**Expected:** You'll get an access token response

---

## 🤖 Step 3: Set Up watsonx.ai (5 minutes)

### 3.1 Create watsonx.ai Project

1. **Go to:** https://dataplatform.cloud.ibm.com
2. **Sign in** with your IBM Cloud account
3. **Click:** "Create a project" or "New project"
4. **Select:** "Create an empty project"
5. **Name it:** "DevPilot AI"
6. **Add description:** "AI-powered developer workspace"
7. **Click:** "Create"

### 3.2 Get Project ID

1. **In your project**, click **"Manage"** tab
2. **Go to:** "General" section
3. **Copy the Project ID** (looks like: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

**Save this Project ID!**

### 3.3 Associate watsonx.ai Service

1. **In your project**, go to **"Manage"** → **"Services & integrations"**
2. **Click:** "Associate service"
3. **Select:** "Watson Machine Learning"
4. **Choose:** Existing service or create new
5. **Click:** "Associate"

### 3.4 Get watsonx.ai URL

**Default URLs by region:**
- **US South:** `https://us-south.ml.cloud.ibm.com`
- **EU Germany:** `https://eu-de.ml.cloud.ibm.com`
- **Japan Tokyo:** `https://jp-tok.ml.cloud.ibm.com`

**To find your region:**
1. Go to your IBM Cloud dashboard
2. Check the region selector (top right)
3. Use the corresponding URL above

---

## 🎤 Step 4: Set Up Watson Speech to Text (Optional, 3 minutes)

### 4.1 Create Service

1. **Go to:** https://cloud.ibm.com/catalog/services/speech-to-text
2. **Select region:** Same as your watsonx.ai
3. **Select plan:** Lite (free) or Standard
4. **Name it:** "DevPilot STT"
5. **Click:** "Create"

### 4.2 Get Credentials

1. **In the service page**, click **"Manage"**
2. **Copy:**
   - API Key
   - URL (e.g., `https://api.us-south.speech-to-text.watson.cloud.ibm.com`)

**Save both values!**

---

## 📝 Step 5: Configure DevPilot AI

### 5.1 Update .env File

**Open:** `C:\Users\Janaa\Desktop\devpilot-ai\backend\.env`

**Replace with your credentials:**

```env
# ============================================================
# IBM CLOUD CREDENTIALS
# ============================================================
IBM_CLOUD_API_KEY=your_ibm_cloud_api_key_here
IBM_CLOUD_REGION=us-south

# ============================================================
# IBM WATSONX.AI
# ============================================================
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Granite Model Configuration
WATSONX_MODEL_ID=ibm/granite-3-8b-instruct
WATSONX_EMBEDDING_MODEL=ibm/slate-125m-english-rtrvr

# Model Parameters
MAX_TOKENS=4096
TEMPERATURE=0.7
TOP_P=1.0
TOP_K=50

# ============================================================
# IBM WATSON SPEECH TO TEXT (Optional)
# ============================================================
WATSON_STT_API_KEY=your_watson_stt_api_key_here
WATSON_STT_URL=https://api.us-south.speech-to-text.watson.cloud.ibm.com

# ============================================================
# DATABASE & VECTOR STORE
# ============================================================
DATABASE_URL=sqlite:///./devpilot.db
CHROMA_PERSIST_DIRECTORY=./chroma_data

# ============================================================
# SERVER CONFIGURATION
# ============================================================
HOST=0.0.0.0
PORT=8000
RELOAD=true
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# ============================================================
# GITHUB (Optional)
# ============================================================
GITHUB_TOKEN=

# ============================================================
# APPLICATION
# ============================================================
APP_NAME=DevPilot AI
APP_VERSION=1.0.0
DEBUG=true
```

### 5.2 Credential Mapping

**What you need to fill in:**

| Variable | Where to Get It | Example |
|----------|----------------|---------|
| `IBM_CLOUD_API_KEY` | IBM Cloud → Profile → API Keys | `xxxxxxxxxxxx...` |
| `IBM_CLOUD_REGION` | IBM Cloud region selector | `us-south` |
| `WATSONX_PROJECT_ID` | watsonx.ai project → Manage → General | `xxxxxxxx-xxxx-...` |
| `WATSONX_URL` | Based on your region | `https://us-south.ml.cloud.ibm.com` |
| `WATSON_STT_API_KEY` | Watson STT service → Manage | `xxxxxxxxxxxx...` |
| `WATSON_STT_URL` | Watson STT service → Manage | `https://api.us-south...` |

---

## ✅ Step 6: Verify Setup

### 6.1 Test IBM Cloud API Key

```powershell
cd C:\Users\Janaa\Desktop\devpilot-ai\backend
.\venv\Scripts\activate
python -c "from app.config import settings; print(f'IBM API Key: {settings.IBM_CLOUD_API_KEY[:10]}...')"
```

**Expected:** Shows first 10 characters of your API key

### 6.2 Test watsonx.ai Connection

```powershell
python test_ibm_api.py
```

**Expected:**
```
[SUCCESS] IBM watsonx.ai is working!
[Response] Hello from DevPilot AI!
```

---

## 🎯 Quick Reference

### All Required Credentials

```env
# REQUIRED
IBM_CLOUD_API_KEY=________________________
WATSONX_PROJECT_ID=________________________
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# OPTIONAL
WATSON_STT_API_KEY=________________________
WATSON_STT_URL=https://api.us-south.speech-to-text.watson.cloud.ibm.com
GITHUB_TOKEN=________________________
```

### IBM Cloud Regions

| Region | Code | watsonx.ai URL |
|--------|------|----------------|
| US South (Dallas) | `us-south` | `https://us-south.ml.cloud.ibm.com` |
| US East (Washington DC) | `us-east` | `https://us-east.ml.cloud.ibm.com` |
| EU Germany (Frankfurt) | `eu-de` | `https://eu-de.ml.cloud.ibm.com` |
| EU UK (London) | `eu-gb` | `https://eu-gb.ml.cloud.ibm.com` |
| Japan (Tokyo) | `jp-tok` | `https://jp-tok.ml.cloud.ibm.com` |
| Japan (Osaka) | `jp-osa` | `https://jp-osa.ml.cloud.ibm.com` |

### Available Granite Models

| Model ID | Description | Use Case |
|----------|-------------|----------|
| `ibm/granite-3-8b-instruct` | 8B instruction-tuned | General AI tasks |
| `ibm/granite-3-2b-instruct` | 2B instruction-tuned | Lightweight tasks |
| `ibm/granite-3-guardian` | Safety & moderation | Content filtering |
| `ibm/granite-20b-multilingual` | 20B multilingual | Multi-language support |

### Available Embedding Models

| Model ID | Description |
|----------|-------------|
| `ibm/slate-125m-english-rtrvr` | 125M English retrieval |
| `ibm/slate-30m-english-rtrvr` | 30M English retrieval |

---

## 🐛 Troubleshooting

### Issue 1: "Invalid API Key"

**Check:**
- [ ] API key copied correctly (no spaces)
- [ ] API key is active (not deleted)
- [ ] Using IBM Cloud API key (not service-specific key)

**Solution:**
```powershell
# Test API key
curl -X POST "https://iam.cloud.ibm.com/identity/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=YOUR_KEY"
```

### Issue 2: "Project not found"

**Check:**
- [ ] Project ID copied correctly
- [ ] Project exists in watsonx.ai
- [ ] Watson Machine Learning service associated

**Solution:**
1. Go to https://dataplatform.cloud.ibm.com
2. Open your project
3. Manage → General → Copy Project ID

### Issue 3: "Region mismatch"

**Check:**
- [ ] `IBM_CLOUD_REGION` matches your services
- [ ] `WATSONX_URL` matches your region
- [ ] All services in same region

**Solution:** Use same region for all services

### Issue 4: "Model not available"

**Check:**
- [ ] Model ID is correct
- [ ] Model is available in your region
- [ ] Project has access to model

**Solution:**
1. Go to watsonx.ai project
2. Try model in Prompt Lab
3. Verify model works there first

---

## 💰 Cost Information

### Free Tier Limits

**IBM Cloud Lite Account:**
- ✅ Free forever
- ✅ No credit card required
- ✅ Access to 40+ services

**watsonx.ai Lite Plan:**
- ✅ Free tier available
- ✅ Limited tokens per month
- ✅ Access to Granite models

**Watson Speech to Text Lite:**
- ✅ 500 minutes/month free
- ✅ No credit card required

### Hackathon Credits

**If you have IBM Hackathon credits:**
1. Go to IBM Cloud dashboard
2. Billing → Feature codes
3. Enter your hackathon code
4. Credits applied automatically

---

## 🔐 Security Best Practices

### Protect Your Credentials

- ✅ Never commit `.env` to Git
- ✅ Use different keys for dev/prod
- ✅ Rotate keys regularly
- ✅ Use IBM Cloud IAM for access control

### .env File Security

```bash
# Check .env is in .gitignore
cat .gitignore | grep .env

# Should show:
# .env
# .env.local
# .env.*.local
```

### Key Rotation

**To rotate your IBM Cloud API key:**
1. Create new API key
2. Update `.env` with new key
3. Test application
4. Delete old API key

---

## 📚 Additional Resources

### IBM Documentation

- **IBM Cloud:** https://cloud.ibm.com/docs
- **watsonx.ai:** https://dataplatform.cloud.ibm.com/docs/content/wsj/getting-started/welcome-main.html
- **Granite Models:** https://www.ibm.com/products/watsonx-ai/foundation-models
- **Watson STT:** https://cloud.ibm.com/docs/speech-to-text

### IBM Hackathon Resources

- **IBM Developer:** https://developer.ibm.com
- **watsonx Tutorials:** https://www.ibm.com/products/watsonx-ai/tutorials
- **Community Forum:** https://community.ibm.com

### Support

- **IBM Cloud Support:** https://cloud.ibm.com/unifiedsupport/supportcenter
- **watsonx.ai Support:** Through IBM Cloud support
- **Hackathon Discord:** (Check your hackathon materials)

---

## ✅ Checklist

### Before Starting Development

- [ ] IBM Cloud account created
- [ ] IBM Cloud API key obtained
- [ ] watsonx.ai project created
- [ ] Project ID copied
- [ ] Watson STT service created (optional)
- [ ] All credentials in `.env` file
- [ ] `.env` file saved
- [ ] Credentials tested with `test_ibm_api.py`
- [ ] Backend starts without errors
- [ ] Can query Granite models

### Verification Steps

```powershell
# 1. Check config loads
python -c "from app.config import settings; print('Config OK')"

# 2. Test IBM connection
python test_ibm_api.py

# 3. Start backend
uvicorn app.main:app --reload --port 8000

# 4. Check health
curl http://localhost:8000/api/health

# 5. Test AI mode
curl -X POST http://localhost:8000/api/modes/illustration/query \
  -H "Content-Type: application/json" \
  -d '{"workspace_id":"test","query":"Hello"}'
```

---

## 🎉 You're Ready!

Once all credentials are set up:
- ✅ Backend will use IBM watsonx.ai
- ✅ All AI modes use Granite models
- ✅ Embeddings use IBM Slate models
- ✅ Speech-to-text uses Watson STT
- ✅ 100% IBM stack!

**Next:** See `IBM_SETUP_GUIDE.md` for running the application

---

**Last Updated:** 2024-01-15  
**For:** IBM Bob Hackathon  
**Stack:** IBM watsonx.ai + Granite + Watson