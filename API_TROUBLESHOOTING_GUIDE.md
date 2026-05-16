# Comprehensive API Troubleshooting Guide: Resolving "Failed to Fetch" Errors

## Table of Contents
1. [Quick Diagnosis Checklist](#quick-diagnosis-checklist)
2. [Common Issues and Solutions](#common-issues-and-solutions)
3. [Debugging Tools and Techniques](#debugging-tools-and-techniques)
4. [Code Examples](#code-examples)
5. [Testing and Validation](#testing-and-validation)

---

## Quick Diagnosis Checklist

Before diving into detailed troubleshooting, run through this quick checklist:

- [ ] Is the backend server running?
- [ ] Are you using the correct API endpoint URL?
- [ ] Is CORS properly configured?
- [ ] Are network requests visible in browser DevTools?
- [ ] Is the authentication token valid?
- [ ] Are environment variables properly set?

---

## Common Issues and Solutions

### 1. CORS Configuration Problems

**Symptoms:**
- Error: "Access to fetch at '...' from origin '...' has been blocked by CORS policy"
- Network request shows status (CORS error) in DevTools

**Solution for Express.js:**

```javascript
// backend/app.js or server.js
const express = require('express');
const cors = require('cors');
const app = express();

// Option 1: Allow all origins (development only)
app.use(cors());

// Option 2: Specific origin configuration (recommended for production)
const corsOptions = {
  origin: ['http://localhost:3000', 'https://yourdomain.com'],
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true,
  maxAge: 86400 // 24 hours
};
app.use(cors(corsOptions));

// Option 3: Manual CORS headers
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', req.headers.origin || '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.header('Access-Control-Allow-Credentials', 'true');
  
  // Handle preflight requests
  if (req.method === 'OPTIONS') {
    return res.sendStatus(200);
  }
  next();
});
```

**Solution for FastAPI (Python):**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "https://yourdomain.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] for all origins (dev only)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600
)
```

**Verification:**
```bash
# Test CORS with curl
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     --verbose \
     http://localhost:8000/api/endpoint
```

---

### 2. Incorrect API Endpoint URLs

**Symptoms:**
- 404 Not Found errors
- Connection refused
- DNS resolution failures

**Diagnosis:**

```javascript
// Check your API configuration
console.log('API Base URL:', process.env.NEXT_PUBLIC_API_URL);
console.log('Full endpoint:', `${process.env.NEXT_PUBLIC_API_URL}/api/data`);

// Verify environment variables are loaded
if (!process.env.NEXT_PUBLIC_API_URL) {
  console.error('❌ API URL not configured!');
}
```

**Common Mistakes:**
```javascript
// ❌ Wrong - missing protocol
const API_URL = 'localhost:8000';

// ❌ Wrong - trailing slash inconsistency
const API_URL = 'http://localhost:8000/';
const endpoint = '/api/data'; // Results in: http://localhost:8000//api/data

// ✅ Correct
const API_URL = 'http://localhost:8000';
const endpoint = '/api/data';
const fullUrl = `${API_URL}${endpoint}`; // http://localhost:8000/api/data
```

**Solution:**

```javascript
// lib/api-config.js
export const API_CONFIG = {
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
};

// Helper function to build URLs
export function buildApiUrl(endpoint) {
  const base = API_CONFIG.baseURL.replace(/\/$/, ''); // Remove trailing slash
  const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${base}${path}`;
}

// Usage
const url = buildApiUrl('/api/data');
console.log('Fetching from:', url);
```

---

### 3. Network Connectivity Issues

**Diagnosis Steps:**

```bash
# 1. Check if backend is reachable
ping localhost

# 2. Check if port is open
nc -zv localhost 8000
# or
telnet localhost 8000

# 3. Check what's listening on the port
lsof -i :8000
# or on Windows
netstat -ano | findstr :8000

# 4. Test with curl
curl -v http://localhost:8000/api/health

# 5. Check DNS resolution (for remote servers)
nslookup api.yourdomain.com
dig api.yourdomain.com
```

**JavaScript Network Check:**

```javascript
async function checkNetworkConnectivity() {
  console.log('🔍 Checking network connectivity...');
  
  // Check if online
  if (!navigator.onLine) {
    console.error('❌ No internet connection');
    return false;
  }
  
  // Try to reach the API
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);
    
    const response = await fetch(`${API_URL}/health`, {
      method: 'GET',
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (response.ok) {
      console.log('✅ Backend is reachable');
      return true;
    } else {
      console.error(`❌ Backend returned status: ${response.status}`);
      return false;
    }
  } catch (error) {
    if (error.name === 'AbortError') {
      console.error('❌ Connection timeout');
    } else {
      console.error('❌ Network error:', error.message);
    }
    return false;
  }
}
```

---

### 4. Server Not Running or Crashed

**Diagnosis:**

```bash
# Check if process is running
ps aux | grep node  # For Node.js
ps aux | grep python  # For Python
ps aux | grep uvicorn  # For FastAPI

# Check server logs
tail -f backend/logs/server.log
# or
docker logs backend-container

# Check system resources
top
htop
free -h  # Memory
df -h    # Disk space
```

**Backend Health Check Endpoint:**

```javascript
// Express.js
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    version: process.env.npm_package_version
  });
});
```

```python
# FastAPI
from fastapi import FastAPI
from datetime import datetime
import psutil

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "memory_percent": psutil.virtual_memory().percent,
        "cpu_percent": psutil.cpu_percent(interval=1)
    }
```

**Auto-restart Configuration:**

```json
// package.json (Node.js with nodemon)
{
  "scripts": {
    "dev": "nodemon --watch src --exec node src/server.js",
    "start": "node src/server.js"
  }
}
```

```bash
# PM2 for production
pm2 start server.js --name api-server --watch
pm2 logs api-server
pm2 restart api-server
```

---

### 5. Firewall or Security Group Blocking Requests

**Diagnosis:**

```bash
# Check firewall status (Linux)
sudo ufw status
sudo iptables -L

# Check firewall (macOS)
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# Check firewall (Windows)
netsh advfirewall show allprofiles

# Test from different network
curl http://your-server-ip:8000/api/health
```

**Solutions:**

```bash
# Allow port through firewall (Linux)
sudo ufw allow 8000/tcp
sudo ufw reload

# Allow port (macOS)
# System Preferences > Security & Privacy > Firewall > Firewall Options

# AWS Security Group (example)
# Add inbound rule: Type: Custom TCP, Port: 8000, Source: 0.0.0.0/0
```

**Docker Network Issues:**

```yaml
# docker-compose.yml
services:
  backend:
    ports:
      - "8000:8000"  # host:container
    networks:
      - app-network
  
  frontend:
    ports:
      - "3000:3000"
    networks:
      - app-network
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000

networks:
  app-network:
    driver: bridge
```

---

### 6. Authentication Token Errors

**Symptoms:**
- 401 Unauthorized
- 403 Forbidden
- Token expired errors

**Proper Token Handling:**

```javascript
// lib/auth.js
export class AuthService {
  static TOKEN_KEY = 'auth_token';
  
  static setToken(token) {
    localStorage.setItem(this.TOKEN_KEY, token);
  }
  
  static getToken() {
    return localStorage.getItem(this.TOKEN_KEY);
  }
  
  static removeToken() {
    localStorage.removeItem(this.TOKEN_KEY);
  }
  
  static isTokenExpired(token) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp * 1000 < Date.now();
    } catch (error) {
      return true;
    }
  }
  
  static async refreshToken() {
    const token = this.getToken();
    if (!token) return null;
    
    try {
      const response = await fetch(`${API_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        this.setToken(data.token);
        return data.token;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      this.removeToken();
    }
    return null;
  }
}

// API client with token handling
export async function fetchWithAuth(endpoint, options = {}) {
  let token = AuthService.getToken();
  
  // Check if token is expired
  if (token && AuthService.isTokenExpired(token)) {
    console.log('Token expired, refreshing...');
    token = await AuthService.refreshToken();
    
    if (!token) {
      throw new Error('Authentication required');
    }
  }
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers
  });
  
  // Handle 401 - token invalid
  if (response.status === 401) {
    AuthService.removeToken();
    throw new Error('Authentication failed');
  }
  
  return response;
}
```

**Backend Token Verification:**

```javascript
// Express.js middleware
const jwt = require('jsonwebtoken');

function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN
  
  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }
  
  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) {
      console.error('Token verification failed:', err.message);
      return res.status(403).json({ error: 'Invalid or expired token' });
    }
    
    req.user = user;
    next();
  });
}

