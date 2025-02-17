from src.utils.imports import * 
from src.utils.variables import TOOL_LOGO, G8_LOGO
from src.lib.layout import *
from src.lib.session_variables import *
from src.parametrization.helpers import *
from src.parametrization.widgets_parametrization import *
from src.parametrization.create_inidicator import indicator_building
from src.parametrization.update_indicator import indicator_editing
from src.lib.layout import page_config_and_menu, set_page_title, set_title_2
from src.request.helpers import managing_existing_csv_zipped


def main():
    """Basic Streamlit app with a title."""
    # Set some layout parameters for the page 
    page_name = "Indicators Parametrization"
    page_config_and_menu(TOOL_LOGO, G8_LOGO)
    set_page_title("Indicators Parametrization")

    set_title_2("Choose ZIP file containing CSV files")
    selected_csv_folder = managing_existing_csv_zipped(CSV_ZIPPED)
    
    # Just a information to give to the user
    if st.button("Load data"):
        with st.status("Preparing the data...", expanded=True):
            st.write("Opening all the CSV files...")
            selected_csv_folder_path = os.path.join(CSV_ZIPPED, selected_csv_folder)
            if selected_csv_folder != st.session_state.selected_csv_loaded:
                process_dataframes_zip_beginner(selected_csv_folder_path,CSV_EXTRACT)
                st.session_state.selected_csv_loaded = selected_csv_folder
            
    # Period
    if len(st.session_state.dataframes)!=0:
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
