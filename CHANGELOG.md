# Changelog

## Unreleased

### Data label updates

- In both `amchart-data/nepalHigh.json` and `nepalLow.json`, update `name` and `NAME_ENG` for provinces 1, 2, 3, and 5 to Koshi, Madhesh, Bagmati, and Lumbini respectively. Update province 7's `NAME_ENG` from `Province 7` to `Sudurpashchim`.
- Remove trailing `\r\n` from `DISTRICT` labels for IDs 11 (Solukhumbu), 33 (Bara), 57 (Banke), and 68 (Bajhang) in all nationwide and relevant province district files.
- Preserve district spellings beyond whitespace cleanup pending a reviewed naming crosswalk. Consumers comparing full label strings should account for these changes.

### Documentation

- Document dataset roles, province membership, properties, usage, provenance gaps, and geometry limitations.
- Correct the format description: existing JSON datasets are GeoJSON, not TopoJSON.
- Add research attribution and repository citation metadata.

No boundaries, coordinate values, IDs, filenames, feature order, or SVG selectors were changed. This is a label/documentation update, not a new boundary edition.
