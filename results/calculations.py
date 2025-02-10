from utils.imports import *
from utils.variables import *
from parametrization.helpers import period_filter


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


def get_only_required_variable(dataframes_dict, variable):
    for (df_key, df) in dataframes_dict.items() :
            if isinstance(variable, list):  # Check if variable is a list
                selected_columns = variable + ["lat", "lon"]  # Create a new list
            else:
                selected_columns = [variable, "lat", "lon"]  # Combine into a list
            
            df = df.loc[:, selected_columns]  # Use the new variable for column selection
            dataframes_dict[df_key] = df
    return dataframes_dict


def filter_all_the_dataframe(dataframes:dict, long_period):
    for key_df, df in dataframes.items():
        # do the filters that have been done on the first dataframe of the dictionary
        data_long_period_filtered = period_filter(df, period=long_period)
        dataframes[key_df] = data_long_period_filtered
    st.write("The filtering is done")
    print(dataframes)
    return dataframes


def reset_cumsum(group):
    """
    Reset the cumulative sum whenever a zero is encountered in the group. Useful to calculate
    consecutive outlier days.
    
    Args:
        group (iterable): A sequence of values to calculate the cumulative sum.
        
    Returns:
        list: The cumulative sum where the sum is reset at each zero value.
    """
    cumsum = 0
    result = []
    for val in group:
        if val == 0:
            cumsum = 0
        else:
            cumsum += val
        result.append(cumsum)
    return result


def make_yearly_agg(df: pd.DataFrame, variable, yearly_aggregation):
    """
    Perform yearly aggregation on the specified variable using the provided aggregation method.
    
    Args:
        df (pd.DataFrame): DataFrame containing the data.
        variable (str): The column name in the DataFrame to be aggregated.
        yearly_aggregation (str or function): The aggregation method (e.g., 'sum', 'mean').
        
    Returns:
        df_yearly (pd.DataFrame): A DataFrame with yearly aggregated data.
        str: The name of the new column with the aggregation suffix.
    """
    df_yearly = df.resample("YE").agg({variable: yearly_aggregation})
    df_yearly = df_yearly.rename(columns={variable: f"yearly_{yearly_aggregation}_{variable}"})
    aggregated_column_name = f"yearly_{yearly_aggregation}_{variable}"
    return df_yearly, aggregated_column_name

def daily_indicators(df:pd.DataFrame, variable, daily_thresh_min, daily_thresh_max):
    """
    Calculate daily indicators based on threshold values.
    
    Args:
        df (pd.DataFrame): DataFrame containing the daily data.
        variable (str): The column name of the variable to calculate the indicator for.
        daily_thresh_min (float): The minimum threshold for the daily indicator.
        daily_thresh_max (float): The maximum threshold for the daily indicator.
        
    Returns:
        df (pd.DataFrame): The DataFrame with the calculated daily indicator column.
        indicator_column (str): The name of the indicator column.
    """
    indicator_column = f"daily_indicator"
    
    # Handling both daily threshold
    if daily_thresh_min is not None and not math.isnan(daily_thresh_min) and daily_thresh_max is not None and not math.isnan(daily_thresh_max):

        df[indicator_column] =  (df[variable].between(daily_thresh_min, daily_thresh_max)).astype(int)   
    
    # Handling daily min threshold
    elif  daily_thresh_min is not None and not math.isnan(daily_thresh_min):
       
        df[indicator_column] =  (df[variable] < daily_thresh_min).astype(int)

    # Handling daily max threshold
    elif  daily_thresh_max is not None and not math.isnan(daily_thresh_max):
     
        df[indicator_column] =  (df[variable] > daily_thresh_max).astype(int)
    # No threshold
    else:
        df = df
    return df, indicator_column


