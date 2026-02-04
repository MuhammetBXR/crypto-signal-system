"""
Bollinger Bands Squeeze and Breakout Strategy
"""
import pandas as pd
from typing import Optional
from ta.volatility import BollingerBands
from .base_strategy import BaseStrategy, Signal
import config

class BollingerBandsStrategy(BaseStrategy):
    """Detects Bollinger Bands squeeze and breakouts"""
    
    def __init__(self):
        params = config.STRATEGY_PARAMS['bollinger_bands']
        super().__init__(params)
        self.name = "BollingerBandsStrategy"
    
    def analyze(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Optional[Signal]:
        """Analyze for BB squeeze and breakout"""
        if len(df) < self.params['period'] + 5:
            return None
            
        bb = BollingerBands(
            close=df['close'],
            window=self.params['period'],
            window_dev=self.params['std_dev']
        )
        
        df_copy = df.copy()
        df_copy['bb_high'] = bb.bollinger_hband()
        df_copy['bb_low'] = bb.bollinger_lband()
        df_copy['bb_mid'] = bb.bollinger_mavg()
        
        # Calculate bandwidth for squeeze detection
        df_copy['bandwidth'] = (df_copy['bb_high'] - df_copy['bb_low']) / df_copy['bb_mid']
        
        current = df_copy.iloc[-1]
        previous = df_copy.iloc[-2]
        
        # Squeeze detection: bandwidth is low
        is_squeeze = current['bandwidth'] < self.params['squeeze_threshold']
        
        # Bullish Breakout
        if current['close'] > current['bb_high'] and previous['close'] <= previous['bb_high']:
            target, stop_loss = self.calculate_target_stop(
                current['close'],
                'BUY',
                stop_percent=config.DEFAULT_STOP_LOSS_PERCENT
            )
            
            squeeze_text = " after Squeeze" if is_squeeze else ""
            return Signal(
                symbol=symbol,
                timeframe=timeframe,
                strategy=self.name,
                direction='BUY',
                price=float(current['close']),
                target=float(target),
                stop_loss=float(stop_loss),
                confidence=0.85 if is_squeeze else 0.75,
                reason=f"Bollinger Top Breakout{squeeze_text}"
            )
            
        # Bearish Breakout
        if current['close'] < current['bb_low'] and previous['close'] >= previous['bb_low']:
            target, stop_loss = self.calculate_target_stop(
                current['close'],
                'SELL',
                stop_percent=config.DEFAULT_STOP_LOSS_PERCENT
            )
            
            squeeze_text = " after Squeeze" if is_squeeze else ""
            return Signal(
                symbol=symbol,
                timeframe=timeframe,
                strategy=self.name,
                direction='SELL',
                price=float(current['close']),
                target=float(target),
                stop_loss=float(stop_loss),
                confidence=0.85 if is_squeeze else 0.75,
                reason=f"Bollinger Bottom Breakout{squeeze_text}"
            )
            
        return None
