"""
Build the campus layer: every campus (a legal school operating at a building) of the 286 legal schools.

Location authority:
  SUNY schools          SUNY Charter Schools Institute 2026-27 site list (the authorizer). Other sources
                        (Charter Center, city 2025-26 list, Success Academy site) corroborate and supply
                        coordinates; NYC GeoSearch geocodes sites no other source has.
  Regents / NYC DOE     No authorizer site list is published. A campus is verified when the Charter Center
                        finder and the city's 2025-26 list both place the same school at the building.
Held for review (listed, not mapped): any campus where sources conflict or only one source supports it.
"""
from __future__ import annotations

import csv
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from shapely.geometry import Point, shape

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from reconcile import norm_addr  # noqa: E402

DATA, SRC = ROOT / "data", ROOT / "data" / "sources"

# Charter Center listing (by its h1 school name, lowercase) -> legal school, for Regents and NYC DOE schools.
CROSSWALK = [
    (r"^access bronx", "Access Bronx Charter School"),
    (r"^aeci 2", "AECI II: NYC Charter High School for Computer Engineering and Innovation"),
    (r"^american dream charter school ii", "American Dream Charter School II"),
    (r"american dream", "American Dream Charter School"),
    (r"^bold charter", "Bold Charter School"),
    (r"^bridge preparatory", "Bridge Preparatory Charter School"),
    (r"^bronx arts and science", "Bronx Arts and Science Charter School"),
    (r"^bronx charter school for the arts", "Bronx Charter School for the Arts"),
    (r"^edmund w\. gordon", "Edmund W Gordon Brooklyn Laboratory Charter School"),
    (r"^brooklyn laboratory", "Brooklyn Laboratory Charter School"),
    (r"^brooklyn rise", "Brooklyn Rise Charter School"),
    (r"^brooklyn urban garden", "Brooklyn Urban Garden Charter School"),
    (r"law and social justice", "Charter High School for Law and Social Justice"),
    (r"^compass charter", "Compass Charter School"),
    (r"^creo college", "Creo College Preparatory Charter School"),
    (r"^nicotra early college", "Early College Charter School"),
    (r"^emblaze", "Emblaze Academy Charter School"),
    (r"^global community", "Global Community Charter School"),
    (r"^great oaks", "Great Oaks Charter School"),
    (r"^growing up green ii ", "Growing Up Green Charter School II"),
    (r"^growing up green i ", "Growing Up Green Charter School"),
    (r"^hebrew language academy charter school 2", "Hebrew Language Academy Charter School 2"),
    (r"^hebrew language academy charter school \(hla\)", "Hebrew Language Academy Charter School"),
    (r"^hellenic classical charter schools-park slope", "Hellenic Classical Charter School -Park Slope"),
    (r"^hellenic classical charter schools - staten island", "Hellenic Classical Charter School - Staten Island"),
    (r"^ivy hill", "Ivy Hill Preparatory Charter School"),
    (r"^john w\. lavelle", "John W Lavelle Preparatory Charter School"),
    (r"^la cima", "La Cima Charter School"),
    (r"^launch expeditionary", "Launch Expeditionary Learning Charter School"),
    (r"^leep dual", "Leep Dual Language Academy Charter School"),
    (r"^mesa charter high school", "Math, Engineering and Science Academy Charter High School"),
    (r"^mott hall charter", "Mott Hall Charter School"),
    (r"^neighborhood charter school harlem", "Neighborhood Charter School of Harlem"),
    (r"^neighborhood charter school bronx", "Neighborhood Charter School-Bronx"),
    (r"^new american academy", "New American Academy Charter School (The)"),
    (r"^new dawn charter high school ii", "New Dawn Charter High School II"),
    (r"^new dawn charter high school", "New Dawn Charter High School"),
    (r"^new ventures", "New Ventures Charter School"),
    (r"construction industries \(aeci 1\)", "New York City Charter High School for Architecture, Engineering & Construction Industries"),
    (r"^northside", "Northside Charter High School"),
    (r"^renaissance charter school 2", "Renaissance Charter School 2 (The)"),
    (r"^renaissance charter school$", "Renaissance Charter School"),
    (r"^richmond preparatory", "Richmond Preparatory Charter School"),
    (r"^rosalyn yalow", "Rosalyn Yalow Charter School"),
    (r"^school in the square", "School In the Square Public Charter School"),
    (r"^south bronx classical charter school iv$", "South Bronx Classical Charter School IV"),
    (r"^south bronx classical charter school iii$", "South Bronx Classical Charter School III"),
    (r"^south bronx classical charter school ii$", "South Bronx Classical Charter School II"),
    (r"^south bronx classical charter school$", "South Bronx Classical Charter School"),
    (r"^south bronx community charter high", "South Bronx Community Charter High School"),
    (r"^south bronx early college", "South Bronx Early College Academy Charter School"),
    (r"^staten island hebrew", "Staten Island Hebrew Public Charter School"),
    (r"^united charter high school for advanced math and science (ii)$", "United Charter High School for Advanced Math and Science II"),
    (r"^united charter high school for advanced math and science lll$", "United Charter High School for Advanced Math and Science III"),
    (r"^united charter high school for advanced math and science iv$", "United Charter High School for Advanced Math and Science IV"),
    (r"^united charter high school for the humanities ii$", "United Charter High School for the Humanities II"),
    (r"^united charter high school for the humanities iv$", "United Charter High School for the Humanities IV"),
    (r"^unity preparatory", "Unity Preparatory Charter School of Brooklyn"),
    (r"^urban dove team charter school ii$", "Urban Dove Team Charter School II"),
    (r"^urban dove team charter school$", "Urban Dove Team Charter School"),
    (r"^whin music", "Whin Music Community Charter School"),
    (r"^williamsburg charter high", "Williamsburg Charter High School"),
    # NYC DOE
    (r"^bronx academy of promise", "Bronx Academy of Promise Charter School"),
    (r"^bronx community charter school$", "Bronx Community Charter School"),
    (r"^bronx global learning institute", "Bronx Global Learning Institute for Girls Charter School, The Shirley Rodriguez-Remeneski School"),
    (r"^brooklyn charter school$", "Brooklyn Charter School (The)"),
    (r"^brooklyn scholars", "Brooklyn Scholars Charter School"),
    (r"^challenge preparatory", "Challenge Preparatory Charter School"),
    (r"^community roots", "Community Roots Charter School"),
    (r"^cultural arts academy", "Cultural Arts Academy Charter School At Spring Creek"),
    (r"izquierdo", "Dr. Richard Izquierdo Health and Science Charter School"),
    (r"^ember charter", "Ember Charter School for Mindful Education, Innovation and Transformation"),
    (r"^equality charter", "Equality Charter School"),
    (r"equity project", "Equity Project Charter School (The)"),
    (r"^future leaders", "Future Leaders Institute Charter School"),
    (r"promise academy ii", "Harlem Children's Zone Promise Academy II Charter School"),
    (r"promise academy i ", "Harlem Children's Zone Promise Academy Charter School"),
    (r"^hyde leadership", "Hyde Leadership Charter School - Brooklyn"),
    (r"^imagine me", "Imagine Me Leadership Charter School"),
    (r"^innovation charter high", "Innovation Charter High School"),
    (r"^inwood academy", "Inwood Academy for Leadership Charter School"),
    (r"^jvl wildcat", "John V. Lindsay Wildcat Academy Charter School"),
    (r"^kipp academy (elementary|middle)|^kipp nyc college prep high school - upper", "KIPP Academy Charter School"),
    (r"^mott haven academy", "Mott Haven Charter School"),
    (r"^new heights academy", "New Heights Academy Charter School"),
    (r"^new york french-american", "New York French-American Charter School"),
    (r"^opportunity charter", "Opportunity Charter School"),
    (r"^peninsula preparatory", "Peninsula Preparatory Academy Charter School"),
    (r"^pharos", "Pharos Academy Charter School"),
    (r"^riverton street", "Riverton Street Charter School"),
    (r"^rochdale", "Rochdale Early Advantage Charter School"),
    (r"international cultures and the arts", "South Bronx Charter School for International Cultures and the Arts"),
    (r"^st hope", "St. Hope Leadership Academy Charter School"),
    (r"^summit academy", "Summit Academy Charter School"),
    (r"^voice charter", "VOICE Charter School of New York"),
]
# SUNY site-list entries contradicted by newer, dated evidence: the campus is mapped at the corrected address.
SITE_CORRECTIONS = {
    ("Earl Monroe New Renaissance Basketball Charter School", "1617 PARKVIEW AV"): ("647 Elton Ave",
        "Moved: NY1 (Oct 16, 2026) reports operations fully moved to the new building in September 2026; Charter Center lists 647 Elton Ave. SUNY's list (Sep 17, 2026) still shows the former site, 1617 Parkview Ave."),
    ("Success Academy Charter School - Harlem 4", "461 W 131 ST"): ("509 West 129th Street",
        "Hamilton Heights Middle School (opened 2022). Success Academy's own site lists it at 509 W 129th St, Floor 3; SUNY, the Charter Center and the city's 2025-26 list show 461 W 131st St, about 160 m away."),
}
# Regents / NYC DOE campuses held on the first pass (one source), confirmed in step 3 by the school or a dated document.
RESOLVED = {
    ("AECI II: NYC Charter High School for Computer Engineering and Innovation", "1000 WALTON AV"):
        "Charter Center + building developer (Barone Management: former All Hallows HS, 111 E 164th St / 1000 Walton Ave, AECI occupancy began 2026)",
    ("American Dream Charter School II", "652 W 187 ST"):
        "Charter Center + Board of Regents charter revision (Apr 2025: converted to grades 9-12, first class Aug 2026, facility 652 W 187th St) + school website (high school opening Fall 2026)",
    ("Bold Charter School", "1093 SOUTHERN BL"):
        "Charter Center + school website (2026-27: kindergarten at 1093 Southern Blvd, grades 1-8 at 1909 Daly Ave)",
    ("Charter High School for Law and Social Justice", "200 W TREMONT AV"):
        "Charter Center (grades 6-8) + Board of Regents revision (Jun 2024: grades 6-8 added) + building developer (Barone Management: 200 W Tremont Ave built for the school's middle school)",
    ("Community Roots Charter School", "101 PARK AV"):
        "Charter Center + school website (middle school campus) + NYC DOE re-siting notice for building K265, 101 Park Ave, effective 2026-27",
    ("Equality Charter School", "801 BARTHOLDI ST"):
        "Charter Center (high school) + school website (High School & Elementary School: 801 Bartholdi St) + building purchase (Commercial Observer, Sep 2026)",
    ("VOICE Charter School of New York", "36-49 11 ST"):
        "Charter Center + school website (Upper Elementary Campus, grades 3-5)",
}
# Every Charter Center or Success Academy listing that is not a campus of record, and why.
LISTING_RESOLUTION = {
    "647 ELTON AV": ("mapped", "Earl Monroe's new building; mapped as its campus (see site corrections)."),
    "509 W 129 ST": ("mapped", "Success Academy Harlem 4's Hamilton Heights Middle School; mapped (see site corrections)."),
    "100 ATTORNEY ST": ("mapped", "Manhattan Charter School (MCS I); mapped. School was missing from SUNY's 2026-27 list but is renewed through June 2029."),
    "3515 BAINBRIDGE AV": ("stale", "International Leadership's middle school opened here in Sept 2023 (Norwood News), but neither SUNY's 2026-27 list nor the city's 2025-26 list includes it; SUNY lists the school at 3030 Riverdale Ave and 306 W 232nd St."),
    "26 BROADWAY": ("stale", "NYC Charter School of the Arts: SUNY's 2026-27 list gives 241 Water St (mapped). 26 Broadway was its 2025-26 site."),
    "31-20 37 ST": ("stale", "Urban Dove Team III: SUNY's 2026-27 list gives 82-06 Northern Blvd (mapped). 31-20 37th St was its 2025-26 site."),
    "136-25 218 ST": ("not_open", "Success Academy Laurelton Middle School: Success Academy's page says it opens Fall 2027."),
    "7801 BAY PKY": ("not_open", "Success Academy Bensonhurst Middle School: Success Academy's page says it opens for 2027-28."),
}
UNRESOLVED_REASON = {}
# Second confirmation for SUNY sites that no other captured source lists (checked Oct 30, 2026).
EXTRA_CONFIRMATION = {
    "200 E 138 ST": "KIPP NYC school directory (kippnyc.org/schools): KIPP NYC College Prep Lower School, grades 9-10, 200 E 138th St",
    "306 W 232 ST": "SUNY school page: middle school, grades 6-8, 306 W 232nd St",
    "82-06 NORTHERN BL": "SUNY school page: site 'UD Team III', 82-06 Northern Blvd",
}
# Charter Center addresses for Regents / NYC DOE schools contradicted by the school and the state.
NONSUNY_CORRECTIONS = {
    ("New Ventures Charter School", "2245 RICHMOND AV"): ("1441 South Avenue",
        "School network website (Integration Charter Schools: 1441 South Ave) + NYSED renewal site visit (Mar 2025: 1441 South Ave, 4th Floor). Charter Center lists 2245 Richmond Ave, which is Richmond Prep's building; the city's 2025-26 list gives 1 Teleport Dr, the other entrance to the same Corporate Commons complex."),
}


