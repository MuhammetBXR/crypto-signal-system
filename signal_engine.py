"""
Signal Engine - Runs all strategies and combines signals
"""
from typing import List, Dict, Optional
from dataclasses import dataclass, field
import pandas as pd
from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed

from strategies.base_strategy import Signal
from strategies.channel_breakout import ChannelBreakoutStrategy
from strategies.rsi_divergence import RSIDivergenceStrategy
from strategies.volume_spike import VolumeSpikeStrategy
from strategies.ema_cross import EMACrossStrategy
from strategies.support_resistance import SupportResistanceStrategy
from strategies.macd_conf import MACDStrategy
from strategies.bollinger_bands import BollingerBandsStrategy
import config
from ta.trend import EMAIndicator


@dataclass
class ConfluentSignal:
    """Signal with confluence from multiple strategies"""
    symbol: str
    timeframe: str
    strategies: List[str]
    direction: str
    price: float
    target: float
    stop_loss: float
    confluence_score: int
    confidence: float
    reasons: List[str]
    
    def to_dict(self) -> dict:
        """Convert to database format"""
        return {
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'strategies': self.strategies,
            'direction': self.direction,
            'entry_price': self.price,
            'target': self.target,
            'stop_loss': self.stop_loss,
            'confidence_score': self.confluence_score,
            'reason': ' | '.join(self.reasons)
        }


class SignalEngine:
    """Runs all strategies and combines signals"""
    
    def __init__(self):
        # Initialize all strategies
        self.strategies = [
            ChannelBreakoutStrategy(),
            RSIDivergenceStrategy(),
            VolumeSpikeStrategy(),
            EMACrossStrategy(),
            SupportResistanceStrategy(),
            MACDStrategy(),
            BollingerBandsStrategy(),
        ]
        logger.info(f"Initialized {len(self.strategies)} strategies")
    
    def analyze_symbol(
        self,
        symbol: str,
        data: Dict[str, pd.DataFrame]
    ) -> List[ConfluentSignal]:
        """
        Analyze a symbol across all timeframes and strategies
        
        Args:
            symbol: Trading pair (e.g., BTC/USDT)
            data: Dict of {timeframe: DataFrame}
        
        Returns:
            List of confluent signals
        """
        # 1. Market Structure Filter (Global Trend)
        market_trend = self._get_market_trend(data)
        
        all_signals = []
        
        # Run each strategy on each timeframe
        for timeframe, df in data.items():
            if df is None or df.empty:
                continue
            
            for strategy in self.strategies:
                try:
                    signal = strategy.analyze(df, symbol, timeframe)
                    if signal:
                        # 2. Filter signal based on market trend
                        if self._is_aligned_with_market(signal, market_trend):
                            all_signals.append(signal)
                        else:
                            logger.info(f"Filtered {signal.direction} signal for {symbol} due to market trend mismatch ({market_trend})")
                except Exception as e:
                    logger.error(f"Error in {strategy.name} for {symbol} {timeframe}: {e}")
        
        # 3. Calculate confluence and MTF
        confluent_signals = self._calculate_confluence(all_signals)
        
        return confluent_signals

    def _get_market_trend(self, data: Dict[str, pd.DataFrame]) -> str:
        """Determine global market trend using BTC (if available) or current symbol"""
        # In a real scenario, we'd fetch BTC/USDT specifically. 
        # For now, let's look at the highest timeframe available (1d or 4h)
        for tf in ['1d', '4h']:
            if tf in data and len(data[tf]) > 200:
                df = data[tf]
                ema200 = EMAIndicator(close=df['close'], window=200).ema_indicator()
                current_price = df['close'].iloc[-1]
                current_ema = ema200.iloc[-1]
                
                if current_price > current_ema:
                    return 'BULLISH'
                else:
                    return 'BEARISH'
        
        return 'NEUTRAL'

    def _is_aligned_with_market(self, signal: Signal, market_trend: str) -> bool:
        """Check if signal direction aligns with global market trend"""
        if market_trend == 'NEUTRAL':
            return True
        if market_trend == 'BULLISH' and signal.direction == 'BUY':
            return True
        if market_trend == 'BEARISH' and signal.direction == 'SELL':
            return True
        return False
    
    def _calculate_confluence(self, signals: List[Signal]) -> List[ConfluentSignal]:
        """Group signals by direction and calculate confluence"""
        if not signals:
            return []
        
        # Group by direction
        buy_signals = [s for s in signals if s.direction == 'BUY']
        sell_signals = [s for s in signals if s.direction == 'SELL']
        
        confluent_signals = []
        
        # Process BUY signals
        if len(buy_signals) >= config.MIN_CONFLUENCE_SCORE:
            confluent_signals.append(self._merge_signals(buy_signals, 'BUY'))
        
        # Process SELL signals
        if len(sell_signals) >= config.MIN_CONFLUENCE_SCORE:
            confluent_signals.append(self._merge_signals(sell_signals, 'SELL'))
        
        return confluent_signals
    
    def _merge_signals(self, signals: List[Signal], direction: str) -> ConfluentSignal:
        """Merge multiple signals into one confluent signal"""
        # Get unique strategies and timeframes
        strategies = list(set(s.strategy for s in signals))
        timeframes = list(set(s.timeframe for s in signals))
        
        # Create strategy-timeframe pairs for better display
        strategy_details = []
        for s in signals:
            detail = f"{s.strategy} ({s.timeframe})" if len(signals) > 1 else s.strategy
            strategy_details.append(detail)
        
        # Average price, target, stop_loss
        avg_price = sum(s.price for s in signals) / len(signals)
        avg_target = sum(s.target for s in signals) / len(signals)
        avg_stop_loss = sum(s.stop_loss for s in signals) / len(signals)
        avg_confidence = sum(s.confidence for s in signals) / len(signals)
        
        # Check for MTF (Multiple Timeframe Confirmation)
        is_mtf = len(timeframes) >= 2
        
        merged_confidence = avg_confidence
        if is_mtf:
            merged_confidence = min(1.0, avg_confidence + 0.1)  # Bonus for MTF
            reasons.append(f"MTF Confirmation ({', '.join(timeframes)})")
            
        return ConfluentSignal(
            symbol=signals[0].symbol,
            timeframe=', '.join(sorted(timeframes)),
            strategies=strategy_details,
            direction=direction,
            price=avg_price,
            target=avg_target,
            stop_loss=avg_stop_loss,
            confluence_score=len(signals),
            confidence=merged_confidence,
            reasons=reasons
        )
    
    def analyze_all(
        self,
        all_data: Dict[str, Dict[str, pd.DataFrame]],
        max_workers: int = 10
    ) -> List[ConfluentSignal]:
        """
        Analyze all symbols concurrently
        
        Args:
            all_data: {symbol: {timeframe: DataFrame}}
            max_workers: Number of concurrent workers
        
        Returns:
            List of all confluent signals
        """
        all_signals = []
        total_symbols = len(all_data)
        
        logger.info(f"Analyzing {total_symbols} symbols...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_symbol = {
                executor.submit(self.analyze_symbol, symbol, data): symbol
                for symbol, data in all_data.items()
            }
            
            completed = 0
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                completed += 1
                
                try:
                    signals = future.result()
                    all_signals.extend(signals)
                    
                    if completed % 100 == 0:
                        logger.info(f"Analyzed {completed}/{total_symbols} symbols, found {len(all_signals)} signals so far")
                        
                except Exception as e:
                    logger.error(f"Error analyzing {symbol}: {e}")
        
        logger.info(f"Analysis complete: {len(all_signals)} signals from {total_symbols} symbols")
        return all_signals
