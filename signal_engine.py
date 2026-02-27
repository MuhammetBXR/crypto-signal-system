"""
Signal Engine - MTF Confluence Motoru
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Her coin için:
1. 4 strateji × 3 timeframe = 12 potansiyel sinyal çalıştırılır
2. Aynı yöndeki sinyaller toplanır (confluence)
3. Farklı timeframe'lerden geliyorsa MTF bonusu eklenir
4. MIN_CONFLUENCE eşiğini geçenler FinalSignal olarak döner

Skor sistemi:
- Her strateji 0.0-1.0 arası skor döner
- Confluence skoru = strateji sayısı × ortalama skor × MTF çarpanı
- Eşik: MIN_CONFLUENCE strateji sayısı
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

from strategies.base_strategy import Signal
from strategies.rsi_stoch import RSIStochStrategy
from strategies.bollinger_bands import BollingerBandsStrategy
from strategies.rsi_divergence import RSIDivergenceStrategy
from strategies.volume_confirm import VolumeConfirmStrategy
import config

logger = logging.getLogger(__name__)


@dataclass
class FinalSignal:
    """
    Birden fazla stratejinin onayladığı nihai sinyal.
    """
    symbol: str
    direction: str          # 'BUY' veya 'SHORT'
    price: float
    target: float
    stop_loss: float
    confluence: int         # Kaç strateji onayladı
    avg_score: float        # Ortalama güven skoru
    timeframes: List[str]   # Hangi timeframe'lerden sinyal geldi
    strategies: List[str]   # Hangi stratejiler tetikledi
    reasons: List[str]      # Detaylı açıklamalar
    is_mtf: bool            # Birden fazla timeframe'den mi geldi?
    timestamp: datetime = field(default_factory=datetime.utcnow)

    @property
    def final_score(self) -> float:
        """MTF bonusu ile birlikte nihai skor"""
        base = self.avg_score
        if self.is_mtf:
            base = min(1.0, base + 0.10)
        return round(base, 2)

    def summary(self) -> str:
        """İnsan okunabilir özet"""
        direction_emoji = "📈 BUY" if self.direction == "BUY" else "📉 SHORT"
        mtf_tag = " [MTF✓]" if self.is_mtf else ""
        tf_str = "+".join(sorted(set(self.timeframes)))

        lines = [
            f"{'='*50}",
            f"{direction_emoji} | {self.symbol} | {tf_str}{mtf_tag}",
            f"  Giriş  : {self.price:.6g}",
            f"  Hedef  : {self.target:.6g}  ({self._pct(self.price, self.target):+.2f}%)",
            f"  Stop   : {self.stop_loss:.6g}  ({self._pct(self.price, self.stop_loss):+.2f}%)",
            f"  Skor   : {self.final_score:.0%}  |  Confluence: {self.confluence} strateji",
            f"  Stratejiler: {', '.join(self.strategies)}",
            "  Sebepler:",
        ]
        for r in self.reasons:
            lines.append(f"    • {r}")
        lines.append(f"{'='*50}")
        return "\n".join(lines)

    @staticmethod
    def _pct(entry: float, other: float) -> float:
        return (other - entry) / entry * 100 if entry else 0


class SignalEngine:
    """Tüm stratejileri çalıştırır, MTF confluence hesaplar."""

    def __init__(self):
        self.strategies = [
            RSIStochStrategy(),
            BollingerBandsStrategy(),
            RSIDivergenceStrategy(),
            VolumeConfirmStrategy(),
        ]
        logger.info(f"SignalEngine başlatıldı: {len(self.strategies)} strateji")

    def analyze(
        self,
        symbol: str,
        data: Dict[str, pd.DataFrame],   # {timeframe: df}
    ) -> List[FinalSignal]:
        """
        Bir coin için tüm timeframe + strateji kombinasyonlarını çalıştır.
        Returns: confluence eşiğini geçen FinalSignal listesi
        """
        raw_signals: List[Signal] = []

        for tf, df in data.items():
            if df is None or df.empty or len(df) < 30:
                continue
            for strategy in self.strategies:
                try:
                    sig = strategy.analyze(df, symbol, tf)
                    if sig is not None:
                        raw_signals.append(sig)
                        logger.debug(
                            f"[{symbol}][{tf}] {strategy.name}: "
                            f"{sig.direction} skor={sig.score:.2f}"
                        )
                except Exception as exc:
                    logger.warning(
                        f"[{symbol}][{tf}] {strategy.name} hata: {exc}"
                    )

        if not raw_signals:
            return []

        return self._build_final_signals(symbol, raw_signals)

    def _build_final_signals(
        self, symbol: str, signals: List[Signal]
    ) -> List[FinalSignal]:
        """Aynı yöndeki sinyalleri grupla, confluence hesapla."""
        results: List[FinalSignal] = []

        for direction in ("BUY", "SHORT"):
            group = [s for s in signals if s.direction == direction]
            if len(group) < config.MIN_CONFLUENCE:
                continue

            # Ağırlıklı ortalama fiyat (skora göre)
            total_score = sum(s.score for s in group)
            w_price = sum(s.price * s.score for s in group) / total_score
            w_target = sum(s.target * s.score for s in group) / total_score
            w_sl = sum(s.stop_loss * s.score for s in group) / total_score
            avg_score = total_score / len(group)

            timeframes = [s.timeframe for s in group]
            unique_tfs = list(set(timeframes))
            strategy_names = list(set(s.strategy for s in group))
            reasons = [s.reason for s in group]
            is_mtf = len(unique_tfs) >= 2

            final = FinalSignal(
                symbol=symbol,
                direction=direction,
                price=round(w_price, 8),
                target=round(w_target, 8),
                stop_loss=round(w_sl, 8),
                confluence=len(group),
                avg_score=round(avg_score, 2),
                timeframes=timeframes,
                strategies=strategy_names,
                reasons=reasons,
                is_mtf=is_mtf,
            )
            results.append(final)
            logger.info(
                f"[{symbol}] {direction} FinalSignal: "
                f"confluence={len(group)} score={final.final_score:.0%} "
                f"mtf={is_mtf} tfs={unique_tfs}"
            )

        return results

    def analyze_batch(
        self,
        all_data: Dict[str, Dict[str, pd.DataFrame]],
    ) -> List[FinalSignal]:
        """
        Tüm coinleri analiz et.
        all_data: {symbol: {timeframe: df}}
        """
        all_signals: List[FinalSignal] = []
        total = len(all_data)

        for idx, (symbol, data) in enumerate(all_data.items(), 1):
            try:
                sigs = self.analyze(symbol, data)
                all_signals.extend(sigs)
            except Exception as exc:
                logger.error(f"[{symbol}] analiz hatası: {exc}")

            if idx % 50 == 0:
                logger.info(f"İlerleme: {idx}/{total} coin tarandı")

        logger.info(
            f"Tarama tamamlandı: {total} coin, "
            f"{len(all_signals)} sinyal üretildi"
        )
        return all_signals