// Usage
app.get('/api/protected', authenticateToken, (req, res) => {
  res.json({ data: 'Protected data', user: req.user });
});
```

---

### 7. Request Timeout Settings

**Frontend Timeout Configuration:**

```javascript
// Fetch with timeout
async function fetchWithTimeout(url, options = {}, timeout = 30000) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    });
    clearTimeout(id);
    return response;
  } catch (error) {
    clearTimeout(id);
    if (error.name === 'AbortError') {
      throw new Error(`Request timeout after ${timeout}ms`);
    }
    throw error;
  }
}

// Axios with timeout
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor for logging
apiClient.interceptors.request.use(
  config => {
    console.log(`🚀 ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  error => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for timeout handling
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.code === 'ECONNABORTED') {
      console.error('Request timeout:', error.message);
      return Promise.reject(new Error('Request took too long'));
    }
    return Promise.reject(error);
  }
);
```

**Backend Timeout Configuration:**

```javascript
// Express.js
const express = require('express');
const app = express();

// Set timeout for all requests
app.use((req, res, next) => {
  req.setTimeout(30000); // 30 seconds
  res.setTimeout(30000);
  next();
});

// Or per route
app.get('/api/long-operation', (req, res) => {
  req.setTimeout(60000); // 60 seconds for this specific route
  
  // Your long operation
  performLongOperation()
    .then(result => res.json(result))
    .catch(error => res.status(500).json({ error: error.message }));
});

// Server timeout
const server = app.listen(8000, () => {
  console.log('Server running on port 8000');
});

server.timeout = 30000; // 30 seconds
server.keepAliveTimeout = 65000; // Should be higher than timeout
server.headersTimeout = 66000; // Should be higher than keepAliveTimeout
```

---

### 8. SSL Certificate Problems

**Symptoms:**
- "NET::ERR_CERT_AUTHORITY_INVALID"
- "SSL certificate problem: unable to get local issuer certificate"

**Development Workarounds (NOT for production):**

```javascript
// Node.js - disable SSL verification (development only)
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

// Fetch with custom agent
import https from 'https';
import fetch from 'node-fetch';

const agent = new https.Agent({
  rejectUnauthorized: false
});

fetch('https://localhost:8000/api/data', { agent });
```

**Production Solutions:**

```bash
# Install certificate
# Linux
sudo cp certificate.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates

# macOS
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain certificate.crt

# Verify certificate
openssl s_client -connect api.yourdomain.com:443 -showcerts
```

**Let's Encrypt Setup (Nginx):**

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d api.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

### 9. Incorrect HTTP Methods or Headers

**Common Issues:**

```javascript
// ❌ Wrong - GET request with body
fetch('/api/data', {
  method: 'GET',
  body: JSON.stringify({ id: 1 }) // GET shouldn't have body
});

// ❌ Wrong - Missing Content-Type
fetch('/api/data', {
  method: 'POST',
  body: JSON.stringify({ name: 'John' })
  // Missing: headers: { 'Content-Type': 'application/json' }
});

// ❌ Wrong - Incorrect method
fetch('/api/data', {
  method: 'POST' // Should be DELETE
});

// ✅ Correct
fetch('/api/data', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  body: JSON.stringify({ name: 'John' })
});
```

**Backend Method Validation:**

```javascript
// Express.js
app.post('/api/data', (req, res) => {
  // Validate Content-Type
  if (!req.is('application/json')) {
    return res.status(415).json({
      error: 'Unsupported Media Type',
      message: 'Content-Type must be application/json'
    });
  }
  
  // Validate required headers
  if (!req.headers['x-api-key']) {
    return res.status(400).json({
      error: 'Missing required header: x-api-key'
    });
  }
  
  // Process request
  res.json({ success: true });
});

// Method not allowed handler
app.all('/api/data', (req, res) => {
  res.status(405).json({
    error: 'Method Not Allowed',
    allowed: ['GET', 'POST', 'PUT', 'DELETE']
  });
});
```

---

### 10. Backend Server Returning Error Status Codes

**Proper Error Response Handling:**

```javascript
// Frontend - Comprehensive error handling
async function apiRequest(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    });
    
    // Parse response body
    const contentType = response.headers.get('content-type');
    let data;
    
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }
    
    // Handle different status codes
    if (!response.ok) {
      const error = new Error(data.message || `HTTP ${response.status}`);
      error.status = response.status;
      error.data = data;
      
      switch (response.status) {
        case 400:
          console.error('Bad Request:', data);
          break;
        case 401:
          console.error('Unauthorized - redirecting to login');
          // Redirect to login
          break;
        case 403:
          console.error('Forbidden:', data);
          break;
        case 404:
          console.error('Not Found:', endpoint);
          break;
        case 429:
          console.error('Rate Limited:', data);
          break;
        case 500:
          console.error('Server Error:', data);
          break;
        case 503:
          console.error('Service Unavailable:', data);
          break;
        default:
          console.error(`Error ${response.status}:`, data);
      }
      
      throw error;
    }
    
    return data;
  } catch (error) {
    if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
      console.error('Network error - server may be down or unreachable');
      throw new Error('Unable to connect to server. Please check your connection.');
    }
    throw error;
  }
}
```

**Backend - Proper Error Responses:**

```javascript
// Express.js error handling
class ApiError extends Error {
  constructor(status, message, details = null) {
    super(message);
    this.status = status;
    this.details = details;
  }
}

// Error handler middleware
app.use((err, req, res, next) => {
  console.error('Error:', {
    message: err.message,
    stack: err.stack,
    url: req.url,
    method: req.method,
    body: req.body
  });
  
  const status = err.status || 500;
  const message = err.message || 'Internal Server Error';
  
  res.status(status).json({
    error: {
      status,
      message,
      details: err.details,
      timestamp: new Date().toISOString(),
      path: req.url
    }
  });
});

// Usage in routes
app.post('/api/data', async (req, res, next) => {
  try {
    if (!req.body.name) {
      throw new ApiError(400, 'Name is required', {
        field: 'name',
        type: 'required'
      });
    }
    
    const result = await processData(req.body);
    res.json({ success: true, data: result });
  } catch (error) {
    next(error);
  }
});
```

---

### 11. Proxy or Middleware Configuration Issues

**Next.js Proxy Configuration:**

```javascript
// next.config.js
module.exports = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*'
      }
    ];
  }
};

// Or use environment-based proxy
module.exports = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.BACKEND_URL}/api/:path*`
      }
    ];
  }
};
```

**Express.js Proxy Middleware:**

```javascript
const { createProxyMiddleware } = require('http-proxy-middleware');

