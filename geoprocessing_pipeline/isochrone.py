import networkx as nx
import geopandas as gpd
from shapely.geometry import Point
from math import sqrt

def euclidean_distance(coord1, coord2):
    """
    Calculate the Euclidean distance between two coordinates (lon, lat).
    """
    return sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)

def find_nearest_node(osm_network, point):
    """
    Find the nearest node in the graph to a given point.
    """
    point_coords = (point.x, point.y)
    min_distance = float('inf')
    nearest_node = None

    for node in osm_network.nodes:
        node_coords = (osm_network.nodes[node]['x'], osm_network.nodes[node]['y'])
        distance = euclidean_distance(point_coords, node_coords)

        if distance < min_distance:
            min_distance = distance
            nearest_node = node

    return nearest_node


def generate_isochrone(osm_network, point, distance):
    """
    Generate an isochrone polygon from a given road network graph.
    """
    nearest_node = find_nearest_node(osm_network, point)
    subgraph = nx.ego_graph(osm_network, nearest_node, radius=distance, distance='length')
    nodes = list(subgraph.nodes())
    node_points = [Point((osm_network.nodes[node]['x'], osm_network.nodes[node]['y'])) for node in nodes]
    isochrone_polygon = gpd.GeoSeries(node_points, crs="EPSG:4326").unary_union.convex_hull
    
    return isochrone_polygon
