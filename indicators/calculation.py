from utils.imports import *
from utils.variables import * 
from layouts.layout import * 
from lib.plot import add_periods_to_df

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
       
        df.loc[:, indicator_column] =  (df[variable] < daily_thresh_min).astype(int)

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
    if above_thresholds:
        if  value < above_thresholds[0]:
            return 1
        elif above_thresholds[0] <= value < above_thresholds[1]:
            return 2
        elif above_thresholds[1] <= value < above_thresholds[2]:
            return 3
        elif value >= above_thresholds[2]:
            return 4

    # Check if value is below thresholds
    if below_thresholds:
        if value > below_thresholds[0]:
            return -1
        elif below_thresholds[0] >= value > below_thresholds[1]:
            return -2
        elif below_thresholds[1] >= value > below_thresholds[2]:
            return -3
        elif value <= below_thresholds[2]:
            return -4

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
