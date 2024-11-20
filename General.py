from utils.imports import *
from utils.variables import DATAFRAME_HEIGHT
from lib.data_process import * 
from lib.parametrization import *
from layout.layout import *

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
    period = (period_start, period_end) = select_period()

    # Period cut

    

    # Loading CSV, this will almost surely be replaced by 
    filename = "CSV_files/cmip6_era5_data_daily_0.csv"
    data, lat, lon = loads_data(filename=filename)
    print(data.index.year)

    st.write("Possibility to upload a CSV file")
    st.write("Here is your dataset with the relevant variable following your precedent choices")
    apply_changes(data, chosen_variables, period)



if "__main__":
    main()