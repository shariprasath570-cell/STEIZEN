from pathlib import Path

path = Path(r"C:\Users\Hariprasath\OneDrive\ICT BOT\src\analysis\signal_engine.py")

content = '''from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TradingSignal:
    direction: str
    confidence: int
    reason: str
    confirmations: List[str] = field(default_factory=list)


class SignalEngine:
    """
    ICT Signal Engine.

    SCORING:
        Trend (required) : 30 pts
        Sweep            : 25 pts
        FVG              : 25 pts
        Order Block      : 20 pts

    THRESHOLD: 50 pts
    """

    MIN_CONFIDENCE = 50

    def generate_signal(
        self,
        trend: str,
        bullish_sweep: bool = False,
        bearish_sweep: bool = False,
        bullish_fvg: bool = False,
        bearish_fvg: bool = False,
        bullish_order_block: bool = False,
        bearish_order_block: bool = False,
    ) -> Optional[TradingSignal]:
        if trend in ("BULLISH", "RANGING"):
            signal = self._evaluate_buy(
                sweep=bullish_sweep,
                fvg=bullish_fvg,
                order_block=bullish_order_block,
            )
            if signal is not None:
                return signal

        if trend in ("BEARISH", "RANGING"):
            signal = self._evaluate_sell(
                sweep=bearish_sweep,
                fvg=bearish_fvg,
                order_block=bearish_order_block,
            )
            if signal is not None:
                return signal

        return None

    def _evaluate_buy(
        self,
        sweep: bool,
        fvg: bool,
        order_block: bool,
    ) -> Optional[TradingSignal]:
        confirmations = ["Bullish Trend"]
        confidence = 30

        if sweep:
            confidence += 25
            confirmations.append("Liquidity Sweep")

        if fvg:
            confidence += 25
            confirmations.append("Bullish FVG")

        if order_block:
            confidence += 20
            confirmations.append("Bullish Order Block")

        if confidence < self.MIN_CONFIDENCE:
            return None

        return TradingSignal(
            direction="BUY",
            confidence=confidence,
            reason=" + ".join(confirmations),
            confirmations=confirmations,
        )

    def _evaluate_sell(
        self,
        sweep: bool,
        fvg: bool,
        order_block: bool,
    ) -> Optional[TradingSignal]:
        confirmations = ["Bearish Trend"]
        confidence = 30

        if sweep:
            confidence += 25
            confirmations.append("Liquidity Sweep")

        if fvg:
            confidence += 25
            confirmations.append("Bearish FVG")

        if order_block:
            confidence += 20
            confirmations.append("Bearish Order Block")

        if confidence < self.MIN_CONFIDENCE:
            return None

        return TradingSignal(
            direction="SELL",
            confidence=confidence,
            reason=" + ".join(confirmations),
            confirmations=confirmations,
        )
'''

path.write_text(content, encoding="utf-8")
print("signal_engine.py rewritten cleanly")
