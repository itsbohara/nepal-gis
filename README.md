# nepal-gis

[![Validate GIS data](https://github.com/itsbohara/nepal-gis/actions/workflows/validate-data.yml/badge.svg)](https://github.com/itsbohara/nepal-gis/actions/workflows/validate-data.yml)

GeoJSON district and province maps of Nepal, plus an SVG district map. The district datasets contain 77 districts grouped into seven provinces.

## Choose a file

| File | Features | Use |
| --- | ---: | --- |
| [nepal-map.geojson](nepal-map.geojson) | 77 districts | Nationwide district map; start here |
| [nepal-district.json](nepal-district.json) | 77 districts | Same parsed data as `nepal-map.geojson`, with expanded formatting |
| [nepal-all.json](nepal-all.json) | 77 districts | Equivalent district shapes with top-level feature IDs |
| [provinces/](provinces/) | District subsets | One file per province; district polygons, not province outlines |
| [amchart-data/nepalHigh.json](amchart-data/nepalHigh.json) | 7 provinces | Province outlines with more coordinate positions |
| [amchart-data/nepalLow.json](amchart-data/nepalLow.json) | 7 provinces | Smaller province outlines for web maps |
| [new-map.svg](new-map.svg) | 77 district paths | Illustration grouped by province; not georeferenced GIS data |

All JSON files are GeoJSON `FeatureCollection` objects with `Polygon` geometries. There are no TopoJSON files in this repository.

## Province files

| Number | Name | District file | Districts | Province outline ID |
| --- | --- | --- | ---: | --- |
| 1 | Koshi | [province-1.json](provinces/province-1.json) | 14 | `NP-P1` |
| 2 | Madhesh | [province-2.json](provinces/province-2.json) | 8 | `NP-P2` |
| 3 | Bagmati | [province-3.json](provinces/province-3.json) | 13 | `NP-P3` |
| 4 | Gandaki | [province-4.json](provinces/province-4.json) | 11 | `NP-P4` |
| 5 | Lumbini | [province-5.json](provinces/province-5.json) | 12 | `NP-P5` |
| 6 | Karnali | [province-6.json](provinces/province-6.json) | 10 | `NP-P6` |
| 7 | Sudurpashchim | [province-7.json](provinces/province-7.json) | 9 | `NP-P7` |

Names and district counts were checked against the [National Statistics Office's local-level code reference](https://ec.nsonepal.gov.np/html/admin_code.html) on 2026-10-21. This reference is not the original source of the geometry.

## Quick start

Read the district data with Python's standard library:

```python
import json
from pathlib import Path

data = json.loads(Path("nepal-map.geojson").read_text(encoding="utf-8"))
districts = {f["properties"]["districtid"]: f for f in data["features"]}
print(len(districts))  # 77
print(districts[27]["properties"]["DISTRICT"])  # काठमाण्डौं
```

For a browser map, serve the files over HTTP. In a Leaflet page with an existing `map`, load the GeoJSON layer:

```javascript
const response = await fetch("./nepal-map.geojson");
if (!response.ok) throw new Error(`Could not load districts: ${response.status}`);
const districts = await response.json();
const layer = L.geoJSON(districts).addTo(map);
map.fitBounds(layer.getBounds());
```

In QGIS, add `nepal-map.geojson` as a vector layer. Coordinates appear to be longitude/latitude degrees in `[longitude, latitude]` order; the original CRS/datum is undocumented. Verify it against your intended reference before spatial analysis or reprojection.

## Properties and compatibility

| District property | Meaning |
| --- | --- |
| `districtid` | Unique legacy integer ID within this dataset; not a documented current NSO code |
| `DISTRICT` | Nepali district label |
| `TARGET` | Legacy English label; includes split-district labels such as `RUKUM5` and `RUKUM6` |
| `DIST_NAME` | Additional English label available only for the 13 province-3 districts |

Only `nepal-all.json` has top-level district feature IDs. Province outline files have both feature-level and property-level IDs, plus `name`, `NAME_ENG`, `CNTRY`, and `TYPE` properties. Join using documented IDs within the same dataset rather than display labels or assuming compatibility with external codes.

The current cleanup updates province display names and removes trailing line breaks from four district labels. Filenames, field names, IDs, geometry, feature order, and SVG selectors are preserved. See [CHANGELOG.md](CHANGELOG.md) for exact label changes.

## Sources and limitations

Original geometry sources, boundary dates, source CRS, and conversion procedures have not yet been recovered. District geometry entered this repository in April 2020; the SVG was added in January 2021. **Updating display names does not update or certify the boundaries.**

An audit found individually valid polygons, but also small district overlaps and holes in the combined outline. Province outlines differ from district geometry and should not be assumed to align exactly. Boundary currency, territorial representation, and geographic accuracy remain unverified.

See [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md) for file-level provenance status, geometry diagnostics, and attribution details.

## Validate the data

With Python 3.11 or newer, run from the repository root:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-validation.txt
.venv/bin/python scripts/validate_data.py
```

Add `--json` for detailed machine-readable diagnostics. Validation checks file structure, geometry, IDs, feature counts, and consistency between district copies and province subsets. It reports existing coverage/orientation issues as warnings and does not change any files. See the [validation details and tests](docs/DATA_SOURCES.md#geometry-diagnostics).

GitHub Actions runs these checks and the validator tests on every push and pull request using Python 3.11 and 3.14. You can also run the workflow manually from the repository's Actions tab. Existing geometry warnings remain visible in the validation logs; malformed or inconsistent data fails the job.

## Used in research

Figure 3 of **“Gemykibivirus detection in acute encephalitis patients from Nepal”** (*mSphere*, 2024; DOI: [10.1128/msphere.00219-24](https://doi.org/10.1128/msphere.00219-24)) credits this repository as the source adapted for its Nepal map, under Apache License 2.0.

[Read the paper on PubMed Central](https://pmc.ncbi.nlm.nih.gov/articles/PMC11287993/). This documents use by the paper's authors; it does not imply NIH endorsement.

## Citation and license

Use [CITATION.cff](CITATION.cff) to cite this repository, and include the commit or release you used. Credit original data sources when established; repository attribution does not replace their attribution requirements.

The repository includes an [Apache License 2.0](LICENSE). Original-source licensing for the existing geometry is not documented; the repository license alone does not establish upstream rights. See the provenance notes before redistributing data or combining it with other sources.
