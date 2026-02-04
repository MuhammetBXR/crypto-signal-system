"""
Test script to verify the system works before running full cycle
"""
from loguru import logger
import sys

logger.remove()
logger.add(sys.stderr, level="INFO")


def test_imports():
    """Test all imports"""
    logger.info("Testing imports...")
    try:
        import ccxt
        import pandas as pd
        import numpy as np
        from ta.momentum import RSIIndicator
        from ta.trend import EMAIndicator, ADXIndicator
        from telegram import Bot
        from scipy import stats
        from sqlalchemy import create_engine
        
        logger.info("✅ All imports successful")
        return True
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        return False


def test_config():
    """Test configuration"""
    logger.info("Testing configuration...")
    try:
        import config
        
        logger.info(f"  - Database path: {config.DATABASE_PATH}")
        logger.info(f"  - Timeframes: {config.TIMEFRAMES}")
        logger.info(f"  - Min confluence: {config.MIN_CONFLUENCE_SCORE}")
        logger.info(f"  - Telegram configured: {bool(config.TELEGRAM_BOT_TOKEN)}")
        
        logger.info("✅ Configuration loaded")
        return True
    except Exception as e:
        logger.error(f"❌ Config error: {e}")
        return False


def test_database():
    """Test database connection"""
    logger.info("Testing database...")
    try:
        from database import DatabaseManager
        
        db = DatabaseManager()
        stats = db.get_overall_stats()
        
        logger.info(f"  - Database connected: {db.db_path}")
        logger.info(f"  - Total signals: {stats['total_signals']}")
        
        logger.info("✅ Database working")
        return True
    except Exception as e:
        logger.error(f"❌ Database error: {e}")
        return False


def test_data_fetcher():
    """Test Binance connection"""
    logger.info("Testing Binance connection...")
    try:
        from data_fetcher import DataFetcher
        
        fetcher = DataFetcher()
        pairs = fetcher.get_usdt_pairs()
        
        logger.info(f"  - Found {len(pairs)} USDT pairs")
        
        # Test fetching one symbol
        logger.info("  - Testing BTC/USDT data fetch...")
        data = fetcher.fetch_ohlcv('BTC/USDT', '1h', limit=10)
        
        if data is not None and not data.empty:
            logger.info(f"  - Fetched {len(data)} candles")
            logger.info(f"  - Latest BTC price: ${data['close'].iloc[-1]:,.2f}")
            logger.info("✅ Data fetcher working")
            return True
        else:
            logger.error("❌ Could not fetch data")
            return False
            
    except Exception as e:
        logger.error(f"❌ Data fetcher error: {e}")
        return False


def test_strategies():
    """Test strategy initialization"""
    logger.info("Testing strategies...")
    try:
        from strategies.channel_breakout import ChannelBreakoutStrategy
        from strategies.rsi_divergence import RSIDivergenceStrategy
        from strategies.volume_spike import VolumeSpikeStrategy
        from strategies.ema_cross import EMACrossStrategy
        from strategies.support_resistance import SupportResistanceStrategy
        
        strategies = [
            ChannelBreakoutStrategy(),
            RSIDivergenceStrategy(),
            VolumeSpikeStrategy(),
            EMACrossStrategy(),
            SupportResistanceStrategy(),
        ]
        
        for strategy in strategies:
            logger.info(f"  - {strategy.name}: ✓")
        
        logger.info("✅ All strategies initialized")
        return True
    except Exception as e:
        logger.error(f"❌ Strategy error: {e}")
        return False


def test_telegram():
    """Test Telegram bot"""
    logger.info("Testing Telegram...")
    try:
        from telegram_bot import TelegramNotifier
        
        telegram = TelegramNotifier()
        
        if telegram.enabled:
            logger.info("  - Telegram configured")
            logger.info("  - Sending test message...")
            
            success = telegram.send_message("🧪 Test message from Crypto Signal System")
            
            if success:
                logger.info("✅ Telegram working - Check your phone!")
                return True
            else:
                logger.warning("⚠️ Message send failed - check credentials")
                return False
        else:
            logger.warning("⚠️ Telegram not configured (optional)")
            return True
            
    except Exception as e:
        logger.error(f"❌ Telegram error: {e}")
        return False


def main():
    """Run all tests"""
    logger.info("="*60)
    logger.info("CRYPTO SIGNAL SYSTEM - TEST SUITE")
    logger.info("="*60 + "\n")
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Database", test_database),
        ("Data Fetcher", test_data_fetcher),
        ("Strategies", test_strategies),
        ("Telegram", test_telegram),
    ]
    
    results = []
    
    for name, test_func in tests:
        logger.info(f"\n{'='*60}")
        result = test_func()
        results.append((name, result))
        logger.info(f"{'='*60}\n")
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{name:20} - {status}")
    
    all_passed = all(r for _, r in results)
    
    logger.info("="*60)
    
    if all_passed:
        logger.info("\n🎉 All tests passed! System is ready to run.")
        logger.info("Run: python main.py")
    else:
        logger.warning("\n⚠️ Some tests failed. Fix issues before running.")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
