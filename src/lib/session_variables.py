from src.utils.imports import * 
from src.utils.variables import ZIP_FOLDER, CSV_ZIPPED


def initialize_session_state_variable(mode="Beginner"):
    """
    Initializes the session state variables.
    Args:
        mode (str): The mode to initialize the session state with.
    """
    if st.session_state == {}:
        # -------------------------------------
        # --- Welcome page & Mode Selection ---
        # -------------------------------------

        if "mode" not in st.session_state:
            st.session_state.mode = mode

        if "last_page" not in st.session_state:
            st.session_state.last_page = None


        # -------------------------------------
        # --- Request & General Information --- 
        # -------------------------------------

        if "shortname" not in st.session_state:
            st.session_state.shortname = None

        if "project_info" not in st.session_state:
            st.session_state.project_info = dict()

        if "gdf_list" not in st.session_state:
            st.session_state.gdf_list = []

        if "combined_gdf" not in st.session_state:
            st.session_state.combined_gdf = pd.DataFrame()

        # -----------------------
        # --- General Results ---
        # -----------------------

        # Folder
        if "selected_csv_folder" not in st.session_state:
            st.session_state.selected_csv_folder = None

        if "selected_csv_loaded" not in st.session_state:
            st.session_state.selected_csv_loaded = None

        # Dataframes
        if "dataframes" not in st.session_state:
            st.session_state.dataframes = dict()  

        if "all_df_mean" not in st.session_state:
            st.session_state.all_df_mean = None

        # Dates
        if "min_year" not in st.session_state:
            st.session_state.min_year = None

        if "max_year" not in st.session_state:
            st.session_state.max_year = None

        if "long_period" not in st.session_state:
            st.session_state.long_period = None

        if "ssp" not in st.session_state:
            st.session_state.ssp = None

        if "crs" not in st.session_state:
            st.session_state.crs = None

        
        # ------------------
        # --- Indicators ---
        # ------------------

        # Season related
        if "season_checkbox" not in st.session_state:
            st.session_state.season_checkbox = False

        if "season_start" not in st.session_state:
            st.session_state.season_start = 6

        if "season_end" not in st.session_state:
            st.session_state.season_end = 10

        # Indicator related
        if "building_indicator_df" not in st.session_state:
            st.session_state.building_indicator_df = pd.DataFrame()

        if "dataframes_modified" not in st.session_state:  
            # This is in order to store less data in case we chose a long period smaller than the whole dataframes period
            st.session_state.dataframes_modified = dict()

        if "uploaded_df_indicators" not in st.session_state:
            st.session_state.uploaded_df_indicators = None

        if 'df_indicators' not in st.session_state:
            st.session_state.df_indicators = pd.DataFrame(columns=st.session_state.indicator.keys())

        if "df_checkbox" not in st.session_state:
            st.session_state.df_checkbox = pd.DataFrame(columns=st.session_state.checkbox_defaults.keys())

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

        
        # --------------------------------------------------------------------
        # Everything after there is not used at all in the beginner part
        # --------------------------------------------------------------------

        if "uploader_shape_checked" not in st.session_state:
            st.session_state.uploader_shape_checked = False

        if "selected_shape_folder" not in st.session_state:
            st.session_state.selected_shape_folder = []






        # ----------------------------------
        # --- Indicators Parametrization ---
        # ----------------------------------

        # Variables initialization

        

        if "variable_chosen" not in st.session_state:
            st.session_state.variable_chosen = None





        

        

        

        if "resolution" not in st.session_state:
            st.session_state.resolution = 0.2

        if "points_df" not in st.session_state:
            st.session_state.points_df = None

        if "lat_lon" not in st.session_state:
            st.session_state.lat_lon = (None, None)

        if "xaxis_range" not in st.session_state:
            st.session_state.xaxis_range = None

        

        if "raster_params" not in st.session_state:
            st.session_state.raster_params = dict()



        if "reset_folder" not in st.session_state:
            st.session_state.reset_folder = None

    


# Callback Functions

def set_mode():
    # Callback function to save the role selection to Session State
        st.session_state.mode = st.session_state._mode

def reset_uploader():
    """Callback only runs after extraction complete"""
    st.session_state.show_uploader = False

def delete_csv_folder():
    """Deletes the selected csv folder"""
    send2trash(os.path.join(CSV_ZIPPED, st.session_state.selected_csv_folder))
        

def delete_shape_folder():
    """Deletes the selected shape folder"""
    for folder in st.session_state.selected_shape_folder:
        shutil.rmtree(os.path.join(ZIP_FOLDER, folder))
        st.session_state.selected_shape_folder.remove(folder)

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
    if updated_indicator["Yearly Threshold Min List"] != []:
        updated_indicator["Yearly Threshold Min"] = updated_indicator["Yearly Threshold Min List"][0] 
    if updated_indicator["Yearly Threshold Max List"] != []:
        updated_indicator["Yearly Threshold Max"] = updated_indicator["Yearly Threshold Max List"][0]

    st.session_state.df_indicators.loc[index] = updated_indicator
    st.session_state.df_checkbox.loc[index] = updated_checkbox

def modify_custom_list(updated_indicator, label):
    """
    Modifies the custom list of thresholds in the indicator session state.
    Args:
        updated_indicator (dict): The updated indicator.
        label (str): The label of the threshold to modify.
    """
    updated_indicator[f"{label} List"][0] = updated_indicator[label]

    


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
    

def reset_df_indicators():
    st.session_state.df_indicators = pd.DataFrame(columns=st.session_state.indicator.keys())
    st.session_state.df_checkbox = pd.DataFrame(columns=st.session_state.checkbox_defaults.keys())