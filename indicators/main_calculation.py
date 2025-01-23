from utils.imports import *
from utils.variables import *
from indicators.calculation import *
from indicators.plot import *
from indicators.parametrization.update_indicator import * 
from indicators.custom_indicators import heat_index_indicator, heat_index_spatial_indicator, display_raster_with_slider_heat_index
from spatial.rasterization import rasterize_data, display_raster_with_slider, raster_download_button, read_shape_zipped_shape_file
from lib.data_process import period_filter


# ------------------------------------------------
# --- Calculation of different indicators type ---
# ------------------------------------------------

def introduce_season_shift_in_calculation(season_start, season_start_shift, season_end, season_end_shift, all_year_data):
    """
    Adjusts the season period based on the start and end season shifts, and filters the data accordingly.

    Args:
        season_start (int): The start month of the season.
        season_start_shift (int or None): The shift to be applied to the start month of the season.
        season_end (int): The end month of the season.
        season_end_shift (int or None): The shift to be applied to the end month of the season.
        all_year_data (pandas.DataFrame): The dataset containing the yearly data to be adjusted.

    Returns:
        pandas.DataFrame: A filtered DataFrame with the adjusted season period.
    """
    if (season_start_shift is not None  and season_end_shift is not None
        and not pd.isna(season_start_shift) and not pd.isna(season_end_shift)):
        df_season_temp = all_year_data[(all_year_data.index.month >= season_start-season_start_shift) 
                                & (all_year_data.index.month <= season_end+season_end_shift)]
        
    elif season_start_shift is not None and not pd.isna(season_start_shift):
        df_season_temp = all_year_data[(all_year_data.index.month >= season_start-season_start_shift) & (all_year_data.index.month <= season_end)]

    elif season_end_shift is not None and not pd.isna(season_end_shift):
        df_season_temp = all_year_data[(all_year_data.index.month >= season_start) & (all_year_data.index.month <= season_end+season_end_shift)]
    
    else:
        df_season_temp = all_year_data

    return df_season_temp

def introduce_season_shift_in_spatial_calculation(season_start, season_start_shift, season_end, season_end_shift, all_year_data):
    """
    Adjusts the season period based on the start and end season shifts, and filters the data accordingly.

    Args:
        season_start (int): The start month of the season.
        season_start_shift (int or None): The shift to be applied to the start month of the season.
        season_end (int): The end month of the season.
        season_end_shift (int or None): The shift to be applied to the end month of the season.
        all_year_data (pandas.DataFrame): The dataset containing the yearly data to be adjusted.

    Returns:
        pandas.DataFrame: A filtered DataFrame with the adjusted season period.
    """
    if (season_start_shift is not None  and season_end_shift is not None
        and not pd.isna(season_start_shift) and not pd.isna(season_end_shift)):
        df_season_temp = all_year_data[(all_year_data.index.month >= season_start-season_start_shift) 
                                & (all_year_data.index.month <= season_end+season_end_shift)]
        
    elif season_start_shift is not None and not pd.isna(season_start_shift):
        df_season_temp = all_year_data[(all_year_data.index.month >= season_start-season_start_shift) & (all_year_data.index.month <= season_end)]

    elif season_end_shift is not None and not pd.isna(season_end_shift):
        df_season_temp = all_year_data[(all_year_data.index.month >= season_start) & (all_year_data.index.month <= season_end+season_end_shift)]
    
    else:
        df_season_temp = all_year_data

    return df_season_temp

def season_aggregation_calculation(row,df_season_temp, score_name, variable):
    """
    Perform seasonal aggregation and score calculation based on yearly aggregation and thresholds.

    Args:
        row (pd.Series): Row of the updated indicator with relevant information for aggregation and thresholds.
        df_season_temp (pandas.DataFrame): The filtered seasonal data.
        score_name (str): The name of the score to be calculated.
        variable (str): The variable to use for aggregation.

    Returns:
        tuple: A DataFrame with the aggregated yearly values and the name of the aggregated column.
    """
    df_yearly_var, aggregated_column_name = make_yearly_agg(df_season_temp,variable, row["Yearly Aggregation"])

    df_yearly_var = indicator_score(
        df_yearly_var,
        aggregated_column_name,
        score_name,
        row["Yearly Threshold Min List"],
        row["Yearly Threshold Max List"])
    return df_yearly_var, aggregated_column_name
    
