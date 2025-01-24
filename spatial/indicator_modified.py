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
from indicators.main_calculation import calculations_and_plots, spatial_calculation, filter_all_the_dataframe
from spatial.rasterization import read_shape_zipped_shape_file


# # This is only because we use this session variable in a default value of a widget
# All the other session
if "columns_chosen" not in st.session_state:
    st.session_state.columns_chosen = None
if "season_checkbox" not in st.session_state:
    st.session_state.season_checkbox = False



def spatial_indicator_management(df_indicator_sample:pd.DataFrame, all_df_dict):
    """
    Manages spatial indicators based on user-selected periods, variables, seasons, and parameters.

    Args:
        df_ind (pd.DataFrame): The initial dataframe containing spatial indicators.
        all_df_dict (dict): Dictionary of all dataframes to process.
    """

    key = "spatial_indicator_part"
    set_title_2("Period")

    # User setting the periods of interest
    long_period = (long_period_start, long_period_end) = select_period(key=key)
    smaller_period_length  = st.select_slider("Choose the length of smaller period to see the evolution of your data on them:",
                                              options=PERIOD_LENGTH, 
                                              key=f"smaller_period{key}")
    periods = split_into_periods_indicators(smaller_period_length, long_period_start, long_period_end)

    # Loading data and applying first filters
    df_indicator_sample = period_filter(df_indicator_sample, period=long_period)
    st.dataframe(df_indicator_sample, height=DATAFRAME_HEIGHT, use_container_width=True)
    
    # Propose variables related to the dataset loaded 
    set_title_2("Variable Choice")
    df_indicator_sample = column_choice(df_indicator_sample)

    # Variables intitialization
    season_start, season_end = None, None

    if not df_indicator_sample.empty:
        st.dataframe(df_indicator_sample, height=DATAFRAME_HEIGHT, use_container_width=True) 

        # Season handdling
        set_title_2("Season Choice")
        if st.checkbox("Need a season or a period study", value=st.session_state.season_checkbox):
            season_start, season_end = select_season()
            df_indicator_sample_season = select_data_contained_in_season(df_indicator_sample, season_start, season_end)
            st.dataframe(df_indicator_sample_season, height=DATAFRAME_HEIGHT, use_container_width=True)
        else:
            df_indicator_sample_season = df_indicator_sample
        
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
            indicator_building(df_indicator_sample_season, season_start, season_end)


        # Display an indicator summary
        if not st.session_state.df_indicators.empty:
            # The copy done is only to display the indicators dataframe on the app
            df_indicator_copy = copy(st.session_state.df_indicators)
            df_indicator_copy["Variable"] = df_indicator_copy["Variable"].astype(str)
            st.dataframe(df_indicator_copy, use_container_width=True)
            download_indicators(st.session_state.df_indicators)

            # Need to calculate score with this parameters
            set_title_2("Indicators Calculation & Rasters Building")
            shape_gdf  = read_shape_zipped_shape_file()
            raster_resolution = st.number_input("Choose the raster resolution",
                                                                min_value=0.001, max_value=1., 
                                                                value=0.005,
                                                                format="%0.3f")
            if st.button("Filter the data"):
                with st.spinner("Filter all the dataframes"):
                    dataframes_dict = filter_all_the_dataframe(dataframes=copy(all_df_dict), long_period=long_period)
                    st.session_state.dataframes = dataframes_dict
            spatial_calculation(df_indicator_sample_season, st.session_state.df_indicators, 
                                st.session_state.df_checkbox,st.session_state.dataframes, 
                                all_df_dict, season_start, season_end, periods, shape_gdf, raster_resolution)

    