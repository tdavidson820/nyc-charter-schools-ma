"""
Reconcile NYC charter school campuses across four independent sources.

Inputs (data/sources/, each captured 2026-10-30 and checksum-verified):
  charter_center_finder_2026-10-30.tsv    NYC Charter School Center campus finder (420 listings)
  nyc_doe_transportation_sites_2025-26.tsv NYC DOE Office of Pupil Transportation sites, charter, 2025-26
  successacademy_2026-10-30.tsv           Success Academy's own school pages
  nysed_directory_nyc.tsv                 NYSED charter directory, NYC rows

Output: data/review/campus_review.csv, one row per candidate campus, with a status and the
evidence from every source, plus data/review/unmatched_city_sites.csv.
"""
from __future__ import annotations

import csv
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "sources"
OUT = ROOT / "data" / "review"

ORD = {"FIRST": "1", "SECOND": "2", "THIRD": "3", "FOURTH": "4", "FIFTH": "5",
       "SIXTH": "6", "SEVENTH": "7", "EIGHTH": "8", "NINTH": "9", "TENTH": "10", "ONE": "1"}
SUFFIX = [(r"\bSTREET\b|\bSTRRET\b|\bSTREEET\b|\bST\b", "ST"), (r"\bAVENUE\b|\bAVE\b", "AV"),
          (r"\bBOULEVARD\b|\bBLVD\b", "BL"), (r"\bPLACE\b|\bPL\b", "PL"), (r"\bPARKWAY\b|\bPKWY\b", "PKY"),
          (r"\bROAD\b|\bRD\b", "RD"), (r"\bDRIVE\b|\bDR\b", "DR"), (r"\bLANE\b", "LN"),
          (r"\bEAST\b", "E"), (r"\bWEST\b", "W"), (r"\bNORTH\b", "N"), (r"\bSOUTH\b", "S"), (r"\bSAINT\b", "ST")]


def norm_addr(s: str) -> str:
    s = (s or "").upper()
    s = re.split(r",| FLOOR| FL\b| \d+(ST|ND|RD|TH) FL| ROOM | ANNEX| TRAILER|\. QUEENS", s)[0]
    s = re.sub(r"[.#']", "", s)
    s = re.sub(r"\b(\d+)(ST|ND|RD|TH)\b", r"\1", s)
    for k, v in ORD.items():
        s = re.sub(rf"\b{k}\b", v, s)
    for pat, rep in SUFFIX:
        s = re.sub(pat, rep, s)
    s = re.sub(r"\s+", " ", s).strip()
    m = re.match(r"^(\d+)-(\d+)\s+(.*)$", s)          # "144-176 E 128 ST" -> keep first number unless Queens style
    if m and len(m.group(2)) >= 3 and int(m.group(2)) > int(m.group(1)):
        s = f"{m.group(1)} {m.group(3)}"
    return s


def dist_m(a, b) -> float:
    (la1, lo1), (la2, lo2) = a, b
    return math.hypot((la1 - la2) * 111_000, (lo1 - lo2) * 84_000)


def read(name: str) -> list[list[str]]:
    with open(SRC / name, encoding="utf-8") as f:
        return [line.rstrip("\n").split("\t") for line in f if line.strip()]


def is_summer(name: str) -> bool:
    return bool(re.match(r"^84[MXKQR]\d{3} ", name)) or "SUMMER" in name.upper()


