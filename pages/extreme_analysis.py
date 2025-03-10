from src.utils.imports import * 
from src.utils.variables import ZIP_FOLDER, TRANSPARENT_TOOL_LOGO, G8_LOGO, DATAFRAME_HEIGHT, REQUEST_TYPE

from src.lib.layout import page_config_and_menu, set_page_title, set_title_1, set_title_2

from src.request.widgets import get_project_location, shapefile_uploader, display_coordinates
from src.request.cmip6_requests import process_shapefile, make_empty_request_for_each_gdf, make_whole_request
from src.request.map_related import map_empty_request
from src.request.open_meteo_request import open_meteo_request

def main():
    """Basic Streamlit app with a title."""
    # Set some layout parameters for the page 
    page_name = "Expert Request"
    page_config_and_menu(TRANSPARENT_TOOL_LOGO, G8_LOGO, page_name)
    set_page_title("Extreme Analysis")
    


    set_title_1("GEV Analysis")
    if len(st.session_state.dataframes_modified) == 0:
        st.error("You should upload a file on the Indicator Parametrization page")


if "__main__":
    main()