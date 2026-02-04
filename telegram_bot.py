"""
Telegram Bot for sending signal notifications
"""
import asyncio
from typing import Optional
from telegram import Bot
from telegram.error import TelegramError
from loguru import logger
import config


class TelegramNotifier:
    """Sends notifications to Telegram"""
    
    def __init__(self):
        self.bot_token = config.TELEGRAM_BOT_TOKEN
        self.chat_id = config.TELEGRAM_CHAT_ID
        self.bot = None
        
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram credentials not configured. Notifications disabled.")
            self.enabled = False
        else:
            self.bot = Bot(token=self.bot_token)
            self.enabled = True
            logger.info("Telegram notifier initialized")
    
    def format_signal_message(self, signal) -> str:
        """Format signal as simplified Telegram message"""
        # Emoji based on direction
        emoji = "🟢" if signal.direction == "BUY" else "🔴"
        action_tr = "YÜKSELIŞ SİNYALİ" if signal.direction == "BUY" else "DÜŞÜŞ SİNYALİ"
        
        # Calculate profit/loss percentages
        if signal.direction == "BUY":
            profit_pct = ((signal.target - signal.price) / signal.price) * 100
            loss_pct = ((signal.price - signal.stop_loss) / signal.price) * 100
        else:
            profit_pct = ((signal.price - signal.target) / signal.price) * 100
            loss_pct = ((signal.stop_loss - signal.price) / signal.price) * 100
        
        # Confluence strength
        if signal.confluence_score >= 4:
            strength = "ÇOK GÜÇLÜ"
            stars = "⭐⭐⭐⭐"
        elif signal.confluence_score >= 3:
            strength = "GÜÇLÜ"
            stars = "⭐⭐⭐"
        else:
            strength = "ORTA GÜÇLÜ"
            stars = "⭐⭐"
        
        message = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{emoji} {action_tr} ({strength})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💎 COİN: {signal.symbol}
