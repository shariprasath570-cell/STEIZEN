from pathlib import Path

p = Path(r"C:\Users\Hariprasath\OneDrive\ICT BOT\src\analysis\strategy_edge_filter.py")
t = p.read_text(encoding="utf-8")
old = "volatility_ratio = regime.volatility_ratio"
insert = old + "\n\n        return EdgeFilterResult(\n            allowed=True,\n            reason=\"EDGE_FILTER_DISABLED\",\n            regime=market_regime,\n            efficiency_ratio=efficiency_ratio,\n            volatility_ratio=volatility_ratio,\n        )\n"
if "EDGE_FILTER_DISABLED" in t:
    print("edge already disabled")
elif old in t:
    p.write_text(t.replace(old, insert, 1), encoding="utf-8")
    print("edge disabled")
else:
    print("edge old text not found")

p2 = Path(r"C:\Users\Hariprasath\OneDrive\ICT BOT\run_strategy_test.py")
t2 = p2.read_text(encoding="utf-8")
t2 = t2.replace("MAX_CONSEC_LOSSES = 3", "MAX_CONSEC_LOSSES = 50")
t2 = t2.replace("MAX_DAILY_LOSS = 300.0", "MAX_DAILY_LOSS = 5000.0")
p2.write_text(t2, encoding="utf-8")
print("limits written")

t = p.read_text(encoding="utf-8")
t2 = p2.read_text(encoding="utf-8")
print("DISABLED in edge:", "EDGE_FILTER_DISABLED" in t)
for line in t2.splitlines():
    if line.strip().startswith("MAX_"):
        print(line.strip())
