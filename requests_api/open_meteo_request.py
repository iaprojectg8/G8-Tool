from utils.imports import *
from utils.variables import *
from maps_related.main_functions import read_shape_file, main_map




# This open the available coordinates of open meteo that we will take
def build_api_params(lat, lon, model, start_year, end_year, variable_list):
    """
    Constructs the API parameters for the request based on latitude, longitude, and variables.
    
    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
    
    Returns:
        dict: Parameters for the API request.
    """
    return {
        "latitude": lat,
        "longitude": lon,
        "start_date": f"{start_year}-01-01",
        "end_date": f"{end_year}-12-31",
        "models": model, #"MRI_AGCM3_2_S",
        "daily": variable_list,
        "timezone": "auto",
        "wind_speed_unit": "ms"
    }


def gdf_to_df(gdf):
    """
    Converts a GeoDataFrame to a DataFrame with latitude and longitude columns.
    Args:
        gdf (gpd.GeoDataFrame): A GeoDataFrame containing geometry data.
    Returns:
        pd.DataFrame: A DataFrame with latitude and longitude columns.
    """
    df = gdf.copy()
    df['lat'] = df.geometry.y
    df['lon'] = df.geometry.x
    return df.drop(columns='geometry')

def get_lat_lon(row):
    """
    Extracts latitude and longitude from a DataFrame row.
    
    Args:
        row (pd.Series): A row from the DataFrame containing 'lat' and 'lon' fields.
    
    Returns:
        tuple: A tuple containing the latitude and longitude.
    """
    lat = row["lat"]
    lon = row["lon"]

    return lat, lon

def get_lat_lon_in_gdf(row):

    lat = row.geometry.y
    lon = row.geometry.x

    return lat, lon


def get_data_from_open_meteo(url, params):
    """
    Fetches weather data from the Open Meteo API using specified URL and parameters.
    
    Args:
        url (str): The API endpoint URL for fetching weather data.
        params (dict): Parameters for the API request.
    
    Returns:
        dict: The API response containing weather data.
    """
    # Initialization
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    return response

def select_period(key):
    """
    Allows the user to select a data period using an interactive Streamlit slider.

    Returns:
        tuple: The start and end values of the selected period.
    """
    # Define the initial limits for the slider
    period_start= st.session_state.min_year
    period_end= st.session_state.max_year

    # Display the slider that allows the user to select the bounds
    period_start, period_end = st.slider(
        "Select the data period:",
        min_value=period_start, 
        max_value=period_end,
        value=(period_start, period_end),
        key=key)      
    return period_start, period_end

def fill_daily_dict(daily, lat, lon):
    """
    Fills a dictionary with daily weather data including date, latitude, and longitude.
    
    Args:
        daily (object): Object containing daily weather data from the API response.
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
        
    Returns:
        dict: A dictionary with the date, latitude, longitude, and weather variables.
    """
    daily_data = {
        "date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        ),
        "lat": lat,
        "lon": lon
    }
    # Loop through the variable list and extract data using their respective indices
    for var_idx, var_name in enumerate(VARIABLES_LIST):
        daily_data[var_name] = daily.Variables(var_idx).ValuesAsNumpy()

    return daily_data


def save_daily_dataset(daily_data, dataset_folder, filename_base, index, lat, lon):
    """
    Saves the daily weather data to a CSV file.
    
    Args:
        daily_data (dict): Dictionary containing daily weather data.
        dataset_folder (str): Path to the folder where the file will be saved.
        filename_base (str): Base name for the output CSV file.
        index (int): Index for distinguishing multiple output files.
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
    """
    daily_dataframe = pd.DataFrame(data = daily_data)
    os.path.join(dataset_folder, filename_base)
    daily_dataframe.to_csv(f'{dataset_folder}/{filename_base}_{index}.csv', index=False)
    print(f"Request number {index} done for Lat:{lat}, and Lon:{lon}")




