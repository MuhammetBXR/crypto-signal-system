"""
Base strategy class - All strategies inherit from this
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import pandas as pd


@dataclass
class Signal:
    """Signal dataclass"""
    symbol: str
    timeframe: str
    strategy: str
    direction: str  # 'BUY' or 'SELL'
    price: float
    target: float
    stop_loss: float
    confidence: float  # 0.0 - 1.0
    reason: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database storage"""
        return {
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'strategies': [self.strategy],  # Will be merged in confluence
            'direction': self.direction,
            'entry_price': self.price,
            'target': self.target,
            'stop_loss': self.stop_loss,
            'confidence_score': 1,  # Initial score, will be updated
            'reason': self.reason,
        }


class BaseStrategy(ABC):
    """Abstract base class for all trading strategies"""
    
    def __init__(self, params: dict = None):
        self.params = params or {}
        self.name = self.__class__.__name__
    
    @abstractmethod
    def analyze(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Optional[Signal]:
        """
        Analyze data and return signal if conditions are met
        
        Args:
            df: OHLCV DataFrame with columns [open, high, low, close, volume]
            symbol: Trading pair symbol (e.g., BTC/USDT)
            timeframe: Timeframe string (e.g., '1h')
        
        Returns:
            Signal object if conditions are met, None otherwise
        """
        pass
    
    def get_name(self) -> str:
        """Get strategy name"""
        return self.name
    
    def calculate_target_stop(
        self,
        entry_price: float,
        direction: str,
        atr: float = None,
        rr_ratio: float = 2.0,
        stop_percent: float = 1.5
    ) -> tuple:
        """
        Calculate target and stop loss prices
        
        Args:
            entry_price: Entry price
            direction: 'BUY' or 'SELL'
            atr: Average True Range (optional, for dynamic stops)
            rr_ratio: Risk-Reward ratio
            stop_percent: Stop loss percentage
        
        Returns:
            (target_price, stop_loss_price)
        """
        if direction == 'BUY':
            if atr:
                stop_loss = entry_price - (atr * 1.5)
                target = entry_price + (atr * 1.5 * rr_ratio)
            else:
                stop_loss = entry_price * (1 - stop_percent / 100)
                target = entry_price * (1 + (stop_percent * rr_ratio) / 100)
        else:  # SELL
            if atr:
                stop_loss = entry_price + (atr * 1.5)
                target = entry_price - (atr * 1.5 * rr_ratio)
            else:
                stop_loss = entry_price * (1 + stop_percent / 100)
                target = entry_price * (1 - (stop_percent * rr_ratio) / 100)
        
        return round(target, 8), round(stop_loss, 8)
