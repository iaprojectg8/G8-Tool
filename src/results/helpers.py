from src.utils.imports import *
from src.utils.variables import DATAFRAME_HEIGHT, FILENAME

from src.lib.layout import *

from src.results.general_plots import *
from src.results.indicators_plot import *
from src.results.main_calculation import introduce_season_shift_in_calculation, calculate_scores, preparing_dataframe_for_plot
from src.results.custom_indicators import heat_index_indicator

from src.parametrization.helpers import indicator_editing
# ---------------------------------------
# --- Function for General management ---
# ---------------------------------------
 
def variable_choice(df:pd.DataFrame):
    """
    Provides a user interface for selecting climate variables using checkboxes.

    Returns:
        variables_choice (list): A list of selected variables chosen by the user.
    """
    available_variables = select_variables_in_columns(df)
    st.write("Choose the climate variable you are interested in: ")
    variables_choice = []
    col1, col2 = st.columns(2)

    # Looping on the available variable to make two checkbox columns and appending variables in the list
    for index, variable in enumerate(available_variables):
        if index%2 == 0:
            with col1:
                if st.checkbox(label=variable):
                    variables_choice.append(variable)
        else:
            with col2:
                if st.checkbox(label=variable):
                    variables_choice.append(variable)

    return variables_choice

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

def select_period_results(key):
    """
    Allows the user to select a data period using an interactive Streamlit slider.

    Returns:
        tuple: The start and end values of the selected period.
    """
    # Define the initial limits for the slider
    period_start, period_end = st.session_state.long_period

    # Display the slider that allows the user to select the bounds
    period_start, period_end = st.slider(
        "Select the data period:",
        min_value=period_start, 
        max_value=period_end,
        value=(period_start, period_end),
        key=f"select_period_{key}")      
    return period_start, period_end

def split_into_periods(period_length, start_year, end_year):
    """
    Splits a given time range into multiple periods of a specified length.

    Args:
        period_length (int): The length of each period in years.
        start_year (int): The starting year of the entire time range.
        end_year (int): The ending year of the entire time range.

    Returns:
        list of tuples: A list of tuples where each tuple represents a period
                        with the format (period_start, period_end).
    """
    whole_period_length = end_year - start_year + 1
    amount_of_periods = math.ceil(whole_period_length / period_length)
    periods = []

    # Loop through each period index and calculate start and end years
    for period_index in range(amount_of_periods):
        period_start = start_year + period_index * period_length  # Start year of the current period
        period_end = period_start + period_length  # End year of the current period

        # Append the period to the list, ensuring it does not exceed the end year
        if period_end <= end_year:
            periods.append((period_start, period_end))
        else:
            periods.append((period_start, end_year))

    return periods

def filtered_data(data:pd.DataFrame, chosen_variables, period):
    """
    Filters a DataFrame based on selected variables and a specified time period, 
    then displays the resulting DataFrame.

    Args:
        data (pd.DataFrame): The input DataFrame with a datetime index.
        chosen_variables (list of str): The list of variables to filter the columns.
        period (tuple of int): The start and end years for filtering the DataFrame.

    Returns:
        pd.DataFrame: The filtered DataFrame containing only the relevant columns and rows within the specified period.
    """

    # Filter by the period
    data_in_right_period = data[(data.index.year>=period[0]) & (data.index.year<=period[-1])]
    
    # Change the format of the proposition made to the user to correspond to the dataframe column name
    chosen_variables_modified = ["_".join(variable.lower().split()) for variable in chosen_variables]

    # Check whether the columns chould be taken or removed from the dataframe
    columns_to_keep = [column for column in data.columns if any(variable in column for variable in chosen_variables_modified)]
    
    # Keep the relevant columns
    data_to_keep = data_in_right_period[columns_to_keep]
    
    data_to_diplay = copy(data_to_keep)
    data_to_diplay.index = data_to_diplay.index.date

    # Display the dataframe
    st.dataframe(data=data_to_diplay,height=DATAFRAME_HEIGHT, use_container_width=True)
    return data_to_keep


def general_plot(data: pd.DataFrame, periods):
    """
    Generates a plot for the selected variable and period, including monthly and yearly means,
    trends, and the option to download the plots as a PDF.

    Args:
        data (pd.DataFrame): The input data frame containing the data to plot.
        periods (list): List of tuples representing the periods to analyze (start year, end year).
        chosen_variable (list): List of available variable options for the user to choose from.

    Returns:
        None: The function generates plots and provides a download button for the PDF.
    """
    # Define columns to keep from the original dataframe
    columns_to_keep = data.columns
    chosen_variables = [" ".join(column.split("_")).title() for column in columns_to_keep 
                        if column not in ["lat", "lon", "Unnamed: 0", "year"]]
    

    # Calculate monthly and yearly mean data
    monthly_data, monthly_mean = calculate_mothly_mean_through_year(copy(data), periods)
    yearly_mean = calculate_yearly_mean_through_year(data, periods)
    
    
    # Create a select box for users to choose the variable they want to plot
    variable_choice = st.selectbox("Choose the variable on which you want to see the plot", options=chosen_variables)
    
    # Loop through columns to find and plot data matching the selected variable
    for column in data.columns:
        if "_".join(variable_choice.lower().split(" ")) in column:
            
            # Generate the monthly and yearly plots for the selected column
            fig1 = plot_monthly_mean(column, monthly_mean, monthly_data)
            fig2 = plot_yearly_curve_and_period_trends(yearly_mean,monthly_mean, column, periods)
            fig3 = plot_monthly_period_variation(monthly_mean,monthly_data, column)

            
            # Generate the PDF with the two figures
            pdf = wrap_into_pdf(fig1, fig2, fig3)

            # Provide a button to download the generated PDF
            st.download_button(
                label="Download PDF",
                data=pdf,
                file_name=f"{st.session_state.project_info["project_name"]}_{column.title()}_General_Graph.pdf",
                mime="application/pdf"
            )


