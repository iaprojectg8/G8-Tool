from utils.imports import *
from utils.variables import DATAFRAME_HEIGHT
from lib.data_process import loads_data, column_choice
from indicators.parametrization.parametrization import * 
from layouts.layout import *
from lib.widget import * 
from indicators.calculation import *
from lib.session_variables import *
from lib.data_process import *
from lib.plot import *
from indicators.plot import *
from indicators.main_calculation import calculations_and_plots, spatial_calculation


# # This is only because we use this session variable in a default value of a widget
# All the other session
if "columns_chosen" not in st.session_state:
    st.session_state.columns_chosen = None
if "season_checkbox" not in st.session_state:
    st.session_state.season_checkbox = False

def indicator_management(df):
    """Basic Streamlit app with a title."""
    # Set some layout parameters for the page 
    # st.set_page_config(layout="wide")
    # set_page_title("Indicators Customization")
    key = "indicator_part"
    set_title_2("Period")

    # User setting the periods of interest
    long_period = (long_period_start, long_period_end) = select_period(key=key)
    smaller_period_length  = st.select_slider("Choose the length of smaller period to see the evolution of your data on them:",
                                              options=PERIOD_LENGTH, 
                                              key=f"smaller_period{key}")
    periods = split_into_periods_indicators(smaller_period_length, long_period_start, long_period_end)

    # Loading data and applying first filters
    path = f"CSV_files/{FILENAME}"
    all_data = df
    data_long_period_filtered = period_filter(all_data, period=long_period)
    st.dataframe(data_long_period_filtered, height=DATAFRAME_HEIGHT, use_container_width=True)
    
    # Propose variables related to the dataset loaded 
    set_title_2("Variable Choice")
    df_chosen = column_choice(data_long_period_filtered)

    # Variables intitialization
    season_start, season_end = None, None
    all_year_data = pd.DataFrame()

    if not df_chosen.empty:
        st.dataframe(df_chosen, height=DATAFRAME_HEIGHT, use_container_width=True)
        all_year_data = df_chosen  

        # Season handdling
        set_title_2("Season Choice")
        if st.checkbox("Need a season or a period study", value=st.session_state.season_checkbox):
            season_start, season_end = select_season()
            df_season = select_data_contained_in_season(df_chosen, season_start, season_end)
            st.dataframe(df_season, height=DATAFRAME_HEIGHT, use_container_width=True)
        else:
            df_season = df_chosen
        
        # Indicators parametrization handling
        set_title_2("Parametrize Indicators")

        # Load indicators from CSV
        if st.checkbox(label="Load indicators from CSV"):
            df_uploaded = upload_csv_file()
            
            if df_uploaded is not None and not df_uploaded.equals(st.session_state.uploaded_df):
                df_checkbox = fill_df_checkbox(df_uploaded)
                st.session_state.uploaded_df = df_uploaded
                st.session_state.df_indicators = copy(df_uploaded)
                st.session_state.df_checkbox = df_checkbox

        # Building the indicator in a popover
        with st.popover("Create Indicator", use_container_width = True):
            indicator_building(df_season, season_start, season_end)

        # Display an indicator summary
        if not st.session_state.df_indicators.empty:
            # The copy done is only to display the indicators dataframe on the app
            df_indicator_copy = copy(st.session_state.df_indicators)
            df_indicator_copy["Variable"] = df_indicator_copy["Variable"].astype(str)
            st.dataframe(df_indicator_copy, use_container_width=True)
            download_indicators(st.session_state.df_indicators)


            # Need to calculate score with this parameters
            set_title_2("Indicators calculation")
            calculations_and_plots(df_season, st.session_state.df_indicators, st.session_state.df_checkbox,all_year_data, season_start, season_end, periods)

