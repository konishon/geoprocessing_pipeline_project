import unittest
import os
from unittest.mock import patch, MagicMock
from geoprocessing_pipeline.data_loader import load_or_download_graph, load_data_by_type

class TestDataLoader(unittest.TestCase):

    @patch('os.path.exists')
    @patch('osmnx.save_graphml')
    @patch('osmnx.graph_from_place')
    @patch('osmnx.load_graphml')
    def test_load_or_download_graph_existing_file(self, mock_load_graphml, mock_graph_from_place, mock_save_graphml, mock_exists):
        """
        Test loading graph from an existing file.
        """
        # Mock that the file exists
        mock_exists.return_value = True
        
        # Mock the graph loading
        mock_graph = MagicMock()
        mock_load_graphml.return_value = mock_graph
        
        # Run the function
        address = "Kathmandu, Nepal"
        filepath = "data/kathmandu_graph.graphml"
        result = load_or_download_graph(address, filepath)
        
        # Assertions
        mock_exists.assert_called_once_with(filepath)
        mock_load_graphml.assert_called_once_with(filepath)
        mock_graph_from_place.assert_not_called()  # Graph should not be downloaded
        mock_save_graphml.assert_not_called()  # Graph should not be saved again
        self.assertEqual(result, mock_graph)  # Result should be the mocked graph

    @patch('os.path.exists')
    @patch('osmnx.save_graphml')
    @patch('osmnx.graph_from_place')
    def test_load_or_download_graph_download(self, mock_graph_from_place, mock_save_graphml, mock_exists):
        """
        Test downloading and saving the graph when the file doesn't exist.
        """
        # Mock that the file does not exist
        mock_exists.return_value = False
        
        # Mock the graph downloading
        mock_graph = MagicMock()
        mock_graph_from_place.return_value = mock_graph
        
        # Run the function
        address = "Kathmandu, Nepal"
        filepath = "data/kathmandu_graph.graphml"
        result = load_or_download_graph(address, filepath)
        
        # Assertions
        mock_exists.assert_called_once_with(filepath)
        mock_graph_from_place.assert_called_once_with(address, network_type="drive")
        mock_save_graphml.assert_called_once_with(mock_graph, filepath=filepath)
        self.assertEqual(result, mock_graph)  # Result should be the mocked graph

    def test_load_data_by_type_existing(self):
        """
        Test loading data by type when data exists in the dictionary.
        """
        # Sample data
        data = {
            'points': [
                {"id": 1, "coordinates": [85.318, 27.712], "height": 15},
                {"id": 2, "coordinates": [85.325, 27.717], "height": 25}
            ],
            'buildings': [
                {"id": 101, "coordinates": [85.318, 27.712], "floors": 10}
            ]
        }
        
        # Test loading points data
        result = load_data_by_type('points', data)
        self.assertEqual(result, data['points'])  # Ensure correct data is returned

        # Test loading buildings data
        result = load_data_by_type('buildings', data)
        self.assertEqual(result, data['buildings'])  # Ensure correct data is returned

    def test_load_data_by_type_non_existing(self):
        """
        Test loading data by type when the data type doesn't exist in the dictionary.
        """
        # Sample data
        data = {
            'points': [
                {"id": 1, "coordinates": [85.318, 27.712], "height": 15}
            ]
        }
        
        # Test loading a non-existent data type
        with self.assertRaises(ValueError) as context:
            load_data_by_type('roads', data)
        
        self.assertTrue("Unknown data type: roads" in str(context.exception))

if __name__ == '__main__':
    unittest.main()

