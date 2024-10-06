import unittest
from unittest.mock import patch, MagicMock
from shapely.geometry import Polygon
from geoprocessing_pipeline.pipeline import run_geoprocessing_pipeline

class TestPipeline(unittest.TestCase):

    @patch('geoprocessing_pipeline.data_loader.load_or_download_graph')
    @patch('geoprocessing_pipeline.isochrone.generate_isochrone')
    @patch('geoprocessing_pipeline.filter.filter_points_by_complex_query')
    @patch('geoprocessing_pipeline.filter.filter_points_within_isochrone')
    def test_run_geoprocessing_pipeline(self, mock_filter_points_within_isochrone, mock_filter_points_by_complex_query, mock_generate_isochrone, mock_load_or_download_graph):
        """
        Test the entire pipeline workflow from loading OSM data to filtering points and checking points within isochrone.
        """
        # Mock for load_or_download_graph
        mock_osm_graph = MagicMock()  # Simulate an OSM road network graph
        mock_load_or_download_graph.return_value = mock_osm_graph

        # Mock for generate_isochrone
        mock_isochrone_polygon = Polygon([(85.315, 27.710), (85.340, 27.710), (85.340, 27.730), (85.315, 27.730)])
        mock_generate_isochrone.return_value = mock_isochrone_polygon

        # Mock for filter_points_by_complex_query
        filtered_points = [
            {"id": 2, "coordinates": [85.325, 27.717], "height": 25},
            {"id": 3, "coordinates": [85.330, 27.720], "height": 30}
        ]
        mock_filter_points_by_complex_query.return_value = filtered_points

        # Mock for filter_points_within_isochrone
        points_within_isochrone = MagicMock()
        mock_filter_points_within_isochrone.return_value = points_within_isochrone

        # Define the JSON pipeline configuration
        json_input = {
            "functions": [
                {
                    "functionName": "loadOsmData",
                    "input": {
                        "data": {
                            "address": "Kathmandu, Nepal",
                            "filepath": "data/kathmandu_graph.graphml"
                        }
                    },
                    "output": "osmNetwork"
                },
                {
                    "functionName": "generateIsochrone",
                    "input": {
                        "data": "osmNetwork",
                        "parameters": {
                            "distance": 1000
                        }
                    },
                    "output": "isochroneOutput"
                },
                {
                    "functionName": "loadData",
                    "input": {
                        "parameters": {
                            "dataType": "points"
                        }
                    },
                    "output": "points"
                },
                {
                    "functionName": "filterPoints",
                    "input": {
                        "data": "points",
                        "parameters": {
                            "filterType": "byComplexQuery",
                            "filterCriteria": {
                                "attribute": "height",
                                "operator": ">",
                                "value": 20
                            }
                        }
                    },
                    "output": "filteredPointsByHeight"
                },
                {
                    "functionName": "checkPointsWithinIsochrone",
                    "input": {
                        "data": "filteredPointsByHeight",
                        "parameters": {
                            "isochrone": "isochroneOutput"
                        }
                    },
                    "output": "pointsWithinIsochrone"
                }
            ]
        }

        # Run the geoprocessing pipeline
        results = run_geoprocessing_pipeline(json_input)

        # Assert that the mock functions were called as expected
        mock_load_or_download_graph.assert_called_once_with("Kathmandu, Nepal", "data/kathmandu_graph.graphml")
        mock_generate_isochrone.assert_called_once_with(mock_osm_graph, 1000)
        mock_filter_points_by_complex_query.assert_called_once_with(filtered_points, "height", ">", 20)
        mock_filter_points_within_isochrone.assert_called_once_with(filtered_points, mock_isochrone_polygon)

        # Check the pipeline results
        self.assertEqual(results["filteredPointsByHeight"], filtered_points)
        self.assertEqual(results["pointsWithinIsochrone"], points_within_isochrone)

if __name__ == '__main__':
    unittest.main()