app.use('/api', createProxyMiddleware({
  target: 'http://localhost:8000',
  changeOrigin: true,
  pathRewrite: {
    '^/api': '/api' // Keep /api prefix
  },
  onProxyReq: (proxyReq, req, res) => {
    console.log('Proxying:', req.method, req.path);
  },
  onProxyRes: (proxyRes, req, res) => {
    console.log('Proxy response:', proxyRes.statusCode);
  },
  onError: (err, req, res) => {
    console.error('Proxy error:', err);
    res.status(500).json({ error: 'Proxy error' });
  }
}));
```

---

### 12. Database Connection Failures

**Backend Database Connection Check:**

```javascript
// Express.js with MongoDB
const mongoose = require('mongoose');

async function connectDatabase() {
  try {
    await mongoose.connect(process.env.MONGODB_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
      serverSelectionTimeoutMS: 5000
    });
    
    console.log('✅ Database connected');
    
    // Monitor connection
    mongoose.connection.on('error', err => {
      console.error('❌ Database error:', err);
    });
    
    mongoose.connection.on('disconnected', () => {
      console.warn('⚠️ Database disconnected');
    });
    
    return true;
  } catch (error) {
    console.error('❌ Database connection failed:', error);
    return false;
  }
}

// Start server only after DB connection
connectDatabase().then(connected => {
  if (connected) {
    app.listen(8000, () => {
      console.log('Server running on port 8000');
    });
  } else {
    console.error('Failed to start server - database not connected');
    process.exit(1);
  }
});
```

```python
# FastAPI with PostgreSQL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import time

