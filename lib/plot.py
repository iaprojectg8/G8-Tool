from utils.imports import *
from utils.variables import *

# ---------------------------------------------------------------
# --- Calculation and data process function done for the plot ---
# ---------------------------------------------------------------

def add_periods_to_df(df:pd.DataFrame, periods):
    """
    Assigns a period to each row in the DataFrame based on the 'year' column.

    Args:
        df (pd.DataFrame): The input DataFrame containing a 'year' column.
        periods (list of tuples): A list of periods, where each period is a tuple (start_year, end_year).

    Returns:
        pd.DataFrame: The DataFrame with an additional 'period' column indicating the assigned period.
    """
    # Assign the first matching period to each 'year' using the next() function that iterates over periods
    df["period"] = df["year"].apply(lambda x: next((period for period in periods if period[0] <= x <= period[1]), None))
    return df

def add_month_name_to_df(df):
    """
    Adds a 'month_name' column to the DataFrame based on the numeric 'month' column.

    Args:
        df (pd.DataFrame): The input DataFrame containing a 'month' column (1 to 12).

    Returns:
        pd.DataFrame: The DataFrame with an additional 'month_name' column.
    """
    df["month_name"] = df["month"].apply(lambda x:MONTHS_LIST[int(x-1)])
    return df

def calculate_mothly_mean_through_year(data:pd.DataFrame, periods):
    """
    Calculates the monthly mean or sum for different variables over a range of years and periods.

    Args:
        data (pd.DataFrame): The input DataFrame with a datetime index and relevant variables.
        periods (list of tuples): List of periods, where each period is a tuple (start_year, end_year).

    Returns:
        tuple: 
            - monthly_data (pd.DataFrame): Monthly average values for each month across all years.
            - monthly_mean (pd.DataFrame): Monthly mean values along with corresponding periods and metadata for plotting.
    """
    # Add month and year colums to the dataframe
    data["month"] = data.index.month
    data["year"] = data.index.year

    # Aggreagate the data in different way following the variable
    monthly_mean = data.resample("ME").agg({
        **{col: "mean" for col in data.columns if "precipitation" not in col.lower()},
        **{col: "sum" for col in data.columns if "precipitation" in col.lower()}
    })

    # Group the data by month so as to take the mean for each month on the whole range of years
    monthly_data = monthly_mean.groupby("month").mean().reset_index()
    monthly_data = add_month_name_to_df(monthly_data)

    # Adding month name and periods to the monthly mean dataframe
    monthly_mean = add_month_name_to_df(monthly_mean)
    monthly_mean =  add_periods_to_df(monthly_mean, periods)

    # These two lines are exlusively to improve the plot layout
    monthly_mean["period_index"] = monthly_mean["period"].apply(lambda p: periods.index(p))
    monthly_mean["customdata"] = monthly_mean["period"].apply(lambda x: "-".join([str(list(x)[0]),str(list(x)[1])]))

    return monthly_data, monthly_mean

def calculate_yearly_mean_through_year(data:pd.DataFrame, periods):
    """
    Calculates the yearly mean or sum for different variables over a range of years and periods.

    Args:
        data (pd.DataFrame): The input DataFrame with a datetime index and relevant variables.
        periods (list of tuples): List of periods, where each period is a tuple (start_year, end_year).

    Returns:
        pd.DataFrame: DataFrame with yearly mean or sum values and corresponding periods.
    """

    # Add the year column to the dataframe
    data["year"] = data.index.year 

    # Same as before but instead of monthly aggregation, a yearly aggregation is done
    yearly_mean = data.resample("YE").agg({
        **{col: "mean" for col in data.columns if "precipitation" not in col.lower()},
        **{col: "sum" for col in data.columns if "precipitation" in col.lower()}
    })  
    yearly_mean = add_periods_to_df(yearly_mean, periods)

    return yearly_mean

# --------------------
# --- Monthly plot ---
# --------------------

