from utils.imports import *
from utils.variables import *
from layouts.layout import *
from parametrization.create_inidicator import *

def select_period(key):
    """
    Allows the user to select a data period using an interactive Streamlit slider.

    Returns:
        tuple: The start and end values of the selected period.
    """
    # Define the initial limits for the slider
    period_start= st.session_state.min_year
    period_end= st.session_state.max_year

    # Display the slider that allows the user to select the bounds
    period_start, period_end = st.slider(
        "Select the data period:",
        min_value=period_start, 
        max_value=period_end,
        value=(period_start, period_end),
        key=key)      
    return period_start, period_end

def split_into_periods_indicators(period_length, start_year, end_year):
    """
    Splits a given time range into multiple periods of a specified length.

    Args:
        period_length (int): The length of each period in years.
        start_year (int): The starting year of the entire time range.
        end_year (int): The ending year of the entire time range.

    Returns:
        list of tuples: A list of tuples where each tuple represents a period
                        with the format (period_start, period_end).
    """
    whole_period_length = end_year - start_year + 1
    amount_of_periods = ceil(whole_period_length / period_length)
    periods = []

    # Loop through each period index and calculate start and end years
    for period_index in range(amount_of_periods):
        period_start = start_year + period_index * period_length   # Start year of the current period
        period_end = period_start + period_length -1  # End year of the current period

        # Append the period to the list, ensuring it does not exceed the end year
        if period_end < end_year:
            periods.append((period_start, period_end))
        elif abs(period_start - end_year)<0.3*period_length:
            # Needs to create last tuple periods before to remove the last element of the list
            last_period = (periods[-1][0], end_year)
            periods.pop()
            periods.append(last_period)
        else:
            periods.append((period_start, end_year))

    return periods

def period_filter(data, period):
    """
    Filters the input data to include only rows within the specified period.

    Args:
        data (DataFrame): A pandas DataFrame with a DateTime index.
        period (list or tuple): A list or tuple containing the start and end years [start_year, end_year].

    Returns:
        DataFrame: A filtered DataFrame containing only rows within the specified period.
    """
    # Select rows where the year in the index is between the start and end years of the period
    data_in_right_period = data[(data.index.year >= period[0]) & (data.index.year <= period[-1])]
    
    return data_in_right_period

def column_choice(data : pd.DataFrame):
    """
    Allows a user to select a column of interest from a DataFrame, excluding certain columns.

    Args:
        data (pd.DataFrame): The input DataFrame containing the data.

    Returns:
        pd.Series: The selected column from the DataFrame as a Pandas Series.
    """
    not_a_variable = [ "lat", "lon"]
    columns_list = [column  for column in data.columns if column not in not_a_variable]

    # Widget that allows the user to select the variable he wants to see plotted
    st.session_state.columns_chosen = st.multiselect("Chose variable of interest", options=columns_list)
    columns_chosen = st.session_state.columns_chosen

    # Restrict the dataframe to the user selected columns
    df_final = data[columns_chosen]

    return df_final

def select_season():
    """
    Allows the user to select a date range using a slider for months.

    Returns:
        tuple: A tuple containing the start and end month selected by the user.
    """
    # Building the avaailable option
    start=1
    end=12
    options =  np.arange(start, end+1)

    # Widget slider to chose the starting and ending month for each years
    start_date, end_date = st.select_slider(
        "Select a date range:",
        options = options,
        value=(st.session_state.season_start, st.session_state.season_end),
        format_func=lambda x:MONTHS_LIST[x-1]  # Displays full month name, day, and year
    )
    # Display the selected range
    selected_months = list(options[start_date-1:end_date])
    st.write(f"The period chosen goes from {MONTHS_LIST[selected_months[0]-1]} to {MONTHS_LIST[selected_months[-1]-1]}")

    return start_date, end_date

def select_data_contained_in_season(data, season_start, season_end):
    """
    Filters the input data to select rows where the month is within the specified season range.

    Args:
        data (DataFrame): A pandas DataFrame with a DateTime index.
        season_start (int): The starting month of the season (1 for January, 12 for December).
        season_end (int): The ending month of the season (1 for January, 12 for December).

    Returns:
        DataFrame: A filtered DataFrame containing only the data for the selected season (month range).
    """
    return data[(data.index.month >= season_start) & (data.index.month <= season_end)].copy()

def upload_csv_file():
    """
    Allows the user to upload a CSV file and returns the content as a pandas DataFrame.
    
    Returns:
        pd.DataFrame: The loaded DataFrame if a file is uploaded, else None.
    """
    uploaded_file = st.file_uploader("Upload an Excel file", type="xlsx")
    if uploaded_file is not None:
        try:
            data = pd.read_excel(uploaded_file)
            for index, row in data.iterrows():
                for col in data.columns:
                    if "List" in col:
                        data.at[index, col] = ast.literal_eval(row[col])
            for index, row in data.iterrows():
                for col in data.columns:

               
                    print(f"  {col}: {row[col]} ({type(row[col])})")
                
            st.success("File uploaded successfully!")
    
            return data
        except Exception as e:
            st.error(f"Error reading the file: {e}")
            return None
    else:
        st.info("Please upload a CSV file.")
        return None
    
