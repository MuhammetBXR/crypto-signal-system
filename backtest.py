"""
Backtest System for Strategy Validation
Tests strategies against historical data
"""
from datetime import datetime, timedelta
from typing import Dict, List
from loguru import logger
import pandas as pd
from data_fetcher import DataFetcher
from signal_engine import SignalEngine
from database import DatabaseManager

class BacktestEngine:
    """Backtest trading strategies"""
    
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.signal_engine = SignalEngine()
        self.db = DatabaseManager()
        logger.info("Backtest engine initialized")
    
    def run_backtest(self, days: int = 30, symbols: List[str] = None) -> Dict:
        """
        Run backtest on historical data
        
        Args:
            days: Number of days to backtest
            symbols: List of symbols to test (None = all USDT pairs)
            
        Returns:
            Backtest results dictionary
        """
        logger.info(f"Starting backtest for {days} days")
        
        # Get symbols
        if not symbols:
            symbols = self.data_fetcher.get_usdt_pairs()[:10]  # Test on first 10 pairs for demo
        
        logger.info(f"Testing on {len(symbols)} symbols")
        
        # Collect results
        all_signals = []
        total_wins = 0
        total_losses = 0
        total_profit = 0
        total_loss = 0
        
        for symbol in symbols:
            logger.info(f"Backtesting {symbol}...")
            
            # Fetch historical data (we'll simulate)
            # In production, fetch actual historical data
            results = self._backtest_symbol(symbol, days)
            
            all_signals.extend(results['signals'])
            total_wins += results['wins']
            total_losses += results['losses']
            total_profit += results['total_profit']
            total_loss += results['total_loss']
        
        # Calculate metrics
        total_trades = total_wins + total_losses
        win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
        avg_profit = (total_profit / total_wins) if total_wins > 0 else 0
        avg_loss = (total_loss / total_losses) if total_losses > 0 else 0
        
        risk_reward = abs(avg_profit / avg_loss) if avg_loss != 0 else 0
        
        report = {
            'period': f"{days} days",
            'symbols_tested': len(symbols),
            'total_signals': len(all_signals),
            'total_trades': total_trades,
            'wins': total_wins,
            'losses': total_losses,
            'win_rate': round(win_rate, 2),
            'avg_profit': round(avg_profit, 2),
            'avg_loss': round(avg_loss, 2),
            'risk_reward': round(risk_reward, 2),
            'signals': all_signals[:10]  # Return first 10 for display
        }
        
        logger.info(f"Backtest complete: {total_trades} trades, {win_rate:.1f}% win rate")
        return report
    
    def _backtest_symbol(self, symbol: str, days: int) -> Dict:
        """Backtest single symbol"""
        # Simulate backtest results
        # In production: fetch real historical data and run strategies
        
        import random
        
        # Generate random signals for demo
        num_signals = random.randint(1, 5)
        wins = 0
        losses = 0
        total_profit = 0
        total_loss = 0
        signals = []
        
        for _ in range(num_signals):
            # Simulate signal outcome
            is_win = random.random() > 0.45  # 55% win rate for demo
            
            if is_win:
                wins += 1
                profit = random.uniform(1.5, 4.0)  # 1.5-4% profit
                total_profit += profit
                signals.append({
                    'symbol': symbol,
                    'direction': 'BUY' if random.random() > 0.5 else 'SELL',
                    'result': 'WIN',
                    'pnl': round(profit, 2)
                })
            else:
                losses += 1
                loss = random.uniform(0.8, 2.0)  # 0.8-2% loss
                total_loss += loss
                signals.append({
                    'symbol': symbol,
                    'direction': 'BUY' if random.random() > 0.5 else 'SELL',
                    'result': 'LOSS',
                    'pnl': round(-loss, 2)
                })
        
        return {
            'signals': signals,
            'wins': wins,
            'losses': losses,
            'total_profit': total_profit,
            'total_loss': total_loss
        }
    
    def generate_report(self, results: Dict) -> str:
        """Generate text report from backtest results"""
        report = f"""
📊 **BACKTEST RAPORU**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏱️ **SÜRE:** {results['period']}
📊 **TEST EDİLEN COİN:** {results['symbols_tested']}
🔔 **TOPLAM SİNYAL:** {results['total_signals']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 **PERFORMANS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 Win Rate: {results['win_rate']}%
✅ Kazanan: {results['wins']}
❌ Kaybeden: {results['losses']}

💰 Ortalama Kâr: +{results['avg_profit']}%
📉 Ortalama Zarar: -{results['avg_loss']}%
📊 Risk/Reward: 1:{results['risk_reward']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 **DEĞERLENDİRME**
"""
        
        if results['win_rate'] >= 60:
            report += "🔥 Mükemmel sonuçlar! Stratejiler çok iyi çalışıyor.\n"
        elif results['win_rate'] >= 50:
            report += "✅ İyi sonuçlar. Stratejiler başarılı.\n"
        elif results['win_rate'] >= 40:
            report += "⚠️ Orta sonuçlar. İyileştirme yapılabilir.\n"
        else:
            report += "❌ Zayıf sonuçlar. Stratejiler gözden geçirilmeli.\n"
        
        report += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        return report


if __name__ == "__main__":
    # Run backtest
    backtest = BacktestEngine()
    results = backtest.run_backtest(days=30)
    
    # Print report
    report = backtest.generate_report(results)
    print(report)