def mean_line_monthly_plot(fig:go.Figure, monthly_data, column):
    """
    Adds a line plot for the monthly mean over the years to the given figure.

    Args:
        fig (go.Figure): The Plotly figure object to which the plot will be added.
        monthly_data (pd.DataFrame): The DataFrame containing monthly data.
        column (str): The column name for which the monthly mean is plotted.
    """
    fig.add_trace(go.Scatter(
        x=monthly_data["month_name"], 
        name="Monthly mean over years", 
        y=monthly_data[column], 
        mode='lines', 
        line=dict(color='blue')
    ))

def monthly_scatter(fig: go.Figure, monthly_mean, column, unit):
    """
    Adds a scatter plot for monthly means with markers to the given figure.

    Args:
        fig (go.Figure): The Plotly figure object to which the plot will be added.
        monthly_mean (pd.DataFrame): The DataFrame containing the monthly mean values.
        column (str): The column name to plot.
        unit (str): The unit of measurement for the variable being plotted.
    """
    fig.add_trace(go.Scatter(
        x=monthly_mean['month_name'],
        y=monthly_mean[column],
        name="Month mean", 
        mode='markers',
        marker=dict(
            size=10,
            color=monthly_mean["period_index"],  # Color by the period_index
            colorscale="agsunset_r",  # Use correct colorscale name
            showscale=True,  # Show color scale
            opacity=0.5,
            line_width=1,
            line_color="black",
            colorbar=dict(
                title="Periods",
                title_side="right", 
                ticktext=monthly_mean["customdata"].unique(), 
                tickvals=monthly_mean["period_index"].unique(), 
                orientation="v",  
                len=1, 
                thickness=15, 
                borderwidth=1,
                x=1.05,  
                y=0.35)),
        text=monthly_mean["year"],
        customdata= monthly_mean["customdata"],
        hovertemplate=(
            f"Temperature: %{{y:.2f}} {unit}<br>" +
            "Year: %{text}<br>"+
            "Decade: %{customdata}<br>"
        ),
        showlegend=False))

def layout_monthly_plot(fig:go.Figure, variable):
    """
    Updates the layout of the Plotly figure for the monthly plot.

    Args:
        fig (go.Figure): The Plotly figure to update.
        variable (str): The name of the variable being plotted, used for title and axis labels.
    """
    fig.update_layout(
        width=1500, height=500,
        title=dict(text=f'Monthly Mean {variable} through years',
                x=0.5,
                xanchor="center",
                font_size=25),
        xaxis_title='Month',
        yaxis_title=f'{variable} - {UNIT_DICT[variable]}',
        legend_title='',
        template='plotly_dark',
        autosize=True,
        hoverlabel_align="auto"
    )

def plot_monthly_mean(column, monthly_mean, monthly_data):
    """
    Creates and displays a monthly mean plot for a specified column.

    Args:
        column (str): The column name for which the monthly mean plot is created.
        monthly_mean (pd.DataFrame): DataFrame containing the monthly mean values.
        monthly_data (pd.DataFrame): DataFrame containing the original monthly data for plotting.

    Returns:
        go.Figure: The Plotly figure with the monthly mean plot.
    """
    fig = go.Figure()

    # Mean blue line
    mean_line_monthly_plot(fig, monthly_data, column)

    # Get the variable name corresponding to the column
    variable = [variable for variable in AVAILABLE_VARIABLES if "_".join(variable.lower().split()) in column][0]
    unit=UNIT_DICT[variable]

    # Make the monthly plot
    monthly_scatter(fig, monthly_mean, column, unit)
    layout_monthly_plot(fig, variable)
    
    # Display the plot in Streamlit
    st.plotly_chart(fig)
    return fig

# -------------------
# --- Yearly plot ---
# -------------------

