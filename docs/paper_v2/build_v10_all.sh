#!/bin/sh
# Build the three v10 pairs on gsplat-ubuntu (tectonic): main_v10 + supplement_v10 (full text, conference class),
# main_v10c + supplement_v10c (IJCB cut), main_v10j + supplement_v10j (TIFS journal). Each pair is built main, supp, main, supp
# so that the xr cross-references resolve both ways. Run from anywhere: sh docs/paper_v2/build_v10_all.sh
set -e
D=$(cd "$(dirname "$0")" && pwd)
cd "$D"
scp -q main_v10.tex main_v10c.tex main_v10j.tex supplement_v10.tex supplement_v10c.tex supplement_v10j.tex refs_v6.bib refs_v8.bib gsplat-ubuntu:paper_build/paper_v2/
scp -q tables/*.tex gsplat-ubuntu:paper_build/paper_v2/tables/
scp -q figs/*.pdf gsplat-ubuntu:paper_build/paper_v2/figs/
ssh gsplat-ubuntu 'cd ~/paper_build/paper_v2 && T=~/miniconda3/envs/tex/bin/tectonic;
  for pair in "main_v10 supplement_v10" "main_v10c supplement_v10c" "main_v10j supplement_v10j"; do
    set -- $pair; for f in $1 $2 $1 $2; do $T -k $f.tex > t_$f.out 2>&1 || { echo FAIL $f; grep -A6 "^error" t_$f.out | head -20; }; done;
  done;
  grep -hE "undefined|^error" t_main_v10*.out t_supplement_v10*.out | sort | uniq -c; echo build done'
for f in main_v10 main_v10c main_v10j supplement_v10 supplement_v10c supplement_v10j; do
  scp -q gsplat-ubuntu:paper_build/paper_v2/$f.pdf "$D/$f.pdf" 2>/dev/null || { echo "WARNING: $f.pdf locked, written as ${f}_new.pdf"; scp -q gsplat-ubuntu:paper_build/paper_v2/$f.pdf "$D/${f}_new.pdf"; }
done
/c/Users/2603055/AppData/Local/miniconda3/python.exe - <<'PY'
import fitz
for f in ("main_v10", "main_v10c", "main_v10j", "supplement_v10", "supplement_v10c", "supplement_v10j"):
    d = fitz.open(f + ".pdf"); refs = ""
    for i, p in enumerate(d):
        for x in p.get_text("blocks"):
            if "EFERENCES" in x[4] and f.startswith("main"): refs = f"refs p{i+1} y{x[1]:.0f} x{x[0]:.0f}"
    print(f, d.page_count, "pages", refs)
PY
