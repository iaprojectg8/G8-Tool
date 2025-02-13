from utils.imports import * 
from utils.variables import ZIP_FOLDER, REQUEST_TYPE, TOOL_LOGO, G8_LOGO
from layouts.layout import *
from lib.session_variables import *
from requests_api.helpers import *
from requests_api.open_meteo_request import open_meteo_request
from requests_api.cmip6_requests import cmip6_request
from parametrization.widgets_parametrization import page_config, increase_logo
from lib.menu import menu




def main():
    """Basic Streamlit app with a title."""
    # Set some layout parameters for the page 
    
    page_config(TOOL_LOGO)
    st.logo(G8_LOGO, size="large", link="https://groupehuit.com/")
    increase_logo()
    set_page_title("Request")
    menu()
    # Project info
    set_title_1("Project Location")
    get_project_location()

    # Display existing files in the ZIP_FOLDER with checkboxes
    set_title_1("Requests")
    set_title_2("Area of interest")
    ensure_zip_folder_exist(ZIP_FOLDER)
    
    # Shapefile uploader
    selected_shape_folder = shapefile_uploader(ZIP_FOLDER)
    
    if selected_shape_folder != []:

        cmip6_request(selected_shape_folder)

        

        
        
        


if "__main__":
    main()