def connect_database(max_retries=5):
    retries = 0
    while retries < max_retries:
        try:
            engine = create_engine(
                os.getenv('DATABASE_URL'),
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20
            )
            
            # Test connection
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            
            print("✅ Database connected")
            return engine
        except OperationalError as e:
            retries += 1
            print(f"❌ Database connection failed (attempt {retries}/{max_retries}): {e}")
            if retries < max_retries:
                time.sleep(2 ** retries)  # Exponential backoff
            else:
                raise

# Dependency for routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Health check with DB status
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
```

---

### 13. Environment Variable Misconfiguration

**Diagnosis:**

```javascript
// Check environment variables
console.log('Environment Check:');
console.log('NODE_ENV:', process.env.NODE_ENV);
console.log('API_URL:', process.env.NEXT_PUBLIC_API_URL);
console.log('DB_URL:', process.env.DATABASE_URL ? '✅ Set' : '❌ Not set');

// Validate required variables
const requiredEnvVars = [
  'NEXT_PUBLIC_API_URL',
  'DATABASE_URL',
  'JWT_SECRET'
];

const missingVars = requiredEnvVars.filter(
  varName => !process.env[varName]
);

if (missingVars.length > 0) {
  console.error('❌ Missing environment variables:', missingVars);
  process.exit(1);
}
```

**Proper .env Setup:**

```bash
# .env.local (Frontend - Next.js)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENV=development

# .env (Backend)
NODE_ENV=development
PORT=8000
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
JWT_SECRET=your-secret-key-here
CORS_ORIGIN=http://localhost:3000
```

**Loading Environment Variables:**

```javascript
// config.js
require('dotenv').config();

const config = {
  env: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT || '8000', 10),
  database: {
    url: process.env.DATABASE_URL,
    poolSize: parseInt(process.env.DB_POOL_SIZE || '10', 10)
  },
  jwt: {
    secret: process.env.JWT_SECRET,
    expiresIn: process.env.JWT_EXPIRES_IN || '24h'
  },
  cors: {
    origin: process.env.CORS_ORIGIN?.split(',') || ['http://localhost:3000']
  }
};

// Validate configuration
function validateConfig() {
  const required = ['database.url', 'jwt.secret'];
  const missing = required.filter(key => {
    const value = key.split('.').reduce((obj, k) => obj?.[k], config);
    return !value;
  });
  
  if (missing.length > 0) {
    throw new Error(`Missing required config: ${missing.join(', ')}`);
  }
}

validateConfig();

module.exports = config;
```

---

### 14. Port Conflicts or Incorrect Port Numbers

**Diagnosis:**

```bash
# Check what's using a port
lsof -i :8000
netstat -ano | findstr :8000  # Windows

# Kill process on port
kill -9 $(lsof -t -i:8000)  # macOS/Linux
# Windows: Find PID from netstat, then:
taskkill /PID <PID> /F

