from utils.imports import *
from utils.variables import DATAFRAME_HEIGHT
from lib.data_process import loads_data, column_choice

def main():
    """Basic Streamlit app with a title."""
    st.title("Basic Streamlit App")
    filename = "CSV_files\cmip6_era5_data_daily_0.csv"
    data, lat, lon = loads_data(filename=filename)

    st.dataframe(data, height=DATAFRAME_HEIGHT)
    df_final = column_choice(data)
    st.dataframe(df_final, height=DATAFRAME_HEIGHT)



if "__main__":
    main()