import sys
import os
import json
import time
import shutil  # Added to delete the existing folder
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


import folium
import geopandas as gpd
from shapely.geometry import Point
from folium.plugins import MarkerCluster

def plot_generic_geometries(results, output_dir, query_name):
    """
    Walk through the results dictionary, detect geometries or coordinates, 
    and add them to a folium map as layers.
    """
    # Initialize a Folium map centered around a default point (Kathmandu)
    folium_map = folium.Map(location=[27.712, 85.318], zoom_start=13)

    # Dictionary for storing layers
    layers = {}

    # 1. Plot Isochrone Output as a GeoJson Layer
    isochrone = results.get('isochroneOutput')
    if isochrone and isinstance(isochrone, Point):
        isochrone_layer = folium.FeatureGroup(name='Isochrone', show=True)
        folium.GeoJson(
            isochrone,
            name="Isochrone",
            style_function=lambda x: {'fillColor': 'blue', 'color': 'black', 'weight': 2, 'fillOpacity': 0.3}
        ).add_to(isochrone_layer)
        layers['Isochrone'] = isochrone_layer

    # 2. Plot Points within Isochrone as a Marker Layer
    points_within_isochrone = results.get('pointsWithinIsochrone', gpd.GeoDataFrame(geometry=[]))
    if not points_within_isochrone.empty:
        points_within_isochrone_layer = folium.FeatureGroup(name='Points Within Isochrone', show=True)
        for _, row in points_within_isochrone.iterrows():
            folium.Marker(
                location=[row.geometry.y, row.geometry.x],
                popup="Point within Isochrone"
            ).add_to(points_within_isochrone_layer)
        layers['PointsWithinIsochrone'] = points_within_isochrone_layer

    # 3. Plot Filtered Points by Height
    filtered_points_by_height = results.get('filteredPointsByHeight', [])
    if filtered_points_by_height:
        filtered_points_layer = folium.FeatureGroup(name='Filtered Points by Height', show=True)
        for point in filtered_points_by_height:
            coordinates = point.get('coordinates')
            if coordinates and isinstance(coordinates, list) and len(coordinates) == 2:
                folium.Marker(
                    location=[coordinates[1], coordinates[0]],  # lat, lon order
                    popup=f"ID: {point['id']}, Height: {point['height']}",
                    icon=folium.Icon(color='red')
                ).add_to(filtered_points_layer)
        layers['FilteredPointsByHeight'] = filtered_points_layer

    # Add each layer to the map
    for layer_name, layer in layers.items():
        layer.add_to(folium_map)

    # Add Layer Control to the map
    folium.LayerControl().add_to(folium_map)

    # Save the map as an HTML file
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

    # Check if the output directory already exists, if so, delete it
    if os.path.exists(output_dir):
        print(f"Directory {output_dir} already exists. Deleting...")
        shutil.rmtree(output_dir)  # Delete the existing directory

    os.makedirs(output_dir, exist_ok=True)

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
            lat = func['input']['parameters']['coordinates']['lat']
            lon = func['input']['parameters']['coordinates']['lon']
            isochrone_point = Point(lon, lat)
            output = generate_isochrone(osm_network, isochrone_point, distance)
        
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
  
    config_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'configs', 'filter_points.json'))
    
    print(f"Config file path: {config_file_path}")
    
    if not os.path.exists(config_file_path):
        print(f"Error: The configuration file {config_file_path} does not exist.")
        return

    # Extract the configuration file name (without extension) to use as the query_name
    config_filename = os.path.splitext(os.path.basename(config_file_path))[0]
    query_name = config_filename  # Use the config file name as the query name
    
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
