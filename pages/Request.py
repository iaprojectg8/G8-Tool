from utils.imports import * 
from utils.variables import ZIP_FOLDER, UNIT_DICT, MODEL_NAMES
from maps_related.main_functions import *
from lib.data_process import select_period



def main():
    """Basic Streamlit app with a title."""
    # Set some layout parameters for the page 
    st.set_page_config(layout="wide")
    set_page_title("Requests and visualization")
    set_title_2("Chose the shapefile to visualize")

    # File uploader for ZIP files
    uploaded_files = st.file_uploader("Upload a ZIP file", type="zip", accept_multiple_files=True)
    print(uploaded_files)


    if uploaded_files:
        if not os.path.exists(ZIP_FOLDER):
                os.makedirs(ZIP_FOLDER)
        for zip_file in uploaded_files:
            print(zip_file)
            temp_file = "temp.zip"
            temp_zip_path = os.path.join(ZIP_FOLDER, temp_file)
            with open(temp_zip_path, "wb") as f:
                    f.write(zip_file.read())
                

            # Extract the ZIP file into the temporary directory
            with zipfile.ZipFile(temp_zip_path, "r") as z:
                z.extractall(ZIP_FOLDER)
        
        extracted_folders_list = [file for file in os.listdir(ZIP_FOLDER) if not file.endswith(".zip")]

        selected_shape_folder=[]
        gdf_list = []
        for file in extracted_folders_list:
            if st.checkbox(file):
                selected_shape_folder.append(file)
        
        if selected_shape_folder:
            for file in selected_shape_folder:
                path_to_shapefile = os.path.join(ZIP_FOLDER, file)
                shape_file = [file for file in os.listdir(path_to_shapefile) if file.endswith(".shp")][0]
                print(shape_file)
                shapefile_path = os.path.join(path_to_shapefile, shape_file)
                print(shapefile_path)
                # Load the shapefile using GeoPandas
                gdf = read_shape_file(shapefile_path)
                gdf_list.append(gdf)
            main_map(gdf_list)
            print(list(UNIT_DICT.keys()))
            selected_variables = st.multiselect("Chose variable to extract", UNIT_DICT.keys(), default=np.random.choice(list(UNIT_DICT.keys())))
            selected_model = st.selectbox("Chose the model to use", MODEL_NAMES)
            long_period = (long_period_start, long_period_end) = select_period()
            

        
        
        


if "__main__":
    main()