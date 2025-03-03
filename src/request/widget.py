from src.utils.imports import *
from src.utils.variables import DATAFRAME_HEIGHT

from src.request.helpers import extract_files, reset_directory, create_temporary_zip, get_years_from_ssp, get_utm_epsg

from src.lib.layout import set_title_3

# ---------------------------
# --- Project Information ---
# ---------------------------

def get_project_location():
    """
    Get the project location from the user.
    """
    st.session_state.shortname = st.text_input("Shortname (without special characters)")


def get_project_information():
    """
    This function will get the project information
    """
    st.session_state.project_info["project_name"] = st.text_input("Project name")
    st.session_state.project_info["client_name"] = st.text_input("Client name")
    st.session_state.project_info["financier_name"] = st.text_input("Financier name")

# ---------------------------
# --- Shape file Uploader ---
# ---------------------------

def shapefile_uploader(zip_folder):
    """
    Upload a shapefile as a ZIP file.
    Args:
        zip_folder (str): The path to the ZIP folder
    Returns:
        list: The list of folders in the ZIP folder if the shapefile is uploaded, else an empty list
    """
    uploaded_shape_zip = st.file_uploader("Upload a ZIP containing a shapefile", type="zip", accept_multiple_files=False)

    if uploaded_shape_zip:

        # First, delete any existing files in the ZIP folder
        reset_directory(zip_folder)
        temporary_zip = create_temporary_zip(zip_folder, uploaded_shape_zip)

        # Check if the ZIP file contains the required shapefile components
        with zipfile.ZipFile(temporary_zip, "r") as z:
            extracted_files = z.namelist()
            required_extensions = {".shp", ".shx", ".prj"}
            extracted_extensions = {ext for ext in (os.path.splitext(file)[1] for file in extracted_files) if ext}

            # Check for the shapefile existence
            if required_extensions.issubset(extracted_extensions):
                st.success("Shape file has been uploaded successfully.")
                extract_files(z, zip_folder)
                os.remove(temporary_zip)
                selected_shape_folder = os.listdir(zip_folder)

                return selected_shape_folder
        
            else:
                extracted_extensions_readable = ", ".join(list(extracted_extensions)[:-1]) + list(extracted_extensions)[-1] if extracted_extensions else ""
                st.error(f"The uploaded ZIP file contains {extracted_extensions_readable} files which is not the kind of file expected for an AOI shape." 
                        " Please ensure your zip includes .shp, .shx, and .prj files.")


# -----------------------
# --- Request Widgets ---
# -----------------------

def manage_buffer(gdf: gpd.GeoDataFrame, default_buffer_distance):
    """
    Manage the buffer distance for the shapefile, and apply it if distance is greater than 0.
    Args:
        gdf (gpd.GeoDataFrame): The GeoDataFrame of the shapefile   
        default_buffer_distance (float): The default buffer distance
    Returns:
        gpd.GeoDataFrame: The GeoDataFrame with the buffer applied.
    """

    if st.session_state.mode == "Beginner":
        buffer_distance = default_buffer_distance
    else:
        buffer_distance = st.number_input(label=f"Enter buffer distance in degree for the shape (0.25 is about 25 kilometers):",
                                        min_value=0, 
                                        step=1000,
                                        value=default_buffer_distance,
                                        key="buffer")
    # Apply the buffer if the distance is greater than 0
    if buffer_distance > 0:
        # This trigger a warning but i don't know how to make this better
        centroid  = gdf.geometry.centroid
        utm_epsg = get_utm_epsg(centroid.y[0], centroid.x[0])
        print(utm_epsg)
        st.session_state.crs = utm_epsg
        gdf = gdf.to_crs(epsg=utm_epsg)
        gdf_geometry : gpd.GeoSeries = gdf["geometry"]
        gdf_geometry.to_csv("test.csv")
        gdf["geometry"] = gdf_geometry.buffer(distance=buffer_distance, resolution=0.05)
        gdf = gdf.to_crs(epsg=4326)
        if st.session_state.mode == "Expert":
            st.success(f"Buffer of {buffer_distance} applied on the shape")
    return gdf


# -------------------------------------
# --- Widget Initialization Request ---
# -------------------------------------

def widget_init_beginner(cmip6_variables: dict, historical_end, ssp_list):
    """
    This function will initialize the widgets for the cmip6 request
    Returns:
        tuple: The selected variables, the selected model, the ssp, the experiment and the years
    """
    # Variable
    selected_variables = select_variables_to_request(cmip6_variables)
    real_selected_variables = list(map(lambda key : cmip6_variables.get(key),selected_variables))
    
    # Period
    (long_period_start, long_period_end) = select_period_cmip6(key="cmip6")
    
    # Model
    selected_model = "CNRM-ESM2-1"
    # Select a scenario
    ssp = select_ssp(long_period_start, long_period_end, historical_end, ssp_list)
    experiment = "r1i1p1f2"

    # Process to get proper years
    years = get_years_from_ssp(ssp, historical_end, long_period_start, long_period_end)
    
    return real_selected_variables, selected_model, ssp, experiment, years


