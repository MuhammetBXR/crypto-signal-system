"""
Support/Resistance Breakout Strategy
Detects key levels and breakouts with volume confirmation
"""
import pandas as pd
import numpy as np
from typing import Optional, List
from .base_strategy import BaseStrategy, Signal
import config


class SupportResistanceStrategy(BaseStrategy):
    """Detects support/resistance levels and breakouts"""
    
    def __init__(self):
        params = config.STRATEGY_PARAMS['support_resistance']
        super().__init__(params)
    
    def analyze(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Optional[Signal]:
        """Analyze for support/resistance breakout"""
        if len(df) < self.params['swing_lookback'] + 10:
            return None
        
        # Find support and resistance levels
        lookback = self.params['swing_lookback']
        recent = df.tail(lookback)
        
        resistance_levels = self._find_resistance_levels(recent)
        support_levels = self._find_support_levels(recent)
        
        if not resistance_levels and not support_levels:
            return None
        
        # Get current candle
        current = df.iloc[-1]
        previous = df.iloc[-2]
        current_price = current['close']
        
        # Calculate volume confirmation
        avg_volume = df['volume'].tail(20).mean()
        volume_ratio = current['volume'] / avg_volume
        
        # Check resistance breakout (bullish)
        for resistance in resistance_levels:
            proximity = abs(current_price - resistance) / resistance
            
            if (previous['close'] < resistance and 
                current['close'] > resistance and
                proximity <= self.params['proximity_threshold'] and
                volume_ratio >= self.params['breakout_volume_multiplier']):
                
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
                    confidence=0.75,
                    reason=f"Resistance Breakout at ${resistance:.4f} (Vol: {volume_ratio:.1f}x)"
                )
        
        # Check support breakdown (bearish)
        for support in support_levels:
            proximity = abs(current_price - support) / support
            
            if (previous['close'] > support and 
                current['close'] < support and
                proximity <= self.params['proximity_threshold'] and
                volume_ratio >= self.params['breakout_volume_multiplier']):
                
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
                    confidence=0.75,
                    reason=f"Support Breakdown at ${support:.4f} (Vol: {volume_ratio:.1f}x)"
                )
        
        return None
    
    def _find_resistance_levels(self, df: pd.DataFrame) -> List[float]:
        """Find resistance levels from swing highs"""
        highs = df['high'].values
        levels = []
        
        # Find swing highs
        for i in range(2, len(highs) - 2):
            if highs[i] == max(highs[i-2:i+3]):
                levels.append(highs[i])
        
        # Cluster nearby levels
        levels = self._cluster_levels(levels)
        
        # Filter by minimum touches
        validated_levels = []
        for level in levels:
            touches = self._count_touches(df, level, is_resistance=True)
            if touches >= self.params['min_touches']:
                validated_levels.append(level)
        
        return validated_levels
    
    def _find_support_levels(self, df: pd.DataFrame) -> List[float]:
        """Find support levels from swing lows"""
        lows = df['low'].values
        levels = []
        
        # Find swing lows
        for i in range(2, len(lows) - 2):
            if lows[i] == min(lows[i-2:i+3]):
                levels.append(lows[i])
        
        # Cluster nearby levels
        levels = self._cluster_levels(levels)
        
        # Filter by minimum touches
        validated_levels = []
        for level in levels:
            touches = self._count_touches(df, level, is_resistance=False)
            if touches >= self.params['min_touches']:
                validated_levels.append(level)
        
        return validated_levels
    
    def _cluster_levels(self, levels: List[float], threshold: float = 0.005) -> List[float]:
        """Cluster nearby price levels"""
        if not levels:
            return []
        
        levels = sorted(levels)
        clustered = []
        current_cluster = [levels[0]]
        
        for level in levels[1:]:
            if abs(level - current_cluster[-1]) / current_cluster[-1] <= threshold:
                current_cluster.append(level)
            else:
                clustered.append(np.mean(current_cluster))
                current_cluster = [level]
        
        clustered.append(np.mean(current_cluster))
        return clustered
    
    def _count_touches(self, df: pd.DataFrame, level: float, is_resistance: bool) -> int:
        """Count how many times price touched a level"""
        threshold = self.params['proximity_threshold']
        touches = 0
        
        for _, row in df.iterrows():
            if is_resistance:
                if abs(row['high'] - level) / level <= threshold:
                    touches += 1
            else:
                if abs(row['low'] - level) / level <= threshold:
                    touches += 1
        
        return touches
