from pathlib import Path
import re

p = Path(r"C:\Users\Hariprasath\OneDrive\ICT BOT\src\analysis\strategy_edge_filter.py")
lines = p.read_text(encoding="utf-8").splitlines(True)
out = []
done = False
for line in lines:
    out.append(line)
    if (not done) and ("volatility_ratio = regime.volatility_ratio" in line) and ("self." not in line):
        indent = line[:len(line) - len(line.lstrip(" \t"))]
        out.append("\n")
        out.append(indent + "return EdgeFilterResult(\n")
        out.append(indent + "    allowed=True,\n")
        out.append(indent + "    reason='EDGE_FILTER_DISABLED',\n")
        out.append(indent + "    regime=market_regime,\n")
        out.append(indent + "    efficiency_ratio=efficiency_ratio,\n")
        out.append(indent + "    volatility_ratio=volatility_ratio,\n")
        out.append(indent + ")\n")
        done = True
p.write_text("".join(out), encoding="utf-8")
print("edge disabled:", done)

p2 = Path(r"C:\Users\Hariprasath\OneDrive\ICT BOT\run_strategy_test.py")
t2 = p2.read_text(encoding="utf-8")
t2 = re.sub(r"MAX_CONSEC_LOSSES\s*=\s*3", "MAX_CONSEC_LOSSES = 50", t2)
t2 = re.sub(r"MAX_DAILY_LOSS\s*=\s*300\.0", "MAX_DAILY_LOSS = 5000.0", t2)
p2.write_text(t2, encoding="utf-8")
print("limits updated")

t = p.read_text(encoding="utf-8")
t2 = p2.read_text(encoding="utf-8")
print("DISABLED:", "EDGE_FILTER_DISABLED" in t)
for line in t2.splitlines():
    s = line.strip()
    if s.startswith("MAX_CONSEC_LOSSES") or s.startswith("MAX_DAILY_LOSS"):
        print(s)
