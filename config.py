"""
Central configuration for Crypto Signal System
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent
CHARTS_DIR = PROJECT_ROOT / "charts"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
CHARTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Telegram settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Database settings
DATABASE_PATH = os.getenv("DATABASE_PATH", "./crypto_signals.db")

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Binance settings (public API - no auth needed for OHLCV)
EXCHANGE_ID = "binance"
BASE_CURRENCY = "USDT"

# Timeframes to analyze
TIMEFRAMES = ["15m", "1h", "4h", "1d"]

# Data fetching settings
OHLCV_LIMIT = 100  # Number of candles to fetch per request
RATE_LIMIT_DELAY = 0.05  # Delay between requests in seconds
MAX_CONCURRENT_REQUESTS = 20  # Max parallel requests

# Signal settings
MIN_CONFLUENCE_SCORE = int(os.getenv("MIN_CONFLUENCE_SCORE", "2"))
SIGNAL_COOLDOWN_HOURS = 1  # Min hours between signals for same coin
MAX_SIGNALS_PER_CYCLE = 50  # Max signals to send per cycle

# Cycle settings
CYCLE_INTERVAL_MINUTES = int(os.getenv("CYCLE_INTERVAL_MINUTES", "5"))

# Strategy parameters
STRATEGY_PARAMS = {
    "channel_breakout": {
        "lookback_period": 50,
        "volume_multiplier": 1.5,  # Breakout volume must be 1.5x average
        "min_channel_width": 0.02,  # Min 2% channel width
    },
    "rsi_divergence": {
        "rsi_period": 14,
        "rsi_overbought": 70,
        "rsi_oversold": 30,
        "divergence_lookback": 20,
        "min_price_swing": 0.03,  # Min 3% price swing for divergence
    },
    "volume_spike": {
        "volume_period": 20,
        "spike_multiplier": 2.0,  # Volume must be 2x average
        "min_candle_body": 0.01,  # Min 1% candle body (avoid doji)
    },
    "ema_cross": {
        "fast_period": 50,
        "slow_period": 200,
        "adx_period": 14,
        "min_adx": 25,  # Trend strength filter
    },
    "support_resistance": {
        "swing_lookback": 20,
        "proximity_threshold": 0.005,  # Price within 0.5% of level
        "min_touches": 2,  # Min touches to confirm level
        "breakout_volume_multiplier": 1.3,
    },
}

# Risk management
DEFAULT_RISK_REWARD_RATIO = 2.0  # Target is 2x stop loss distance
DEFAULT_STOP_LOSS_PERCENT = 1.5  # 1.5% stop loss

# Performance tracking
BACKTEST_DAYS = 90  # Days of historical data for backtesting
PERFORMANCE_REVIEW_HOURS = 24  # Hours to wait before marking signal as win/loss
