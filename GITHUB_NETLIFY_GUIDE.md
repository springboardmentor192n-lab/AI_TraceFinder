# 🚀 AI TraceFinder - GitHub & Netlify Deployment Guide

## Prerequisites
- GitHub account
- Netlify account (free tier available)
- Git installed on your machine

---

## Step 1: Connect Your Local Repository to GitHub

Since you have the repository URL but don't have push access, follow these steps:

### Option A: Fork the Repository (Recommended)
1. Go to: https://github.com/springboardmentor192n-lab/AI_TraceFinder
2. Click **Fork** button (top-right)
3. This creates your own copy where you have full access

### Option B: Push to Your Own Repository
1. Create a new repository on GitHub (or use an existing one)
2. In your local project directory, run:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` and `YOUR_REPO` with your actual GitHub username and repository name.

---

## Step 2: Push Your Code to GitHub

```bash
# From: d:\Infosys-INTERNSHIP\AI_TraceFinder_Complete

# Add GitHub as remote (if not already done)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Push all commits
git push -u origin main
```

---

## Step 3: Deploy to Netlify

### Frontend-Only Deployment (Recommended for Quick Setup)
1. Go to [netlify.com](https://app.netlify.com/)
2. Click **Add new site** → **Import an existing project**
3. Select **GitHub** and authorize Netlify
4. Choose your repository
5. Configure build settings:
   - **Build command**: `npm install && npm run build` (or leave empty if no build needed)
   - **Publish directory**: `frontend` or `frontend/templates`
6. Click **Deploy site**

### Full Stack Deployment (Backend + Frontend)

**Option 1: Netlify Frontend + Heroku Backend**
- Deploy frontend to Netlify (steps above)
- Deploy backend to Heroku:
  ```bash
  # Install Heroku CLI first
  heroku login
  heroku create your-app-name
  git push heroku main
  ```
- Update your frontend API calls to use Heroku backend URL

**Option 2: GitHub + Railway (Easier than Heroku)**
1. Go to [railway.app](https://railway.app/)
2. Click **New Project** → **Deploy from GitHub**
3. Select your repository
4. Set environment variables (if needed)
5. Deploy

---

## Files Included in This Repository

```
AI_TraceFinder/
├── frontend/
│   ├── templates/
│   │   └── index.html          # Main UI
│   └── static/
│       ├── script.js            # Frontend logic
│       ├── styles.css           # Dark theme styling
│       └── new_styles.css       # Additional styles
├── backend/
│   ├── app.py                   # Flask API server
│   ├── image_forensics.py       # Forensics engine
│   ├── config.py                # Configuration
│   ├── scanner_model.pkl        # ML model
│   ├── classes_mapping.pkl      # ML classes
│   └── requirements.txt          # Python dependencies
├── README.md                     # Documentation
├── requirements.txt              # Full project dependencies
├── netlify.toml                 # Netlify configuration
├── run_windows.bat              # Windows startup script
├── run_unix.sh                  # Unix startup script
└── setup_windows.bat            # Windows setup script
```

---

## Important Files to Keep

✅ **Keep These:**
- `frontend/` - All frontend files
- `backend/app.py` - Main API
- `backend/image_forensics.py` - Forensics engine
- `backend/*model*.pkl` - ML models  
- `requirements.txt` - Dependencies
- `README.md` - Documentation
- `netlify.toml` - Netlify config

❌ **Ignored in .gitignore:**
- `venv/` - Virtual environment
- `__pycache__/` - Python cache
- `backend/uploads/` - Temporary uploads
- `.env` - Secrets
- `*.log` - Log files
- `analysis_history.json` - Runtime generated

---

## Quick Start After Deployment

### 1. Access Your Deployed Site
```
https://your-netlify-site.netlify.app
```

### 2. Use the Web Interface
- Upload images for analysis
- View results with confidence scores
- Check analysis history
- Generate reports

### 3. API Endpoints (After Backend Deployment)
```
GET    /api/health              - Health check
POST   /api/analyze             - Single image analysis
POST   /api/batch-analyze       - Multiple images
GET    /api/history             - View analysis history
POST   /api/report              - Generate HTML report
POST   /api/compare             - Compare analyses
GET    /api/docs                - API documentation
```

---

## Troubleshooting

### Issue: Push rejected
**Solution**: Ensure you have write access to the repository
```bash
git remote -v  # Check remote URL
```

### Issue: Netlify build fails
**Solution**: Check build logs in Netlify dashboard
- Make sure `frontend/templates/index.html` exists
- Verify all static files are in `frontend/static/`

### Issue: Backend API not accessible
**Solution**: Set environment variables in Netlify:
- Go to **Site settings** → **Build & deploy** → **Environment**
- Add `BACKEND_URL` pointing to your backend server

### Issue: CORS errors
**Solution**: Backend already has CORS enabled in `app.py`
- If deploying to different domain, update CORS settings

---

## Environment Variables (For Netlify)

If deploying with a backend server, add to Netlify:

```
BACKEND_URL=https://your-backend-url.com
API_TIMEOUT=30
```

---

## Next Steps

1. ✅ **Push to GitHub** using commands above
2. ✅ **Deploy Frontend to Netlify**
3. ✅ **Deploy Backend** (Heroku, Railway, or your server)
4. ✅ **Update API URLs** in `frontend/static/script.js`
5. ✅ **Test live deployment**

---

## Support & Resources

- **Netlify Docs**: https://docs.netlify.com/
- **Flask Deployment**: https://flask.palletsprojects.com/en/latest/deploying/
- **GitHub Pages**: https://pages.github.com/
- **Railway Docs**: https://docs.railway.app/

---

**Last Updated**: March 19, 2026  
**Version**: 1.0.0
