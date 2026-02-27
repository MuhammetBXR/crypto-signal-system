"""
Bollinger Bands Stratejisi
━━━━━━━━━━━━━━━━━━━━━━━━━
BUY  → Fiyat alt bandın altına düştü / alt bandı dokundu (dip bölge)
SHORT→ Fiyat üst bandın üstüne çıktı / üst bandı dokundu (tepe bölge)

Ek sinyal gücü: Squeeze sonrası patlama daha güvenilir
"""
import pandas as pd
import numpy as np
from typing import Optional

from .base_strategy import BaseStrategy, Signal
import config


class BollingerBandsStrategy(BaseStrategy):

    def analyze(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Optional[Signal]:
        period = config.BB_PERIOD
        if len(df) < period + 5:
            return None

        close = df["close"]
        mid = close.rolling(period).mean()
        std = close.rolling(period).std()
        upper = mid + config.BB_STD * std
        lower = mid - config.BB_STD * std
        bandwidth = (upper - lower) / mid  # göreceli bant genişliği

        atr_series = self.calc_atr(df, config.ATR_PERIOD)

        cur = df.iloc[-1]
        prev = df.iloc[-2]
        cur_price = float(cur["close"])
        atr = float(atr_series.iloc[-1])

        cur_upper = float(upper.iloc[-1])
        cur_lower = float(lower.iloc[-1])
        cur_mid = float(mid.iloc[-1])
        prev_upper = float(upper.iloc[-2])
        prev_lower = float(lower.iloc[-2])
        cur_bw = float(bandwidth.iloc[-1])

        # Sıkışma (squeeze) tespiti: bant genişliği eşiğin altındaysa
        is_squeeze = cur_bw < config.BB_SQUEEZE_THRESHOLD
        squeeze_bonus = 0.10 if is_squeeze else 0.0

        if pd.isna(cur_upper) or pd.isna(cur_lower) or atr == 0:
            return None

        # ── BUY: Alt bandın altına düşüş (oversold bölge) ──────────
        # Mum alt bandı aşağı kesti (önceki mum üstteydi)
        if (float(prev["close"]) >= prev_lower and
                cur_price <= cur_lower):

            score = min(1.0, 0.70 + squeeze_bonus)
            # Bandın ne kadar altındayız?
            depth_pct = (cur_lower - cur_price) / cur_lower
            score = min(1.0, score + depth_pct * 2)

            target, stop_loss = self.calc_tp_sl(cur_price, "BUY", atr)

            reason = "BB Alt Band Kırıldı"
            if is_squeeze:
                reason += " (Squeeze Sonrası)"

            return Signal(
                symbol=symbol,
                timeframe=timeframe,
                strategy=self.name,
                direction="BUY",
                price=cur_price,
                target=target,
                stop_loss=stop_loss,
                score=round(score, 2),
                reason=f"{reason} | Lower={cur_lower:.4f} | BW={cur_bw:.3f}",
            )

        # ── SHORT: Üst bandın üstüne çıkış (overbought bölge) ──────
        if (float(prev["close"]) <= prev_upper and
                cur_price >= cur_upper):

            score = min(1.0, 0.70 + squeeze_bonus)
            depth_pct = (cur_price - cur_upper) / cur_upper
            score = min(1.0, score + depth_pct * 2)

            target, stop_loss = self.calc_tp_sl(cur_price, "SHORT", atr)

            reason = "BB Üst Band Kırıldı"
            if is_squeeze:
                reason += " (Squeeze Sonrası)"

            return Signal(
                symbol=symbol,
                timeframe=timeframe,
                strategy=self.name,
                direction="SHORT",
                price=cur_price,
                target=target,
                stop_loss=stop_loss,
                score=round(score, 2),
                reason=f"{reason} | Upper={cur_upper:.4f} | BW={cur_bw:.3f}",
            )

        return None
