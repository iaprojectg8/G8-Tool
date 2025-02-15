from utils.imports import * 
from utils.variables import ZIP_FOLDER, REQUEST_TYPE, TOOL_LOGO, G8_LOGO
from lib.session_variables import *
from requests_api.helpers import *
from requests_api.open_meteo_request import open_meteo_request
from requests_api.cmip6_requests import cmip6_request
from lib.layout import page_config_and_menu, set_page_title, set_title_1, set_title_2




def main():
    """Basic Streamlit app with a title."""
    # Set some layout parameters for the page 
    page_name = "General Information & Requests"
    page_config_and_menu(TOOL_LOGO, G8_LOGO)
    set_page_title("General Information & Requests")


    # Project info
    set_title_1("General information about your project")
    get_project_information()

    # Display existing files in the ZIP_FOLDER with checkboxes
    set_title_1("Requests")
    set_title_2("Area of interest")
    ensure_zip_folder_exist(ZIP_FOLDER)
    managing_existing_folders(ZIP_FOLDER)
    
    # Shapefile uploader
    shapefile_uploader_management()

    if st.session_state.selected_shape_folder != []:
        request_type = st.radio("What do you want to do ?", REQUEST_TYPE )
        if request_type == REQUEST_TYPE[0]:
            cmip6_request(st.session_state.selected_shape_folder)
        else:
            open_meteo_request(st.session_state.selected_shape_folder)

        

        
        
        


if "__main__":
    main()