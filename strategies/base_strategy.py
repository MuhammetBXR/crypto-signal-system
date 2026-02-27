"""
Base strategy - Tüm stratejiler bu sınıftan türetilir
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import pandas as pd
import numpy as np


@dataclass
class Signal:
    """
    Tek bir strateji tarafından üretilen sinyal.
    direction: 'BUY' (dip bölgede al) veya 'SHORT' (tepe bölgede sat)
    score    : 1-10 arası güven skoru
    """
    symbol: str
    timeframe: str
    strategy: str
    direction: str          # 'BUY' veya 'SHORT'
    price: float
    target: float
    stop_loss: float
    score: float            # 0.0 – 1.0
    reason: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "strategy": self.strategy,
            "direction": self.direction,
            "price": self.price,
            "target": self.target,
            "stop_loss": self.stop_loss,
            "score": self.score,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
        }


class BaseStrategy(ABC):
    """Soyut taban sınıf"""

    def __init__(self):
        self.name = self.__class__.__name__

    @abstractmethod
    def analyze(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Optional[Signal]:
        """
        OHLCV DataFrame'i analiz eder, sinyal varsa döner.
        df sütunları: open, high, low, close, volume (hepsi float)
        """
        pass

    # ── Yardımcı metotlar ─────────────────────────────────

    def calc_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Average True Range hesapla"""
        high = df["high"]
        low = df["low"]
        close = df["close"]
        prev_close = close.shift(1)
        tr = pd.concat([
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs()
        ], axis=1).max(axis=1)
        return tr.ewm(span=period, adjust=False).mean()

    def calc_tp_sl(
        self,
        entry: float,
        direction: str,
        atr: float,
        rr: float = 2.0,
        atr_mult: float = 1.5
    ) -> tuple[float, float]:
        """
        ATR'ye göre Take Profit ve Stop Loss hesapla.
        Returns: (target, stop_loss)
        """
        sl_dist = atr * atr_mult
        tp_dist = sl_dist * rr
        if direction == "BUY":
            return round(entry + tp_dist, 8), round(entry - sl_dist, 8)
        else:  # SHORT
            return round(entry - tp_dist, 8), round(entry + sl_dist, 8)

    def find_swing_lows(self, arr: np.ndarray, window: int = 3) -> list:
        """Lokal minimum noktaları bul"""
        lows = []
        for i in range(window, len(arr) - window):
            if arr[i] == arr[i - window:i + window + 1].min():
                lows.append((i, arr[i]))
        return lows

    def find_swing_highs(self, arr: np.ndarray, window: int = 3) -> list:
        """Lokal maksimum noktaları bul"""
        highs = []
        for i in range(window, len(arr) - window):
            if arr[i] == arr[i - window:i + window + 1].max():
                highs.append((i, arr[i]))
        return highs
