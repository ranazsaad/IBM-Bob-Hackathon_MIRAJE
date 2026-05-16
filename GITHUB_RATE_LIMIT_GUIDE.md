# GitHub API Rate Limit Guide

## Issue
The error you're seeing indicates that GitHub's API rate limit has been exceeded:
```
Request GET /repos/.../contents/package-lock.json?ref=main failed with 403: rate limit exceeded
```

## Understanding GitHub Rate Limits

### Unauthenticated Requests
- **Limit:** 60 requests per hour per IP address
- **Current usage:** Used when no GitHub token is provided

### Authenticated Requests
- **Limit:** 5,000 requests per hour per user
- **Recommended:** Always use authentication for production

## Solution: Add GitHub Personal Access Token

### Step 1: Create GitHub Personal Access Token

1. Go to GitHub Settings: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name: "DevPilot AI"
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `public_repo` (Access public repositories)
5. Click "Generate token"
6. **IMPORTANT:** Copy the token immediately (you won't see it again!)

### Step 2: Add Token to DevPilot

1. Open `devpilot-ai/backend/.env`
2. Find the line: `GITHUB_TOKEN=`
3. Add your token:
   ```env
   GITHUB_TOKEN=ghp_your_token_here_1234567890abcdef
   ```
4. Save the file

### Step 3: Restart Backend

```bash
cd devpilot-ai/backend
# Stop the backend (Ctrl+C)
# Start it again
python -m uvicorn app.main:app --reload
```

## How DevPilot Handles Rate Limits

### Automatic Detection
The GitHub analyzer now detects rate limit errors and stops gracefully:

```python
except Exception as e:
    if "rate limit" in str(e).lower():
        print(f"[GitHub] Rate limit hit, stopping at {file_count} files")
        break
```

### Graceful Degradation
- Analyzes as many files as possible before hitting the limit
- Saves partial results to database
- Returns what was successfully analyzed
- User can still use the workspace with available data

### File Limits
- **Shallow scan:** Up to 500 files
- **Deep scan:** Up to 2000 files
- Stops early if rate limit is hit

## Checking Your Rate Limit

### Using GitHub API
```bash
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/rate_limit
```

### Response Example
```json
{
  "resources": {
    "core": {
      "limit": 5000,
      "remaining": 4999,
      "reset": 1372700873
    }
  }
}
```

## Best Practices

### 1. Always Use Authentication
```env
# backend/.env
GITHUB_TOKEN=ghp_your_actual_token_here
```

### 2. Monitor Rate Limits
Check remaining requests before large operations:
```python
rate_limit = github.get_rate_limit()
print(f"Remaining: {rate_limit.core.remaining}/{rate_limit.core.limit}")
```

### 3. Use Shallow Scans for Demos
```bash
# Analyze with shallow scan (fewer API calls)
curl -X POST http://localhost:8000/api/analyze/github \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/user/repo", "depth": "shallow"}'
```

### 4. Cache Results
DevPilot automatically caches analyzed repositories in the database:
- First analysis: Uses GitHub API
- Subsequent queries: Uses cached data
- No additional API calls needed

## Troubleshooting

### Problem: "rate limit exceeded" error
**Solution:** Add GitHub token (see Step 1-3 above)

### Problem: Token not working
**Check:**
1. Token has correct scopes (`repo` or `public_repo`)
2. Token is not expired
3. Token is correctly copied (no extra spaces)
4. Backend was restarted after adding token

### Problem: Still hitting limits with token
**Possible causes:**
1. Analyzing very large repositories (1000+ files)
2. Multiple users sharing same token
3. Other applications using the same token

**Solutions:**
- Use shallow scan instead of deep scan
- Create separate tokens for different applications
- Wait for rate limit to reset (shown in error message)

## Rate Limit Reset Time

When you hit the limit, GitHub tells you when it resets:
```
Setting next backoff to 1537.901626s
```

This means:
- **1537 seconds** = ~25 minutes until reset
- Rate limits reset every hour
- Plan your analysis accordingly

## Alternative: Use Cached Data

If you've already analyzed a repository:
1. The data is in the database
2. No additional API calls needed
3. Query the workspace directly:
   ```bash
   curl http://localhost:8000/api/workspace/{workspace_id}
   ```

## For Production

### Use GitHub App
For production deployments, consider using a GitHub App:
- Higher rate limits (5,000 per installation)
- Better security (scoped permissions)
- Audit logging
- Multiple installations

### Documentation
https://docs.github.com/en/developers/apps/building-github-apps

## Summary

**Quick Fix:**
1. Get GitHub token: https://github.com/settings/tokens
2. Add to `backend/.env`: `GITHUB_TOKEN=your_token`
3. Restart backend

**Result:**
- 60 requests/hour → 5,000 requests/hour
- Can analyze large repositories
- No more rate limit errors

---

**Need Help?**
- GitHub Token Guide: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
- Rate Limit Docs: https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting

Made with ❤️ by DevPilot AI Team