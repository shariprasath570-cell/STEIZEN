from pathlib import Path
path = Path(r"C:\Users\Hariprasath\OneDrive\ICT BOT\run_strategy_test.py")
text = path.read_text(encoding="utf-8")
text = text.replace("MAX_TRADES_PER_DAY = 3", "MAX_TRADES_PER_DAY = 50")
text = text.replace("MAX_CONSEC_LOSSES = 3", "MAX_CONSEC_LOSSES = 50")
text = text.replace("MAX_DAILY_LOSS = 300.0", "MAX_DAILY_LOSS = 5000.0")
path.write_text(text, encoding="utf-8")
print("Risk limits raised for backtest")