# GeoSearch returned a different building for these three; coordinates come from the named source instead.
GEO_OVERRIDE = {
    "101 E 150 ST": (40.820671, -73.929353, "Success Academy site (GeoSearch matched 150 E 150th St)"),
    "217 N 10 ST": (40.718300, -73.953570, "NYC GeoSearch for 215 N 10th St, the city's address for this building (217 matched 5 N 10th St)"),
    "528 W 162 ST": (40.836442, -73.940845, "City 2025-26 site list (GeoSearch matched 528 W 189th St)"),
}


def dist_m(a, b):
    return math.hypot((a[0] - b[0]) * 111_000, (a[1] - b[1]) * 84_000)


def toks(s):
    s = s.upper().replace("'", "")
    for a, b in (("INNOV.", "INNOVATION"), ("AGR,ENG", "ARCHITECTURE ENGINEERING"), ("CONST", "CONSTRUCTION"), ("ACAD.", "ACADEMY ")):
        s = s.replace(a, b)
    stop = set("CHARTER SCHOOL SCHOOLS SCH CS THE OF FOR AND NYC NY NEW YORK ACADEMY ACAD PREP PREPARATORY ELEMENTARY MIDDLE HIGH ES MS HS ELEM".split())
    return {t for t in re.findall(r"[A-Z0-9]+", s) if t not in stop and len(t) > 1}


