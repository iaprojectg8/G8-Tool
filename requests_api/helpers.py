from utils.imports import *
from utils.variables import ZIP_FOLDER
from layouts.layout import *
from lib.session_variables import *

def extract_files(z:ZipFile,zip_folder, temp_zip_path):
    """Handle file extraction and cleanup"""
    z.extractall(zip_folder)
    z.close()
    os.remove(temp_zip_path)


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


def get_project_location():
    st.session_state.location = st.text_input("Location")

def get_project_information():
    st.session_state.project_info["project_name"] = st.text_input("Project name")
    st.session_state.project_info["client_name"] = st.text_input("Client name")
    st.session_state.project_info["financier_name"] = st.text_input("Financier name")

def ensure_zip_folder_exist(zip_folder):
    if not os.path.exists(zip_folder):
        os.makedirs(zip_folder)

def extract_csv_from_zip(zip_file, extract_to):
    """
    Extracts the CSV files from a zip file.
    Args:
        zip_file (BytesIO): The zip file containing the CSV files.
        extract_to (str): The directory to extract the files
    """
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def managing_existing_csv_zipped(csv_folder):
    existing_csv_folder = [csv_folder for csv_folder in os.listdir(csv_folder) if csv_folder.endswith(".zip")]
    # Checkboxes to select the csv folder
    if existing_csv_folder != []:
        set_title_3("Select already uploaded csv folders")

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
    selected_csv_folder = st.radio("Select CSV folder", existing_csv_folder, key="radio_csv_folder",horizontal=True, )
            
    tab1, tab2, tab3 = st.columns(3)
    with tab2:
        if st.session_state.selected_csv_folder :
            st.button("Delete selected csv folder", key="delete_csv_folder", on_click=delete_csv_folder)
    return selected_csv_folder

def managing_existing_folders(zip_folder):
    existing_shape_folder = [shape_folder for shape_folder in os.listdir(zip_folder) if not shape_folder.endswith(".zip")]
    # Checkboxes to select the shape folder
    if existing_shape_folder != []:
        set_title_3("Select already uploaded shape folders")

    tab1, tab2, tab3 = st.columns(3)
    for i, folder in enumerate(existing_shape_folder):
        with tab1 if i % 3 == 0 else tab2 if i % 3 == 1 else tab3:
            checkbox = st.checkbox(folder)
        if checkbox and folder not in st.session_state.selected_shape_folder:
            st.session_state.selected_shape_folder.append(folder)
        elif not checkbox and folder in st.session_state.selected_shape_folder:
            st.session_state.selected_shape_folder.remove(folder)
    tab1, tab2, tab3 = st.columns(3)
    with tab2:
        if st.session_state.selected_shape_folder != []:
            st.button("Delete selected shape folder", key="delete_shape_folder", on_click=delete_shape_folder)


def shapefile_uploader(zip_folder):
    uploaded_shape_zip = st.file_uploader("Upload your polygon shape as a ZIP file", type="zip", accept_multiple_files=False)

    if uploaded_shape_zip:

        # Create a temporary file to store the uploaded ZIP file
        if os.listdir(zip_folder) != []:
            for folder in os.listdir(zip_folder):
                shutil.rmtree(os.path.join(zip_folder, folder))
        temp_file = "temp.zip"
        temp_zip_path = os.path.join(zip_folder, temp_file)
        with open(temp_zip_path, "wb") as f:
            f.write(uploaded_shape_zip.read())

        # Check if the ZIP file contains the required shapefile components
        with zipfile.ZipFile(temp_zip_path, "r") as z:
            extracted_files = z.namelist()
            required_extensions = {".shp", ".shx", ".prj"}
            extracted_extensions = {ext for ext in (os.path.splitext(file)[1] for file in extracted_files) if ext}

            if required_extensions.issubset(extracted_extensions):
                st.success("Shape file has been uploaded successfully.")
                extract_files(z, zip_folder, temp_zip_path)
                selected_shape_folder = os.listdir(zip_folder)
                return selected_shape_folder
        
            else:
                extracted_extensions_readable = ", ".join(list(extracted_extensions)[:-1]) + list(extracted_extensions)[-1] if extracted_extensions else ""
                st.error(f"The uploaded ZIP file contains {extracted_extensions_readable} files which is not the kind of file expected for an AOI shape." 
                        " Please ensure it includes .shp, .shx, and .prj files.")

def shapefile_uploader_management():
    set_title_3("Upload a new shapefile")
    show_uploader = st.checkbox("Upload new ZIP file", key="show_uploader")

    if show_uploader:
        uploaded_shape_zip = st.file_uploader("Upload your polygon shape as a ZIP file", type="zip", accept_multiple_files=False)

        if uploaded_shape_zip:

            # Create a temporary file to store the uploaded ZIP file
            temp_file = "temp.zip"
            temp_zip_path = os.path.join(ZIP_FOLDER, temp_file)
            with open(temp_zip_path, "wb") as f:
                f.write(uploaded_shape_zip.read())

            # Check if the ZIP file contains the required shapefile components
            with zipfile.ZipFile(temp_zip_path, "r") as z:
                extracted_files = z.namelist()
                required_extensions = {".shp", ".shx", ".prj"}
                extracted_extensions = {ext for ext in (os.path.splitext(file)[1] for file in extracted_files) if ext}

                if required_extensions.issubset(extracted_extensions):
                    st.success("Shape file has been uploaded successfully.")
                    extract_files(z, ZIP_FOLDER, temp_zip_path)
                    st.button("Reset the uploader", key="extract_shape_zip", on_click=reset_uploader)

            
                else:
                    extracted_extensions_readable = ", ".join(list(extracted_extensions)[:-1]) + list(extracted_extensions)[-1] if extracted_extensions else ""
                    st.error(f"The uploaded ZIP file contains {extracted_extensions_readable} files which is not the kind of file expected for an AOI shape." 
                            " Please ensure it includes .shp, .shx, and .prj files.")