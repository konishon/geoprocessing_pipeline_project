import unittest
from unittest.mock import MagicMock
from geoprocessing_pipeline.isochrone import generate_isochrone
from shapely.geometry import Polygon
import networkx as nx

class TestIsochrone(unittest.TestCase):

    def setUp(self):
        # Set up a sample road network using NetworkX
        self.graph = nx.Graph()
        
        # Add nodes with coordinates (longitude, latitude)
        self.graph.add_node(1, x=85.318, y=27.712)
        self.graph.add_node(2, x=85.325, y=27.717)
        self.graph.add_node(3, x=85.330, y=27.720)
        self.graph.add_node(4, x=85.335, y=27.725)
        
        # Add edges between the nodes with distances
        self.graph.add_edge(1, 2, length=500)
        self.graph.add_edge(2, 3, length=500)
        self.graph.add_edge(3, 4, length=500)
        
        # Define a sample distance for the isochrone (in meters)
        self.distance = 1000
    
    def test_generate_isochrone(self):
        """
        Test generating an isochrone from a road network graph.
        """
        # Call the generate_isochrone function with the test graph and distance
        isochrone_polygon = generate_isochrone(self.graph, self.distance)
        
        # We expect a polygon that encloses all the nodes within the distance
        # Check if the returned isochrone is a Polygon
        self.assertIsInstance(isochrone_polygon, Polygon)
        
        # Check if the polygon encloses the expected points (nodes)
        expected_coords = [(85.318, 27.712), (85.325, 27.717), (85.330, 27.720), (85.335, 27.725)]
        actual_coords = [(point.x, point.y) for point in isochrone_polygon.exterior.coords]
        
        for expected_coord in expected_coords:
            self.assertIn(expected_coord, actual_coords)
    
    def test_isochrone_empty_graph(self):
        """
        Test generating an isochrone with an empty road network graph.
        """
        empty_graph = nx.Graph()
        
        # Expect that the isochrone generation returns an empty Polygon or None
        isochrone_polygon = generate_isochrone(empty_graph, self.distance)
        
        # If the graph is empty, we expect the isochrone to be None or an empty Polygon
        self.assertIsNone(isochrone_polygon)

if __name__ == '__main__':
    unittest.main()

