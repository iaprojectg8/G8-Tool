from utils.imports import *
from lib.session_variables import * 
from utils.variables import *
from lib.widget import display_thresholds



# -----------------------------
# --- Widgets building part ---
# -----------------------------

## General
def general_information(df_chosen :pd.DataFrame):
    """
    Display general information input fields and store the user-provided values in the session state.

    Args:
        df_chosen (pd.DataFrame): The DataFrame containing the available data columns for selection.

    Returns:
        str: The selected indicator type.
    """
    st.subheader("General Information")
    st.session_state.indicator["Name"] = st.text_input("Indicator Name", value=st.session_state.indicator["Name"])
    indicator_type = st.session_state.indicator["Indicator Type"] = st.selectbox("Indicator Type", options=INDICATOR_TYPES, key="indicator_type")
    if indicator_type == "Crossed Variables":
        st.session_state.indicator["Variable"] = st.multiselect(label="Variables", options=df_chosen.columns,key="variables")
    else :
        st.session_state.indicator["Variable"] = st.selectbox("Variable", options=df_chosen.columns,key="variable")
    
    return indicator_type

## Daily
def create_daily_threshold(label : str, checkbox_key):
    """
    Creates a UI component consisting of a checkbox and a corresponding number input field 
    that becomes visible when the checkbox is selected.

    Args:
        label (str): The label for the checkbox and number input.
        checkbox_key (str): A unique key to identify the checkbox in the Streamlit session state.
    """
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        st.session_state.checkbox_defaults[checkbox_key] = st.checkbox(label=label, key=checkbox_key)
        
    if st.session_state.checkbox_defaults[checkbox_key]:
        with col2:
            st.session_state.indicator[label] = st.number_input(label, value=None, label_visibility="collapsed", key="_".join(label.lower().split(" ")))
    else:
        st.session_state.indicator[label] = None


## Yearly
def create_yearly_thresholds(label : str, checkbox_key, list_checkbox_key, thresholds_position):    
    """
    Handles the creation of a checkbox and a number input for setting a maximum yearly aggregation threshold.
    Allows defining additional thresholds above the entered value by specifying step values.

    Args:
        label (str): The label for the checkbox and number input.
        checkbox_key (str): A unique key for the checkbox in the session state.
    """

    # Basic threshold part
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        st.session_state.checkbox_defaults[checkbox_key] = st.checkbox(label=label, key=checkbox_key)
        
    if st.session_state.checkbox_defaults[checkbox_key]:
        with col2:
            st.session_state.indicator[label] = step = st.number_input(label, value=None, label_visibility="collapsed", key="_".join(label.lower().split(" ")))
        
        # Step part
        if st.session_state.indicator[label] is not None:
            
            st.session_state.checkbox_defaults[list_checkbox_key] =  st.checkbox(label="Custom your thresholds",
                                                                                         key=f"create_threshold_list{thresholds_position}")
            if st.session_state.checkbox_defaults[list_checkbox_key]:
                st.subheader(f"Custom List")
                col1, col2 = st.columns([0.5, 0.5])
                with col1:
                    st.write(f"""
                                Specify a custom thesholds list to replace the step creation method
                            """)
                with col2:
                    st.session_state.indicator[label+" List"] = ast.literal_eval(st.text_input(
                                                                                    label="Put a list",
                                                                                    value=st.session_state.indicator[label+" List"],
                                                                                    key="create_threshold_list", 
                                                                                    label_visibility="collapsed"),
                                                                                    )
            else :
                st.subheader(f"Step {thresholds_position}")
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    st.write(f"""
                            Specify a step value to create additional thresholds above the main threshold. 
                            These thresholds will represent distinct hazard levels (e.g., Low, Moderate, High, Very High). 
                            Each range is calculated by {"adding" if thresholds_position == "above" else "subtraction"} multiples of the step value to the current threshold.
                        """)
            
                with col2:
                    st.session_state.indicator[label+ " Step"] = step = st.number_input(label="Step", key=f"step {thresholds_position}", label_visibility="collapsed")
                    st.session_state.indicator[label+" List"] = [st.session_state.indicator[label] + step * i 
                                                                    if thresholds_position == "above" 
                                                                    else st.session_state.indicator[label] - step * i
                                                                    for i in range(NUM_THRESHOLDS)]


        # Display the list of thresholds in a table format
        if st.session_state.indicator[label] is not None:
            display_thresholds(st.session_state.indicator, label)
    else:
        st.session_state.indicator[label] = None


## Rolling window part
def create_window_length(label):
    """
    Creates an input section for specifying the rolling window length.

    Args:
        label (str): The label to display and use as the key in session state.
    """
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        st.write(label)
    with col2:
        st.session_state.indicator[label] = st.number_input(label, value=None,
                                                            min_value=2, max_value=365,
                                                            label_visibility="collapsed", 
                                                            key="_".join(label.lower().split(" ")))
        
