from src.utils.imports import *
from src.utils.variables import *

from src.lib.layout import *

from results.helpers import *

from parametrization.helpers import select_season, select_data_contained_in_season, download_indicators, period_filter


def make_zone_average(dataframes:dict):
    """
    Calculate average values across all geographical points for each timestamp.
    
    Args:
        dataframes (dict): Dictionary containing DataFrames for each lat/lon point
    """

    # Step 2: Combine all datasets
    combined_df = pd.concat(dataframes.values(), ignore_index=False)
    mean_df = combined_df.groupby(combined_df.index).mean()
    st.session_state.all_df_mean = mean_df
    return mean_df


def general_management_beginner(df):
    """
    Function to manage the general results got with the data selected in the Indicator Parametrizer
    Args:
        df (pd.dataframe) : Dataframe that contains the averaged data
    """
    set_title_1("Climate Variables")
    key = "general_part_beginner"

    # Period choice
    long_period = (long_period_start, long_period_end) = select_period_results(key)

    # Period cut
    smaller_period_length  = st.select_slider("Choose the length of smaller period to see the evolution of your data on them:",
                                              options=PERIOD_LENGTH,
                                              key = f"smaller_period{key}",
                                              value=10)

    data_to_keep = period_filter(df, long_period)
    periods = split_into_periods(smaller_period_length, long_period_start, long_period_end)
    general_plot(data_to_keep, periods)

def general_management(df):
    """
    Function to manage the general results got with the data selected in the Indicator Parametrizer
    Args:
        df (pd.dataframe) : Dataframe that contains the averaged data
    """
    set_title_1("Climate Variables")
    key = "general_part"
    # Chosen variable has a certain case that might be broken to easier use
    chosen_variables = variable_choice(df)
    

    # Period choice
    long_period = (long_period_start, long_period_end) = select_period_results(key)

    # Period cut
    smaller_period_length  = st.select_slider("Choose the length of smaller period to see the evolution of your data on them:",
                                              options=PERIOD_LENGTH,
                                              key = f"smaller_period{key}",
                                              value=10)
    periods = split_into_periods(smaller_period_length, long_period_start, long_period_end)

    if chosen_variables : 
        data = df

        st.write("Here is your dataset with the relevant variables following your precedent choices:")
        data_to_keep = filtered_data(data, chosen_variables, long_period)

        
        # Plot part with monthly means and regression through all time
        general_plot(data_to_keep, periods)


def indicator_management(df):
    """
    Function to manage the indicators results got with the data selected in the Indicator Parametrizer
    Args:
        df (pd.dataframe) : Dataframe that contains the averaged data
    """
    key = "indicator_part"
    set_title_2("Period")

    # User setting the periods of interest
    long_period = (long_period_start, long_period_end) = select_period_results(key=key)
    smaller_period_length  = st.select_slider("Choose the length of smaller period to see the evolution of your data on them:",
                                              options=PERIOD_LENGTH, 
                                              key=f"smaller_period{key}")
    periods = split_into_periods_indicators(smaller_period_length, long_period_start, long_period_end)

    # Loading data and applying first filters
    all_data = df
    data_long_period_filtered = period_filter(all_data, period=long_period)
    # st.dataframe(data_long_period_filtered, height=DATAFRAME_HEIGHT, use_container_width=True)

    # Variables intitialization
    season_start, season_end = None, None
    all_year_data = pd.DataFrame()

    if not data_long_period_filtered.empty:
        all_year_data = data_long_period_filtered 

        # Season handdling
        set_title_2("Season Choice")
        if st.checkbox("Need a season or a period study", value=st.session_state.season_checkbox):
            season_start, season_end = select_season()
            df_season = select_data_contained_in_season(data_long_period_filtered, season_start, season_end)
            st.dataframe(df_season, height=DATAFRAME_HEIGHT, use_container_width=True)
        else:
            df_season = data_long_period_filtered
        
        # Display an indicator summary
        if not st.session_state.df_indicators.empty:
            # The copy done is only to display the indicators dataframe on the app
            df_indicator_copy = copy(st.session_state.df_indicators)
            df_indicator_copy["Variable"] = df_indicator_copy["Variable"].astype(str)
            set_title_2("Indicators Summary")
            st.dataframe(df_indicator_copy, use_container_width=True)
            download_indicators(st.session_state.df_indicators, filename="indicators.xlsx")


            # Need to calculate score with this parameters
            set_title_2("Indicators calculation")
            calculations_and_plots(df_season, st.session_state.df_indicators, st.session_state.df_checkbox,all_year_data, season_start, season_end, periods)