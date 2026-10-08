#!/usr/bin/env python3
"""Validates data files and writes data/laws.bundle.json for the app (federal + states)."""
import json, pathlib, sys, re
R = pathlib.Path(__file__).resolve().parents[1] / "data"
f = json.load(open(R / "federal.json")); s = json.load(open(R / "states.json"))
bad = []
if len(s["states"]) != 51: bad.append(f"expected 51 jurisdictions, got {len(s['states'])}")
for st in s["states"]:
    for k in ("code", "name", "agency", "verified_at"):
        if not st.get(k): bad.append(f"{st.get('code')}: missing {k}")
    for u in re.findall(r'"(http[^"]+)"', json.dumps(st)):
        if not u.startswith("https://"): bad.append(f"{st['code']}: non-https {u}")
if bad: print("\n".join(bad)); sys.exit(1)
json.dump({"federal": f, "states": s}, open(R / "laws.bundle.json", "w"), ensure_ascii=False, separators=(",", ":"))
print("ok", len(s["states"]), "states")
