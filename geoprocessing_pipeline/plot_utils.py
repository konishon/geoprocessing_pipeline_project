import matplotlib.pyplot as plt
import geopandas as gpd

def plot_geometries(geometries, labels=None, colors=None, title="Geospatial Plot", xlabel="Longitude", ylabel="Latitude"):
    """
    Generic function to plot multiple geometries on a map.

    Parameters:
    - geometries: A list of GeoDataFrames (each representing a geometry to plot).
    - labels: A list of labels corresponding to the geometries (optional).
    - colors: A list of colors corresponding to the geometries (optional).
    - title: The title of the plot.
    - xlabel: Label for the X-axis.
    - ylabel: Label for the Y-axis.
    """
    fig, ax = plt.subplots(figsize=(10, 10))

    # Default labels and colors if none are provided
    if labels is None:
        labels = [f"Geometry {i+1}" for i in range(len(geometries))]
    if colors is None:
        colors = ["blue", "red", "green", "purple", "orange"][:len(geometries)]

    # Plot each GeoDataFrame with its corresponding label and color
    for geometry, label, color in zip(geometries, labels, colors):
        geometry.boundary.plot(ax=ax, color=color, label=label, linewidth=2) if geometry.geom_type[0] == 'Polygon' else geometry.plot(ax=ax, color=color, label=label, marker='o')

    # Customize the plot
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.legend()
    plt.show()
