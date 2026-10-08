#!/usr/bin/env python3
"""SpecialMe laws refresh: change detection only. It never edits laws data itself.
Run weekly. Writes laws/state/hashes.json and laws/review/REPORT.md.
Exit code 0 always; a non-empty report means a human should review.
"""
import json, hashlib, re, sys, datetime, urllib.request, urllib.parse, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
STATE = ROOT / "state"; REVIEW = ROOT / "review"
STATE.mkdir(exist_ok=True); REVIEW.mkdir(exist_ok=True)
UA = {"User-Agent": "SpecialMe-law-check/1.0 (+https://specialme.app)"}

def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()

def norm(body):
    t = body.decode("utf-8", "ignore")
    t = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    t = re.sub(r"\b(19|20)\d\d-\d\d-\d\d[T ][\d:.]+Z?\b", " ", t)  # timestamps
    return re.sub(r"\s+", " ", t).strip().lower()

def main():
    src = json.load(open(ROOT / "data/sources.json"))
    states = json.load(open(ROOT / "data/states.json"))["states"]
    pages = list(src["pages"])
    for s in states:
        for label, u in (("special_ed", s.get("special_ed_page")), ("rights", s.get("parent_rights_page")),
                         ("regs", (s.get("regulations") or {}).get("url")),
                         ("dispute", (s.get("dispute_resolution") or {}).get("page"))):
            if u: pages.append({"id": f"{s['code']}-{label}", "url": u})
    hp = STATE / "hashes.json"
    old = json.load(open(hp)) if hp.exists() else {}
    new, changed, broken, first = {}, [], [], not old
    for p in pages:
        try:
            _, body = get(p["url"])
            h = hashlib.sha256(norm(body).encode()).hexdigest()
            new[p["id"]] = {"url": p["url"], "hash": h, "checked": datetime.date.today().isoformat()}
            if not first and p["id"] in old and old[p["id"]].get("hash") != h: changed.append(p)
        except Exception as e:
            broken.append((p, str(e)[:80]))
            if p["id"] in old: new[p["id"]] = old[p["id"]]
    # Federal Register
    fr_hits = []
    fr = src["federal_register"]
    since = (datetime.date.today() - datetime.timedelta(days=fr["lookback_days"])).isoformat()
    for q in fr["queries"]:
        params = [("conditions[term]", q["term"]), ("conditions[publication_date][gte]", since),
                  ("order", "newest"), ("per_page", "10"),
                  ("fields[]", "title"), ("fields[]", "publication_date"), ("fields[]", "html_url"), ("fields[]", "type")]
        for a in q.get("agencies", []): params.append(("conditions[agencies][]", a))
        try:
            _, body = get(fr["api"] + "?" + urllib.parse.urlencode(params))
            for r in json.loads(body).get("results", []): fr_hits.append((q["id"], r))
        except Exception as e:
            broken.append(({"id": "FR-" + q["id"], "url": fr["api"]}, str(e)[:80]))
    json.dump(new, open(hp, "w"), indent=1)
    lines = [f"# Laws refresh report {datetime.date.today().isoformat()}", ""]
    if first: lines += ["First run: baseline saved. No comparison yet.", ""]
    lines += [f"## Federal Register ({len(fr_hits)} items in last {fr['lookback_days']} days)"]
    lines += [f"- [{k}] {r['publication_date']} {r['type']}: [{r['title']}]({r['html_url']})" for k, r in fr_hits] or ["- none"]
    lines += ["", f"## Pages changed ({len(changed)})"] + ([f"- {p['id']}: {p['url']}" for p in changed] or ["- none"])
    lines += ["", f"## Unreachable ({len(broken)})"] + ([f"- {p['id']}: {p['url']} ({e})" for p, e in broken] or ["- none"])
    lines += ["", "## Reviewer steps", "1. Open each item and compare with data/federal.json or data/states.json.",
              "2. Edit the data file, set verified_at, change review status only after a human check.",
              "3. Close this issue.", ""]
    rep = "\n".join(lines)
    (REVIEW / "REPORT.md").write_text(rep)
    print(rep)
    needs = bool(fr_hits or changed) and not first
    (REVIEW / "NEEDS_REVIEW").write_text("1" if needs else "0")

if __name__ == "__main__":
    main()
