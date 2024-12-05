import pandas as pd
import streamlit as st
from utils.variables import *
from lib.session_variables import *

# Assuming AGG_FUNC and INDICATOR_TYPES are already defined somewhere in the code
st.set_page_config(layout="wide")
# Sample data for the first run, in case session_state is empty


if "indicator" not in st.session_state:
    st.session_state.indicator = {
        "Name": "",
        "Variable": None,
        "Indicator Type": None,
        "Daily Threshold Min": None,
        "Daily Threshold Max": None,
        "Yearly Threshold Min": None,
        "Yearly Threshold Max": None,
        "Yearly Aggregation": None,
        "Season Start Shift": None,
        "Season End Shift": None
    }
    # print(st.session_state.indicator

if "checkbox_defaults" not in st.session_state:
    st.session_state.checkbox_defaults = {
        "min_daily_checkbox": False,
        "max_daily_checkbox": False,
        "min_yearly_checkbox": False,
        "max_yearly_checkbox": False,
        "shift_start_checkbox": False,
        "shift_end_checkbox": False
    }

def reset_indicator():
    st.session_state.indicator = {
        "Name": "",
        "Variable": None,
        "Indicator Type": None,
        "Daily Threshold Min": None,
        "Daily Threshold Max": None,
        "Yearly Threshold Min": None,
        "Yearly Threshold Max": None,
        "Yearly Aggregation": None,
        "Season Start Shift": None,
        "Season End Shift": None
    }
    st.session_state.daily_threshold_min_checkbox= False
    st.session_state.daily_threshold_max_checkbox = False
    st.session_state.yearly_threshold_min_checkbox = False
    st.session_state.yearly_threshold_max_checkbox = False
    st.session_state.season_start_shift_checkbox = False
    st.session_state.season_end_shift_checkbox = False
    
if 'df_indicators' not in st.session_state:
    st.session_state.df_indicators = pd.DataFrame(columns=st.session_state.indicator.keys())

if "df_checkbox" not in st.session_state:
    st.session_state.df_checkbox = pd.DataFrame(columns=st.session_state.checkbox_defaults.keys())

# Template for creating a new indicator



# Create tabs to separate the two parts
tab1, tab2 = st.tabs(["Create/Update Indicator", "Edit Existing Indicators"])