# --- Main function to get openmeteo data from Gambia ---
def request_all_data(coordinates:gpd.GeoDataFrame, dataset_folder, filename_base, model, start_year, end_year, variable_list):
    """
    Orchestrates the process of requesting and saving daily weather data for multiple coordinates.
    
    Args:
        coordinates_csv (str): Path to the CSV file containing coordinates.
        dataset_folder (str): Path to the folder where the results will be saved.
    """

    if os.path.isdir(dataset_folder):
        print("Dataset folder already exist")
    else:
        os.makedirs(dataset_folder)
        print("Dataset folder created")

    url ="https://climate-api.open-meteo.com/v1/climate"

    # Take only the root name, and get rid of the resolution
    model = model.split(" ")[0]
    total = len(coordinates)
    progress_bar = st.progress(0, f"Request progression - {0}%")
    for index, row in coordinates.iterrows():
       
        lat, lon = get_lat_lon(row)
        params = build_api_params(lat, lon, model, start_year, end_year, variable_list)

        try:
            
            response = get_data_from_open_meteo(url, params)
            if response:
                
                daily = response.Daily()
                daily_data = fill_daily_dict(daily, lat, lon)
                save_daily_dataset(daily_data, dataset_folder, filename_base, index, lat, lon)

            else:
                print(f"No data for point: Latitude {lat}, Longitude {lon}")
            
        except Exception as e:
            st.error(f"Error for point: Latitude {lat}, Longitude {lon} - {str(e)}")
            break
        # Time sleep here to not causing trouble reaching the request limit
        time.sleep(2)
        progress_bar.progress((index + 1) / total, f"Request progression - {round((index + 1)*100 / total)}%")
    st.success("All the requests done")





# Main function
def open_meteo_request(selected_shape_folder):
    """
    Main function to request data from Open Meteo API.
    Args:
        selected_shape_folder (list): List of selected shape files.
    """
    if selected_shape_folder:
        gdf_list = []
        for file in selected_shape_folder:
            path_to_shapefile = os.path.join(ZIP_FOLDER, file)
            shape_file = [file for file in os.listdir(path_to_shapefile) if file.endswith(".shp")][0]
            shapefile_path = os.path.join(path_to_shapefile, shape_file)

            gdf :gpd.GeoDataFrame = read_shape_file(shapefile_path)
            # Ask the user to define a buffer distance
            buffer_distance = st.number_input(
                label=f"Enter buffer distance (in the same units as {file} coordinates):",
                min_value=0.0, 
                step=0.1,
                value=0.0,
                format="%0.3f",
                key=file
            )
            
            # Apply the buffer if the distance is greater than 0
            if buffer_distance > 0:
                gdf["geometry"] = gdf["geometry"].buffer(buffer_distance, resolution=0.05)
                st.success(f"Buffer of {buffer_distance} applied to {file}")

            gdf_list.append(gdf)
        combined_gdf = pd.concat(gdf_list, ignore_index=True)
        df = main_map(combined_gdf)
        print(len(df))
        with st.expander(label="Your coordinates"):
            st.dataframe(data=df, height=DATAFRAME_HEIGHT, use_container_width=True)
        if st.checkbox(label="Take all variables"):
            selected_variables = st.multiselect("Chose variable to extract", 
                                                UNIT_DICT.keys(), 
                                                default=UNIT_DICT.keys())
        else:
            selected_variables = st.multiselect("Chose variable to extract", 
                                                UNIT_DICT.keys(), 
                                                default=np.random.choice(list(UNIT_DICT.keys())))
        selected_model = st.selectbox("Chose the model to use", MODEL_NAMES)
        (long_period_start, long_period_end) = select_period(key="request")

        if st.button(label="Start the Request"):
            request_all_data(coordinates=df,
                                dataset_folder=OPEN_METEO_FOLDER,
                                filename_base="moroni_extraction",
                                model=selected_model,
                                start_year=long_period_start,
                                end_year=long_period_end,
                                variable_list=selected_variables)