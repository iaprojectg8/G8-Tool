from src.utils.imports import *
from src.utils.variables import DATAFRAME_HEIGHT, PERIOD_LENGTH, TRANSPARENT_TOOL_LOGO, G8_LOGO
from src.lib.layout import *
from src.lib.session_variables import *
from src.parametrization.helpers import select_season, select_data_contained_in_season, download_indicators, period_filter
from src.results.helpers import select_period_results, split_into_periods_indicators
from src.spatial.rasterization import read_shape_zipped_shape_file
from src.spatial.spatial_indicator import spatial_calculation, filter_all_the_dataframe
from src.lib.layout import page_config_and_menu, set_page_title, set_title_1, set_title_2


def main():
    """Basic Streamlit app with a title."""
    # Set some layout parameters for the page 
    page_name = "Specific Results"
    page_config_and_menu(TRANSPARENT_TOOL_LOGO, G8_LOGO, page_name)
    set_page_title("Specific Results")

    if len(st.session_state.dataframes_modified) == 0:
        st.error("You should upload a file on the Indicator Parametrization page")
    else:
        df_indicator_sample = copy(st.session_state.dataframes_modified[list(st.session_state.dataframes_modified.keys())[0]])
        key = "spatial_indicator_part"
        set_title_2("Period")

        # User setting the periods of interest
        long_period = (long_period_start, long_period_end) = select_period_results(key=key)
        smaller_period_length  = st.select_slider("Choose the length of smaller period to see the evolution of your data on them:",
                                                options=PERIOD_LENGTH, 
                                                key=f"smaller_period{key}")
        periods = split_into_periods_indicators(smaller_period_length, long_period_start, long_period_end)

        # Loading data and applying first filters
        df_indicator_sample = period_filter(df_indicator_sample, period=long_period)
        st.dataframe(df_indicator_sample, height=DATAFRAME_HEIGHT, use_container_width=True)
        
        # Variables intitialization
        season_start, season_end = None, None

        if not df_indicator_sample.empty:

            # Season handdling
            set_title_2("Season Choice")
            if st.checkbox("Need a season or a period study", value=st.session_state.season_checkbox):
                season_start, season_end = select_season()
                df_indicator_sample_season = select_data_contained_in_season(df_indicator_sample, season_start, season_end)
                st.dataframe(df_indicator_sample_season, height=DATAFRAME_HEIGHT, use_container_width=True)
            else:
                df_indicator_sample_season = df_indicator_sample
            

            # Display an indicator summary
            if not st.session_state.df_indicators.empty:
                # The copy done is only to display the indicators dataframe on the app
                df_indicator_copy = copy(st.session_state.df_indicators)
                df_indicator_copy["Variable"] = df_indicator_copy["Variable"].astype(str)
                st.dataframe(df_indicator_copy, use_container_width=True)
                download_indicators(st.session_state.df_indicators, filename="indicators.xlsx")

                # Need to calculate score with this parameters
                set_title_2("Indicators Calculation & Rasters Building")
                shape_gdf  = read_shape_zipped_shape_file()
                raster_resolution = st.number_input("Choose the raster resolution",
                                                                    min_value=0.001, max_value=1., 
                                                                    value=0.25,
                                                                    format="%0.3f")
            
                
                dataframes_dict = filter_all_the_dataframe(dataframes=copy(st.session_state.dataframes_modified), long_period=long_period)
                        
                spatial_calculation(df_indicator_sample_season, st.session_state.df_indicators, 
                                    st.session_state.df_checkbox,copy(dataframes_dict), 
                                    season_start, season_end, periods, shape_gdf, raster_resolution)
            else: 
                st.warning("To obtain spatial indicator results, you must first create them on the Indicator Parametrization page.")
if __name__ == "__main__":
    main()
