# ⚡ DevPilot AI - Quick Fix Checklist

## 🎯 Current Issue: Bob API 401 Unauthorized

### ✅ What We Found
- ✅ Python 3.12 installed
- ✅ Virtual environment exists
- ✅ All dependencies installed
- ✅ OpenAI SDK upgraded to latest version
- ✅ Configuration files correct
- ❌ **Bob API key is expired/invalid**

### 🔧 The Fix (2 Minutes)

#### Step 1: Get Fresh Bob API Key

**Open Cline Extension:**
1. Click Cline icon in VS Code sidebar
2. Click ⚙️ Settings (gear icon)
3. Click **"Sign Out"**
4. Click **"Sign In"** again
5. After signing in, copy your **NEW API key**

**Your key should look like:**
```
bob_prod_bob-user_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

#### Step 2: Update .env File

1. **Open:** `C:\Users\Janaa\Desktop\devpilot-ai\backend\.env`

2. **Find line 6:**
   ```env
   OPENAI_API_KEY=bob_prod_bob-user_44Er6d67wHFCVCY4C7YsV2V3akkwRYA9fD5nfugUfZRdFz7ZDuvFEKYGL9fswiyttRD4tgjzzPgm6R3X6GLBaHSi_HsHgYNbepQUhB3zPzMwLP8br7hoESeP64Eo5A2RVLZef
   ```

3. **Replace with YOUR new key:**
   ```env
   OPENAI_API_KEY=bob_prod_YOUR_NEW_KEY_HERE
   ```

4. **Save** (Ctrl+S)

#### Step 3: Test Again

```powershell
cd C:\Users\Janaa\Desktop\devpilot-ai\backend
.\venv\Scripts\activate
python test_api.py
```

**Expected:**
```
[SUCCESS] Bob API is working!
[Response] Hello from DevPilot AI!
```

---

## 🚀 Start the Application

### Terminal 1 - Backend
```powershell
cd C:\Users\Janaa\Desktop\devpilot-ai\backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

### Terminal 2 - Frontend
```powershell
cd C:\Users\Janaa\Desktop\devpilot-ai\frontend
npm run dev
```

### Access
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🐛 If Still Not Working

### Option 1: Check Cline Extension Version
```
1. Open VS Code Extensions (Ctrl+Shift+X)
2. Search "Cline"
3. Click "Update" if available
4. Restart VS Code
5. Get new API key
```

### Option 2: Try Alternative API Key Location
```
1. Go to https://app.cline.bot
2. Sign in
3. Settings → API Keys
4. Copy production key
5. Update .env file
```

### Option 3: Contact Support
```
If API key still doesn't work:
- Check Cline status: https://status.cline.bot
- Contact Cline support
- Check if account is active
```

---

## 📋 Verification Steps

After getting new API key:

- [ ] Updated `.env` file with new key
- [ ] Saved `.env` file
- [ ] Ran `python test_api.py`
- [ ] Saw `[SUCCESS]` message
- [ ] Started backend server
- [ ] Started frontend server
- [ ] Opened http://localhost:3000
- [ ] No errors in console

---

## 🎯 Summary

**Problem:** Bob API key expired (401 error)

**Solution:** 
1. Sign out and back into Cline
2. Get fresh API key
3. Update `.env` file
4. Test with `python test_api.py`

**Time Required:** 2-3 minutes

**Status:** Ready to fix! Just need fresh API key from Cline.

---

## 📞 Need Help?

See the complete guide: `COMPLETE_SETUP_AND_DEBUG_GUIDE.md`

**Quick Links:**
- [Common Errors](#) - Section in main guide
- [Troubleshooting](#) - Detailed debugging steps
- [Testing](#) - How to verify everything works