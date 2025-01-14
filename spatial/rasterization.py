from utils.imports import *
from utils.variables import *

def apply_mask(masked, grid_score, shape_gdf, min_lon, max_lat, resolution):
    """
    Applies a mask to the grid score data based on the specified shape geometry.
    
    Args:
    - masked (bool): Flag indicating whether to apply the mask.
    - grid_score (ndarray): Array of interpolated scores.
    - shape_gdf (GeoDataFrame): GeoDataFrame containing the shape geometry.
    - min_lon (float): Minimum longitude of the grid.
    - max_lat (float): Maximum latitude of the grid.
    - resolution (float): Grid cell resolution.
    
    Returns:
    - ndarray: Masked grid score array with NaNs outside the shape geometry.
    """
    grid_score = grid_score[::-1]
    if masked:
        # Create the mask
        mask = geometry_mask([mapping(shape_gdf.geometry.union_all())], 
                            transform=from_origin(min_lon, max_lat, resolution, resolution), 
                            out_shape=grid_score.shape)
        
        # Apply the mask to the interpolated scores
        grid_score[mask] = np.nan

    return grid_score

def get_gdf_values(gdf, period):
    """
    Extracts latitude, longitude, and score values from a GeoDataFrame.
    
    Args:
    - gdf (GeoDataFrame): The GeoDataFrame containing latitude, longitude, and score data.
    - score_column (str): The column name for score data.
    
    Returns:
    - tuple: Arrays of latitude, longitude, and score values.
    """
    lat = gdf["lat"].values
    lon = gdf["lon"].values
    score = gdf[period].values  # Replace with the actual column name

    return lat, lon, score


def create_grid(min_lon, min_lat, max_lon, max_lat, resolution):
    """
    Creates a grid of longitude and latitude values for raster data.
    
    Args:
    - min_lon (float): Minimum longitude of the grid.
    - min_lat (float): Minimum latitude of the grid.
    - max_lon (float): Maximum longitude of the grid.
    - max_lat (float): Maximum latitude of the grid.
    - resolution (float): Resolution of each grid cell.
    
    Returns:
    - tuple: Meshgrid arrays of longitude and latitude values.
    """
    # Create a grid for the raster
    grid_lon = np.arange(min_lon, max_lon, resolution)
    grid_lat = np.arange(min_lat, max_lat, resolution)
    grid_lon, grid_lat = np.meshgrid(grid_lon, grid_lat)
    return grid_lon, grid_lat

def read_shape_file(shapefile_path):
    gdf = gpd.read_file(shapefile_path)
    gdf = gdf.to_crs("EPSG:4326")
    return gdf




def create_raster_from_df(gdf, period,masked, resolution=0.1):
    """
    Generates a raster from a GeoDataFrame and applies an optional mask.
    
    Args:
    - gdf (GeoDataFrame): The input data containing latitude, longitude, and score columns.
    - score_column (str): The column name of the score data.
    - shapefile_path (str): Path to the shapefile for masking the raster.
    - masked (bool): Flag indicating whether to apply the mask.
    - resolution (float): Grid cell resolution.
    
    Returns:
    - tuple: Masked raster grid score and affine transform for spatial alignment.
    """
    # Read the shapefile
    shape_gdf = read_shape_file("zip_files/South_Bengal/South_Bengal.shp")
    # Get Latitude, Longitude and Scores
    print(gdf.total_bounds)
    min_lon, min_lat, max_lon, max_lat = gdf.total_bounds

    lat, lon, score = get_gdf_values(gdf,period)
    grid_lon, grid_lat = create_grid(min_lon, min_lat, max_lon, max_lat, resolution)
    print(grid_lon)
    # Interpolate the irregular data to the regular grid
    grid_score = griddata((lon, lat), score, (grid_lon, grid_lat), method='linear')
    
    grid_score = apply_mask(masked, grid_score, shape_gdf, min_lon, max_lat, resolution)
    print(np.unique(grid_score))

    # Define the affine transform for the raster from top-left
    transform = from_origin(min_lon, max_lat, resolution, resolution)

    return grid_score, transform

