"""
EMA Cross Strategy
Golden Cross and Death Cross with ADX trend filter
"""
import pandas as pd
from typing import Optional
from ta.trend import EMAIndicator, ADXIndicator
from .base_strategy import BaseStrategy, Signal
import config


class EMACrossStrategy(BaseStrategy):
    """EMA 50/200 crossover with trend strength filter"""
    
    def __init__(self):
        params = config.STRATEGY_PARAMS['ema_cross']
        super().__init__(params)
    
    def analyze(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Optional[Signal]:
        """Analyze for EMA crossover"""
        required_length = max(self.params['slow_period'], self.params['adx_period']) + 5
        if len(df) < required_length:
            return None
        
        # Calculate EMAs
        ema_fast = EMAIndicator(close=df['close'], window=self.params['fast_period'])
        ema_slow = EMAIndicator(close=df['close'], window=self.params['slow_period'])
        
        df_copy = df.copy()
        df_copy['ema_fast'] = ema_fast.ema_indicator()
        df_copy['ema_slow'] = ema_slow.ema_indicator()
        
        # Calculate ADX for trend strength
        adx = ADXIndicator(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=self.params['adx_period']
        )
        df_copy['adx'] = adx.adx()
        
        # Get current and previous values
        current = df_copy.iloc[-1]
        previous = df_copy.iloc[-2]
        
        # Check ADX trend strength
        if current['adx'] < self.params['min_adx']:
            return None  # No strong trend
        
        current_price = current['close']
        
        # Golden Cross (bullish)
        if (previous['ema_fast'] <= previous['ema_slow'] and 
            current['ema_fast'] > current['ema_slow']):
            
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
                confidence=0.85,
                reason=f"Golden Cross (EMA 50/200, ADX: {current['adx']:.1f})"
            )
        
        # Death Cross (bearish)
        if (previous['ema_fast'] >= previous['ema_slow'] and 
            current['ema_fast'] < current['ema_slow']):
            
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
                confidence=0.85,
                reason=f"Death Cross (EMA 50/200, ADX: {current['adx']:.1f})"
            )
        
        return None
