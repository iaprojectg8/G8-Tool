from utils.imports import *
from lib.session_variables import * 
from utils.variables import *

# ---------------------------
# --- Handle upadate part ---
# ---------------------------

def general_information_update(updated_indicator,i, df_chosen:pd.DataFrame):
    
    updated_indicator["Name"] = st.text_input("Indicator Name", updated_indicator["Name"], key=f"edit_name_{i}")
    updated_indicator["Variable"] = st.selectbox("Variable", options =df_chosen.columns,
                                                 index=list(df_chosen.columns).index(updated_indicator["Variable"]), 
                                                 key=f"edit_variable_{i}")
    
    updated_indicator["Indicator Type"] = st.selectbox("Indicator Type", options=INDICATOR_TYPES, 
                                                       index=INDICATOR_TYPES.index(updated_indicator["Indicator Type"]), 
                                                       key=f"edit_indicator_type_{i}")


def handle_input_update(updated_indicator, updated_checkbox_value,label, i):
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

        
def update_rolling_window(updated_indicator, i):
    if updated_indicator["Indicator Type"] == "Sliding Windows Aggregation":
        handle_update_window_lenght(updated_indicator, i, label = "Windows Length")
        handle_update_window_aggregation(updated_indicator, i, label = "Windows Aggregation")

def handle_update_window_lenght(updated_indicator, i, label):

    st.subheader("Rolling Window Parameters")
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        st.write(label)
    with col2:
        updated_indicator[label] = st.number_input(label, value=updated_indicator[label],
                                                            min_value=2, max_value=365,
                                                            label_visibility="collapsed", 
                                                            key=f"edit_window_length_{i}")
        
def handle_update_window_aggregation(updated_indicator, i, label):
    col1, col2 = st.columns([0.2, 0.8])
    with col1:

        st.write(label)

    with col2:
        updated_indicator[label] = st.selectbox(label=label,
                                                options=AGG_FUNC,
                                                index=AGG_FUNC.index(updated_indicator[label]), 
                                                key=f"edit_window_aggregation_{i}", 
                                                disabled=INDICATOR_AGG[updated_indicator["Indicator Type"]][1],
                                                label_visibility="collapsed"
                                            )


    
def handle_input_update_season_shift_start(updated_indicator, updated_checkbox_value,label, i, season_start):
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        
        if st.checkbox(label=label, value=updated_checkbox_value, key=f"edit_{"_".join(label.lower().split(" "))}_checkbox_{i}"):
            with col2:
                updated_indicator[label] = st.number_input(label=label, 
                                                           value=updated_indicator[label], 
                                                           min_value=0,
                                                           max_value = season_start,
                                                           label_visibility="collapsed", 
                                                           key=f"edit_{"_".join(label.lower().split(" "))}_{i}")
        else:
            updated_indicator[label] = None

def handle_input_update_season_shift_end(updated_indicator, updated_checkbox_value,label, i, season_end):
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        
        if st.checkbox(label=label, value=updated_checkbox_value, key=f"edit_{"_".join(label.lower().split(" "))}_checkbox_{i}"):
            with col2:
                updated_indicator[label] = st.number_input(label=label, 
                                                           value=updated_indicator[label], 
                                                           min_value=0,
                                                           max_value = 12 - season_end,
                                                           label_visibility="collapsed", 
                                                           key=f"edit_{"_".join(label.lower().split(" "))}_{i}")
        else:
            updated_indicator[label] = None

def handle_update_checkbox_and_input_yearly_agg_min(updated_indicator, updated_checkbox_value, label, i):
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
        st.subheader("Step below")
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            st.write("""Choose a step value to define additional thresholds below the current one. 
                    Each step will determine the range for hazard levels (e.g., Low, Moderate, High, Very High).
                    Starting from the current threshold, each subsequent range will be created by substracting the step value.""")
        
        with col2:
            updated_indicator[label+" Step"] = step = st.number_input(label="Step",
                                                                        value=updated_indicator[label+" Step"],
                                                                        key=f"edit step below {i}",
                                                                        label_visibility="collapsed")

            updated_indicator[label+" List"] = [updated_indicator[label] - step * i for i in range(NUM_THRESHOLDS + 1)]
        st.write("Your ohter threshold will be the ones there ", updated_indicator[label+" List"])
    else:
        updated_indicator[label] = None

