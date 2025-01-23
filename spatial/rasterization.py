from utils.imports import *
from utils.variables import *



# ------------------------------------
# --- Function to build the raster ---
# ------------------------------------

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

def apply_mask(grid_score, shape_gdf, min_lon, max_lat, resolution):
    """
    Applies a mask to the grid score data based on the specified shape geometry.
    
    Args:
    - grid_score (ndarray): Array of interpolated scores.
    - shape_gdf (GeoDataFrame): GeoDataFrame containing the shape geometry.
    - min_lon (float): Minimum longitude of the grid.
    - max_lat (float): Maximum latitude of the grid.
    - resolution (float): Grid cell resolution.
    
    Returns:
    - ndarray: Masked grid score array with NaNs outside the shape geometry.
    """
    grid_score = grid_score[::-1]
    if shape_gdf is not None:
        # Create the mask
        mask = geometry_mask([mapping(shape_gdf.geometry.union_all())], 
                            transform=from_origin(min_lon, max_lat, resolution, resolution), 
                            out_shape=grid_score.shape)
        
        # Apply the mask to the interpolated scores
        grid_score[mask] = np.nan
    return grid_score

def read_shape_file(shapefile_path):
    gdf = gpd.read_file(shapefile_path)
    gdf = gdf.to_crs("EPSG:4326")
    return gdf


def create_raster_from_df(gdf,shape_gdf, period, resolution):
    """
    Generates a raster from a GeoDataFrame and applies an optional mask.
    
    Args:
    - gdf (GeoDataFrame): The input data containing latitude, longitude, and score columns.
    - period (tuple): Contains start and end of the processing period
    - masked (bool): Flag indicating whether to apply the mask.
    - resolution (float): Grid cell resolution.
    
    Returns:
    - tuple: Masked raster grid score and affine transform for spatial alignment.
    """
    # Read the shapefile
    
    # Get Latitude, Longitude and Scores

    min_lon, min_lat, max_lon, max_lat = gdf.total_bounds
    lat, lon, score = get_gdf_values(gdf,period)
    grid_lon, grid_lat = create_grid(min_lon, min_lat, max_lon, max_lat, resolution)

    # Interpolate the irregular data to the regular grid
    grid_score = griddata((lon, lat), score, (grid_lon, grid_lat), method='cubic')
    # Apply the mask is so
    grid_score = apply_mask(grid_score, shape_gdf, min_lon, max_lat, resolution)
    # Define the affine transform for the raster from top-left
    transform = from_origin(min_lon, max_lat, resolution, resolution)

    return grid_score, transform

def get_raster_info(gdf, shape_gdf, periods, resolution):
    """
    Extracts raster informations from a GeoDataFrame (gdf) based on a specific score type.
    
    Args:
        gdf (GeoDataFrame): The GeoDataFrame containing the data to be processed.
        shape_gdf (GeoDataFrame) : Contains the shape of the AOI 
        periods (list(tuple)) : It contains the list of the different periods
        resolution (float) : The resolution of the built raster
    
    Returns:
        tuple: A tuple containing:
            - grid_score_list (list): A list of raster grids created for the relevant score columns.
            - transform_list (list): A list of transformation matrices for the created rasters.
            - score_columns (list): A list of score column names that match the `score_type`.
    """
    grid_score_list = list()
    transform_list = list()
    
    # Builds the raster for each period
    for period in periods:

        grid_score, tranform = create_raster_from_df(gdf=gdf,shape_gdf=shape_gdf, period=period, resolution=resolution)            
        grid_score_list.append(grid_score)
        transform_list.append(tranform)

    return grid_score_list, transform_list


def rasterize_data(df: pd.DataFrame, shape_gdf, resolution, score_name):
    """
    Converts a DataFrame with geospatial data into rasterized grids and saves the raster parameters for later use.

    Args:
        df (pd.DataFrame): The input DataFrame containing 'lon', 'lat', and data for multiple time periods.
        shape_gdf: The shapefile (as a GeoDataFrame) defining the region of interest.
        resolution: The desired resolution for the rasterization process.
    """
    periods = list(df.columns)
    df = df.reset_index(names=None)
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["lon"], df["lat"]))
    gdf.set_crs(epsg=4326, inplace=True)
    grid_score_list, transform_list = get_raster_info(gdf, shape_gdf,  periods=periods, resolution=resolution)

    # Save the raster variable in session variable for later uses
    st.session_state.raster_params[score_name] = grid_score_list, transform_list


