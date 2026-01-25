# Deployment Guide - Agentic Business Ops

## 🚀 Quick Deployment (15 minutes)

This guide deploys your app to:
- **Backend API**: Render (free tier)
- **Frontend UI**: Streamlit Community Cloud (free)

---

## Step 1: Push Code to GitHub

1. **Initialize Git** (if not already done):
```bash
cd "C:\Users\hanae\OneDrive - Nile University\Desktop\Uni Courses\MLops project\Agentic-business-ops"
git init
git add .
git commit -m "Initial commit - ready for deployment"
```

2. **Create GitHub Repository**:
   - Go to https://github.com/new
   - Name: `agentic-business-ops`
   - Make it **Public** (required for free tiers)
   - Don't initialize with README
   - Click "Create repository"

3. **Push to GitHub**:
```bash
git remote add origin https://github.com/YOUR_USERNAME/agentic-business-ops.git
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy Backend to Render

1. **Go to Render**: https://render.com
2. **Sign up/Login** (use GitHub to sign in)
3. **Click "New +"** → **"Web Service"**
4. **Connect your GitHub repo**: `agentic-business-ops`
5. **Configure**:
   - **Name**: `agentic-business-ops-backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn api:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

6. **Add Environment Variables**:
   - Click "Environment" tab
   - Add:
     - `PERPLEXITY_API_KEY` = `your_key_here`
     - `LANGSMITH_API_KEY` = `your_key_here` (optional)

7. **Click "Create Web Service"**
8. **Wait 5 minutes** for deployment
9. **Copy your backend URL**: `https://agentic-business-ops-backend.onrender.com`

---

## Step 3: Deploy Frontend to Streamlit Cloud

1. **Go to Streamlit Cloud**: https://share.streamlit.io
2. **Sign up/Login** (use GitHub)
3. **Click "New app"**
4. **Configure**:
   - **Repository**: `YOUR_USERNAME/agentic-business-ops`
   - **Branch**: `main`
   - **Main file path**: `streamlit_professional_ui.py`

5. **Advanced Settings** → **Add Secrets**:
```toml
API_BASE_URL = "https://agentic-business-ops-backend.onrender.com"
```

6. **Click "Deploy"**
7. **Wait 2 minutes**
8. **Done!** Your app is live at: `https://YOUR_APP.streamlit.app`

---

## Step 4: Test Your Deployment

1. Visit your Streamlit app URL
2. Login (any email/password works)
3. Upload a test document
4. Ask a question
5. Generate a plan

---

## 🔧 Troubleshooting

### Backend won't start
- Check Render logs for errors
- Verify environment variables are set
- Make sure Python version is 3.11+ in Render settings

### Frontend can't connect to backend
- Verify `API_BASE_URL` in Streamlit secrets matches your Render URL
- Check Render backend is "Live" (not sleeping)
- Test backend directly: `https://YOUR_BACKEND.onrender.com/health`

### Database errors
- Render free tier has ephemeral filesystem (resets on sleep)
- For persistence, upgrade to paid tier or use external database

---

## 💰 Costs

- **Render Free Tier**: $0/month (backend sleeps after 15 min inactivity)
- **Streamlit Cloud**: $0/month (unlimited public apps)
- **Total**: **FREE** ✅

---

## 🎉 You're Done!

Share your app URL with anyone. They can:
- Upload business documents
- Chat with AI consultant
- Generate action plans
- Track analytics

**Note**: Free tier apps "wake up" in ~30 seconds after inactivity. First request may be slow.