def handle_update_checkbox_and_input_yearly_agg_max(updated_indicator, updated_checkbox_value, label, i):
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
 
        if st.checkbox(label=label, value=updated_checkbox_value, key=f"edit_{"_".join(label.lower().split(" "))}_checkbox_{i}"):
            with col2:
                st.write(updated_indicator[label])
                updated_indicator[label] = st.number_input(label, value=updated_indicator[label], label_visibility="collapsed",  key=f"edit{"_".join(label.lower().split(" "))}_{i}")
        else:
            updated_indicator[label] = None
            updated_indicator[label+" Step"] = 0
            updated_indicator[label+" List"] = []
    if updated_indicator[label] is not None:
        col1, col2 = st.columns([0.8, 0.2])
        st.subheader("Step above")
        with col1:
            st.write("""Choose a step value to define additional thresholds above the current one. 
                    Each step will determine the range for hazard levels (e.g., Low, Moderate, High, Very High).
                    Starting from the current threshold, each subsequent range will be created by adding the step value.""")
        
        with col2:
            st.write(updated_indicator[label+" Step"])
            updated_indicator[label+" Step"] = step = st.number_input(label="Step",
                                                                        value=updated_indicator[label+" Step"],
                                                                        key=f"edit step above {i}",
                                                                        label_visibility="collapsed")

            updated_indicator[label+" List"] = [updated_indicator[label] + step * i for i in range(NUM_THRESHOLDS + 1)]
        st.write("Your ohter threshold will be the ones there ", updated_indicator[label+" List"])



def handle_threshold_update(updated_indicator, updated_checkbox, i):

    # Handle all the threshold update
    if updated_indicator["Indicator Type"] in ["Outlier Days", "Consecutive Outlier Days"]:
        
        handle_threshold_daily_update(updated_indicator, updated_checkbox, i)
        handle_threshold_yearly_update(updated_indicator, updated_checkbox, i)
    elif updated_indicator["Indicator Type"] == "Season Aggregation":
        handle_threshold_yearly_update(updated_indicator, updated_checkbox, i)
    if updated_indicator["Indicator Type"] == "Sliding Windows Aggregation":
        update_rolling_window(updated_indicator, i)
        handle_threshold_yearly_update(updated_indicator, updated_checkbox, i)

def handle_threshold_daily_update(updated_indicator, updated_checkbox, i):
    st.subheader("Daily Thresholds")
    handle_input_update(updated_indicator, updated_checkbox["min_daily_checkbox"],"Daily Threshold Min", i)
    handle_input_update(updated_indicator, updated_checkbox["max_daily_checkbox"],"Daily Threshold Max", i)

def handle_threshold_yearly_update(updated_indicator, updated_checkbox, i):
    st.subheader("Yearly Thresholds")
    handle_update_checkbox_and_input_yearly_agg_min(updated_indicator, updated_checkbox["min_yearly_checkbox"],"Yearly Threshold Min", i)
    handle_update_checkbox_and_input_yearly_agg_max(updated_indicator, updated_checkbox["max_yearly_checkbox"],"Yearly Threshold Max", i)




def handle_shift_update(updated_indicator, updated_checkbox, i,season_start, season_end):
    
    # Handle all the shift update
    st.subheader("Season shift")
    handle_input_update_season_shift_start(updated_indicator, updated_checkbox["shift_start_checkbox"],"Season Start Shift", i, season_start)
    handle_input_update_season_shift_end(updated_indicator, updated_checkbox["shift_end_checkbox"],"Season End Shift", i, season_end)



def handle_aggregation_update(updated_indicator, i, label):
    
    # Handle aggregation function
    st.subheader("Aggregation functions")
    updated_indicator[label] = st.selectbox(label="Yearly Aggregation",
                                                            options=AGG_FUNC,
                                                            index=AGG_FUNC.index(updated_indicator[label]),
                                                            key=f"edit_yearly_aggregation_{i}",
                                                            disabled=INDICATOR_AGG[updated_indicator["Indicator Type"]][1])
    
def handle_button_update(updated_indicator, row, i):
    if st.button(f"Update Indicator: {row['Name']}", key=f"edit_update_{i}"):
        st.session_state.df_indicators.loc[i] = updated_indicator

    st.button(label = "Delete Indicator",key=f"delete_{i}",on_click=lambda index=i: delete_indicator(index))

    
    




