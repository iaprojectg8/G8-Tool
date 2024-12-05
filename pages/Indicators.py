from utils.imports import *
from utils.variables import DATAFRAME_HEIGHT
from lib.data_process import loads_data, column_choice
from indicators.parametrization import * 
from layouts.layout import *
from lib.widget import * 
from indicators.calculation import *

def main():
    """Basic Streamlit app with a title."""
    # Set some layout parameters for the page 
    st.set_page_config(layout="wide")
    set_page_title("Indicators Customization")
    set_title_1("First Selection")
    set_title_2("Variable Summary")
    # Loading CSV 
    filename = "CSV_files/cmip6_era5_data_daily_0.csv"
    data = loads_data(filename=filename)
    st.dataframe(data, height=DATAFRAME_HEIGHT, use_container_width=True)

    set_title_2("Variable Choice")
    df_chosen = column_choice(data)
    if not df_chosen.empty:
        print(type(df_chosen))
        st.dataframe(df_chosen, height=DATAFRAME_HEIGHT, use_container_width=True)
        

        set_title_2("Season Choice")
        if st.checkbox("Need a season or a period study", value=True):
            season_start, season_end = select_season()
            df_season = select_data_contained_in_season(df_chosen, season_start, season_end)
        else:
            df_season = df_chosen
        st.dataframe(df_season, height=DATAFRAME_HEIGHT, use_container_width=True)

        # Initialize indicators
        st.subheader("Parametrize indicators")
        file_upload = st.checkbox(label="Upload your CSV indicator configuration")
        if file_upload :
            df = upload_csv_file()
        else :
            df = create_empty_dataframe()
        df_indicator_paramters = create_dynamic_dataframe(df, df_season.columns)
        

        # Need to calculate score with this parameters
        calculate_score(df_season, df_indicator_paramters)

    set_title_2("Exposure or suitability")
    # Faire une function pour différencier les seuils mettre en place l'ordre du comptage

    set_title_1("Indicators Calculation")
    yearly_threshold_init()

        # # The threshold init
        # st.subheader("Daily threshold definition")
        # daily_thresh_dict = daily_threshold_init()
        # yearly_thresh_dict = yearly_threshold_init()
    



if "__main__":
    main()