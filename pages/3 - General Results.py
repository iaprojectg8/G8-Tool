from utils.imports import * 
from utils.variables import DATAFRAME_HEIGHT
from layouts.layout import *
from lib.session_variables import *
from results.result_functions import make_zone_average, general_management, indicator_management


def main():
    """Basic Streamlit app with a title."""
    # Set some layout parameters for the page 
    st.session_state.last_page = "General Results"
    st.set_page_config(layout="wide", page_title="General Results")
    set_page_title("General Results")
    if len(st.session_state.dataframes_modified) == 0:
        st.error("You should upload a file on the Indicator Parametrization page")
        
    else:
        st.dataframe(st.session_state.dataframes_modified[list(st.session_state.dataframes_modified.keys())[0]], height=DATAFRAME_HEIGHT, use_container_width=True)

        set_title_2("Overall average indicator")
        make_zone_average(dataframes=st.session_state.dataframes_modified)
        if st.session_state.all_df_mean is not None :
            df_overall_averaged = st.session_state.all_df_mean
            
            # Tab init
            tab_general, tab_indicator = st.tabs(["General", "Indicators"])
            with tab_general:
                general_management(df_overall_averaged)
            with tab_indicator:
                indicator_management(df_overall_averaged)

if __name__ == "__main__":
    main()