# Tab 1: Create or Update an Indicator
with tab1:
    st.subheader("Create indicators")
    with st.expander("Indicator template"):
        st.subheader("General Information")
        st.session_state.indicator["Name"] = st.text_input("Indicator Name", value=st.session_state.indicator["Name"])
        st.session_state.indicator["Variable"] = st.selectbox("Variable", ["precipitation_sum", "temperature_max_2m"], key="variable")
        indicator_type = st.session_state.indicator["Indicator Type"] = st.selectbox("Indicator Type", options=INDICATOR_TYPES, key="indicator_type")

        if indicator_type in ["Outlier Days Sum", "Consecutive Outlier Days Sum"]:
            st.subheader("Thresholds")

            # Daily Threshold Min
            col1, col2 = st.columns([0.2, 0.8])
            with col1:
            
                st.session_state.checkbox_defaults["min_daily_checkbox"] = st.checkbox(
                    label="Daily Threshold Min", key="daily_threshold_min_checkbox"
                )

            if st.session_state.checkbox_defaults["min_daily_checkbox"]:
                with col2:
                    st.session_state.indicator["Daily Threshold Min"] = st.number_input(
                        label="Daily Threshold Min", value=st.session_state.indicator["Daily Threshold Min"],
                        label_visibility="collapsed", key="daily_threshold_min"
                    )
            else:
                st.session_state.indicator["Daily Threshold Min"]=None

            # Daily Threshold Max
            col1, col2 = st.columns([0.2, 0.8])
            with col1:
                st.session_state.checkbox_defaults["max_daily_checkbox"] = st.checkbox(
                    label="Daily Threshold Max", key="daily_threshold_max_checkbox"
                )
            if st.session_state.checkbox_defaults["max_daily_checkbox"]:
                with col2:
                    st.session_state.indicator["Daily Threshold Max"] = st.number_input(
                        label="Daily Threshold Max", value=st.session_state.indicator["Daily Threshold Max"],
                        label_visibility="collapsed", key="daily_threshold_max"
                    )
            else:
                st.session_state.indicator["Daily Threshold Max"] = None


            # Yearly Threshold Min
            col1, col2 = st.columns([0.2, 0.8])
            with col1:
                st.session_state.checkbox_defaults["min_yearly_checkbox"] = st.checkbox(
                    label="Yearly Threshold Min", key="yearly_threshold_min_checkbox"
                )
            if st.session_state.checkbox_defaults["min_yearly_checkbox"]:
                with col2:
                    st.session_state.indicator["Yearly Threshold Min"] = st.number_input(
                        label="Yearly Threshold Min", value=st.session_state.indicator["Yearly Threshold Min"],
                        label_visibility="collapsed", key="yearly_threshold_min"
                    )
            else:
                st.session_state.indicator["Yearly Threshold Min"] = None

            # Yearly Threshold Max
            col1, col2 = st.columns([0.2, 0.8])
            with col1:
                st.session_state.checkbox_defaults["max_yearly_checkbox"] = st.checkbox(
                    label="Yearly Threshold Max", key="yearly_threshold_max_checkbox"
                )
            if st.session_state.checkbox_defaults["max_yearly_checkbox"]:
                with col2:
                    st.session_state.indicator["Yearly Threshold Max"] = st.number_input(
                        label="Yearly Threshold Max", value=st.session_state.indicator["Yearly Threshold Max"],
                        label_visibility="collapsed", key="yearly_threshold_max"
                    )
            else: 
                st.session_state.indicator["Yearly Threshold Max"] = None

        st.subheader("Aggregation functions")
        st.session_state.indicator["Yearly Aggregation"] = st.selectbox(
            label="Yearly Aggregation", options=AGG_FUNC, key="yearly_aggregation"
        )

        st.subheader("Season shift")

        # Season Start Shift
        col1, col2 = st.columns([0.2, 0.8])
        with col1:
            st.session_state.checkbox_defaults["shift_start_checkbox"] = st.checkbox(
                label="Season Start Shift (in months)", key="season_start_shift_checkbox"
            )
        if st.session_state.checkbox_defaults["shift_start_checkbox"]:
            with col2:
                st.session_state.indicator["Season Start Shift"] = st.number_input(
                    label="Season Start Shift", value=st.session_state.indicator["Season Start Shift"],
                    label_visibility="collapsed", key="season_start_shift"
                )
        else:
            st.session_state.indicator["Season Start Shift"] = None
        # Season End Shift
        col1, col2 = st.columns([0.2, 0.8])
        with col1:
            st.session_state.checkbox_defaults["shift_end_checkbox"] = st.checkbox(
                label="Season End Shift (in months)", key="season_end_shift_checkbox"
            )
        if st.session_state.checkbox_defaults["shift_end_checkbox"]:
            with col2:
                st.session_state.indicator["Season End Shift"] = st.number_input(
                    label="Season End Shift",
                    label_visibility="collapsed", key="season_end_shift"
                )
        else:
            st.session_state.indicator["Season End Shift"] = None

        if st.button(label="Add or Update Indicator"):
  
            if st.session_state.indicator["Name"] is None:
       
                st.error("Your indicator is empty, you can't add it to your indicators list")
            elif st.session_state.indicator["Name"] not in st.session_state.df_indicators["Name"].values:
                # Add new row
          
                st.session_state.df_indicators = st.session_state.df_indicators._append(st.session_state.indicator, ignore_index=True)
                st.session_state.df_checkbox = st.session_state.df_checkbox._append(st.session_state.checkbox_defaults, ignore_index=True)
                print(st.session_state.df_indicators)
                print(st.session_state.df_checkbox)
            else:
                st.warning("This indicator already exists in your indicators list")
            # Add new row if the indicator doesn't exist, else update the existing one
            
            #     # Update existing row
            #     idx = st.session_state.df_indicators[st.session_state.df_indicators["Name"] == indicator["Name"]].index[0]
            #     st.session_state.df_indicators.loc[idx] = indicator
        st.button(label="Reset the indicator", on_click=reset_indicator)



    # if not st.session_state.df_indicators.empty:
    #     st.dataframe(st.session_state.df_indicators, use_container_width=True)

