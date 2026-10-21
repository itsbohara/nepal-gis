"""Small synthetic geometries exercise failures absent from the real dataset."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate_data import inspect_collection


def collection(*rings):
    return {'type': 'FeatureCollection', 'features': [
        {'type': 'Feature', 'properties': {'districtid': i, 'DISTRICT': 'जिल्ला', 'TARGET': str(i)},
         'geometry': {'type': 'Polygon', 'coordinates': [ring]}}
        for i, ring in enumerate(rings, 1)
    ]}


SQUARE = [[80, 27], [81, 27], [81, 28], [80, 28], [80, 27]]


class ValidationTests(unittest.TestCase):
    def test_touching_edges_are_not_overlaps(self):
        adjacent = [[x + 1, y] for x, y in SQUARE]
        result = inspect_collection(collection(SQUARE, adjacent), 2)
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['overlap_pairs'], [])
        self.assertEqual(result['union_holes'], 0)

    def test_overlap_reports_ids_and_area(self):
        shifted = [[x + 0.5, y] for x, y in SQUARE]
        result = inspect_collection(collection(SQUARE, shifted), 2)
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['overlap_pairs'], [{'a': 1, 'b': 2, 'square_degrees': 0.5}])

    def test_hole_area_and_orientation_are_warnings(self):
        data = collection(list(reversed(SQUARE)))
        data['features'][0]['geometry']['coordinates'].append(
            [[80.25, 27.25], [80.75, 27.25], [80.75, 27.75], [80.25, 27.75], [80.25, 27.25]])
        result = inspect_collection(data, 1)
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['clockwise_exteriors'], 1)
        self.assertEqual(result['union_holes'], 1)
        self.assertAlmostEqual(result['hole_area_square_degrees'], 0.25)
        self.assertTrue(result['warnings'])

    def test_unclosed_ring_rejected_before_geos_autoclosure(self):
        result = inspect_collection(collection(SQUARE[:-1]), 1)
        self.assertTrue(any('Unclosed ring' in error for error in result['errors']))
        self.assertNotIn('union_holes', result)

    def test_self_intersection_rejected(self):
        bowtie = [SQUARE[i] for i in [0, 2, 1, 3, 0]]
        result = inspect_collection(collection(bowtie), 1)
        self.assertTrue(any('invalid geometry' in error for error in result['errors']))

    def test_duplicate_id_rejected(self):
        data = collection(SQUARE, SQUARE)
        data['features'][1]['properties']['districtid'] = 1
        self.assertTrue(any('Duplicate IDs' in e for e in inspect_collection(data, 2)['errors']))

    def test_malformed_and_nonfinite_coordinates_rejected(self):
        for position in [None, [80, float('nan')], [80, 27, 0], [True, 27], [181, 27]]:
            with self.subTest(position=position):
                data = copy.deepcopy(collection(SQUARE))
                data['features'][0]['geometry']['coordinates'][0][1] = position
                self.assertTrue(inspect_collection(data, 1)['errors'])

    def test_wrong_count_and_missing_properties_rejected(self):
        data = collection(SQUARE)
        del data['features'][0]['properties']['TARGET']
        self.assertEqual(len(inspect_collection(data, 2)['errors']), 2)

    def test_not_a_feature_collection(self):
        for data in [None, [], {'type': 'FeatureCollection', 'features': None}]:
            with self.subTest(data=data):
                self.assertTrue(inspect_collection(data, 0)['errors'])


if __name__ == '__main__':
    unittest.main()
