from pathlib import Path
path = Path(r"C:\Users\Hariprasath\OneDrive\ICT BOT\src\core\automated_trading_engine.py")
lines = path.read_text(encoding="utf-8").splitlines(True)
ref_indent = "        "
for line in lines:
    if "if signal is None" in line:
        ref_indent = line[: len(line) - len(line.lstrip(" \t"))]
        break
print("Using indent:", repr(ref_indent))
start = end = None
for i, line in enumerate(lines):
    if "trend_value = (" in line and start is None:
        start = i
    if start is not None and "bearish_order_block=bearish_order_block" in line:
        end = i + 2
        break
if start is None:
    print("Could not find trend_value block")
else:
    ri = ref_indent
    new_block = [
        ri + "trend_value = (\n",
        ri + "    state.trend.value\n",
        ri + "    if hasattr(state.trend, \"value\")\n",
        ri + "    else str(state.trend)\n",
        ri + ")\n",
        ri + "trend_value = trend_value.replace(\"Trend.\", \"\").upper()\n",
        "\n",
        ri + "signal = self.signal_engine.generate_signal(\n",
        ri + "    trend=trend_value,\n",
        ri + "    bullish_sweep=bullish_sweep,\n",
        ri + "    bearish_sweep=bearish_sweep,\n",
        ri + "    bullish_fvg=bullish_fvg,\n",
        ri + "    bearish_fvg=bearish_fvg,\n",
        ri + "    bullish_order_block=bullish_order_block,\n",
        ri + "    bearish_order_block=bearish_order_block,\n",
        ri + ")\n",
    ]
    lines = lines[:start] + new_block + lines[end:]
    path.write_text("".join(lines), encoding="utf-8")
    print(f"Fixed lines {start+1}-{end}")
