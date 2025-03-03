from utils.imports import *
from utils.variables import DATAFRAME_HEIGHT, FILENAME
from archives.data_process import * 
from indicators.parametrization.parametrization import *
from lib.plot import *
from lib.layout import *



def main():
    """Basic Streamlit app with a title."""

    # Set some layout parameters for the page 
    st.set_page_config(layout="wide")
    set_page_title("General Informations")
    set_title_1("Climate Variables")
    key="General"

    # Chosen variable has a certain case that might be broken to easier use
    chosen_variables = variable_choice()
    print(chosen_variables)

    # Period choice
    long_period = (long_period_start, long_period_end) = select_period(key)

    # Period cut
    smaller_period_length  = st.select_slider("Choose the length of smaller period to see the evolution of your data on them:",
                                              options=PERIOD_LENGTH)
    periods = split_into_periods(smaller_period_length, long_period_start, long_period_end)
    print(periods)
    
    # Loading CSV, this will almost surely be replaced by 
    path = f"CSV_files/{FILENAME}"
    if chosen_variables : 
        data = loads_data(filename=path)

        st.write("Here is your dataset with the relevant variables following your precedent choices:")
        data_to_keep = filtered_data(data, chosen_variables, long_period)

        
        # Plot part with monthly means and regression through all time
        filename = FILENAME.split(".")[0]
        general_plot(data_to_keep, periods, filename)

if __name__== "__main__":
    main()