def create_window_aggregation(label):
    """
    Creates an input section for selecting the aggregation function for a rolling window.

    Args:
        label (str): The label for the aggregation function.
    """
    col1, col2 = st.columns([0.2, 0.8])
    with col1:

        st.write(label)
    with col2:
        st.session_state.indicator[label] = st.selectbox(label=label,
                                                        options=AGG_FUNC,
                                                        index=INDICATOR_AGG[st.session_state.indicator["Indicator Type"]][0], 
                                                        key="_".join(label.lower().split(" ")), 
                                                        disabled=INDICATOR_AGG[st.session_state.indicator["Indicator Type"]][1],
                                                        label_visibility="collapsed")

## Aggregations
def create_yearly_aggregation():
    """
    Displays an aggregation function selection for yearly data.
    """
    st.subheader("Aggregation functions")

    # Dropdown to choose aggregation function based on indicator type
    st.session_state.indicator["Yearly Aggregation"] = st.selectbox(
            label="Yearly Aggregation",
            options=AGG_FUNC,
            index=INDICATOR_AGG[st.session_state.indicator["Indicator Type"]][0], 
            key="yearly_aggregation", 
            disabled=INDICATOR_AGG[st.session_state.indicator["Indicator Type"]][1])
    

## Season Shift
def create_season_shift(label:str, checkbox_key, max_value):
    """
    Handles the input for a checkbox and associated number input for seasonal shift.

    Args:
        label (str): The label for the checkbox and number input.
        checkbox_key: The key used for storing the checkbox state in session state.
        max_value: The maximum value allowed for the number input.
    """
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        st.session_state.checkbox_defaults[checkbox_key] = st.checkbox(label=label, key=checkbox_key)
        
    if st.session_state.checkbox_defaults[checkbox_key]:
        with col2:
            st.session_state.indicator[label] = st.number_input(label, value=None,
                                                                 min_value=0, max_value=max_value,
                                                                 label_visibility="collapsed", 
                                                                 key="_".join(label.lower().split(" ")))
    else:
        st.session_state.indicator[label] = None


## Buttons
def create_buttons():
    """
    Handles the button actions for adding and resetting indicators.
    """
    if st.button(label="Add Indicator"):
        if st.session_state.indicator["Name"] is None:
            st.error("Your indicator is empty, you can't add it to your indicators list")

        elif st.session_state.indicator["Name"] not in st.session_state.df_indicators["Name"].values:
            
            # Add new row
            st.session_state.df_indicators = st.session_state.df_indicators._append(st.session_state.indicator, ignore_index=True)
            st.session_state.df_checkbox = st.session_state.df_checkbox._append(st.session_state.checkbox_defaults, ignore_index=True)
        else:
            st.warning("This indicator already exists in your indicators list")
    st.button(label="Reset Indicator", on_click=reset_indicator)


# -----------------------
# --- Assembling part ---
# -----------------------

def create_daily_threshold_input():
    """
    Handles the input for daily thresholds, including minimum and maximum thresholds.
    """
    st.subheader("Daily Thresholds")
    create_daily_threshold(label="Daily Threshold Min", checkbox_key="min_daily_checkbox")
    create_daily_threshold(label="Daily Threshold Max", checkbox_key="max_daily_checkbox")

def create_yearly_thresholds_input():
    """
    Creates the input for yearly thresholds, including minimum and maximum thresholds.
    """
    st.subheader("Yearly Thresholds")
    create_yearly_thresholds(label="Yearly Threshold Min", checkbox_key="min_yearly_checkbox",
                             list_checkbox_key="threshold_list_checkbox_min", thresholds_position="below")
    create_yearly_thresholds(label="Yearly Threshold Max", checkbox_key="max_yearly_checkbox",
                             list_checkbox_key="threshold_list_checkbox_max", thresholds_position="above")


def create_rolling_window_input():
    """
    Creates the input for rolling window parameters, including length and aggregation.
    """
    st.subheader("Rolling Window Parameters")
    create_window_length(label = "Windows Length")
    create_window_aggregation(label = "Windows Aggregation")


def create_season_shift_input(season_start, season_end):
    """
    Creates the input for season shift parameters, including season start and end shifts.

    Args:
        season_start: The start of the season (used to limit max value for season start shift).
        season_end: The end of the season (used to limit max value for season end shift).
    """
    st.subheader("Season shift")
    if season_start is not None and season_end is not None:
        create_season_shift(label="Season Start Shift", checkbox_key="shift_start_checkbox",max_value=season_start )
        create_season_shift(label="Season End Shift", checkbox_key="shift_end_checkbox", max_value=12-season_end)


def create_built_indicator():
    """
    Creates a select box for choosing a built-in indicator and stores the selected indicator
    in the session state.

    """
    st.session_state["Builtin Indicator"] = st.selectbox("Indicator", options=BUILTIN_INDICATORS)


    