def get_raster_info(gdf, masked, periods):
    """
    Extracts raster informations from a GeoDataFrame (gdf) based on a specific score type.
    
    Args:
        gdf (GeoDataFrame): The GeoDataFrame containing the data to be processed.
        score_type (str): A string to identify relevant score columns in the GeoDataFrame.
        shapefile_path (str): Path to the shapefile to use for raster creation.
        masked (bool): Whether to mask the raster data during creation.
    
    Returns:
        tuple: A tuple containing:
            - grid_score_list (list): A list of raster grids created for the relevant score columns.
            - transform_list (list): A list of transformation matrices for the created rasters.
            - score_columns (list): A list of score column names that match the `score_type`.
    """
    period_columns = []
    grid_score_list = list()
    transform_list = list()
    for period in periods:
    
            grid_score, tranform = create_raster_from_df(gdf=gdf,period=period,
                                        masked=masked)            
            grid_score_list.append(grid_score)
            transform_list.append(tranform)
            period_columns.append(period)
    return grid_score_list, transform_list, period_columns

def write_multiband_tif(output_path, grid_score_list, transform_list):
    """
    Writes multiple bands of raster data to a GeoTIFF file.
    
    Args:
    - output_path (str): The path where the output GeoTIFF will be saved.
    - grid_score_list (list): A list of 2D arrays representing the raster data for each band.
    - transform_list (list): A list of affine transformations for each raster band.
    """
    with rasterio.open(
        output_path,
        'w',
        driver='GTiff',
        height=grid_score_list[0].shape[0],
        width=grid_score_list[0].shape[1],
        count=len(grid_score_list),
        dtype=grid_score_list[0].dtype,
        crs='EPSG:4326',
        transform=transform_list[0],
    ) as dst:
        for i in range(len(grid_score_list)):
            dst.write(grid_score_list[i], i+1)


def rasterize_data( df : pd.DataFrame ):
    periods = list(df.columns)
    df = df.reset_index(names=None)
    print(df)
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["lon"], df["lat"]))
    gdf.set_crs(epsg=4326, inplace=True)
    grid_score_list, transform_list, _ = get_raster_info(gdf, masked=1, periods=periods)
    write_multiband_tif(output_path="another.tif", grid_score_list=grid_score_list, transform_list=transform_list)


def display_raster_with_slider(raster_path):
    """
    Display a multi-band raster with a slider to switch between epochs using Plotly.

    Args:
        raster_path (str): Path to the raster file.
    """
    # Open the raster file
    with rasterio.open(raster_path) as src:
        bands = src.read()
        epochs = [f"Epoch {i+1}" for i in range(bands.shape[0])]  # Create epoch labels

        # Find the min and max values directly from the raster data
        data_min = 1
        data_max = 4  # Use actual max value in data
        print("Data Min:", data_min)
        print("Data Max:", data_max)

    # Create a slider-based visualization without normalizing the data
    print(bands)
    fig = px.imshow(
        bands,  # Initial band for display
        # animation_frame=
        color_continuous_scale=["green", "yellow", "orange","red"],  # Choose your preferred colormap
        zmin=data_min,  # Use the actual min value from the data
        zmax=data_max,  # Use the actual max value from the data
        title="Raster Visualization",
    )

    # Add a slider for epochs
    steps = []
    for i, band in enumerate(bands):
        step = {
            "args": [{"z": [band]}],
            "label": epochs[i],
            "method": "update",
        }
        steps.append(step)

    sliders = [
        {
            "active": 0,
            "currentvalue": {"prefix": "Epoch: "},
            "pad": {"t": 50},
            "steps": steps,
        }
    ]

    fig.update_layout(sliders=sliders)

    # Display the map in Streamlit
    st.plotly_chart(fig, use_container_width=True)

# Streamlit app
def display_raster():
    
    # Save the file locally
    raster_path = "another.tif"
    display_raster_with_slider(raster_path)