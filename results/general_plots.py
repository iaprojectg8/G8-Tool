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

def add_month_name_to_df(df:pd.DataFrame):
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
        line=dict(color='dodgerblue')
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
    colorscale = px.colors.sequential.Agsunset_r  # Use the desired part of the colorscale
    num_colors = 100
    color_indices = np.linspace(0, 1, num_colors)

    # Sample the colorscale
    extended_colorscale = px.colors.sample_colorscale(colorscale, color_indices)[1:-16]
    fig.add_trace(go.Scatter(
        x=monthly_mean['month_name'],
        y=monthly_mean[column],
        name="Month mean", 
        mode='markers',
        marker=dict(
            size=10,
            color=monthly_mean["period_index"],  # Color by the period_index
            colorscale=extended_colorscale,  # Use correct colorscale name
            showscale=True,  # Show color scale
            opacity=1,
            line_width=0.2,
            line_color="black",
            colorbar=dict(
                title="Periods",
                title_side="right", 
                ticktext=monthly_mean["customdata"].unique(), 
                tickvals=monthly_mean["period_index"].unique(), 
                orientation="v",  
                len=0.8, 
                thickness=25, 
                tickfont=dict(size=14),
                borderwidth=1,
                x=1.05,  
                y=0.35)),
        text=monthly_mean["year"],
        customdata= monthly_mean["customdata"],
        hovertemplate=(
            f"Temperature: %{{y:.2f}} {unit}<br>" +
            "Year: %{text}<br>"+
            "Period: %{customdata}<br>"
        ),
        showlegend=False))
    
def plot_current_year(fig:go.Figure, monthly_mean, column, unit, year=datetime.now().year):
    fig.add_trace(go.Scatter(
        x=monthly_mean.loc[monthly_mean["year"] == year, 'month_name'],  # Filter for 2025
        y=monthly_mean.loc[monthly_mean["year"] == year, column],  # Filter for 2025
        name=f"{year} Curve",  # Legend name
        mode='lines+markers',  # Line and markers
        line=dict(color='limegreen', width=2, dash='solid'),  # Customize the line appearance
        marker=dict(size=5, color='limegreen'),  # Marker customization
        hoveron='points+fills',  # Enable hover on both markers and the line
        hovertemplate=(
            f"Temperature: %{{y:.2f}} {unit}<br>" +
            f"Year: {year}<br>" +
            "Month: %{x}<br>"
        ),
        showlegend=True  # Show this in the legend
    ))

def layout_monthly_plot(fig:go.Figure, column_name,  unit):
    """
    Updates the layout of the Plotly figure for the monthly plot.

    Args:
        fig (go.Figure): The Plotly figure to update.
        variable (str): The name of the variable being plotted, used for title and axis labels.
    """
    mean  = "Mean "
    fig.update_layout(
        width=1500, height=500,
        title=dict(text=f'Monthly {mean if column_name != "Precipitation Sum" else ''}{column_name} through years',
                x=0.5,
                xanchor="center",
                font_size=25),
        xaxis_title='Month',
        yaxis_title=f'{column_name} - {unit}',
        legend_title='',
        template=TEMPLATE_COLOR,
        autosize=True,
        hoverlabel_align="auto",
        font=dict(size=17, weight=800),
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
    unit = UNIT_DICT[column]
    column_name = " ".join(column.split("_")).title()

    # Make the monthly plot
    monthly_scatter(fig, monthly_mean, column, unit)
    plot_current_year(fig, monthly_mean, column, unit)
    layout_monthly_plot(fig, column_name, unit)
    
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
        
        # Create the trend using the line parameters got
        trend_line = slope * years + intercept
        return trend_line, years, slope

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
    slopes = []
    
    # Loop to go through each period in order to get the trend line for them
    for period in periods: 
        start, end = period
        if start != end:
            trend_line, years, slope = get_period_trend(year_mean_df,column, int(start), int(end))
            trend_lines.append(trend_line)
            years_all.append(years)
            slopes.append(slope)
        
    return trend_lines, years_all, slopes


def plot_yearly_curve(fig:go.Figure, yearly_mean, column, column_name):
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
        name=f"Year Average",
        line=dict(color="dodgerblue"),
    ))

