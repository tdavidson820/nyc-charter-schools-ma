"""
Data integrity checks. Runs in GitHub Actions before every deploy; any failure stops the deploy.

Checks that the published files agree with each other and with the reviewed counts, that every campus
has evidence and valid coordinates inside its borough, that nothing is duplicated, and that the
Charter Center reconciliation accounts for every finder listing.

Usage: python scripts/check_data.py
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

from shapely.geometry import Point, shape

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# The reviewed totals (see VALIDATION.md). Change these only after a reviewed data refresh.
EXPECTED = {"schools": 287, "campuses": 415, "buildings": 383}
AUTHORIZERS = {"SUNY", "Board of Regents", "NYC DOE"}
BOROUGHS = {"Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island"}

failures: list[str] = []


def check(ok: bool, msg: str) -> None:
    print(("PASS  " if ok else "FAIL  ") + msg)
    if not ok:
        failures.append(msg)


def rows(p: Path) -> list[dict]:
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f))


legal = rows(DATA / "legal_schools.csv")
excluded = rows(DATA / "legal_schools_excluded.csv")
camp = rows(DATA / "campuses.csv")
review = rows(DATA / "campuses_under_review.csv")
recon = rows(DATA / "review" / "count_reconciliation.csv")
summary = json.load(open(DATA / "summary.json", encoding="utf-8"))
buildings = json.load(open(DATA / "buildings.geojson", encoding="utf-8"))

# Counts
school_names = [r["school"] for r in legal]
check(len(legal) == EXPECTED["schools"], f"{len(legal)} schools (expected {EXPECTED['schools']})")
check(len(camp) == EXPECTED["campuses"], f"{len(camp)} campuses (expected {EXPECTED['campuses']})")
check(len(buildings["features"]) == EXPECTED["buildings"], f"{len(buildings['features'])} buildings (expected {EXPECTED['buildings']})")
check(summary["schools"] == len(legal) and summary["campuses"] == len(camp) and summary["buildings"] == len(buildings["features"]),
      "summary.json agrees with the CSV and GeoJSON files")
check(sum(len(f["properties"]["campuses"]) for f in buildings["features"]) == len(camp), "every campus appears in exactly one building marker")

# Schools
check(len(set(school_names)) == len(school_names), "no duplicate school names")
check(all(r["authorizer"] in AUTHORIZERS for r in legal), "every school has a valid authorizer")
check(not (set(school_names) & {r["school"] for r in excluded}), "no school is both counted and excluded")
check(all(r["reason"] and r["detail"] for r in excluded), "every exclusion has a reason and an explanation")
by_school = Counter(c["school"] for c in camp)
check(set(by_school) == set(school_names), "every counted school has at least one campus, and every campus belongs to a counted school")

# Campuses
keys = [(c["school"], round(float(c["lat"]), 4), round(float(c["lon"]), 4)) for c in camp]
check(len(set(keys)) == len(keys), "no school is mapped twice at the same building")
check(all(c["evidence"].strip() for c in camp), "every campus lists its evidence")
check(all(("+" in c["evidence"]) or ("Site correction" in c["evidence"]) for c in camp), "every campus cites at least two sources")
check(all(c["borough"] in BOROUGHS and c["district"] for c in camp), "every campus has a borough and community school district")
check(not review, "no campus is left under review")

# Coordinates fall inside the borough the campus is assigned to (allowing 300 m for shoreline simplification).
boros = {f["properties"]["name"]: shape(f["geometry"]) for f in json.load(open(DATA / "boroughs.geojson"))["features"]}
outside = [c["school"] + " @ " + c["address"] for c in camp
           if boros[c["borough"]].distance(Point(float(c["lon"]), float(c["lat"]))) > 0.003]
check(not outside, "every campus lies inside its borough" + (f": {outside[:3]}" if outside else ""))

# Reconciliation with the Charter Center finder
finder_rows = [r for r in recon if r["finder_listing"]]
check(len(finder_rows) == 420, f"all {len(finder_rows)} Charter Center finder listings are accounted for")
check(all(r["outcome"] != "UNMATCHED" for r in recon), "no finder listing is left unmatched")
check(all(r["reason"] for r in recon if r["outcome"] == "not a campus"), "every finder listing that is not a campus has a reason")

print()
if failures:
    print(f"{len(failures)} check(s) failed.")
    sys.exit(1)
print("All checks passed.")
