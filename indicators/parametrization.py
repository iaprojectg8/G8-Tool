from utils.imports import *
from lib.session_variables import * 
from utils.variables import *
from layouts.layout import *


def create_empty_dataframe():
    df = pd.DataFrame()
    return df



def create_dynamic_dataframe(df:pd.DataFrame,columns_chosen):
    if df is None or df.empty:
        df = pd.DataFrame(columns=["Name","Type", "Variable", 
                                    "Daily Threshold Min","Daily Threshold Max", "Monthly Agg", 
                                    "Yearly Threshold Min", "Yearly Threshold Max", "Yearly Agg", 
                                    "Cumulated Days Threshold",
                                    'Season Shift Start', 'Season Shift End'
                            ])
        
    column_config={
        'Name': st.column_config.TextColumn(
            max_chars=50,
            default=str(),
        ),
        'Type': st.column_config.TextColumn(
            max_chars=50,
            default=str(),
        ),
        'Variable': st.column_config.SelectboxColumn(
            options=columns_chosen,
            default=columns_chosen[0]),

        'Daily Threshold Min': st.column_config.NumberColumn(),  # Boolean checkbox
        'Daily Threshold Max': st.column_config.NumberColumn(),  # Boolean checkbox

        # Is it really necessary ?
        'Monthly Agg': st.column_config.SelectboxColumn(
            options=AGG_FUNC,
            default=AGG_FUNC[0]),

        'Yearly Threshold Min': st.column_config.NumberColumn(),  # Boolean checkbox
        'Yearly Threshold Max': st.column_config.NumberColumn(),  # Boolean checkbox

        'Yearly Agg': st.column_config.SelectboxColumn(
            options=AGG_FUNC,
            default=AGG_FUNC[0]),

        'Cumulated Days Threshold': st.column_config.NumberColumn(default=None),

        'Season Shift Start': st.column_config.NumberColumn(default=None),
        'Season Shift End': st.column_config.NumberColumn(default=None),
    }
    df_indicator_parameters = st.data_editor(df, use_container_width=True, num_rows="dynamic", column_config=column_config)
    return df_indicator_parameters
    




def variable_choice():
    st.write("Choose the climate variable you are interested in: ")
    variables_choice = []
    col1, col2 = st.columns(2)
    for index, variable in enumerate(AVAILABLE_VARIABLES):
        if index%2 == 0:
            with col1:
                if st.checkbox(label=variable):
                    variables_choice.append(variable)
        else:
            with col2:
                if st.checkbox(label=variable):
                    variables_choice.append(variable)

    return variables_choice

def invert_month_choice(inverted, options, start_date, end_date):
    if inverted.lower() == "yes":
        # Create an inverted range by splitting the months
        selected_months = list(options[end_date-1:]) + list(options[:start_date])
    else:
        # Normal range
        selected_months = list(options[start_date-1:end_date])
    return selected_months

def select_season():
    # Create a list of months with placeholder year 2000 (leap year)

    # The year here is random, it is just to have the format that work on datetime object
    start=1
    end=12
    options =  np.arange(start, end+1)

    start_date, end_date = st.select_slider(
        "Select a date range:",
        options = options,
        value=(6, 10),
        format_func=lambda x:MONTHS_LIST[x-1]  # Displays full month name, day, and year
    )
    selected_months = list(options[start_date-1:end_date])

    # Display the selected range
    st.write(f"The period chosen goes from {MONTHS_LIST[selected_months[0]-1]} to {MONTHS_LIST[selected_months[-1]-1]}")
    return start_date, end_date

def select_data_contained_in_season(data, season_start, season_end):

    return data[(data.index.month >= season_start) & (data.index.month <= season_end)].copy()