def spatial_indicator_management(df_ind:pd.DataFrame, all_df_dict):
    """Basic Streamlit app with a title."""
    # Set some layout parameters for the page 
    # st.set_page_config(layout="wide")
    # set_page_title("Indicators Customization")


    key = "spatial_indicator_part"
    set_title_2("Period")

    # User setting the periods of interest
    long_period = (long_period_start, long_period_end) = select_period(key=key)
    smaller_period_length  = st.select_slider("Choose the length of smaller period to see the evolution of your data on them:",
                                              options=PERIOD_LENGTH, 
                                              key=f"smaller_period{key}")
    periods = split_into_periods_indicators(smaller_period_length, long_period_start, long_period_end)

    # Loading data and applying first filters
    df_ind = period_filter(df_ind, period=long_period)
    st.dataframe(df_ind, height=DATAFRAME_HEIGHT, use_container_width=True)
    
    # Propose variables related to the dataset loaded 
    set_title_2("Variable Choice")
    df_ind = column_choice(df_ind)

    # Variables intitialization
    season_start, season_end = None, None

    if not df_ind.empty:
        st.dataframe(df_ind, height=DATAFRAME_HEIGHT, use_container_width=True) 

        # Season handdling
        set_title_2("Season Choice")
        if st.checkbox("Need a season or a period study", value=st.session_state.season_checkbox):
            season_start, season_end = select_season()
            df_ind_final = select_data_contained_in_season(df_ind, season_start, season_end)
            st.dataframe(df_ind_final, height=DATAFRAME_HEIGHT, use_container_width=True)
        else:
            df_ind_final = df_ind
        
        # Indicators parametrization handling
        set_title_2("Parametrize Indicators")

        # Load indicators from CSV
        if st.checkbox(label="Load indicators from CSV"):
            df_uploaded = upload_csv_file()
            
            if df_uploaded is not None and not df_uploaded.equals(st.session_state.uploaded_df):
                df_checkbox = fill_df_checkbox(df_uploaded)
                st.session_state.uploaded_df = df_uploaded
                st.session_state.df_indicators = copy(df_uploaded)
                st.session_state.df_checkbox = df_checkbox

        # Building the indicator in a popover
        
        with st.popover("Create Indicator", use_container_width = True):
            indicator_building(df_ind_final, season_start, season_end)


        # Display an indicator summary
        if not st.session_state.df_indicators.empty:
            # The copy done is only to display the indicators dataframe on the app
            df_indicator_copy = copy(st.session_state.df_indicators)
            df_indicator_copy["Variable"] = df_indicator_copy["Variable"].astype(str)
            st.dataframe(df_indicator_copy, use_container_width=True)
            download_indicators(st.session_state.df_indicators)

            # Need to calculate score with this parameters
            set_title_2("Indicators calculation")
            if st.button("Filter the data"):
                with st.spinner("Filter all the dataframes"):
                    dataframes_dict = filter_all_the_dataframe(dataframes=copy(all_df_dict), long_period=long_period)
                    st.session_state.dataframes = dataframes_dict
            spatial_calculation(df_ind_final, st.session_state.df_indicators, st.session_state.df_checkbox,st.session_state.dataframes, all_df_dict, season_start, season_end, periods)

        
def filter_all_the_dataframe(dataframes:dict, long_period):
    for key_df, df in dataframes.items():
        # do the filters that have been done on the first dataframe of the dictionary
        data_long_period_filtered = period_filter(df, period=long_period)
        dataframes[key_df] = data_long_period_filtered
    st.write("The filtering is done")
    print(dataframes)
    return dataframes

    # for (df_key, df), (df_all_key, df_all) in zip(dataframes_dict.items(), all_dataframes_dict.items()):
    #     if isinstance(variable, list):  # Check if variable is a list
    #         selected_columns = variable + ["lat", "lon"]  # Create a new list
    #     else:
    #         selected_columns = [variable, "lat", "lon"]  # Combine into a list
        
    #     df = df_all.loc[:, selected_columns]  # Use the new variable for column selection
    #     dataframes_dict[df_key] = df