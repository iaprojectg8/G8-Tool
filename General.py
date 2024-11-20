from utils.imports import *
from utils.variables import DATAFRAME_HEIGHT
from lib.data_process import * 
from lib.parametrization import *
from layout.layout import *
from lib.plot import *

def main():
    """Basic Streamlit app with a title."""
    set_page_width(1200)
    set_page_title("title")
    set_title_1("Climate Variables")

    # Variable choice
    # Chosen variable has a certain case that might be broken to easier use
    chosen_variables = variable_choice()
    print(chosen_variables)


    # Period choice
    long_period = (long_period_start, long_period_end) = select_period()

    # Period cut
    smaller_period_length  = st.select_slider("Chose the length of smaller period to see the evolution of your data on them",options=[10,20,25,30])
    periods = split_into_periods(smaller_period_length, long_period_start, long_period_end)
    print(periods)
    
    # Loading CSV, this will almost surely be replaced by 
    filename = "CSV_files/cmip6_era5_data_daily_0.csv"
    data, lat, lon = loads_data(filename=filename)

    st.write("Possibility to upload a CSV file")
    st.write("Here is your dataset with the relevant variable following your precedent choices")
    data_to_keep = apply_changes(data, chosen_variables, long_period)

    # -- From now it will be a plot part with monthly means and regression through all time --
    plot_monthly_means(data_to_keep, periods)

if "__main__":
    main()