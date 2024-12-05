from utils.imports import *
from utils.variables import *
from lib.session_variables import *



indicator = {
    "Name": None,
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
with st.container(border=True):


    st.subheader("General Informations")
    indicator["Name"] = st.text_input("Indicator Name")
    indicator["Variable"] = st.selectbox("Variable", ["precipitation_sum", "temperature_max_2m"])
    indicator_type = indicator["Indicator Type"] = st.selectbox("Indicator Type", options=INDICATOR_TYPES)



    
    if indicator_type in ["Outlier Days Sum", "Consecutive Outlier Days Sum",]:
        st.subheader("Thresholds")
        col1, col2 = st.columns([0.2,0.8])
        with col1:
            # daily_threshold_min_box= st.checkbox(label="Daily Threshold Min")
            if st.checkbox(label="Daily Threshold Min"):
                with col2:
                    indicator["Daily Threshold Min"] = st.number_input(label="Daily Threshold Min",value=None, label_visibility="collapsed")
            # daily_threshold_max_box= st.checkbox(label="Daily Threshold Max")
        col1, col2 = st.columns([0.2,0.8])
        with col1:
            if st.checkbox(label="Daily Threshold Max"):
                with col2:
                    indicator["Daily Threshold Max"] = st.number_input(label="Daily Threshold Max",value=None, label_visibility="collapsed")
        col1, col2 = st.columns([0.2,0.8])
        with col1:
            # daily_threshold_min_box= st.checkbox(label="Daily Threshold Min")
            if st.checkbox(label="Yearly Threshold Min"):
                with col2:
                    indicator["Yearly Threshold Min"] = st.number_input(label="Yearly Threshold Min",value=None, label_visibility="collapsed")
            # daily_threshold_max_box= st.checkbox(label="Daily Threshold Max")
        col1, col2 = st.columns([0.2,0.8])
        with col1:
            if st.checkbox(label="Yearly Threshold Max"):
                with col2:
                    indicator["Yearly Threshold Max"] = st.number_input(label="Yearly Threshold Max",value=None, label_visibility="collapsed")


    st.subheader("Aggregation functions")
    if indicator_type == "Outlier Days Sum":
        indicator["Yearly Aggregation"] = st.selectbox(label="Yearly Aggregation", options=AGG_FUNC, index=1,disabled=True)
    elif indicator_type == "Consecutive Outlier Days Sum":
        indicator["Yearly Aggregation"] = st.selectbox(label="Yearly Aggregation", options = AGG_FUNC, index=3,disabled=True)
    elif indicator_type == "Season Sum":
        indicator["Yearly Aggregation"] = st.selectbox(label="Yearly Aggregation", options = AGG_FUNC, index=1,disabled=True)
    elif indicator_type == "Monthly Variation Coefficient":
        indicator["Yearly Aggregation"] = st.selectbox(label="Yearly Aggregation", options = AGG_FUNC, index=0,disabled=True)
    

    st.subheader("Season shift")
    col1, col2 = st.columns([0.2,0.8])
    with col1:
        # daily_threshold_min_box= st.checkbox(label="Daily Threshold Min")
        if st.checkbox(label="Season Start Shift (in months)"):
            with col2:
                indicator ["Season Start Shift"]= st.number_input(label="Season Start Shift",value=None, label_visibility="collapsed")
            # daily_threshold_max_box= st.checkbox(label="Daily Threshold Max")
    col1, col2 = st.columns([0.2,0.8])
    with col1:
        if st.checkbox(label="Season End Shift (in months)"):
            with col2:
                indicator["Season End Shift"] = st.number_input(label="Season End Shift",value=None, label_visibility="collapsed")

    st.session_state.indicator = indicator
    st.button("Add indicator", on_click=add_indicator_to_df)

df_indicators = pd.DataFrame(st.session_state.df_indicators)

if not df_indicators.empty:
    st.write(df_indicators)


# if st.session_state.indicators:
#     # Convert indicators to DataFrame
#     indicators_df = pd.DataFrame(st.session_state.indicators)

#     # Display the DataFrame with an editable option
#     edited_df = st.data_editor(indicators_df, use_container_width=True, hide_index=True)

#     # Identify if any row was edited
#     if not indicators_df.equals(edited_df):
#         st.session_state.indicators = edited_df.to_dict(orient='records')
#         st.success("Indicator updated successfully!")

#     # Delete an indicator
#     delete_index = st.selectbox("Select Indicator to Delete", indicators_df.index)
#     if st.button("Delete Indicator"):
#         st.session_state.indicators.pop(delete_index)
#         st.success("Indicator deleted successfully!")
# else:
#     st.write("No indicators created yet.")