def outlier_days_calculation(row, df_season_temp, score_name, variable, spatial):
    """
    Calculate outlier days based on daily thresholds and yearly aggregation.

    Args:
        row (pd.Series): Row of the updated indicator with relevant information for thresholds and aggregation.
        df_season_temp (pandas.DataFrame): The filtered seasonal data.
        score_name (str): The name of the score to be calculated.
        variable (str): The variable to use for aggregation.

    Returns:
        tuple: A DataFrame with the aggregated yearly values and the name of the aggregated column.
    """
    df_daily, indicator_column = daily_indicators(df_season_temp, variable, row["Daily Threshold Min"], row["Daily Threshold Max"])
    if not spatial:
        with st.expander("Show Daily Dataframe"):
            st.dataframe(df_daily, height=DATAFRAME_HEIGHT,use_container_width=True)

    df_yearly_var, aggregated_column_name = make_yearly_agg(df_season_temp,indicator_column, row["Yearly Aggregation"])
    df_yearly_var = indicator_score(
        df_yearly_var,
        aggregated_column_name,
        score_name,
        row["Yearly Threshold Min List"],
        row["Yearly Threshold Max List"])
    
    return df_yearly_var, aggregated_column_name

def consecutive_outlier_days_calculation(row, df_season_temp, score_name, variable, spatial):
    """
    Calculate consecutive outlier days using cumulative sum of daily indicators and yearly aggregation.

    Args:
        row (pd.Series): Row of the updated indicator with relevant information for thresholds and aggregation.
        df_season_temp (pandas.DataFrame): The filtered seasonal data.
        score_name (str): The name of the score to be calculated.
        variable (str): The variable to use for aggregation.

    Returns:
        tuple: A DataFrame with the aggregated yearly values and the name of the aggregated column.
    """
    df_daily, indicator_column = daily_indicators(df_season_temp, variable, row["Daily Threshold Min"], row["Daily Threshold Max"])
    df_daily["cumulated_days_sum"] = df_season_temp.groupby(df_season_temp.index.year)[indicator_column].transform(reset_cumsum)

    if not spatial:
        with st.expander("Show Daily Dataframe"):
            st.dataframe(df_daily, height=DATAFRAME_HEIGHT,use_container_width=True)

    df_yearly_var, aggregated_column_name = make_yearly_agg(df_season_temp,"cumulated_days_sum", row["Yearly Aggregation"])
    
    df_yearly_var = indicator_score(
        df_yearly_var,
        aggregated_column_name,
        score_name,
        row["Yearly Threshold Min List"],
        row["Yearly Threshold Max List"])
    
    return df_yearly_var, aggregated_column_name

def sliding_window_calculation(row, df_season_temp, score_name, variable, spatial):
    """
    Perform sliding window calculation based on window length and aggregation, and yearly aggregation.

    Args:
        row (pd.Series): Row of the updated indicator with relevant information for window parameters and aggregation.
        df_season_temp (pandas.DataFrame): The filtered seasonal data.
        score_name (str): The name of the score to be calculated.
        variable (str): The variable to use for aggregation.

    Returns:
        tuple: A DataFrame with the aggregated yearly values and the name of the aggregated column.
    """
    df_daily, _ = rolling_period_indicator(df_season_temp, variable, row["Windows Length"], row["Windows Aggregation"])

    if not spatial:
        with st.expander("Show Daily Dataframe"):
            st.dataframe(df_daily, height=DATAFRAME_HEIGHT,use_container_width=True)

    df_yearly_var, aggregated_column_name = make_yearly_agg(df_season_temp, variable, row["Yearly Aggregation"])
    df_yearly_var = indicator_score(
        df_yearly_var,
        aggregated_column_name,
        score_name,
        row["Yearly Threshold Min List"],
        row["Yearly Threshold Max List"])
    
    return df_yearly_var, aggregated_column_name


# -----------------------------------
# --- Assembling all calculations ---
# -----------------------------------