def yearly_layout(fig:go.Figure, column_name, unit):
    """
    Updates the layout of the Plotly figure for the yearly curve plot.

    Args:
        fig (go.Figure): The Plotly figure to update.
        column_name (str): The column name used for title and axis labels.
        unit (str) : The unit that corresponds to the variable ploted
    """
    mean = "Mean "
    fig.update_layout(
        width=1500, height=500,
        title=dict(text=f'Yearly {mean if column_name != "Precipitation Sum" else ''}{column_name} and Trends from Different Periods',
                    x=0.5,
                    xanchor="center",
                    font_size=25),
        xaxis_title="Year",
        yaxis_title=f"{column_name} - {unit}",
        template=TEMPLATE_COLOR,
        autosize=True,
        showlegend=True,
        legend=dict(
            orientation="v",  # Horizontal orientation
            x=1.05,            # Center the legend horizontally
            y=0.5,           # Position the legend below the plot (adjust as needed)
        ),
        font=dict(size=17, weight=800)
    )

def plot_all_trend_lines(fig:go.Figure, yearly_mean, monthly_mean, periods, column, column_name, unit):
    """
    Adds multiple trend lines for different periods to the figure.

    Args:
        fig (go.Figure): The Plotly figure to which the trend lines will be added.
        yearly_mean (pd.DataFrame): DataFrame containing yearly mean data.
        monthly_mean (pd.Dataframe) : Dataframe containing monthly mean data 
        periods (list of tuples): List of periods (start, end) for which trends are calculated.
        column (str): The column name for which the trend lines are plotted.
        column_name (str): The column name for labeling and title purposes.
        unit (str): The unit that corresponds to the variables ploted
    """
    trend_lines, years_all, slope = build_trend_plot(yearly_mean, periods, column)
    colorscale = px.colors.sequential.YlOrRd[3:-1]  # Choose the desired colorscale
    num_trends = len(trend_lines)
    color_indices = np.linspace(0, 1, num_trends)  # Generate equally spaced values between 0 and 1

    for i, trend_line in enumerate(trend_lines):
        color = px.colors.sample_colorscale(colorscale, color_indices[i])[0]  # Extract the color string
        fig.add_trace(go.Scatter(
            x=years_all[i],
            y=trend_line,
            mode='lines',
            name=f"{periods[i][0]}-{periods[i][1]} Trend",
            line=dict(color=color),
            customdata= monthly_mean["customdata"],
                hovertemplate=(
                f"Slope: {round(slope[i],3)} {unit}/year <br>" +
                f"Slope: {round(slope[i]*(periods[i][1] - periods[i][0]),3)} {unit}/period <br>" +
                f"Period: {periods[i][0]}-{periods[i][1]}<br>"
            ),
            ))

def plot_yearly_curve_and_period_trends(yearly_mean, monthly_mean, column, periods):
    """
    Plots the yearly curve along with trend lines for different periods.

    Args:
        yearly_mean (pd.DataFrame): DataFrame containing the yearly mean data.
        monthly_mean (pd.DataFrame) : Dataframe containing period-specific means.
        column (str): The column name for which the yearly curve and trends are plotted.
        periods (list of tuples): List of periods (start, end) for which trends are calculated.

    Returns:
        go.Figure: The Plotly figure containing the yearly curve and trend lines.
    """
    fig = go.Figure()
    # Initializing column name and unit for the plot's layout
    unit = UNIT_DICT[column]
    column_name = " ".join(column.split("_")).title()

    # Plot yearly curve and trend lines
    plot_yearly_curve(fig, yearly_mean, column, column_name)
    add_vertical_line(fig, year=datetime.now(pytz.utc).year)
    plot_all_trend_lines(fig, yearly_mean,monthly_mean, periods, column, column_name, unit)

    # Update layout with titles and labels
    yearly_layout(fig,column_name, unit)
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


def monthly_variation_plot(fig:go.Figure, monthly_mean, color_scale, column_name, unit):
    """
    Adds a heatmap trace to the figure showing the variation of a specified variable.

    Args:
        fig (go.Figure): The Plotly figure to update.
        monthly_mean (pd.DataFrame): DataFrame containing the monthly variations.
        color_scale (str): Color scale used for the heatmap.
        column_name (str): The column name.
        unit (str): Unit of the variable being plotted.
    """

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
            f"{column_name} "+"Variation: %{z}"+f" {unit}"
        ),
    ))