def main():
    legal = list(csv.DictReader(open(DATA / "legal_schools.csv", encoding="utf-8")))
    by_name = {r["school"]: r for r in legal}
    cc = [l.rstrip("\n").split("\t") for l in open(SRC / "charter_center_finder_2026-10-30.tsv", encoding="utf-8")]
    cc = [c for c in cc if not (c[0].startswith("test") or c[2].upper().startswith("TEST"))]
    city = [l.rstrip("\n").split("\t") for l in open(SRC / "nyc_doe_transportation_sites_2025-26.tsv", encoding="utf-8")]
    city = [c for c in city if not (re.match(r"^84[MXKQR]\d{3} ", c[1]) or "SUMMER" in c[1].upper())]
    sa = [l.rstrip("\n").split("\t") for l in open(SRC / "successacademy_2026-10-30.tsv", encoding="utf-8")]
    geo = {norm_addr(r[0]): (float(r[2]), float(r[3]), r[4]) for r in (l.rstrip("\n").split("\t") for l in open(SRC / "nyc_geosearch_2026-10-30.tsv", encoding="utf-8"))}

    # Address index of every point from every source.
    pts = defaultdict(list)
    for c in cc: pts[norm_addr(c[5])].append(("Charter Center", float(c[8]), float(c[9]), c[2]))
    for c in city: pts[norm_addr(c[2])].append(("City 2025-26", float(c[4]), float(c[5]), c[1]))
    for s in sa: pts[norm_addr(s[2])].append(("Success Academy site", float(s[7]), float(s[8]), s[1]))
    allpts = [(k, p) for k, v in pts.items() for p in v]

    campuses, held = [], []
    # --- SUNY schools: authorizer site list ---
    for s in (r for r in legal if r["authorizer"] == "SUNY"):
        seen = set()
        for site in s["authorizer_sites"].split(" | "):
            street = site.split(",")[0].strip().rstrip(",")
            key = norm_addr(street)
            if not key or key in seen:
                continue
            seen.add(key)
            corr_note = ""
            if (s["school"], key) in SITE_CORRECTIONS:
                street, corr_note = SITE_CORRECTIONS[(s["school"], key)]
                key = norm_addr(street)
            hits = pts.get(key, [])
            if hits:
                lat, lon = hits[0][1], hits[0][2]
                geonote = ""
            elif key in geo:
                lat, lon, geonote = geo[key][0], geo[key][1], "Coordinates from NYC GeoSearch (" + geo[key][2] + ")"
            else:
                raise SystemExit(f"No coordinates for {s['school']} @ {street}")
            near = sorted({p[0] for k, p in allpts if dist_m((lat, lon), (p[1], p[2])) < 120})
            rec = {"school": s["school"], "authorizer": "SUNY", "address": street, "lat": lat, "lon": lon,
                   "grades": s["grades_2026_27"], "evidence": "SUNY 2026-27 site list" + (" + " + ", ".join(near) if near else ""),
                   "note": corr_note or geonote}
            if corr_note:
                rec["evidence"] = "Site correction (see note) + " + ", ".join(near)
            campuses.append(rec)

    # --- Regents / NYC DOE schools: Charter Center listing + city corroboration ---
    nonsuny = {r["school"] for r in legal if r["authorizer"] != "SUNY"}
    assigned = defaultdict(list)
    unassigned = []
    for c in cc:
        h1 = c[2].lower().strip()
        school = next((sch for pat, sch in CROSSWALK if re.search(pat, h1)), None)
        if school:
            assert school in nonsuny, school
            assigned[school].append(c)
        else:
            unassigned.append(c)
    for school, rows in assigned.items():
        seen = []
        for c in rows:
            pt = (float(c[8]), float(c[9]))
            if any(dist_m(pt, q) < 40 for q in seen):
                continue  # same school, same building (e.g. two grade spans in one building)
            seen.append(pt)
            nm = toks(school) | toks(c[2])
            corro = [x for x in city if (norm_addr(x[2]) == norm_addr(c[5]) or dist_m(pt, (float(x[4]), float(x[5]))) < 120) and (nm & toks(x[1]))]
            rec = {"school": school, "authorizer": by_name[school]["authorizer"], "address": c[5].strip().rstrip(","),
                   "lat": pt[0], "lon": pt[1], "grades": "", "evidence": "", "note": ""}
            if (school, norm_addr(c[5])) in NONSUNY_CORRECTIONS:
                rec["address"], rec["evidence"] = NONSUNY_CORRECTIONS[(school, norm_addr(c[5]))]
                campuses.append(rec)
            elif corro:
                rec["evidence"] = "Charter Center finder + City 2025-26 (" + corro[0][1] + ")"
                campuses.append(rec)
            elif (school, norm_addr(c[5])) in RESOLVED:
                rec["evidence"] = RESOLVED[(school, norm_addr(c[5]))]
                campuses.append(rec)
            elif (school, norm_addr(c[5])) in UNRESOLVED_REASON:
                held.append({**rec, "evidence": "Charter Center finder only", "reason": UNRESOLVED_REASON[(school, norm_addr(c[5]))]})
            else:
                held.append({**rec, "evidence": "Charter Center finder only",
                             "reason": "Not in the city's 2025-26 site list under this school's name; needs confirmation from the school."})

    # --- Listings that belong to no campus of record ---
    def near_campus(pt):
        return any(dist_m(pt, (c["lat"], c["lon"])) < 120 for c in campuses + held)
    camp_keys = {norm_addr(c["address"]) for c in campuses + held}
    unassigned_all = [c for c in unassigned if norm_addr(c[5]) in LISTING_RESOLUTION or not near_campus((float(c[8]), float(c[9])))]
    sa_unmatched = [s for s in sa if norm_addr(s[2]) in LISTING_RESOLUTION or (norm_addr(s[2]) not in camp_keys and not near_campus((float(s[7]), float(s[8]))))]
    orphans = [c for c in unassigned_all if LISTING_RESOLUTION.get(norm_addr(c[5]), ("",))[0] != "mapped" and norm_addr(c[5]) not in camp_keys]
    sa_orphans = [s for s in sa_unmatched if LISTING_RESOLUTION.get(norm_addr(s[2]), ("",))[0] != "mapped" and norm_addr(s[2]) not in camp_keys]

    # Every legal school accounted for?
    have = Counter(c["school"] for c in campuses)
    held_only = sorted({h["school"] for h in held} - set(have))
    none_at_all = sorted(set(by_name) - set(have) - set(held_only))

    for rec in campuses:
        k = norm_addr(rec["address"])
        if k in EXTRA_CONFIRMATION:
            rec["evidence"] += " + " + EXTRA_CONFIRMATION[k]

    # Plot every campus at its NYC GeoSearch (city geocoder) point; flag any source point more than 150 m away.
    geoall = {norm_addr(r[0]): (float(r[3]), float(r[4])) for r in (l.rstrip("\n").split("\t") for l in open(SRC / "nyc_geosearch_all_2026-10-30.tsv", encoding="utf-8"))}
    for k, (la, lo, why) in GEO_OVERRIDE.items():
        geoall[k] = (la, lo)
    flags = []
    for rec in campuses + held:
        key = norm_addr(rec["address"])
        if key not in geoall:
            raise SystemExit(f"Not geocoded: {rec['address']}")
        g = geoall[key]
        srcpts = [(p[0], dist_m(g, (p[1], p[2]))) for p in pts.get(key, [])] + [("original", dist_m(g, (rec["lat"], rec["lon"])))]
        worst = max(d for _, d in srcpts)
        rec["lat"], rec["lon"] = g
        rec["note"] = "; ".join(x for x in [GEO_OVERRIDE[key][2] if key in GEO_OVERRIDE else "", rec.get("note", "") if "GeoSearch" not in rec.get("note", "") else ""] if x)
        if worst > 150:
            flags.append((rec["school"], rec["address"], [(n, round(d)) for n, d in srcpts if d > 150]))
    EXPLAIN = {
        "341 39 ST": "City record longitude typo (-73.007 for -74.007); other city records at this address agree with the geocode.",
        "3000 AV X": "City record for Success Academy has a transposed longitude (-73.974 for -73.937); city's own UCHS III record, Success Academy site and Charter Center agree with the geocode.",
        "1475 MACOMBS RD": "City point is about 1.8 km south of the address; Charter Center and the geocode agree, consistent with neighboring 1504 Macombs Rd.",
        "787 LAFAYETTE AV": "Success Academy site point is about 900 m off; Charter Center and the city agree with the geocode.",
    }
    with open(DATA / "review" / "coordinate_checks.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["school", "address", "sources_over_150m_from_geocode", "resolution"])
        for sch, addr, bad in flags:
            k = norm_addr(addr)
            res = EXPLAIN.get(k) or (GEO_OVERRIDE[k][2] if k in GEO_OVERRIDE else "Same building; difference of 150-270 m is frontage geocode vs building centroid. Geocode kept.")
            w.writerow([sch, addr, "; ".join(f"{n} {d} m" for n, d in bad), res])
    print("Source coordinates > 150 m from geocode:", len(flags))
    for f_ in flags: print("  ", f_)

    # Borough and district from coordinates.
    boros = [(f["properties"]["name"], shape(f["geometry"])) for f in json.load(open(DATA / "boroughs.geojson"))["features"]]
    dists = [(f["properties"]["district"], shape(f["geometry"])) for f in json.load(open(DATA / "districts.geojson"))["features"]]
    for rec in campuses + held:
        p = Point(rec["lon"], rec["lat"])
        rec["borough"] = next((b for b, g in boros if g.contains(p)), None) or min(boros, key=lambda bg: bg[1].distance(p))[0]
        rec["district"] = next((d for d, g in dists if g.contains(p)), "")
        rec["lat"], rec["lon"] = round(rec["lat"], 6), round(rec["lon"], 6)

    fields = ["school", "authorizer", "address", "borough", "district", "grades", "lat", "lon", "evidence", "note"]
    with open(DATA / "campuses.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore"); w.writeheader()
        w.writerows(sorted(campuses, key=lambda r: (r["borough"], r["school"])))
    with open(DATA / "campuses_under_review.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields + ["reason"], extrasaction="ignore"); w.writeheader()
        w.writerows(sorted(held, key=lambda r: r["school"]))
        extra = [(c[2], c[5], "Charter Center finder") for c in orphans] + [(x[1], x[2], "Success Academy site") for x in sa_orphans]
        unres = [e for e in extra if norm_addr(e[1]) not in LISTING_RESOLUTION]
        for name, addr, src in unres:
            w.writerow({"school": name, "address": addr, "evidence": src + " only",
                        "reason": "Listing at an address its school's authorizer does not list for 2026-27; not yet resolved."})
    with open(DATA / "review" / "listings_not_mapped.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["listing", "address", "source", "status", "resolution"])
        for name, addr, src in [(c[2], c[5], "Charter Center finder") for c in unassigned_all] + [(x[1], x[2], "Success Academy site") for x in sa_unmatched]:
            st, why = LISTING_RESOLUTION.get(norm_addr(addr), ("unresolved", ""))
            w.writerow([name, addr, src, st, why])

    bldgs = {(round(c["lat"], 4), round(c["lon"], 4)) for c in campuses}
    print("Legal schools:", len(legal))
    print("Verified campuses:", len(campuses), "| buildings:", len(bldgs), "| by authorizer:", dict(Counter(c["authorizer"] for c in campuses)))
    print("Held campuses:", len(held), "| orphan listings:", len(orphans), "| SA-site-only:", len(sa_orphans))
    print("Schools with a verified campus:", len(have))
    print("Schools with only held campuses:", held_only)
    print("Schools with no campus found:", none_at_all)
    print("\nOrphan listings:"); [print("  ", c[2], "@", c[5]) for c in orphans]
    print("SA-site-only:"); [print("  ", s[1], "@", s[2]) for s in sa_orphans]


if __name__ == "__main__":
    main()
