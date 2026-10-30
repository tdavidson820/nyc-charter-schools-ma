"""
Build the legal list of NYC charter schools open with students on October 30, 2026.

Definition: a public school operating under a charter granted under Article 56 of the New York State
Education Law, authorized by the Board of Regents, the SUNY Trustees, or the NYC Schools Chancellor;
open with students in the 2026-27 school year; at least one campus in the five boroughs.

Authority, by authorizer:
  SUNY           SUNY Charter Schools Institute school list (newyorkcharters.org, updated Sep 17, 2026),
                 which gives each school's 2026-27 grades and sites. Grade "0" = approved, not open.
  Board of Regents  NYSED liaison roster of Regents-authorized schools (Aug 2025), adjusted for every
                 Regents action since (NYSED "Actions Taken by the Board of Regents") and confirmed closures.
  NYC DOE        NYSED Charter Schools Directory rows authorized by NYCDOE, adjusted for Regents actions.
Outputs: data/legal_schools.csv (included) and data/legal_schools_excluded.csv (every exclusion and why).
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "sources"

BOR_ROSTER_AUG_2025 = """Access Bronx Charter School|AECI II: NYC Charter High School for Computer Engineering and Innovation|American Dream Charter School|American Dream Charter School II|Bold Charter School|Bridge Preparatory Charter School|Bronx Arts and Science Charter School|Bronx Charter School for the Arts|Brooklyn Laboratory Charter School|Brooklyn Rise Charter School|Brooklyn Urban Garden Charter School|Charter High School for Law and Social Justice|Collegiate Academy for Mathematics and Personal Awareness Charter School|Compass Charter School|Creo College Preparatory Charter School|Early College Charter School|Edmund W Gordon Brooklyn Laboratory Charter School|Emblaze Academy Charter School|Global Community Charter School|Great Oaks Charter School|Growing Up Green Charter School|Growing Up Green Charter School II|Harriet Tubman Charter School|Hebrew Language Academy Charter School 2|Hellenic Classical Charter School - Staten Island|Hellenic Classical Charter School -Park Slope|Ivy Hill Preparatory Charter School|John W Lavelle Preparatory Charter School|La Cima Charter School|Launch Expeditionary Learning Charter School|Leep Dual Language Academy Charter School|Math, Engineering and Science Academy Charter High School|Mott Hall Charter School|Neighborhood Charter School of Harlem|Neighborhood Charter School-Bronx|New American Academy Charter School (The)|New Dawn Charter High School|New Dawn Charter High School II|New Ventures Charter School|New York City Charter High School for Architecture, Engineering & Construction Industries|Northside Charter High School|Renaissance Charter School 2 (The)|Richmond Preparatory Charter School|Rosalyn Yalow Charter School|School In the Square Public Charter School|South Bronx Classical Charter School|South Bronx Classical Charter School II|South Bronx Classical Charter School III|South Bronx Classical Charter School IV|South Bronx Community Charter High School|South Bronx Early College Academy Charter School|Staten Island Hebrew Public Charter School|United Charter High School for Advanced Math and Science II|United Charter High School for Advanced Math and Science III|United Charter High School for Advanced Math and Science IV|United Charter High School for the Humanities II|United Charter High School for the Humanities IV|Unity Preparatory Charter School of Brooklyn|Urban Dove Team Charter School|Urban Dove Team Charter School II|Whin Music Community Charter School|Williamsburg Charter High School""".split("|")

BOR_EXCLUDE = {
    "Harriet Tubman Charter School": ("closed", "Closed end of June 2026; charter expired June 2026 with no renewal (NYSED 2025-26 eligible renewal list; NYSED Regents actions; News 12 Bronx, May 21, 2026)."),
    "Collegiate Academy for Mathematics and Personal Awareness Charter School": ("merged", "Renamed MESA Charter High School: East New York, then merged into Math, Engineering and Science Academy Charter High School (Regents, March 9-10, 2026)."),
}
OTHER_EXCLUSIONS = [  # schools in the state directory that are not separate open schools in 2026-27
    ("South Bronx Classical Charter School VI", "Board of Regents", "not_open", "Approved 2025 (state directory) but absent from the Regents roster of operating schools and from the Charter Center's list of fall 2026 openings."),
    ("Achievement First Charter School 11", "SUNY", "not_open", "Not on SUNY's 2026-27 school list."),
    ("Uncommon New York City Charter School #1", "SUNY", "not_open", "Not on SUNY's 2026-27 school list."),
    ("Harbor Science and Arts Charter School", "SUNY", "not_operating", "Not on SUNY's 2026-27 school list; SUNY's school page has been removed and the school's website (hsacs.org, checked Oct 30, 2026) now shows only a contact for student records requests. Treated as closed after 2025-26."),
    ("Explore Charter School / Empower / Enrich / Exceed / Excel (5 charters)", "SUNY", "consolidated", "SUNY's 2026-27 list shows three Explore schools (Canarsie, Crown Heights, Flatbush). Five state-directory charters correspond to these three; two are not separate schools in 2026-27."),
    ("Success Academy Charter School - Bronx 5 Lower", "SUNY", "transferred", "Charter transferred to Strive Charter School (SUNY approval; Regents returned it Jan 2026; SUNY maintained approval; Strive opened Sept 2026; union lawsuit pending)."),
]
# Operating schools missing from SUNY's 2026-27 NYC list, added on stronger evidence.
SUNY_ADDITIONS = [
    {"school": "Manhattan Charter School", "authorizer": "SUNY", "district": "Manhattan 1", "grades_2026_27": "K-5",
     "authorizer_sites": "100 Attorney Street, New York",
     "source": "SUNY renewal report (Feb 2024): charter renewed through June 30, 2029; school website lists MCS I at 100 Attorney St",
     "note": "Missing from SUNY's 2026-27 NYC school list, but renewed by SUNY through June 2029 and listed as operating by the school, the Charter Center finder and the city's 2025-26 site list."},
]
NAME_CHANGES = [
    ("Boys/Girls Preparatory Charter Schools (Public Prep, 4 charters)", "Bronx Charter School for Excellence 6, 7, 8, 9",
     "SUNY's 2026-27 list shows Bronx Excellence 6-9 at Public Prep's buildings (681 Kelly St, 192 E 151st St, 263 E 203rd St) with grades matching Public Prep's March 2026 revision notice."),
    ("Brooklyn Prospect Charter School - CSD 13, 13.2, 15, 15.2", "Brooklyn Prospect Bed-Stuy Clinton Hill, Downtown, Sunset Yards, Windsor Terrace Campuses", "SUNY list names each charter by campus."),
    ("Math, Engineering, and Science Academy Charter High School 2", "MESA Charter High School: South Brooklyn", "SUNY list."),
    ("Zeta Charter School - Queens 2", "Zeta Charter School - Queens Flushing", "SUNY list."),
    ("Great Oaks Kathleen Sherry Charter School", "Great Oaks Charter School", "Regents roster."),
]


def main() -> None:
    included, excluded = [], []
    for name, district, grades, sites in (l.rstrip("\n").split("\t") for l in open(SRC / "suny_csi_nyc_2026-10-30.tsv", encoding="utf-8")):
        g = grades.split(" / ")[0]
        if g == "0":
            if name == "Next Generation Charter School":
                excluded.append({"school": name, "authorizer": "SUNY", "reason": "merged",
                                 "detail": "Merged with Nuasin Next Generation Charter School in July 2025 (Regents, May 2025); counted once under Nuasin Next Generation. SUNY shows no grades for Next Generation in 2026-27."})
                continue
            excluded.append({"school": name, "authorizer": "SUNY", "reason": "not_open",
                             "detail": "On SUNY's list with no grades for 2026-27 (approved, not yet open)."})
            continue
        note = "Opened Sept 2026 via charter transfer from Success Academy Bronx 5 Lower; Regents objected; union lawsuit pending." if name == "Strive Charter School" else ""
        included.append({"school": name, "authorizer": "SUNY", "district": district, "grades_2026_27": g,
                         "authorizer_sites": sites, "source": "SUNY Charter Schools Institute list (updated Sep 17, 2026)", "note": note})
    included.extend(SUNY_ADDITIONS)
    for name in BOR_ROSTER_AUG_2025:
        if name in BOR_EXCLUDE:
            reason, detail = BOR_EXCLUDE[name]
            excluded.append({"school": name, "authorizer": "Board of Regents", "reason": reason, "detail": detail})
            continue
        included.append({"school": name, "authorizer": "Board of Regents", "district": "", "grades_2026_27": "", "authorizer_sites": "",
                         "source": "NYSED Regents roster (Aug 2025) + Regents actions through May 2026", "note": ""})
    for r in (l.rstrip("\n").split("\t") for l in open(SRC / "nysed_directory_nyc.tsv", encoding="utf-8")):
        if r[4].upper() == "NYCDOE":
            included.append({"school": r[0], "authorizer": "NYC DOE", "district": f"{r[2]} {r[1]}", "grades_2026_27": "",
                             "authorizer_sites": "", "source": "NYSED directory + Regents actions through May 2026", "note": ""})
    for school, auth, reason, detail in OTHER_EXCLUSIONS:
        excluded.append({"school": school, "authorizer": auth, "reason": reason, "detail": detail})
    for old, new, detail in NAME_CHANGES:
        excluded.append({"school": old, "authorizer": "", "reason": "renamed", "detail": f"Counted under '{new}'. {detail}"})

    with open(ROOT / "data" / "legal_schools.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(included[0].keys())); w.writeheader(); w.writerows(included)
    with open(ROOT / "data" / "legal_schools_excluded.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(excluded[0].keys())); w.writeheader(); w.writerows(excluded)
    from collections import Counter
    c = Counter(r["authorizer"] for r in included)
    print("Included:", len(included), dict(c))
    print("Excluded/explained:", len(excluded), dict(Counter(r["reason"] for r in excluded)))


if __name__ == "__main__":
    main()