# Find available port
for port in {8000..8100}; do
  ! nc -z localhost $port && echo "Port $port is available" && break
done
```

**Dynamic Port Assignment:**

```javascript
// server.js
const express = require('express');
const app = express();

const PORT = process.env.PORT || 8000;

function startServer(port) {
  const server = app.listen(port, () => {
    console.log(`✅ Server running on port ${port}`);
  }).on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
      console.log(`❌ Port ${port} is busy, trying ${port + 1}...`);
      startServer(port + 1);
    } else {
      console.error('Server error:', err);
    }
  });
}

startServer(PORT);
```

**Docker Port Mapping:**

```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend
    ports:
      - "${BACKEND_PORT:-8000}:8000"
    environment:
      - PORT=8000
  
  frontend:
    build: ./frontend
    ports:
      - "${FRONTEND_PORT:-3000}:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:${BACKEND_PORT:-8000}
```

---

### 15. Backend Route Handlers Not Properly Defined

**Common Issues:**

```javascript
// ❌ Wrong - Route not defined
app.get('/api/users', (req, res) => {
  // Handler code
});

// Request to /api/user (typo) will fail with 404

// ❌ Wrong - Missing async/await
app.get('/api/data', (req, res) => {
  fetchDataFromDB()  // Returns promise but not awaited
    .then(data => res.json(data));
  // If error occurs, it won't be caught
});

// ❌ Wrong - Not sending response
app.post('/api/data', (req, res) => {
  processData(req.body);
  // Forgot to send response - request will timeout
});

// ✅ Correct
app.get('/api/data', async (req, res, next) => {
  try {
    const data = await fetchDataFromDB();
    res.json({ success: true, data });
  } catch (error) {
    next(error);  // Pass to error handler
  }
});
```

**Route Debugging:**

```javascript
// List all registered routes
function listRoutes(app) {
  console.log('\n📋 Registered Routes:');
  app._router.stack.forEach(middleware => {
    if (middleware.route) {
      const methods = Object.keys(middleware.route.methods)
        .map(m => m.toUpperCase())
        .join(', ');
      console.log(`${methods} ${middleware.route.path}`);
    } else if (middleware.name === 'router') {
      middleware.handle.stack.forEach(handler => {
        if (handler.route) {
          const methods = Object.keys(handler.route.methods)
            .map(m => m.toUpperCase())
            .join(', ');
          console.log(`${methods} ${handler.route.path}`);
        }
      });
    }
  });
  console.log('');
}

// Call after defining all routes
listRoutes(app);

// Request logging middleware
app.use((req, res, next) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    console.log(
      `${req.method} ${req.path} - ${res.statusCode} (${duration}ms)`
    );
  });
  
  next();
});
```

---

##  Debugging Tools and Techniques

### Browser Developer Tools

**Network Tab Analysis:**

1. Open DevTools (F12)
2. Go to Network tab
3. Reload page or trigger API call
4. Look for failed requests (red status)
5. Click on failed request to see details:
   - **Headers**: Check request/response headers
   - **Response**: See error message
   - **Timing**: Identify bottlenecks

**Console Debugging:**

```javascript
// Enable verbose logging
localStorage.setItem('debug', 'api:*');

// Custom logger
const logger = {
  request: (method, url, data) => {
    console.group(`🚀 ${method} ${url}`);
    console.log('Request data:', data);
    console.time('request-duration');
  },
  
  response: (status, data) => {
    console.timeEnd('request-duration');
    console.log(`Response ${status}:`, data);
    console.groupEnd();
  },
  
  error: (error) => {
    console.timeEnd('request-duration');
    console.error('❌ Request failed:', error);
    console.groupEnd();
  }
};

// Usage in fetch wrapper
async function debugFetch(url, options = {}) {
  logger.request(options.method || 'GET', url, options.body);
  
  try {
    const response = await fetch(url, options);
    const data = await response.json();
    logger.response(response.status, data);
    return { response, data };
  } catch (error) {
    logger.error(error);
    throw error;
  }
}
```

### Command Line Testing

**cURL Examples:**

```bash
# Basic GET request
curl -v http://localhost:8000/api/health

# POST with JSON data
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"name":"John","email":"john@example.com"}' \
  http://localhost:8000/api/users

# With authentication
curl -X GET \
  -H "Authorization: Bearer your-token-here" \
  http://localhost:8000/api/protected

# Test CORS
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     http://localhost:8000/api/data

# Save response to file
curl -o response.json http://localhost:8000/api/data

# Follow redirects
curl -L http://localhost:8000/api/redirect

# Test with timeout
curl --max-time 30 http://localhost:8000/api/slow
```

**HTTPie (Alternative to cURL):**

```bash
# Install
pip install httpie

# Basic usage
http GET localhost:8000/api/health
http POST localhost:8000/api/users name=John email=john@example.com
http GET localhost:8000/api/protected Authorization:"Bearer token"

# Upload file
http --form POST localhost:8000/api/upload file@document.pdf

