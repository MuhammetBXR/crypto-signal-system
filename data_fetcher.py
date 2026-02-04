"""
Data fetcher for Binance USDT pairs using CCXT
"""
import ccxt
import pandas as pd
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger
import time
import config


class DataFetcher:
    """Fetches OHLCV data from Binance"""
    
    def __init__(self):
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        self.usdt_pairs_cache = None
        self.cache_timestamp = 0
        self.cache_ttl = 3600  # Cache pairs for 1 hour
    
    def get_usdt_pairs(self, force_refresh: bool = False) -> List[str]:
        """Get all USDT trading pairs"""
        current_time = time.time()
        
        # Return cached if available and not expired
        if not force_refresh and self.usdt_pairs_cache and (current_time - self.cache_timestamp < self.cache_ttl):
            return self.usdt_pairs_cache
        
        try:
            logger.info("Fetching USDT pairs from Binance...")
            markets = self.exchange.load_markets()
            
            # Filter for USDT pairs and active markets
            usdt_pairs = [
                symbol for symbol, market in markets.items()
                if market['quote'] == config.BASE_CURRENCY
                and market['active']
                and market['spot']
            ]
            
            # Cache the results
            self.usdt_pairs_cache = sorted(usdt_pairs)
            self.cache_timestamp = current_time
            
            logger.info(f"Found {len(usdt_pairs)} USDT pairs")
            return self.usdt_pairs_cache
            
        except Exception as e:
            logger.error(f"Error fetching USDT pairs: {e}")
            # Return cached if error occurs
            return self.usdt_pairs_cache or []
    
    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int = None
    ) -> Optional[pd.DataFrame]:
        """Fetch OHLCV data for a single symbol and timeframe"""
        limit = limit or config.OHLCV_LIMIT
        
        try:
            # Fetch from exchange
            ohlcv = self.exchange.fetch_ohlcv(
                symbol,
                timeframe=timeframe,
                limit=limit
            )
            
            if not ohlcv:
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Ensure numeric types
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df
            
        except ccxt.NetworkError as e:
            logger.warning(f"Network error fetching {symbol} {timeframe}: {e}")
            return None
        except ccxt.ExchangeError as e:
            logger.warning(f"Exchange error fetching {symbol} {timeframe}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {symbol} {timeframe}: {e}")
            return None
    
    def fetch_symbol_data(self, symbol: str, timeframes: List[str] = None) -> Dict[str, pd.DataFrame]:
        """Fetch data for a single symbol across multiple timeframes"""
        timeframes = timeframes or config.TIMEFRAMES
        result = {}
        
        for tf in timeframes:
            df = self.fetch_ohlcv(symbol, tf)
            if df is not None and not df.empty:
                result[tf] = df
            time.sleep(config.RATE_LIMIT_DELAY)  # Rate limiting
        
        return result
    
    def fetch_all_pairs_data(
        self,
        pairs: List[str] = None,
        timeframes: List[str] = None,
        max_workers: int = None
    ) -> Dict[str, Dict[str, pd.DataFrame]]:
        """Fetch data for all pairs concurrently"""
        pairs = pairs or self.get_usdt_pairs()
        timeframes = timeframes or config.TIMEFRAMES
        max_workers = max_workers or config.MAX_CONCURRENT_REQUESTS
        
        all_data = {}
        total_pairs = len(pairs)
        
        logger.info(f"Fetching data for {total_pairs} pairs across {len(timeframes)} timeframes...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_symbol = {
                executor.submit(self.fetch_symbol_data, symbol, timeframes): symbol
                for symbol in pairs
            }
            
            # Process completed tasks
            completed = 0
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                completed += 1
                
                try:
                    data = future.result()
                    if data:  # Only add if we got data
                        all_data[symbol] = data
                    
                    if completed % 50 == 0:
                        logger.info(f"Progress: {completed}/{total_pairs} pairs processed")
                        
                except Exception as e:
                    logger.error(f"Error processing {symbol}: {e}")
        
        logger.info(f"Successfully fetched data for {len(all_data)}/{total_pairs} pairs")
        return all_data
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current ticker price for a symbol"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None
