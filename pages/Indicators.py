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
from indicators.main_calculation import calculate_score


# # This is only because we use this session variable in a default value of a widget
# All the other session
if "columns_chosen" not in st.session_state:
    st.session_state.columns_chosen = None

def main():
    """Basic Streamlit app with a title."""
    # Set some layout parameters for the page 
    st.set_page_config(layout="wide")
    set_page_title("Indicators Customization")
    set_title_2("Period")

    # User setting the periods of interest
    long_period = (long_period_start, long_period_end) = select_period()
    smaller_period_length  = st.select_slider("Choose the length of smaller period to see the evolution of your data on them:",options=PERIOD_LENGTH)
    periods = split_into_periods_indicators(smaller_period_length, long_period_start, long_period_end)

    # Loading data and applying first filters
    path = f"CSV_files/{FILENAME}"
    all_data = loads_data(filename=path)
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
        else:
            df_season = df_chosen
        st.dataframe(df_season, height=DATAFRAME_HEIGHT, use_container_width=True)

        
        # Indicators parametrization handling
        set_title_2("Parametrize Indictors")
        tab1, tab2 = st.tabs(["Create/Update Indicator", "Edit Existing Indicators"])

        # Building in a tab
        with tab1:
            indicator_building(df_season, season_start, season_end)

        # Editing in the other
        with tab2:
            indicator_editing(df_season, season_start, season_end)

        if not st.session_state.df_indicators.empty:
            st.dataframe(st.session_state.df_indicators, use_container_width=True)


            # Need to calculate score with this parameters
            set_title_2("Indicators calculation")
            calculate_score(df_season, st.session_state.df_indicators,all_year_data, season_start, season_end, periods)


if "__main__":
    main()