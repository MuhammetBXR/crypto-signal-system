"""
Channel Breakout Strategy
Detects falling/rising channels and breakout signals
"""
import pandas as pd
import numpy as np
from typing import Optional
from scipy import stats
from .base_strategy import BaseStrategy, Signal
import config


class ChannelBreakoutStrategy(BaseStrategy):
    """Detects channel patterns and breakouts"""
    
    def __init__(self):
        params = config.STRATEGY_PARAMS['channel_breakout']
        super().__init__(params)
    
    def analyze(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Optional[Signal]:
        """Analyze for channel breakout"""
        if len(df) < self.params['lookback_period']:
            return None
        
        # Get recent data
        lookback = self.params['lookback_period']
        recent = df.tail(lookback).copy()
        recent['index_col'] = range(len(recent))
        
        # Calculate upper and lower channel using linear regression
        highs = recent['high'].values
        lows = recent['low'].values
        x = recent['index_col'].values
        
        # Upper channel (resistance)
        slope_high, intercept_high, r_high, _, _ = stats.linregress(x, highs)
        upper_channel = slope_high * x + intercept_high
        
        # Lower channel (support)
        slope_low, intercept_low, r_low, _, _ = stats.linregress(x, lows)
        lower_channel = slope_low * x + intercept_low
        
        # Check if channel is well-defined (R-squared > 0.7)
        if abs(r_high) < 0.7 or abs(r_low) < 0.7:
            return None
        
        # Calculate channel width
        current_upper = upper_channel[-1]
        current_lower = lower_channel[-1]
        channel_width = (current_upper - current_lower) / current_lower
        
        # Ensure minimum channel width
        if channel_width < self.params['min_channel_width']:
            return None
        
        # Get current and previous candles
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        # Calculate average volume
        avg_volume = df['volume'].tail(20).mean()
        volume_ratio = current['volume'] / avg_volume
        
        # Check for upward breakout (Falling or Rising channel breakout to upside)
        if (previous['close'] <= current_upper and 
            current['close'] > current_upper and
            volume_ratio >= self.params['volume_multiplier']):
            
            target, stop_loss = self.calculate_target_stop(
                current['close'],
                'BUY',
                stop_percent=config.DEFAULT_STOP_LOSS_PERCENT
            )
            
            channel_type = "Falling" if slope_high < 0 else "Rising"
            
            return Signal(
                symbol=symbol,
                timeframe=timeframe,
                strategy=self.name,
                direction='BUY',
                price=float(current['close']),
                target=float(target),
                stop_loss=float(stop_loss),
                confidence=0.75,
                reason=f"{channel_type} Channel Upward Breakout (Vol: {volume_ratio:.1f}x)"
            )
        
        # Check for downward breakout
        if (previous['close'] >= current_lower and 
            current['close'] < current_lower and
            volume_ratio >= self.params['volume_multiplier']):
            
            target, stop_loss = self.calculate_target_stop(
                current['close'],
                'SELL',
                stop_percent=config.DEFAULT_STOP_LOSS_PERCENT
            )
            
            channel_type = "Rising" if slope_low > 0 else "Falling"
            
            return Signal(
                symbol=symbol,
                timeframe=timeframe,
                strategy=self.name,
                direction='SELL',
                price=float(current['close']),
                target=float(target),
                stop_loss=float(stop_loss),
                confidence=0.75,
                reason=f"{channel_type} Channel Downward Breakout (Vol: {volume_ratio:.1f}x)"
            )
        
        return None
