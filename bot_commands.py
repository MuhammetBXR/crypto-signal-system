"""
Telegram Bot Commands Handler
Interactive commands for system control and statistics
"""
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from loguru import logger
import config
from database import DatabaseManager

class BotCommands:
    """Handle Telegram bot commands"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        logger.info("Bot commands handler initialized")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        message = """
🚀 **CRYPTO SIGNAL SYSTEM**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Sistem aktif! 446 USDT paritesi izleniyor.

📋 **Komutlar:**
/stats - İstatistikler
/signals - Son sinyaller
/performance - Performans raporu
/help - Yardım

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💎 İyi tradelar!
"""
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        try:
            stats = self.db.get_performance_stats()
            
            message = f"""
📊 **PERFORMANS İSTATİSTİKLERİ**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔢 Toplam Sinyal: {stats.get('total_signals', 0)}
📈 Açık Pozisyon: {stats.get('open_signals', 0)}
✅ Kazanan: {stats.get('total_wins', 0)}
❌ Kaybeden: {stats.get('total_losses', 0)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 **PERFORMANS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 Win Rate: {stats.get('win_rate', 0):.1f}%
💰 Ortalama Kâr: +{stats.get('avg_profit', 0):.2f}%
📉 Ortalama Zarar: -{stats.get('avg_loss', 0):.2f}%
📊 Risk/Reward: 1:{stats.get('risk_reward', 0):.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in stats command: {e}")
            await update.message.reply_text("❌ İstatistikler yüklenirken hata oluştu.")
    
    async def signals_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /signals command"""
        try:
            # Get last 10 signals
            signals = self.db.get_recent_signals(limit=10)
            
            if not signals:
                await update.message.reply_text("📭 Henüz sinyal yok.")
                return
            
            message = "📊 **SON 10 SİNYAL**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            for sig in signals:
                emoji = "🟢" if sig['direction'] == "BUY" else "🔴"
                status_emoji = "✅" if sig['status'] == "win" else "❌" if sig['status'] == "loss" else "⏳"
                
                message += f"""{emoji} **{sig['symbol']}** {status_emoji}
└─ {sig['direction']} @ ${sig['entry_price']:.4f}
└─ Güç: {sig.get('confluence_score', 0)}/5
└─ {sig.get('created_at', 'N/A')}

"""
            
            message += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in signals command: {e}")
            await update.message.reply_text("❌ Sinyaller yüklenirken hata oluştu.")
    
    async def performance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /performance command"""
        try:
            stats = self.db.get_performance_stats()
            
            # Calculate additional metrics
            total_closed = stats.get('total_wins', 0) + stats.get('total_losses', 0)
            
            message = f"""
📈 **DETAYLI PERFORMANS RAPORU**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **GENEL DURUM**
• Toplam Sinyal: {stats.get('total_signals', 0)}
• Kapalı İşlem: {total_closed}
• Açık Pozisyon: {stats.get('open_signals', 0)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ **KAZANAN İŞLEMLER**
• Sayı: {stats.get('total_wins', 0)}
• Oran: {stats.get('win_rate', 0):.1f}%
• Avg Kâr: +{stats.get('avg_profit', 0):.2f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ **KAYBEDEN İŞLEMLER**
• Sayı: {stats.get('total_losses', 0)}
• Oran: {100 - stats.get('win_rate', 0):.1f}%
• Avg Zarar: -{stats.get('avg_loss', 0):.2f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 **DEĞERLENDİRME**
"""
            
            # Add performance evaluation
            win_rate = stats.get('win_rate', 0)
            if win_rate >= 60:
                message += "🔥 Mükemmel performans! Sistem çok iyi çalışıyor.\n"
            elif win_rate >= 50:
                message += "✅ İyi performans. Sistem başarılı.\n"
            elif win_rate >= 40:
                message += "⚠️ Orta performans. İyileştirme gerekebilir.\n"
            else:
                message += "❌ Düşük performans. Strateji gözden geçirilmeli.\n"
            
            message += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in performance command: {e}")
            await update.message.reply_text("❌ Performans raporu oluşturulurken hata oluştu.")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        message = """
📚 **KOMUT KILAVUZU**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Bilgi Komutları:**
/stats - Sistem istatistikleri
/signals - Son 10 sinyal listesi
/performance - Detaylı performans raporu

**Sistem Komutları:**
/start - Hoşgeldin mesajı
/help - Bu yardım mesajı

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 **NASIL KULLANILIR?**

1️⃣ Sinyal geldiğinde Telegram'a bildirim gelir
2️⃣ Chart linkine tıklayarak grafiği incele
3️⃣ Entry, TP ve SL seviyelerini not et
4️⃣ Binance Futures'ta pozisyon aç
5️⃣ TP veya SL olduğunda bildirim alırsın

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        await update.message.reply_text(message, parse_mode='Markdown')


def setup_bot_commands(bot_token: str, db: DatabaseManager):
    """Setup and run bot with commands"""
    application = Application.builder().token(bot_token).build()
    
    commands = BotCommands(db)
    
    # Register command handlers
    application.add_handler(CommandHandler("start", commands.start_command))
    application.add_handler(CommandHandler("stats", commands.stats_command))
    application.add_handler(CommandHandler("signals", commands.signals_command))
    application.add_handler(CommandHandler("performance", commands.performance_command))
    application.add_handler(CommandHandler("help", commands.help_command))
    
    logger.info("Bot commands registered")
    
    return application
