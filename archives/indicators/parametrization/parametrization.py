from utils.imports import *
from lib.session_variables import * 
from utils.variables import *
from lib.layout import *
from indicators.parametrization.create_inidicator import *
from indicators.parametrization.update_indicator import *


def select_variables_in_columns(df:pd.DataFrame):
    """
    Select variables availables in the columns of the dataframe
    """
    columns = df.columns
    available_variables = []
    all_available_variables = ["_".join(variable.lower().split()) for variable in AVAILABLE_VARIABLES]
    for column in columns:
        for variable in all_available_variables:
            if variable in column and variable not in available_variables:
                available_variables.append(variable) 

    available_variables = [" ".join(variable.split("_")).title() for variable in available_variables] 
    return available_variables


# ----------------------------
# --- Season selection part---
# ----------------------------

def select_season():
    """
    Allows the user to select a date range using a slider for months.

    Returns:
        tuple: A tuple containing the start and end month selected by the user.
    """
    # Building the avaailable option
    start=1
    end=12
    options =  np.arange(start, end+1)

    # Widget slider to chose the starting and ending month for each years
    start_date, end_date = st.select_slider(
        "Select a date range:",
        options = options,
        value=(st.session_state.season_start, st.session_state.season_end),
        format_func=lambda x:MONTHS_LIST[x-1]  # Displays full month name, day, and year
    )
    # Display the selected range
    selected_months = list(options[start_date-1:end_date])
    st.write(f"The period chosen goes from {MONTHS_LIST[selected_months[0]-1]} to {MONTHS_LIST[selected_months[-1]-1]}")

    return start_date, end_date

def select_data_contained_in_season(data, season_start, season_end):
    """
    Filters the input data to select rows where the month is within the specified season range.

    Args:
        data (DataFrame): A pandas DataFrame with a DateTime index.
        season_start (int): The starting month of the season (1 for January, 12 for December).
        season_end (int): The ending month of the season (1 for January, 12 for December).

    Returns:
        DataFrame: A filtered DataFrame containing only the data for the selected season (month range).
    """
    return data[(data.index.month >= season_start) & (data.index.month <= season_end)].copy()


# ---------------------------------
# --- Indicator management part ---
# ---------------------------------


def indicator_building(df_chosen:pd.DataFrame, season_start, season_end):
    """
    Handles the creation of indicators based on user input.

    Args:
        df_chosen (DataFrame): The selected data for which indicators will be created.
        season_start (int): Starting month of the season.
        season_end (int): Ending month of the season.
    """
    # st.subheader("Create indicators")
    # with st.expander("Indicator template",expanded=False):
        
    indicator_type = general_information(df_chosen)


    if indicator_type in ["Outlier Days", "Consecutive Outlier Days"]:
        create_daily_threshold_input()
        create_yearly_thresholds_input()
    elif indicator_type == "Sliding Windows Aggregation":
        create_rolling_window_input()
        create_yearly_thresholds_input()
    elif indicator_type == "Season Aggregation":
        create_yearly_thresholds_input()

    # Crossed variable indicator or not
    if indicator_type == "Crossed Variables":
        create_built_indicator()
    else: 
        create_yearly_aggregation()
    if season_start is not None and season_end is not None:
        create_season_shift_input(season_start, season_end)

    # Buttons
    create_buttons()
