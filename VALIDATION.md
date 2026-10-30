# Validation report

Data as of **October 30, 2026** (the 2026–27 school year). This report explains what was counted, where every number comes from, and every judgment call made along the way.

## Result

| | Count |
|---|---|
| Charter schools operating in New York City | **287** |
| Campuses (a school operating in a building) | **415** |
| Buildings those campuses occupy | 383 |
| Campuses under review, not mapped | **0** |
| Success Academy | 38 schools on 54 campuses |

| Authorizer | Schools | Campuses |
|---|---|---|
| SUNY Board of Trustees | 192 | 285 |
| NYS Board of Regents | 60 | 75 |
| NYC Schools Chancellor | 35 | 55 |

| Borough | Campuses | Schools with a campus there |
|---|---|---|
| Bronx | 142 | 100 |
| Brooklyn | 132 | 91 |
| Manhattan | 81 | 58 |
| Queens | 50 | 36 |
| Staten Island | 10 | 8 |

Schools add up to more than 287 across boroughs because some schools run campuses in more than one borough.

## Definition

A charter school is an independent public school operating under a charter granted under Article 56 of the New York State Education Law. In New York City, charters are authorized by the SUNY Board of Trustees, the NYS Board of Regents, or the NYC Schools Chancellor. A school is counted if it is open with students in 2026–27 and has at least one campus physically in the five boroughs. A **school** is one legal charter. A **campus** is that school operating in a particular building.

## Sources

Every source was captured on October 30, 2026 and is stored unchanged in `data/sources/`. Files captured in the browser were checksummed at the source and again after transfer; the two matched every time.