# Custom headers
http GET localhost:8000/api/data X-API-Key:secret User-Agent:MyApp/1.0
```

### Postman/Insomnia Testing

**Postman Collection Example:**

```json
{
  "info": {
    "name": "API Tests",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "baseUrl",
      "value": "http://localhost:8000"
    }
  ],
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{baseUrl}}/health",
          "host": ["{{baseUrl}}"],
          "path": ["health"]
        }
      },
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test('Status code is 200', function () {",
              "    pm.response.to.have.status(200);",
              "});",
              "",
              "pm.test('Response has status field', function () {",
              "    const jsonData = pm.response.json();",
              "    pm.expect(jsonData).to.have.property('status');",
              "});"
            ]
          }
        }
      ]
    }
  ]
}
```

---

## Code Examples

### Complete Fetch Wrapper with Error Handling

```javascript
// lib/api-client.js
class ApiClient {
  constructor(baseURL, options = {}) {
    this.baseURL = baseURL.replace(/\/$/, '');
    this.defaultOptions = {
      timeout: 30000,
      retries: 3,
      retryDelay: 1000,
      ...options
    };
  }
  
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      ...this.defaultOptions,
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...this.defaultOptions.headers,
        ...options.headers
      }
    };
    
    let lastError;
    
    for (let attempt = 1; attempt <= config.retries; attempt++) {
      try {
        console.log(`🚀 Attempt ${attempt}: ${config.method || 'GET'} ${url}`);
        
        const response = await this.fetchWithTimeout(url, config, config.timeout);
        
        // Log response
        console.log(`✅ Response ${response.status}: ${url}`);
        
        if (!response.ok) {
          const errorData = await this.parseResponse(response);
          throw new ApiError(response.status, errorData.message || response.statusText, errorData);
        }
        
        return await this.parseResponse(response);
        
      } catch (error) {
        lastError = error;
        
        console.error(`❌ Attempt ${attempt} failed:`, error.message);
        
        // Don't retry on client errors (4xx) except 408, 429
        if (error.status >= 400 && error.status < 500 && 
            error.status !== 408 && error.status !== 429) {
          break;
        }
        
        // Don't retry on last attempt
        if (attempt === config.retries) {
          break;
        }
        
        // Wait before retry
        await this.delay(config.retryDelay * attempt);
      }
    }
    
    throw lastError;
  }
  
  async fetchWithTimeout(url, options, timeout) {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    
    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal
      });
      clearTimeout(id);
      return response;
    } catch (error) {
      clearTimeout(id);
      if (error.name === 'AbortError') {
        throw new Error(`Request timeout after ${timeout}ms`);
      }
      throw error;
    }
  }
  
  async parseResponse(response) {
    const contentType = response.headers.get('content-type');
    
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    } else {
      return await response.text();
    }
  }
  
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  
  // Convenience methods
  get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'GET' });
  }
  
  post(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data)
    });
  }
  
  put(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }
  
  delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'DELETE' });
  }
}

class ApiError extends Error {
  constructor(status, message, data = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

// Usage
const api = new ApiClient(process.env.NEXT_PUBLIC_API_URL);

// With authentication
class AuthenticatedApiClient extends ApiClient {
  constructor(baseURL, options = {}) {
    super(baseURL, options);
    this.token = null;
  }
  
  setToken(token) {
    this.token = token;
  }
  
  async request(endpoint, options = {}) {
    if (this.token) {
      options.headers = {
        ...options.headers,
        'Authorization': `Bearer ${this.token}`
      };
    }
    
    try {
      return await super.request(endpoint, options);
    } catch (error) {
      // Handle token expiration
      if (error.status === 401) {
        this.token = null;
        // Trigger re-authentication
        window.dispatchEvent(new CustomEvent('auth:required'));
      }
      throw error;
    }
  }
}

export { ApiClient, AuthenticatedApiClient, ApiError };
```

### Backend Server with Comprehensive Error Handling

```javascript
// server.js
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const { body, validationResult } = require('express-validator');

const app = express();

// Security middleware
app.use(helmet());

// CORS configuration
app.use(cors({
  origin: process.env.CORS_ORIGIN?.split(',') || ['http://localhost:3000'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: {
    error: 'Too many requests',
    retryAfter: '15 minutes'
  }
});
app.use('/api/', limiter);

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Request logging
app.use((req, res, next) => {
  const start = Date.now();
  
  console.log(`📥 ${req.method} ${req.path}`, {
    ip: req.ip,
    userAgent: req.get('User-Agent'),
    body: req.method !== 'GET' ? req.body : undefined
  });
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    console.log(`📤 ${req.method} ${req.path} - ${res.statusCode} (${duration}ms)`);
  });
  
  next();
});

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    version: process.env.npm_package_version || '1.0.0'
  });
});

