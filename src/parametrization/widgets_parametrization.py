from src.utils.imports import *
from src.lib.session_variables import reset_df_indicators

# ----------------------------------------------------------------
# --- All the widgets needed for the indicator parametrization ---
# ----------------------------------------------------------------

def select_period(key):
    """
    Allows the user to select a data period using an interactive Streamlit slider.

    Returns:
        tuple: The start and end values of the selected period.
    """
    # Define the initial limits for the slider
    min_year, max_year = st.session_state.min_year, st.session_state.max_year
    if st.session_state.last_page != "Indicator Parametrization":
        if st.session_state.long_period is not None:
            period_start, period_end = st.session_state.long_period
        else: period_start, period_end = min_year, max_year


    else:
        period_start, period_end = (min_year, max_year)
    
    st.session_state.last_page = "Indicator Parametrization"
    # Display the slider that allows the user to select the bounds
    period_start, period_end = st.slider(
        "Select the data period:",
        min_value=min_year, 
        max_value=max_year,
        value=(period_start, period_end),
        key=key)
    return period_start, period_end



def variable_choice(data : pd.DataFrame):
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
    if st.checkbox("All variables"):
        st.session_state.variable_chosen = st.multiselect("Chose variable of interest", options=columns_list, default=columns_list)
    else:
        st.session_state.variable_chosen = st.multiselect("Chose variable of interest", options=columns_list)
    variable_chosen = st.session_state.variable_chosen

    # Restrict the dataframe to the user selected columns
    df_final = data[variable_chosen]

    return df_final

def select_season(months_list):
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
        format_func=lambda x:months_list[x-1]  # Displays full month name, day, and year
    )
    # Display the selected range
    selected_months = list(options[start_date-1:end_date])
    st.write(f"The period chosen goes from {months_list[selected_months[0]-1]} to {months_list[selected_months[-1]-1]}")

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
                    # print(row[col])
                    if isinstance(row[col], str) and row[col][0] == "[":
                        data.at[index, col] = ast.literal_eval(row[col])
                
            st.success("File uploaded successfully!")
    
            return data
        except Exception as e:
            st.error(f"Error reading the file: {e}")
            return None
    else:
        st.info("Please upload a CSV file.")
        st.session_state.uploaded_df = None
        return None
    

def download_indicators(df: pd.DataFrame, filename):
    """
    Creates a download button for the indicators DataFrame in Streamlit in excel format.

    Args:
        df (pd.DataFrame): DataFrame containing the indicators.
        filename (str): The name of the file to be downloaded.
    """
    # Use an in-memory buffer to save the Excel file
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Indicators")
    buffer.seek(0)  # Reset buffer pointer to the start

    # Create a download button in Streamlit
    st.download_button(
        label="Download Indicators",
        data=buffer,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

def delete_all_indicators():
    """
    Deletes all the indicators stored in the session state.
    """
    st.button("Delete all indicators", on_click=reset_df_indicators,use_container_width=True)

