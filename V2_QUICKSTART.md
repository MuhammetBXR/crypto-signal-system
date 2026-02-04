# 🎉 V2 Features - Quick Reference

## 📱 Bot Commands (In Telegram)

After running the system, use these commands in your Telegram chat:

```
/start      - Welcome message
/stats      - Performance statistics
/signals    - Last 10 signals
/performance - Detailed report
/help       - Help message
```

To enable bot commands, run:
```powershell
python -m telegram.ext.Application --token YOUR_TOKEN --polling
```

Or integrate into main.py by adding bot polling.

---

## 🌐 Dashboard

Start the dashboard:
```powershell
python dashboard/app.py
```

Then visit: **http://localhost:5000**

**Pages:**
- `/` - Home (system status)
- `/signals` - Signal history
- `/performance` - Analytics

---

## 🧪 Backtest

Run backtest on 30 days of data:
```powershell
python backtest.py
```

---

## ☁️ Railway Deployment

### Quick Deploy:
```powershell
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Environment Variables:
Add in Railway dashboard:
- `TELEGRAM_BOT_TOKEN=your_token`
- `TELEGRAM_CHAT_ID=your_chat_id`
- `DATABASE_PATH=crypto_signals.db`

See [DEPLOYMENT.md](DEPLOYMENT.md) for full guide.

---

## 📊 Features Summary

| Feature | File | Status |
|---------|------|--------|
| Chart Links | `chart_generator.py` | ✅ Complete |
| Bot Commands | `bot_commands.py` | ✅ Complete |
| Dashboard | `dashboard/` | ✅ Complete |
| Backtest | `backtest.py` | ✅ Complete |
| Deploy Config | `Procfile`, `railway.json` | ✅ Complete |

---

**All V2 features ready to use!** 🚀
