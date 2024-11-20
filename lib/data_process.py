from utils.imports import *


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
    return data, lat, lon

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
    column_chosen = st.multiselect("Chose variable of interest", options=columns_list, default=columns_list[0])
    df_final = data[column_chosen]

    return df_final

def apply_changes(data, chosen_variables, period):

    # Change the format of the proposition made to the user to correspond to the dataframe column name
    chosen_variables_modified = ["_".join(variable.lower().split()) for variable in chosen_variables]
    # Check whether the columns chould be taken or removed from the dataframe
    columns_to_keep = [column for column in data.columns if any(variable in column for variable in chosen_variables_modified)]
    # Filter by the period
    data_in_right_period = data[(data.index.year>=period[0]) & (data.index.year<=period[-1])]
    # Filter the relevant columns
    data_to_keep = data_in_right_period[columns_to_keep]
    # Display the final dataframe
    st.dataframe(data=data_to_keep,use_container_width=True)
    return data_to_keep


def split_into_periods(period_length, start_year, end_year):
    whole_period_length = end_year - start_year + 1
    amount_of_periods = whole_period_length//period_length +1
    periods = []
    for period_index in range(amount_of_periods):
        period_start = start_year+period_index*period_length
        period_end = period_start + period_length 
        if period_end <= end_year:
            periods.append((period_start, period_end))
        else:
            periods.append((period_start, end_year))
    return periods



