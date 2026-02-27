"""
Volume Confirmation Stratejisi
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tek başına sinyal VERMEZ. Diğer sinyallere ek skor katar.
Ancak şu koşullarda bağımsız sinyal de üretebilir:

BUY  → Büyük hacimli güçlü yeşil mum + fiyat lokal diplerde
SHORT→ Büyük hacimli güçlü kırmızı mum + fiyat lokal tepelerde

Hacim onayı olmayan sinyaller daha az güvenilirdir.
"""
import pandas as pd
import numpy as np
from typing import Optional

from .base_strategy import BaseStrategy, Signal
import config


class VolumeConfirmStrategy(BaseStrategy):

    def analyze(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Optional[Signal]:
        period = config.VOL_MA_PERIOD
        if len(df) < period + 5:
            return None

        vol_ma = df["volume"].rolling(period).mean()
        atr_series = self.calc_atr(df, config.ATR_PERIOD)

        cur = df.iloc[-1]
        prev = df.iloc[-2]
        cur_price = float(cur["close"])
        cur_vol = float(cur["volume"])
        avg_vol = float(vol_ma.iloc[-1])
        atr = float(atr_series.iloc[-1])

        if avg_vol == 0 or pd.isna(avg_vol) or atr == 0:
            return None

        vol_ratio = cur_vol / avg_vol

        # Hacim spike değilse çık
        if vol_ratio < config.VOL_SPIKE_MULTIPLIER:
            return None

        # Mum gövdesi (doji filtresi)
        body = abs(cur_price - float(cur["open"]))
        candle_range = float(cur["high"]) - float(cur["low"])
        if candle_range == 0:
            return None
        body_ratio = body / candle_range
        if body_ratio < 0.4:   # Doji veya belirsiz mum → sinyal üretme
            return None

        price_change_pct = (cur_price - float(cur["open"])) / float(cur["open"])

        # Fiyatın son 20 mumda nerede olduğunu kontrol et
        recent_close = df["close"].tail(20)
        percentile_rank = (recent_close < cur_price).mean()  # 0=dip, 1=tepe

        # ── BUY: Güçlü yükseliş mumu + fiyat dip bölgede ──────────
        if (cur_price > float(cur["open"]) and
                price_change_pct >= 0.005 and   # en az %0.5 yükseliş
                percentile_rank <= 0.35):        # son 20 mumun alt %35'inde

            score = min(1.0, 0.55 + min(vol_ratio / 10, 0.25) + (0.35 - percentile_rank) * 0.5)

            target, stop_loss = self.calc_tp_sl(cur_price, "BUY", atr)

            return Signal(
                symbol=symbol,
                timeframe=timeframe,
                strategy=self.name,
                direction="BUY",
                price=cur_price,
                target=target,
                stop_loss=stop_loss,
                score=round(score, 2),
                reason=(
                    f"Hacim Onaylı Dip Alımı | "
                    f"Vol={vol_ratio:.1f}x | "
                    f"+{price_change_pct*100:.2f}% | "
                    f"Fiyat rank=%{percentile_rank*100:.0f}"
                ),
            )

        # ── SHORT: Güçlü düşüş mumu + fiyat tepe bölgede ──────────
        if (cur_price < float(cur["open"]) and
                abs(price_change_pct) >= 0.005 and
                percentile_rank >= 0.65):        # son 20 mumun üst %35'inde

            score = min(1.0, 0.55 + min(vol_ratio / 10, 0.25) + (percentile_rank - 0.65) * 0.5)

            target, stop_loss = self.calc_tp_sl(cur_price, "SHORT", atr)

            return Signal(
                symbol=symbol,
                timeframe=timeframe,
                strategy=self.name,
                direction="SHORT",
                price=cur_price,
                target=target,
                stop_loss=stop_loss,
                score=round(score, 2),
                reason=(
                    f"Hacim Onaylı Tepe Short | "
                    f"Vol={vol_ratio:.1f}x | "
                    f"{price_change_pct*100:.2f}% | "
                    f"Fiyat rank=%{percentile_rank*100:.0f}"
                ),
            )

        return None
