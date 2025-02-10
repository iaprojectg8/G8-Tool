from utils.imports import *
from utils.variables import ZIP_FOLDER
from layouts.layout import *
from lib.session_variables import *

def extract_files(z:ZipFile,zip_folder, temp_zip_path):
    """Handle file extraction and cleanup"""
    z.extractall(zip_folder)
    z.close()
    os.remove(temp_zip_path)


def get_project_information():
    st.session_state.project_info["project_name"] = st.text_input("Project name")
    st.session_state.project_info["client_name"] = st.text_input("Client name")
    st.session_state.project_info["financier_name"] = st.text_input("Financier name")

def ensure_zip_folder_exist(zip_folder):
    if not os.path.exists(zip_folder):
        os.makedirs(zip_folder)

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