def widget_init(cmip6_variables: dict, model_name, ssp_list, historical_end, experiment):

    """
    This function will initialize the widgets for the cmip6 request
    Returns:
        tuple: The selected variables, the selected model, the ssp, the experiment and the years
    """
    # Variable
    selected_variables = select_variables_to_request(cmip6_variables)
    real_selected_variables = list(map(lambda key : cmip6_variables.get(key),selected_variables))

    

    # Period
    (long_period_start, long_period_end) = select_period_cmip6(key="cmip6")
    
    # Model
    if st.session_state.mode == "Beginner":
        selected_model = "CNRM-ESM2-1"
    else:
        selected_model = st.selectbox("Chose the model to use", model_name)

    # Select a scenario
    ssp = select_ssp(long_period_start, long_period_end, historical_end, ssp_list)
    if st.session_state.mode == "Beginner":
        experiment = "r1i1p1f2"
    else:
        experiment = st.selectbox(label="Chose the experiment to use", options=experiment)

    # Process to get proper years
    years = get_years_from_ssp(ssp, historical_end, long_period_start, long_period_end)
    
    return real_selected_variables, selected_model, ssp, experiment, years


def select_variables_to_request(cmip6_variables):
    """
    This function will allow the user to select the variables to extract
    Args:
        cmip6_variables (dict): The dict of variables
    Returns:    
        list: The selected variables
    """
    all_variable_checkbox = st.checkbox(label="Take all variables")
    selected_variables = st.pills("Chose variable to extract", 
                                        cmip6_variables.keys(), 
                                        default=cmip6_variables.keys() if all_variable_checkbox else None,
                                        selection_mode="multi")
    
    return selected_variables


def select_period_cmip6(key):
    """
    Allows the user to select a data period using an interactive Streamlit slider.

    Returns:
        tuple: The start and end values of the selected period.
    """
    # Display the slider that allows the user to select the bounds
    
    start = 1950
    end = 2100
    period_start, period_end = st.slider(
        "Select the data period:",
        min_value=start, 
        max_value=end,
        value=(start, end),
        key=key)      
    return period_start, period_end

def select_ssp(long_period_start, long_period_end, historical_end, ssp_list):
    """
    This function will allow the user to select the ssp to use
    Args:
        long_period_start (int): The start year of the period
        long_period_end (int): The end year of the period
    Returns:
        str: The ssp to use
    """
    if long_period_end<=historical_end:
        ssp = ["historical"]
    elif long_period_start > historical_end :
        ssp = st.pills(label="Chose the ssp to use", options=ssp_list, default=ssp_list[0], selection_mode="multi")
    else:
        ssp = st.pills(label="Chose the ssp to use", options=ssp_list, default=ssp_list[0], selection_mode="multi")
        ssp = ["historical", *ssp]
    return ssp



def ask_reset_directory(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    existing_files = os.listdir(folder)
    if existing_files != []:
        set_title_3("Before to make your request, you should know that your request folder is not empty, and here are the files in it")
        with st.expander(label="Files in the request folder"):
            # The markdown here is just to have a fix height for the expander
            st.markdown(
                f"""
                <div style="height: {DATAFRAME_HEIGHT}px; overflow-y: auto;">
                    {existing_files}
                </div>
                """, 
                unsafe_allow_html=True
            )
        choice = st.radio("Do you want to empty it", ["No","Yes"])
        return choice
    
# ----------------------------------------
# --- Widget initialization Open-Meteo ---
# ----------------------------------------
def widget_init_open_meteo(open_meteo_dict : dict, model_names):
    if st.checkbox(label="Take all variables"):
            selected_variables = st.pills("Chose variable to extract", 
                                                open_meteo_dict.keys(), 
                                                default=open_meteo_dict.keys(),
                                                selection_mode="multi")
    else:
        selected_variables = st.pills("Chose variable to extract", 
                                            open_meteo_dict.keys(), 
                                            default=np.random.choice(list(open_meteo_dict.keys())),
                                            selection_mode="multi") 
    selected_model = st.selectbox("Chose the model to use", model_names)
    (long_period_start, long_period_end) = select_period_open_meteo(key="request")
    return selected_variables, selected_model, long_period_start, long_period_end



def select_period_open_meteo(key):
    """
    Allows the user to select a data period using an interactive Streamlit slider.

    Returns:
        tuple: The start and end values of the selected period.
    """
    # Define the initial limits for the slider
    period_start= 1950
    period_end= 2050

    # Display the slider that allows the user to select the bounds
    period_start, period_end = st.slider(
        "Select the data period:",
        min_value=period_start, 
        max_value=period_end,
        value=(period_start, period_end),
        key=key)      
    return period_start, period_end


# -------------------------------
# --- Progress bar management ---
# -------------------------------

def initialize_progress_bar(size_or_iterable, text):
    """
    Progress bar initialization
    Args:
        years_list (list): The list of years
        text (str): The text to display
    Returns:
        tuple: The progress bar, the progress and the total
    """
    progress_bar = st.progress(0, text=text)
    progress = 0
    total_progress = size_or_iterable if isinstance(size_or_iterable, int) else len(size_or_iterable)
    print(total_progress)
    return progress_bar, progress, total_progress

def update_progress_bar(progress_bar, progress, total_progress, text):
    """
    Update the progress bar
    Args:
        progress_bar (st.progress): The progress bar
        progress (int): The progress
        total_progress (int): The total progress
        text (str): The text to display
    """
    progress +=1
    progress_percentage = int((progress / total_progress) * 100)
    progress_bar.progress(progress / total_progress, text=f"{text} {progress_percentage}%")
    return progress_bar, progress, total_progress,


# -------------------
# --- Display gdf ---
# -------------------

def display_coordinates(empty_request_gdf, height):
    """
    Display the coordinates of the shapefile
    Args:
        empty_request_gdf (gpd.GeoDataFrame): The GeoDataFrame of the shapefile
        height (int): The height of the displayed GeoDataFrame
    """
    with st.expander(label="Your coordinates"):
        displayed_gdf = empty_request_gdf[["lat", "lon"]]
        st.dataframe(data=displayed_gdf, height=height, use_container_width=True)
