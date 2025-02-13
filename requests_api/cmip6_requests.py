from utils.imports import *
from utils.variables import *

from layouts.layout import *
from maps_related.main_functions import map_empty_request, read_shape_file
from lib.session_variables import *

from requests_api.helpers import reset_directory


# -----------------------------
# --- Widget Initialization ---
# -----------------------------

def widget_init_beginner():
    """
    This function will initialize the widgets for the cmip6 request
    Returns:
        tuple: The selected variables, the selected model, the ssp, the experiment and the years
    """
    # Variable
    selected_variables = list(READABLE_TO_CMIP6.values())
    
    # Period
    (long_period_start, long_period_end) = select_period_cmip6(key="cmip6")
    
    # Model
    selected_model = "CNRM-ESM2-1"
    # Select a scenario
    ssp = select_ssp(long_period_start, long_period_end)
    experiment = "r1i1p1f2"

    # Process to get proper years
    years = get_years_from_ssp(ssp, long_period_start, long_period_end)
    
    return selected_variables, selected_model, ssp, experiment, years

def widget_init():
    """
    This function will initialize the widgets for the cmip6 request
    Returns:
        tuple: The selected variables, the selected model, the ssp, the experiment and the years
    """
    # Variable
    if st.session_state.mode == "Beginner":
        selected_variables = list(READABLE_TO_CMIP6.values())
        print(selected_variables)
    else : 
        if st.checkbox(label="Take all variables"):
            selected_variables = st.pills("Chose variable to extract", 
                                                READABLE_TO_CMIP6.keys(), 
                                                default=READABLE_TO_CMIP6.keys(),
                                                selection_mode="multi")
        else:
            selected_variables = st.pills("Chose variable to extract", 
                                                READABLE_TO_CMIP6.keys(),
                                                selection_mode="multi")
        
    real_selected_variables = list(map(lambda key : READABLE_TO_CMIP6.get(key),selected_variables))

    # Period
    (long_period_start, long_period_end) = select_period_cmip6(key="cmip6")
    
    # Model
    if st.session_state.mode == "Beginner":
        selected_model = "CNRM-ESM2-1"
    else:
        selected_model = st.selectbox("Chose the model to use", MODEL_NAMES_CMIP6)

    # Select a scenario
    ssp = select_ssp(long_period_start, long_period_end)
    if st.session_state.mode == "Beginner":
        experiment = "r1i1p1f2"
    else:
        experiment = st.selectbox(label="Chose the experiment to use", options=EXPERIMENTS)

    # Process to get proper years
    years = get_years_from_ssp(ssp, long_period_start, long_period_end)
    
    return real_selected_variables, selected_model, ssp, experiment, years


def select_period_cmip6(key):
    """
    Allows the user to select a data period using an interactive Streamlit slider.

    Returns:
        tuple: The start and end values of the selected period.
    """
    # Display the slider that allows the user to select the bounds
    
    start = 1950
    end = 2100
    period_start, period_end = st.slider(
        "Select the data period:",
        min_value=start, 
        max_value=end,
        value=(start, end),
        key=key)      
    return period_start, period_end

def select_ssp(long_period_start, long_period_end):
    """
    This function will allow the user to select the ssp to use
    Args:
        long_period_start (int): The start year of the period
        long_period_end (int): The end year of the period
    Returns:
        str: The ssp to use
    """
    if long_period_end<=HISTORICAL_END_YEAR:
        ssp = ["historical"]
    elif long_period_start > HISTORICAL_END_YEAR :
        ssp = st.pills(label="Chose the ssp to use", options=SSP, default=SSP[0], selection_mode="multi")
    else:
        ssp = st.pills(label="Chose the ssp to use", options=SSP, default=SSP[0], selection_mode="multi")
        ssp = ["historical", *ssp]
    return ssp


