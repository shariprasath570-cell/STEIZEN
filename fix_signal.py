from pathlib import Path
path = Path(r"C:\Users\Hariprasath\OneDrive\ICT BOT\src\analysis\signal_engine.py")
text = path.read_text(encoding="utf-8")

start = text.find("def _evaluate_buy(")
end = text.find("def _evaluate_sell(")
if start == -1 or end == -1:
    print("Could not find methods")
    print(text[:500])
else:
    new_buy = '''def _evaluate_buy(
        self,
        sweep: bool,
        fvg: bool,
        order_block: bool,
    ):
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


    '''
    text = text[:start] + new_buy + text[end:]
    path.write_text(text, encoding="utf-8")
    print("BUY method restored")