def fill_df_checkbox(df: pd.DataFrame):
    """
    Fills the df_checkbox Dataframe corresponding to the df content.

    Args:
        df (pd.DataFrame): The DataFrame containing the indicators.
        
    Returns:
        pd.DataFrame: The df_checkbox DataFrame with the same index as df.

    """
    # Initialize the df_checkbox DataFrame with the same index as df
    
    df_checkbox = st.session_state.df_checkbox
    
    # Initialize all checkboxes to False
    for index, row in df.iterrows():
        df_checkbox.at[index, "min_daily_checkbox"] = pd.notna(row.get("Daily Threshold Min"))
        df_checkbox.at[index, "max_daily_checkbox"] = pd.notna(row.get("Daily Threshold Max"))
        df_checkbox.at[index, "min_yearly_checkbox"] = pd.notna(row.get("Yearly Threshold Min"))
        df_checkbox.at[index, "max_yearly_checkbox"] = pd.notna(row.get("Yearly Threshold Max"))
        df_checkbox.at[index, "shift_start_checkbox"] = pd.notna(row.get("Season Start Shift"))
        df_checkbox.at[index, "shift_end_checkbox"] = pd.notna(row.get("Season End Shift"))
        df_checkbox.at[index, "threshold_list_checkbox_min"] = pd.notna(row.get("Yearly Threshold Min"))
        df_checkbox.at[index, "threshold_list_checkbox_max"] = pd.notna(row.get("Yearly Threshold Max"))

    return df_checkbox

def indicator_building(df_chosen:pd.DataFrame, season_start, season_end):
    """
    Handles the creation of indicators based on user input.

    Args:
        df_chosen (DataFrame): The selected data for which indicators will be created.
        season_start (int): Starting month of the season.
        season_end (int): Ending month of the season.
    """
    # st.subheader("Create indicators")
    # with st.expander("Indicator template",expanded=False):
        
    indicator_type = general_information(df_chosen)


    if indicator_type in ["Outlier Days", "Consecutive Outlier Days"]:
        create_daily_threshold_input()
        create_yearly_thresholds_input()
    elif indicator_type == "Sliding Windows Aggregation":
        create_rolling_window_input()
        create_yearly_thresholds_input()
    elif indicator_type == "Season Aggregation":
        create_yearly_thresholds_input()

    # Crossed variable indicator or not
    if indicator_type == "Crossed Variables":
        create_built_indicator()
    else: 
        create_yearly_aggregation()
    if season_start is not None and season_end is not None:
        create_season_shift_input(season_start, season_end)

    # Buttons
    create_buttons()

def indicator_management(df):
    """Basic Streamlit app with a title."""
    key = "indicator_part"
    set_title_2("Period")

    # User setting the periods of interest
    long_period = (long_period_start, long_period_end) = select_period(key=key)
    smaller_period_length  = st.select_slider("Choose the length of smaller period to see the evolution of your data on them:",
                                              options=PERIOD_LENGTH, 
                                              key=f"smaller_period{key}")
    periods = split_into_periods_indicators(smaller_period_length, long_period_start, long_period_end)

    # Loading data and applying first filters
    all_data = df
    data_long_period_filtered = period_filter(all_data, period=long_period)
    st.dataframe(data_long_period_filtered, height=DATAFRAME_HEIGHT, use_container_width=True)
    
    # Propose variables related to the dataset loaded 
    set_title_2("Variable Choice")
    df_chosen = column_choice(data_long_period_filtered)

    # Variables intitialization
    season_start, season_end = None, None
    all_year_data = pd.DataFrame()

    if not df_chosen.empty:
        st.dataframe(df_chosen, height=DATAFRAME_HEIGHT, use_container_width=True)
        all_year_data = df_chosen  

        # Season handdling
        set_title_2("Season Choice")
        if st.checkbox("Need a season or a period study", value=st.session_state.season_checkbox):
            season_start, season_end = select_season()
            df_season = select_data_contained_in_season(df_chosen, season_start, season_end)
            st.dataframe(df_season, height=DATAFRAME_HEIGHT, use_container_width=True)
        else:
            df_season = df_chosen
        
        # Indicators parametrization handling
        set_title_2("Parametrize Indicators")

        # Load indicators from CSV
        if st.checkbox(label="Load indicators from CSV"):
            df_uploaded = upload_csv_file()
            
            if df_uploaded is not None and not df_uploaded.equals(st.session_state.uploaded_df):
                df_checkbox = fill_df_checkbox(df_uploaded)
                st.session_state.uploaded_df = df_uploaded
                st.session_state.df_indicators = copy(df_uploaded)
                st.session_state.df_checkbox = df_checkbox

        # Building the indicator in a popover
        with st.popover("Create Indicator", use_container_width = True):
            indicator_building(df_season, season_start, season_end)

        # Avec un popover, il faut pouvoir update