// API routes with validation
app.post('/api/users',
  // Validation middleware
  [
    body('name').notEmpty().withMessage('Name is required'),
    body('email').isEmail().withMessage('Valid email is required'),
    body('age').optional().isInt({ min: 0 }).withMessage('Age must be a positive integer')
  ],
  async (req, res, next) => {
    try {
      // Check validation results
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          error: 'Validation failed',
          details: errors.array()
        });
      }
      
      // Simulate processing
      const user = await createUser(req.body);
      
      res.status(201).json({
        success: true,
        data: user
      });
    } catch (error) {
      next(error);
    }
  }
);

// Async function simulation
async function createUser(userData) {
  // Simulate database operation
  await new Promise(resolve => setTimeout(resolve, 100));
  
  // Simulate random error
  if (Math.random() < 0.1) {
    throw new Error('Database connection failed');
  }
  
  return {
    id: Date.now(),
    ...userData,
    createdAt: new Date().toISOString()
  };
}

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: `Route ${req.method} ${req.originalUrl} not found`,
    availableRoutes: [
      'GET /health',
      'POST /api/users'
    ]
  });
});

// Global error handler
app.use((err, req, res, next) => {
  console.error('💥 Error:', {
    message: err.message,
    stack: err.stack,
    url: req.url,
    method: req.method,
    body: req.body,
    headers: req.headers
  });
  
  // Default error response
  let status = err.status || 500;
  let message = err.message || 'Internal Server Error';
  
  // Handle specific error types
  if (err.name === 'ValidationError') {
    status = 400;
    message = 'Validation failed';
  } else if (err.name === 'UnauthorizedError') {
    status = 401;
    message = 'Unauthorized';
  } else if (err.code === 'ECONNREFUSED') {
    status = 503;
    message = 'Service unavailable';
  }
  
  res.status(status).json({
    error: {
      status,
      message,
      timestamp: new Date().toISOString(),
      path: req.url,
      ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
    }
  });
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  server.close(() => {
    console.log('Process terminated');
  });
});

const PORT = process.env.PORT || 8000;
const server = app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`📋 Health check: http://localhost:${PORT}/health`);
});

// Handle server errors
server.on('error', (error) => {
  if (error.code === 'EADDRINUSE') {
    console.error(`❌ Port ${PORT} is already in use`);
    process.exit(1);
  } else {
    console.error('❌ Server error:', error);
  }
});

module.exports = app;
```

---

## Testing and Validation

### Automated API Testing

```javascript
// tests/api.test.js
const request = require('supertest');
const app = require('../server');

describe('API Endpoints', () => {
  test('Health check should return 200', async () => {
    const response = await request(app)
      .get('/health')
      .expect(200);
    
    expect(response.body).toHaveProperty('status', 'healthy');
    expect(response.body).toHaveProperty('timestamp');
  });
  
  test('POST /api/users should create user', async () => {
    const userData = {
      name: 'John Doe',
      email: 'john@example.com',
      age: 30
    };
    
    const response = await request(app)
      .post('/api/users')
      .send(userData)
      .expect(201);
    
    expect(response.body.success).toBe(true);
    expect(response.body.data).toHaveProperty('id');
    expect(response.body.data.name).toBe(userData.name);
  });
  
  test('POST /api/users should validate required fields', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({})
      .expect(400);
    
    expect(response.body.error).toBe('Validation failed');
    expect(response.body.details).toHaveLength(2); // name and email required
  });
  
  test('Unknown route should return 404', async () => {
    const response = await request(app)
      .get('/api/unknown')
      .expect(404);
    
    expect(response.body.error).toBe('Not Found');
  });
});

// Integration test with real network
describe('Network Integration', () => {
  const API_URL = process.env.TEST_API_URL || 'http://localhost:8000';
  
  test('Server should be reachable', async () => {
    const response = await fetch(`${API_URL}/health`);
    expect(response.ok).toBe(true);
    
    const data = await response.json();
    expect(data.status).toBe('healthy');
  });
  
  test('CORS should be configured', async () => {
    const response = await fetch(`${API_URL}/health`, {
      method: 'OPTIONS',
      headers: {
        'Origin': 'http://localhost:3000',
        'Access-Control-Request-Method': 'GET'
      }
    });
    
    expect(response.ok).toBe(true);
    expect(response.headers.get('Access-Control-Allow-Origin')).toBeTruthy();
  });
});
```

### Frontend Testing

```javascript
// tests/api-client.test.js
import { ApiClient, ApiError } from '../lib/api-client';

// Mock fetch
global.fetch = jest.fn();

