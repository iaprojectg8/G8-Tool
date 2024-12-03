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
        col1, col2 = st.columns([1, 1])  # Adjust the column width ratios
        with col1:
            if st.checkbox(label):
                with col2:
                    yearly_threshold[label] = st.number_input(label="1", value=default_value, label_visibility="collapsed")  # Empty label for cleaner layout

    # Afficher les valeurs pour vérification
    if yearly_threshold:
        st.write("### Summary of the Selected Thresholds")
        df = pd.DataFrame(yearly_threshold.items(), columns=["Threshold", "Value"]).reset_index(drop=True)
        st.dataframe(yearly_threshold, column_config=[""])



# Indicateurs
# Les basiques
#     compte le nombre de jour
#     compte le nombre de jour consécutifs
# Pour les variables à cumul
#     Faire la sum de toute la growing season et voir si c'est entre des seuil
# A voir pour mettre un shift (growing season)
# + indicateur de variabilité