from src.utils.imports import *


def adjust_bounding_box(coord_value, min_coord, max_coord, resolution, bounding_box, direction1, direction2):
    """
    Adjusts the bounding box when only one unique latitude or longitude is present.
    Args:
        coord_value (float): The value of the coordinate
        min_coord (float): The minimum coordinate value
        max_coord (float): The maximum coordinate value
        resolution (float): The resolution of the data
        bounding_box (dict): The bounding box dictionary
        direction1 (str): The direction to adjust
        direction2 (str): The direction to adjust
    """
    if abs(min_coord - coord_value) < abs(max_coord - coord_value):
        max_coord += resolution - abs(max_coord - coord_value)
        bounding_box[direction1] = max_coord
    else:
        min_coord -= resolution - abs(min_coord - coord_value)
        bounding_box[direction2] = min_coord
    return min_coord, max_coord
    

def request_with_larger_area(df:pd.DataFrame, bounding_box, cmip6_resolution, request_params, filename):
    """
    This function will make a request with a larger area if the number of coordinates on one axis is less than 2
    Args:
        df (pd.DataFrame): The dataframe with the coordinates
        bounding_box (dict): The bounding box dictionary
        cmip6_resolution (float): The resolution of the data
        request_params (tuple): The request parameters
        filename (str): The name of the file
    Returns:
        pd.DataFrame: The dataframe with the coordinates
    """

    if df["lat"].nunique() == 1:
        min_lat, max_lat = adjust_bounding_box(df["lat"].unique()[0], min_lat, max_lat, cmip6_resolution, bounding_box, "north", "south")
        url = create_request_url(*request_params)
        df = try_request(url, filename)

    elif df["lon"].nunique() == 1:
        min_lon, max_lon = adjust_bounding_box(df["lon"].unique()[0], min_lon, max_lon, cmip6_resolution, bounding_box, "east", "west")
        url = create_request_url(*request_params)
        df = try_request(url, filename)
    return df


def try_request(url, filename):
    """
    This function will try to make a request to the NASA server
    Args:
        url (str): The url to request
        year (int): The year to extract
        variable (str): The variable to extract
    Returns:
        pd.DataFrame: The dataframe with the coordinates
    """
    try:
        
        response = requests.get(url)
        response.raise_for_status()
        
        with open(f"{EMPTY_REQUEST_FOLDER}/{filename}.nc", "wb") as f:
            f.write(response.content)
        if response.status_code == 200:
            st.success("Second empty request to find at leat 4 coordinates successful")   
            df = open_empty_request_df(filename)
            df = df[["lat", "lon"]].drop_duplicates()
    except Exception as e:
        print(f"An error occurred: {e}")
        st.error(f"An error occurred: {e}")
    return df



# Function to create a grid of points within a shapefile
def generate_csv_from_shape(gdf, resolution):
    """
    Generate a CSV file with points at a certain resolution within the bounds of the GeoDataFrame.
    Args:
        gdf (gpd.GeoDataFrame): The input GeoDataFrame.
        resolution (float): The resolution for the grid points.
    Returns:
        pd.DataFrame: DataFrame with 'lat' and 'lon' columns for the generated points.
    """
    # Calculate the bounding box of the shapefile
    bounds = gdf.total_bounds
    min_x, min_y, max_x, max_y = bounds

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
    })

    return points_df


def open_nc_files_in_df(nc_file_dir, years_list):
    """
    Loop through the NetCDF files and concatenate them into a single DataFrame.
    Args:
        nc_file_dir (str): The directory containing the NetCDF files.
        years_list (list): The list of years to loop through.
    Returns:
        pd.DataFrame: The concatenated DataFrame.
    """
    # Progress bar initialization
    whole_df = pd.DataFrame()
    progress_bar_params=initialize_progress_bar(years_list, text="Concatenating Requested Files: 0%")    
    for year in years_list:
        whole_year_df = pd.DataFrame()
        for nc_file in os.listdir(nc_file_dir):
            if str(year) in nc_file and nc_file.endswith(".nc"):
                nc_file_path = os.path.join(nc_file_dir, nc_file)

                # Process the NetCDF file to a DataFrame
                df = process_nc_file_to_dataframe(nc_file_path)
                whole_year_df=pd.concat([whole_year_df, df], ignore_index=False, axis=1)

        whole_df = pd.concat([whole_df, whole_year_df], ignore_index=False, axis=0)
        progress_bar_params = update_progress_bar(*progress_bar_params, text="Concatenating Requested Files:")
    return whole_df


def shapefile_uploader_management():
    set_title_3("Upload a new shapefile")
    show_uploader = st.checkbox("Upload new ZIP file", key="show_uploader")

    if show_uploader:
        uploaded_shape_zip = st.file_uploader("Upload your polygon shape as a ZIP file", type="zip", accept_multiple_files=False)

        if uploaded_shape_zip:

            # Create a temporary file to store the uploaded ZIP file
            temp_file = "temp.zip"
            temp_zip_path = os.path.join(ZIP_FOLDER, temp_file)
            with open(temp_zip_path, "wb") as f:
                f.write(uploaded_shape_zip.read())

            # Check if the ZIP file contains the required shapefile components
            with zipfile.ZipFile(temp_zip_path, "r") as z:
                extracted_files = z.namelist()
                required_extensions = {".shp", ".shx", ".prj"}
                extracted_extensions = {ext for ext in (os.path.splitext(file)[1] for file in extracted_files) if ext}

                if required_extensions.issubset(extracted_extensions):
                    st.success("Shape file has been uploaded successfully.")
                    extract_files(z, ZIP_FOLDER, temp_zip_path)
                    st.button("Reset the uploader", key="extract_shape_zip", on_click=reset_uploader)

            
                else:
                    extracted_extensions_readable = ", ".join(list(extracted_extensions)[:-1]) + list(extracted_extensions)[-1] if extracted_extensions else ""
                    st.error(f"The uploaded ZIP file contains {extracted_extensions_readable} files which is not the kind of file expected for an AOI shape." 
                            " Please ensure it includes .shp, .shx, and .prj files.")
                    

def managing_existing_folders(zip_folder):
    existing_shape_folder = [shape_folder for shape_folder in os.listdir(zip_folder) if not shape_folder.endswith(".zip")]
    # Checkboxes to select the shape folder
    if existing_shape_folder != []:
        set_title_3("Select already uploaded shape folders")

    tab1, tab2, tab3 = st.columns(3)
    for i, folder in enumerate(existing_shape_folder):
        with tab1 if i % 3 == 0 else tab2 if i % 3 == 1 else tab3:
            checkbox = st.checkbox(folder)
        if checkbox and folder not in st.session_state.selected_shape_folder:
            st.session_state.selected_shape_folder.append(folder)
        elif not checkbox and folder in st.session_state.selected_shape_folder:
            st.session_state.selected_shape_folder.remove(folder)
    tab1, tab2, tab3 = st.columns(3)
    with tab2:
        if st.session_state.selected_shape_folder != []:
            st.button("Delete selected shape folder", key="delete_shape_folder", on_click=delete_shape_folder)

def extract_csv_from_zip(zip_file, extract_to):
    """
    Extracts the CSV files from a zip file.
    Args:
        zip_file (BytesIO): The zip file containing the CSV files.
        extract_to (str): The directory to extract the files
    """
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)