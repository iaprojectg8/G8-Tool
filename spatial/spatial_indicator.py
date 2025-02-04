from utils.imports import *
from results.main_calculation import calculate_scores, preparing_dataframe_for_plot, introduce_season_shift_in_calculation
from results.helpers import aggregate_category

from parametrization.helpers import period_filter
from parametrization.update_indicator import indicator_editing

from spatial.rasterization import rasterize_data, display_raster_with_slider, raster_download_button

from results.custom_indicators import heat_index_spatial_indicator, display_raster_with_slider_heat_index


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


def get_only_required_variable(dataframes_dict, variable):
    for (df_key, df) in dataframes_dict.items() :
            if isinstance(variable, list):  # Check if variable is a list
                selected_columns = variable + ["lat", "lon"]  # Create a new list
            else:
                selected_columns = [variable, "lat", "lon"]  # Combine into a list
            
            df = df.loc[:, selected_columns]  # Use the new variable for column selection
            dataframes_dict[df_key] = df
    return dataframes_dict

def spatial_calculation_for_raster(row, below_thresholds, above_thresholds, df, score_name, variable, periods):
    """
    This needs to be cleaned
    """
     # Get the score_column
    lat, lon = df.at[df.index[0],"lat"], df.at[df.index[0],"lon"]
    unit, df_yearly_var, aggregated_column_name = calculate_scores(row,df, score_name, variable,spatial=1)

    # Plot preparation
    df_yearly = preparing_dataframe_for_plot(df_yearly_var, periods, score_name)
    score_column = f"yearly_indicator_{score_name}"
    
    # Asks the user to choose the aggregation type and then aggregates the data
    aggregation_type = "Category Mean"
    # aggregation_type = st.selectbox(label="Aggregation Type", options=EXPOSURE_AGGREGATION, key=f"aggregation_type_{index}_{additional_key}")
    df_period = aggregate_category(aggregation_type, df_yearly, score_column, aggregated_column_name, below_thresholds, above_thresholds)
    df_period['lat'] = lat
    df_period['lon'] = lon
    sumup_df = df_period.pivot_table(
        index=['lat', 'lon'], 
        columns='period', 
        values='absolute_score', # ['absolute_score', 'category', 'color', 'exposure_prob'], 
        aggfunc='first',
        observed=False
    )

    return sumup_df

def filter_all_the_dataframe(dataframes:dict, long_period):
    for key_df, df in dataframes.items():
        # do the filters that have been done on the first dataframe of the dictionary
        data_long_period_filtered = period_filter(df, period=long_period)
        dataframes[key_df] = data_long_period_filtered

    return dataframes

def spatial_calculation(df_season, df_indicators_parameters: pd.DataFrame,df_checkbox:pd.DataFrame, dataframes_dict, 
                         season_start, season_end,periods, shape_gdf, raster_resolution):
    """
    Perform calculations and generate plots for each indicator in the given indicator parameters DataFrame.

    Args:
        df_season (pandas.DataFrame): Seasonal data containing variables for calculation.
        df_indicators_parameters (pandas.DataFrame): DataFrame containing the parameters for each indicator.
        all_year_data (pandas.DataFrame): Data containing all yearly data to be used for shifting and calculation.
        season_start (int): The starting month for the season.
        season_end (int): The ending month for the season.
        periods (list): List of periods for categorization.

    Returns:
        pandas.DataFrame: A DataFrame containing the yearly data after processing all indicators.
    """
    # Store all newly created columns in a dictionary to merge later
    df_yearly = pd.DataFrame()
    _, col, _ = st.columns([1, 2, 1])
    with col:
        general_compute = st.button(label="Compute rasters for all indicators", key = f"general_compute", use_container_width=True,type="primary")


    tabs = st.tabs(list(df_indicators_parameters["Name"].values))
    # Iterating over indicators dataframe
    for (index, row), (j, row_checkbox) in zip(df_indicators_parameters.iterrows(), df_checkbox.iterrows()):
        with tabs[index]:
            
            # Offer the possibility to edit the indicator

            indicator_editing(df_season, season_start, season_end, row, row_checkbox, index)
            
            # Initializing useful variables
            variable = row["Variable"]
            dataframes_dict_filtered = get_only_required_variable(copy(dataframes_dict), variable)
            score_name = row["Name"]
            season_start_shift=row["Season Start Shift"]
            season_end_shift= row["Season End Shift"]
            below_thresholds=copy(row["Yearly Threshold Min List"])
            above_thresholds= copy(row["Yearly Threshold Max List"])

            
            df_raster = pd.DataFrame()
            # Season shift handling
            if dataframes_dict_filtered is not None:
                random_dataframe = rd.choice(list(dataframes_dict_filtered.values()))           
                if ((isinstance(variable,list) and all(var in list(random_dataframe.columns) for var in variable)) 
                    or (not isinstance(variable,list) and (variable in random_dataframe.columns))):
                    with st.spinner("Handling season shift"):
                        
                        if season_start is not None or season_end is not None:
                            if (not pd.isna(season_start_shift) or not pd.isna(season_end_shift)
                                or season_start_shift is not None or season_end_shift is not None):
                                for (df_key, df), (df_all_key, df_all) in zip(dataframes_dict_filtered.items(), dataframes_dict.items()):
                                    df = introduce_season_shift_in_calculation(season_start, season_start_shift, season_end, season_end_shift, df_all)
                       
                        # Specific part to allow crossed variable computation
                    with st.spinner("Computing raster"):
                        _, col, _ = st.columns([1, 2, 1])
                        with col:
                            specific_compute = st.button(label="Compute raster for current indicator", key=f"compute_raster{index}",
                                                         use_container_width=True,
                                                         type="secondary")
                        if row["Indicator Type"] == "Crossed Variables":
                            if specific_compute or general_compute:
                                for df in dataframes_dict_filtered.values():
                                    sumup_df = heat_index_spatial_indicator(df, periods)
                                    df_raster = pd.concat([df_raster, sumup_df])
                                rasterize_data(df_raster, shape_gdf=shape_gdf, resolution=raster_resolution, score_name=score_name)
                        
                        # All the other parts are located here                                        
                        else:
                            
                            if specific_compute or general_compute:
                                for df in dataframes_dict_filtered.values():

                                    sumup_df = spatial_calculation_for_raster(row, below_thresholds, above_thresholds, df, score_name, variable, periods)
                                    df_raster = pd.concat([df_raster, sumup_df])
                                    
                                rasterize_data(df_raster, shape_gdf=shape_gdf, resolution=raster_resolution, score_name=score_name)
 
                else:
                    st.warning("Your variable is not in the taken in the dataframes dictionary, please click on 'Filter the data' button to get it")
                if len(st.session_state.raster_params) !=0 and score_name in st.session_state.raster_params:
                    try :
                        if row["Indicator Type"] == "Crossed Variables":
                            display_raster_with_slider_heat_index(score_name, periods)
                            raster_download_button(score_name, periods, index=index)
                        else:
                            display_raster_with_slider(score_name, periods)
                            raster_download_button(score_name, periods, index=index)
                    except IndexError as e:
                        st.error(f"Index out of range error: You changed something with the periods, please recompute the raster")
                    except Exception as e:
                        st.error(f"An error occurred while rendering the rasters: {e}")
                        
                
    return df_yearly