def get_years_from_ssp(ssp, long_period_start, long_period_end):
    """
    This function will get the years from the ssp
    Args:
        ssp (list): The ssp to use
        long_period_start (int): The start year of the period
        long_period_end (int): The end year of the period
    Returns:
        list: The list of years
    """
    years = []
    for scenario in ssp:
        if scenario == "historical":
            if long_period_end <= HISTORICAL_END_YEAR:
                years.append(list(range(long_period_start, long_period_end + 1)))
            else:
                years.append(list(range(long_period_start, HISTORICAL_END_YEAR + 1)))
        else:
            if long_period_start > HISTORICAL_END_YEAR:
                years.append(list(range(long_period_start, long_period_end + 1)))
            else:
                years.append(list(range(HISTORICAL_END_YEAR + 1, long_period_end + 1)))
    return years

# -------------------------------
# --- Making the real request ---
# -------------------------------


def make_whole_request(bounds, nc_directory):
    """
    This function will make the request to the NASA server and download the files
    Args:
        bounds (tuple): The bounds of the area to extract
    """
    if st.session_state.mode == "Beginner":
        selected_variables, selected_model, ssp, experiment, years = widget_init_beginner()
        if st.button("Make request", key="cmip6_button", use_container_width=True):
            reset_directory(nc_directory)
            request_loop(selected_variables, selected_model, ssp, experiment, years, bounds, nc_folder=nc_directory)
            process_all_nc_files(nc_directory, CSV_FILE_DIR)
            create_zip_and_save(CSV_FILE_DIR, CSV_ZIPPED)
    else:
        selected_variables, selected_model, ssp, experiment, years = widget_init()
        choice = ask_reset_directory(nc_directory)
        if st.button("Make request", key="cmip6_button", use_container_width=True):
            # Reset the directory that will contain the data files
            reset_directory_if_needed(choice, nc_directory)
            request_loop(selected_variables, selected_model, ssp, experiment, years, bounds, nc_folder=nc_directory)
        convert_nc_to_csv(NC_FILE_DIR, CSV_FILE_DIR)


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
    progress_bar = st.progress(0, text="Request Progress: 0%")
    progress = 0
    # one request about 15 points, takes apoxximatly 10 seconds for one year, one variable
    for variable in selected_variables:
        for ssp, years in zip(ssp_list, years_list):
            for year in years:
                make_year_request(variable, selected_model, ssp, experiment, bounds, year, nc_folder)
                progress += 1
                progress_percentage = int((progress / total_requests) * 100)

                progress_bar.progress(progress / total_requests, text=f"Request Progress: {progress_percentage}%")
    st.success("All the requests have been made")
    
    

def reset_directory_if_needed(choice, nc_directory):
    """
    This function will reset the directory if needed
    Args:
        choice (str): The choice of the user
        nc_directory (str): The directory to reset
    """
    if choice == "Yes":
        reset_directory(nc_directory)
        st.success("Your files have been deleted")
    elif choice == "No":
        st.success("Your files are still there")


def convert_nc_to_csv(nc_file_path, csv_file_path):
    """
    This function will convert the netcdf files into csv files
    Args:
        nc_file_path (str): The path to the netcdf files
        csv_file_path (str): The path to the csv files
    """
    if st.button("Convert everything you downloaded into CSV zip", use_container_width=True):    

        process_all_nc_files(nc_file_path, csv_file_path)
        create_zip_download_button(csv_file_path, button_text="Download ZIP file")
                
            
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
        with open(f"{nc_folder}/{year}_{variable}.nc", "wb") as f:
            f.write(response.content)
    except Exception as e:
        print(e)
    
        


# --------------------------
# --- Empty request part ---
# --------------------------

