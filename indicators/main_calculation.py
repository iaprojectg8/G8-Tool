from utils.imports import *
from utils.variables import *
from indicators.calculation import *
from indicators.plot import *
from indicators.parametrization.update_indicator import * 
from indicators.custom_indicators import heat_index_indicator


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
    print(season_start, season_end)
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
    
def outlier_days_calculation(row, df_season_temp, score_name, variable):
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

def consecutive_outlier_days_calculation(row, df_season_temp, score_name, variable):
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

def sliding_window_calculation(row, df_season_temp, score_name, variable):
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

def calculate_scores(row, df_season_temp, score_name, variable):
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
        unit = UNIT_FROM_VARIABLE[row["Variable"]]
        df_yearly_var, aggregated_column_name = season_aggregation_calculation(row,df_season_temp, score_name, variable)
        return unit, df_yearly_var, aggregated_column_name
    
    elif row["Indicator Type"] == "Outlier Days":
        unit = "days"
        df_yearly_var, aggregated_column_name = outlier_days_calculation(row, df_season_temp, score_name, variable)
        return unit, df_yearly_var, aggregated_column_name

    elif row["Indicator Type"] == "Consecutive Outlier Days":
        unit = "days"
        df_yearly_var, aggregated_column_name = consecutive_outlier_days_calculation(row, df_season_temp, score_name, variable)
        return unit, df_yearly_var, aggregated_column_name
        
    elif row["Indicator Type"] == "Sliding Windows Aggregation":
        unit = UNIT_FROM_VARIABLE[row["Variable"]]
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
                heat_index_indicator(df_season_temp)
            else:
                unit, df_yearly_var, aggregated_column_name = calculate_scores(row,df_season_temp, score_name, variable)
                
                # Plot preparation
                df_yearly_var = preparing_dataframe_for_plot(df_yearly_var, periods, score_name)
                with st.expander("Show Yearly Dataframe"):
                    st.dataframe(df_yearly_var, height=DATAFRAME_HEIGHT, use_container_width=True)
                
                # Multiple plot to understand the calculated indicators
                plot_daily_data(all_year_data, variable)
                plot_years_exposure(df_yearly_var, aggregated_column_name, below_thresholds, above_thresholds, score_name,unit)
                plot_deficit_and_excess_exposure(df_yearly_var, score_name)
                plot_global_exposure(df_yearly_var, score_name, i, aggregated_column_name, below_thresholds, above_thresholds)

    return df_yearly