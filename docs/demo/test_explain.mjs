// node test_explain.mjs demo_parity_inputs.json
// Checks explain.js against the Python rule-B part names on the same crops (demo_parity_dump.py), and reports how often
// the demo names the edited part of held-out part forgeries.
import { readFileSync } from "node:fs";
import { explain, PARTS } from "./explain.js";

const items = JSON.parse(readFileSync(process.argv[2], "utf8"));
let same = 0, n = 0, partRight = 0, partN = 0, maxDiff = 0;
for (const it of items) {
  const r = explain(it.logits, it.presence, it.ev, it.h, it.w, it.lm, 380);
  const jsTop = PARTS.reduce((a, b) => (r.parts[b] > r.parts[a] ? b : a));
  n++; same += jsTop === it.py_top;
  for (const k of PARTS) maxDiff = Math.max(maxDiff, Math.abs(r.parts[k] - it.py_parts[k]));
  if (["eyes", "nose", "mouth"].includes(it.truth) && r.label === "fake") { partN++; partRight += jsTop === it.truth; }
}
console.log(JSON.stringify({ items: n, top_part_same_as_python: `${same}/${n}`, max_abs_diff_part_mean: +maxDiff.toFixed(4),
  part_forgeries_detected: partN, right_part_named: `${partRight}/${partN}` }));
