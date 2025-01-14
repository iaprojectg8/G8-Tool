from utils.imports import * 
from utils.variables import ZIP_FOLDER, UNIT_DICT, MODEL_NAMES, DATAFRAME_HEIGHT, DATASET_FOLDER
from maps_related.main_functions import *
from lib.data_process import select_period
from requests_api.request_functions import request_all_data, gdf_to_df



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
                shapefile_path = os.path.join(path_to_shapefile, shape_file)

                # Load the shapefile using GeoPandas
                gdf :gpd.GeoDataFrame = read_shape_file(shapefile_path)
                # Ask the user to define a buffer distance
                buffer_distance = st.number_input(
                    label=f"Enter buffer distance (in the same units as {file} coordinates):",
                    min_value=0.0, 
                    step=0.1,
                    value=0.0,
                    format="%0.3f",
                    key=file
                )
                
                # Apply the buffer if the distance is greater than 0
                if buffer_distance > 0:
                    gdf["geometry"] = gdf["geometry"].buffer(buffer_distance, resolution=0.05)
                    st.success(f"Buffer of {buffer_distance} applied to {file}")

                gdf_list.append(gdf)
            combined_gdf = pd.concat(gdf_list, ignore_index=True)
            df = main_map(combined_gdf)
            print(len(df))
            with st.expander(label="Your coordinates"):
                st.dataframe(data=df, height=DATAFRAME_HEIGHT, use_container_width=True)
            if st.checkbox(label="Take all variables"):
                selected_variables = st.multiselect("Chose variable to extract", 
                                                    UNIT_DICT.keys(), 
                                                    default=UNIT_DICT.keys())
            else:
                selected_variables = st.multiselect("Chose variable to extract", 
                                                    UNIT_DICT.keys(), 
                                                    default=np.random.choice(list(UNIT_DICT.keys())))
            selected_model = st.selectbox("Chose the model to use", MODEL_NAMES)
            (long_period_start, long_period_end) = select_period(key="request")

            if st.button(label="Start the Request"):
                request_all_data(coordinates=df,
                                 dataset_folder=DATASET_FOLDER,
                                 filename_base="moroni_extraction",
                                 model=selected_model,
                                 start_year=long_period_start,
                                 end_year=long_period_end,
                                 variable_list=selected_variables)
            

        
        
        


if "__main__":
    main()