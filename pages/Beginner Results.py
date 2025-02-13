from utils.imports import * 
from utils.variables import ZIP_FOLDER, REQUEST_TYPE, TOOL_LOGO, G8_LOGO, CSV_ZIPPED, CSV_EXTRACT
from layouts.layout import *
from lib.session_variables import *
from requests_api.helpers import *
from requests_api.open_meteo_request import open_meteo_request
from requests_api.cmip6_requests import cmip6_request
from parametrization.widgets_parametrization import page_config, increase_logo
from parametrization.helpers import process_dataframes_zip_beginner
from results.result_functions import make_zone_average, general_management_beginner
from lib.menu import menu




def main():
    """Basic Streamlit app with a title."""
    # Set some layout parameters for the page 
    
    page_config(TOOL_LOGO)
    st.logo(G8_LOGO, size="large", link="https://groupehuit.com/")
    increase_logo()
    set_page_title("General Results")
    menu()
    # Project info
    set_title_1("General Project Information")
    get_project_information()

    # Display existing files in the ZIP_FOLDER with checkboxes
    set_title_1("General Results")
    selected_csv_folder = managing_existing_csv_zipped(CSV_ZIPPED)

    # Just a information to give to the user
    with st.status("Preparing the data...", expanded=True):
        st.write("Opening all the CSV files...")
        selected_csv_folder_path = os.path.join(CSV_ZIPPED, selected_csv_folder)
        if selected_csv_folder != st.session_state.selected_csv_folder:
            process_dataframes_zip_beginner(selected_csv_folder_path,CSV_EXTRACT)
            st.write("Making the data average on your AOI...")
            make_zone_average(dataframes=st.session_state.dataframes)
            st.session_state.long_period = st.session_state.all_df_mean.index.year.min(), st.session_state.all_df_mean.index.year.max()
            st.write("Data is ready")
            st.session_state.selected_csv_folder = selected_csv_folder
        else :
            st.write("Data has already been computed")
    general_management_beginner(st.session_state.all_df_mean)



        

        
        
        


if "__main__":
    main()