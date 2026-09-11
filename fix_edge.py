from pathlib import Path
path = Path(r"C:\Users\Hariprasath\OneDrive\ICT BOT\src\analysis\strategy_edge_filter.py")
text = path.read_text(encoding="utf-8")

# Lower choppy threshold from 0.20 to 0.10
text2 = text.replace("efficiency_ratio < 0.20", "efficiency_ratio < 0.10")
text2 = text2.replace("efficiency_ratio >= 0.20", "efficiency_ratio >= 0.10")

if text2 == text:
    print("No replacements made - check file content")
else:
    path.write_text(text2, encoding="utf-8")
    print("Edge filter relaxed: ER threshold 0.20 -> 0.10")
