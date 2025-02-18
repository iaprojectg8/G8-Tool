from src.utils.imports import *
from src.utils.variables import (EMPTY_REQUEST_FOLDER, READABLE_TO_CMIP6, CSV_FILE_DIR, MODEL_NAMES_CMIP6, 
                                 SSP, HISTORICAL_END, EXPERIMENT, NC_FILE_DIR, CMIP6_TO_READABLE, DATAFRAME_HEIGHT)

from src.lib.session_variables import *

from src.request.helpers import (reset_directory, reset_directory_if_needed, shapefile_into_gdf, get_shapefile_path,
                                normalize_longitudes, df_to_csv,create_zip)
from src.request.widget import (manage_buffer, ask_reset_directory, widget_init, widget_init_beginner,
                                initialize_progress_bar, update_progress_bar)

# -----------------------------
# --- Work on the shapefile ---
# -----------------------------

def process_shapefile(selected_shape_folder, zip_folder, default_buffer_distance):
    """
    Read the shape files and apply a buffer if needed.
    Args:
        selected_shape_folder (list): List of selected shape folders.
        zip_folder (str): The path to the zip folder.
        default_buffer_distance (float): The default buffer distance to apply.
    Returns:
        gpd.GeoDataFrame: The combined GeoDataFrame.
        list: The list of GeoDataFrames.
    """
    gdf_list = []
    st.session_state.gdf_list = []
    for folder in selected_shape_folder:

        # Open the shape file and get its content
        shapefile_path = get_shapefile_path(zip_folder, folder)
        gdf = shapefile_into_gdf(shapefile_path)

        # Put the gdf into a session variable to keep the shape not buffered
        st.session_state.gdf_list.append(copy(gdf))

        gdf = manage_buffer(folder,gdf, default_buffer_distance)
        gdf_list.append(gdf)
    print(st.session_state.gdf_list)
    st.session_state.combined_gdf = pd.concat(st.session_state.gdf_list, ignore_index=True)
    combined_gdf = pd.concat(gdf_list, ignore_index=True)

    return combined_gdf, gdf_list



# --------------------------
# --- Empty request part ---
# --------------------------

def make_empty_request_for_each_gdf(gdf_list):
    """
    This function will make an empty request for each GeoDataFrame
    Args:
        gdf_list (list): The list of GeoDataFrames
    Returns:
        pd.DataFrame: The concatenated dataframe
    """
    empty_request_gdf = pd.DataFrame()
    for gdf in gdf_list:
        df_unique = make_empty_request(gdf.total_bounds)
        if df_unique is not None:
            empty_request_gdf = pd.concat([empty_request_gdf, df_unique], ignore_index=True)
    return empty_request_gdf


def make_empty_request(bounds):
    """
    This function will make an empty request to the NASA server in order to give the 
    user an idea about the requested point repartition in there AOI
    Args:
        bounds (tuple): The bounds of the area to extract
    Returns:
        pd.DataFrame: The dataframe with the coordinates
    """

    # Variable initialization
    filename = "empty_request"
    request_params = variable_initialization(bounds)  

    url = create_request_url(*request_params)
    reset_directory(EMPTY_REQUEST_FOLDER)
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with open(f"{EMPTY_REQUEST_FOLDER}/{filename}.nc", "wb") as f:
            f.write(response.content)
        if response.status_code == 200:
            st.success("Empty request successful")   
            df = open_empty_request_df(filename)
            gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat))
            gdf.set_crs("EPSG:4326", inplace=True)
            return gdf
    except Exception as e:
        print(f"An error occurred: {e}")
        st.error(f"An error occurred: {e}")


def variable_initialization(bounds):
    """
    This function will initialize the variables for the empty request
    Args:
        bounds (tuple): The bounds of the area to extract
    Returns:
        tuple: The variable, the model, the ssp, the experiment and the year
    """
    # Variable
    min_lon, min_lat, max_lon, max_lat = bounds  
    variable = "pr"
    year = 2015
    model = "CNRM-ESM2-1"
    ssp = "ssp585"
    experiment = "r1i1p1f2"
    bounding_box= {
        "north": max_lat,
        "west": min_lon,
        "east": max_lon,
        "south": min_lat
    }
    return bounding_box, model, ssp, experiment, variable, year

