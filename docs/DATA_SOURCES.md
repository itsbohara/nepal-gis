# Data sources and provenance status

Reviewed 2026-10-21. Repository commit dates are not boundary effective dates. Original geometry sources and boundary dates have not been recovered.

## Existing assets

| File | Contents and relationship | First repository commit | Original source / boundary date / source license |
| --- | --- | --- | --- |
| `nepal-map.geojson` | 77 districts; nationwide reference file for this repository | 2020-04-20 (`b352841`) | Unknown / unknown / undocumented |
| `nepal-district.json` | Same parsed data as `nepal-map.geojson`; expanded formatting | 2020-04-20 (`b352841`) | Unknown / unknown / undocumented |
| `nepal-all.json` | Same district shapes/properties; adds feature IDs; two ring sequences differ but are geometrically equal | 2020-04-20 (`ce53bf0`) | Unknown / unknown / undocumented |
| `provinces/province-1.json` | 14 district features matching the nationwide data | 2020-04-20 (`b352841`) | Unknown / unknown / undocumented |
| `provinces/province-2.json` | 8 matching district features | 2020-04-20 (`b352841`) | Unknown / unknown / undocumented |
| `provinces/province-3.json` | 13 matching district features | 2020-04-20 (`b352841`) | Unknown / unknown / undocumented |
| `provinces/province-4.json` | 11 matching district features, including eastern Nawalparasi (481) | 2020-04-20 (`b352841`) | Unknown / unknown / undocumented |
| `provinces/province-5.json` | 12 matching district features, including western Nawalparasi (482) and eastern Rukum (541) | 2020-04-20 (`b352841`) | Unknown / unknown / undocumented |
| `provinces/province-6.json` | 10 matching district features, including western Rukum (542) | 2020-04-20 (`b352841`) | Unknown / unknown / undocumented |
| `provinces/province-7.json` | 9 matching district features | 2020-04-20 (`b352841`) | Unknown / unknown / undocumented |
| `amchart-data/nepalHigh.json` | 7 province outlines; 1,907 coordinate positions | 2020-04-20 (`b352841`) | Unknown / unknown / undocumented |
| `amchart-data/nepalLow.json` | 7 province outlines; 729 positions; same feature attributes as High | 2020-04-20 (`b352841`) | Unknown / unknown / undocumented |
| `new-map.svg` | 77 district paths grouped into seven provinces; drawing coordinates | 2021-01-04 (`8adf98e`) | Unknown / unknown / undocumented |

No original download URLs, retrieval dates, transformation recipes, or source CRS declarations were found in the repository or its six-commit history. The `amchart-data` directory name does not establish an upstream author or license. SVG namespace URLs are format declarations, not attribution.

JSON files contain two-dimensional coordinates consistent with longitude/latitude degrees. This observation does not independently establish the original datum. SVG coordinates use its `0 0 1224.992 817.002` viewBox, not geographic coordinates.

## Reference used for label maintenance

- Publisher: National Statistics Office, Nepal.
- Page: [Nepal Local Level Code](https://ec.nsonepal.gov.np/html/admin_code.html).
- Checked: 2026-10-21, including the page's embedded administrative records.
- Used to check current province display names, district counts, and province membership; no geometry was copied from this reference.
- These codes differ from the repository's legacy `districtid` values. A reviewed crosswalk is needed before joining on external administrative codes.

District spelling variants occur between the repository and this reference. They have not been silently replaced. The present cleanup removes trailing CRLF characters from four district labels and updates province names; no source geometry was transformed.

## Geometry diagnostics

Checks on existing coordinates using Shapely/GEOS found:

- All individual polygons valid and nonempty; all rings closed. IDs are unique within each dataset.
- All exterior rings clockwise, opposite the exterior orientation specified by GeoJSON RFC 7946. GEOS validity and GeoJSON ring orientation are different checks.
- In the nationwide district layer, 51 pairs have intersection area above `1e-12` square degrees. The largest observed intersection is between Dhading (30) and Gorkha (36), approximately `0.0000645831` square degrees.
- The district union contains 2,967 interior holes, totalling approximately `0.0006561313` square degrees. These require investigation as candidate coverage gaps; no automated repairs have been applied.
- Each province outline layer has one interior hole of approximately `0.000000415` square degrees and no pairwise intersections above the same area tolerance.

These planar areas are diagnostic values, not square metres. Individual polygon validity does not establish coverage quality or real-world accuracy. Province and district layers have different extents/precision and are not verified as mutually aligned. Territorial representation and current boundary accuracy have not been checked against authoritative geometry.

## Licensing and attribution

The repository carries Apache License 2.0. Per-asset upstream licensing and original-source rights are undocumented. This is an unresolved provenance finding, not a determination that the data is unauthorized. Record each newly imported dataset's source, license, attribution, date, and processing steps rather than assuming the repository license covers it.

The [mSphere paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC11287993/) attributes its Figure 3 map adaptation to this repository under Apache License 2.0. That is evidence of downstream use, not evidence of the geometry's original source or license.

Future source-tracing contributions should include the original URL or archived download, applicable license text, boundary/reference date, and a reproducible comparison or transformation. Preserve distinct source versions rather than silently combining boundaries.
