# Vercel Deployment Guide - LMS Web App

## 🚨 Root Cause of 404 Errors

Your LMS application is a **React Single Page Application (SPA)** using **React Router** for client-side routing. The 404 errors occur because:

1. **Client-Side Routes**: Routes like `/mentor`, `/admin/courses`, `/student/tasks` are handled by React Router in the browser
2. **Server-Side Issue**: When you directly access these URLs or refresh the page, Vercel's server tries to find actual files at these paths
3. **Missing Files**: Since these are client-side routes, no physical files exist at those paths, causing 404 errors

## ✅ Solution Applied

Created `vercel.json` configuration files that:
- **Rewrite all routes** to `/index.html` (SPA fallback)
- **Preserve static assets** (CSS, JS, images) with correct paths
- **Cache static files** for better performance
- **Add security headers**

---

## 📋 Deployment Steps

### Step 1: Prepare Environment Variables

Create a `.env` file in the frontend directory or set these in Vercel dashboard:

```bash
# Frontend Environment Variables (Vercel Dashboard)
REACT_APP_BACKEND_URL=https://your-backend-url.com
```

**For Supabase (if using):**
```bash
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-anon-key
```

### Step 2: Deploy Frontend to Vercel

#### Option A: Using Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to project root
cd /app

# Deploy
vercel