def create_request_url(params, model, ssp, experiment, variable, year):
    """
    This function will create the request URL
    Args:
        params (dict): The parameters for the request
        model (str): The model to extract
        ssp (str): The ssp to extract
        experiment (str): The experiment to extract
        variable (str): The variable to extract
        year (int): The year to extract
    Returns:
        str: The URL
    """
    base_url = (f"https://ds.nccs.nasa.gov/thredds/ncss/grid/AMES/NEX/GDDP-CMIP6/{model}/{ssp}/{experiment}/{variable}/"
                    f"{variable}_day_{model}_{ssp}_{experiment}_gr_{year}.nc")
    coordinates_part=(f"?var={variable}&north={params["north"]}&west={params["west"]}&east={params["east"]}&south={params["south"]}&"
                    f"horizStride=1&time_start={year}-01-01T12:00:00Z&time_end={year}-01-02T11:00:00Z&&&accept=netcdf3&addLatLon=true")
    url = f"{base_url}{coordinates_part}"

    return url

def open_empty_request_df(filename):
    """
    This function will handle the netcdf files requested from the NASA server
    Args:
        filename (str): The filename of the netcdf file
    Returns:
        pd.DataFrame: The concatenated dataframe
    """
    dataset = xr.open_dataset(f"{EMPTY_REQUEST_FOLDER}/{filename}.nc", engine="netcdf4",) # Adjust the engine as needed
    df = dataset[["lat", "lon"]].to_dataframe().drop_duplicates().reset_index()
    df = normalize_longitudes(df)

    return df


# -------------------------------
# --- Making the real request ---
# -------------------------------

def make_whole_request(bounds):
    """
    This function will make the request to the NASA server and download the files
    Args:
        bounds (tuple): The bounds of the area to extract
    """
    if st.session_state.mode == "Beginner":
        selected_variables, selected_model, ssp, experiment, years = widget_init_beginner(
            READABLE_TO_CMIP6, HISTORICAL_END, SSP
        )

        if st.button("Make request", key="cmip6_button", use_container_width=True):
            reset_directory(NC_FILE_DIR)
            st.warning("Don't touch anything, the request is being made")
            request_loop(selected_variables, selected_model, ssp, experiment, years, bounds, nc_folder=NC_FILE_DIR) 
            nc_files_processing(NC_FILE_DIR, CSV_FILE_DIR, CSV_ZIPPED, ssp)
            
    else:
        selected_variables, selected_model, ssp, experiment, years = widget_init(
            READABLE_TO_CMIP6, MODEL_NAMES_CMIP6, SSP, HISTORICAL_END, EXPERIMENT
        )
        choice = ask_reset_directory(NC_FILE_DIR)
        if st.button("Make request", key="cmip6_button", use_container_width=True):
            # Reset the directory that will contain the data files
            reset_directory_if_needed(choice, NC_FILE_DIR)
            request_loop(selected_variables, selected_model, ssp, experiment, years, bounds, nc_folder=NC_FILE_DIR)
        if st.button("Convert everything you downloaded into CSV zip", use_container_width=True):    

            nc_files_processing(NC_FILE_DIR, CSV_FILE_DIR, CSV_ZIPPED, ssp)


def request_loop(selected_variables, selected_model, ssp_list, experiment, years_list, bounds, nc_folder):
    """
    This function will loop through the request to the NASA server and download the files
    Args:
        selected_variables (list): The variables chosen by the user
        selected_model (str): The model chosen by the user
        ssp (list): The ssp chosen by the user
        experiment (str): The experiment chosen by the user
        years (list): The years to extract
        bounds (tuple): The bounds of the area to extract
    """
    total_requests = len(selected_variables) * len(sum(years_list, []))
    progress_params = initialize_progress_bar(total_requests,text="Request Progress: 0%")
    # one request about 15 points, takes aproximatly 10 seconds for one year, one variable
    for variable in selected_variables:
        for ssp, years in zip(ssp_list, years_list):
            for year in years:
                make_year_request(variable, selected_model, ssp, experiment, bounds, year, nc_folder)
                progress_params = update_progress_bar(*progress_params, text="Request Progress:")
    st.success("All the requests have been made")


