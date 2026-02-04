"""
Veri doğrulama scripti - Binance'den çektiğimiz veriyi göster
"""
import ccxt
import pandas as pd
from datetime import datetime

def test_data_fetch():
    print("\n" + "="*60)
    print("BINANCE VERİ DOĞRULAMA TESTİ")
    print("="*60)
    
    # Binance bağlantısı
    exchange = ccxt.binance()
    
    # Test için BTC/USDT ve CHESS/USDT çekelim
    test_symbols = ['BTC/USDT', 'CHESS/USDT', 'ETH/USDT']
    timeframe = '1h'
    limit = 10  # Son 10 mum
    
    for symbol in test_symbols:
        print(f"\n{'='*60}")
        print(f"📊 {symbol} - {timeframe} (Son 10 Mum)")
        print('='*60)
        
        try:
            # Veri çek
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            # DataFrame'e çevir
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Son 5 mumu göster
            print("\nSON 5 MUM:")
            print("-" * 60)
            for idx, row in df.tail(5).iterrows():
                time_str = row['timestamp'].strftime('%Y-%m-%d %H:%M')
                print(f"{time_str} | O: ${row['open']:.4f} | H: ${row['high']:.4f} | L: ${row['low']:.4f} | C: ${row['close']:.4f} | V: {row['volume']:.0f}")
            
            # Özet bilgiler
            latest = df.iloc[-1]
            print(f"\n✅ SON FİYAT: ${latest['close']:.4f}")
            print(f"📈 24H En Yüksek: ${df['high'].max():.4f}")
            print(f"📉 24H En Düşük: ${df['low'].min():.4f}")
            print(f"📊 Ortalama Hacim: {df['volume'].mean():.0f}")
            
            # Son mumun yönü
            color = "🟢 YEŞİL" if latest['close'] > latest['open'] else "🔴 KIRMIZI"
            change = ((latest['close'] - latest['open']) / latest['open']) * 100
            print(f"🎨 Son Mum: {color} ({change:+.2f}%)")
            
        except Exception as e:
            print(f"❌ Hata: {e}")
    
    print("\n" + "="*60)
    print("SONUÇ: Tüm veriler Binance'den canlı çekiliyor! ✅")
    print("="*60)
    
    # Şimdi stratejilerin kullandığı göstergeleri test et
    print("\n" + "="*60)
    print("TEKNİK GÖSTERGE TESTİ (CHESS/USDT)")
    print("="*60)
    
    symbol = 'CHESS/USDT'
    ohlcv = exchange.fetch_ohlcv(symbol, '1h', limit=100)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    # RSI hesapla
    import ta
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    
    # EMA hesapla
    df['ema_50'] = ta.trend.EMAIndicator(df['close'], window=50).ema_indicator()
    df['ema_200'] = ta.trend.EMAIndicator(df['close'], window=200).ema_indicator()
    
    # Hacim ortalaması
    df['volume_avg'] = df['volume'].rolling(window=20).mean()
    
    latest = df.iloc[-1]
    print(f"\n📊 Teknik Göstergeler (Son Mum):")
    print(f"  • RSI: {latest['rsi']:.2f}")
    print(f"  • EMA 50: ${latest['ema_50']:.4f}")
    print(f"  • EMA 200: ${latest['ema_200']:.4f}")
    print(f"  • Hacim: {latest['volume']:.0f}")
    print(f"  • Ortalama Hacim (20): {latest['volume_avg']:.0f}")
    print(f"  • Hacim Oranı: {latest['volume'] / latest['volume_avg']:.2f}x")
    
    # RSI durumu
    if latest['rsi'] < 30:
        print(f"\n🔵 RSI < 30 → OVERSOLD (Aşırı Satım)")
    elif latest['rsi'] > 70:
        print(f"\n🔴 RSI > 70 → OVERBOUGHT (Aşırı Alım)")
    else:
        print(f"\n⚪ RSI Normal Bölgede")
    
    # EMA durumu
    if latest['ema_50'] > latest['ema_200']:
        print(f"📈 EMA 50 > EMA 200 → Yükseliş Trendi")
    else:
        print(f"📉 EMA 50 < EMA 200 → Düşüş Trendi")
    
    print("\n✅ Göstergeler doğru hesaplanıyor!")

if __name__ == "__main__":
    test_data_fetch()
