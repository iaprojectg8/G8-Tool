from utils.imports import * 


if "indicator" not in st.session_state:
    st.session_state.indicator = {
        "Name": "",
        "Variable": None,
        "Indicator Type": None,
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
        "shift_end_checkbox": False
    }

if "df_checkbox" not in st.session_state:
    st.session_state.df_checkbox = pd.DataFrame(columns=st.session_state.checkbox_defaults.keys())
    
if "columns_chosen" not in st.session_state:
    st.session_state.columns_chosen = None


if "season_start" not in st.session_state:
    st.session_state.season_start = 6


if "season_end" not in st.session_state:
    st.session_state.season_end = 10


def delete_indicator(index):
    """
    Deletes an indicator from the list of indicators.
    Args:
        index (int): The index of the indicator to delete.
    """
    print("index", index)
    st.session_state.df_indicators = st.session_state.df_indicators.drop(index).reset_index(drop=True)

def update_indicator(index, updated_indicator):
    """
    Updates in the indicator dataframe at the given index.
    Args:
        index (int): The index of the indicator to update.
        updated_indicator (dict): The updated indicator.
    """
    st.session_state.df_indicators.loc[index] = updated_indicator


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
    

    