def daily_threshold_init():
    """
    Initializes daily thresholds based on user input.
    Users can select thresholds via checkboxes and set values through number inputs.
    
    Returns:
        dict: A dictionary of selected thresholds and their corresponding values.
    """
    daily_threshold = {}

    # Thresholds with their default values
    thresholds = {
        "GDD Base Temp": 10,
        "Daily Extreme Precipitation Threshold": 40,
        "Daily Dry Day Threshold": 1,
        "Daily Heat Stress Threshold": 35,
        "Daily Wind Stress Threshold": 10,
        "Daily Soil Moisture Threshold": 0.2,
        "Daily Humidity Risk": 90,
    }

    # Loop through thresholds and create UI elements
    for label, default_value in thresholds.items():
        col1, col2 = st.columns([1, 1])  # Adjust the column width ratios if needed
        with col1:
            if st.checkbox(label):
                with col2:
                    daily_threshold[label] = st.number_input(label="1", value=default_value,  label_visibility="collapsed")

    # Display the selected thresholds as a summary table
    if daily_threshold:
        st.write("### Thresholds array  summary")
        df = pd.DataFrame(daily_threshold.items(), columns=["Threshold", "Value"]).reset_index(drop=True)
        st.dataframe(df)
    
    return daily_threshold




def yearly_threshold_init():
    yearly_threshold = {}

    # Créer deux colonnes pour les checkboxes et les inputs
    st.write("### Yearly Threshold Configuration")
    for label, default_value in {
        "Yearly Min Temp Suitability Threshold": 24,
        "Yearly Max Temp Suitability Threshold": 30,
        "Yearly Max CV Temp Suitability": 10,
        "Yearly Min GDD Suitability Threshold": 2200,
        "Yearly Min Prec Suitability Threshold": 650,
        "Yearly Max Prec Suitability Threshold": 1500,
        "Yearly Max Extreme Prec Days Threshold": 15,
        "Yearly Max CV Prec Suitability": 150,
        "Yearly Max Soil Moisture Deficit Threshold": 1.5,
        "Yearly Min Solar Radiation Suitability Threshold": 450,
        "Yearly Max Season Start Shift": 10,
        "Yearly Min Season Length": 120,
        "Yearly Humidity Stress Threshold": 30,
        "Yearly Dry Days Stress Threshold": 25,
        "Yearly Heat Days Stress Threshold": 15,
        "Yearly Wind Stress Threshold": 10,
    }.items():
        col1, col2 = st.columns([1, 4])  # Adjust the column width ratios
        with col1:
            if st.checkbox(label):
                with col2:
                    yearly_threshold[label] = st.number_input(label="1", value=default_value, label_visibility="collapsed")  # Empty label for cleaner layout

    # Afficher les valeurs pour vérification
    if yearly_threshold:
        st.write("### Summary of the Selected Thresholds")
        df = pd.DataFrame(yearly_threshold.items(), columns=["Threshold", "Value"]).reset_index(drop=True)
        st.dataframe(yearly_threshold, column_config=[""])






















# Real part start there
# -------------------------
# --- Handle input part ---
# -------------------------


# Template for creating a new indicator
def handle_checkbox_and_input(label : str, checkbox_key):
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
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

def handle_yearly_threshold_input():
    st.subheader("Thresholds")
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

def general_information(df_chosen :pd.DataFrame):
    st.subheader("General Information")
    st.session_state.indicator["Name"] = st.text_input("Indicator Name", value=st.session_state.indicator["Name"])
    st.session_state.indicator["Variable"] = st.selectbox("Variable", options=df_chosen.columns,key="variable")
    indicator_type = st.session_state.indicator["Indicator Type"] = st.selectbox("Indicator Type", options=INDICATOR_TYPES, key="indicator_type")
    return indicator_type

def indicator_building(df_chosen:pd.DataFrame):
    st.subheader("Create indicators")
    with st.expander("Indicator template",expanded=True):
        
        indicator_type = general_information(df_chosen)
        if indicator_type in ["Outlier Days", "Consecutive Outlier Days"]:
            handle_threshold_input()
        elif indicator_type == "Season Sum":
            handle_yearly_threshold_input()

        handle_yearly_aggregation_input()
        handle__season_shift_input()

        # Button 
        handle_buttons()



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
    elif updated_indicator["Indicator Type"] == "Season Sum":
        st.subheader("Thresholds")
        handle_threshold_yearly_update(updated_indicator, updated_checkbox, i)