| Source | Used for | Records | SHA-256 |
|---|---|---|---|
| [SUNY Charter Schools Institute school list](https://www.newyorkcharters.org/charter-schools/) (updated Sep 17, 2026) | SUNY schools, their 2026–27 grades and site addresses | 196 NYC schools | `4eb9dc0e…0bf0d2c` |
| [NYSED Charter Schools Directory](https://www.nysed.gov/charter-schools/charter-schools-directory) and [Regents actions](https://www.nysed.gov/charter-schools/actions-taken-board-regents) | Regents and Chancellor schools; closures, mergers, revisions | 299 NYC rows | `5336dbab…57b70e01d` |
| [NYC Charter School Center finder](https://findnyccharterschools.org/) | Campus addresses and grades (independent of the authorizers) | 420 listings | `22d996db…e339b5d3` |
| NYC DOE pupil transportation sites, [NYC Open Data `hg3c-2jsy`](https://data.cityofnewyork.us/d/hg3c-2jsy), 2025–26 | Independent city record of where each school operated last year | 498 records | `6676236d…0d12bc6e7` |
| [Success Academy school pages](https://www.successacademies.org/schools/) | Success Academy campuses, as the operator lists them | 59 pages | `a2dece44…f29abbb4b` |
| [NYC GeoSearch](https://geosearch.planninglabs.nyc/) (the city's geocoder) | Coordinates for every campus | 394 addresses | `6df02f87…7f45f994` |

**Rejected source.** NYC Open Data's "School Locations" files are the obvious starting point, but the newest one covers 2019–20. A map built on it would be six years out of date.

## Step 1: which schools exist

The authorizers decide which schools exist, so the school list comes from them.

* **SUNY (192).** SUNY's list has 196 NYC schools. Five show no grades for 2026–27 and are excluded as not yet open or merged. Manhattan Charter School is missing from SUNY's 2026–27 list but was added back: SUNY renewed its charter through June 30, 2029 (renewal report, February 2024), and the school's own website, the Charter Center and the city all list it at 100 Attorney Street.
* **Board of Regents (60).** NYSED's roster of Regents schools (62), less Harriet Tubman Charter School (closed June 2026) and CAMPA (merged into MESA, March 2026).
* **NYC Chancellor (35).** NYSED directory rows authorized by the NYC DOE.

Every school on a state list that is not counted is in `data/legal_schools_excluded.csv` with its reason, and is shown on the page below the map: not yet open (7), merged (2), closed (2), consolidated (Explore's five state charters operate as three schools), transferred (Success Academy Bronx 5 Lower to Strive Charter School), and renamed (5 cases counted under their current names).

**One contested school.** Strive Charter School is included. SUNY approved the transfer of Success Academy Bronx 5 Lower's charter to Strive, the Regents returned the transfer in January 2026, SUNY maintained its approval, and Strive opened with students in September 2026. A union lawsuit is pending.

**Comparison with the Charter Center.** The Charter Center reports 286 NYC charter schools. Our count is 287. The Center does not publish its school level list, so the difference cannot be traced to a single school. What can be checked points to a difference in how the Center counts, not an extra school on our side: the Center's own finder lists campuses for 285 of our 287 schools, and the two it lacks (Manhattan Charter School II and Urban Dove Team Charter School III) are both on SUNY's 2026–27 list with grades and a site. Other possible causes are Strive, whose status was contested in 2026, and Manhattan Charter School, which SUNY's own 2026–27 list omits.

## Step 2: where each school operates

* **SUNY schools** use SUNY's own 2026–27 site list.
* **Regents and Chancellor schools** have no published site list, so each campus came from the Charter Center finder and was accepted only when the city's 2025–26 list places **the same school** at the same building. Matching on name as well as address matters: many buildings are shared, and two sources can agree on an address while naming different schools.
* **Every campus has at least two independent sources.** Campuses that a second source could not confirm were researched individually in step 3.
* **Borough and community school district** are computed from each campus's coordinates using official boundary files, not copied from any source.

## Step 3: every conflict resolved

Eighteen items needed individual research. All were resolved using the school's or network's own website, an authorizer document, or dated 2026 coverage.

| Item | Resolution |
|---|---|
| AECI II, 1000 Walton Ave | Confirmed. School moved into the former All Hallows High School (111 E 164th St / 1000 Walton Ave) in 2026, per the building's developer. |
| American Dream II, 652 W 187th St | Confirmed. Regents approved converting the school to grades 9–12, first class August 2026 at this address (April 2025). |
| Bold, 1093 Southern Blvd | Confirmed. School's 2026–27 enrollment page: kindergarten here, grades 1–8 at 1909 Daly Ave. |
| Law and Social Justice, 200 W Tremont Ave | Confirmed. Regents added grades 6–8 (June 2024); the developer built this building for the middle school. |
| Community Roots, 101 Park Ave | Confirmed. School website and the DOE's re-siting notice for building K265, effective 2026–27. |
| Equality, 801 Bartholdi St | Confirmed. School website lists its high school here; building purchased September 2026. |
| VOICE, 36-49 11th St | Confirmed. School website: Upper Elementary Campus, grades 3–5. |
| New Ventures | Mapped at 1441 South Ave (school network website and NYSED's March 2025 visit). The Charter Center's 2245 Richmond Ave is Richmond Prep's building. |
| Earl Monroe | Moved to 647 Elton Ave in September 2026 (NY1, October 16, 2026). SUNY's list still shows the old site. |
| Success Academy Harlem 4 | Its Hamilton Heights Middle School is mapped at 509 W 129th St, as Success Academy lists it. SUNY and the other sources give 461 W 131st St, 160 meters away. |
| Manhattan Charter School, 100 Attorney St | Mapped. See step 1. |
| International Leadership, 3515 Bainbridge Ave | Old address. Not on SUNY's 2026–27 list or the city's 2025–26 list. |
| NYC Charter School of the Arts, 26 Broadway | Old address. SUNY lists 241 Water St. |
| Urban Dove III, 31-20 37th St | Old address. SUNY lists 82-06 Northern Blvd. |
| Success Academy Laurelton MS | Opens fall 2027 (Success Academy's page). Not mapped. |
| Success Academy Bensonhurst MS | Opens 2027–28 (Success Academy's page). Not mapped. |
| Manhattan Charter School (exclusion reversed) | See step 1. |
| Harbor Science and Arts | Exclusion confirmed. SUNY's page for the school is gone and its website shows only a contact for student records. |

Four campuses that only SUNY's list showed were confirmed separately: KIPP's directory for 200 E 138th St, and SUNY's individual school pages for 306 W 232nd St and 82-06 Northern Blvd.

## Coordinates

All 394 campus addresses were geocoded with NYC GeoSearch, and every source's coordinates were compared with the geocode (`data/review/coordinate_checks.csv`).

* **Geocoder errors, corrected (3).** 101 E 150th St matched 150 E 150th St; 217 N 10th St matched 5 N 10th St; 528 W 162nd St matched 528 W 189th St. Each was replaced with an agreeing source.
* **Source errors, caught (4).** A city record for 341 39th St has longitude −73.007 instead of −74.007, which puts it 84 km away. A city record for 3000 Avenue X has a transposed digit (3.1 km off). A city record for 1475 Macombs Rd sits 1.8 km south. Success Academy's own site places 787 Lafayette Ave 900 meters away.
* **Normal differences (15 campuses).** 150 to 270 meters, the usual gap between a geocoder's street front point and a source's building centroid. The geocode was kept.

## Step 4: counts reconciled

Every one of the Charter Center finder's 420 listings is accounted for in `data/review/count_reconciliation.csv`:

| Finder listings | 420 |
|---|---|
| Matched one to one to a campus here | 406 |
| A second listing for a campus already matched (separate grade spans in one building) | 9 |
| Not a 2026–27 campus (2 test records, 3 old addresses) | 5 |

| Our campuses | 415 |
|---|---|
| With a finder listing | 406 |
| Not in the finder, confirmed by the authorizer and a second source | 9 |

The Charter Center's published figure of about 424 campuses is higher than its own finder, which holds 418 real listings on October 30, 2026; the published figure could not be broken down further.

## Step 5: blind audit

A random sample of 30 schools (18 SUNY, 7 Regents, 5 Chancellor; drawn with a fixed seed, `data/review/blind_audit_sample.json`) was given by name only to a separate AI agent with no access to this dataset. It was asked to find, from public sources on its own, every building where each school operates in 2026–27, and to check the status of every excluded school.

| Result | |
|---|---|
| Addresses the auditor found for the 30 schools | 39 |
| Of those, also in this dataset | **39 (100%)** |
| Addresses the auditor found that contradict this dataset | **0** |
| Campuses in this dataset the auditor did not find | 5 (Access Bronx at 629 Courtlandt Ave; Challenge Prep at 1520 Central Ave and 12-79 Redfern Ave; VOICE at 37-15 13th St and 36-49 11th St). Each has at least two sources here, including VOICE's own campus page. The auditor relied on older pages for these schools and noted that a second site was possible. |
| Excluded schools whose status the auditor confirmed | 14 of 14 (not yet open, merged, closed, consolidated or transferred, as recorded) |

The auditor also independently found that Success Academy NYC 15 and NYC 18 are planned for 2028–29, that Achievement First 11 and Uncommon NYC #1 are in planning years, and that Explore's charters now operate as three schools, all consistent with the exclusions here. Its full report is in `data/review/blind_audit_results.md`.

## Errors the cross checks caught

These would have reached the map if any single source had been trusted.

* **SUNY's own list** omits an operating school (Manhattan Charter School) and still shows Earl Monroe's old building.
* **The Charter Center finder** has two test records, mislabeled Success Academy campuses, wrong boroughs, three old addresses, and a school listed at its neighbor's building (New Ventures).
* **The city's 2025–26 list** has three badly wrong coordinates and is one school year old by design.
* **Success Academy's site** misplaces one campus by 900 meters.
* **The geocoder** returned the wrong building for three addresses.

## Known limitations

* Grades shown are SUNY's 2026–27 grades for SUNY schools. Grades for Regents and Chancellor schools were not independently verified and are left blank.
* Two sources agreeing is strong evidence, not proof. A school can move after every source was last updated, as Earl Monroe did.
* The data is a snapshot. Refreshing it means recapturing the sources and repeating the review, which is deliberate: the review is what makes the numbers reliable.

## Reproducing this

```bash
pip install -r requirements.txt
python scripts/legal_schools.py      # step 1: data/legal_schools.csv, data/legal_schools_excluded.csv
python scripts/build_campuses.py     # steps 2-3: data/campuses.csv, coordinate checks
python scripts/reconcile_counts.py   # step 4: data/review/count_reconciliation.csv
python scripts/build_site_data.py    # data/buildings.geojson, data/summary.json for the page
python scripts/check_data.py         # 19 integrity checks; GitHub Actions runs these before every deploy
```
