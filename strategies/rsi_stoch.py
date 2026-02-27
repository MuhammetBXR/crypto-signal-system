"""
RSI + Stochastic RSI Stratejisi
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BUY  → RSI ≤ 30 (oversold) VE Stoch RSI K < 20 VE K, D'yi yukarı keser
SHORT→ RSI ≥ 70 (overbought) VE Stoch RSI K > 80 VE K, D'yi aşağı keser

Mantık: Her iki indikatör aynı anda aşırı bölgede ve dönüş başlamışsa gir.
"""
import pandas as pd
import numpy as np
from typing import Optional

from .base_strategy import BaseStrategy, Signal
import config


class RSIStochStrategy(BaseStrategy):

    def analyze(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Optional[Signal]:
        min_len = config.RSI_PERIOD + config.STOCH_RSI_PERIOD + 10
        if len(df) < min_len:
            return None

        # ── RSI hesapla ───────────────────────────────────
        delta = df["close"].diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)
        avg_gain = gain.ewm(com=config.RSI_PERIOD - 1, adjust=False).mean()
        avg_loss = loss.ewm(com=config.RSI_PERIOD - 1, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))

        # ── Stochastic RSI hesapla ────────────────────────
        rsi_min = rsi.rolling(config.STOCH_RSI_PERIOD).min()
        rsi_max = rsi.rolling(config.STOCH_RSI_PERIOD).max()
        stoch_rsi = (rsi - rsi_min) / (rsi_max - rsi_min).replace(0, np.nan) * 100
        stoch_k = stoch_rsi.rolling(config.STOCH_K_PERIOD).mean()
        stoch_d = stoch_k.rolling(config.STOCH_D_PERIOD).mean()

        # ── ATR (TP/SL için) ──────────────────────────────
        atr_series = self.calc_atr(df, config.ATR_PERIOD)

        # Son 2 mum
        cur_rsi = rsi.iloc[-1]
        cur_k = stoch_k.iloc[-1]
        cur_d = stoch_d.iloc[-1]
        prev_k = stoch_k.iloc[-2]
        prev_d = stoch_d.iloc[-2]
        cur_price = df["close"].iloc[-1]
        atr = atr_series.iloc[-1]

        if pd.isna(cur_rsi) or pd.isna(cur_k) or pd.isna(cur_d):
            return None

        # ── BUY koşulu ────────────────────────────────────
        # RSI aşırı satım + Stoch K oversold + K, D'yi yukarı kesmiş
        if (cur_rsi <= config.RSI_OVERBOUGHT and  # RSI oversold bölgesine yakın
            cur_k < config.STOCH_OVERSOLD and
            prev_k <= prev_d and cur_k > cur_d):  # Stoch K yukarı kesti

            # RSI ne kadar düşükse skor o kadar yüksek
            rsi_score = max(0, (config.RSI_OVERBOUGHT - cur_rsi) / config.RSI_OVERBOUGHT)
            stoch_score = max(0, (config.STOCH_OVERSOLD - cur_k) / config.STOCH_OVERSOLD)
            score = min(1.0, 0.5 + (rsi_score + stoch_score) * 0.25)

            # RSI aşırı düşükse bonus
            if cur_rsi <= config.RSI_EXTREME_OVERSOLD:
                score = min(1.0, score + 0.15)

            target, stop_loss = self.calc_tp_sl(cur_price, "BUY", atr)

            return Signal(
                symbol=symbol,
                timeframe=timeframe,
                strategy=self.name,
                direction="BUY",
                price=float(cur_price),
                target=float(target),
                stop_loss=float(stop_loss),
                score=round(score, 2),
                reason=(
                    f"RSI Oversold: {cur_rsi:.1f} | "
                    f"StochRSI K={cur_k:.1f} D={cur_d:.1f} (K ↑ D)"
                ),
            )

        # ── SHORT koşulu ──────────────────────────────────
        # RSI aşırı alım + Stoch K overbought + K, D'yi aşağı kesmiş
        if (cur_rsi >= config.RSI_OVERSOLD and
            cur_k > config.STOCH_OVERBOUGHT and
            prev_k >= prev_d and cur_k < cur_d):  # Stoch K aşağı kesti

            rsi_score = max(0, (cur_rsi - config.RSI_OVERSOLD) / (100 - config.RSI_OVERSOLD))
            stoch_score = max(0, (cur_k - config.STOCH_OVERBOUGHT) / (100 - config.STOCH_OVERBOUGHT))
            score = min(1.0, 0.5 + (rsi_score + stoch_score) * 0.25)

            if cur_rsi >= config.RSI_EXTREME_OVERBOUGHT:
                score = min(1.0, score + 0.15)

            target, stop_loss = self.calc_tp_sl(cur_price, "SHORT", atr)

            return Signal(
                symbol=symbol,
                timeframe=timeframe,
                strategy=self.name,
                direction="SHORT",
                price=float(cur_price),
                target=float(target),
                stop_loss=float(stop_loss),
                score=round(score, 2),
                reason=(
                    f"RSI Overbought: {cur_rsi:.1f} | "
                    f"StochRSI K={cur_k:.1f} D={cur_d:.1f} (K ↓ D)"
                ),
            )

        return None
