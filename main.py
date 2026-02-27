"""
Crypto Signal Bot - Ana Döngü
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Çalışma akışı:
1. Binance'ten tüm USDT paritelerini çek (hacme göre filtrele)
2. Her 5 dakikada bir tüm coinleri analiz et
3. Confluence sinyalleri konsola yaz + Telegram'a gönder (token varsa)
4. Aynı coin için cooldown süresi dolmadan tekrar sinyal verme

Kullanım:
    python main.py
    python main.py --once     # Tek seferlik çalış ve çık
    python main.py --symbol BTC/USDT  # Tek coin test et
"""
from __future__ import annotations

import argparse
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List

import config
from data_fetcher import DataFetcher
from signal_engine import SignalEngine, FinalSignal

# ── Logging ────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(config.LOG_FILE, encoding="utf-8"),
    ],
)
logger = logging.getLogger("main")

# ── Telegram (isteğe bağlı) ────────────────────────────────────
_telegram_available = False
if config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID:
    try:
        import requests
        _telegram_available = True
        logger.info("Telegram entegrasyonu aktif")
    except ImportError:
        logger.warning("requests kütüphanesi yok, Telegram devre dışı")


def send_telegram(text: str) -> None:
    """Telegram'a mesaj gönder (opsiyonel)"""
    if not _telegram_available:
        return
    import requests
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={
            "chat_id": config.TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
        }, timeout=10)
    except Exception as exc:
        logger.warning(f"Telegram gönderim hatası: {exc}")


def format_telegram_message(sig: FinalSignal) -> str:
    """Telegram için HTML formatlı mesaj"""
    direction_icon = "🟢 LONG/BUY" if sig.direction == "BUY" else "🔴 SHORT/SELL"
    mtf = " | MTF ✅" if sig.is_mtf else ""
    tf_str = "+".join(sorted(set(sig.timeframes)))
    pct_tp = (sig.target - sig.price) / sig.price * 100
    pct_sl = (sig.stop_loss - sig.price) / sig.price * 100
    reasons_str = "\n".join(f"  • {r}" for r in sig.reasons)

    return (
        f"<b>{direction_icon}</b>  |  <b>{sig.symbol}</b>  [{tf_str}{mtf}]\n"
        f"\n"
        f"📌 Giriş   : <code>{sig.price:.6g}</code>\n"
        f"🎯 Hedef   : <code>{sig.target:.6g}</code>  ({pct_tp:+.2f}%)\n"
        f"🛑 Stop    : <code>{sig.stop_loss:.6g}</code>  ({pct_sl:+.2f}%)\n"
        f"\n"
        f"📊 Confluence : {sig.confluence} strateji\n"
        f"💯 Skor       : {sig.final_score:.0%}\n"
        f"🔧 Stratejiler: {', '.join(sig.strategies)}\n"
        f"\n"
        f"📝 Sebepler:\n{reasons_str}\n"
        f"\n"
        f"⏰ {sig.timestamp.strftime('%H:%M:%S UTC')}"
    )


class Bot:
    def __init__(self):
        self.fetcher = DataFetcher()
        self.engine = SignalEngine()
        # Cooldown takibi: {symbol: datetime}
        self._last_signal: Dict[str, Dict[str, datetime]] = {}

    def _is_on_cooldown(self, symbol: str, direction: str) -> bool:
        key = f"{symbol}:{direction}"
        if key not in self._last_signal:
            return False
        elapsed = datetime.utcnow() - self._last_signal[key]
        return elapsed < timedelta(minutes=config.SIGNAL_COOLDOWN_MINUTES)

    def _mark_signal(self, symbol: str, direction: str) -> None:
        key = f"{symbol}:{direction}"
        self._last_signal[key] = datetime.utcnow()

    def run_once(self, symbols: List[str] = None) -> List[FinalSignal]:
        """Tek bir tarama döngüsü çalıştır"""
        if symbols is None:
            symbols = self.fetcher.get_usdt_symbols()

        if not symbols:
            logger.error("Analiz edilecek sembol bulunamadı!")
            return []

        logger.info(f"Tarama başladı: {len(symbols)} coin")

        # Veri çek
        all_data = self.fetcher.fetch_all(symbols)

        # Analiz et
        signals = self.engine.analyze_batch(all_data)

        # Skora göre sırala (en yüksek önce)
        signals.sort(key=lambda s: s.final_score, reverse=True)

        # Çıktı
        published = []
        for sig in signals:
            if self._is_on_cooldown(sig.symbol, sig.direction):
                logger.debug(f"[{sig.symbol}] cooldown aktif, atlanıyor")
                continue

            # Konsola yaz
            print(sig.summary())
            logger.info(
                f"SİNYAL: {sig.symbol} {sig.direction} "
                f"@ {sig.price:.6g} | skor={sig.final_score:.0%}"
            )

            # Telegram
            if _telegram_available:
                send_telegram(format_telegram_message(sig))

            self._mark_signal(sig.symbol, sig.direction)
            published.append(sig)

        if not published:
            logger.info("Bu döngüde sinyal üretilmedi.")
        else:
            logger.info(f"Bu döngüde {len(published)} sinyal yayınlandı.")

        return published

    def run_loop(self, symbols: List[str] = None) -> None:
        """Sürekli döngü: her CYCLE_INTERVAL_SECONDS saniyede bir tara"""
        logger.info(
            f"Bot başlatıldı | Döngü: {config.CYCLE_INTERVAL_SECONDS}sn | "
            f"Confluence: {config.MIN_CONFLUENCE}+"
        )
        print(f"\n{'='*60}")
        print(f"  CRYPTO SIGNAL BOT")
        print(f"  Tarama aralığı : {config.CYCLE_INTERVAL_SECONDS // 60} dakika")
        print(f"  Zaman dilimleri: {', '.join(config.TIMEFRAMES)}")
        print(f"  Min confluence : {config.MIN_CONFLUENCE} strateji")
        print(f"  Çıkmak için    : Ctrl+C")
        print(f"{'='*60}\n")

        cycle = 0
        while True:
            cycle += 1
            start = time.time()
            logger.info(f"── Döngü #{cycle} başladı ──")

            try:
                self.run_once(symbols)
            except KeyboardInterrupt:
                logger.info("Bot durduruldu (Ctrl+C)")
                break
            except Exception as exc:
                logger.error(f"Döngü hatası: {exc}", exc_info=True)

            elapsed = time.time() - start
            wait = max(0, config.CYCLE_INTERVAL_SECONDS - elapsed)
            logger.info(
                f"── Döngü #{cycle} bitti ({elapsed:.0f}sn) | "
                f"Sonraki: {wait:.0f}sn ──"
            )

            try:
                time.sleep(wait)
            except KeyboardInterrupt:
                logger.info("Bot durduruldu (Ctrl+C)")
                break


# ── Entry point ────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Crypto Signal Bot")
    parser.add_argument(
        "--once", action="store_true",
        help="Tek seferlik tara ve çık"
    )
    parser.add_argument(
        "--symbol", type=str, default=None,
        help="Tek bir sembol test et (ör: BTC/USDT)"
    )
    args = parser.parse_args()

    bot = Bot()

    symbols = None
    if args.symbol:
        symbols = [args.symbol]
        logger.info(f"Tek sembol modu: {args.symbol}")

    if args.once or args.symbol:
        signals = bot.run_once(symbols)
        if signals:
            print(f"\n{'='*60}")
            print(f"Toplam {len(signals)} sinyal üretildi.")
        else:
            print("Sinyal üretilmedi.")
    else:
        bot.run_loop(symbols)


if __name__ == "__main__":
    main()