def make_empty_request(bounds):
    """
    This function will make an empty request to the NASA server in order to see the resolution of the data
    Args:
        bounds (tuple): The bounds of the area to extract
    """

    # Request parametrization
    min_lon, min_lat, max_lon, max_lat = bounds  
    variable = "pr"
    year = 2015
    model = "CNRM-ESM2-1"
    ssp = "ssp585"
    experiment = "r1i1p1f2"
    params = {
        "north": max_lat,
        "west": min_lon,
        "east": max_lon,
        "south": min_lat
    }
    
    base_url = (f"https://ds.nccs.nasa.gov/thredds/ncss/grid/AMES/NEX/GDDP-CMIP6/{model}/{ssp}/{experiment}/{variable}/"
                    f"{variable}_day_{model}_{ssp}_{experiment}_gr_{year}.nc")
    coordinates_part=(f"?var={variable}&north={params["north"]}&west={params["west"]}&east={params["east"]}&south={params["south"]}&"
                      f"horizStride=1&time_start={year}-01-01T12:00:00Z&time_end={year}-01-02T11:00:00Z&&&accept=netcdf3&addLatLon=true")
    url = f"{base_url}{coordinates_part}"
    
    reset_directory(EMPTY_REQUEST_FOLDER)
    cmip6_resolution = 0.25
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with open(f"{EMPTY_REQUEST_FOLDER}/{year}.nc", "wb") as f:
            f.write(response.content)
        if response.status_code == 200:
            st.success("Empty request successful")   
            df = handle_empty_request_files(year, variable)

            if df["lat"].nunique() == 1 :
                lat = df["lat"].unique()[0] 
                if abs(min_lat - lat) < abs(max_lat - lat):
                    max_lat = max_lat + (cmip6_resolution - abs(max_lat - lat))
                    params["north"] = max_lat
                else:
                    min_lat = min_lat - (cmip6_resolution - abs(min_lat - lat))
                    params["south"] = min_lat
                url = create_request_url(params, model, ssp, experiment, variable, year)
                df = try_request(url, year, variable)
                


            elif df["lon"].nunique() == 1:
                lon = df["lon"].unique()[0]
                if abs(min_lon - lon) < abs(max_lon - lon):
                    max_lon = max_lon + (cmip6_resolution - abs(max_lon - lon))
                    params["east"] = max_lon
                else:
                    min_lon = min_lon - (cmip6_resolution - abs(min_lon - lon))
                    params["west"] = min_lon

                url = create_request_url(params, model, ssp, experiment, variable, year)
                df = try_request(url, year, variable)
               
            
            gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat))
            gdf.set_crs("EPSG:4326", inplace=True)
            return gdf
    except Exception as e:
        print(f"An error occurred: {e}")
        st.error(f"An error occurred: {e}")


def ask_reset_directory(folder):
    existing_files = os.listdir(folder)
    if existing_files != []:
        set_title_3("Before to make your request, you should know that your request folder is not empty, and here are the files in it")
        with st.expander(label="Files in the request folder"):
            # The markdown here is just to have a fix height for the expander
            st.markdown(
                f"""
                <div style="height: {DATAFRAME_HEIGHT}px; overflow-y: auto;">
                    {existing_files}
                </div>
                """, 
                unsafe_allow_html=True
            )
        choice = st.radio("Do you want to empty it", ["No","Yes"])
        return choice
        


        
# Look for the way it should be used, because i think it can be a good way to do, it is like an alert

def create_request_url(params, model, ssp, experiment, variable, year):

    base_url = (f"https://ds.nccs.nasa.gov/thredds/ncss/grid/AMES/NEX/GDDP-CMIP6/{model}/{ssp}/{experiment}/{variable}/"
                    f"{variable}_day_{model}_{ssp}_{experiment}_gr_{year}.nc")
    coordinates_part=(f"?var={variable}&north={params["north"]}&west={params["west"]}&east={params["east"]}&south={params["south"]}&"
                    f"horizStride=1&time_start={year}-01-01T12:00:00Z&time_end={year}-01-02T11:00:00Z&&&accept=netcdf3&addLatLon=true")
    url = f"{base_url}{coordinates_part}"

    return url

def try_request(url, year, variable):
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
        
        with open(f"{EMPTY_REQUEST_FOLDER}/{year}.nc", "wb") as f:
            f.write(response.content)
        if response.status_code == 200:
            st.success("Second empty request to find at leat 4 coordinates successful")   
            df = handle_empty_request_files(year, variable)
            df = df[["lat", "lon"]].drop_duplicates()
    except Exception as e:
        print(f"An error occurred: {e}")
        st.error(f"An error occurred: {e}")
    return df