# Tab 2: Display and Edit Existing Indicators
with tab2:
    if not st.session_state.df_indicators.empty:
        st.subheader("Edit Indicators")
        for (i, row), (j, row_checkbox) in zip(st.session_state.df_indicators.iterrows(), st.session_state.df_checkbox.iterrows()):
          
            with st.expander(f"Edit Indicator: {row['Name']}"):
                # Display the same form as used for creating indicators, pre-fill with the existing values
                updated_indicator = row.to_dict()
                updated_checkbox = row_checkbox.to_dict()
                print(j)
                print(updated_checkbox)
        

                updated_indicator["Name"] = st.text_input("Indicator Name", updated_indicator["Name"], key=f"edit_name_{i}")
                updated_indicator["Variable"] = st.selectbox("Variable", ["precipitation_sum", "temperature_max_2m"], index=["precipitation_sum", "temperature_max_2m"].index(updated_indicator["Variable"]), key=f"edit_variable_{i}")
                updated_indicator["Indicator Type"] = st.selectbox("Indicator Type", options=INDICATOR_TYPES, index=INDICATOR_TYPES.index(updated_indicator["Indicator Type"]), key=f"edit_indicator_type_{i}")

                if updated_indicator["Indicator Type"] in ["Outlier Days Sum", "Consecutive Outlier Days Sum"]:
                    st.subheader("Thresholds")
                    col1, col2 = st.columns([0.2, 0.8])
                    with col1:
                        if st.checkbox(label="Daily Threshold Min", value=updated_checkbox["min_daily_checkbox"], key=f"edit_daily_threshold_min_checkbox_{i}"):
                            with col2:
                                updated_indicator["Daily Threshold Min"] = st.number_input(label="Daily Threshold Min", value=updated_indicator["Daily Threshold Min"], label_visibility="collapsed", key=f"edit_daily_threshold_min_{i}")
                        else:
                            updated_indicator["Daily Threshold Min"] = None
                    
                    col1, col2 = st.columns([0.2, 0.8])
                    with col1:
                        if st.checkbox(label="Daily Threshold Max", value=updated_checkbox["max_daily_checkbox"], key=f"edit_daily_threshold_max_checkbox_{i}"):
                            with col2:
                                updated_indicator["Daily Threshold Max"] = st.number_input(label="Daily Threshold Max", value=updated_indicator["Daily Threshold Max"], label_visibility="collapsed", key=f"edit_daily_threshold_max_{i}")
                        else:
                            updated_indicator["Daily Threshold Max"] = None
                    
                    col1, col2 = st.columns([0.2, 0.8])
                    with col1:
                        if st.checkbox(label="Yearly Threshold Min", value=updated_checkbox["min_yearly_checkbox"], key=f"edit_yearly_threshold_min_checkbox_{i}"):
                            with col2:
                                updated_indicator["Yearly Threshold Min"] = st.number_input(label="Yearly Threshold Min", value=updated_indicator["Yearly Threshold Min"], label_visibility="collapsed", key=f"edit_yearly_threshold_min_{i}")
                        else:
                            updated_indicator["Yearly Threshold Min"] = None
                    
                    col1, col2 = st.columns([0.2, 0.8])
                    with col1:
                        if st.checkbox(label="Yearly Threshold Max", value=updated_checkbox["max_yearly_checkbox"], key=f"edit_yearly_threshold_max_checkbox_{i}"):
                            with col2:
                                updated_indicator["Yearly Threshold Max"] = st.number_input(label="Yearly Threshold Max", value=updated_indicator["Yearly Threshold Max"], label_visibility="collapsed", key=f"edit_yearly_threshold_max_{i}")

                st.subheader("Aggregation functions")
                updated_indicator["Yearly Aggregation"] = st.selectbox(label="Yearly Aggregation", options=AGG_FUNC, index=AGG_FUNC.index(updated_indicator["Yearly Aggregation"]), key=f"edit_yearly_aggregation_{i}")
                st.subheader("Season shift")
                col1, col2 = st.columns([0.3, 0.7])
                with col1:
                    if st.checkbox(label="Season Start Shift (in months)", value=updated_checkbox["shift_start_checkbox"], key=f"edit_season_start_shift_checkbox_{i}"):
                        with col2:
                            updated_indicator["Season Start Shift"] = st.number_input(label="Season Start Shift", value=updated_indicator["Season Start Shift"], label_visibility="collapsed", key=f"edit_season_start_shift_{i}")  
                    else:
                        updated_indicator["Season Start Shift"] = None
                
                col1, col2 = st.columns([0.3, 0.7])
                with col1:
                    if st.checkbox(label="Season End Shift (in months)", value=updated_checkbox["shift_end_checkbox"], key=f"edit_season_end_shift_checkbox_{i}"):
                        with col2:
                            updated_indicator["Season End Shift"] = st.number_input(label="Season End Shift", value=updated_indicator["Season End Shift"], label_visibility="collapsed", key=f"edit_season_end_shift_{i}")
                    else:
                        updated_indicator["Season End Shift"] = None
                
                if st.button(f"Update Indicator: {row['Name']}", key=f"edit_update_{i}"):
                    st.session_state.df_indicators.loc[i] = updated_indicator

                st.button(label = "Delete Indicator",key=f"delete_{i}",on_click=lambda : delete_indicator(i))


    else:
        st.write("No indicators available yet.")

# Show the dataframe in the "Creating" tab
if not st.session_state.df_indicators.empty:
    st.dataframe(st.session_state.df_indicators, use_container_width=True)
