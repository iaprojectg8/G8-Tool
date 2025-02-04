from utils.imports import * 
from utils.variables import MONTHS_LIST, DATAFRAME_HEIGHT
from layouts.layout import *
from lib.session_variables import *
from parametrization.helpers import *
from parametrization.widgets_parametrization import *
from parametrization.create_inidicator import indicator_building
from parametrization.update_indicator import indicator_editing




def main():
    """Basic Streamlit app with a title."""
    # Set some layout parameters for the page 
    st.set_page_config(layout="wide")
    set_page_title("Indicators Parametrizations")


    set_title_2("Choose ZIP file containing CSV files")
    uploaded_file = st.file_uploader("Upload a zip file containing CSV files", type="zip")
    
    if uploaded_file is not None or st.session_state.already_uploaded_file is not None:
        extract_to = 'extracted_files'
        # Remove the directory if it exists
        if uploaded_file is not None and uploaded_file != st.session_state.already_uploaded_file:
            
            process_dataframes_zip(uploaded_file, extract_to)
        
        # Period
        set_title_2("Period")
        df_time_filtered = period_management()
        
        if not df_time_filtered.empty:
            
            # Season choice 
            set_title_2("Season Choice")
            df_season, season_start, season_end = season_management(df_time_filtered)
            apply_change_to_dataframes()
            
            # Indicators parametrization
            set_title_2("Parametrize Indicators")

            # Load indicators from CSV
            if st.checkbox(label="Load indicators from CSV"):
                df_uploaded = upload_csv_file()
                if df_uploaded is not None and not df_uploaded.equals(st.session_state.uploaded_df):
                    initialize_indicators_tool_management(df_uploaded)
                    st.session_state.uploaded_df = copy(df_uploaded)
                    
            # Building the indicator in a popover
            with st.popover("Create Indicator", use_container_width = True):
                indicator_building(df_season, season_start, season_end)
            

            if not st.session_state.df_indicators.empty:

                st.dataframe(st.session_state.df_indicators, use_container_width=True)
                _, col1,_, col2, _ = st.columns(5)
                with col1:
                    download_indicators(st.session_state.df_indicators, filename="indicators.csv")
                with col2:
                    delete_all_indicators()
                tabs = st.tabs(list(st.session_state.df_indicators["Name"].values))

                # Iterating over indicators dataframe
                for (i, row), (j, row_checkbox) in zip(st.session_state.df_indicators.iterrows(), st.session_state.df_checkbox.iterrows()):
                    with tabs[i]:
                    
                        indicator_editing(df_season, season_start, season_end, row, row_checkbox, i)
                    
        
if __name__ == "__main__":
    main()
