"""
Crypto Signal Bot - Konfigürasyon
Amaç: Tepe bölgede SHORT, dip bölgede BUY sinyali üretmek
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Exchange ──────────────────────────────────────────────
EXCHANGE_ID = "binance"
BASE_CURRENCY = "USDT"

# ── Telegram ──────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ── Tarama ayarları ───────────────────────────────────────
TIMEFRAMES = ["15m", "1h", "4h"]          # Analiz edilecek zaman dilimleri
OHLCV_LIMIT = 250                          # Her timeframe için çekilecek mum sayısı
CYCLE_INTERVAL_SECONDS = 300               # 5 dakikada bir tara
MAX_CONCURRENT_SYMBOLS = 20               # Aynı anda kaç coin paralel analiz edilsin
RATE_LIMIT_DELAY = 0.1                     # İstekler arası bekleme (sn)

# Coin filtresi: sadece yüksek hacimli coin tara
MIN_QUOTE_VOLUME_USDT = 5_000_000          # Son 24s hacim >= 5M USDT
TOP_N_SYMBOLS = 100                        # En yüksek hacimli kaç coin

# ── Sinyal eşikleri ───────────────────────────────────────
# Confluence: kaç strateji aynı anda aynı yönde sinyal vermeli
MIN_CONFLUENCE = 2                         # En az 2 strateji aynı fikirde olmalı
MTF_BONUS = True                           # Farklı timeframe'lerde eşleşme bonus puan verir

# Cooldown: aynı coin için tekrar sinyal verme süresi (dakika)
SIGNAL_COOLDOWN_MINUTES = 60

# ── RSI ayarları ──────────────────────────────────────────
RSI_PERIOD = 14
RSI_OVERSOLD = 30          # BUY bölgesi
RSI_OVERBOUGHT = 70        # SHORT bölgesi
RSI_EXTREME_OVERSOLD = 20  # Ekstra güçlü BUY
RSI_EXTREME_OVERBOUGHT = 80 # Ekstra güçlü SHORT

# ── Stochastic RSI ────────────────────────────────────────
STOCH_RSI_PERIOD = 14
STOCH_K_PERIOD = 3
STOCH_D_PERIOD = 3
STOCH_OVERSOLD = 20
STOCH_OVERBOUGHT = 80

# ── Bollinger Bands ───────────────────────────────────────
BB_PERIOD = 20
BB_STD = 2.0
BB_SQUEEZE_THRESHOLD = 0.03   # Bant genişliği < %3 → sıkışma

# ── RSI Divergence ────────────────────────────────────────
DIV_LOOKBACK = 30             # Kaç mumda divergence ara
DIV_MIN_SWING = 0.02          # Minimum %2 fiyat hareketi
DIV_SWING_WINDOW = 3          # Swing high/low tespit penceresi

# ── Volume ────────────────────────────────────────────────
VOL_MA_PERIOD = 20
VOL_SPIKE_MULTIPLIER = 1.5    # Ortalamanın 1.5 katı hacim = onay

# ── Risk / Ödül ───────────────────────────────────────────
DEFAULT_RR = 2.0              # Risk/Ödül oranı (1 risk → 2 kazanç)
DEFAULT_STOP_PCT = 1.5        # Stop loss %1.5
ATR_PERIOD = 14               # ATR tabanlı dinamik SL için

# ── Loglama ───────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = "signals.log"
