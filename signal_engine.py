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
import config


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
        all_signals = []
        
        # Run each strategy on each timeframe
        for timeframe, df in data.items():
            if df is None or df.empty:
                continue
            
            for strategy in self.strategies:
                try:
                    signal = strategy.analyze(df, symbol, timeframe)
                    if signal:
                        all_signals.append(signal)
                except Exception as e:
                    logger.error(f"Error in {strategy.name} for {symbol} {timeframe}: {e}")
        
        # Calculate confluence
        confluent_signals = self._calculate_confluence(all_signals)
        
        return confluent_signals
    
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
        
        # Collect reasons
        reasons = [s.reason for s in signals]
        
        return ConfluentSignal(
            symbol=signals[0].symbol,
            timeframe=', '.join(sorted(timeframes)),
            strategies=strategy_details,  # Use detailed list instead of unique names
            direction=direction,
            price=avg_price,
            target=avg_target,
            stop_loss=avg_stop_loss,
            confluence_score=len(signals),
            confidence=avg_confidence,
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
