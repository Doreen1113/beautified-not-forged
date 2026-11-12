"""Six-feature AI-writing self-check on main_v7.tex (feedback_no_ai_writing): hype adjectives, coined terms, sentence-initial
adverb + comma, self-addressed section openers, repeated sentences, em-dashes. Also counts 'X, not Y' contrasts and colons.
python docs/paper_v2/style_check_v7.py -> STYLE_CHECK_v7.md"""
import re
from collections import Counter
from pathlib import Path

H = Path(__file__).resolve().parent; s = (H / "main_v7.tex").read_text(encoding="utf-8")
body = s[s.index("\\begin{abstract}"):s.index("\\bibliographystyle")]
body = re.sub(r"\\begin\{(table|figure)\*?\}.*?\\end\{(table|figure)\*?\}", " ", body, flags=re.S)
text = re.sub(r"%.*", "", body); text = re.sub(r"\\(cite|ref|label|eqref)\{[^}]*\}", "", text)
text = re.sub(r"\$[^$]*\$", "X", text); text = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", " ", text); text = re.sub(r"[{}~]", " ", text)
sents = [x.strip() for x in re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text)) if len(x.strip()) > 20]

HYPE = r"\b(striking|remarkabl\w*|dramatic\w*|crucial\w*|fundamental\w*|unprecedented|groundbreaking|novel|significantly|substantially|notabl\w*|importantly|critically|clearly|surprisingly|impressive\w*|key insight|paradigm|pivotal|robustly|vastly|massive\w*|extensive\w*|comprehensive\w*)\b"
ADV = r"^(Notably|Importantly|Crucially|Interestingly|Moreover|Furthermore|Additionally|Overall|Consequently|Thus|Hence|Indeed|Specifically|Finally|First|Second|Third|In contrast|In particular|Surprisingly|Strikingly),"
OPEN = r"\b(in this section|this section|we now|we next|here we|we first|let us|we begin)\b"
L = ["# Style check, main_v7.tex", ""]
hits = [(m.group(0), x) for x in sents for m in re.finditer(HYPE, x, re.I)]
L += [f"## 1. Hype words: {len(hits)}", ""] + [f"- **{w}**: {x[:160]}" for w, x in hits] + [""]
adv = [x for x in sents if re.match(ADV, x)]
L += [f"## 3. Sentence-initial adverb + comma: {len(adv)}", ""] + [f"- {x[:160]}" for x in adv] + [""]
op = [x for x in sents if re.search(OPEN, x, re.I)]
L += [f"## 4. Self-addressed openers: {len(op)}", ""] + [f"- {x[:160]}" for x in op] + [""]
tri = Counter(" ".join(w) for x in sents for w in zip(*[re.findall(r"[a-z]+", x.lower())[i:] for i in range(6)]))
rep = [(k, v) for k, v in tri.most_common(40) if v >= 3]
L += [f"## 5. Repeated 6-word phrases (>= 3 times): {len(rep)}", ""] + [f"- {v}x: {k}" for k, v in rep] + [""]
em = len(re.findall(r"---|\u2014", body))
L += [f"## 6. Em-dashes: {em}", ""]
nots = [x for x in sents if re.search(r", not [a-z]", x)]
L += [f"## Extra: 'X, not Y' contrasts: {len(nots)}", ""] + [f"- {x[:160]}" for x in nots] + [""]
cols = sum(x.count(":") for x in sents)
L += [f"## Extra: colons in sentences: {cols} over {len(sents)} sentences", ""]
caps = Counter(re.findall(r"\b[A-Z][a-z]+(?:-[A-Z][a-z]+)+\b", text))
L += ["## 2. Hyphenated capitalised terms (candidate coined names)", ""] + [f"- {k}: {v}" for k, v in caps.most_common(15)]
(H / "STYLE_CHECK_v7.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print(f"hype {len(hits)} | adverb-comma {len(adv)} | openers {len(op)} | repeated6 {len(rep)} | em-dash {em} | not-contrasts {len(nots)} | colons {cols}/{len(sents)}")
