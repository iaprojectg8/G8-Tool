from src.utils.imports import *

from src.lib.layout import set_title_3
from src.lib.session_variables import *

# ---------------------------
# --- Zip file management ---
# ---------------------------

def reset_directory(dir_name):
    """
    This function will reset the directory
    Args:
        dir_name (str): The directory to reset
    """
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)
    else:
        shutil.rmtree(dir_name) 
        os.makedirs(dir_name)


def create_temporary_zip(zip_folder, uploaded_file):
    """
    Create a temporary ZIP file to store the uploaded ZIP file
    Args:
        zip_folder (str): The path to the ZIP folder
        uploaded_file (BytesIO): The uploaded ZIP file  
    Returns:
        str: The path to the temporary ZIP file
    """
    temp_file = "temp.zip"
    temp_zip_path = os.path.join(zip_folder, temp_file)
    with open(temp_zip_path, "wb") as f:
        f.write(uploaded_file.read())

    return temp_zip_path

def extract_files(z:ZipFile,zip_folder):
    """
    Handle file extraction and cleanup
    Args:
        z (ZipFile): The zip file
        zip_folder (str): The path to the zip folder
    """
    z.extractall(zip_folder)
    z.close()
    

def reset_directory_if_needed(choice, nc_directory):
    """
    This function will reset the directory if needed
    Args:
        choice (str): The choice of the user
        nc_directory (str): The directory to reset
    """
    if choice == "Yes":
        reset_directory(nc_directory)
        st.success("Your files have been deleted")
    elif choice == "No":
        st.success("Your files are still there")


def managing_existing_csv_zipped(csv_folder):
    """
    This function will manage the existing csv zipped and style the radio button
    Args:
        csv_folder (str): The csv folder
    Returns:
        str: The selected csv folder
    """
    if not os.path.isdir(csv_folder):
        os.makedirs(csv_folder)
    existing_csv_folder = [csv_folder for csv_folder in os.listdir(csv_folder) if csv_folder.endswith(".zip")]
    
    # Checkboxes to select the csv folder
    st.markdown(
        """
        <style>
        .stRadio > div {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;  /* Adjust gap between items */
        }
        .stRadio > div > label {
            flex: 1 1 calc(33.333% - 20px);  /* Three items per row with some gap */
            box-sizing: border-box;

        }
        </style>
        """,
        unsafe_allow_html=True
    )
    ssp = None
    if existing_csv_folder !=[]:
        st.session_state.selected_csv_folder = st.radio("Select CSV folder", existing_csv_folder, key="radio_csv_folder",horizontal=True, )
        ssp = get_ssp_from_zip(st.session_state.selected_csv_folder)
        _, tab2, _ = st.columns(3)
        with tab2:
            if st.session_state.selected_csv_folder :
                st.button("Delete selected csv folder", key="delete_csv_folder", on_click=delete_csv_folder)
    return st.session_state.selected_csv_folder, ssp

def get_ssp_from_zip(filename):
    """
    Get the SSP from the zip file
    Args:
        filename (str): The filename
    Returns:
        str: The SSP
    """
    
    match = re.search(r'\((.*?)\)', filename)
    if match:
        ssp = match.group(1).upper()
        return ssp

# ----------------------------
# --- Shapefile management ---
# ----------------------------

def shapefile_into_gdf(shapefile_path):
    """
    Read a shapefile and return a GeoDataFrame in EPSG:4326 projection.
    Args:
        shapefile_path (str): The path to the shapefile.
    Returns:
        gpd.GeoDataFrame: The GeoDataFrame read from the shapefile.
    """
    gdf = gpd.read_file(shapefile_path)
    gdf = gdf.to_crs("EPSG:4326")
    return gdf
def get_shapefile_path(shapefolder_path):
    """
    Get the path to the shapefile.
    Args:
        shapefolder_path (str): The path to the shapefolder.
    Returns:
        str: The path to the shapefile
    """
    shape_file = [file for file in os.listdir(shapefolder_path) if file.endswith(".shp")][0]
    shapefile_path = os.path.join(shapefolder_path, shape_file)
    return shapefile_path

# ------------------------------------------
# --- Used in the request initialization ---
# ------------------------------------------

def get_years_from_ssp(ssp, historical_end, long_period_start, long_period_end):
    """
    This function will get the years from the ssp
    Args:
        ssp (list): The ssp to use
        historical_end (int): The end year of the historical period
        long_period_start (int): The start year of the period
        long_period_end (int): The end year of the period
    Returns:
        list: The list of years
    """
    years = []
    for scenario in ssp:
        if scenario == "historical":
            if long_period_end <= historical_end:
                years.append(list(range(long_period_start, long_period_end + 1)))
            else:
                years.append(list(range(long_period_start, historical_end + 1)))
        else:
            if long_period_start > historical_end:
                years.append(list(range(long_period_start, long_period_end + 1)))
            else:
                years.append(list(range(historical_end + 1, long_period_end + 1)))
    return years


# ------------------------------
# --- Used after the request ---
# ------------------------------

def normalize_longitudes(df:pd.DataFrame):
    """
    This function will check the coordinates of the dataframe and correct them if necessary.
    Args:
        df (pd.DataFrame): The dataframe to check

    Returns:
        pd.DataFrame: The corrected dataframe
    """
    df.loc[df["lon"] > 180, "lon"] = df.loc[df["lon"] > 180, "lon"] - 360
    return df


def df_to_csv(df: pd.DataFrame, csv_file_path):
    """
    Save a DataFrame to a CSV file.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        csv_file_path (str): The path to the CSV file.
    """
    df.to_csv(csv_file_path, index=True)

def create_zip(zip_file_path, folder):
    """
    Zip a folder containing CSV files.
    Args:
        zip_file_path (str): The path to the ZIP file.
        csv_dir (str): The path to the directory containing the CSV files.
    """
    with ZipFile(zip_file_path, 'w') as zip_file:
        for file in os.listdir(folder):
            if file.endswith('.csv'):
                file_path = os.path.join(folder, file)
                zip_file.write(file_path, file)