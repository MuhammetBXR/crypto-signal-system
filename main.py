"""
Main application - Crypto Signal System
"""
import time
import signal
import sys
from datetime import datetime
from loguru import logger

from data_fetcher import DataFetcher
from signal_engine import SignalEngine
from telegram_bot import TelegramNotifier
from database import DatabaseManager
import config

# Configure logger
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=config.LOG_LEVEL
)
logger.add(
    config.LOGS_DIR / "crypto_signals_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="7 days",
    level=config.LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}"
)


class CryptoSignalSystem:
    """Main system orchestrator"""
    
    def __init__(self):
        logger.info("=== Initializing Crypto Signal System ===")
        
        self.data_fetcher = DataFetcher()
        self.signal_engine = SignalEngine()
        self.telegram = TelegramNotifier()
        self.db = DatabaseManager()
        
        self.running = False
        self.cycle_count = 0
        
        # Setup graceful shutdown
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        
        logger.info("System initialized successfully")
    
    def shutdown(self, signum, frame):
        """Graceful shutdown"""
        logger.warning("Shutdown signal received. Stopping...")
        self.running = False
        sys.exit(0)
    
    def run_cycle(self):
        """Run one analysis cycle"""
        self.cycle_count += 1
        cycle_start = time.time()
        
        logger.info(f"\n{'='*60}")
        logger.info(f"CYCLE #{self.cycle_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'='*60}")
        
        try:
            # 1. Fetch data
            logger.info("Step 1: Fetching market data...")
            all_data = self.data_fetcher.fetch_all_pairs_data()
            
            if not all_data:
                logger.warning("No data fetched. Skipping cycle.")
                return
            
            logger.info(f"Fetched data for {len(all_data)} pairs")
            
            # 2. Analyze for signals
            logger.info("Step 2: Analyzing signals...")
            signals = self.signal_engine.analyze_all(all_data)
            
            logger.info(f"Found {len(signals)} potential signals")
            
            # 3. Filter signals (cooldown, max per cycle)
            logger.info("Step 3: Filtering signals...")
            filtered_signals = self.filter_signals(signals)
            
            logger.info(f"After filtering: {len(filtered_signals)} signals")
            
            # 4. Save to database and send notifications
            if filtered_signals:
                logger.info("Step 4: Saving signals and sending notifications...")
                self.process_signals(filtered_signals)
            else:
                logger.info("No signals to process")
            
            # 5. Update performance tracking
            logger.info("Step 5: Updating signal performance...")
            self.update_performance()
            
            cycle_duration = time.time() - cycle_start
            logger.info(f"Cycle completed in {cycle_duration:.1f} seconds")
            
        except Exception as e:
            logger.error(f"Error in cycle: {e}", exc_info=True)
            self.telegram.send_error_message(f"Cycle error: {str(e)}")
    
    def filter_signals(self, signals):
        """Filter signals based on cooldown and limits"""
        filtered = []
        
        for signal in signals:
            # Check cooldown
            if not self.db.can_send_signal(signal.symbol):
                logger.debug(f"Skipping {signal.symbol} - cooldown active")
                continue
            
            filtered.append(signal)
            
            # Check max signals per cycle
            if len(filtered) >= config.MAX_SIGNALS_PER_CYCLE:
                logger.warning(f"Reached max signals per cycle ({config.MAX_SIGNALS_PER_CYCLE})")
                break
        
        return filtered
    
    def process_signals(self, signals):
        """Save signals and send notifications"""
        for signal in signals:
            try:
                # Save to database
                signal_id = self.db.save_signal(signal.to_dict())
                logger.info(f"Saved signal #{signal_id}: {signal.symbol} {signal.direction}")
                
                # Send Telegram notification
                if self.telegram.send_signal(signal):
                    logger.info(f"Sent Telegram notification for {signal.symbol}")
                else:
                    logger.warning(f"Failed to send Telegram notification for {signal.symbol}")
                
                # Small delay between messages
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error processing signal for {signal.symbol}: {e}")
    
    def update_performance(self):
        """Update performance for open signals"""
        try:
            open_signals = self.db.get_open_signals()
            
            for signal in open_signals:
                # Get current price
                current_price = self.data_fetcher.get_current_price(signal['symbol'])
                
                if not current_price:
                    continue
                
                # Calculate duration
                from datetime import datetime
                created_at_str = signal.get('created_at')
                if created_at_str:
                    if isinstance(created_at_str, str):
                        created_at = datetime.fromisoformat(created_at_str)
                    else:
                        created_at = created_at_str
                    duration_hours = (datetime.now() - created_at).total_seconds() / 3600
                else:
                    duration_hours = 0
                
                # Check if target or stop loss hit
                if signal['direction'] == 'BUY':
                    if current_price >= signal['target']:
                        profit_pct = ((current_price - signal['entry_price']) / signal['entry_price']) * 100
                        self.db.update_signal_performance(signal['id'], current_price, win=True)
                        logger.info(f"Signal #{signal['id']} ({signal['symbol']}) HIT TARGET! 🎯")
                        
                        # Send Telegram notification
                        self.telegram.send_target_hit_notification(
                            signal_id=signal['id'],
                            symbol=signal['symbol'],
                            direction=signal['direction'],
                            entry_price=signal['entry_price'],
                            target_price=signal['target'],
                            current_price=current_price,
                            profit_pct=profit_pct,
                            duration_hours=duration_hours
                        )
                    elif current_price <= signal['stop_loss']:
                        loss_pct = ((signal['entry_price'] - current_price) / signal['entry_price']) * 100
                        self.db.update_signal_performance(signal['id'], current_price, win=False)
                        logger.info(f"Signal #{signal['id']} ({signal['symbol']}) hit stop loss ❌")
                        
                        # Send Telegram notification
                        self.telegram.send_stop_loss_notification(
                            signal_id=signal['id'],
                            symbol=signal['symbol'],
                            direction=signal['direction'],
                            entry_price=signal['entry_price'],
                            stop_loss=signal['stop_loss'],
                            current_price=current_price,
                            loss_pct=loss_pct,
                            duration_hours=duration_hours
                        )
                else:  # SELL
                    if current_price <= signal['target']:
                        profit_pct = ((signal['entry_price'] - current_price) / signal['entry_price']) * 100
                        self.db.update_signal_performance(signal['id'], current_price, win=True)
                        logger.info(f"Signal #{signal['id']} ({signal['symbol']}) HIT TARGET! 🎯")
                        
                        # Send Telegram notification
                        self.telegram.send_target_hit_notification(
                            signal_id=signal['id'],
                            symbol=signal['symbol'],
                            direction=signal['direction'],
                            entry_price=signal['entry_price'],
                            target_price=signal['target'],
                            current_price=current_price,
                            profit_pct=profit_pct,
                            duration_hours=duration_hours
                        )
                    elif current_price >= signal['stop_loss']:
                        loss_pct = ((current_price - signal['entry_price']) / signal['entry_price']) * 100
                        self.db.update_signal_performance(signal['id'], current_price, win=False)
                        logger.info(f"Signal #{signal['id']} ({signal['symbol']}) hit stop loss ❌")
                        
                        # Send Telegram notification
                        self.telegram.send_stop_loss_notification(
                            signal_id=signal['id'],
                            symbol=signal['symbol'],
                            direction=signal['direction'],
                            entry_price=signal['entry_price'],
                            stop_loss=signal['stop_loss'],
                            current_price=current_price,
                            loss_pct=loss_pct,
                            duration_hours=duration_hours
                        )
                
        except Exception as e:
            logger.error(f"Error updating performance: {e}")
    
    def run(self):
        """Main run loop"""
        logger.info("Starting Crypto Signal System...")
        
        # Send startup notification
        self.telegram.send_startup_message()
        
        self.running = True
        cycle_interval = config.CYCLE_INTERVAL_MINUTES * 60  # Convert to seconds
        
        logger.info(f"Running cycles every {config.CYCLE_INTERVAL_MINUTES} minutes")
        logger.info("Press Ctrl+C to stop\n")
        
        while self.running:
            try:
                self.run_cycle()
                
                # Wait for next cycle
                logger.info(f"\nWaiting {config.CYCLE_INTERVAL_MINUTES} minutes until next cycle...")
                time.sleep(cycle_interval)
                
            except KeyboardInterrupt:
                logger.warning("\nKeyboard interrupt received. Shutting down...")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                time.sleep(60)  # Wait 1 minute before retry
        
        logger.info("System stopped")


def main():
    """Entry point"""
    try:
        system = CryptoSignalSystem()
        system.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
