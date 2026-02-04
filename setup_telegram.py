"""
Telegram Setup Helper - Automatically get your Chat ID
"""
import os
import sys
from telegram import Bot
from telegram.error import TelegramError
import asyncio

def update_env_file(chat_id: str):
    """Update .env file with chat ID"""
    env_path = ".env"
    
    # Read current .env
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Update TELEGRAM_CHAT_ID line
    new_lines = []
    found = False
    for line in lines:
        if line.startswith('TELEGRAM_CHAT_ID='):
            new_lines.append(f'TELEGRAM_CHAT_ID={chat_id}\n')
            found = True
        else:
            new_lines.append(line)
    
    # If not found, add it
    if not found:
        new_lines.append(f'TELEGRAM_CHAT_ID={chat_id}\n')
    
    # Write back
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

async def get_chat_id(bot_token: str):
    """Get chat ID from latest message"""
    try:
        bot = Bot(token=bot_token)
        
        print("\n" + "="*60)
        print("📱 TELEGRAM BOT SETUP")
        print("="*60)
        print(f"\n✅ Bot bağlantısı başarılı!")
        
        # Get bot info
        me = await bot.get_me()
        print(f"\n🤖 Bot Bilgileri:")
        print(f"   İsim: {me.first_name}")
        print(f"   Username: @{me.username}")
        
        print(f"\n📩 Şimdi Telegram'da @{me.username} bot'una bir mesaj gönder!")
        print("   (Herhangi bir şey yazabilirsin, örnek: 'Merhaba')")
        print("\nBekleniyor", end="", flush=True)
        
        # Poll for messages
        for i in range(60):  # 60 seconds timeout
            await asyncio.sleep(1)
            print(".", end="", flush=True)
            
            try:
                updates = await bot.get_updates()
                
                if updates:
                    # Get the latest message
                    latest_update = updates[-1]
                    
                    if latest_update.message:
                        chat_id = latest_update.message.chat.id
                        user = latest_update.message.from_user
                        
                        print("\n\n✅ MESAJ ALINDI!")
                        print(f"\n👤 Kullanıcı: {user.first_name}")
                        print(f"💬 Chat ID: {chat_id}")
                        
                        # Update .env file
                        update_env_file(str(chat_id))
                        
                        print(f"\n✅ .env dosyası güncellendi!")
                        print(f"   TELEGRAM_CHAT_ID={chat_id}")
                        
                        # Send test message
                        await bot.send_message(
                            chat_id=chat_id,
                            text="🎉 Bağlantı başarılı!\n\nCrypto Signal System hazır. Artık `python main.py` ile sistemi başlatabilirsin!"
                        )
                        
                        print(f"\n✅ Test mesajı gönderildi (Telegram'ı kontrol et)")
                        print("\n" + "="*60)
                        print("🎉 KURULUM TAMAMLANDI!")
                        print("="*60)
                        print("\nŞimdi sistemi başlatabilirsin:")
                        print("  python main.py")
                        
                        return chat_id
                        
            except Exception as e:
                pass  # Continue polling
        
        print("\n\n❌ Zaman aşımı! 60 saniye içinde mesaj gelmedi.")
        print(f"\nTekrar dene: Bot'a (@{me.username}) mesaj atmayı unutma!")
        return None
        
    except TelegramError as e:
        print(f"\n❌ Telegram hatası: {e}")
        print("\nBot token'ını kontrol et!")
        return None
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        return None

def main():
    print("\n" + "="*60)
    print("🚀 TELEGRAM SETUP - CHAT ID OTOMATIK BULMA")
    print("="*60)
    
    # Check if .env exists
    if not os.path.exists(".env"):
        print("\n❌ .env dosyası bulunamadı!")
        print("Önce .env.example dosyasını .env olarak kopyala.")
        return
    
    # Read bot token from .env or ask
    from dotenv import load_dotenv
    load_dotenv()
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    
    if not bot_token:
        print("\nBot token bulunamadı (.env dosyasında).")
        print("\nBot token'ını buraya yapıştır:")
        bot_token = input("Token: ").strip()
        
        if not bot_token:
            print("\n❌ Token boş olamaz!")
            return
        
        # Update .env with token
        with open(".env", 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        new_lines = []
        found = False
        for line in lines:
            if line.startswith('TELEGRAM_BOT_TOKEN='):
                new_lines.append(f'TELEGRAM_BOT_TOKEN={bot_token}\n')
                found = True
            else:
                new_lines.append(line)
        
        if not found:
            new_lines.insert(0, f'TELEGRAM_BOT_TOKEN={bot_token}\n')
        
        with open(".env", 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print("✅ Token .env dosyasına kaydedildi")
    
    # Get chat ID
    try:
        chat_id = asyncio.run(get_chat_id(bot_token))
        
        if chat_id:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ İşlem iptal edildi.")
        sys.exit(1)

if __name__ == "__main__":
    main()
