from utils.imports import *

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

    return df_checkbox
    

def download_indicators(df: pd.DataFrame, filename="indicators.xlsx"):
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
        writer._save()
        buffer.seek(0)  # Reset buffer pointer to the start

    # Create a download button in Streamlit
    st.download_button(
        label="Download Indicators",
        data=buffer,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )