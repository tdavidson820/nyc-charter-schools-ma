# Blind audit results (October 30, 2026)

An independent agent with no access to this repository was given 30 randomly drawn school names (seed 20261030, see `blind_audit_sample.json`) and the list of excluded schools, and asked to find each school's 2026–27 buildings and status from public sources on its own. Its findings, compared with `data/campuses.csv`:

| # | School | Auditor found | In this dataset? |
|---|---|---|---|
| 1 | Access Bronx | 388 Willis Ave | Yes. Dataset also has 629 Courtlandt Ave (Charter Center + city). |
| 2 | Success Academy NYC 17 | 58-23 Catalpa Ave | Yes |
| 3 | Harlem Village Academy West | 74 W 124th St | Yes |
| 4 | Zeta Inwood | 401 W 218th St; 517 W 164th St | Yes, both |
| 5 | Renaissance | 35-59 81st St | Yes |
| 6 | Uncommon Brownsville South | 985 Rockaway Ave; 213 Osborn St | Yes, both |
| 7 | Peninsula Prep | 611 Beach 19th St | Yes |
| 8 | Brooklyn Rise | 9 Hanover Pl (new building not yet in use) | Yes |
| 9 | Harlem Village Academy North | 244 W 144th St; 35 W 124th St | Yes, both |
| 10 | Explore Crown Heights | 188 Rochester Ave | Yes |
| 11 | Brooklyn Urban Garden | 500 19th St | Yes |
| 12 | East Harlem Scholars Academy | 2017 1st Ave | Yes |
| 13 | Success Academy Harlem 2 | 144 E 128th St | Yes |
| 14 | Challenge Prep | 710 Hartman Ln | Yes. Dataset also has 1520 Central Ave and 12-79 Redfern Ave (Charter Center + city). |
| 15 | Great Oaks | 240 Bleecker St | Yes |
| 16 | Success Academy Crown Heights | 330 Crown St; 72 Veronica Pl | Yes, both |
| 17 | South Bronx Classical | 977 Fox St | Yes |
| 18 | Lamad Academy | 1060 Clarkson Ave | Yes |
| 19 | Brooklyn Ascend 6 | 205 Rockaway Pkwy; 123 E 98th St | Yes, both |
| 20 | VOICE | 36-24 12th St | Yes. Dataset also has 37-15 13th St and 36-49 11th St (school's campus page). |
| 21 | East Brooklyn Ascend | 260 Shepherd Ave | Yes |
| 22 | Success Academy Bronx 1 | 339 Morris Ave | Yes |
| 23 | Bridge Prep | 715 Ocean Terrace | Yes |
| 24 | Achievement First Legacy | 118-49 Montauk St; 115-50 221st St | Yes, both |
| 25 | Wildcat Academy | 17 Battery Pl; 1239 Lafayette Ave | Yes, both |
| 26 | Hellenic Classical Staten Island | 1631 and 1641 Richmond Ave (adjacent) | Yes (1641 Richmond Ave) |
| 27 | Bronx Excellence 6 | 681 Kelly St | Yes |
| 28 | Success Academy Upper West | 145 W 84th St | Yes |
| 29 | Brooklyn Ascend | 1501 Pitkin Ave | Yes |
| 30 | Children's Aid College Prep | 1232 Southern Blvd; 1919 Prospect Ave | Yes, both |

**Addresses found by the auditor: 39. Also in the dataset: 39. Contradictions: 0.**

## Excluded schools

| School | Auditor's finding | Dataset |
|---|---|---|
| Lamad Arverne Academy | Not yet open (0 grades for 2026–27) | Not yet open |
| Minisink | Not yet open | Not yet open |
| Next Generation | No grades for 2026–27; merged corporation with Nuasin | Merged, counted under Nuasin Next Generation |
| Nuasin Next Generation | Operating, 180 W 165th St and 1366 Cromwell Ave | Included, same two campuses |
| Success Academy NYC 15, NYC 18 | Planned for 2028–29 | Not yet open |
| CAMPA | Merged into MESA (Regents, March 2026) | Merged |
| Harriet Tubman | Closed June 2026 | Closed |
| South Bronx Classical VI | Not found as an operating school | Not yet open |
| Achievement First 11 | Planning year, no site | Not yet open |
| Uncommon NYC #1 | Planning year, no site | Not yet open |
| Harbor Science and Arts | Closed (SUNY page removed, listed as closed); no closure date found | Closed |
| Explore (five state charters) | Three operate: Canarsie, Crown Heights, Flatbush | Consolidated to three |
| Success Academy Bronx 5 Lower | Became Strive Charter School, opened fall 2026 at 604 E 139th St | Transferred; Strive included at 604 E 139th St |

## Auditor's stated limitations

Several Regents and Chancellor schools' websites and NYSED pages blocked automated reading, so for those schools the auditor relied on older directory pages. That is why it found fewer campuses for Access Bronx, Challenge Prep and VOICE than this dataset holds; it found nothing that contradicts the dataset.