def get_period_trend(df : pd.DataFrame,column, start, stop):
    """
    Calculates the trend line (slope and intercept) for a specified period based on linear regression.

    Args:
        df (pd.DataFrame): DataFrame containing the data.
        column (str): The column name for which the trend is calculated.
        start (int): The start year of the period.
        stop (int): The end year of the period.

    Returns:
        tuple: A tuple containing the trend line values and the corresponding years.
    """
    # Get the data for the corresponding period interval
    df = df[(df["year"] >= start) & (df["year"]<= stop) ]

    if not df.empty:
        # Get the years and the values
        years = np.array(df["year"])
        annual_values = df[column]

        # Creating the parameters for the line, only slope and intercept will be useful in our case
        slope, intercept, _ , _ , _ = linregress(years, annual_values)
        print("Line slope:",slope)
        
        # Create the trend using the line parameters got
        trend_line = slope * years + intercept
        return trend_line, years

def build_trend_plot(year_mean_df, periods, column):
    """
    Builds the trend lines for multiple periods.

    Args:
        year_mean_df (pd.DataFrame): DataFrame containing the yearly mean data.
        periods (list of tuples): List of tuples, each representing a start and end year for a period.
        column (str): The column name for which the trends are calculated.

    Returns:
        tuple: A tuple containing the list of trend lines and corresponding years for each period.
    """
    trend_lines = []
    years_all = []
    
    # Loop to go through each period in order to get the trend line for them
    for period in periods: 
        start, end = period
        if start != end:
            print(start, end)
            trend_line, years = get_period_trend(year_mean_df,column, int(start), int(end))
            trend_lines.append(trend_line)
            years_all.append(years)
        
    return trend_lines, years_all


def plot_yearly_curve(fig:go.Figure, yearly_mean, column, variable):
    """
    Adds a line plot for the yearly mean of a variable to the figure.

    Args:
        fig (go.Figure): The Plotly figure to which the trace will be added.
        yearly_mean (pd.DataFrame): DataFrame containing the yearly mean values.
        column (str): The column name for which the yearly mean is plotted.
        variable (str): The variable name for the title and axis labels.
    """
    fig.add_trace(go.Scatter(
        x=yearly_mean["year"],
        y=yearly_mean[column],
        mode='lines',
        name=f"Year Average {variable}",
        line=dict(color="blue"),
    ))

def yearly_layout(fig:go.Figure, variable):
    """
    Updates the layout of the Plotly figure for the yearly curve plot.

    Args:
        fig (go.Figure): The Plotly figure to update.
        variable (str): The variable name used for title and axis labels.
    """
    fig.update_layout(
        width=1500, height=500,
        title=dict(text=f'Mean Year {variable} and Trends from Different Periods',
                    x=0.5,
                    xanchor="center",
                    font_size=25),
        xaxis_title="Year",
        yaxis_title=f"{variable} - {UNIT_DICT[variable]}",
        autosize=True,
        template='plotly_dark',
        showlegend=True,
        legend=dict(
            orientation="v",  # Horizontal orientation
            x=1.05,            # Center the legend horizontally
            y=0.5,           # Position the legend below the plot (adjust as needed)
        )
    )

def plot_all_trend_lines(fig:go.Figure, yearly_mean, periods, column, variable):
    """
    Adds multiple trend lines for different periods to the figure.

    Args:
        fig (go.Figure): The Plotly figure to which the trend lines will be added.
        yearly_mean (pd.DataFrame): DataFrame containing the yearly mean data.
        periods (list of tuples): List of periods (start, end) for which trends are calculated.
        column (str): The column name for which the trend lines are plotted.
        variable (str): The variable name for labeling and title purposes.
    """
    trend_lines, years_all = build_trend_plot(yearly_mean, periods, column)
    colorscale = px.colors.sequential.YlOrRd  # Choose the desired colorscale
    num_trends = len(trend_lines)
    color_indices = np.linspace(0, 1, num_trends)  # Generate equally spaced values between 0 and 1

    for i, trend_line in enumerate(trend_lines):
        color = px.colors.sample_colorscale(colorscale, color_indices[i])[0]  # Extract the color string
        fig.add_trace(go.Scatter(
            x=years_all[i],
            y=trend_line,
            mode='lines',
            name=f"{periods[i][0]}-{periods[i][1]} {variable} Trend",
            line=dict(color=color),
        ))

