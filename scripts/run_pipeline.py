import sys
import os
import json
import time
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster
from shapely.geometry import Point, Polygon
from tqdm import tqdm

# Add the project root to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from geoprocessing_pipeline.data_loader import load_or_download_graph, load_data_by_type
from geoprocessing_pipeline.isochrone import generate_isochrone
from geoprocessing_pipeline.filter import filter_points_by_complex_query, filter_points_within_isochrone


def handle_osm_network_dummy(osm_network, output_dir, name):
    """
    Dummy function to handle osmNetwork.
    Currently passes without doing anything.
    TODO: Implement proper handling of osmNetwork (e.g., save as GraphML or adjacency list).
    """
    print(f"Handling osmNetwork is a TODO for now: {name}")
    pass  # Placeholder for future implementation


def plot_generic_geometries(results, output_dir, query_name):
    """
    Walks through the results dictionary, detects geometries or coordinates, and adds them to a folium map.

    Parameters:
    - results (dict): The results dictionary with possible geometry or coordinate fields.
    - output_dir (str): Directory to save the generated map.
    - query_name (str): The name for the query (used for the output map filename).
    """
   
    folium_map = folium.Map(location=[27.712, 85.318], zoom_start=13)  
    marker_cluster = MarkerCluster().add_to(folium_map)

    # 1. Handle `isochroneOutput` (Polygon)
    isochrone = results.get('isochroneOutput')
    if isinstance(isochrone, Polygon):
        folium.GeoJson(
            isochrone,
            name="Isochrone",
            style_function=lambda x: {'fillColor': 'blue', 'color': 'black', 'weight': 2, 'fillOpacity': 0.3}
        ).add_to(folium_map)

    # 2. Handle point datasets (e.g., `points`, `filteredPointsByHeight`)
    for key in ['points', 'filteredPointsByHeight']:
        points_data = results.get(key, [])
        if isinstance(points_data, list):
            for point in points_data:
                coordinates = point.get('coordinates')
                if coordinates and isinstance(coordinates, list) and len(coordinates) == 2:
                    # Add marker to the map
                    folium.Marker(
                        location=[coordinates[1], coordinates[0]],  # [lat, lon] order
                        popup=f"ID: {point['id']}, Height: {point['height']}",
                        icon=folium.Icon(color='red')
                    ).add_to(marker_cluster)

    # Save the folium map as an HTML file
    map_filepath = os.path.join(output_dir, f"{query_name}_map.html")
    folium_map.save(map_filepath)
    print(f"Folium map saved as {map_filepath}")


def process_and_save_results(query_name, results):
    """
    Processes the results from the pipeline and creates a folium map with all geometries found.

    Parameters:
    - query_name (str): The name for the results directory.
    - results (dict): The results returned from the pipeline.
    """
    
    print(results)
    # Create output directory for this query
    output_dir = os.path.join('results', query_name)
    os.makedirs(output_dir, exist_ok=True)

    # Handle osmNetwork with the dummy function
    osm_network = results.get('osmNetwork', None)
    if osm_network:
        handle_osm_network_dummy(osm_network, output_dir, "osm_network")

    # Plot all geometries found in the results
    plot_generic_geometries(results, output_dir, query_name)




def run_geoprocessing_pipeline(json_data):
    """
    Runs the geoprocessing pipeline based on a JSON configuration.

    Parameters:
    - json_data (dict): A dictionary representing the JSON configuration for the pipeline.

    Returns:
    - dict: A dictionary containing the outputs of the various pipeline steps.
    """
    outputs = {}

    for func in tqdm(json_data['functions'], desc="Running Pipeline", unit="function"):
        func_name = func['functionName']

        # Load or download OSM data
        if func_name == "loadOsmData":
            address = func['input']['data']['address']
            filepath = func['input']['data']['filepath']
            output = load_or_download_graph(address, filepath)
        
        # Generate Isochrone
        elif func_name == "generateIsochrone":
            osm_network = outputs[func['input']['data']]
            distance = func['input']['parameters']['distance']
            output = generate_isochrone(osm_network, distance)
        
        # Load generic data (points, buildings, etc.)
        elif func_name == "loadData":
            data_type = func['input']['parameters']['dataType']
            output = load_data_by_type(data_type)
        
        # Filter Points by Complex Query (e.g., height > 20)
        elif func_name == "filterPoints" and func['input']['parameters']['filterType'] == "byComplexQuery":
            points = outputs[func['input']['data']]  # Use the points that were loaded earlier
            attribute = func['input']['parameters']['filterCriteria']['attribute']
            operator = func['input']['parameters']['filterCriteria']['operator']
            value = func['input']['parameters']['filterCriteria']['value']
            output = filter_points_by_complex_query(points, attribute, operator, value)
        
        # Check which points are within the isochrone
        elif func_name == "checkPointsWithinIsochrone":
            points = outputs[func['input']['data']]
            isochrone_polygon = outputs[func['input']['parameters']['isochrone']]
            output = filter_points_within_isochrone(points, isochrone_polygon)

        # Store the output of this function in the outputs dictionary
        outputs[func['output']] = output

    return outputs


def main():
    # Define the query name (folder name) based on the current timestamp for uniqueness
    query_name = time.strftime("%Y%m%d-%H%M%S")

    # Get the path to the configuration file
    config_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'configs', 'pipeline_config.json'))
    
    print(f"Config file path: {config_file_path}")
    
    if not os.path.exists(config_file_path):
        print(f"Error: The configuration file {config_file_path} does not exist.")
        return
    
    start_time = time.time()

    # Load the JSON configuration
    try:
        with open(config_file_path, 'r') as f:
            pipeline_config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return
    
    # Run the geoprocessing pipeline
    results = run_geoprocessing_pipeline(pipeline_config)

    # Process and save the results
    process_and_save_results(query_name, results)

    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nTotal time taken for the entire pipeline: {total_time:.2f} seconds")


if __name__ == "__main__":
    main()
