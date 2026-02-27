"""
Data Fetcher - Binance'ten OHLCV verisi çeker
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- ccxt kütüphanesi ile Binance Spot/Futures
- Tüm USDT paritelerini çeker, hacme göre filtreler
- Her timeframe için OHLCV_LIMIT mum döner
- Hız sınırı (rate limit) koruması vardır
"""
from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional

import ccxt
import pandas as pd

import config

logger = logging.getLogger(__name__)

COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]


class DataFetcher:
    def __init__(self):
        self.exchange = ccxt.binance({
            "enableRateLimit": True,
            "options": {"defaultType": "spot"},
        })
        logger.info("Binance bağlantısı kuruldu (spot)")

    # ── Sembol listesi ────────────────────────────────────────────

    def get_usdt_symbols(self) -> List[str]:
        """
        Binance'teki tüm USDT paritelerini getirir,
        24s hacme göre filtreler ve en yüksek hacimli TOP_N tanesini döner.
        """
        try:
            markets = self.exchange.load_markets()
            tickers = self.exchange.fetch_tickers()
        except Exception as exc:
            logger.error(f"Piyasa verisi çekilemedi: {exc}")
            return []

        candidates = []
        for symbol, market in markets.items():
            if not symbol.endswith("/USDT"):
                continue
            if not market.get("active", False):
                continue
            if market.get("type", "spot") != "spot":
                continue

            ticker = tickers.get(symbol, {})
            quote_vol = ticker.get("quoteVolume") or 0
            if quote_vol >= config.MIN_QUOTE_VOLUME_USDT:
                candidates.append((symbol, quote_vol))

        # Hacme göre azalan sıra
        candidates.sort(key=lambda x: x[1], reverse=True)
        symbols = [s for s, _ in candidates[: config.TOP_N_SYMBOLS]]
        logger.info(
            f"{len(symbols)} USDT çifti seçildi "
            f"(min hacim: ${config.MIN_QUOTE_VOLUME_USDT/1e6:.0f}M)"
        )
        return symbols

    # ── OHLCV çekme ───────────────────────────────────────────────

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int = None,
    ) -> Optional[pd.DataFrame]:
        """
        Tek sembol + timeframe için OHLCV DataFrame döner.
        None dönerse veri çekilememiştir.
        """
        limit = limit or config.OHLCV_LIMIT
        try:
            raw = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            if not raw:
                return None
            df = pd.DataFrame(raw, columns=COLUMNS)
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)
            for col in ["open", "high", "low", "close", "volume"]:
                df[col] = df[col].astype(float)
            return df
        except ccxt.BadSymbol:
            logger.debug(f"{symbol} {timeframe}: Geçersiz sembol, atlanıyor")
            return None
        except ccxt.RateLimitExceeded:
            logger.warning(f"{symbol} {timeframe}: Rate limit, 5sn bekleniyor")
            time.sleep(5)
            return None
        except Exception as exc:
            logger.warning(f"{symbol} {timeframe}: Veri çekme hatası: {exc}")
            return None

    def fetch_symbol_all_timeframes(
        self, symbol: str
    ) -> Dict[str, pd.DataFrame]:
        """
        Bir sembol için tüm timeframe'leri çeker.
        Returns: {timeframe: DataFrame}
        """
        result = {}
        for tf in config.TIMEFRAMES:
            df = self.fetch_ohlcv(symbol, tf)
            if df is not None and not df.empty:
                result[tf] = df
            time.sleep(config.RATE_LIMIT_DELAY)
        return result

    # ── Toplu çekme ───────────────────────────────────────────────

    def fetch_all(
        self,
        symbols: List[str],
    ) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Tüm semboller için tüm timeframe'leri paralel çeker.
        Returns: {symbol: {timeframe: DataFrame}}
        """
        all_data: Dict[str, Dict[str, pd.DataFrame]] = {}
        total = len(symbols)
        logger.info(f"{total} coin için veri çekiliyor...")

        with ThreadPoolExecutor(max_workers=config.MAX_CONCURRENT_SYMBOLS) as pool:
            future_map = {
                pool.submit(self.fetch_symbol_all_timeframes, sym): sym
                for sym in symbols
            }
            done = 0
            for future in as_completed(future_map):
                sym = future_map[future]
                done += 1
                try:
                    data = future.result()
                    if data:
                        all_data[sym] = data
                except Exception as exc:
                    logger.error(f"{sym}: {exc}")

                if done % 25 == 0:
                    logger.info(f"Veri çekme: {done}/{total}")

        logger.info(f"Veri çekme tamamlandı: {len(all_data)} coin")
        return all_data
