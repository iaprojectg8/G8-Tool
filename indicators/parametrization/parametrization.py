from utils.imports import *
from lib.session_variables import * 
from utils.variables import *
from layouts.layout import *
from indicators.parametrization.create_inidicator import *
from indicators.parametrization.update_indicator import *


def variable_choice():
    """
    Provides a user interface for selecting climate variables using checkboxes.

    Returns:
        variables_choice (list): A list of selected variables chosen by the user.
    """
    st.write("Choose the climate variable you are interested in: ")
    variables_choice = []
    col1, col2 = st.columns(2)

    # Looping on the available variable to make two checkbox columns and appending variables in the list
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


# def indicators_editing(df_chosen : pd.DataFrame, season_start, season_end):
#     """
#     Allows users to edit existing indicators.

#     Args:
#         df_chosen (DataFrame): The selected data for which indicators will be edited.
#         season_start (int): Starting month of the season.
#         season_end (int): Ending month of the season.
#     """
#     if not st.session_state.df_indicators.empty:
#         st.subheader("Edit Indicators")

#         # Looping through indicators to change them
#         for (i, row), (j, row_checkbox) in zip(st.session_state.df_indicators.iterrows(), st.session_state.df_checkbox.iterrows()):
#             with st.expander(f"Edit Indicator: {row['Name']}"):

#                 updated_indicator = row.to_dict()
#                 updated_checkbox = row_checkbox.to_dict()

#                 # Updating the different fields
#                 update_general_information(updated_indicator, i, df_chosen)
            
#                 if updated_indicator["Indicator Type"] in ["Outlier Days", "Consecutive Outlier Days"]:
#                     update_daily_threshold_input(updated_indicator, updated_checkbox, i)
#                     update_yearly_thresholds_input(updated_indicator, updated_checkbox, i)
#                 elif updated_indicator["Indicator Type"] == "Sliding Windows Aggregation":
#                     update_rolling_window_input(updated_indicator, i)
#                     update_yearly_thresholds_input(updated_indicator, updated_checkbox, i)
#                 elif updated_indicator["Indicator Type"] == "Season Aggregation":
#                     update_yearly_thresholds_input(updated_indicator, updated_checkbox, i)


#                 update_yearly_aggregation(updated_indicator, i, label="Yearly Aggregation")
#                 if season_start is not None and season_end is not None:
#                     update_season_shift(updated_indicator, updated_checkbox, i, season_start, season_end)

#                 # Buttons
#                 update_buttons(updated_indicator, row, i)
                
#     else:
#         st.write("No indicators available yet.")



# def indicator_editing(df_season, season_start, season_end, row, row_checkbox,i):
    
#     with st.popover(f"Update :  {row["Name"]}", use_container_width = True):
#         updated_indicator = row.to_dict()
#         updated_checkbox = row_checkbox.to_dict()

#         # Updating the different fields
#         update_general_information(updated_indicator, i, df_season)

#         if updated_indicator["Indicator Type"] in ["Outlier Days", "Consecutive Outlier Days"]:
#             update_daily_threshold_input(updated_indicator, updated_checkbox, i)
#             update_yearly_thresholds_input(updated_indicator, updated_checkbox, i)
#         elif updated_indicator["Indicator Type"] == "Sliding Windows Aggregation":
#             update_rolling_window_input(updated_indicator, i)
#             update_yearly_thresholds_input(updated_indicator, updated_checkbox, i)
#         elif updated_indicator["Indicator Type"] == "Season Aggregation":
#             update_yearly_thresholds_input(updated_indicator, updated_checkbox, i)


#         update_yearly_aggregation(updated_indicator, i, label="Yearly Aggregation")
#         if season_start is not None and season_end is not None:
#             update_season_shift(updated_indicator, updated_checkbox, i, season_start, season_end)

#         # Buttons
#         update_buttons(updated_indicator, i)
