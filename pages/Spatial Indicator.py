from utils.imports import * 
from utils.variables import ZIP_FOLDER, UNIT_DICT, MODEL_NAMES, DATAFRAME_HEIGHT
from maps_related.main_functions import *
from lib.session_variables import *
from spatial.spatial_indicator import *
from spatial.indicator_modified import indicator_management, spatial_indicator_management
from spatial.general_modified import general_management

def main():
    """Basic Streamlit app with a title."""
    # Set some layout parameters for the page 
    st.set_page_config(layout="wide")
    set_page_title("SIG and visualization")
    set_title_2("Chose the shapefile to load for creating a raster")
    
    uploaded_file = st.file_uploader("Upload a zip file containing CSV files", type="zip")
    
    if uploaded_file is not None:
        extract_to = 'extracted_files'
        # Remove the directory if it exists
        if uploaded_file != st.session_state.uploaded_file_spatial:
            
            if os.path.exists(extract_to):
                shutil.rmtree(extract_to)
            
            # Create the directory
            os.makedirs(extract_to, exist_ok=True)
            
            extract_csv_from_zip(uploaded_file, extract_to)
            st.session_state.uploaded_file_spatial = uploaded_file
            # This is a dataframe dictionary
            st.session_state.dataframes = read_csv_files_from_directory(extract_to)
            st.session_state.gdf = extract_coordinates(st.session_state.dataframes)
            st.session_state.dataframes = put_date_as_index(dataframe_dict=st.session_state.dataframes)

        
        # Create a map centered at the first coordinate
        if st.session_state.gdf is not None:
            with st.expander(label="Dataset coordinates on map"):
                gdf = st.session_state.gdf
                centroid = gdf.geometry.centroid
                bounds = gdf.total_bounds
                zoom_start = calculate_zoom_level(bounds)
                m = folium.Map(location=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()], zoom_start=zoom_start)
                for _, row in gdf.iterrows():
                    folium.Marker(location=[row.lat, row.lon]).add_to(m)
                st_folium(m,height= 300, use_container_width=True)
        else:
            st.write("No coordinates found in the CSV files.")

        
        set_title_2("What do you want to do ?") 
        indicator_choice = st.radio(
            label="Choose an indicator type:",
            options=["Make spatial indicators", "Make overall average indicator"],
            index=0  # Default selection
        )
        if indicator_choice == "Make spatial indicators":
            # Define an indicator sample to simutlate the indicator building on a subset
            df_indicator_sample = copy(st.session_state.dataframes[list(st.session_state.dataframes.keys())[0]])

            spatial_indicator_management(df_indicator_sample, st.session_state.dataframes)


        elif indicator_choice == "Make overall average indicator":
            set_title_2("Overall average indicator")
            if st.button(label="Average your Dataset"):
                make_zone_average(dataframes=st.session_state.dataframes)
            if st.session_state.all_df_mean is not None :
                df_overall_averaged = st.session_state.all_df_mean
                with st.expander(label="Your dataset average is ready"):
                    lat, lon = df_overall_averaged.iloc[0][['lat', 'lon']]
                    folium.Marker(location=[lat, lon],
                                    icon=folium.Icon(icon="glyphicon-ok-circle", 
                                                    prefix="glyphicon", 
                                                    color="red")
                                    ).add_to(m)
                    st_folium(m,height= 300, use_container_width=True)
                
                # Tab init
                tab_general, tab_indicator = st.tabs(["General", "Indicators"])
                with tab_general:
                    general_management(df_overall_averaged)
                with tab_indicator:
                    indicator_management(df_overall_averaged)

if __name__ == "__main__":
    main()
