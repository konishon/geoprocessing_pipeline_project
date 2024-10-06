import unittest
from shapely.geometry import Polygon
from geoprocessing_pipeline.filter import filter_points_by_complex_query, filter_points_within_isochrone

class TestFilter(unittest.TestCase):

    def setUp(self):
        # Sample points data with attributes like 'height'
        self.points = [
            {"id": 1, "coordinates": [85.318, 27.712], "height": 15},
            {"id": 2, "coordinates": [85.325, 27.717], "height": 25},
            {"id": 3, "coordinates": [85.330, 27.720], "height": 30},
            {"id": 4, "coordinates": [85.335, 27.725], "height": 50}
        ]
        
        # Sample isochrone polygon
        self.isochrone_polygon = Polygon([
            (85.315, 27.710), (85.340, 27.710), (85.340, 27.730), (85.315, 27.730)
        ])
    
    def test_filter_points_by_greater_than(self):
        """
        Test filtering points where the height is greater than 20.
        """
        filtered_points = filter_points_by_complex_query(self.points, 'height', '>', 20)
        
        # We expect 3 points where height > 20
        expected_points = [
            {"id": 2, "coordinates": [85.325, 27.717], "height": 25},
            {"id": 3, "coordinates": [85.330, 27.720], "height": 30},
            {"id": 4, "coordinates": [85.335, 27.725], "height": 50}
        ]
        
        self.assertEqual(filtered_points, expected_points)
    
    def test_filter_points_by_less_than(self):
        """
        Test filtering points where the height is less than 30.
        """
        filtered_points = filter_points_by_complex_query(self.points, 'height', '<', 30)
        
        # We expect 2 points where height < 30
        expected_points = [
            {"id": 1, "coordinates": [85.318, 27.712], "height": 15},
            {"id": 2, "coordinates": [85.325, 27.717], "height": 25}
        ]
        
        self.assertEqual(filtered_points, expected_points)
    
    def test_filter_points_by_equal_to(self):
        """
        Test filtering points where the height is equal to 30.
        """
        filtered_points = filter_points_by_complex_query(self.points, 'height', '==', 30)
        
        # We expect 1 point where height == 30
        expected_points = [
            {"id": 3, "coordinates": [85.330, 27.720], "height": 30}
        ]
        
        self.assertEqual(filtered_points, expected_points)
    
    def test_filter_points_by_not_equal_to(self):
        """
        Test filtering points where the height is not equal to 15.
        """
        filtered_points = filter_points_by_complex_query(self.points, 'height', '!=', 15)
        
        # We expect 3 points where height != 15
        expected_points = [
            {"id": 2, "coordinates": [85.325, 27.717], "height": 25},
            {"id": 3, "coordinates": [85.330, 27.720], "height": 30},
            {"id": 4, "coordinates": [85.335, 27.725], "height": 50}
        ]
        
        self.assertEqual(filtered_points, expected_points)

    def test_filter_points_within_isochrone(self):
        """
        Test filtering points that are within the isochrone polygon.
        """
        points_within_isochrone = filter_points_within_isochrone(self.points, self.isochrone_polygon)
        
        # We expect all points to be within the isochrone polygon
        self.assertEqual(len(points_within_isochrone), 4)
        
        # Extract point coordinates from the filtered GeoDataFrame
        expected_coords = [(85.318, 27.712), (85.325, 27.717), (85.330, 27.720), (85.335, 27.725)]
        actual_coords = [(p.x, p.y) for p in points_within_isochrone.geometry]
        
        self.assertEqual(actual_coords, expected_coords)
    
    def test_filter_points_outside_isochrone(self):
        """
        Test filtering points when none of the points fall within the isochrone.
        """
        # Define a polygon far away from the points
        far_away_polygon = Polygon([
            (85.350, 27.740), (85.360, 27.740), (85.360, 27.750), (85.350, 27.750)
        ])
        
        points_within_isochrone = filter_points_within_isochrone(self.points, far_away_polygon)
        
        # We expect no points to be within this far-away polygon
        self.assertEqual(len(points_within_isochrone), 0)

if __name__ == '__main__':
    unittest.main()

