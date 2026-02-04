"""
Chart Screenshot Generator
Generates TradingView chart screenshots for signals
"""
import requests
from datetime import datetime
from loguru import logger
import config

class ChartGenerator:
    """Generate chart screenshots for signals"""
    
    def __init__(self):
        self.chart_service = "https://api.chart-img.com/v2/tradingview/advanced-chart"
        logger.info("Chart generator initialized")
    
    def generate_chart_url(self, symbol: str, timeframe: str, width: int = 800, height: int = 600) -> str:
        """
        Generate TradingView chart image URL
        
        Args:
            symbol: Trading pair (e.g., BTC/USDT)
            timeframe: Timeframe (15m, 1h, 4h, 1d)
            width: Image width
            height: Image height
            
        Returns:
            Chart image URL
        """
        # Convert symbol format (BTC/USDT -> BTCUSDT)
        binance_symbol = symbol.replace("/", "")
        
        # Convert timeframe to TradingView format
        tv_timeframe = self._convert_timeframe(timeframe)
        
        # Build chart URL
        chart_url = f"https://s3.tradingview.com/snapshots/{binance_symbol.lower()}_snapshot.png"
        
        # Alternative: Use external chart service
        params = {
            "symbol": f"BINANCE:{binance_symbol}",
            "interval": tv_timeframe,
            "theme": "dark",
            "width": width,
            "height": height,
            "studies": "RSI@tv-basicstudies,MACD@tv-basicstudies",
            "timezone": "exchange"
        }
        
        # Build query string
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        api_url = f"{self.chart_service}?{query}"
        
        logger.debug(f"Generated chart URL for {symbol}: {api_url}")
        return api_url
    
    def _convert_timeframe(self, timeframe: str) -> str:
        """Convert timeframe to TradingView format"""
        mapping = {
            "1m": "1",
            "5m": "5",
            "15m": "15",
            "30m": "30",
            "1h": "60",
            "2h": "120",
            "4h": "240",
            "1d": "D",
            "1w": "W"
        }
        return mapping.get(timeframe, "60")
    
    def download_chart(self, symbol: str, timeframe: str, save_path: str = None) -> str:
        """
        Download chart image
        
        Args:
            symbol: Trading pair
            timeframe: Timeframe
            save_path: Path to save image (optional)
            
        Returns:
            Path to saved image
        """
        try:
            chart_url = self.generate_chart_url(symbol, timeframe)
            
            # Download image
            response = requests.get(chart_url, timeout=10)
            response.raise_for_status()
            
            # Generate filename if not provided
            if not save_path:
                binance_symbol = symbol.replace("/", "")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = f"temp_charts/{binance_symbol}_{timeframe}_{timestamp}.png"
            
            # Save image
            import os
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, "wb") as f:
                f.write(response.content)
            
            logger.info(f"Chart saved: {save_path}")
            return save_path
            
        except Exception as e:
            logger.error(f"Error downloading chart for {symbol}: {e}")
            return None
    
    def get_tradingview_chart_link(self, symbol: str) -> str:
        """
        Generate TradingView web link
        
        Args:
            symbol: Trading pair
            
        Returns:
            TradingView chart URL
        """
        binance_symbol = symbol.replace("/", "")
        return f"https://www.tradingview.com/chart/?symbol=BINANCE:{binance_symbol}"