def calculate_scores(row, df_season_temp, score_name, variable, spatial):
    """
    Calculate scores for different indicator types based on the input row and data.

    Args:
        row (pandas.Series): A row from the DataFrame containing indicator details.
        df_season_temp (pandas.DataFrame): The seasonal data to perform calculations on.
        score_name (str): The name of the score used for aggregation.
        variable (str): The variable used for calculation (e.g., temperature, precipitation).

    Returns:
        tuple: A tuple containing the unit of measurement, the yearly variable DataFrame, and the aggregated column name.
    """
    if row["Indicator Type"] == "Season Aggregation":
        unit = UNIT_DICT[row["Variable"]]
        df_yearly_var, aggregated_column_name = season_aggregation_calculation(row,df_season_temp, score_name, variable)
        return unit, df_yearly_var, aggregated_column_name
    
    elif row["Indicator Type"] == "Outlier Days":
        unit = "days"
        df_yearly_var, aggregated_column_name = outlier_days_calculation(row, df_season_temp, score_name, variable, spatial)
        return unit, df_yearly_var, aggregated_column_name

    elif row["Indicator Type"] == "Consecutive Outlier Days":
        unit = "days"
        df_yearly_var, aggregated_column_name = consecutive_outlier_days_calculation(row, df_season_temp, score_name, variable, spatial)
        return unit, df_yearly_var, aggregated_column_name
        
    elif row["Indicator Type"] == "Sliding Windows Aggregation":
        unit = UNIT_DICT[row["Variable"]]
        df_yearly_var, aggregated_column_name = sliding_window_calculation(row, df_season_temp, score_name, variable)
        return unit, df_yearly_var, aggregated_column_name
    


# --------------------------
# --- Preparing for plot ---
# --------------------------

def preparing_dataframe_for_plot(df_yearly_var, periods, score_name):
    """
    Prepare the DataFrame for plotting by adding additional columns such as year, period, color, and category.

    Args:
        df_yearly_var (pandas.DataFrame): DataFrame containing yearly data to be prepared for plotting.
        periods (list): List of periods to be added to the DataFrame.
        score_name (str): The name of the score to be used for categorization and color mapping.

    Returns:
        pandas.DataFrame: The modified DataFrame with additional columns for plotting.
    """
    df_yearly_var["year"] = df_yearly_var.index.year
    df_yearly_var = add_periods_to_df(df_yearly_var, periods)
    df_yearly_var["period"] = df_yearly_var["period"].apply(lambda x: f"{x[0]}-{x[1]}")
    df_yearly_var["color"] = df_yearly_var[f"yearly_indicator_{score_name}"].apply(lambda category:CATEGORY_TO_COLOR_MAP[category])
    df_yearly_var["category"] = df_yearly_var["color"].apply(lambda color: RISK_MAP[color])
    return df_yearly_var


# -----------------------------------------------
# --- Main part where everything is assembled ---
# -----------------------------------------------

def calculations_and_plots(df_season, df_indicators_parameters: pd.DataFrame,df_checkbox:pd.DataFrame, all_year_data, season_start, season_end,periods):
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
    tabs = st.tabs(list(df_indicators_parameters["Name"].values))


    # Iterating over indicators dataframe
    for (i, row), (j, row_checkbox) in zip(df_indicators_parameters.iterrows(), df_checkbox.iterrows()):
        with tabs[i]:
            
            # Offer the possibility to edit the indicator

            indicator_editing(df_season, season_start, season_end, row, row_checkbox, i)
            
            # Initializing useful variables
            variable = row["Variable"]
            score_name = row["Name"]
            season_start_shift=row["Season Start Shift"]
            season_end_shift= row["Season End Shift"]
            below_thresholds=copy(row["Yearly Threshold Min List"])
            above_thresholds= copy(row["Yearly Threshold Max List"])
    
            
            
            # Season shift handling
            if season_start is not None or season_end is not None:
                if (not pd.isna(season_start_shift) or not pd.isna(season_end_shift)
                    or season_start_shift is not None or season_end_shift is not None):

                    df_season = introduce_season_shift_in_calculation(season_start, season_start_shift, season_end, season_end_shift, all_year_data)

            if type(variable) is list:
                df_season_temp=df_season[variable]
            else:
                df_season_temp=df_season[[variable]]

            # Crossed Variable indicators have their own graph so don't need to go further there
            if row["Indicator Type"] == "Crossed Variables":
                heat_index_indicator(df_season_temp, all_year_data, key=i, periods=periods)
            else:
                unit, df_yearly_var, aggregated_column_name = calculate_scores(row,df_season_temp, score_name, variable, spatial=0)
                # Plot preparation
                df_yearly_var = preparing_dataframe_for_plot(df_yearly_var, periods, score_name)
                with st.expander("Show Yearly Dataframe"):
                    st.dataframe(df_yearly_var, height=DATAFRAME_HEIGHT, use_container_width=True)
                

                
                # Multiple plot to understand the calculated indicators
                fig1 = plot_daily_data(all_year_data, variable)
                fig2 = plot_years_exposure(df_yearly_var, aggregated_column_name, below_thresholds, above_thresholds, score_name,unit)
                fig3 = plot_deficit_and_excess_exposure(df_yearly_var, score_name)
                fig4 = plot_global_exposure(df_yearly_var, score_name, i, aggregated_column_name, below_thresholds, above_thresholds)
                fig_list = [fig1, fig2, fig3, fig4]
                pdf = wrap_indicator_into_pdf(fig_list)
                st.download_button(
                    label="Download PDF",
                    data=pdf,
                    file_name="whatever.pdf",
                    mime="application/pdf",
                    key=f"download_{i}"
                )
    return df_yearly


