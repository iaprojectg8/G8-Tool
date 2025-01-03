from utils.imports import *
from layouts.layout import *

# --- Main functions ---
def loads_data(filename):
    """
    Loads the CSV data with daily timestamps.
    
    Arg:
    filename (str): The path to the CSV file.
    
    Returns:
    tuple:
        - (pd.DataFrame): Loaded data with 'date' as the index.
        - (float): Latitude of the data point.
        - (float): Longitude of the data point.
    """
    # Load the CSV data with daily timestamps
    data = pd.read_csv(filename, parse_dates=['date'], index_col=0)
    
    # Extract the lat and lon and the point to identify it later to make the raster
    lat = data.loc[0, "lat"]
    lon = data.loc[0, "lon"]

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
    columns_chosen = st.session_state.columns_chosen = st.multiselect("Chose variable of interest", options=columns_list, default=st.session_state.columns_chosen)
    df_final = data[columns_chosen]

    return df_final

def period_filter(data,period):
    data_in_right_period = data[(data.index.year>=period[0]) & (data.index.year<=period[-1])]
    return data_in_right_period

def filtered_data(data:pd.DataFrame, chosen_variables, period):
    """
    Filters a DataFrame based on selected variables and a specified time period, 
    then displays the resulting DataFrame.

    Args:
        data (pd.DataFrame): The input DataFrame with a datetime index.
        chosen_variables (list of str): The list of variables to filter the columns.
        period (tuple of int): The start and end years for filtering the DataFrame.

    Returns:
        pd.DataFrame: The filtered DataFrame containing only the relevant columns and rows within the specified period.
    """

    # Filter by the period
    data_in_right_period = data[(data.index.year>=period[0]) & (data.index.year<=period[-1])]
    
    # Change the format of the proposition made to the user to correspond to the dataframe column name
    chosen_variables_modified = ["_".join(variable.lower().split()) for variable in chosen_variables]

    # Check whether the columns chould be taken or removed from the dataframe
    columns_to_keep = [column for column in data.columns if any(variable in column for variable in chosen_variables_modified)]
    
    # Keep the relevant columns
    data_to_keep = data_in_right_period[columns_to_keep]
    
    data_to_diplay = copy(data_to_keep)
    data_to_diplay.index = data_to_diplay.index.date

    # Display the dataframe
    st.dataframe(data=data_to_diplay,use_container_width=True)
    return data_to_keep


def select_period():
    
    period_start= 1950
    period_end= 2050

    period_start, period_end = st.slider(
        "Select the data period:",
        min_value=period_start, 
        max_value=period_end,
        value=(period_start, period_end))      
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
    amount_of_periods = whole_period_length // period_length + 1
    periods = []

    # Loop through each period index and calculate start and end years
    for period_index in range(amount_of_periods):
        period_start = start_year + period_index * period_length   # Start year of the current period
        period_end = period_start + period_length -1  # End year of the current period

        # Append the period to the list, ensuring it does not exceed the end year
        if period_end <= end_year:
            periods.append((period_start, period_end))
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
    print(end_year)
    whole_period_length = end_year - start_year + 1
    amount_of_periods = whole_period_length // period_length + 1
    periods = []

    # Loop through each period index and calculate start and end years
    for period_index in range(amount_of_periods):
        period_start = start_year + period_index * period_length  # Start year of the current period
        period_end = period_start + period_length  # End year of the current period

        # Append the period to the list, ensuring it does not exceed the end year
        if period_end <= end_year:
            periods.append((period_start, period_end))
        elif period_index == amount_of_periods-1 and  end_year - period_start < 2:
            last_period = periods.pop()
            print(last_period)
            print(last_period[0])
            print(end_year)
            periods.append((last_period[0], end_year))
        else:
            periods.append((period_start, end_year))

    print(periods)

    return periods



