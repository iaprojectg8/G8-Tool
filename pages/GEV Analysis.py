import streamlit as st
import pandas as pd

# Initialize the session state to store indicators
if "indicators" not in st.session_state:
    st.session_state.indicators = []

# Sidebar form for creating a new indicator
with st.form("Indicator Form"):
    st.subheader("Create a New Indicator")

    # Input fields for indicator details
    name = st.text_input("Indicator Name")
    variable = st.selectbox("Variable", ["precipitation_sum", "temperature_max_2m"])
    yearly_agg = st.selectbox("Yearly Aggregation", ["sum", "mean", "max", "min"])
    daily_thresh_min = st.number_input("Daily Threshold Min", value=0.0)
    daily_thresh_max = st.number_input("Daily Threshold Max", value=100.0)
    yearly_thresh_min = st.number_input("Yearly Threshold Min", value=0.0)
    yearly_thresh_max = st.number_input("Yearly Threshold Max", value=100.0)

    # Submit button
    submitted = st.form_submit_button("Add Indicator")

    if submitted:
        # Store the indicator details in the session state
        indicator = {
            "Name": name,
            "Variable": variable,
            "Yearly Agg": yearly_agg,
            "Daily Threshold Min": daily_thresh_min,
            "Daily Threshold Max": daily_thresh_max,
            "Yearly Threshold Min": yearly_thresh_min,
            "Yearly Threshold Max": yearly_thresh_max,
        }
        st.session_state.indicators.append(indicator)
        st.success(f"Indicator '{name}' added successfully!")

# Display the list of indicators
st.subheader("List of Indicators")

if st.session_state.indicators:
    # Convert indicators to DataFrame
    indicators_df = pd.DataFrame(st.session_state.indicators)

    # Display the DataFrame with an editable option
    edited_df = st.data_editor(indicators_df, use_container_width=True, hide_index=True)

    # Identify if any row was edited
    if not indicators_df.equals(edited_df):
        st.session_state.indicators = edited_df.to_dict(orient='records')
        st.success("Indicator updated successfully!")

    # Delete an indicator
    delete_index = st.selectbox("Select Indicator to Delete", indicators_df.index)
    if st.button("Delete Indicator"):
        st.session_state.indicators.pop(delete_index)
        st.success("Indicator deleted successfully!")
else:
    st.write("No indicators created yet.")
