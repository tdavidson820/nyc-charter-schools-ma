"""
Step 4: reconcile our campus count with the NYC Charter School Center finder, listing by listing.
Every finder listing is assigned to exactly one of our campuses or given an explicit reason it is not one,
and every campus of ours without a finder listing is named. Output: data/review/count_reconciliation.csv.
"""
import csv, re, sys
from collections import Counter, defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from reconcile import norm_addr
from build_campuses import dist_m, toks, LISTING_RESOLUTION, NONSUNY_CORRECTIONS

SRC = ROOT / "data" / "sources"
camp = list(csv.DictReader(open(ROOT / "data" / "campuses.csv", encoding="utf-8")))
raw = [l.rstrip("\n").split("\t") for l in open(SRC / "charter_center_finder_2026-10-30.tsv", encoding="utf-8")]
corrected_src = {k[1] for k in NONSUNY_CORRECTIONS}
rows, used = [], Counter()
for c in raw:
    if c[0].startswith("test") or c[2].upper().startswith("TEST"):
        rows.append([c[2], c[5], "not a campus", "Test record in the finder", ""]); continue
    key, pt = norm_addr(c[5]), (float(c[8]), float(c[9]))
    if key in LISTING_RESOLUTION and LISTING_RESOLUTION[key][0] != "mapped":
        rows.append([c[2], c[5], "not a campus", LISTING_RESOLUTION[key][1], ""]); continue
    cand = [x for x in camp if norm_addr(x["address"]) == key or dist_m(pt, (float(x["lat"]), float(x["lon"]))) < 250]
    if key in corrected_src and "new ventures" in c[2].lower():
        cand = [x for x in camp if x["school"] == "New Ventures Charter School"]
    nm = toks(c[2])
    cid_of = lambda x: x["school"] + " @ " + x["address"]
    best = sorted(cand, key=lambda x: (used[cid_of(x)] > 0 or not (nm & toks(x["school"])), -len(nm & toks(x["school"])), dist_m(pt, (float(x["lat"]), float(x["lon"])))))
    best = [x for x in best if nm & toks(x["school"])] or best
    if not best:
        rows.append([c[2], c[5], "UNMATCHED", "", ""]); continue
    b = best[0]; cid = b["school"] + " @ " + b["address"]
    used[cid] += 1
    rows.append([c[2], c[5], "campus" if used[cid] == 1 else "extra listing for same campus", "", cid])
no_listing = [x["school"] + " @ " + x["address"] for x in camp if x["school"] + " @ " + x["address"] not in used]
with open(ROOT / "data" / "review" / "count_reconciliation.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["finder_listing", "finder_address", "outcome", "reason", "our_campus"])
    w.writerows(rows)
    for n in no_listing: w.writerow(["", "", "our campus with no finder listing", "", n])
oc = Counter(r[2] for r in rows)
print("Finder listings:", len(raw), dict(oc))
print("Our campuses:", len(camp), "| with a finder listing:", len(used), "| without:", len(no_listing))
for r in rows:
    if r[2] in ("UNMATCHED",): print("  UNMATCHED", r[0], "@", r[1])
print("Extra listings (same campus):"); [print("  ", r[0], "->", r[4]) for r in rows if r[2].startswith("extra")]
print("Campuses with no finder listing:"); [print("  ", n) for n in no_listing]
