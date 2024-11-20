from utils.imports import *
from utils.variables import DATAFRAME_HEIGHT
from lib.data_process import loads_data, column_choice
from lib.parametrization import select_season, daily_threshold_init, yearly_threshold_init

def main():
    """Basic Streamlit app with a title."""
    st.title("General Information")

    # Loading CSV 
    filename = "CSV_files/cmip6_era5_data_daily_0.csv"
    data, lat, lon = loads_data(filename=filename)

    st.dataframe(data, height=DATAFRAME_HEIGHT)
    df_final = column_choice(data)
    print(type(df_final))
    st.dataframe(df_final, height=DATAFRAME_HEIGHT)

    # Initialize indicators
    st.subheader("Parametrize indicators")
 
    if st.checkbox("Need a season or a period study", value=True):
        # Here we get a period in case there is a need of this in the analysis
        period_start, period_end = select_season()

    # The threshold init
    st.subheader("Daily threshold definition")
    daily_thresh_dict = daily_threshold_init()
    yearly_thresh_dict = yearly_threshold_init()



if "__main__":
    main()