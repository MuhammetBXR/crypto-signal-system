# 🚀 Crypto Signal System V2

Advanced cryptocurrency trading signal system with AI-powered strategies, Telegram notifications, web dashboard, and cloud deployment.

## ✨ Features

### 📊 Core System
- **446 USDT pairs** monitored 24/7
- **5 trading strategies** with confluence scoring
- **Multi-timeframe analysis** (15m, 1h, 4h, 1d)
- **Real-time signals** with entry, TP, and SL
- **Performance tracking** with win/loss metrics

### 📱 V2 Enhancements
1. **Chart Screenshots** - TradingView chart links in every signal
2. **Telegram Bot Commands** - Interactive control via `/stats`, `/signals`, `/performance`, `/help`
3. **Web Dashboard** - Beautiful monitoring interface at `localhost:5000`
4. **Backtest System** - Historical strategy validation
5. **Railway Deployment** - Free 24/7 cloud hosting

---

## 🎯 Strategies

1. **Channel Breakout** - Detects falling/rising channel breaks
2. **RSI Divergence** - Identifies bullish/bearish divergences
3. **Volume Spike** - Monitors abnormal volume with price action
4. **EMA Cross** - Golden/Death cross detection
5. **Support/Resistance** - Breakout and breakdown signals

**Confluence System**: Signals require 2+ strategies agreeing (customizable)

---

## 🚀 Quick Start

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Configuration
Create `.env` file:
```
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### 3. Run Core System
```powershell
python main.py
```

### 4. Run Dashboard (Optional)
```powershell
python dashboard/app.py
```
Visit: http://localhost:5000

---

## 📱 Telegram Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/stats` | Performance statistics |
| `/signals` | Last 10 signals |
| `/performance` | Detailed report |
| `/help` | Commands list |

---

## 🌐 Web Dashboard

Access at `http://localhost:5000` when running:

- **Home** - Live system status
- **Signals** - Signal history table  
- **Performance** - Analytics and charts

---

## 🧪 Backtest

Test strategies on historical data:

```powershell
python backtest.py
```

---

## ☁️ Cloud Deployment

### Railway (Free 500hrs/month)

1. Install Railway CLI:
   ```powershell
   npm install -g @railway/cli
   ```

2. Deploy:
   ```powershell
   railway login
   railway init
   railway up
   ```

3. Add environment variables in Railway dashboard

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guide.

---

## 📊 How It Works

```
┌─────────────┐
│ Data Fetch  │  ← Binance API (446 USDT pairs)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Strategies │  ← 5 strategies × 4 timeframes
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Confluence  │  ← 2+ strategies agree?
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Filter     │  ← Cooldown, quality check
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Notify     │  ← Telegram + Dashboard
└─────────────┘
```

---

## 📁 Project Structure

```
BİTCOİN TEST/
├── main.py                 # Main orchestrator
├── config.py               # Configuration
├── data_fetcher.py         # Binance data
├── signal_engine.py        # Strategy engine
├── telegram_bot.py         # Telegram notifications
├── bot_commands.py         # Interactive commands
├── chart_generator.py      # Chart screenshots
├── database.py             # SQLite database
├── backtest.py             # Backtesting engine
│
├── dashboard/              # Web dashboard
│   ├── app.py              # Flask app
│   ├── templates/          # HTML pages
│   └── static/             # CSS files
│
├── strategies/             # Trading strategies
│   ├── channel_breakout.py
│   ├── rsi_divergence.py
│   ├── volume_spike.py
│   ├── ema_cross.py
│   └── support_resistance.py
│
├── Procfile                # Railway deployment
├── railway.json            # Railway config
└── DEPLOYMENT.md           # Deploy guide
```

---

## 🎨 Signal Example

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟢 YÜKSELIŞ SİNYALİ (GÜÇLÜ)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💎 COİN: BTC/USDT
💰 ŞU ANKİ FİYAT: $73,250.00

🟢 GİRİŞ: $73,250
🎯 HEDEF: $75,450 (+3.0%)
🛡️ STOP: $72,150 (-1.5%)

⚡ Confluence: 3/5 ⭐⭐⭐
⭐ Güven: 85%
⏰ Timeframes: 1h, 4h

📊 Chart: https://tradingview.com/...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## ⚙️ Configuration

Edit `config.py`:

```python
MIN_CONFLUENCE_SCORE = 2        # Min strategies required
SIGNAL_COOLDOWN_HOURS = 1       # Cooldown between signals
TIMEFRAMES = ['15m', '1h', '4h', '1d']
```

---

##  📈 Performance Metrics

- **Win Rate**: Percentage of winning trades
- **Risk/Reward**: Average profit vs loss ratio
- **Confluence Score**: Number of agreeing strategies
- **Confidence**: Strategy conviction level

---

## 🛠️ Troubleshooting

### No signals appearing?
- Check Telegram token in `.env`
- Verify bot has permission to send messages
- Check cooldown settings

### Dashboard not loading?
- Ensure Flask is installed: `pip install flask`
- Check port 5000 is available
- Run: `python dashboard/app.py`

### Bot commands not working?
- Bot must be running in main.py
- Commands only work after system starts
- Check Telegram bot token

---

## 📚 Documentation

- [BAŞLANGIÇ.md](BAŞLANGIÇ.md) - Turkish setup guide
- [kullanim_rehberi.md](kullanim_rehberi.md) - Usage guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Cloud deployment

---

## 🤝 Contributing

This is a personal trading system. Feel free to fork and customize for your needs.

---

## ⚠️ Disclaimer

This system is for educational purposes only. Trading cryptocurrencies involves risk. Always do your own research and never invest more than you can afford to lose.

---

## 📊 Stats

- **Strategies**: 5
- **Symbols Monitored**: 446 USDT pairs
- **Timeframes**: 4 (15m, 1h, 4h, 1d)
- **Scan Frequency**: Every 5 minutes
- **Average Signals/Day**: ~50-100 (varies by market)

---

## 🎉 V2 Release

All features complete:
✅ Chart screenshots
✅ Bot commands
✅ Web dashboard  
✅ Backtest system
✅ Railway deployment

---

**Built with ❤️ for profitable trading**

🚀 Trade smart, trade safe!
