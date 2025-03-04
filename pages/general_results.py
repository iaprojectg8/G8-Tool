from src.utils.imports import * 
from src.utils.variables import TRANSPARENT_TOOL_LOGO, G8_LOGO

from src.lib.layout import page_config_and_menu, set_page_title, set_title_1
from src.lib.session_variables import initialize_session_state_variable

from src.results.result_functions import make_zone_average, general_management, indicator_management
from src.request.widgets import get_project_information

def main():
    """Basic Streamlit app with a title."""
    # Set some layout parameters for the page 
    initialize_session_state_variable(mode="Expert")
    page_name = "Expert General Results"
    page_config_and_menu(TRANSPARENT_TOOL_LOGO, G8_LOGO, page_name)
    set_page_title("General Results")
    set_title_1("General Project Information")
    get_project_information()


    if len(st.session_state.dataframes_modified) == 0:
        st.error("You should upload a file on the Indicator Parametrization page")
        
    else:
        
        make_zone_average(dataframes=st.session_state.dataframes_modified)
        if st.session_state.all_df_mean is not None :
            df_overall_averaged = st.session_state.all_df_mean
            
            # Tab init
            tab_general, tab_indicator = st.tabs(["General", "Indicators"])
            with tab_general:
                general_management(df_overall_averaged, st.session_state.ssp)
            with tab_indicator:
                indicator_management(df_overall_averaged)

if __name__ == "__main__":
    main()