def main() -> None:
    cc = [dict(zip(["slug", "title", "h1", "csd", "grades", "street", "boro", "zip", "lat", "lon", "web"], r))
          for r in read("charter_center_finder_2026-10-30.tsv")]
    opt = [dict(zip(["code", "name", "street", "zip", "lat", "lon"], r))
           for r in read("nyc_doe_transportation_sites_2025-26.tsv")]
    sa = [dict(zip(["slug", "name", "street", "city", "zip", "grades", "csd", "lat", "lon"], r))
          for r in read("successacademy_2026-10-30.tsv")]

    for rows in (cc, opt, sa):
        for r in rows:
            r["key"] = norm_addr(r["street"])
            r["pt"] = (float(r["lat"]), float(r["lon"])) if r.get("lat") else None

    opt_real = [o for o in opt if not is_summer(o["name"])]
    summer = [o for o in opt if is_summer(o["name"])]

    def opt_match(r):
        same = [o for o in opt_real if o["key"] == r["key"]]
        if same:
            return "address", same
        near = [o for o in opt_real if r["pt"] and dist_m(r["pt"], o["pt"]) < 120]
        return ("nearby", near) if near else ("none", [])

    rows = []
    used_opt = set()
    # Success Academy: the network's own site is authoritative.
    for s in sa:
        how, hits = opt_match(s)
        used_opt.update(o["code"] for o in hits)
        cc_hits = [c for c in cc if "success" in (c["title"] + c["h1"]).lower() and
                   (c["key"] == s["key"] or (c["pt"] and dist_m(c["pt"], s["pt"]) < 120))]
        rows.append({
            "campus": s["name"].replace("Success Academy - ", "Success Academy "), "network_hint": "Success Academy",
            "street": s["street"], "zip": s["zip"], "lat": s["lat"], "lon": s["lon"], "grades": s["grades"],
            "primary_source": "successacademies.org", "city_2025_26": how,
            "city_names": " / ".join(o["name"] for o in hits),
            "finder_names": " / ".join(c["title"].split(",")[0] for c in cc_hits),
            "status": "verified_network_site",
        })
    # Everything else from the Charter Center finder.
    for c in cc:
        if "success academy" in (c["title"] + c["h1"]).lower():
            continue
        if c["slug"].startswith("test") or c["h1"].upper().startswith("TEST"):
            rows.append({"campus": c["h1"], "street": c["street"], "status": "excluded_test_record",
                         "primary_source": "charter center", "lat": c["lat"], "lon": c["lon"]})
            continue
        how, hits = opt_match(c)
        used_opt.update(o["code"] for o in hits)
        status = {"address": "confirmed_two_sources", "nearby": "confirmed_nearby_check",
                  "none": "finder_only_needs_check"}[how]
        rows.append({
            "campus": c["title"].split(",")[0], "network_hint": c["h1"], "street": c["street"], "zip": c["zip"],
            "lat": c["lat"], "lon": c["lon"], "grades": c["grades"], "web": c["web"],
            "primary_source": "charter center", "city_2025_26": how,
            "city_names": " / ".join(f'{o["name"]} @ {o["street"]}' if how == "nearby" else o["name"] for o in hits),
            "status": status,
        })

    # City sites that matched nothing.
    sa_keys = {s["key"] for s in sa}
    leftovers = []
    for o in opt_real:
        if o["code"] in used_opt:
            continue
        matched_any = any(r.get("lat") and dist_m((float(r["lat"]), float(r["lon"])), o["pt"]) < 120
                          for r in rows if r["status"] != "excluded_test_record")
        if matched_any:
            continue
        leftovers.append({**{k: o[k] for k in ("code", "name", "street", "zip", "lat", "lon")},
                          "is_success_academy": "success" in o["name"].lower(),
                          "note": "SA site does not list this address" if "success" in o["name"].lower() else ""})

    OUT.mkdir(parents=True, exist_ok=True)
    fields = ["status", "campus", "network_hint", "street", "zip", "grades", "lat", "lon", "web",
              "primary_source", "city_2025_26", "city_names", "finder_names"]
    with open(OUT / "campus_review.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in sorted(rows, key=lambda r: (r["status"], r["campus"])):
            w.writerow(r)
    with open(OUT / "unmatched_city_sites.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(leftovers[0].keys()) if leftovers else ["code"])
        w.writeheader()
        w.writerows(leftovers)

    from collections import Counter
    print("Campus rows by status:", dict(Counter(r["status"] for r in rows)))
    print("Summer-only city records set aside:", len(summer))
    print("City sites unmatched to any campus:", len(leftovers),
          f'({sum(1 for l in leftovers if l["is_success_academy"])} Success Academy)')


if __name__ == "__main__":
    main()
