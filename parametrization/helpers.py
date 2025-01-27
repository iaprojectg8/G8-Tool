from utils.imports import *
from layouts.layout import *
from parametrization.create_inidicator import *
from parametrization.update_indicator import *
from parametrization.widgets_parametrization import *

# ---------------------------------------------------
# --- Functions for the indicator parametrization ---
# ---------------------------------------------------

def process_dataframes_zip(uploaded_file, extract_to):
    """
    Processes the uploaded zip file containing CSV files.
    Args:
        uploaded_file (BytesIO): The uploaded zip file.
        extract_to (str): The directory to extract the files to.
    """
            
    if os.path.exists(extract_to):
        shutil.rmtree(extract_to)
    
    # Create the directory
    os.makedirs(extract_to, exist_ok=True)
    
    extract_csv_from_zip(uploaded_file, extract_to)
    st.session_state.already_uploaded_file = uploaded_file

    # This is a dataframe dictionary
    st.session_state.dataframes = read_csv_files_from_directory(extract_to)
    st.session_state.dataframes = put_date_as_index(dataframe_dict=st.session_state.dataframes)
    st.session_state.building_indicator_df = st.session_state.dataframes[rd.choice(list(st.session_state.dataframes.keys()))]
    

def period_management():
    """
    Manages the period selection for the indicators.
    Returns:
        pd.DataFrame: The filtered DataFrame containing the selected period
    """
    # User setting the periods of interest
    st.session_state.long_period = select_period(key = "indicator_part")

    # Loading data and applying first filters
    all_data = st.session_state.building_indicator_df
    data_long_period_filtered = period_filter(all_data, period=st.session_state.long_period)
    st.dataframe(data_long_period_filtered, height=DATAFRAME_HEIGHT, use_container_width=True)

    return data_long_period_filtered


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

def season_management(df_chosen: pd.DataFrame):
    """
    Manages the season selection for the indicators.
    Args:
        df_chosen (pd.DataFrame): The DataFrame containing the indicators.
    Returns:
        pd.DataFrame: The filtered DataFrame containing the selected season
        int: The start month of the season
        int: The end month of the season
    """
    season_start, season_end = None, None
    if st.checkbox("Need a season or a period study", value=st.session_state.season_checkbox):
        season_start, season_end = select_season(months_list=MONTHS_LIST)
        df_season = select_data_contained_in_season(df_chosen, season_start, season_end)
        st.dataframe(df_season, height=DATAFRAME_HEIGHT, use_container_width=True)
    else:
        df_season = df_chosen

    return df_season, season_start, season_end

def initialize_indicators_tool_management(df_uploaded):
    """
    Initializes the indicators tool management.
    Args:
        df_uploaded (pd.DataFrame): The DataFrame containing the uploaded indicators.
    """
    df_checkbox = fill_df_checkbox(df_uploaded)
    st.session_state.uploaded_df = df_uploaded
    st.session_state.df_indicators = copy(df_uploaded)
    st.session_state.df_checkbox = df_checkbox




# -------------------------------------------
# --- Functions for the uploaded CSV file ---
# -------------------------------------------

def extract_csv_from_zip(zip_file, extract_to):
    """
    Extracts the CSV files from a zip file.
    Args:
        zip_file (BytesIO): The zip file containing the CSV files.
        extract_to (str): The directory to extract the files
    """
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def read_csv_files_from_directory(folder):
    """
    Reads the CSV files from a directory and returns them as a dictionary of DataFrames.
    Args:
        folder (str): The directory containing the CSV files.
    Returns:
        dict: A dictionary of DataFrames containing the CSV files.
    """
    # L'utilisation de glob est surement plus approprié dans ce genre de cas
    extracted_dir_name = os.listdir(folder)[0]
    extracted_dir_path = os.path.join(folder, extracted_dir_name)
    
    # Just to manage different zip file structures
    if os.path.isfile(extracted_dir_path):
        extracted_dir_path = folder

    csv_files = [f for f in os.listdir(extracted_dir_path) if f.endswith('.csv')]
    dataframes = {}
    for file in csv_files:
        file_path = os.path.join(extracted_dir_path, file)
        dataframes[file] = pd.read_csv(file_path)
    get_min_and_max_year(dataframes)
    return dataframes


def get_min_and_max_year(dataframes:dict):
    """
    Get the min and max year of the dataframes.
    Args:
        dataframes (dict): A dictionary of DataFrames containing the CSV files.
    """
    df = copy(dataframes[list(dataframes.keys())[0]])

    # Put the date column in datetime format
    df["date"] = pd.to_datetime(df["date"])
    # Assign extreme years long period
    min_year = df['date'].min().year
    max_year = df['date'].max().year
    st.session_state.min_year, st.session_state.max_year = min_year, max_year

def put_date_as_index(dataframe_dict:dict):
    """
    Puts the 'date' column as the index of the DataFrames in the dictionary.
    Args:
        dataframe_dict (dict): A dictionary of DataFrames containing the CSV files.
    Returns:
        dict: A dictionary of DataFrames with the 'date' column as the index.
    """
    for key, df in dataframe_dict.items():
        df['date'] = pd.to_datetime(df['date'])  # Ensure the 'date' column is in datetime format
        df.set_index('date', inplace=True)  # Set the 'date' column as the index
        dataframe_dict[key] = df
    return dataframe_dict



# --------------------------------------------------
# --- Function to fill the df_checkbox DataFrame ---
# --------------------------------------------------

def fill_df_checkbox(df: pd.DataFrame):
    """
    Fills the df_checkbox Dataframe corresponding to the df content.

    Args:
        df (pd.DataFrame): The DataFrame containing the indicators.
        
    Returns:
        pd.DataFrame: The df_checkbox DataFrame with the same index as df.
    """
    # Initialize the df_checkbox DataFrame with the same index as df
    df_checkbox = st.session_state.df_checkbox
    
    # Initialize all checkboxes to False
    for index, row in df.iterrows():
        df_checkbox.at[index, "min_daily_checkbox"] = pd.notna(row.get("Daily Threshold Min"))
        df_checkbox.at[index, "max_daily_checkbox"] = pd.notna(row.get("Daily Threshold Max"))
        df_checkbox.at[index, "min_yearly_checkbox"] = pd.notna(row.get("Yearly Threshold Min"))
        df_checkbox.at[index, "max_yearly_checkbox"] = pd.notna(row.get("Yearly Threshold Max"))
        df_checkbox.at[index, "shift_start_checkbox"] = pd.notna(row.get("Season Start Shift"))
        df_checkbox.at[index, "shift_end_checkbox"] = pd.notna(row.get("Season End Shift"))
        df_checkbox.at[index, "threshold_list_checkbox_min"] = pd.notna(row.get("Yearly Threshold Min"))
        df_checkbox.at[index, "threshold_list_checkbox_max"] = pd.notna(row.get("Yearly Threshold Max"))

    return df_checkbox

# ---------------------------------------------------
# --- Function to update the dataframe dictionary ---
# ---------------------------------------------------
def apply_change_to_dataframes():
    """
    Applies the changes to the dataframes.
    Args:
        dataframes (dict): The dictionary of dataframes.
    """
    st.session_state.dataframes_modified = copy(st.session_state.dataframes)
    for key, df in st.session_state.dataframes_modified.items():
        df = period_filter(df, st.session_state.long_period)
        st.session_state.dataframes_modified[key] = df 
