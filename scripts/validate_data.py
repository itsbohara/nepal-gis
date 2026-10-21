#!/usr/bin/env python3
"""Validate the checked-in Polygon datasets without modifying them."""

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import sys

import shapely
from shapely.geometry import Polygon, shape
from shapely.ops import unary_union
from shapely.validation import explain_validity

ROOT = Path(__file__).resolve().parents[1]
AREA_TOLERANCE = 1e-12  # Planar square degrees, not square metres.
DATASETS = {
    'nepal-map.geojson': 77,
    'nepal-district.json': 77,
    'nepal-all.json': 77,
    **{f'provinces/province-{i}.json': count
       for i, count in enumerate([14, 8, 13, 11, 12, 10, 9], 1)},
    'amchart-data/nepalHigh.json': 7,
    'amchart-data/nepalLow.json': 7,
}


def inspect_collection(data, expected_count, province=False):
    """Return errors and diagnostic measurements for one FeatureCollection.

    Coverage and orientation findings are reported separately from hard errors.
    Do not let GEOS silently close malformed GeoJSON rings before checking them.
    """
    errors, warnings, geometries, ids, positions = [], [], [], [], []
    result = {'errors': errors, 'warnings': warnings}
    if not isinstance(data, dict) or data.get('type') != 'FeatureCollection':
        errors.append('Expected a GeoJSON FeatureCollection')
        return result
    features = data.get('features')
    if not isinstance(features, list):
        errors.append('features must be an array')
        return result
    result['features'] = len(features)
    if len(features) != expected_count:
        errors.append(f'Expected {expected_count} features, got {len(features)}')
    for index, feature in enumerate(features):
        prefix = f'Feature {index}'
        try:
            if not isinstance(feature, dict) or feature.get('type') != 'Feature':
                raise ValueError('Expected a Feature')
            props = feature.get('properties')
            if not isinstance(props, dict):
                raise ValueError('properties must be an object')
            required = ('id', 'name', 'NAME_ENG', 'CNTRY', 'TYPE') if province else ('districtid', 'DISTRICT', 'TARGET')
            for key in required:
                value = props.get(key)
                if key == 'districtid':
                    if type(value) is not int:
                        raise ValueError('districtid must be an integer')
                elif not isinstance(value, str) or not value.strip():
                    raise ValueError(f'{key} must be a nonempty string')
            identifier = props['id' if province else 'districtid']
            ids.append(identifier)
            if 'id' in feature and feature['id'] != identifier:
                errors.append(f'{prefix}: feature ID differs from property ID')
            for key, value in props.items():
                if isinstance(value, str) and value != value.strip():
                    errors.append(f'{prefix}: {key} has surrounding whitespace')
            geom = feature.get('geometry')
            if not isinstance(geom, dict) or geom.get('type') != 'Polygon':
                raise ValueError('Expected Polygon geometry')
            rings = geom.get('coordinates')
            if not isinstance(rings, list) or not rings:
                raise ValueError('Polygon must have at least one ring')
            for ring in rings:
                if not isinstance(ring, list) or len(ring) < 4:
                    raise ValueError('Ring must have at least four positions')
                if ring[0] != ring[-1]:
                    raise ValueError('Unclosed ring')
                for position in ring:
                    if (not isinstance(position, list) or len(position) != 2
                            or any(type(v) not in (int, float) or not math.isfinite(v) for v in position)):
                        raise ValueError('Expected finite two-dimensional positions')
                    lon, lat = position
                    if not (-180 <= lon <= 180 and -90 <= lat <= 90):
                        raise ValueError('Position outside longitude/latitude ranges')
                    positions.append(position)
            polygon = shape(geom)
            if polygon.is_empty or not polygon.is_valid:
                raise ValueError(f'Empty or invalid geometry: {explain_validity(polygon)}')
            geometries.append((identifier, polygon))
        except (ValueError, TypeError, KeyError, IndexError) as exc:
            errors.append(f'{prefix}: {exc}')
    duplicates = [identifier for identifier, n in Counter(ids).items() if n > 1]
    if duplicates:
        errors.append(f'Duplicate IDs: {duplicates}')
    result['positions'] = len(positions)
    if positions:
        result['bbox'] = [min(p[0] for p in positions), min(p[1] for p in positions),
                          max(p[0] for p in positions), max(p[1] for p in positions)]
    # Do not perform overlay operations on a partial/invalid collection.
    if errors:
        return result
    clockwise = sum(not g.exterior.is_ccw for _, g in geometries)
    wrong_holes = sum(r.is_ccw for _, g in geometries for r in g.interiors)
    result['clockwise_exteriors'] = clockwise
    result['counterclockwise_interiors'] = wrong_holes
    if clockwise or wrong_holes:
        warnings.append(f'Ring orientation: {clockwise} clockwise exteriors, {wrong_holes} counterclockwise interiors')
    overlaps = []
    for i, (first_id, first) in enumerate(geometries):
        for second_id, second in geometries[i + 1:]:
            if first.intersects(second):
                area = first.intersection(second).area
                if area > AREA_TOLERANCE:
                    overlaps.append({'a': first_id, 'b': second_id, 'square_degrees': area})
    combined = unary_union([g for _, g in geometries])
    parts = list(combined.geoms) if combined.geom_type == 'MultiPolygon' else [combined]
    holes = [Polygon(ring) for part in parts for ring in part.interiors]
    result.update(overlap_pairs=overlaps, union_type=combined.geom_type,
                  union_holes=len(holes),
                  hole_area_square_degrees=sum(hole.area for hole in holes))
    if overlaps:
        warnings.append(f'{len(overlaps)} pairs overlap above {AREA_TOLERANCE} square degrees')
    if holes:
        warnings.append(f'{len(holes)} union holes: candidate coverage gaps, not verified boundary errors')
    return result