💰 ŞU ANKİ FİYAT: ${signal.price:,.4f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 FİYAT SEVİYELERİ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🟢 GİRİŞ FİYATI: ${signal.price:,.4f}
🎯 KÂR AL (HEDEF): ${signal.target:,.4f}
🛡️ ZARAR KES (STOP): ${signal.stop_loss:,.4f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 SİNYAL GÜCÜ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ Confluence Skoru: {signal.confluence_score}/5 {stars}
   └─ {signal.confluence_score} strateji aynı yönde sinyal veriyor
   └─ {strength}! ({"daha güvenilir" if signal.confluence_score >= 3 else "dikkatli ol"})

⭐ Güven Seviyesi: {signal.confidence*100:.0f}%

⏰ Zaman Dilimleri: {signal.timeframe}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 NEDEN BU SİNYALİ VERDİ?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        # Add strategy details
        for i, (strategy, reason) in enumerate(zip(signal.strategies, signal.reasons), 1):
            # Parse reason to make it more readable
            reason_text = self._format_reason(reason, signal.direction)
            message += f"📌 Strateji #{i}: {strategy}\n{reason_text}\n\n"
        
        
        # Add TradingView chart link
        from chart_generator import ChartGenerator
        chart_gen = ChartGenerator()
        chart_link = chart_gen.get_tradingview_chart_link(signal.symbol)
        
        message += f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Chart: {chart_link}
📱 Sinyali takip et: #{''.join(signal.symbol.split('/'))}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        return message
    
    def _format_reason(self, reason: str, direction: str) -> str:
        """Format strategy reason to be more readable"""
        # Extract key info from reason
        if "Volume Spike" in reason:
            parts = reason.split("(")
            if len(parts) > 1:
                details = parts[1].rstrip(")")
                vol_mult = details.split(",")[0] if "," in details else details
                trend = "Büyük oyuncular AL yapıyor" if direction == "BUY" else "Büyük oyuncular SAT yapıyor"
                return f"   ├─ Hacim normal hacmin {vol_mult} arttı! 💥\n   └─ → {trend}"
        
        elif "Breakdown" in reason or "Breakout" in reason:
            # Support/Resistance breakout
            level = reason.split("at")[-1].split("(")[0].strip() if "at" in reason else ""
            action = "KIRILDI" if "Breakout" in reason else "KIRILDI"
            direction_text = "yukarı" if direction == "BUY" else "aşağı"
            continuation = "Yükseliş" if direction == "BUY" else "Düşüş"
            return f"   ├─ {level} seviyesi {direction_text} {action}! 🚀\n   └─ → {continuation} devam edebilir"
        
        elif "Cross" in reason:
            cross_type = "Golden Cross" if "Golden" in reason else "Death Cross"
            trend = "Yükseliş" if direction == "BUY" else "Düşüş"
            return f"   ├─ EMA 50 {'yukarı' if direction == 'BUY' else 'aşağı'} EMA 200'ü KESTİ! 📈\n   └─ → {trend} trendi başlıyor"
        
        elif "Divergence" in reason:
            div_type = "Bullish" if direction == "BUY" else "Bearish"
            return f"   ├─ Fiyat ile RSI arasında uyumsuzluk! 🔄\n   └─ → Trend değişimi olabilir ({div_type})"
        
        elif "Channel" in reason:
            return f"   ├─ Kanal kırılması algılandı! 📈\n   └─ → Trend değişimi başladı"
        
        # Default formatting
        return f"   └─ {reason}"
    
    async def send_message_async(self, message: str) -> bool:
        """Send message asynchronously"""
        if not self.enabled:
            logger.warning("Telegram notifications disabled")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            return True
        except TelegramError as e:
            logger.error(f"Telegram error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram message: {e}")
            return False
    
    def send_message(self, message: str) -> bool:
        """Send message synchronously (wrapper for async)"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If event loop is already running, create a new one
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                result = new_loop.run_until_complete(self.send_message_async(message))
                new_loop.close()
                return result
            else:
                return loop.run_until_complete(self.send_message_async(message))
        except Exception as e:
            logger.error(f"Error in send_message wrapper: {e}")
            return False
    
    def send_signal(self, signal) -> bool:
        """Send a signal notification"""
        message = self.format_signal_message(signal)
        return self.send_message(message)
    
    def send_stats(self, stats: dict) -> bool:
        """Send performance statistics"""
        message = f"""
📊 PERFORMANS İSTATİSTİKLERİ

🔢 Toplam Sinyal: {stats['total_signals']}
📈 Açık Pozisyon: {stats['open_signals']}
✅ Kazanan: {stats['total_wins']}
❌ Kaybeden: {stats['total_losses']}

🎯 Kazanma Oranı: {stats['win_rate']:.1f}%
💰 Ortalama Kâr: {stats['avg_profit']:.2f}%
📉 Ortalama Zarar: {stats['avg_loss']:.2f}%
"""
        return self.send_message(message)
    
    def send_target_hit_notification(self, signal_id: int, symbol: str, direction: str, 
                                     entry_price: float, target_price: float, 
                                     current_price: float, profit_pct: float,
                                     duration_hours: float) -> bool:
        """Send notification when target is hit"""
        emoji = "🎉" if direction == "BUY" else "🎉"
        trade_type = "LONG (Alış)" if direction == "BUY" else "SHORT (Satış)"
        
        # Calculate duration string
        if duration_hours < 1:
            duration_str = f"{int(duration_hours * 60)} dakika"
        else:
            hours = int(duration_hours)
            minutes = int((duration_hours - hours) * 60)
            duration_str = f"{hours} saat {minutes} dakika" if minutes > 0 else f"{hours} saat"
        
        message = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{emoji} HEDEF ULAŞILDI! KÂR ALDI! {emoji}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💎 COİN: {symbol}
📊 SİNYAL: #{signal_id} ({trade_type})

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 KAZANÇ DETAYLARI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🟢 Giriş Fiyatı: ${entry_price:,.4f}
🎯 Hedef Fiyat: ${target_price:,.4f} ✅ ULAŞTI!
💵 Mevcut Fiyat: ${current_price:,.4f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 PERFORMANS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ KÂR: +%{profit_pct:.1f}
⏱️ Süre: {duration_str}
🎮 İşlem: {trade_type}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎊 TEBRİKLER! Başarılı işlem!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

#{''.join(symbol.split('/'))} #WIN
"""
        return self.send_message(message)
    
    def send_stop_loss_notification(self, signal_id: int, symbol: str, direction: str,
                                    entry_price: float, stop_loss: float,
                                    current_price: float, loss_pct: float,
                                    duration_hours: float) -> bool:
        """Send notification when stop loss is hit"""
        trade_type = "LONG (Alış)" if direction == "BUY" else "SHORT (Satış)"
        
        # Calculate duration string
        if duration_hours < 1:
            duration_str = f"{int(duration_hours * 60)} dakika"
        else:
            hours = int(duration_hours)
            minutes = int((duration_hours - hours) * 60)
            duration_str = f"{hours} saat {minutes} dakika" if minutes > 0 else f"{hours} saat"
        
        message = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ STOP LOSS! ZARAR KESİLDİ ⚠️
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💎 COİN: {symbol}
📊 SİNYAL: #{signal_id} ({trade_type})

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💔 ZARAR DETAYLARI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🟢 Giriş Fiyatı: ${entry_price:,.4f}
🛡️ Stop Loss: ${stop_loss:,.4f} ❌ TETİKLENDİ!
💵 Mevcut Fiyat: ${current_price:,.4f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📉 PERFORMANS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ ZARAR: -%{abs(loss_pct):.1f}
⏱️ Süre: {duration_str}
🎮 İşlem: {trade_type}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 HATIRLATMA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Stop loss sistemi çalışıyor! 
✅ Zararını küçük tuttun - doğru yaptın!
📊 Her işlem kazanmaz, bu normal.
🎯 Bir sonraki sinyali bekle!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#{''.join(symbol.split('/'))} #LOSS
"""
        return self.send_message(message)
    
    def send_startup_message(self) -> bool:
        """Send system startup notification"""
        message = """
🚀 CRYPTO SIGNAL SYSTEM BAŞLATILDI

Sistem çalışmaya başladı ve tüm USDT paritelerini izliyor.

⚙️ Aktif Stratejiler:
  ✅ Channel Breakout
  ✅ RSI Divergence
  ✅ Volume Spike
  ✅ EMA Cross (50/200)
  ✅ Support/Resistance Breakout

📈 İyi tradelar! 💎
"""
        return self.send_message(message)
    
    def send_error_message(self, error: str) -> bool:
        """Send error notification"""
        message = f"⚠️ HATA\n\n{error}"
        return self.send_message(message)