def rolling_period_indicator(df:pd.DataFrame, variable, window_length, window_aggregation):
    """
    Calculate a rolling window aggregation on a specified variable.

    Args:
        df (pd.DataFrame): DataFrame containing the data.
        variable (str): The column name in the DataFrame to calculate the rolling window on.
        window_length (int): The length of the rolling window (number of periods).
        window_aggregation (str): The aggregation function to apply (e.g., 'sum', 'mean', 'max', 'min').

    Returns:
        df (pd.DataFrame): The DataFrame with the calculated rolling window aggregation.
        indicator_column (str): The name of the new indicator column.
    """
    indicator_column = f"{variable}_window_{window_aggregation}"
    df[indicator_column] = df[variable].rolling(window=window_length).agg(window_aggregation)


    return df, indicator_column

    
def categorize_both(value, below_thresholds=None,above_thresholds=None):
    """
    Categorizes a value based on both above and below thresholds.
    
    Args:
        value (float): The value to categorize.
        above_thresholds (list, optional): A sorted list of thresholds for values above the normal range.
        below_thresholds (list, optional): A sorted list of thresholds for values below the normal range (in descending order).
    
    Returns:
        int: The category, positive for above thresholds, negative for below thresholds, and 0 for normal.
    """
    # Check if value is above thresholds
    if below_thresholds and above_thresholds:
        if  below_thresholds [0] <value < above_thresholds[0]:
            return 1
        elif above_thresholds[0] <= value < above_thresholds[1]:
            return 2
        elif above_thresholds[1] <= value < above_thresholds[2]:
            return 3
        elif above_thresholds[2] <= value :
            return 4
        
        elif above_thresholds[0] > value > below_thresholds[0]:
            return -1
        elif below_thresholds[0] >= value > below_thresholds[1]:
            return -2
        elif below_thresholds[1] >= value > below_thresholds[2]:
            return -3
        elif value <= below_thresholds[2]:
            return -4
        
    elif below_thresholds:
        if  value > below_thresholds[0]:
            return -1
        elif below_thresholds[0] >= value > below_thresholds[1]:
            return -2
        elif below_thresholds[1] >= value > below_thresholds[2]:
            return -3
        elif value <= below_thresholds[2]:
            return -4
        
    elif above_thresholds:
        if  value < above_thresholds[0]:
            return 1
        elif above_thresholds[0] <= value < above_thresholds[1]:
            return 2
        elif above_thresholds[1] <= value < above_thresholds[2]:
            return 3
        elif above_thresholds[2] <= value :
            return 4

    return 0

def indicator_score(df: pd.DataFrame, variable, score, yearly_trehsholds_min: list, yearly_trehsholds_max:list):
    """
    Categorizes data based on threshold values and assigns an indicator score.

    Args:
        df (pd.DataFrame): DataFrame containing the data.
        variable (str): The column name in the DataFrame to categorize.
        score (str): The score name to be used in the output column.
        yearly_thresholds_min (list): List of minimum thresholds for categorization.
        yearly_thresholds_max (list): List of maximum thresholds for categorization.

    Returns:
        df (pd.DataFrame): The DataFrame with a new column for the indicator score.
    """
    below_thresholds = yearly_trehsholds_min
    above_thresholds = yearly_trehsholds_max
    
    df[f"yearly_indicator_{score}"] =(df[variable].apply(lambda x:categorize_both(x,below_thresholds, above_thresholds) )).astype(int)

    return df


def add_periods_to_df(df:pd.DataFrame, periods):
    """
    Assigns a period to each row in the DataFrame based on the 'year' column.

    Args:
        df (pd.DataFrame): The input DataFrame containing a 'year' column.
        periods (list of tuples): A list of periods, where each period is a tuple (start_year, end_year).

    Returns:
        pd.DataFrame: The DataFrame with an additional 'period' column indicating the assigned period.
    """
    # Assign the first matching period to each 'year' using the next() function that iterates over periods
    df["period"] = df["year"].apply(lambda x: next((period for period in periods if period[0] <= x <= period[1]), None))
    return df