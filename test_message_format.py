"""
Telegram Mesaj Test Çıktısı
"""

# ============================================================
# ŞU ANKİ MESAJ FORMATI (KÖTÜ)
# ============================================================

current_format = """
🔴 ORTA SAT SİNYALİ

💎 Coin: MASK/USDT
💰 Fiyat: $0.5025
⏰ Timeframe: 15m, 1h
📊 Stratejiler (2):
  ✅ VolumeSpikeStrategy (15m)
  ✅ VolumeSpikeStrategy (1h)

🎯 Hedef: $0.4874 (+3.0%)
🛡️ Stop Loss: $0.5100 (-1.5%)
⭐ Confidence: 70%

📝 Detaylar:
1. Bearish Volume Spike (5.2x avg, -2.5%)
2. Bearish Volume Spike (4.5x avg, -2.7%)

#MASKUSDT
"""

# ============================================================
# YENİ MESAJ FORMATI (İYİ, AÇIKLAYICI)
# ============================================================

new_format = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 DÜŞÜŞ SİNYALİ (ORTA GÜÇLÜ)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💎 COİN: MASK/USDT
💰 ŞU ANKİ FİYAT: $0.5025

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 NE YAPMALISIN?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎮 İŞLEM: SHORT (Satış) pozisyonu aç
📊 BORSA: Binance Futures
💵 POZİSYON: Sermayenin %1-2'si (küçük başla!)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 FİYAT SEVİYELERİ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🟢 GİRİŞ FİYATI: $0.5025
   └─ Şu anki fiyattan SHORT aç

🎯 KÂR AL (HEDEF): $0.4874
   └─ +%3.0 kâr (yaklaşık $15 / 500 USDT pozisyon)
   └─ Buraya ulaşınca pozisyonu kapat

🛡️ ZARAR KES (STOP): $0.5100
   └─ -%1.5 zarar (yaklaşık $7.5 / 500 USDT pozisyon)
   └─ MUTLAKA koy! Buraya gelirse otomatik çık

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 SİNYAL GÜCÜ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ Confluence Skoru: 2/5
   └─ 2 strateji aynı yönde sinyal veriyor
   └─ ORTA GÜÇLÜ (dikkatli ol, küçük pozisyon)

⭐ Güven Seviyesi: 70%
   └─ Sistemin bu sinyale güveni

⏰ Zaman Dilimleri: 15m, 1h
   └─ 2 farklı timeframe'de sinyal var (daha güçlü!)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 NEDEN BU SİNYALİ VERDİ?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 Strateji #1: Hacim Patlaması (15m)
   ├─ Hacim normal hacmin 5.2 KATI arttı! 💥
   ├─ Fiyat -%2.5 düştü
   └─ → Büyük oyuncular SAT yapıyor

📌 Strateji #2: Hacim Patlaması (1h)
   ├─ Hacim normal hacmin 4.5 KATI arttı! 💥
   ├─ Fiyat -%2.7 düştü
   └─ → Satış baskısı devam ediyor

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ ÖNEMLİ HATIRLATMALAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Stop Loss'u MUTLAKA koy
✅ Küçük pozisyon aç (%1-2)
✅ Hedef'e yaklaşınca yarısını sat
❌ Tüm parayı yükleme!
❌ Stop loss'u kaydırma!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 Sinyali takip et: #MASKUSDT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ============================================================
# AL SİNYALİ ÖRNEĞİ
# ============================================================

buy_signal_format = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟢 YÜKSELIŞ SİNYALİ (GÜÇLÜ)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💎 COİN: BTC/USDT
💰 ŞU ANKİ FİYAT: $73,250.00

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 NE YAPMALISIN?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎮 İŞLEM: LONG (Alış) pozisyonu aç
📊 BORSA: Binance Futures
💵 POZİSYON: Sermayenin %2-3'ü (3 strateji hemfikir!)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 FİYAT SEVİYELERİ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🟢 GİRİŞ FİYATI: $73,250
   └─ Şu anki fiyattan LONG aç

🎯 KÂR AL (HEDEF): $75,450
   └─ +%3.0 kâr (yaklaşık $30 / 1000 USDT pozisyon)
   └─ Buraya ulaşınca pozisyonu kapat

🛡️ ZARAR KES (STOP): $72,150
   └─ -%1.5 zarar (yaklaşık $15 / 1000 USDT pozisyon)
   └─ MUTLAKA koy! Buraya gelirse otomatik çık

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 SİNYAL GÜCÜ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ Confluence Skoru: 3/5 ⭐⭐⭐
   └─ 3 strateji aynı yönde sinyal veriyor
   └─ GÜÇLÜ SİNYAL! (daha güvenilir)

⭐ Güven Seviyesi: 85%
   └─ Sistemin bu sinyale güveni yüksek

⏰ Zaman Dilimleri: 1h, 4h
   └─ 2 farklı timeframe'de sinyal var (çok güçlü!)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 NEDEN BU SİNYALİ VERDİ?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 Strateji #1: Destek/Direnç Kırılması (1h)
   ├─ $72,800 direnç seviyesi yukarı KIRILDI! 🚀
   ├─ Kırılma sırasında hacim 2.8x arttı
   └─ → Yükseliş devam edebilir

📌 Strateji #2: Hacim Patlaması (1h)
   ├─ Hacim normal hacmin 3.1 KATI arttı! 💥
   ├─ Fiyat +%2.1 yükseldi (yeşil mum)
   └─ → Büyük oyuncular AL yapıyor

📌 Strateji #3: Golden Cross (4h)
   ├─ EMA 50 yukarı EMA 200'ü KESTİ! 📈
   ├─ Trend gücü (ADX): 28 (güçlü trend)
   └─ → Uzun vadeli yükseliş trendi başlıyor

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ ÖNEMLİ HATIRLATMALAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Stop Loss'u MUTLAKA koy
✅ Pozisyon büyüklüğü: %2-3 (güçlü sinyal)
✅ Hedef'e yaklaşınca yarısını sat
❌ Tüm parayı yükleme!
❌ Stop loss'u kaydırma!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 Sinyali takip et: #BTCUSDT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

print("="*60)
print("ESKİ MESAJ FORMATI")
print("="*60)
print(current_format)

print("\n" + "="*60)
print("YENİ MESAJ FORMATI - SAT SİNYALİ ÖRNEĞİ")
print("="*60)
print(new_format)

print("\n" + "="*60)
print("YENİ MESAJ FORMATI - AL SİNYALİ ÖRNEĞİ")
print("="*60)
print(buy_signal_format)

print("\n" + "="*60)
print("FARKLAR:")
print("="*60)
print("""
YENİ FORMATTA:
✅ "Ne yapmalısın?" bölümü var - NET talimat
✅ İşlem tipi açık: LONG/SHORT
✅ Pozisyon büyüklüğü önerisi var
✅ Fiyat seviyeleri daha detaylı açıklanmış
✅ Her seviyenin yanında KAÇ PARA kazanırsın/kaybedersin yazıyor
✅ Confluence skoru görsel (⭐⭐⭐)
✅ Strateji açıklamaları BASIT ve ANLAŞILIR
✅ "Neden" sorusunu cevaplıyor (hacim 5.2x arttı vs.)
✅ Önemli hatırlatmalar var

ESKİ FORMATTA:
❌ Sadece veri var, ne yapacağım yok
❌ "SELL" ne demek bilmeyebilirsin
❌ Detaylar teknik (Bearish Volume Spike...)
❌ Kaç para kazanacağın belirsiz
""")
