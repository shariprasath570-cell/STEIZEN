from pathlib import Path
path = Path(r"C:\Users\Hariprasath\OneDrive\ICT BOT\src\analysis\strategy_edge_filter.py")
text = path.read_text(encoding="utf-8")
marker = "volatility_ratio = regime.volatility_ratio"
insert = '''volatility_ratio = regime.volatility_ratio
        # TEMP DEBUG: allow all
        return EdgeFilterResult(
            allowed=True,
            reason="EDGE_FILTER_DISABLED",
            regime=market_regime,
            efficiency_ratio=efficiency_ratio,
            volatility_ratio=volatility_ratio,
        )
'''
if "EDGE_FILTER_DISABLED" in text:
    print("Already disabled")
elif marker not in text:
    print("Marker not found")
else:
    text = text.replace(marker, insert, 1)
    path.write_text(text, encoding="utf-8")
    print("Edge filter disabled")
