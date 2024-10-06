import os
import osmnx as ox

def load_or_download_graph(address, filepath):
    """
    Load a graph from a file if it exists, otherwise download it from OpenStreetMap.

    Parameters:
    - address (str): The address or place name to retrieve the graph for.
    - filepath (str): The filepath to save or load the graph from.

    Returns:
    - networkx.Graph: The loaded or downloaded graph.
    """
    # Check if the file exists
    if os.path.exists(filepath):
        # If the file exists, load the graph from the file
        G = ox.load_graphml(filepath)
        print(f"Graph loaded from file: {filepath}")
    else:
        # If the file doesn't exist, download the graph from OpenStreetMap
        G = ox.graph_from_place(address, network_type="drive")
        # Save the graph to the specified filepath
        ox.save_graphml(G, filepath=filepath)
        print(f"Graph downloaded from OpenStreetMap and saved to file: {filepath}")
    
    return G

# Sample data with multiple types (points, roads, buildings)
data = {
    'points': [
        {"id": 1, "coordinates": [85.318, 27.712], "height": 15},
        {"id": 2, "coordinates": [85.325, 27.717], "height": 25},
        {"id": 3, "coordinates": [85.330, 27.720], "height": 30},
        {"id": 4, "coordinates": [85.335, 27.725], "height": 50}
    ],
    'roads': [
        {"id": 101, "coordinates": [85.318, 27.712], "name": "Main Road"},
        {"id": 102, "coordinates": [85.325, 27.717], "name": "Second Road"}
    ],
    'buildings': [
        {"id": 201, "coordinates": [85.318, 27.712], "floors": 10},
        {"id": 202, "coordinates": [85.325, 27.717], "floors": 5}
    ]
}

# Generic function to load data by type
def load_data_by_type(data_type):
    """
    Generic function to load data based on the provided data type.
    
    Parameters:
    - data_type (str): Type of data to load (e.g., 'points', 'roads', 'buildings').
    
    Returns:
    - The loaded data of the specified type.
    """
    if data_type in data:
        return data[data_type]
    else:
        raise ValueError(f"Unknown data type: {data_type}")