def make_year_request(variable, model, ssp, experiment, bounds, year, nc_folder):
    """
    This function will make the request to the NASA server and download the files
    Args:
        variable_chosen (str): The variable chosen by the user
        model (str): The model chosen by the user
        ssp (str): The ssp chosen by the user
        experiment (str): The experiment chosen by the user
        bounds (tuple): The bounds of the area to extract
        year (int): The year to extract
        nc_folder (str): The folder to save the NetCDF files
    """

    base_url = (f"https://ds.nccs.nasa.gov/thredds/ncss/grid/AMES/NEX/GDDP-CMIP6/{model}/{ssp}/{experiment}/{variable}/"
                    f"{variable}_day_{model}_{ssp}_{experiment}_gr_{year}.nc")
    min_lon, min_lat, max_lon, max_lat = bounds
    params = {
        "var": "pr",
        "north": max_lat,
        "west": min_lon,
        "east": max_lon,
        "south": min_lat
    }

    coordinates_part=(f"?var={variable}&north={params["north"]}&west={params["west"]}&east={params["east"]}&south={params["south"]}&"
                      f"horizStride=1&time_start={year}-01-01T12:00:00Z&time_end={year}-12-31T11:00:00Z&&&accept=netcdf3&addLatLon=true")
    
    url = f"{base_url}{coordinates_part}"
    response = requests.get(url)
    try:
        
        with open(f"{nc_folder}/{year}_{variable}_{ssp}.nc", "wb") as f:
            f.write(response.content)
    except Exception as e:
        print(e)


# ------------------------------------------------
# --- Tranform the netcdf files into csv files ---
# ------------------------------------------------

def nc_files_processing(nc_file_dir, csv_file_dir, csv_zipped_dir, ssp_list):
    """
    Process all NetCDF files in a directory and save them as CSV files.

    Args:
        nc_file_dir (str): The directory containing the NetCDF files.
        csv_file_dir (str): The directory to save the CSV files.
        csv_zipped_dir (str): The directory to save the zipped CSV files.
        ssp_list (list): The list of Shared Socioeconomic Pathways (SSPs) to extract.
    """
    # Ensure the CSV directory exists
    nc_file_list = os.listdir(nc_file_dir)
    years_list = list(set([int(file.split("_")[0]) for file in nc_file_list]))
    years_list.sort()
    
    # Preparing the CSV directory
    ssp_list = [ssp for ssp in ssp_list if ssp != "historical"]

    for ssp in ssp_list:
        reset_directory(csv_file_dir)
        whole_df = open_nc_files_in_df(nc_file_dir, years_list, ssp)
        if not whole_df.empty:
            whole_df_converted = convert_variable_units(whole_df)
            restructure_data_and_save_into_csv(whole_df_converted, csv_file_dir)
            create_zip_and_save(csv_file_dir, csv_zipped_dir, ssp, years_list)
    st.success("Everything has been gone through, go to the result page to see the data")
        
    

def open_nc_files_in_df(nc_file_dir, years_list, ssp):
    """
    Loop through the NetCDF files and concatenate them into a single DataFrame.
    Args:
        nc_file_dir (str): The directory containing the NetCDF files.
        years_list (list): The list of years to loop through.
        ssp (str): The Shared Socioeconomic Pathway (SSP) to extract.
    Returns:
        pd.DataFrame: The concatenated DataFrame.
    """
    # Progress bar initialization
    whole_df = pd.DataFrame()
    progress_bar_params=initialize_progress_bar(years_list, text=f"Concatenating Requested Files ({ssp}): 0%") 
   
    for year in years_list:
        whole_year_df = pd.DataFrame()
        for nc_file in os.listdir(nc_file_dir):
            if str(year) in nc_file and nc_file.endswith(".nc") and (ssp in nc_file or "historical" in nc_file):
                nc_file_path = os.path.join(nc_file_dir, nc_file)

                # Process the NetCDF file to a DataFrame
                df = process_nc_file_to_dataframe(nc_file_path)
                whole_year_df=pd.concat([whole_year_df, df], ignore_index=False, axis=1)

        whole_df = pd.concat([whole_df, whole_year_df], ignore_index=False, axis=0)
        progress_bar_params = update_progress_bar(*progress_bar_params, text=f"Concatenating Requested Files ({ssp})")
    
    return whole_df