def plot_yearly_curve_and_period_trends(yearly_mean, column, periods):
    """
    Plots the yearly curve along with trend lines for different periods.

    Args:
        yearly_mean (pd.DataFrame): DataFrame containing the yearly mean data.
        column (str): The column name for which the yearly curve and trends are plotted.
        periods (list of tuples): List of periods (start, end) for which trends are calculated.

    Returns:
        go.Figure: The Plotly figure containing the yearly curve and trend lines.
    """
    fig = go.Figure()

    variable = [variable for variable in AVAILABLE_VARIABLES if "_".join(variable.lower().split()) in column][0]

    # Plot yearly curve and trend lines
    plot_yearly_curve(fig, yearly_mean, column, variable)
    plot_all_trend_lines(fig, yearly_mean, periods, column, variable)

    # Update layout with titles and labels
    yearly_layout(fig, variable)
    st.plotly_chart(fig)

    return fig

# --------------------------------
# --- Monthly period variation ---
# --------------------------------
def change_color_scale(color_scale_reversed, color_scale):
    """
    Modifies the color scale by appending '_r' to reverse it if specified.

    Args:
        color_scale_reversed (bool): Whether the color scale should be reversed.
        color_scale (str): The original color scale.

    Returns:
        str: The modified color scale (reversed if applicable).
    """
    if color_scale_reversed:
        color_scale+="_r"
    return color_scale

