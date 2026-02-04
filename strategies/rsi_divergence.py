"""
RSI Divergence Strategy
Detects regular and hidden divergences
"""
import pandas as pd
import numpy as np
from typing import Optional
from ta.momentum import RSIIndicator
from .base_strategy import BaseStrategy, Signal
import config


class RSIDivergenceStrategy(BaseStrategy):
    """Detects RSI divergences (bullish and bearish)"""
    
    def __init__(self):
        params = config.STRATEGY_PARAMS['rsi_divergence']
        super().__init__(params)
    
    def analyze(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Optional[Signal]:
        """Analyze for RSI divergence"""
        if len(df) < self.params['divergence_lookback'] + self.params['rsi_period']:
            return None
        
        # Calculate RSI
        rsi = RSIIndicator(close=df['close'], window=self.params['rsi_period'])
        df_copy = df.copy()
        df_copy['rsi'] = rsi.rsi()
        
        # Get recent window
        lookback = self.params['divergence_lookback']
        recent = df_copy.tail(lookback)
        
        # Find price swings
        price_lows = self._find_swing_lows(recent['low'].values)
        price_highs = self._find_swing_highs(recent['high'].values)
        
        # Find RSI swings
        rsi_lows = self._find_swing_lows(recent['rsi'].values)
        rsi_highs = self._find_swing_highs(recent['rsi'].values)
        
        current_rsi = df_copy['rsi'].iloc[-1]
        current_price = df_copy['close'].iloc[-1]
        
        # Bullish Regular Divergence (price lower low, RSI higher low)
        if len(price_lows) >= 2 and len(rsi_lows) >= 2:
            if (price_lows[-1] < price_lows[-2] and 
                rsi_lows[-1] > rsi_lows[-2] and
                current_rsi < self.params['rsi_oversold']):
                
                price_move = abs((price_lows[-1] - price_lows[-2]) / price_lows[-2])
                if price_move >= self.params['min_price_swing']:
                    
                    target, stop_loss = self.calculate_target_stop(
                        current_price,
                        'BUY',
                        stop_percent=config.DEFAULT_STOP_LOSS_PERCENT
                    )
                    
                    return Signal(
                        symbol=symbol,
                        timeframe=timeframe,
                        strategy=self.name,
                        direction='BUY',
                        price=float(current_price),
                        target=float(target),
                        stop_loss=float(stop_loss),
                        confidence=0.80,
                        reason=f"Bullish RSI Divergence (RSI: {current_rsi:.1f})"
                    )
        
        # Bearish Regular Divergence (price higher high, RSI lower high)
        if len(price_highs) >= 2 and len(rsi_highs) >= 2:
            if (price_highs[-1] > price_highs[-2] and 
                rsi_highs[-1] < rsi_highs[-2] and
                current_rsi > self.params['rsi_overbought']):
                
                price_move = abs((price_highs[-1] - price_highs[-2]) / price_highs[-2])
                if price_move >= self.params['min_price_swing']:
                    
                    target, stop_loss = self.calculate_target_stop(
                        current_price,
                        'SELL',
                        stop_percent=config.DEFAULT_STOP_LOSS_PERCENT
                    )
                    
                    return Signal(
                        symbol=symbol,
                        timeframe=timeframe,
                        strategy=self.name,
                        direction='SELL',
                        price=float(current_price),
                        target=float(target),
                        stop_loss=float(stop_loss),
                        confidence=0.80,
                        reason=f"Bearish RSI Divergence (RSI: {current_rsi:.1f})"
                    )
        
        return None
    
    def _find_swing_lows(self, data: np.ndarray, window: int = 3) -> list:
        """Find swing low points"""
        swings = []
        for i in range(window, len(data) - window):
            if data[i] == min(data[i-window:i+window+1]):
                swings.append(data[i])
        return swings
    
    def _find_swing_highs(self, data: np.ndarray, window: int = 3) -> list:
        """Find swing high points"""
        swings = []
        for i in range(window, len(data) - window):
            if data[i] == max(data[i-window:i+window+1]):
                swings.append(data[i])
        return swings