def handle_threshold_yearly_update(updated_indicator, updated_checkbox, i):
    
    handle_input_update(updated_indicator, updated_checkbox["min_yearly_checkbox"],"Yearly Threshold Min", i)
    handle_input_update(updated_indicator, updated_checkbox["max_yearly_checkbox"],"Yearly Threshold Max", i)

def handle_threshold_daily_update(updated_indicator, updated_checkbox, i):
    handle_input_update(updated_indicator, updated_checkbox["min_daily_checkbox"],"Daily Threshold Min", i)
    handle_input_update(updated_indicator, updated_checkbox["max_daily_checkbox"],"Daily Threshold Max", i)


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

    
    
def indicator_editing(df_chosen : pd.DataFrame):
    if not st.session_state.df_indicators.empty:
        st.subheader("Edit Indicators")
        for (i, row), (j, row_checkbox) in zip(st.session_state.df_indicators.iterrows(), st.session_state.df_checkbox.iterrows()):
            with st.expander(f"Edit Indicator: {row['Name']}"):

                updated_indicator = row.to_dict()
                updated_checkbox = row_checkbox.to_dict()
    
                general_information_update(updated_indicator, i, df_chosen)
                handle_threshold_update(updated_indicator, updated_checkbox, i)
                handle_aggregation_update(updated_indicator, i)
                handle_shift_update(updated_indicator, updated_checkbox, i)
                handle_button_update(updated_indicator, row, i)
                
    else:
        st.write("No indicators available yet.")

def get_frequency_threshold_inputs():
    col1, col2, col3 = st.columns([1,5,1])
    with col2:
        with st.container(border=True):
            set_title_5("Set your frequency threshold as you wish")
            col11, col12, col13 = st.columns(3)
            with col11:
                st.number_input(label="Low_bottom", min_value=0.0, max_value=1.0, value=0.0, disabled=True, label_visibility="collapsed")
            with col12:
                set_frequency_label("Low")
            with col13:
                threshold1 = st.number_input(label="Low_top", min_value=0.0, max_value=1.0, value=0.25, disabled=False, label_visibility="collapsed")

            col11, col12, col13 = st.columns(3)
            with col11:
                st.number_input(label="Moderate_bottom", min_value=0.0, max_value=1.0, value=threshold1, disabled=True, label_visibility="collapsed")
            with col12:
                set_frequency_label("Moderate")
            with col13:
                threshold2 = st.number_input(label="Moderate_top", min_value=0.0, max_value=1.0, value=0.5, disabled=False, label_visibility="collapsed")

            col11, col12, col13 = st.columns(3)
            with col11:
                st.number_input(label="High_bottom", min_value=0.0, max_value=1.0, value=threshold2, disabled=True, label_visibility="collapsed")
            with col12:
                set_frequency_label("High")
            with col13:
                threshold3 = st.number_input(label="High_top", min_value=0.0, max_value=1.0, value=0.75, disabled=False, label_visibility="collapsed")

            col11, col12, col13 = st.columns(3)
            with col11:
                st.number_input(label="Very_High_bottom", min_value=0.0, max_value=1.0, value=threshold3, disabled=True, label_visibility="collapsed")
            with col12:
                set_frequency_label("Very High")
            with col13:
                st.number_input(label="Very_High_top", min_value=0.0, max_value=1.0, value=1.0, disabled=True, label_visibility="collapsed")
    return threshold1, threshold2, threshold3

# Indicateurs
# Les basiques
#     compte le nombre de jour
#     compte le nombre de jour consécutifs
# Pour les variables à cumul
#     Faire la sum de toute la growing season et voir si c'est entre des seuil
# A voir pour mettre un shift (growing season)
# + indicateur de variabilité