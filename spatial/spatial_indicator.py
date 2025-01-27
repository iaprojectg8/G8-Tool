from utils.imports import *


def extract_csv_from_zip(zip_file, extract_to):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def read_csv_files_from_directory(directory):

    # L'utilisation de glob est surement plus approprié dans ce genre de cas
    extracted_dir_name = os.listdir(directory)[0]
    extracted_dir_path = os.path.join(directory, extracted_dir_name)
    
    # Just to manage different zip file structures
    if os.path.isfile(extracted_dir_path):
        extracted_dir_path = directory

    csv_files = [f for f in os.listdir(extracted_dir_path) if f.endswith('.csv')]
    dataframes = {}
    for file in csv_files:
        file_path = os.path.join(extracted_dir_path, file)
        dataframes[file] = pd.read_csv(file_path)
    get_min_and_max_year(dataframes)
    return dataframes

def get_min_and_max_year(dataframes:dict):
    df = copy(dataframes[list(dataframes.keys())[0]])
    df["date"] = pd.to_datetime(df["date"])
    min_year = df['date'].min().year
    max_year = df['date'].max().year
    st.session_state.min_year = min_year
    st.session_state.max_year = max_year

def extract_coordinates(dataframes):
    coordinates = []
    for df in dataframes.values():
        if not df.empty:
            lat, lon = df.iloc[0][['lat', 'lon']]
            coordinates.append((lat, lon))
    gdf = gpd.GeoDataFrame(coordinates, columns=['lat', 'lon'])
    gdf['geometry'] = gdf.apply(lambda row: Point(row['lon'], row['lat']), axis=1)
    return gdf


def make_zone_average(dataframes:dict):
    # Open all the files with glob and put it in a list of dataframes

    # Step 2: Combine all datasets
    combined_df = pd.concat(dataframes.values(), ignore_index=False)
    mean_df = combined_df.groupby(combined_df.index).mean()
    st.session_state.all_df_mean = mean_df



def put_date_as_index(dataframe_dict:dict):
    for key, df in dataframe_dict.items():
        print(df.index)
        df['date'] = pd.to_datetime(df['date'])  # Ensure the 'date' column is in datetime format
        df.set_index('date', inplace=True)  # Set the 'date' column as the index
        dataframe_dict[key] = df
    return dataframe_dict


def spatial_indicator_management(df_indicator_sample:pd.DataFrame, all_df_dict):
    """
    Manages spatial indicators based on user-selected periods, variables, seasons, and parameters.

    Args:
        df_ind (pd.DataFrame): The initial dataframe containing spatial indicators.
        all_df_dict (dict): Dictionary of all dataframes to process.
    """

    key = "spatial_indicator_part"
    set_title_2("Period")

    # User setting the periods of interest
    long_period = (long_period_start, long_period_end) = select_period(key=key)
    smaller_period_length  = st.select_slider("Choose the length of smaller period to see the evolution of your data on them:",
                                              options=PERIOD_LENGTH, 
                                              key=f"smaller_period{key}")
    periods = split_into_periods_indicators(smaller_period_length, long_period_start, long_period_end)

    # Loading data and applying first filters
    df_indicator_sample = period_filter(df_indicator_sample, period=long_period)
    st.dataframe(df_indicator_sample, height=DATAFRAME_HEIGHT, use_container_width=True)
    
    # Propose variables related to the dataset loaded 
    set_title_2("Variable Choice")
    df_indicator_sample = column_choice(df_indicator_sample)

    # Variables intitialization
    season_start, season_end = None, None

    if not df_indicator_sample.empty:
        st.dataframe(df_indicator_sample, height=DATAFRAME_HEIGHT, use_container_width=True) 

        # Season handdling
        set_title_2("Season Choice")
        if st.checkbox("Need a season or a period study", value=st.session_state.season_checkbox):
            season_start, season_end = select_season()
            df_indicator_sample_season = select_data_contained_in_season(df_indicator_sample, season_start, season_end)
            st.dataframe(df_indicator_sample_season, height=DATAFRAME_HEIGHT, use_container_width=True)
        else:
            df_indicator_sample_season = df_indicator_sample
        
        # Indicators parametrization handling
        set_title_2("Parametrize Indicators")

        # Load indicators from CSV
        if st.checkbox(label="Load indicators from CSV"):
            df_uploaded = upload_csv_file()
            
            if df_uploaded is not None and not df_uploaded.equals(st.session_state.uploaded_df):
                df_checkbox = fill_df_checkbox(df_uploaded)
                st.session_state.uploaded_df = df_uploaded
                st.session_state.df_indicators = copy(df_uploaded)
                st.session_state.df_checkbox = df_checkbox

        # Building the indicator in a popover
        with st.popover("Create Indicator", use_container_width = True):
            indicator_building(df_indicator_sample_season, season_start, season_end)


        # Display an indicator summary
        if not st.session_state.df_indicators.empty:
            # The copy done is only to display the indicators dataframe on the app
            df_indicator_copy = copy(st.session_state.df_indicators)
            df_indicator_copy["Variable"] = df_indicator_copy["Variable"].astype(str)
            st.dataframe(df_indicator_copy, use_container_width=True)
            download_indicators(st.session_state.df_indicators)

            # Need to calculate score with this parameters
            set_title_2("Indicators Calculation & Rasters Building")
            shape_gdf  = read_shape_zipped_shape_file()
            raster_resolution = st.number_input("Choose the raster resolution",
                                                                min_value=0.001, max_value=1., 
                                                                value=0.005,
                                                                format="%0.3f")
            if st.button("Filter the data"):
                with st.spinner("Filter all the dataframes"):
                    dataframes_dict = filter_all_the_dataframe(dataframes=copy(all_df_dict), long_period=long_period)
                    st.session_state.dataframes = dataframes_dict
            spatial_calculation(df_indicator_sample_season, st.session_state.df_indicators, 
                                st.session_state.df_checkbox,st.session_state.dataframes, 
                                all_df_dict, season_start, season_end, periods, shape_gdf, raster_resolution)