# Follow prompts:
# - Link to existing project or create new
# - Set root directory: ./
# - Build command: cd frontend && yarn install && yarn build
# - Output directory: frontend/build
```

#### Option B: Using Vercel Dashboard

1. **Import Project**:
   - Go to https://vercel.com/new
   - Import your GitHub/GitLab repository
   - Select the repository

2. **Configure Build Settings**:
   - **Framework Preset**: Other (or Create React App)
   - **Root Directory**: `./` (keep at root)
   - **Build Command**: 
     ```bash
     cd frontend && yarn install && yarn build
     ```
   - **Output Directory**: `frontend/build`
   - **Install Command**: `yarn install` (in frontend directory)

3. **Environment Variables**:
   - Add `REACT_APP_BACKEND_URL`
   - Add Supabase variables if needed
   - Click "Add" for each variable

4. **Deploy**: Click "Deploy"

### Step 3: Deploy Backend (Separate)

⚠️ **Important**: Vercel is designed for frontend and serverless functions. Your FastAPI backend needs to be deployed separately.

**Backend Deployment Options**:

1. **Render.com** (Recommended for FastAPI):
   ```bash
   # Render will use: uvicorn backend.server:app --host 0.0.0.0 --port 8001
   ```

2. **Railway.app**:
   - Automatically detects FastAPI
   - Simple deployment

3. **Heroku**:
   - Create `Procfile`: `web: uvicorn backend.server:app --host 0.0.0.0 --port $PORT`

4. **AWS/GCP/Azure**:
   - Deploy as containerized application

### Step 4: Update Frontend Environment Variable

After backend deployment, update Vercel environment variable:

```bash
REACT_APP_BACKEND_URL=https://your-actual-backend-url.onrender.com
```

Then **redeploy** the frontend on Vercel.

---

## 🔍 Vercel Configuration Explained

### Root `/app/vercel.json` (Main Config)

```json
{
  "buildCommand": "cd frontend && yarn install && yarn build",
  "outputDirectory": "frontend/build",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

**Key Settings**:
- **buildCommand**: Navigates to frontend, installs dependencies, builds
- **outputDirectory**: Where React build outputs files
- **rewrites**: Routes ALL requests to index.html (SPA fallback)

### Frontend `/app/frontend/vercel.json` (Backup Config)

Simple rewrite rule as a fallback if deploying from frontend directory.

---

## 🧪 Testing After Deployment

### 1. Test Direct URL Access

Open these URLs directly in browser (not by navigating from homepage):

✅ **Should Work**:
- `https://your-app.vercel.app/`
- `https://your-app.vercel.app/auth`
- `https://your-app.vercel.app/login`
- `https://your-app.vercel.app/mentor`
- `https://your-app.vercel.app/mentor/courses`
- `https://your-app.vercel.app/admin/students`
- `https://your-app.vercel.app/student/tasks`

### 2. Test Page Refresh

1. Navigate to any route (e.g., `/mentor/attendance`)
2. Press F5 or Cmd+R to refresh
3. Page should reload correctly (not 404)

### 3. Test Authentication Flow

1. Go to `/auth`
2. Register a new mentor account
3. Login
4. Should redirect to `/mentor` dashboard
5. All mentor pages should be accessible

### 4. Check Browser Console

Press F12 → Console tab:
- ❌ Should see NO 404 errors for routes
- ✅ May see 404 for API calls if backend not connected (expected)
- ✅ Static assets (JS, CSS) should load correctly

### 5. Check Vercel Build Logs

1. Go to Vercel Dashboard → Your Project → Deployments
2. Click on latest deployment
3. Check "Build Logs" tab
4. Look for:
   - ✅ "Build completed successfully"
   - ❌ Any errors about missing files or build failures

---

## 🐛 Troubleshooting Common Issues

### Issue 1: Still Getting 404 on Some Routes

**Cause**: `vercel.json` not properly configured or in wrong location

**Fix**:
1. Ensure `vercel.json` is in project root (`/app/vercel.json`)
2. Check "Rewrite" rules are present
3. Redeploy: `vercel --force`

### Issue 2: Blank Page After Deployment

**Cause**: Incorrect output directory or missing environment variables

**Fix**:
1. Check Vercel logs for build errors
2. Verify output directory is `frontend/build`
3. Check browser console for JavaScript errors
4. Verify `REACT_APP_BACKEND_URL` is set

### Issue 3: Static Assets (CSS/JS) Not Loading

**Cause**: Incorrect public path or base URL

**Fix**:
1. Check `package.json` for `"homepage"` field (should not be set or set to `/`)
2. Verify static files are in `frontend/build/static/`
3. Check Network tab in browser dev tools

### Issue 4: API Calls Failing (CORS Errors)

**Cause**: Backend CORS not configured for Vercel domain

**Fix** (in FastAPI backend):
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 5: Environment Variables Not Working

**Cause**: Variables not prefixed with `REACT_APP_`

**Fix**:
- All React environment variables MUST start with `REACT_APP_`
- Example: `REACT_APP_API_URL` (✅) vs `API_URL` (❌)
- Set in Vercel Dashboard → Project Settings → Environment Variables
- Redeploy after adding variables

---

## 📊 Vercel Dashboard Checklist

After deployment, verify in Vercel Dashboard:

### Deployments Tab
- ✅ Status: "Ready" (not "Error")
- ✅ Build Duration: < 5 minutes
- ✅ No build errors in logs

### Settings → General
- ✅ Framework: "Other" or "Create React App"
- ✅ Node Version: 18.x or 20.x
- ✅ Build Command: `cd frontend && yarn install && yarn build`
- ✅ Output Directory: `frontend/build`

### Settings → Environment Variables
- ✅ `REACT_APP_BACKEND_URL` is set
- ✅ All variables start with `REACT_APP_`
- ✅ Production, Preview, and Development environments configured

### Settings → Domains
- ✅ Custom domain added (if applicable)
- ✅ SSL certificate is active

---

## 🚀 Performance Optimization

### 1. Enable Vercel Analytics

```bash
npm install @vercel/analytics
```

In `frontend/src/index.js`:
```javascript
import { Analytics } from '@vercel/analytics/react';

// Add to root component
<Analytics />
```

### 2. Add Preload Links

In `frontend/public/index.html`:
```html
<link rel="preconnect" href="https://your-backend-url.com">
<link rel="dns-prefetch" href="https://your-backend-url.com">
```

### 3. Enable Gzip/Brotli Compression

Already enabled by default in Vercel for static assets.

---

## 📝 Post-Deployment Validation Report Template

```markdown
## LMS Vercel Deployment Validation Report

**Deployment URL**: https://your-app.vercel.app
**Deployment Date**: [Date]
**Tested By**: [Name]

### 1. Deployment Health
- [ ] Site is live and accessible
- [ ] No build errors in Vercel logs
- [ ] All environment variables set correctly

### 2. Functionality Tests
- [ ] Login page loads (`/auth`)
- [ ] Register flow works
- [ ] Admin dashboard accessible (`/admin`)
- [ ] Mentor dashboard accessible (`/mentor`)
- [ ] Student dashboard accessible (`/student`)
- [ ] All sub-routes work (tasks, attendance, etc.)

### 3. Routing Tests
- [ ] Direct URL access works for all routes
- [ ] Page refresh does not cause 404
- [ ] Browser back/forward buttons work
- [ ] Deep links work correctly

### 4. API Connectivity
- [ ] Frontend connects to backend
- [ ] Authentication tokens pass correctly
- [ ] No CORS errors in console
- [ ] Data loads successfully

### 5. UI/UX Validation
- [ ] Login/signup inputs are visible and functional
- [ ] All styles load correctly
- [ ] Dark mode works (if applicable)
- [ ] Responsive on mobile devices

### 6. Performance
- [ ] Initial load < 3 seconds
- [ ] No console errors
- [ ] Lighthouse score > 80

### Issues Found:
1. [List any issues]

### Fixes Applied:
1. [List fixes]

### Status: ✅ PASS / ❌ FAIL
```

---

## 📞 Need Help?

If you encounter issues:

1. **Check Vercel Build Logs**: Most issues are visible here
2. **Browser Console**: Check for JavaScript errors
3. **Network Tab**: Check API call responses
4. **Vercel Support**: https://vercel.com/support

---

## 🎯 Summary

✅ **Root Cause Fixed**: Added SPA fallback configuration via `vercel.json`

✅ **Configuration Applied**: 
- Rewrite rules for all routes
- Static asset handling
- Security headers
- Cache optimization

✅ **Next Steps**:
1. Deploy frontend to Vercel
2. Deploy backend separately (Render/Railway)
3. Update environment variables
4. Test all routes
5. Validate functionality

Your 404 errors should now be resolved! 🚀