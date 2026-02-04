"""
Volume Spike Strategy
Detects unusual volume spikes with directional price action
"""
import pandas as pd
from typing import Optional
from .base_strategy import BaseStrategy, Signal
import config


class VolumeSpikeStrategy(BaseStrategy):
    """Detects volume spikes with strong price action"""
    
    def __init__(self):
        params = config.STRATEGY_PARAMS['volume_spike']
        super().__init__(params)
    
    def analyze(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Optional[Signal]:
        """Analyze for volume spikes"""
        if len(df) < self.params['volume_period'] + 2:
            return None
        
        # Calculate average volume
        avg_volume = df['volume'].tail(self.params['volume_period']).mean()
        
        # Current candle
        current = df.iloc[-1]
        current_volume = current['volume']
        
        # Check for volume spike
        volume_ratio = current_volume / avg_volume
        if volume_ratio < self.params['spike_multiplier']:
            return None
        
        # Calculate candle body
        candle_body = abs(current['close'] - current['open'])
        candle_range = current['high'] - current['low']
        
        if candle_range == 0:
            return None
        
        body_ratio = candle_body / candle_range
        min_body_percent = self.params['min_candle_body']
        
        # Avoid doji candles (no clear direction)
        if body_ratio < 0.3:
            return None
        
        # Calculate price change percentage
        price_change = (current['close'] - current['open']) / current['open']
        
        # Bullish volume spike (strong upward candle)
        if (current['close'] > current['open'] and 
            abs(price_change) >= min_body_percent):
            
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
                confidence=0.70,
                reason=f"Bullish Volume Spike ({volume_ratio:.1f}x avg, +{price_change*100:.1f}%)"
            )
        
        # Bearish volume spike (strong downward candle)
        if (current['close'] < current['open'] and 
            abs(price_change) >= min_body_percent):
            
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
                confidence=0.70,
                reason=f"Bearish Volume Spike ({volume_ratio:.1f}x avg, {price_change*100:.1f}%)"
            )
        
        return None
