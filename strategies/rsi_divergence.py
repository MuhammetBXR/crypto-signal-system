"""
RSI Divergence Stratejisi
━━━━━━━━━━━━━━━━━━━━━━━━
Bullish Divergence → Fiyat daha düşük dip yaparken RSI daha yüksek dip yapıyor
                     → Düşüş momenti zayıflıyor → BUY sinyali

Bearish Divergence → Fiyat daha yüksek tepe yaparken RSI daha düşük tepe yapıyor
                     → Yükseliş momenti zayıflıyor → SHORT sinyali

Bu divergence dönüş noktalarını en erken tespit eden indikatördür.
"""
import pandas as pd
import numpy as np
from typing import Optional

from .base_strategy import BaseStrategy, Signal
import config


class RSIDivergenceStrategy(BaseStrategy):

    def _calc_rsi(self, close: pd.Series) -> pd.Series:
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)
        avg_gain = gain.ewm(com=config.RSI_PERIOD - 1, adjust=False).mean()
        avg_loss = loss.ewm(com=config.RSI_PERIOD - 1, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        return 100 - (100 / (1 + rs))

    def analyze(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Optional[Signal]:
        min_len = config.RSI_PERIOD + config.DIV_LOOKBACK + 10
        if len(df) < min_len:
            return None

        rsi = self._calc_rsi(df["close"])
        atr_series = self.calc_atr(df, config.ATR_PERIOD)

        # Son DIV_LOOKBACK mumu al
        window = config.DIV_LOOKBACK
        recent_price_low = df["low"].values[-window:]
        recent_price_high = df["high"].values[-window:]
        recent_rsi = rsi.values[-window:]
        sw = config.DIV_SWING_WINDOW

        price_lows = self.find_swing_lows(recent_price_low, sw)
        price_highs = self.find_swing_highs(recent_price_high, sw)
        rsi_lows = self.find_swing_lows(recent_rsi, sw)
        rsi_highs = self.find_swing_highs(recent_rsi, sw)

        cur_price = float(df["close"].iloc[-1])
        cur_rsi = float(rsi.iloc[-1])
        atr = float(atr_series.iloc[-1])

        if pd.isna(cur_rsi) or atr == 0:
            return None

        # ── Bullish Divergence (BUY) ──────────────────────────────────
        # Fiyat: daha düşük dip (LL), RSI: daha yüksek dip (HL)
        if len(price_lows) >= 2 and len(rsi_lows) >= 2:
            p_idx1, p_val1 = price_lows[-2]
            p_idx2, p_val2 = price_lows[-1]
            r_idx1, r_val1 = rsi_lows[-2]
            r_idx2, r_val2 = rsi_lows[-1]

            price_move = abs(p_val2 - p_val1) / (p_val1 + 1e-9)

            if (p_val2 < p_val1 and          # Fiyat daha düşük dip
                r_val2 > r_val1 and          # RSI daha yüksek dip
                price_move >= config.DIV_MIN_SWING):

                # RSI oversold bölgesindeyse çok daha güçlü
                oversold_bonus = 0.15 if cur_rsi < config.RSI_OVERBOUGHT else 0.0
                score = min(1.0, 0.75 + oversold_bonus)

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
                        f"Bullish RSI Divergence | "
                        f"Fiyat LL ({p_val1:.4f}→{p_val2:.4f}) "
                        f"RSI HL ({r_val1:.1f}→{r_val2:.1f}) "
                        f"[RSI mevcut: {cur_rsi:.1f}]"
                    ),
                )

        # ── Bearish Divergence (SHORT) ────────────────────────────────
        # Fiyat: daha yüksek tepe (HH), RSI: daha düşük tepe (LH)
        if len(price_highs) >= 2 and len(rsi_highs) >= 2:
            p_idx1, p_val1 = price_highs[-2]
            p_idx2, p_val2 = price_highs[-1]
            r_idx1, r_val1 = rsi_highs[-2]
            r_idx2, r_val2 = rsi_highs[-1]

            price_move = abs(p_val2 - p_val1) / (p_val1 + 1e-9)

            if (p_val2 > p_val1 and          # Fiyat daha yüksek tepe
                r_val2 < r_val1 and          # RSI daha düşük tepe
                price_move >= config.DIV_MIN_SWING):

                overbought_bonus = 0.15 if cur_rsi > config.RSI_OVERSOLD else 0.0
                score = min(1.0, 0.75 + overbought_bonus)

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
                        f"Bearish RSI Divergence | "
                        f"Fiyat HH ({p_val1:.4f}→{p_val2:.4f}) "
                        f"RSI LH ({r_val1:.1f}→{r_val2:.1f}) "
                        f"[RSI mevcut: {cur_rsi:.1f}]"
                    ),
                )

        return None
