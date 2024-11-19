from utils.imports import *
from lib.session_variables import * 
from utils.variables import *


def select_season():
    # Create a list of months with placeholder year 2000 (leap year)

    # The year here is random, it is just to have the format that work on datetime object
    start_date=datetime(2000, 1, 1)
    end_date=datetime(2000, 12, 31)

    start_date, end_date = st.slider(
        "Select a date range:",
        min_value=start_date,
        max_value=end_date,
        value=(start_date, end_date),
        format="MMMM"  # Displays full month name, day, and year
    )      

    start_month = start_date.month
    end_month = end_date.month
    return start_month, end_month



