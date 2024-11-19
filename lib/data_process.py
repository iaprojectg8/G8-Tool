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