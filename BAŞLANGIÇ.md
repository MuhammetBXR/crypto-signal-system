# HIZLI BAŞLANGIÇ REHBERİ

## Adım 1: Python Kütüphanelerini Kur

```powershell
pip install -r requirements.txt
```

Bu işlem 2-3 dakika sürebilir. Tüm kütüphaneler yüklenecek.

## Adım 2: Telegram Bot Oluştur ve Kurulum Yap

### 2.1. Bot Oluştur
1. **Telegram'ı aç** ve **@BotFather**'ı ara
2. `/newbot` komutunu gönder
3. Bot için bir **isim** seç (örnek: "Crypto Signals Bot")
4. Bot için bir **username** seç (örnek: "mycryptobotxyz_bot" - mutlaka **_bot** ile bitmeli)
5. BotFather sana bir **token** verecek. Bunu kopyala! (Örnek: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2.2. Otomatik Kurulum (KOLAY YOL) ⭐

```powershell
python setup_telegram.py
```

Script senden:
1. Bot token'ını isteyecek (yapıştır)
2. Bot'a mesaj atmanı isteyecek
3. Mesajı alınca **otomatik** Chat ID'ni bulup `.env`'ye kaydedecek
4. Telegram'a test mesajı gönderecek

**Hepsi bu kadar!** 🎉

---

## Adım 3: Sistemi Test Et

```powershell
python test_system.py
```

Bu komut:
- ✅ Tüm kütüphaneleri kontrol edecek
- ✅ Binance bağlantısını test edecek
- ✅ Telegram bot'una test mesajı gönderecek
- ✅ Database'i oluşturacak

Telegram'da test mesajını görürsen **HER ŞEY HAZIR!** 🎉

## Adım 6: Sistemi Çalıştır

```powershell
python main.py
```

Sistem:
- Her 5 dakikada bir çalışacak
- Binance'deki tüm USDT paritelerini tarayacak
- Güçlü sinyalleri Telegram'a gönderecek
- Durdurmak için **Ctrl+C** yapman yeterli

---

## ⚠️ Önemli Notlar

- **İlk cycle 3-5 dakika sürebilir** (300+ coin analiz ediliyor)
- **Her zaman sinyal gelmeyebilir** - piyasa sakinse sinyal az olur
- **Win rate %100 değil** - risk yönetimi yap, stop loss kullan
- **Bilgisayar kapalıyken çalışmaz** - VPS kullanmak istersen sonra konuşalım

---

## 📊 Performans İstatistikleri

Telegram'da bot'a şu komutları gönderebilirsin:

- `/start` - Bot'u başlat
- `/stats` - Genel performans istatistikleri

(Not: Bu komutlar henüz aktif değil, V2'de eklenecek)

---

## ❓ Sorun mu var?

### "ModuleNotFoundError" hatası alıyorum
```powershell
pip install -r requirements.txt --upgrade
```

### Telegram'a mesaj gelmiyor
- `.env` dosyasındaki token ve chat ID'yi kontrol et
- Bot'a bir mesaj gönderdiğinden emin ol
- `test_system.py`'yi tekrar çalıştır

### "API rate limit" hatası
- Normal, Binance sınırlarını aşmışsın
- Sistem otomatik bekler ve devam eder

### Çok az sinyal geliyor
- `config.py`'de `MIN_CONFLUENCE_SCORE = 1` yap (daha çok sinyal ama kalite düşer)

---

## 🚀 İyi Tradelar!
