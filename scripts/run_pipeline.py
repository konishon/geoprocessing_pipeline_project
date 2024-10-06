
import sys
import os

# Add the project root to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from geoprocessing_pipeline.data_loader import load_or_download_graph, load_data_by_type
from geoprocessing_pipeline.isochrone import generate_isochrone
from geoprocessing_pipeline.filter import filter_points_by_complex_query, filter_points_within_isochrone
from geoprocessing_pipeline.plot_utils import plot_geometries


import json
import time
import pprint

from tqdm import tqdm

def run_geoprocessing_pipeline(json_data):
    """
    Runs the geoprocessing pipeline based on a JSON configuration.

    Parameters:
    - json_data (dict): A dictionary representing the JSON configuration for the pipeline.

    Returns:
    - dict: A dictionary containing the outputs of the various pipeline steps.
    """
    # This dictionary will hold the output of each function in the pipeline
    outputs = {}

    # Iterate through each function step in the pipeline configuration, wrapped in tqdm for progress
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
    # Get the absolute path to the project root and the configs directory
    config_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'configs', 'pipeline_config.json'))
    
    # Print out the path to check if it’s correct
    print(f"Config file path: {config_file_path}")
    
    # Step 1: Ensure the file exists before attempting to load it
    if not os.path.exists(config_file_path):
        print(f"Error: The configuration file {config_file_path} does not exist.")
        return
    
    # Start tracking total execution time
    start_time = time.time()
    
    # Step 2: Load the JSON configuration from the file
    try:
        with open(config_file_path, 'r') as f:
            pipeline_config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return
    
    # Step 3: Run the geoprocessing pipeline with the loaded configuration
    results = run_geoprocessing_pipeline(pipeline_config)

    # Step 4: Output the results
    print("Filtered Points with height > 20:", results.get('filteredPointsByHeight', []))
    print("Points within the Isochrone:", results.get('pointsWithinIsochrone', []))
    
    # End tracking total execution time and print the total time taken
    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nTotal time taken for the entire pipeline: {total_time:.2f} seconds")
    
    


if __name__ == "__main__":
    main()
