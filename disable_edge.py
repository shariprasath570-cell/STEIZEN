from pathlib import Path
path = Path(r"C:\Users\Hariprasath\OneDrive\ICT BOT\src\analysis\strategy_edge_filter.py")
text = path.read_text(encoding="utf-8")

old = '''def evaluate(
        self,
        direction: str,
        candles,
    ) -> EdgeFilterResult:
        regime = self.regime_engine.detect(
            candles
        )
        market_regime = regime.regime
        efficiency_ratio = regime.efficiency_ratio
        volatility_ratio = regime.volatility_ratio'''

new = '''def evaluate(
        self,
        direction: str,
        candles,
    ) -> EdgeFilterResult:
        regime = self.regime_engine.detect(
            candles
        )
        market_regime = regime.regime
        efficiency_ratio = regime.efficiency_ratio
        volatility_ratio = regime.volatility_ratio
        # TEMP: allow all trades for strategy debugging
        return EdgeFilterResult(
            allowed=True,
            reason="EDGE_FILTER_DISABLED",
            regime=market_regime,
            efficiency_ratio=efficiency_ratio,
            volatility_ratio=volatility_ratio,
        )
        # --- original logic below (disabled) ---'''

if old not in text:
    print("BLOCK NOT FOUND")
else:
    path.write_text(text.replace(old, new), encoding="utf-8")
    print("Edge filter disabled for testing")
