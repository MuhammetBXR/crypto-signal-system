"""
MACD Confirmation Strategy
Detects MACD line and Signal line crossovers
"""
import pandas as pd
from typing import Optional
from ta.trend import MACD
from .base_strategy import BaseStrategy, Signal
import config

class MACDStrategy(BaseStrategy):
    """MACD crossover strategy for trend confirmation"""
    
    def __init__(self):
        params = config.STRATEGY_PARAMS['macd']
        super().__init__(params)
        self.name = "MACDStrategy"
    
    def analyze(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Optional[Signal]:
        """Analyze for MACD crossover"""
        if len(df) < self.params['slow_period'] + 10:
            return None
        
        # Calculate MACD
        macd_ind = MACD(
            close=df['close'],
            window_fast=self.params['fast_period'],
            window_slow=self.params['slow_period'],
            window_sign=self.params['signal_period']
        )
        
        df_copy = df.copy()
        df_copy['macd'] = macd_ind.macd()
        df_copy['signal'] = macd_ind.macd_signal()
        df_copy['diff'] = macd_ind.macd_diff()
        
        current = df_copy.iloc[-1]
        previous = df_copy.iloc[-2]
        
        # Bullish Crossover (MACD crosses above Signal)
        if previous['macd'] <= previous['signal'] and current['macd'] > current['signal']:
            target, stop_loss = self.calculate_target_stop(
                current['close'],
                'BUY',
                stop_percent=config.DEFAULT_STOP_LOSS_PERCENT
            )
            
            return Signal(
                symbol=symbol,
                timeframe=timeframe,
                strategy=self.name,
                direction='BUY',
                price=float(current['close']),
                target=float(target),
                stop_loss=float(stop_loss),
                confidence=0.80,
                reason=f"Bullish MACD Cross (MACD: {current['macd']:.4f})"
            )
            
        # Bearish Crossover (MACD crosses below Signal)
        if previous['macd'] >= previous['signal'] and current['macd'] < current['signal']:
            target, stop_loss = self.calculate_target_stop(
                current['close'],
                'SELL',
                stop_percent=config.DEFAULT_STOP_LOSS_PERCENT
            )
            
            return Signal(
                symbol=symbol,
                timeframe=timeframe,
                strategy=self.name,
                direction='SELL',
                price=float(current['close']),
                target=float(target),
                stop_loss=float(stop_loss),
                confidence=0.80,
                reason=f"Bearish MACD Cross (MACD: {current['macd']:.4f})"
            )
            
        return None
