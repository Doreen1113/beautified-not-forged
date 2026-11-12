"""v7: move the recipe trade-off table (tab:tradeoff) out of the main text; point its references at the supplement's full table."""
from pathlib import Path

p = Path(__file__).resolve().parent / "main_v7.tex"; s = p.read_text(encoding="utf-8")
a = s.index("\\begin{table*}[t]\n\\centering\n\\caption{What each training recipe buys and costs")
b = s.index("\\end{table*}", a) + len("\\end{table*}\n")
s = s[:a] + s[b:]
s = s.replace("Table~\\ref{tab:tradeoff}", "Table~\\ref{S-tab:tradeofffull}")
p.write_text(s, encoding="utf-8"); print("removed tab:tradeoff block;", s.count("tab:tradeoff"), "references left")
