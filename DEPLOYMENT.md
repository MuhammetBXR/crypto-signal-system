# Crypto Signal System - V2 Deployment Guide

## 🚀 Railway Deployment (24/7 Free Hosting)

### Prerequisites
1. GitHub account (optional)
2. Railway account (railway.app)
3. Your `.env` file ready

### Step 1: Railway Account
1. Go to https://railway.app
2. Sign up with GitHub
3. Verify email

### Step 2: Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo" OR "Deploy from local"
3. If local: Install Railway CLI:
   ```powershell
   npm install -g @railway/cli
   ```

### Step 3: Link Project
```powershell
cd "c:\Users\muham\Desktop\BİTCOİN TEST"
railway login
railway init
```

### Step 4: Add Environment Variables
Go to Railway dashboard → Your project → Variables

Add these from your `.env`:
```
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
DATABASE_PATH=crypto_signals.db
```

### Step 5: Deploy
```powershell
railway up
```

Or push to GitHub and Railway will auto-deploy.

### Step 6: Monitor
- Dashboard URL: Will be provided by Railway
- Worker logs: Check Railway dashboard
- Telegram: Should start receiving signals!

---

## 📊 Dashboard Access

After deployment, Railway will give you a URL like:
```
https://your-app.up.railway.app
```

Open this to access your dashboard!

---

## 🤖 Telegram Bot Commands

After deployment, use these commands in Telegram:

- `/start` - Welcome message
- `/stats` - Performance statistics  
- `/signals` - Last 10 signals
- `/performance` - Detailed report
- `/help` - Help message

---

## 🔧 Troubleshooting

### Bot not responding?
Check environment variables in Railway dashboard.

### No signals coming?
Check worker logs in Railway dashboard.

### Dashboard not loading?
Make sure web service is running.

---

## 💾 Backup Database

Railway provides persistent storage. Database is saved automatically.

To download:
```powershell
railway run python -c "import shutil; shutil.copy('crypto_signals.db', 'backup.db')"
```

---

## 📈 Monitoring

Check Railway dashboard for:
- CPU usage
- Memory usage
- Network traffic
- Logs

**IMPORTANT:** Railway free tier = 500 hours/month. This is enough for 24/7 if you optimize.

---

## ✅ Deployment Checklist

- [ ] Railway account created
- [ ] Environment variables added
- [ ] Database initialized
- [ ] Bot token verified
- [ ] First signal received
- [ ] Dashboard accessible
- [ ] Bot commands work

---

🎉 **You're live!** System is now running 24/7 on the cloud!