describe('ApiClient', () => {
  let client;
  
  beforeEach(() => {
    client = new ApiClient('http://localhost:8000');
    fetch.mockClear();
  });
  
  test('should make successful GET request', async () => {
    const mockData = { id: 1, name: 'Test' };
    fetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      headers: new Map([['content-type', 'application/json']]),
      json: async () => mockData
    });
    
    const result = await client.get('/api/test');
    
    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/test',
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({
          'Content-Type': 'application/json'
        })
      })
    );
    expect(result).toEqual(mockData);
  });
  
  test('should handle network errors', async () => {
    fetch.mockRejectedValueOnce(new Error('Failed to fetch'));
    
    await expect(client.get('/api/test')).rejects.toThrow('Failed to fetch');
  });
  
  test('should handle HTTP errors', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      statusText: 'Not Found',
      headers: new Map([['content-type', 'application/json']]),
      json: async () => ({ error: 'Not found' })
    });
    
    await expect(client.get('/api/test')).rejects.toThrow(ApiError);
  });
  
  test('should retry on server errors', async () => {
    // First two calls fail, third succeeds
    fetch
      .mockRejectedValueOnce(new Error('Network error'))
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Map([['content-type', 'application/json']]),
        json: async () => ({ success: true })
      });
    
    const result = await client.get('/api/test');
    
    expect(fetch).toHaveBeenCalledTimes(3);
    expect(result).toEqual({ success: true });
  });
});
```

### Monitoring and Alerting

```javascript
// monitoring/health-check.js
const fetch = require('node-fetch');

class HealthMonitor {
  constructor(endpoints, options = {}) {
    this.endpoints = endpoints;
    this.interval = options.interval || 60000; // 1 minute
    this.timeout = options.timeout || 10000; // 10 seconds
    this.retries = options.retries || 3;
    this.alerts = options.alerts || [];
  }
  
  async checkEndpoint(endpoint) {
    const start = Date.now();
    
    for (let attempt = 1; attempt <= this.retries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);
        
        const response = await fetch(endpoint.url, {
          signal: controller.signal,
          headers: endpoint.headers || {}
        });
        
        clearTimeout(timeoutId);
        
        const duration = Date.now() - start;
        const isHealthy = response.ok;
        
        return {
          endpoint: endpoint.name,
          url: endpoint.url,
          status: response.status,
          healthy: isHealthy,
          duration,
          attempt,
          timestamp: new Date().toISOString()
        };
        
      } catch (error) {
        if (attempt === this.retries) {
          return {
            endpoint: endpoint.name,
            url: endpoint.url,
            healthy: false,
            error: error.message,
            duration: Date.now() - start,
            attempt,
            timestamp: new Date().toISOString()
          };
        }
        
        // Wait before retry
        await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
      }
    }
  }
  
  async checkAll() {
    const results = await Promise.all(
      this.endpoints.map(endpoint => this.checkEndpoint(endpoint))
    );
    
    // Log results
    results.forEach(result => {
      const status = result.healthy ? '✅' : '❌';
      console.log(
        `${status} ${result.endpoint}: ${result.status || 'ERROR'} (${result.duration}ms)`
      );
    });
    
    // Send alerts for unhealthy endpoints
    const unhealthy = results.filter(r => !r.healthy);
    if (unhealthy.length > 0) {
      await this.sendAlerts(unhealthy);
    }
    
    return results;
  }
  
  async sendAlerts(unhealthyEndpoints) {
    const message = `🚨 Health Check Alert\n\nUnhealthy endpoints:\n${
      unhealthyEndpoints.map(e => 
        `- ${e.endpoint}: ${e.error || `HTTP ${e.status}`}`
      ).join('\n')
    }`;
    
    // Send to configured alert channels
    for (const alert of this.alerts) {
      try {
        await alert.send(message);
      } catch (error) {
        console.error('Failed to send alert:', error);
      }
    }
  }
  
  start() {
    console.log('🔍 Starting health monitor...');
    this.checkAll(); // Initial check
    
    this.intervalId = setInterval(() => {
      this.checkAll();
    }, this.interval);
  }
  
  stop() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      console.log('⏹️ Health monitor stopped');
    }
  }
}

// Usage
const monitor = new HealthMonitor([
  {
    name: 'API Server',
    url: 'http://localhost:8000/health'
  },
  {
    name: 'Database',
    url: 'http://localhost:8000/health/db'
  }
], {
  interval: 30000, // Check every 30 seconds
  timeout: 5000,   // 5 second timeout
  alerts: [
    {
      send: async (message) => {
        // Send to Slack, email, etc.
        console.log('ALERT:', message);
      }
    }
  ]
});

monitor.start();

// Graceful shutdown
process.on('SIGINT', () => {
  monitor.stop();
  process.exit(0);
});

module.exports = HealthMonitor;
```

---

## Summary

This comprehensive troubleshooting guide covers the most common "Failed to fetch" errors and their solutions. Remember to:

1. **Start with the basics**: Check if the server is running and reachable
2. **Use systematic debugging**: Follow the network request from frontend to backend
3. **Implement proper error handling**: Both on frontend and backend
4. **Monitor and log**: Set up proper logging and monitoring
5. **Test thoroughly**: Use automated tests to catch issues early
6. **Document your API**: Keep clear documentation of endpoints and expected responses

When encountering API connection issues, work through this guide systematically, starting with the quick diagnosis checklist and then diving into specific areas based on the symptoms you observe.