def modify_differences(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Replace small variations in the 'difference' column with 0.

    Args:
        df (pd.DataFrame): DataFrame containing the difference column.
        column (str): Column name where small variations will be replaced.

    Returns:
        pd.DataFrame: Modified DataFrame with small variations set to 0.
    """
    
    max_variation = df[column].abs().max()
    threshold = VARIATION_THRESHOLD * max_variation  # 5% of the max variation
    df[column] = df[column].apply(lambda x: 0 if abs(x) < threshold else x)
    return df


def monthly_variation_calculation(monthly_mean, monthly_data, column):
    """
    Calculates the difference between the mean value of a specified column 
    across periods and the overall mean for each month.

    Args:
        monthly_mean (pd.DataFrame): DataFrame containing period-specific means.
        monthly_data (pd.DataFrame): DataFrame containing overall monthly data.
        column (str): The column for which differences are calculated.

    Returns:
        pd.DataFrame: A DataFrame with the calculated differences and period names.
    """
    # Group by period and month, and calculate the mean for the specified column
    monthly_mean = (
        monthly_mean.groupby(["period", "month"])
        .agg({column: "mean"})
        .reset_index()
    )

    # Merge the period-specific mean with overall monthly data
    monthly_mean = monthly_mean.merge(monthly_data, on="month", suffixes=("_period", "_overall"))

    # Calculate the difference between period-specific and overall mean
    monthly_mean["difference"] = monthly_mean[column + "_period"] - monthly_mean[column + "_overall"]
    # monthly_mean = modify_differences(monthly_mean, "difference")

    # Create a human-readable period name (e.g., "2020-2022")
    monthly_mean["period_name"] = monthly_mean["period"].apply(lambda x: f"{x[0]}-{x[1]}")

    return monthly_mean


def monthly_variation_plot(fig:go.Figure, monthly_mean, unit, color_scale, variable):
    """
    Adds a heatmap trace to the figure showing the variation of a specified variable.

    Args:
        fig (go.Figure): The Plotly figure to update.
        monthly_mean (pd.DataFrame): DataFrame containing the monthly variations.
        unit (str): Unit of the variable being plotted.
        color_scale (str): Color scale used for the heatmap.
        variable (str): The variable name.
    """
    colorscale = px.colors.diverging.Spectral
    print(type(colorscale))
    # custom_colorscale = [
    #     [0, colorscale[0]],  # Start of the original colorscale
    #     [0.4999999999999999, colorscale[4]],
    #     [0.5, 'rgb(169,169,169)'],        # Midpoint
    #     [0.5000000000000001, colorscale[4]],
    #     [1, colorscale[-1]]           # Full color scale
    # ]
    fig.add_trace(go.Heatmap(
        name=f"",
        z=round(monthly_mean["difference"],3),
        zmid = 0,
        x=monthly_mean["month_name"],  # Months
        y=monthly_mean["period_name"],    # Periods
        colorbar=dict(title=f"Difference {unit}"),
        colorscale=color_scale,
        connectgaps=False,
        hovertemplate=(
            "Month:  %{x}<br>" +
            "Period: %{y}<br>"+
            f"{variable} "+"Variation: %{z}"+f" {unit}"
        ),
    ))

def monthly_variation_layout(fig:go.Figure, graph_part, variable):
    """
    Updates the layout of the Plotly figure to customize its appearance.

    Args:
        fig (go.Figure): The Plotly figure to update.
        graph_part (float): Proportion of the layout width allocated to the graph.
        variable (str): The variable being plotted, used for the title.
    """
    fig.update_layout(
        width=1500*graph_part, height=1000*graph_part,
        title=dict(text=f"Monthly {variable} Variation over Periods ",
                    x=0.5,
                    xanchor="center",
                    font_size=25),
        autosize=True,
        template='plotly_dark',
        showlegend=True,
        xaxis=dict(tickfont_size=15,
                    title = dict(
                        text="Month",
                        font_size=17,
                        standoff=50),       
                    ticklabelstandoff =20),
        yaxis=dict(tickfont_size=15,
                    title=dict(
                        text="Year",
                        font_size=17,
                        standoff=50),
                    ticklabelstandoff = 20),
        legend=dict(
            orientation="v", 
            x=1.05,            
            y=0.5),
        font=dict(
            size=17),
        )

def plot_monthly_period_variation(monthly_mean: pd.DataFrame, monthly_data: pd.DataFrame, column: str) -> go.Figure:
    """
    Main function to calculate and plot the monthly variation for a given column.

    Args:
        monthly_mean (pd.DataFrame): DataFrame containing period-specific data.
        monthly_data (pd.DataFrame): DataFrame containing overall monthly data.
        column (str): The column to analyze.

    Returns:
        go.Figure: The Plotly figure displaying the heatmap.
    """
    graph_part = 0.85  # Proportion of the layout for the graph
    col1, col2 = st.columns([1 - graph_part, graph_part], vertical_alignment="center")

    # Sidebar for color scale selection and reversing
    with col1:
        color_scale = st.selectbox("Choose the colorscale you want", options=COLORSCALE)
        color_scale_reversed = st.checkbox("Reverse the colorscale")
        color_scale = change_color_scale(color_scale_reversed, color_scale)

    # Initialize the Plotly figure
    fig = go.Figure()

    # Determine the variable name and unit from the column name
    variable = [v for v in AVAILABLE_VARIABLES if "_".join(v.lower().split()) in column][0]
    unit = UNIT_DICT[variable]

    # Calculate the monthly variation
    monthly_mean = monthly_variation_calculation(monthly_mean, monthly_data, column)

    # Plot the heatmap and update layout
    monthly_variation_plot(fig, monthly_mean, unit, color_scale, variable)
    monthly_variation_layout(fig, graph_part, variable)

    # Display the figure on the right
    with col2:
        st.plotly_chart(fig)

    return fig

# --------------------
# --- PDF filling  ---
# --------------------


def wrap_into_pdf(fig1, fig2, fig3):
    """
    Wraps two Plotly figures into a PDF file with a black background and landscape layout.

    Args:
        fig1 (go.Figure): The first Plotly figure to be included in the PDF.
        fig2 (go.Figure): The second Plotly figure to be included in the PDF.
        fig3 (go.Figure): The second Plotly figure to be included in the PDF.

    Returns:
        bytes: The PDF content as bytes.
    """
    # Create an in-memory buffer to store the PDF content
    pdf_buffer = BytesIO()

    # Initialize the PDF canvas with landscape orientation A4 size
    c = canvas.Canvas(pdf_buffer, pagesize=landscape(A4))

    # Set the background color to black
    c.setFillColorRGB(0, 0, 0)
    c.rect(0, 0, 892, 612, fill=1)  # Fill the entire page with black color

    # Convert the Plotly figures to PNG images in memory using kaleido
    fig1_image = pio.to_image(fig1, format="jpg", width=fig1.layout.width, height=fig1.layout.height)
    fig2_image = pio.to_image(fig2, format="jpg", width=fig2.layout.width, height=fig2.layout.height)
    fig3_image = pio.to_image(fig3, format="jpg", width=fig3.layout.width, height=fig3.layout.height)

    # Create ImageReader objects for the figures' image data
    img1_reader = ImageReader(BytesIO(fig1_image))
    img2_reader = ImageReader(BytesIO(fig2_image))
    img3_reader = ImageReader(BytesIO(fig3_image))

    # Place the first figure image on the PDF at a specific location with scaled dimensions
    c.drawImage(img1_reader, x=-330, y=320, height=fig1.layout.height / 2, width=fig1.layout.width, preserveAspectRatio=True)
    
    # Place the second figure image on the PDF at a specific location with scaled dimensions
    c.drawImage(img2_reader, x=-330, y=20, height=fig2.layout.height / 2, width=fig2.layout.width, preserveAspectRatio=True)
    c.showPage()
    c.rect(0, 0, 892, 612, fill=1)  # Fill the entire page with black color
    c.drawImage(img3_reader, x=-220, y=40, height=fig3.layout.height*0.60, width=fig3.layout.width, preserveAspectRatio=True)
    # Finalize the PDF document
    c.save()

    # Retrieve the content of the PDF from the buffer
    pdf_buffer.seek(0)
    pdf_bytes = pdf_buffer.read()

    # Close the buffer and return the PDF bytes
    pdf_buffer.close()

    return pdf_bytes


# --------------------------
# --- Main plot function ---
# --------------------------

def general_plot(data: pd.DataFrame, periods, chosen_variable, filename):
    """
    Generates a plot for the selected variable and period, including monthly and yearly means,
    trends, and the option to download the plots as a PDF.

    Args:
        data (pd.DataFrame): The input data frame containing the data to plot.
        periods (list): List of tuples representing the periods to analyze (start year, end year).
        chosen_variable (list): List of available variable options for the user to choose from.

    Returns:
        None: The function generates plots and provides a download button for the PDF.
    """
    # Define columns to keep from the original dataframe
    columns_to_keep = data.columns

    # Calculate monthly and yearly mean data
    monthly_data, monthly_mean = calculate_mothly_mean_through_year(copy(data), periods)
    yearly_mean = calculate_yearly_mean_through_year(data, periods)
    
    # Create a select box for users to choose the variable they want to plot
    variable_choice = st.selectbox("Choose the variable on which you want to see the plot", options=chosen_variable)
    
    # Loop through columns to find and plot data matching the selected variable
    for column in data.columns:
        if column in columns_to_keep and "min" not in column and "max" not in column and "_".join(variable_choice.lower().split(" ")) in column:
            
            # Generate the monthly and yearly plots for the selected column
            fig1 = plot_monthly_mean(column, monthly_mean, monthly_data)
            fig2 = plot_yearly_curve_and_period_trends(yearly_mean, column, periods)
            fig3 = plot_monthly_period_variation(monthly_mean,monthly_data, column)

            
            # Generate the PDF with the two figures
            pdf = wrap_into_pdf(fig1, fig2, fig3)

            # Provide a button to download the generated PDF
            st.download_button(
                label="Download PDF",
                data=pdf,
                file_name=f"{filename}_{variable_choice}.pdf",
                mime="application/pdf"
            )

        