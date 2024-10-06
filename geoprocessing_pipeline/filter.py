from shapely.geometry import Point
import geopandas as gpd

def filter_points_by_complex_query(points, attribute, operator, value):
    """
    Filters points based on a complex query with comparisons (e.g., <, >, ==, !=).

    Parameters:
    - points (list): A list of points (each point as a dictionary with various attributes).
    - attribute (str): The key of the attribute to filter by (e.g., 'height').
    - operator (str): The comparison operator as a string ('<', '>', '==', '!=').
    - value: The value to compare the attribute to.

    Returns:
    - list: A list of points that match the filtering criteria.
    """
    if operator == ">":
        filtered_points = [p for p in points if p.get(attribute, 0) > value]
    elif operator == "<":
        filtered_points = [p for p in points if p.get(attribute, 0) < value]
    elif operator == "==":
        filtered_points = [p for p in points if p.get(attribute, 0) == value]
    elif operator == "!=":
        filtered_points = [p for p in points if p.get(attribute, 0) != value]
    else:
        raise ValueError(f"Unsupported operator: {operator}")
    
    return filtered_points

def filter_points_within_isochrone(points, isochrone_polygon):
    """
    Check which points are within the isochrone polygon.

    Parameters:
    - points (list): A list of dictionaries representing points with 'coordinates'.
    - isochrone_polygon (Polygon): The isochrone polygon.

    Returns:
    - GeoDataFrame: A GeoDataFrame of points that are within the isochrone.
    """
    # Convert points into GeoDataFrame for spatial operations
    point_coords = [Point(p['coordinates']) for p in points]
    point_gdf = gpd.GeoDataFrame(geometry=point_coords, crs="EPSG:4326")
    
    # Find points within the isochrone
    points_within = point_gdf[point_gdf.within(isochrone_polygon)]
    return points_within