def process_nc_file_to_dataframe(nc_file_path):
    """
    Process a NetCDF file and convert it into a DataFrame.
    Args:
        nc_file_path (str): The path to the NetCDF file.
    Returns:
        pd.DataFrame: The processed data as a DataFrame.
    """
    # Open the NetCDF file using xarray
    ds = xr.open_dataset(nc_file_path, engine="netcdf4")
    df = ds.to_dataframe().reset_index()

    # Change the name of the time columns to date to correspond to the future processing
    df.rename(columns={"time": "date"}, inplace=True)
    df.set_index(["date", "lat", "lon"], inplace=True)
    # Sort the data we have to get the right order in terms of date
    df.sort_index(inplace=True)
    return df

def convert_variable_units(df):
    """
    Convert certain variables to the correct units.
    - Temperature is converted from Kelvin to Celsius.
    - Precipitation is converted from kg m^-2 s^-1 to mm
    - Wind speed is converted from m s^-1 to km h^-1
    Args:
        df (pd.DataFrame): The DataFrame to convert.
    Returns:
        pd.DataFrame: The converted DataFrame.
    """
    # Convert all the temperature field from Kelvin to Celsius
    if "tas" in df.columns:
        df["tas"] = df["tas"] - 273.15
    if "tasmin" in df.columns:
        df["tasmin"] = df["tasmin"] - 273.15
    if "tasmax" in df.columns:
        df["tasmax"] = df["tasmax"] - 273.15
    # Convert all the precipitation field from kg m^-2 s^-1 to mm multiplied by 86400 to get the daily precipitation
    if "pr" in df.columns:
        df["pr"] = df["pr"] * 86400 
    # Convert the wind speed from m s^-1 to km h^-1
    if "sfcWind" in df.columns:
        df["sfcWind"] = df["sfcWind"] * 3.6
    # Convert the radiation from W m^-2 to MJ m^-2 day^-1
    # df["rsds"] = df["rsds"] * 0.0864
    # df["rlds"] = df["rlds"] * 0.0864

    return df


def restructure_data_and_save_into_csv(whole_df:pd.DataFrame, csv_file_dir):
    """
    Restructure the data and save it into CSV files.
    Args:
        whole_df (pd.DataFrame): The DataFrame to restructure.
        csv_file_dir (str): The directory to save the CSV files.
    """
    whole_df_grouped = whole_df.groupby(['lat', 'lon'])
    progress_params = initialize_progress_bar(whole_df_grouped, text="Coordinates Separation: 0%")
    for (lat, lon), group_df in whole_df_grouped:

        # Create filename using lat/lon
        filename = f"lat_{lat}_lon_{lon}.csv"
        csv_file_path = os.path.join(csv_file_dir, filename)
        group_df.rename(mapper=CMIP6_TO_READABLE, inplace=True, axis=1)
        df_to_csv(group_df, csv_file_path)
        print(f"Saved {csv_file_path}")
        progress_params = update_progress_bar(*progress_params, text="Coordinates Separation:")



       

# ---------------------
# --- Zip CSV files ---
# ---------------------

def create_zip_and_save(csv_dir, zipped_csv_dir, ssp:str, year_list):
    """
    Create a ZIP file from CSV files in a directory and save it to a specific folder.
    Args:
        csv_dir (str): The directory containing the CSV files.
        save_folder (str): The folder to save the ZIP file.
    Returns:
        str: The path of the saved ZIP file.
    """
    # Ensure the save folder exists
    if not os.path.exists(zipped_csv_dir):
        os.makedirs(zipped_csv_dir, exist_ok=True)

    # Create the zip csv file with the project location given at the beginning

    min_year = year_list[0]
    max_year = year_list[-1]
    print(year_list)
    zip_filename = f"{st.session_state.shortname} {min_year}-{max_year} ({ssp.upper()}).zip"
    zip_file_path = os.path.join(zipped_csv_dir, zip_filename)

    create_zip(zip_file_path, csv_dir)
    print(f"ZIP file saved at: {zip_file_path}") 

    return zip_file_path

def create_zip_download_button(csv_dir, button_text="Download ZIP file"):
    """
    Create in-memory zip and Streamlit download button
    Args:
        csv_dir (str): The directory containing the CSV files.
        button_text (str): The text to display on the download button
    """
    # Create in-memory buffer
    buffer = io.BytesIO()
    create_zip(buffer, csv_dir)
    buffer.seek(0)
    
    # Create download button
    st.download_button(
        label=button_text,
        data=buffer,
        file_name="climate_data.zip",
        mime="application/zip"
    )