from utils.imports import *
from lib.session_variables import * 
from utils.variables import *

# ----------------------------
# --- Widget updating part ---
# ----------------------------

## General 
def update_general_information(updated_indicator,i, df_chosen:pd.DataFrame):
    """
    Updates the general information of an indicator through interactive Streamlit widgets.

    Args:
        updated_indicator (dict): The current information of the indicator to be updated.
        i (int): The index or identifier for the indicator, used for widget keys.
        df_chosen (pd.DataFrame): The DataFrame containing the available variables for selection.
    """
    updated_indicator["Name"] = st.text_input("Indicator Name", updated_indicator["Name"], key=f"edit_name_{i}")
    updated_indicator["Variable"] = st.selectbox("Variable", options =df_chosen.columns,
                                                 index=list(df_chosen.columns).index(updated_indicator["Variable"]), 
                                                 key=f"edit_variable_{i}")
    
    updated_indicator["Indicator Type"] = st.selectbox("Indicator Type", options=INDICATOR_TYPES, 
                                                       index=INDICATOR_TYPES.index(updated_indicator["Indicator Type"]), 
                                                       key=f"edit_indicator_type_{i}")


## Daily
def update_daily_threshold(updated_indicator, updated_checkbox_value,label, i):
    """
    Updates a daily threshold indicator using interactive Streamlit widgets.

    Args:
        updated_indicator (dict): The current information of the indicator to be updated.
        updated_checkbox_value (bool): The initial state of the checkbox.
        label (str): The label for the indicator being updated.
        i (int): The index or identifier for the indicator, used for widget keys.
    """
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        
        if st.checkbox(label=label, value=updated_checkbox_value, key=f"edit_{"_".join(label.lower().split(" "))}_checkbox_{i}"):
            with col2:
                updated_indicator[label] = st.number_input(label=label, 
                                                           value=updated_indicator[label], 
                                                           label_visibility="collapsed", 
                                                           key=f"edit_{"_".join(label.lower().split(" "))}_{i}")
        else:
            updated_indicator[label] = None


## Yearly 
def update_yearly_thresholds(updated_indicator, updated_checkbox_value, label, i, thresholds_position):
    """
    Updates yearly thresholds for an indicator using interactive Streamlit widgets. 
    Allows the user to define additional thresholds based on a step value.

    Args:
        updated_indicator (dict): The current information of the indicator to be updated.
        updated_checkbox_value (bool): The initial state of the checkbox.
        label (str): The label for the indicator being updated.
        i (int): The index or identifier for the indicator, used for widget keys.
        thresholds_position (str): Indicates whether additional thresholds are "above" or "below" the main threshold.
    """

    # Basic threshold part
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        if st.checkbox(label=label,value=updated_checkbox_value, key=f"edit_{"_".join(label.lower().split(" "))}_checkbox_{i}"):
            with col2:
                st.write(updated_indicator[label])
                updated_indicator[label] = st.number_input(label, value=updated_indicator[label], label_visibility="collapsed", key=f"edit{"_".join(label.lower().split(" "))}_{i}")
        else:
            updated_indicator[label] = None
            updated_indicator[label+" Step"] = 0
            updated_indicator[label+" List"] = []
    if updated_indicator[label] is not None:
        st.subheader(f"Step {thresholds_position}")
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            st.write(f"""
                            Specify a step value to create additional thresholds above the main threshold. 
                            These thresholds will represent distinct hazard levels (e.g., Low, Moderate, High, Very High). 
                            Each range is calculated by {"adding" if thresholds_position == "above" else "subtraction"} multiples of the step value to the current threshold.
                        """)
        
        with col2:
            updated_indicator[label+" Step"] = step = st.number_input(label="Step",
                                                                        value=updated_indicator[label+" Step"],
                                                                        key=f"edit step {thresholds_position} {i}",
                                                                        label_visibility="collapsed")

            updated_indicator[label+" List"] = [updated_indicator[label] + step * i 
                                                                if thresholds_position == "above" 
                                                                else updated_indicator[label] - step * i
                                                                for i in range(NUM_THRESHOLDS + 1)]
        st.write("Your ohter threshold will be the ones there ", updated_indicator[label+" List"])
    else:
        updated_indicator[label] = None



## Rolling window
def update_window_length(updated_indicator, i, label):
    """
    Updates the window length for an indicator using a number input widget.

    Args:
        updated_indicator (dict): The current information of the indicator to be updated.
        i (int): The index or identifier for the indicator, used for widget keys.
        label (str): The label for the window length parameter.
    """    
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        st.write(label)
    with col2:
        updated_indicator[label] = st.number_input(label, value=updated_indicator[label],
                                                            min_value=2, max_value=365,
                                                            label_visibility="collapsed", 
                                                            key=f"edit_window_length_{i}")
        