# ------------------------------------------
# --- Function for Indicators management ---
# ------------------------------------------

def split_into_periods_indicators(period_length, start_year, end_year):
    """
    Splits a given time range into multiple periods of a specified length.

    Args:
        period_length (int): The length of each period in years.
        start_year (int): The starting year of the entire time range.
        end_year (int): The ending year of the entire time range.

    Returns:
        list of tuples: A list of tuples where each tuple represents a period
                        with the format (period_start, period_end).
    """
    whole_period_length = end_year - start_year + 1
    amount_of_periods = math.ceil(whole_period_length / period_length)
    periods = []

    # Loop through each period index and calculate start and end years
    for period_index in range(amount_of_periods):
        period_start = start_year + period_index * period_length   # Start year of the current period
        period_end = period_start + period_length -1  # End year of the current period

        # Append the period to the list, ensuring it does not exceed the end year
        if period_end < end_year:
            periods.append((period_start, period_end))
        elif abs(period_start - end_year)<0.3*period_length:
            # Needs to create last tuple periods before to remove the last element of the list
            last_period = (periods[-1][0], end_year)
            periods.pop()
            periods.append(last_period)
        else:
            periods.append((period_start, end_year))

    return periods

def calculations_and_plots(df_season, df_indicators_parameters: pd.DataFrame,df_checkbox:pd.DataFrame, all_year_data, season_start, season_end,periods):
    """
    Perform calculations and generate plots for each indicator in the given indicator parameters DataFrame.

    Args:
        df_season (pandas.DataFrame): Seasonal data containing variables for calculation.
        df_indicators_parameters (pandas.DataFrame): DataFrame containing the parameters for each indicator.
        all_year_data (pandas.DataFrame): Data containing all yearly data to be used for shifting and calculation.
        season_start (int): The starting month for the season.
        season_end (int): The ending month for the season.
        periods (list): List of periods for categorization.

    Returns:
        pandas.DataFrame: A DataFrame containing the yearly data after processing all indicators.
    """
    # Store all newly created columns in a dictionary to merge later

    df_yearly = pd.DataFrame()
    tabs = st.tabs(list(df_indicators_parameters["Name"].values))


    # Iterating over indicators dataframe
    for (i, row), (j, row_checkbox) in zip(df_indicators_parameters.iterrows(), df_checkbox.iterrows()):
        with tabs[i]:
            
            # Offer the possibility to edit the indicator

            indicator_editing(df_season, season_start, season_end, row, row_checkbox, i)
            
            # Initializing useful variables
            variable = row["Variable"]
            score_name = row["Name"]
            season_start_shift=row["Season Start Shift"]
            season_end_shift= row["Season End Shift"]
            below_thresholds=copy(row["Yearly Threshold Min List"])
            above_thresholds= copy(row["Yearly Threshold Max List"])
    
            
            
            # Season shift handling
            if season_start is not None or season_end is not None:
                if (not pd.isna(season_start_shift) or not pd.isna(season_end_shift)
                    or season_start_shift is not None or season_end_shift is not None):

                    df_season = introduce_season_shift_in_calculation(season_start, season_start_shift, season_end, season_end_shift, all_year_data)

            if type(variable) is list:
                df_season_temp=df_season[variable]
            else:
                df_season_temp=df_season[[variable]]

            # Crossed Variable indicators have their own graph so don't need to go further there
            if row["Indicator Type"] == "Crossed Variables":
                heat_index_indicator(df_season_temp, all_year_data, key=i, periods=periods)
            else:
                unit, df_yearly_var, aggregated_column_name = calculate_scores(row,df_season_temp, score_name, variable, spatial=0)
                # Plot preparation
                df_yearly_var = preparing_dataframe_for_plot(df_yearly_var, periods, score_name)
                with st.expander("Show Yearly Dataframe"):
                    st.dataframe(df_yearly_var, height=DATAFRAME_HEIGHT, use_container_width=True)
                

                
                # Multiple plot to understand the calculated indicators
                fig1 = plot_daily_data(all_year_data, variable, key=i)
                fig2 = plot_years_exposure(df_yearly_var, aggregated_column_name, below_thresholds, above_thresholds, score_name,unit)
                fig3 = plot_deficit_and_excess_exposure(df_yearly_var, score_name)
                fig4 = plot_global_exposure(df_yearly_var, score_name, i, aggregated_column_name, below_thresholds, above_thresholds)
                fig_list = [fig1, fig2, fig3, fig4]
                pdf = wrap_indicator_into_pdf(fig_list)
                st.download_button(
                    label="Download PDF",
                    data=pdf,
                    file_name=f"{score_name}.pdf",
                    mime="application/pdf",
                    key=f"download_{i}"
                )
    return df_yearly




    