def validate(root):
    report = {'shapely_version': shapely.__version__, 'geos_version': shapely.geos_version_string,
              'overlap_tolerance_square_degrees': AREA_TOLERANCE, 'datasets': {}, 'errors': []}
    loaded = {}
    for name, expected_count in DATASETS.items():
        try:
            raw = (root / name).read_bytes()
            data = json.loads(raw)
            result = inspect_collection(data, expected_count, name.startswith('amchart-data/'))
            result['sha256'] = hashlib.sha256(raw).hexdigest()
            if not result['errors']:
                loaded[name] = data
        except (OSError, ValueError, UnicodeError) as exc:
            result = {'errors': [str(exc)], 'warnings': []}
        report['datasets'][name] = result
    base = loaded.get('nepal-map.geojson')
    if base:
        by_id = {f['properties']['districtid']: f for f in base['features']}
        duplicate = loaded.get('nepal-district.json')
        if duplicate is not None and duplicate != base:
            report['errors'].append('nepal-district.json differs from nepal-map.geojson')
        all_districts = loaded.get('nepal-all.json')
        if all_districts:
            for feature in all_districts['features']:
                identifier = feature['properties']['districtid']
                original = by_id.get(identifier)
                if (original is None or feature.get('id') != identifier
                        or feature['properties'] != original['properties']
                        or not shape(feature['geometry']).equals(shape(original['geometry']))):
                    report['errors'].append(f'nepal-all.json: inconsistent district {identifier}')
        membership = []
        for name, data in loaded.items():
            if name.startswith('provinces/'):
                for feature in data['features']:
                    identifier = feature['properties']['districtid']
                    membership.append(identifier)
                    if by_id.get(identifier) != feature:
                        report['errors'].append(f'{name}: inconsistent district {identifier}')
        if all(f'provinces/province-{i}.json' in loaded for i in range(1, 8)):
            if Counter(membership) != Counter(by_id.keys()):
                report['errors'].append('Province subsets do not partition all districts exactly once')
    high, low = (loaded.get(f'amchart-data/nepal{level}.json') for level in ('High', 'Low'))
    if high and low:
        attributes = lambda data: [{k: v for k, v in f.items() if k != 'geometry'} for f in data['features']]
        if attributes(high) != attributes(low):
            report['errors'].append('High and Low province attributes differ')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT, help='Repository root (default: script parent directory)')
    parser.add_argument('--json', action='store_true', help='Print full machine-readable diagnostics to stdout')
    args = parser.parse_args()
    report = validate(args.root)
    error_count = len(report['errors']) + sum(len(d['errors']) for d in report['datasets'].values())
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    else:
        print(f"Shapely {report['shapely_version']} / GEOS {report['geos_version']}")
        for name, data in report['datasets'].items():
            print(f"{name}: {data.get('features', '?')} features; {len(data['errors'])} errors")
            for error in data['errors']:
                print(f'  ERROR: {error}')
            for warning in data['warnings']:
                print(f'  WARNING: {warning}')
        for error in report['errors']:
            print(f'ERROR: {error}')
        print(f'{error_count} errors. Coverage/orientation warnings do not fail validation; no files modified.')
    return 1 if error_count else 0


if __name__ == '__main__':
    sys.exit(main())