def handle_empty_request_files(year, variable):
    """
    This function will handle the netcdf files requested from the NASA server
    Args:
        years (list): The years to extract
    Returns:
        pd.DataFrame: The concatenated dataframe
    """
    dataset = xr.open_dataset(f"{EMPTY_REQUEST_FOLDER}/{year}.nc", engine="netcdf4",) # Adjust the engine as needed
    df = dataset[["lat", "lon"]].to_dataframe().drop_duplicates().reset_index()
    df = check_coordinates(df)


    return df

def check_coordinates(df:pd.DataFrame):
    """
    This function will check the coordinates of the dataframe and correct them if necessary.
    Args:
        df (pd.DataFrame): The dataframe to check

    Returns:
        pd.DataFrame: The corrected dataframe
    """
    # i want you to iterate over the df and change all the longitude above 180 to negative values
    df.loc[df["lon"] > 180, "lon"] = df.loc[df["lon"] > 180, "lon"] - 360
    return df



# ------------------------------------------------
# --- Tranform the netcdf files into csv files ---
# ------------------------------------------------

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

def save_dataframe_to_csv(df, csv_file_path):
    """
    Save a DataFrame to a CSV file.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        csv_file_path (str): The path to the CSV file.
    """
    df.to_csv(csv_file_path, index=True)

def process_all_nc_files(nc_file_dir, csv_file_dir):
    """
    Process all NetCDF files in a directory and save them as CSV files.

    Args:
        nc_file_dir (str): The directory containing the NetCDF files.
        csv_file_dir (str): The directory to save the CSV files.
    """
    # Ensure the CSV directory exists
    all_file_list = os.listdir(nc_file_dir)
    years = list(set([int(file.split("_")[0]) for file in all_file_list]))
    years.sort()
    # Loop through all NetCDF files in the directory
    whole_df = pd.DataFrame()
    progress_bar = st.progress(0, text="Convert Progress: 0%")
    progress = 0
    total_progress = len(years)
    for year in years:
        whole_year_df = pd.DataFrame()
        for nc_file in os.listdir(nc_file_dir):
            if str(year) in nc_file and nc_file.endswith(".nc"):
                nc_file_path = os.path.join(nc_file_dir, nc_file)

                # Process the NetCDF file to a DataFrame
                df = process_nc_file_to_dataframe(nc_file_path)
                whole_year_df=pd.concat([whole_year_df, df], ignore_index=False, axis=1)

        whole_df = pd.concat([whole_df, whole_year_df], ignore_index=False, axis=0)
        progress +=1
        progress_percentage = int((progress / total_progress) * 100)
        progress_bar.progress(progress / total_progress, text=f"Convert Progress: {progress_percentage}%")
    whole_df = convert_variable_units(whole_df)
    progress_bar = st.progress(0, text="Restructuration Progress: 0%")
    progress = 0
    total_progress = len(whole_df.groupby(['lat', 'lon']))
    if os.path.exists(csv_file_dir):
        shutil.rmtree(csv_file_dir)  # Delete the directory and its contents
    os.makedirs(csv_file_dir)  # Recreate the directory
    for (lat, lon), group_df in whole_df.groupby(['lat', 'lon']):
        # Create filename using lat/lon
        filename = f"lat_{lat}_lon_{lon}.csv"
        csv_file_path = os.path.join(csv_file_dir, filename)
        group_df.rename(mapper=CMIP6_TO_READABLE, inplace=True, axis=1)
        # Save individual lat/lon DataFrame to CSV
        save_dataframe_to_csv(group_df, csv_file_path)
        print(f"Saved {csv_file_path}")
        progress +=1
        progress_percentage = int((progress / total_progress) * 100)
        progress_bar.progress(progress / total_progress, text=f"Restructuration Progress: {progress_percentage}%")
    

def zip_csv_files(csv_dir, zip_name):
    """
    Zip all CSV files in the directory
    """
    # Create zip file
    shutil.make_archive(zip_name, 'zip', csv_dir)
    return f"{zip_name}.zip"


