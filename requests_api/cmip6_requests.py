from utils.imports import *
from utils.variables import *
from lib.data_process import select_period_cmip6
from layouts.layout import *


def reset_directory(dir_name):
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)
    else:
        shutil.rmtree(dir_name) 
        os.makedirs(dir_name)

def widget_init():
    # This part will in the future be located in the variable file
    
    # please do a streamlit multiselect to choose the variables

    if st.checkbox(label="Take all variables"):
        selected_variables = st.multiselect("Chose variable to extract", 
                                            READABLE_TO_CMIP6.keys(), 
                                            default=READABLE_TO_CMIP6.keys())
    else:
        selected_variables = st.multiselect("Chose variable to extract", 
                                            READABLE_TO_CMIP6.keys(), 
                                            default=np.random.choice(list(READABLE_TO_CMIP6.keys())))
    real_selected_variables = list(map(lambda key : READABLE_TO_CMIP6.get(key),selected_variables))
    selected_model = st.selectbox("Chose the model to use", MODEL_NAMES_CMIP6)
    ssp = st.selectbox(label="Chose the ssp to use", options=SSP)
    experiment = st.selectbox(label="Chose the experiment to use", options=EXPERIMENTS)
    (long_period_start, long_period_end) = select_period_cmip6(key="cmip6", ssp=ssp)
    years = list(range(long_period_start, long_period_end+1))
    print(years)
    

    return real_selected_variables, selected_model, ssp, experiment, years



def make_whole_request(bounds):

    selected_variables, selected_model, ssp, experiment, years = widget_init()
    choice = ask_reset_directory(NC_FILE_DIR)
    # Add a progress bar to see the evolution of the request

    if st.button("Make request", key="cmip6_button"):
        # Reset the directory that will contain the data files
        if choice == "Yes":
            reset_directory(NC_FILE_DIR)
            st.success("Your files have been deleted")
        elif choice == "No":
            st.success("Your files are still there")

        total_requests = len(selected_variables) * len(years)
        progress_bar = st.progress(0, text="Request Progress: 0%")
        progress = 0
        # one request about 15 points, takes apoxximatly 10 seconds for one year, one variable
        for variable in selected_variables:
            for year in years:
                make_year_request(variable, selected_model, ssp, experiment, bounds, year)
                progress += 1
                progress_percentage = int((progress / total_requests) * 100)

                progress_bar.progress(progress / total_requests, text=f"Request Progress: {progress_percentage}%")
    if st.button("Convert everything you downloaded into CSV zip"):
        # Example usage
        
        process_all_nc_files(NC_FILE_DIR, CSV_FILE_DIR)
        create_zip_download_button(CSV_FILE_DIR, button_text="Download ZIP file")
                
            
def make_year_request(variable, model, ssp, experiment, bounds, year):
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
        with open(f"{NC_FILE_DIR}/{year}_{variable}.nc", "wb") as f:
            f.write(response.content)
    except Exception as e:
        print(e)
    
        



# This is another part that handle the netcdf requested files
def handle_request_files(years, variable):
    """
    This function will handle the netcdf files requested from the NASA server
    Args:
        years (list): The years to extract
        variable (str): The variable
    Returns:
        pd.DataFrame: The concatenated dataframe
    """
    for year in years:
        dataset = xr.open_dataset(f"{NC_FILE_DIR}/{year}.nc", engine="netcdf4",) # Adjust the engine as needed
        df = dataset[["time","lat", "lon", f"{variable}"]].to_dataframe().reset_index()
        entire_dataframe = pd.concat([entire_dataframe, df], ignore_index=True)

    return entire_dataframe


# --------------------------
# --- Empty request part ---
# --------------------------

def make_empty_request(bounds):
    """
    This function will make an empty request to the NASA server in order to see the resolution of the data
    Args:
        bounds (tuple): The bounds of the area to extract
    """
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
            df = df[["lat", "lon"]].drop_duplicates()
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
        st.write(f'{existing_files}')
        choice = st.radio("Do you want to empty it", ["Yes", "No"])
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
    df = dataset[["time","lat", "lon", f"{variable}"]].to_dataframe().reset_index()

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
    print(years)
    years.sort()
    print(years)
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
    print(whole_df)
    progress_bar = st.progress(0, text="Restructuration Progress: 0%")
    progress = 0
    total_progress = len(whole_df.groupby(['lat', 'lon']))
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
    print(df)
    # Convert all the temperature field from Kelvin to Celsius
    df["tas"] = df["tas"] - 273.15
    df["tasmin"] = df["tasmin"] - 273.15
    df["tasmax"] = df["tasmax"] - 273.15
    # Convert all the precipitation field from kg m^-2 s^-1 to mm multiplied by 86400 to get the daily precipitation
    df["pr"] = df["pr"] * 86400 
    # Convert the wind speed from m s^-1 to km h^-1
    df["sfcWind"] = df["sfcWind"] * 3.6
    # Convert the radiation from W m^-2 to MJ m^-2 day^-1
    # df["rsds"] = df["rsds"] * 0.0864
    # df["rlds"] = df["rlds"] * 0.0864

    return df