def update_window_aggregation(updated_indicator, i, label):
    """
    Updates the aggregation method for a rolling window indicator using a selectbox widget.

    Args:
        updated_indicator (dict): The current information of the indicator to be updated.
        i (int): The index or identifier for the indicator, used for widget keys.
        label (str): The label for the aggregation parameter.
    """
    col1, col2 = st.columns([0.2, 0.8])
    with col1:

        st.write(label)

    with col2:
        updated_indicator[label] = st.selectbox(label=label,
                                                options=AGG_FUNC,
                                                index=AGG_FUNC.index(updated_indicator[label]) if updated_indicator[label] is not None 
                                                                    else INDICATOR_AGG[st.session_state.indicator["Indicator Type"]][0], 
                                                key=f"edit_window_aggregation_{i}", 
                                                disabled=INDICATOR_AGG[updated_indicator["Indicator Type"]][1],
                                                label_visibility="collapsed")
        
## Season shift 
def update_season_shift(updated_indicator, updated_checkbox_value,label, i, max_value):
    """
    Updates the season shift indicator using a checkbox and number input widget.

    Args:
        updated_indicator (dict): The current information of the indicator to be updated.
        updated_checkbox_value (bool): The initial state of the checkbox.
        label (str): The label for the season shift indicator.
        i (int): The index or identifier for the indicator, used for widget keys.
        max_value (int): The maximum allowable value for the season shift.
    """
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        
        if st.checkbox(label=label, value=updated_checkbox_value, key=f"edit_{"_".join(label.lower().split(" "))}_checkbox_{i}"):
            with col2:
                updated_indicator[label] = st.number_input(label=label, 
                                                           value=updated_indicator[label], 
                                                           min_value=0,
                                                           max_value = max_value,
                                                           label_visibility="collapsed", 
                                                           key=f"edit_{"_".join(label.lower().split(" "))}_{i}")
        else:
            updated_indicator[label] = None
    


# -----------------------
# --- Assembling part ---
# -----------------------

def update_daily_threshold_input(updated_indicator, updated_checkbox, i):
    """
    Updates daily thresholds.

    Args:
        updated_indicator (dict): The current information of the indicator to be updated.
        updated_checkbox (dict): The checkbox states for the daily thresholds.
        i (int): The index or identifier for the indicator, used for widget keys.
    """
    st.subheader("Daily Thresholds")
    update_daily_threshold(updated_indicator, updated_checkbox["min_daily_checkbox"],"Daily Threshold Min", i)
    update_daily_threshold(updated_indicator, updated_checkbox["max_daily_checkbox"],"Daily Threshold Max", i)

def update_yearly_thresholds_input(updated_indicator, updated_checkbox, i):
    """
    Updates yearly thresholds.

    Args:
        updated_indicator (dict): The current information of the indicator to be updated.
        updated_checkbox (dict): The checkbox states for the yearly thresholds.
        i (int): The index or identifier for the indicator, used for widget keys.
    """
    st.subheader("Yearly Thresholds")
    update_yearly_thresholds(updated_indicator, updated_checkbox["min_yearly_checkbox"],"Yearly Threshold Min", i, thresholds_position="below")
    update_yearly_thresholds(updated_indicator, updated_checkbox["max_yearly_checkbox"],"Yearly Threshold Max", i, thresholds_position= "above")


def update_rolling_window_input(updated_indicator, i):
    """
    Updates rolling window.

    Args:
        updated_indicator (dict): The current information of the indicator to be updated.
        i (int): The index or identifier for the indicator, used for widget keys.
    """
    st.subheader("Rolling Window Parameters")
    update_window_length(updated_indicator, i, label = "Windows Length")
    update_window_aggregation(updated_indicator, i, label = "Windows Aggregation")


def update_season_shift_input(updated_indicator, updated_checkbox, i,season_start, season_end):
    """
    Updates season shift if it exists.

    Args:
        updated_indicator (dict): The current information of the indicator to be updated.
        updated_checkbox (dict): The checkbox states for the season shift.
        i (int): The index or identifier for the indicator, used for widget keys.
        season_start (int): The start month for the season shift.
        season_end (int): The end month for the season shift.
    """
    st.subheader("Season shift")
    update_season_shift(updated_indicator, updated_checkbox["shift_start_checkbox"],"Season Start Shift", i, season_start)
    update_season_shift(updated_indicator, updated_checkbox["shift_start_checkbox"],"Season Start Shift", i, 12 - season_end)



def update_yearly_aggregation(updated_indicator, i, label):
    """
    Updates yearly aggregation.

    Args:
        updated_indicator (dict): The current information of the indicator to be updated.
        i (int): The index or identifier for the indicator, used for widget keys.
        label (str): The label for the aggregation function.
    """
    st.subheader("Aggregation functions")
    updated_indicator[label] = st.selectbox(label="Yearly Aggregation",
                                            options=AGG_FUNC,
                                            index=AGG_FUNC.index(updated_indicator[label]),
                                            key=f"edit_yearly_aggregation_{i}",
                                            disabled=INDICATOR_AGG[updated_indicator["Indicator Type"]][1])
    
def update_buttons(updated_indicator, row, i):
    """
    Buttons for update management.

    Args:
        updated_indicator (dict): The updated information of the indicator.
        row (pandas.Series): The row corresponding to the current indicator in the dataframe.
        i (int): The index or identifier for the indicator, used for widget keys.
    """
    if st.button(f"Update Indicator: {row['Name']}", key=f"edit_update_{i}"):
        st.session_state.df_indicators.loc[i] = updated_indicator

    st.button(label = "Delete Indicator",key=f"delete_{i}",on_click=lambda index=i: delete_indicator(index))

    
    



