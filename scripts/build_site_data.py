"""
Step 6: package the verified data for the web page.

Inputs : data/legal_schools.csv, data/legal_schools_excluded.csv, data/campuses.csv,
         data/campuses_under_review.csv, data/review/listings_not_mapped.csv
Outputs: data/buildings.geojson  one point per building, listing every school campus in it
         data/summary.json       headline counts, breakdowns and the not-mapped lists
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
AS_OF = "2026-10-30"

# Operator networks, grouped by school name (networks with three or more NYC schools).
NETWORKS = [
    (r"^Success Academy", "Success Academy"),
    (r"^Achievement First", "Achievement First"),
    (r"^Uncommon ", "Uncommon Schools"),
    (r"Ascend Charter School", "Ascend"),
    (r"^KIPP ", "KIPP NYC"),
    (r"^Bronx Charter School for Excellence", "Excellence Community Schools"),
    (r"^Icahn Charter", "Icahn Charter Schools"),
    (r"^Zeta Charter", "Zeta Charter Schools"),
    (r"^United Charter High School", "United Charter High Schools"),
    (r"^South Bronx Classical", "Classical Charter Schools"),
    (r"^Urban Dove", "Urban Dove Team"),
    (r"^Brilla ", "Brilla (Seton Education)"),
    (r"^Family Life Academy", "Family Life Academy"),
    (r"^Brooklyn Prospect", "Brooklyn Prospect"),
    (r"^Explore Charter", "Explore Schools"),
    (r"^Harlem Village Academy", "Harlem Village Academies"),
    (r"^DREAM Charter", "DREAM"),
    (r"^Democracy Prep", "Democracy Prep"),
    (r"^Amber Charter", "Amber Charter Schools"),
    (r"^Our World Neighborhood", "Our World Neighborhood"),
]
OTHER = "Independent and smaller networks"


def network(name):
    return next((n for pat, n in NETWORKS if re.search(pat, name)), OTHER)


def rows(p):
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    legal = rows(DATA / "legal_schools.csv")
    excluded = rows(DATA / "legal_schools_excluded.csv")
    camp = rows(DATA / "campuses.csv")
    review = rows(DATA / "campuses_under_review.csv")
    listings = rows(DATA / "review" / "listings_not_mapped.csv")
    auth = {r["school"]: r["authorizer"] for r in legal}

    # One point per building: campuses within ~11 m (4 decimal places) share a marker.
    bld = defaultdict(list)
    for c in camp:
        bld[(round(float(c["lat"]), 4), round(float(c["lon"]), 4))].append(c)
    feats = []
    for (la, lo), cs in sorted(bld.items()):
        lat = sum(float(c["lat"]) for c in cs) / len(cs)
        lon = sum(float(c["lon"]) for c in cs) / len(cs)
        feats.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]},
            "properties": {
                "borough": cs[0]["borough"],
                "district": cs[0]["district"],
                "campuses": [{
                    "school": c["school"], "authorizer": c["authorizer"], "address": c["address"],
                    "grades": c["grades"], "evidence": c["evidence"], "note": c["note"],
                    "sa": c["school"].startswith("Success Academy"),
                    "network": network(c["school"]),
                } for c in sorted(cs, key=lambda c: c["school"])],
            },
        })
    json.dump({"type": "FeatureCollection", "features": feats}, open(DATA / "buildings.geojson", "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))

    schools_by_boro = defaultdict(set)
    for c in camp:
        schools_by_boro[c["borough"]].add(c["school"])
    summary = {
        "as_of": AS_OF,
        "schools": len(legal),
        "campuses": len(camp),
        "buildings": len(bld),
        "schools_by_authorizer": dict(Counter(r["authorizer"] for r in legal)),
        "campuses_by_authorizer": dict(Counter(c["authorizer"] for c in camp)),
        "campuses_by_borough": dict(Counter(c["borough"] for c in camp)),
        "schools_with_a_campus_in_borough": {b: len(s) for b, s in schools_by_boro.items()},
        "success_academy": {"schools": sum(r["school"].startswith("Success Academy") for r in legal),
                            "campuses": sum(c["school"].startswith("Success Academy") for c in camp)},
        "under_review": review,
        "excluded_schools": excluded,
        "listings_not_mapped": [l for l in listings if l["status"] != "mapped"],
    }
    # Networks, districts and findings.
    net_s, net_c = Counter(network(r["school"]) for r in legal), Counter(network(c["school"]) for c in camp)
    summary["networks"] = sorted([{"network": n, "schools": net_s[n], "campuses": net_c[n]} for n in net_s],
                                 key=lambda r: (r["network"] == OTHER, -r["campuses"], r["network"]))
    dist = Counter((c["borough"], c["district"]) for c in camp)
    summary["campuses_by_district"] = {str(d): n for (b, d), n in dist.items()}
    multi = sum(1 for n in Counter(c["school"] for c in camp).values() if n > 1)
    shared = sum(1 for cs in bld.values() if len({c["school"] for c in cs}) > 1)
    top_d = dist.most_common(3)
    bx_bk = summary["campuses_by_borough"]["Bronx"] + summary["campuses_by_borough"]["Brooklyn"]
    sa = summary["success_academy"]
    in_net = len(legal) - net_s[OTHER]
    summary["findings"] = [
        {"figure": f"{round(100 * bx_bk / len(camp))}%", "text": f"of campuses are in the Bronx and Brooklyn ({bx_bk} of {len(camp)}). Staten Island has {summary['campuses_by_borough']['Staten Island']}."},
        {"figure": f"{round(100 * summary['schools_by_authorizer']['SUNY'] / len(legal))}%", "text": f"of schools are authorized by SUNY ({summary['schools_by_authorizer']['SUNY']} of {len(legal)}), including every Success Academy, Uncommon and Achievement First school."},
        {"figure": str(in_net), "text": f"schools belong to one of {len(NETWORKS)} networks with three or more schools; the other {net_s[OTHER]} are independent or part of smaller networks."},
        {"figure": str(sa["campuses"]), "text": f"Success Academy campuses, the largest network: {sa['schools']} schools, {round(100 * sa['campuses'] / len(camp))}% of all campuses."},
        {"figure": str(multi), "text": f"schools run more than one campus, and {shared} buildings are shared by two or more different schools."},
        {"figure": ", ".join(f"{d}" for (b, d), n in top_d), "text": "are the community school districts with the most campuses (" + "; ".join(f"District {d}, {b}: {n}" for (b, d), n in top_d) + ")."},
    ]
    json.dump(summary, open(DATA / "summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{summary['schools']} schools, {summary['campuses']} campuses, {summary['buildings']} buildings")
    print("campuses by borough:", summary["campuses_by_borough"])
    print("schools by authorizer:", summary["schools_by_authorizer"])
    print("SA:", summary["success_academy"])


if __name__ == "__main__":
    main()