def monthly_variation_layout(fig:go.Figure, graph_part, column_name):
    """
    Updates the layout of the Plotly figure to customize its appearance.

    Args:
        fig (go.Figure): The Plotly figure to update.
        graph_part (float): Proportion of the layout width allocated to the graph.
        column_name (str): The column name being plotted, used for the title.
    """
    fig.update_layout(
        width=1500*graph_part, height=1000*graph_part,
        title=dict(text=f"Monthly {column_name} Variation over Periods ",
                    x=0.5,
                    xanchor="center",
                    font_size=25),
        autosize=True,
        template=TEMPLATE_COLOR,
        showlegend=True,
        xaxis=dict(tickfont_size=15,
                    title = dict(
                        text="Month",
                        font_size=17,
                        standoff=50),       
                    ticklabelstandoff =20),
        yaxis=dict(tickfont_size=15,
                    title=dict(
                        text="Period",
                        font_size=17,
                        standoff=50),
                    ticklabelstandoff = 20),
        legend=dict(
            orientation="v", 
            x=1.05,            
            y=0.5),
        font=dict(size=17, weight=800),
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
        color_scale_reversed = st.checkbox("Reverse the colorscale", value="temperature" in column)
        color_scale = change_color_scale(color_scale_reversed, color_scale)

    # Initialize the Plotly figure
    fig = go.Figure()

    # Determine the variable name and unit from the column name
    unit = UNIT_DICT[column]
    column_name = " ".join(column.split("_")).title()

    # Calculate the monthly variation
    monthly_mean = monthly_variation_calculation(monthly_mean, monthly_data, column)

    # Plot the heatmap and update layout
    monthly_variation_plot(fig, monthly_mean, color_scale, column_name, unit)
    monthly_variation_layout(fig, graph_part, column_name)

    # Display the figure on the right
    with col2:
        st.plotly_chart(fig)

    return fig


# -------------------------
# --- Current Year Plot ---
# -------------------------

def add_vertical_line(fig:go.Figure, year,  periods=None):
    """
    Adds a vertical line to the Plotly figure to indicate a specific year.

    Parameters:
    fig (Figure): The Plotly figure to update.
    year (int): The year to indicate with the vertical line.
    periods (list of str): List of periods to display on the x-axis.
    """
    if type(year) is datetime:
        # For graph with x type datetime (daily plot graphs)
        line_and_annotation(fig, x=year.isoformat(), x_text=year.year)

    elif type(year) is int and periods:
        # For graph with x type periods (str)
        period = get_period_for_year(year, periods)
        if period is not None:
            line_and_annotation(fig, x=period, x_text=year)

    elif type(year) is int:
        # For graph with x type int (only for heat index for the moment)
        line_and_annotation(fig, x=year, x_text=year)
        
def get_period_for_year(year, periods):
    """
    Determines the period a given year belongs to.
    
    Args:
        year (int): The year to check.
        categories (list of str): List of categories in the format "start-end".
        
    Returns:
        str: The category the year belongs to, or None if no category matches.
    """
    for period in periods:
        try:
            start, end = map(int, period.split('-'))
            if start <= year <= end:
                return period
        except ValueError:
            raise ValueError(f"Invalid period format: '{period}'. Expected 'start-end'.")
    return None  

def line_and_annotation(fig : go.Figure,x, x_text):
    """
    Adds a vertical line and an annotation to the given Plotly figure.

    Args:
        fig (go.Figure): The Plotly figure to which the line and annotation are added.
        x (float): The x-coordinate where the vertical line is drawn.
        x_text (str): The text displayed as an annotation near the vertical line.

    """
    fig.add_vline(x=x, line=dict(color='green', width=2))
    fig.add_annotation(
        x=x,
        y=1.08,
        yref="paper",
        text= x_text,
        showarrow=False
    )

# --------------------
# --- PDF filling  ---
# --------------------

def create_header_text():
    """
    Creates a dynamic header text by concatenating available project details.
    
    Returns:
        str: The header text to display on the PDF.
    """
    project_info = st.session_state.project_info

    parts = []  # List to store non-empty values

    if project_info.get("project_name"):
        parts.append(f"Project: {project_info['project_name']}")
    if project_info.get("client_name"):
        parts.append(f"Client: {project_info['client_name']}")
    if project_info.get("financier_name"):
        parts.append(f"Financier: {project_info['financier_name']}")
    header_text = "  |  ".join(parts) 

    return header_text

def create_header(c: canvas.Canvas):
    """
    Draws the header and a separating line on each page.
    
    Args:
        c (canvas.Canvas): The PDF canvas object to draw on.
    """

    # Build and position the header text
    header_text = create_header_text()
    c.setFont("Helvetica-Bold", 14)
    text_width = c.stringWidth(header_text)
    page_width = landscape(A4)[0]
    x_position = (page_width - text_width) / 2
    c.drawString(x_position, 560, header_text)
    
    # Draw a separating line
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(1)
    c.line(40, 540, 800, 540) 

    # Add logos on both sides of the header
    logo_width = 80  
    logo_height = 40  
    c.drawImage(G8_LOGO, 40, 545, width=logo_width, height=logo_height, mask='auto', preserveAspectRatio=True)
    c.drawImage(NCCS_LOGO, page_width - logo_width - 40, 545, width=logo_width, height=logo_height, mask='auto', preserveAspectRatio=True)
    # c.drawImage(NCCS_LOGO, page_width - logo_width- logo_height - 10, 547, width=logo_width, height=logo_height, mask='auto', preserveAspectRatio=True)

def make_layout_improvement(fig1, fig2, fig3):
    """
    Improves the layout of the Plotly figures for better readability.
    """
    # Adjustement done on the layout of several graph to better fit the page
    fig1.layout.font.color = "black"
    fig1.layout.font.family = "Helvetica"
    fig1.layout.font.weight = 600
    fig2.layout.font.color = "black"
    fig2.layout.font.family = "Helvetica"
    fig2.layout.font.weight = 600 
    fig2.layout.legend.font.size = 13
    fig3.layout.font.color = "black"
    fig3.layout.font.family = "Helvetica"
    fig3.layout.font.weight = 600

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

    make_layout_improvement(fig1, fig2, fig3)

    create_header(c)
    # Convert the Plotly figures to JPG images in memory using kaleido
    fig1_image = pio.to_image(fig1, format="jpg", width=fig1.layout.width, height=fig1.layout.height)
    fig2_image = pio.to_image(fig2, format="jpg", width=fig2.layout.width, height=fig2.layout.height)
    fig3_image = pio.to_image(fig3, format="jpg", width=fig3.layout.width, height=fig3.layout.height)

    # Create ImageReader objects for the figures' image data
    img1_reader = ImageReader(BytesIO(fig1_image))
    img2_reader = ImageReader(BytesIO(fig2_image))
    img3_reader = ImageReader(BytesIO(fig3_image))

    # Place the first figure image on the PDF at a specific location with scaled dimensions
    c.drawImage(img1_reader, x=-330, y=280, height=fig1.layout.height / 2, width=fig1.layout.width, preserveAspectRatio=True)
    
    # Place the second figure image on the PDF at a specific location with scaled dimensions
    c.drawImage(img2_reader, x=-330, y=20, height=fig2.layout.height / 2, width=fig2.layout.width, preserveAspectRatio=True)
    c.showPage()

    create_header(c)
    # c.rect(0, 0, 892, 612, fill=1)  # Fill the entire page with black color
    c.drawImage(img3_reader, x=-220, y=20, height=fig3.layout.height*0.60, width=fig3.layout.width, preserveAspectRatio=True)
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

def general_plot(data: pd.DataFrame, periods, filename):
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
    chosen_variables = [" ".join(column.split("_")).title() for column in columns_to_keep]
    

    # Calculate monthly and yearly mean data
    monthly_data, monthly_mean = calculate_mothly_mean_through_year(copy(data), periods)
    yearly_mean = calculate_yearly_mean_through_year(data, periods)
    
    
    # Create a select box for users to choose the variable they want to plot
    variable_choice = st.selectbox("Choose the variable on which you want to see the plot", options=chosen_variables)
    
    # Loop through columns to find and plot data matching the selected variable
    for column in data.columns:
        if "_".join(variable_choice.lower().split(" ")) in column:
            
            # Generate the monthly and yearly plots for the selected column
            fig1 = plot_monthly_mean(column, monthly_mean, monthly_data)
            fig2 = plot_yearly_curve_and_period_trends(yearly_mean,monthly_mean, column, periods)
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

