from utils.imports import * 


if "indicator" not in st.session_state:
    st.session_state.indicator = {
        "Name": "",
        "Variable": None,
        "Indicator Type": None,
        "Builtin Indicator": None, 
        "Daily Threshold Min": None,
        "Daily Threshold Max": None,
        "Windows Length": 2,
        "Windows Aggregation" : None,
        "Yearly Threshold Min": None,
        "Yearly Threshold Max": None,
        "Yearly Threshold Min Step" : 0,
        "Yearly Threshold Min List": [],
        "Yearly Threshold Max Step" : 0,
        "Yearly Threshold Max List" : [],
        "Yearly Aggregation": None,
        "Season Start Shift": None,
        "Season End Shift": None
    }

if 'df_indicators' not in st.session_state:
    st.session_state.df_indicators = pd.DataFrame(columns=st.session_state.indicator.keys())

if "checkbox_defaults" not in st.session_state:
    st.session_state.checkbox_defaults = {
        "min_daily_checkbox": False,
        "max_daily_checkbox": False,
        "min_yearly_checkbox": False,
        "max_yearly_checkbox": False,
        "shift_start_checkbox": False,
        "shift_end_checkbox": False,
        "threshold_list_checkbox" : False,
        "threshold_list_checkbox_min" : False,
        "threshold_list_checkbox_max" : False
    }

if "df_checkbox" not in st.session_state:
    st.session_state.df_checkbox = pd.DataFrame(columns=st.session_state.checkbox_defaults.keys())
    
if "columns_chosen" not in st.session_state:
    st.session_state.columns_chosen = None


if "season_start" not in st.session_state:
    st.session_state.season_start = 6


if "season_end" not in st.session_state:
    st.session_state.season_end = 10

if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = None

if "resolution" not in st.session_state:
    st.session_state.resolution = 0.2

if "points_df" not in st.session_state:
    st.session_state.points_df = None

if "combined_gdf" not in st.session_state:
    st.session_state.combined_gdf = None

if "uploaded_file_spatial" not in st.session_state:
    st.session_state.uploaded_file_spatial = None

if "lat_lon" not in st.session_state:
    st.session_state.lat_lon = (None, None)

if "gdf" not in st.session_state:
    st.session_state.gdf = None

if "xaxis_range" not in st.session_state:
    st.session_state.xaxis_range = None

if "dataframes" not in st.session_state:
    st.session_state.dataframes = dict()

if "raster_params" not in st.session_state:
    st.session_state.raster_params = dict()

if "all_df_mean" not in st.session_state:
    st.session_state.all_df_mean = None 

if "reset_folder" not in st.session_state:
    st.session_state.reset_folder = None

if "min_year" not in st.session_state:
    st.session_state.min_year = None

if "max_year" not in st.session_state:
    st.session_state.max_year = None

def delete_indicator(index):
    """
    Deletes an indicator from the list of indicators.
    Args:
        index (int): The index of the indicator to delete.
    """
    print("index", index)
    st.session_state.df_indicators = st.session_state.df_indicators.drop(index).reset_index(drop=True)

def update_indicator(index, updated_indicator, updated_checkbox):
    """
    Updates in the indicator dataframe at the given index.
    Args:
        index (int): The index of the indicator to update.
        updated_indicator (dict): The updated indicator.
    """
    print("Indicators updated")
    if updated_indicator["Yearly Threshold Min List"] != []:
        updated_indicator["Yearly Threshold Min"] = updated_indicator["Yearly Threshold Min List"][0] 
    if updated_indicator["Yearly Threshold Max List"] != []:
        updated_indicator["Yearly Threshold Max"] = updated_indicator["Yearly Threshold Max List"][0]
    st.session_state.df_indicators.loc[index] = updated_indicator
    st.session_state.df_checkbox.loc[index] = updated_checkbox


     


def update_chosen_variable(values):
    """
    Updates the chosen variable in the session state.
    """
    st.session_state.columns_chosen = values




def reset_indicator():
    """
    Resets the indicator session state to its default values.
    This function initializes the indicator session state with default values
    and resets various checkboxes to their default (unchecked) state.
    """
    # Initialize the indicator session state with default values
    st.session_state.indicator = {
        "Name": "",
        "Variable": None,
        "Indicator Type": None,
        "Builtin Indicator": None,
        "Daily Threshold Min": None,
        "Daily Threshold Max": None,
        "Windows Length": 2,
        "Windows Aggregation": None,
        "Yearly Threshold Min": None,
        "Yearly Threshold Max": None,
        "Yearly Threshold Min Step": 0,
        "Yearly Threshold Min List": [],
        "Yearly Threshold Max Step": 0,
        "Yearly Threshold Max List": [],
        "Yearly Aggregation": None,
        "Season Start Shift": None,
        "Season End Shift": None
    }
    
    # Reset various checkboxes to their default (unchecked) state
    st.session_state.min_daily_checkbox = False
    st.session_state.max_daily_checkbox = False
    st.session_state.min_yearly_checkbox = False
    st.session_state.max_yearly_checkbox = False
    st.session_state.shift_start_checkbox = False
    st.session_state.shift_end_checkbox = False
    st.session_state.threshold_list_checkbox_min = False
    st.session_state.threshold_list_checkbox_max = False
    

    