def display_raster_with_slider(score_name, periods):
    """
    Display a multi-band raster with a slider to switch between epochs using Plotly.

    Args:
        periods (list(tuple)) : Contains the list of the periods encapsulated in tuples
    """
    periods = [f"{period[0]}-{period[1]}" for period in periods]
    # Open the raster file

    grid_score_list, _ = st.session_state.raster_params[score_name]
    bands = grid_score_list


    # Colorscale min and max
    data_min = 1
    data_max = 4

    fig = px.imshow(
        bands[0], 
        color_continuous_scale=["green", "yellow", "orange","red"],
        zmin=data_min,  # Use the actual min value from the data
        zmax=data_max,  # Use the actual max value from the data
        title=f"{score_name} Exposure through Periods",
        height=800
    )

    # Building each step of the slider
    steps = []
    for i, band in enumerate(bands):
        step = {
            "args": [{"z": [band]}],
            "label": periods[i],
            "method": "update",
        }
        steps.append(step)

    # Creating the slider for the raster
    sliders = [dict(active= 0,
                    pad={"t": 120, "r":50, "l":50, "b":50},
                    steps = steps,
                    font=dict(size=17,
                              weight=800),
                    name = "Periods")]

    fig.update_layout(sliders=sliders,
                        title=dict(x=0.5,
                                    xanchor="center",
                                    font_size=25),
                        coloraxis_colorbar=dict(
                                    title=dict(text="Exposure",
                                                font=dict(size=20, color="white",weight=900),
                                                        side="top",
                                                        ),   
                                    ticks="outside",  
                                    tickvals=[1, 2, 3, 4],  # Custom tick values
                                    ticktext=["Low","Moderate", "High", "Very High"],  # Custom tick labels
                                    lenmode="fraction",            # Control the length of the colorbar
                                    len=0.8, 
                                    yanchor="middle",
                                    y=0.5,
                               ),
                        xaxis=dict(tickfont_size=15,
                                tickangle=0 ,
                                    title = dict(
                                        text="Longitude",
                                        font_size=17,
                                        standoff=50), 
                                    ticklabelstandoff =15),
                        yaxis=dict(tickfont_size=15,
                                    range=[0,1],
                                    title=dict(
                                        text="Latitude",
                                        font_size=17,
                                        standoff=50),
                                    ticklabelstandoff = 15),
                        font=dict(size=17, weight=800),
                        autosize=True)
                        

    # Display the map in Streamlit
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------
# --- Widget for the raster visualisation ---
# -------------------------------------------

def raster_download_button(score_name, index):
    """
    Creates a download button in Streamlit to allow users to download a raster file.
    The raster file is created in-memory using Rasterio's MemoryFile.
    """
    # Use Rasterio MemoryFile to create an in order do save the file
    grid_score_list, transform_list = st.session_state.raster_params 
    with MemoryFile() as memfile:
        with memfile.open(
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
                
        # Return the in-memory file's content as bytes
        raster_data = memfile.read()

    # Streamlit download part 
    st.download_button(
        label="Download Raster",
        data=raster_data,
        file_name=f"{score_name}.tif",
        mime="image/tiff",
        key=f"download_raster{index}"
    )


def read_shape_zipped_shape_file():
    """
    Handles the upload and extraction of a zipped shapefile, validates its contents, 
    and reads the shapefile if valid.

    Returns:
        GeoDataFrame: The GeoDataFrame read from the shapefile, or None if no valid shapefile is found.
    """
    uploaded_file = st.file_uploader("Upload your shapefile (ZIP format)", type="zip", key="raster shapefile")

    if uploaded_file is not None:
        st.success("ZIP file uploaded!")

        # Extract ZIP file in memory
        with zipfile.ZipFile(uploaded_file) as z:
            shapefile_files = [file for file in z.namelist()]

            # Check if a .shp file is present
            shapefile_name = [file for file in shapefile_files if file.endswith(".shp")]
            if not shapefile_name:
                st.error("No .shp file found in the ZIP archive.")
            else:
                # Extract all files into a temporary directory
                with tempfile.TemporaryDirectory() as temp_dir:
                    z.extractall(temp_dir)
                    shapefile_path = os.path.join(temp_dir, shapefile_name[0])
                    
                    return read_shape_file(shapefile_path=shapefile_path)
