import pandas as pd
import streamlit as st
from utils.variables import *
from lib.session_variables import *


st.set_page_config(layout="wide")

# -------------------------
# --- Handle input part ---
# -------------------------


# Template for creating a new indicator
def handle_checkbox_and_input(label : str, checkbox_key):
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        print(st.session_state.checkbox_defaults[checkbox_key])

        st.session_state.checkbox_defaults[checkbox_key] = st.checkbox(label=label, key=checkbox_key)
    if st.session_state.checkbox_defaults[checkbox_key]:
        with col2:
            st.session_state.indicator[label] = st.number_input(label, value=None, label_visibility="collapsed", key="_".join(label.lower().split(" ")))
    else:
        st.session_state.indicator[label] = None

def handle_threshold_input():

    # Thresholds init
    st.subheader("Thresholds")
    handle_checkbox_and_input(label="Daily Threshold Min", checkbox_key="min_daily_checkbox")
    handle_checkbox_and_input(label="Daily Threshold Max", checkbox_key="max_daily_checkbox")
    handle_checkbox_and_input(label="Yearly Threshold Min", checkbox_key="min_yearly_checkbox")
    handle_checkbox_and_input(label="Yearly Threshold Max", checkbox_key="max_yearly_checkbox")

def handle__season_shift_input():

    # Season shift init 
    st.subheader("Season shift")
    handle_checkbox_and_input(label="Season Start Shift", checkbox_key="shift_start_checkbox")
    handle_checkbox_and_input(label="Season End Shift", checkbox_key="shift_end_checkbox")


def handle_yearly_aggregation_input():
    st.subheader("Aggregation functions")
    st.session_state.indicator["Yearly Aggregation"] = st.selectbox(
            label="Yearly Aggregation",
            options=AGG_FUNC,
            index=INDICATOR_AGG[st.session_state.indicator["Indicator Type"]][0], 
            key="yearly_aggregation", 
            disabled=INDICATOR_AGG[st.session_state.indicator["Indicator Type"]][1]
        )
    
def handle_buttons():
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

def general_information():
    st.subheader("General Information")
    st.session_state.indicator["Name"] = st.text_input("Indicator Name", value=st.session_state.indicator["Name"])
    st.session_state.indicator["Variable"] = st.selectbox("Variable", ["precipitation_sum", "temperature_max_2m"], key="variable")
    indicator_type = st.session_state.indicator["Indicator Type"] = st.selectbox("Indicator Type", options=INDICATOR_TYPES, key="indicator_type")
    return indicator_type

def indicator_building():
    st.subheader("Create indicators")
    with st.expander("Indicator template",expanded=True):
        
        indicator_type = general_information()
        if indicator_type in ["Outlier Days", "Consecutive Outlier Days"]:
            handle_threshold_input()

        handle_yearly_aggregation_input()
        handle__season_shift_input()

        # Button 
        handle_buttons()



# ---------------------------
# --- Handle upadate part ---
# ---------------------------

def general_information_update(updated_indicator,i):
    
    updated_indicator["Name"] = st.text_input("Indicator Name", updated_indicator["Name"], key=f"edit_name_{i}")
    updated_indicator["Variable"] = st.selectbox("Variable", ["precipitation_sum", "temperature_max_2m"], 
                                                 index=["precipitation_sum", "temperature_max_2m"].index(updated_indicator["Variable"]), 
                                                 key=f"edit_variable_{i}")
    
    updated_indicator["Indicator Type"] = st.selectbox("Indicator Type", options=INDICATOR_TYPES, 
                                                       index=INDICATOR_TYPES.index(updated_indicator["Indicator Type"]), 
                                                       key=f"edit_indicator_type_{i}")


def handle_input_update(updated_indicator, updated_checkbox_value,label, i):
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        print(f"edit_{"_".join(label.lower().split(" "))}_checkbox_{i}")
        if st.checkbox(label=label, value=updated_checkbox_value, key=f"edit_{"_".join(label.lower().split(" "))}_checkbox_{i}"):
            with col2:
                updated_indicator[label] = st.number_input(label=label, value=updated_indicator[label], label_visibility="collapsed", key=f"edit_{"_".join(label.lower().split(" "))}_{i}")
        else:
            updated_indicator[label] = None

def handle_threshold_update(updated_indicator, updated_checkbox, i):

    # Handle all the threshold update
    if updated_indicator["Indicator Type"] in ["Outlier Days", "Consecutive Outlier Days"]:
        st.subheader("Thresholds")
        handle_input_update(updated_indicator, updated_checkbox["min_daily_checkbox"],"Daily Threshold Min", i)
        handle_input_update(updated_indicator, updated_checkbox["max_daily_checkbox"],"Daily Threshold Max", i)
        handle_input_update(updated_indicator, updated_checkbox["min_yearly_checkbox"],"Yearly Threshold Min", i)
        handle_input_update(updated_indicator, updated_checkbox["max_yearly_checkbox"],"Yearly Threshold Max", i)

def handle_shift_update(updated_indicator, updated_checkbox, i):
    
    # Handle all the shift update
    st.subheader("Season shift")
    handle_input_update(updated_indicator, updated_checkbox["shift_start_checkbox"],"Season Start Shift", i)
    handle_input_update(updated_indicator, updated_checkbox["shift_end_checkbox"],"Season End Shift", i)



def handle_aggregation_update(updated_indicator, i):
    
    # Handle aggregation function
    st.subheader("Aggregation functions")
    updated_indicator["Yearly Aggregation"] = st.selectbox(label="Yearly Aggregation",
                                                            options=AGG_FUNC,
                                                            index=INDICATOR_AGG[updated_indicator["Indicator Type"]][0],
                                                            key=f"edit_yearly_aggregation_{i}",
                                                            disabled=INDICATOR_AGG[updated_indicator["Indicator Type"]][1])
    
def handle_button_update(updated_indicator, row, i):
    if st.button(f"Update Indicator: {row['Name']}", key=f"edit_update_{i}"):
        st.session_state.df_indicators.loc[i] = updated_indicator

    st.button(label = "Delete Indicator",key=f"delete_{i}",on_click=lambda index=i: delete_indicator(index))

    
    
def indicator_editing():
    if not st.session_state.df_indicators.empty:
        st.subheader("Edit Indicators")
        for (i, row), (j, row_checkbox) in zip(st.session_state.df_indicators.iterrows(), st.session_state.df_checkbox.iterrows()):
            with st.expander(f"Edit Indicator: {row['Name']}"):

                updated_indicator = row.to_dict()
                updated_checkbox = row_checkbox.to_dict()
    
                general_information_update(updated_indicator, i)
                handle_threshold_update(updated_indicator, updated_checkbox, i)
                handle_aggregation_update(updated_indicator, i)
                handle_shift_update(updated_indicator, updated_checkbox, i)
                handle_button_update(updated_indicator, row, i)
                
    else:
        st.write("No indicators available yet.")




# -----------------
# --- Main part ---
# -----------------


# Create tabs to separate the two parts
tab1, tab2 = st.tabs(["Create/Update Indicator", "Edit Existing Indicators"])

# Tab 1: Create or Update an Indicator
with tab1:
    indicator_building()

# Tab 2: Display and Edit Existing Indicators
with tab2:
    indicator_editing()

# Show the dataframe
if not st.session_state.df_indicators.empty:
    st.dataframe(st.session_state.df_indicators, use_container_width=True)
