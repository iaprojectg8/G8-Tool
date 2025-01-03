from utils.imports import * 
from utils.variables import ZIP_FOLDER, UNIT_DICT, MODEL_NAMES
from maps_related.main_functions import *
from lib.data_process import select_period



def main():
    """Basic Streamlit app with a title."""
    # Set some layout parameters for the page 
    st.set_page_config(layout="wide")
    set_page_title("SIG and visualization")
    set_title_2("Chose the shapefile to load for creating a raster")
        
        
        


if "__main__":
    main()