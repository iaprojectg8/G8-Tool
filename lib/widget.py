from utils.imports import *
from utils.variables import *

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


def display_thresholds(updated_indicator, label):
    """
    Displays the thresholds with the corresponding colors.

    Args:
        updated_indicator (dict): The updated indicator.
        label (str): The label of the indicator.
    """
    thresholds : list = copy(updated_indicator[label + " List"])
    # Define thresholds and corresponding data

    colors = THRESHOLD_COLORS
  
    # Risk band visualization
    fig = go.Figure()
    
    thresholds.append(min(thresholds) - (thresholds[1]-thresholds[0]))
    thresholds.append(max(thresholds) + (thresholds[1]-thresholds[0]))
    print(thresholds)

    if "min" in label.lower():
        colors = colors[::-1]
        thresholds.sort()

    else:
        thresholds.sort()

    print(colors)
    print(len)
    # Add horizontal colored bands
    for i in range(0,len(thresholds)-1):
        start = thresholds[i] 
        end = thresholds[i+1]
        fig.add_shape(
            type="rect",
            x0=start, x1=end,
            y0=0, y1=3,
            fillcolor=colors[i],
            opacity=0.6,
            line_width=0
        )
        # Add text labels for each band
        fig.add_trace(go.Scatter(
            x=[(start + end) / 2],
            y=[1.5],
            text=RISK_MAP[colors[i]],
            mode="text",
            textfont=dict(color="white", size=14)
        ))


    # Update layout
    fig.update_layout(
        title="Risk Levels Based on Thresholds",
        yaxis=dict(visible=False),  # Hide the y-axis
        height=220,
        showlegend=False
    )

    st.plotly_chart(fig)
    

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
    buffer.seek(0)  # Reset buffer pointer to the start

    # Create a download button in Streamlit
    st.download_button(
        label="Download Indicators",
        data=buffer,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )