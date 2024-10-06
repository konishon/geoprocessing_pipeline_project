import networkx as nx
import geopandas as gpd
from shapely.geometry import Point

def generate_isochrone(osm_network, distance):
    """
    Generate an isochrone polygon from a given road network graph.

    Parameters:
    - osm_network: The road network graph (OSM data).
    - distance: Distance in meters to generate the isochrone.

    Returns:
    - isochrone_polygon: A Shapely Polygon representing the isochrone area.
    """
    # Find the center node, assuming the first node is close to the center
    center_node = list(osm_network.nodes)[0]
    
    # Generate an ego graph (subgraph) around the center node with the specified distance
    subgraph = nx.ego_graph(osm_network, center_node, radius=distance, distance='length')
    
    # Extract the nodes within the subgraph
    nodes = list(subgraph.nodes())
    
    # Convert the node coordinates to Shapely Points
    node_points = [Point((osm_network.nodes[node]['x'], osm_network.nodes[node]['y'])) for node in nodes]
    
    # Create a GeoSeries of points and generate the convex hull (enclosure polygon) as the isochrone
    isochrone_polygon = gpd.GeoSeries(node_points, crs="EPSG:4326").unary_union.convex_hull
    
    return isochrone_polygon

