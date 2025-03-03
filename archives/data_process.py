from utils.imports import *
from lib.layout import *
from utils.variables import DATAFRAME_HEIGHT
from lib.session_variables import update_chosen_variable



# --- Main functions ---
def loads_data(filename):
    """
    Loads the CSV data with daily timestamps.
    
    Arg:
    filename (str): The path to the CSV file.
    
    Returns:
    data : (pd.DataFrame): Loaded data with 'date' as the index.
    """
    # Load the CSV data with daily timestamps
    data = pd.read_csv(filename, parse_dates=['date'], index_col=0)

    # Set the index to the date for the process to be easier
    data = data.set_index("date")
    return data

def column_choice(data : pd.DataFrame):
    """
    Allows a user to select a column of interest from a DataFrame, excluding certain columns.

    Args:
        data (pd.DataFrame): The input DataFrame containing the data.

    Returns:
        pd.Series: The selected column from the DataFrame as a Pandas Series.
    """
    not_a_variable = [ "lat", "lon"]
    columns_list = [column  for column in data.columns if column not in not_a_variable]

    # Widget that allows the user to select the variable he wants to see plotted
    st.session_state.columns_chosen = st.multiselect("Chose variable of interest", options=columns_list)
    columns_chosen = st.session_state.columns_chosen

    # Restrict the dataframe to the user selected columns
    df_final = data[columns_chosen]

    return df_final

def period_filter(data, period):
    """
    Filters the input data to include only rows within the specified period.

    Args:
        data (DataFrame): A pandas DataFrame with a DateTime index.
        period (list or tuple): A list or tuple containing the start and end years [start_year, end_year].

    Returns:
        DataFrame: A filtered DataFrame containing only rows within the specified period.
    """
    # Select rows where the year in the index is between the start and end years of the period
    data_in_right_period = data[(data.index.year >= period[0]) & (data.index.year <= period[-1])]
    
    return data_in_right_period






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

def split_into_periods_indicators(period_length, start_year, end_year):
    """
    Splits a given time range into multiple periods of a specified length.

    Args:
        period_length (int): The length of each period in years.
        start_year (int): The starting year of the entire time range.
        end_year (int): The ending year of the entire time range.

    Returns:
        list of tuples: A list of tuples where each tuple represents a period
                        with the format (period_start, period_end).
    """
    whole_period_length = end_year - start_year + 1
    amount_of_periods = ceil(whole_period_length / period_length)
    periods = []

    # Loop through each period index and calculate start and end years
    for period_index in range(amount_of_periods):
        period_start = start_year + period_index * period_length   # Start year of the current period
        period_end = period_start + period_length -1  # End year of the current period

        # Append the period to the list, ensuring it does not exceed the end year
        if period_end < end_year:
            periods.append((period_start, period_end))
        elif abs(period_start - end_year)<0.3*period_length:
            # Needs to create last tuple periods before to remove the last element of the list
            last_period = (periods[-1][0], end_year)
            periods.pop()
            periods.append(last_period)
        else:
            periods.append((period_start, end_year))

    return periods

def split_into_periods(period_length, start_year, end_year):
    """
    Splits a given time range into multiple periods of a specified length.

    Args:
        period_length (int): The length of each period in years.
        start_year (int): The starting year of the entire time range.
        end_year (int): The ending year of the entire time range.

    Returns:
        list of tuples: A list of tuples where each tuple represents a period
                        with the format (period_start, period_end).
    """
    whole_period_length = end_year - start_year + 1
    amount_of_periods = ceil(whole_period_length / period_length)
    periods = []

    # Loop through each period index and calculate start and end years
    for period_index in range(amount_of_periods):
        period_start = start_year + period_index * period_length  # Start year of the current period
        period_end = period_start + period_length  # End year of the current period

        # Append the period to the list, ensuring it does not exceed the end year
        if period_end <= end_year:
            periods.append((period_start, period_end))
        else:
            periods.append((period_start, end_year))

    return periods



