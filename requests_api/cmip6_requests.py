from utils.imports import *
from utils.variables import *
from lib.data_process import select_period_cmip6


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
                                            UNIT_DICT.keys(), 
                                            default=UNIT_DICT.keys())
    else:
        selected_variables = st.multiselect("Chose variable to extract", 
                                            UNIT_DICT.keys(), 
                                            default=np.random.choice(list(UNIT_DICT.keys())))
    selected_model = st.selectbox("Chose the model to use", MODEL_NAMES_CMIP6)
    ssp = st.selectbox(label="Chose the ssp to use", options=SSP)
    experiment = st.selectbox(label="Chose the experiment to use", options=EXPERIMENTS)
    (long_period_start, long_period_end) = select_period_cmip6(key="cmip6", ssp=ssp)
    years = list(range(long_period_start, long_period_end+1))
    print(years)
    

    return selected_variables, selected_model, ssp, experiment, years


def make_whole_request(bounds):

    selected_variables, selected_model, ssp, experiment, years = widget_init()
    # Reset the directory that will contain the data files
       
    # reset_directory(NC_FILE_DIR)
    # reset_directory(CSV_FILE_DIR)
    # Add a progress bar to see the evolution of the request
    if st.button("Make request", key="cmip6_button"):
        for variable in selected_variables:
            for year in years:
                make_year_request(variable, selected_model, ssp, experiment, bounds, year)
                time.sleep(2)
            
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
    min_lat, max_lat, min_lon, max_lon = bounds
    params = {
        "var": "pr",
        "north": max_lat,
        "west": min_lon,
        "east": max_lon,
        "south": min_lat
    }

    coordinates_part=(f"?var=pr&north={params["north"]}&west={params["west"]}&east={params["east"]}&south={params["south"]}&"
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
    
    print("before to try")
    try:
        # Send a GET request to the specified URL
        print("before to launch the request")
        response = requests.get(url)
        response.raise_for_status()
        
        with open(f"{EMPTY_REQUEST_FOLDER}/{year}.nc", "wb") as f:
            f.write(response.content)
        if response.status_code == 200:
            st.success("Empty request successful")   
            df = handle_empty_request_files(year, variable)
            df = df[["lat", "lon"]].drop_duplicates()
            gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat))
            gdf.set_crs("EPSG:4326", inplace=True)
            return gdf
    except Exception as e:
        print(f"An error occurred: {e}")
        st.error(f"An error occurred: {e}")


    


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
