from src.utils.imports import * 
from src.utils.variables import ZIP_FOLDER, TRANSPARENT_TOOL_LOGO, G8_LOGO, DATAFRAME_HEIGHT
from src.lib.session_variables import initialize_session_state_variable

from src.lib.layout import page_config_and_menu, set_page_title, set_title_1, set_title_2

from src.request.widget import get_project_location, shapefile_uploader, display_coordinates
from src.request.cmip6_requests import process_shapefile, make_empty_request_for_each_gdf, make_whole_request
from src.request.map_related import map_empty_request


def main():
    """Basic Streamlit app with a title."""
    # Set some layout parameters for the page 
    page_name = "Beginner Request"
    initialize_session_state_variable()
    page_config_and_menu(TRANSPARENT_TOOL_LOGO, G8_LOGO, page_name)
    set_page_title("Request")
    
    set_title_1("Project Shortname")
    get_project_location()

    set_title_1("Requests")
    set_title_2("Area of interest")
    
    # Shapefile uploader
    selected_shape_folder = shapefile_uploader(ZIP_FOLDER)
    if selected_shape_folder is not None:

        combined_gdf, gdf_list = process_shapefile(selected_shape_folder, ZIP_FOLDER, default_buffer_distance=0.2)
        empty_request_gdf = make_empty_request_for_each_gdf(gdf_list)

        # Display
        display_coordinates(empty_request_gdf, height=DATAFRAME_HEIGHT)

        if not empty_request_gdf.empty:

            # Put on a map the requested coordinates
            map_empty_request(combined_gdf, empty_request_gdf)
            print("start requesting")
            make_whole_request(combined_gdf.total_bounds)


if "__main__":
    main()