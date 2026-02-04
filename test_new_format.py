"""
Quick test to verify new Telegram format
"""
from signal_engine import ConfluentSignal
from telegram_bot import TelegramNotifier
from datetime import datetime

# Create test signal
test_signal = ConfluentSignal(
    symbol="BTC/USDT",
    timeframe="1h, 4h",
    strategies=["SupportResistanceStrategy (1h)", "VolumeSpikeStrategy (1h)", "EMACrossStrategy (4h)"],
    direction="BUY",
    price=73250.0,
    target=75450.0,
    stop_loss=72150.0,
    confluence_score=3,
    confidence=0.85,
    reasons=[
        "Support Breakout at $72,800 (Vol: 2.8x)",
        "Bullish Volume Spike (3.1x avg, +2.1%)",
        "Golden Cross EMA 50/200 (ADX: 28)"
    ]
)

telegram = TelegramNotifier()
message = telegram.format_signal_message(test_signal)

print("="*60)
print("YENİ TELEGRAM MESAJ FORMATI")
print("="*60)
print(message)
print("\n" + "="*60)
print("Bu mesaj Telegram'a bu şekilde gönderilecek!")
print("="*60)
