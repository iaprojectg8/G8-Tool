from utils.imports import *
from utils.variables import DATAFRAME_HEIGHT
from lib.data_process import loads_data, column_choice
from lib.parametrization import select_season

def main():
    """Basic Streamlit app with a title."""
    st.title("Basic Streamlit App")

    # Loading CSV 
    filename = "CSV_files/cmip6_era5_data_daily_0.csv"
    data, lat, lon = loads_data(filename=filename)

    st.dataframe(data, height=DATAFRAME_HEIGHT)
    df_final = column_choice(data)
    print(type(df_final))
    st.dataframe(df_final, height=DATAFRAME_HEIGHT)

    # Initialize indicators
    st.subheader("Parametrize indicators")

    season_bool = st.checkbox("Need a season or a period study", value=True)
    if season_bool:
        period_start, period_end = select_season()



if "__main__":
    main()