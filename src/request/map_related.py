from src.utils.imports import *
from src.lib.layout import set_title_2

# -------------------------
# --- CMIP6 Request Map ---
# -------------------------

def calculate_zoom_level(bounds):
    """
    Calculate the zoom level for a Folium map based on the bounds of the GeoDataFrame.

    Args:
        bounds (tuple): The bounds of the GeoDataFrame (minx, miny, maxx, maxy).

    Returns:
        int: The calculated zoom level.
    """
    minx, miny, maxx, maxy = bounds
    lat_diff = maxy - miny
    lon_diff = maxx - minx

    # Calculate the zoom level based on the extent of the bounding box
    zoom_level = int(9 - np.log(max(lat_diff, lon_diff)))
    return max(1, min(zoom_level, 18))  # Ensure zoom level is between 1 and 18


def map_empty_request(combined_gdf, empty_gdf:gpd.GeoDataFrame):
    """
    Generate a map with the GeoDataFrame and the requested coordinates.
    Args:
        combined_gdf (gpd.GeoDataFrame): The GeoDataFrame to display.
        empty_gdf (gpd.GeoDataFrame): The GeoDataFrame with empty points.
    """
    projected_gdf = combined_gdf.to_crs(epsg=st.session_state.crs)
    center = [projected_gdf.geometry.centroid.x.mean(),projected_gdf.geometry.centroid.y.mean()]
    transformer = Transformer.from_crs(f"EPSG:{st.session_state.crs}", "EPSG:4326", always_xy=True)
    center = transformer.transform(*center)
    bounds = combined_gdf.total_bounds
    zoom_start = calculate_zoom_level(bounds)
    m = folium.Map(location=center[::-1], zoom_start=zoom_start, control_scale=True)

    # Add generated points to the map
    print("Adding requested points to map")
    for _, row in empty_gdf.iterrows():
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=1,
            color='blue',
            fill=True,
            fill_color='blue'
        ).add_to(m)
    print(st.session_state.combined_gdf)
    folium.GeoJson(st.session_state.combined_gdf).add_to(m)
    set_title_2("Map")
    st_folium(m, height=600, use_container_width=True)



# ----------------------
# --- Open meteo map ---
# ----------------------


def generate_points_within_gdf(gdf, resolution):
    """
    Generate a DataFrame with coordinates at a certain resolution within the bounds of the GeoDataFrame.

    Args:
        gdf (gpd.GeoDataFrame): The input GeoDataFrame.
        resolution (float): The resolution for the grid points.

    Returns:
        pd.DataFrame: DataFrame with 'lat' and 'lon' columns for the generated points.
    """
    # Get the bounds of the GeoDataFrame
    min_x, min_y, max_x, max_y = gdf.total_bounds

    # Generate grid points
    x_coords = np.arange(min_x, max_x, resolution)
    y_coords = np.arange(min_y, max_y, resolution)
    points = [Point(x, y) for x in x_coords for y in y_coords]

    # Create GeoDataFrame for grid points
    points_gdf = gpd.GeoDataFrame(geometry=points, crs=gdf.crs)
    points_within = points_gdf[points_gdf.within(gdf.unary_union)]

    # Convert to DataFrame
    points_df = pd.DataFrame({
        'lon': points_within.geometry.x,
        'lat': points_within.geometry.y
    }).reset_index()

    return points_df

def main_map(combined_gdf):
    """
    Generate a map with the GeoDataFrame and the generated points.
    Args:
        combined_gdf (gpd.GeoDataFrame): The GeoDataFrame to display.
    Returns:
        pd.DataFrame: The generated points DataFrame.
    """
    
    center = [combined_gdf.geometry.centroid.y.mean(), combined_gdf.geometry.centroid.x.mean()]
    bounds = combined_gdf.total_bounds
    zoom_start = calculate_zoom_level(bounds)
    m = folium.Map(location=center, zoom_start=zoom_start)
    resolution = st.number_input("Resolution", 
                                 min_value=0.0001,
                                 max_value=1.0, 
                                 value=0.1, 
                                 step=0.0001,
                                 format="%0.3f")

    if resolution != st.session_state.resolution or not combined_gdf.equals(st.session_state.combined_gdf):
        st.session_state.point_df = generate_points_within_gdf(combined_gdf, resolution)
        st.session_state.resolution = resolution
        st.session_state.combined_gdf = combined_gdf

    # Add generated points to the map
    print("Adding points to map")
    for _, row in st.session_state.point_df.iterrows():
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=1,
            color='blue',
            fill=True,
            fill_color='blue'
        ).add_to(m)

    folium.GeoJson(combined_gdf).add_to(m)
    set_title_2("Map")
    st_folium(m, height=600, use_container_width=True)

    return st.session_state.point_df
    

