from src.utils.imports import * 
from src.utils.variables import TRANSPARENT_TOOL_LOGO, G8_LOGO, CSV_ZIPPED, CSV_EXTRACT
from src.lib.session_variables import *
from src.request.helpers import managing_existing_csv_zipped
from request.widgets import get_project_information

from src.parametrization.helpers import process_dataframes_zip
from src.results.result_functions import make_zone_average, general_management_beginner
from src.lib.layout import page_config_and_menu, set_title_1, set_page_title



def main():
    """
    Beginner Results page
    """
    # Set some layout parameters for the page 
    page_name = "General Results"
    initialize_session_state_variable()
    page_config_and_menu(TRANSPARENT_TOOL_LOGO, G8_LOGO, page_name)
    set_page_title("General Results")
  
    # Project info
    set_title_1("General Project Information")
    get_project_information()

    # Display existing files in the ZIP_FOLDER with checkboxes
    set_title_1("General Results")
    selected_csv_folder, ssp = managing_existing_csv_zipped(CSV_ZIPPED)

    # Just a information to give to the user
    if selected_csv_folder is not None:
        if st.button("Load data"):
            with st.status("Preparing the data...", expanded=True):
                st.write("Opening all the CSV files...")
                selected_csv_folder_path = os.path.join(CSV_ZIPPED, selected_csv_folder)
                if selected_csv_folder != st.session_state.selected_csv_loaded:
                    process_dataframes_zip(selected_csv_folder_path,CSV_EXTRACT)
                    st.session_state.selected_csv_loaded = selected_csv_folder
                    st.write("Making the data average on your AOI...")
                    make_zone_average(dataframes=st.session_state.dataframes)
                    st.session_state.long_period = st.session_state.all_df_mean.index.year.min(), st.session_state.all_df_mean.index.year.max()
                    st.write("Data is ready")
                    st.session_state.selected_csv_folder = selected_csv_folder
        if len(st.session_state.dataframes) != 0:
            general_management_beginner(st.session_state.all_df_mean, ssp)
    else:
        st.warning("You don't have anything in your requested folder, it means you need to make a request to have data")


if "__main__":
    main()