def spatial_calculation(df_season, df_indicators_parameters: pd.DataFrame,df_checkbox:pd.DataFrame, dataframes_dict, 
                        all_dataframes_dict, season_start, season_end,periods, shape_gdf, raster_resolution):
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
    tabs = st.tabs(list(df_indicators_parameters["Name"].values))

    # Iterating over indicators dataframe
    for (i, row), (j, row_checkbox) in zip(df_indicators_parameters.iterrows(), df_checkbox.iterrows()):
        with tabs[i]:
            
            # Offer the possibility to edit the indicator

            indicator_editing(df_season, season_start, season_end, row, row_checkbox, i)
            
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
                                for (df_key, df), (df_all_key, df_all) in zip(dataframes_dict_filtered.items(), all_dataframes_dict.items()):
                                    df = introduce_season_shift_in_calculation(season_start, season_start_shift, season_end, season_end_shift, df_all)
                       
                        st.write("Data ready")
                        
                    
                        # Specific part to allow crossed variable computation
                        if row["Indicator Type"] == "Crossed Variables":
                            if st.button(label="Compute Data to get the graphs", key="crossed_variable_compute"):
                                progress_bar = st.progress(0)
                                for i,  (df_key, df) in enumerate(dataframes_dict_filtered.items()):
                                    sumup_df = heat_index_spatial_indicator(df, periods)
                                    df_raster = pd.concat([df_raster, sumup_df])
                                    progress_bar.progress((i+1)/len(dataframes_dict_filtered), text=df_key)
                                rasterize_data(df_raster, shape_gdf=shape_gdf, resolution=raster_resolution, score_name=score_name)
                        
                        # All the other parts are located here                                        
                        else:
                            
                            if st.button(label="Compute Data to get the graphs", key=f"other_compute_{i}"):
                                progress_bar = st.progress(0)
                                for i, ((df_key, df), (all_df_key, all_df)) in enumerate(zip(dataframes_dict_filtered.items(), all_dataframes_dict.items())):

                                    
                                    sumup_df = spatial_calculation_for_raster(row, below_thresholds, above_thresholds, df, score_name, variable, periods)
                                    df_raster = pd.concat([df_raster, sumup_df])
                                    progress_bar.progress((i+1)/len(dataframes_dict_filtered), text=df_key)
                                    
                                rasterize_data(df_raster, shape_gdf=shape_gdf, resolution=raster_resolution, score_name=score_name)
 
                else:
                    st.warning("Your variable is not in the taken in the dataframes dictionary, please click on 'Filter the data' button to get it")
                if st.session_state.raster_params is not None:
                    try :
                        if row["Indicator Type"] == "Crossed Variables":
                            display_raster_with_slider_heat_index(score_name, periods)
                        else:
                            display_raster_with_slider(score_name, periods)
                        raster_download_button(score_name, index=i)
                    except Exception as e:
                        st.error(f"An error occurred while rendering the rasters: {e}")
                        st.info("The data has changed, but it has not been recomputed yet. Please click on the button")
                
    return df_yearly


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
    aggregation_type = "Variable Mean Category"
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
    st.write("The filtering is done")
    print(dataframes)
    return dataframes