def create_zip_and_save(csv_dir, save_folder):
    """
    Create a ZIP file from CSV files in a directory and save it to a specific folder.
    """
    # Ensure the save folder exists
    if not os.path.exists(save_folder):
        os.makedirs(save_folder, exist_ok=True)

    zip_filename = f"{st.session_state.location}.zip"
    # Define the ZIP file path
    zip_file_path = os.path.join(save_folder, zip_filename)

    # Create the ZIP file and save it
    with ZipFile(zip_file_path, 'w') as zip_file:
        for csv_file in os.listdir(csv_dir):
            if csv_file.endswith('.csv'):
                file_path = os.path.join(csv_dir, csv_file)
                zip_file.write(file_path, csv_file)

    print(f"ZIP file saved at: {zip_file_path}")  # Log the saved location

    return zip_file_path  # Return the path of the saved ZIP file

def create_zip_download_button(csv_dir, button_text="Download ZIP file"):
    """
    Create in-memory zip and Streamlit download button
    """
    # Create in-memory buffer
    buffer = io.BytesIO()
    
    with ZipFile(buffer, 'w') as zip_file:
        for csv_file in os.listdir(csv_dir):
            if csv_file.endswith('.csv'):
                file_path = os.path.join(csv_dir, csv_file)
                zip_file.write(file_path, csv_file)
    
    buffer.seek(0)
    
    # Create download button
    st.download_button(
        label=button_text,
        data=buffer,
        file_name="climate_data.zip",
        mime="application/zip"
    )

def convert_variable_units(df):
    """
    Convert certain variables to the correct units.
    - Temperature is converted from Kelvin to Celsius.
    - Precipitation is converted from kg m^-2 s^-1 to mm
    - Wind speed is converted from m s^-1 to km h^-1
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


# -------------------------------------------
# --- Main function to request CMIP6 data ---
# -------------------------------------------

def cmip6_request(selected_shape_folder):
    """
    Main function to request CMIP6 data.
    Args:
        selected_shape_folder (list): List of selected shape folders.
    """
    if selected_shape_folder:
        gdf_list = []
        st.session_state.gdf_list = []
        for folder in selected_shape_folder:

            # Open the shape file and get its content
            path_to_shapefolder = os.path.join(ZIP_FOLDER, folder)
            shape_file = [file for file in os.listdir(path_to_shapefolder) if file.endswith(".shp")][0]
            shapefile_path = os.path.join(path_to_shapefolder, shape_file)
            gdf = read_shape_file(shapefile_path)

            # Ask the user to define a buffer distance if not beginner
            if st.session_state.mode == "Beginner":
                buffer_distance = 0.2
            else:
                buffer_distance = st.number_input(
                    label=f"Enter buffer distance for {folder} in degree (0.25 is about 25 kilometers):",
                    min_value=0.0, 
                    step=0.1,
                    value=0.0,
                    format="%0.3f",
                    key=folder
                )
            st.session_state.gdf_list.append(copy(gdf))

            # Apply the buffer if the distance is greater than 0
            if buffer_distance > 0:
                gdf["geometry"] = gdf["geometry"].buffer(buffer_distance, resolution=0.05)
                if st.session_state.mode == "Expert":
                    st.success(f"Buffer of {buffer_distance} applied to {folder}")
            gdf_list.append(gdf)
        
        # Concatenates the Geodataframes together
        st.session_state.combined_gdf = pd.concat(st.session_state.gdf_list, ignore_index=True)
        combined_gdf = pd.concat(gdf_list, ignore_index=True)
        empty_request_gdf = pd.DataFrame()

        # Make the empty request to show the user how it will look like in terms of resolution
        for gdf in gdf_list:
            df_unique = make_empty_request(gdf.total_bounds)
            if df_unique is not None:
                empty_request_gdf = pd.concat([empty_request_gdf, df_unique], ignore_index=True)

        # Display
        with st.expander(label="Your coordinates"):
            displayed_gdf = empty_request_gdf[["lat", "lon"]]
            st.dataframe(data=displayed_gdf, height=DATAFRAME_HEIGHT, use_container_width=True)

        if not empty_request_gdf.empty:
            map_empty_request(combined_gdf, empty_request_gdf)
            make_whole_request(combined_gdf.total_bounds, nc_directory=NC_FILE_DIR)