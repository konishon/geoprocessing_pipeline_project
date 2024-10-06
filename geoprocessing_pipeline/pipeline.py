from geoprocessing_pipeline.data_loader import load_or_download_graph, load_data_by_type
from geoprocessing_pipeline.isochrone import generate_isochrone
from geoprocessing_pipeline.filter import filter_points_by_complex_query, filter_points_within_isochrone

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

    # Iterate through each function step in the pipeline configuration
    for func in json_data['functions']:
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

