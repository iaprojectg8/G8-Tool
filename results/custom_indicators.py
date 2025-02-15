from src.utils.imports import *
from src.utils.variables import *
from src.lib.layout import *
from results.indicators_plot import plot_daily_data, wrap_indicator_into_pdf
from results.general_plots import add_vertical_line, add_periods_to_df


# ----------------------------
# --- Heat Index Indicator ---
# ----------------------------

def verify_heat_index_taken_variable(variables):
    # This may be used in the futuue to well determined wether the variable have been well chosen by the user
    if "temperature_2m_max" in variables and "relative_humidity_2m_min":
        st.success("You have taken all the right variable for this indicator")
        return 1
    else :
        st.error("You need to take temperature_2m_max and relative_humidity_2m_min in order to make calculate this indicator")
        return 0
    
def classify_heat_index(heat_index):
    """
    Classifies the heat index into different levels of discomfort.

    Parameters:
    heat_index (float): The heat index value to classify.

    Returns:
    str: The level of discomfort based on the heat index.
    """
    if heat_index < 27:
        return 'Low Discomfort'
    elif 27 <= heat_index < 32:
        return 'Moderate Discomfort'
    elif 32 <= heat_index < 39:
        return 'High Discomfort'
    else:
        return 'Very High Discomfort'
    
def heat_index_calculation(df, rh, tmp_2m):
    """
    Calculates the heat index based on temperature and relative humidity.

    Parameters:
    df (DataFrame): The DataFrame containing the temperature and relative humidity data.
    rh (str): The column name for relative humidity in the DataFrame.
    tmp_2m (str): The column name for temperature in the DataFrame.

    Returns:
    DataFrame: The DataFrame with an additional column for the calculated heat index.
    """
    # Constants for the heat index calculation formula
    c1, c2, c3, c4, c5, c6, c7, c8, c9 = (-42.379, 2.04901523, 10.14333127, -0.22475541, -0.00683783,
                                          -0.05481717, 0.00122874, 0.00085282, -0.00000199)

    # Calculate the heat index using the formula
    df["heat_index"] = (c1 + c2 * df[tmp_2m] + c3 * df[rh] + c4 * df[tmp_2m] * df[rh] + c5 * df[tmp_2m]**2 +
                        c6 * df[rh]**2 + c7 * df[tmp_2m]**2 * df[rh] + c8 * df[tmp_2m] * df[rh]**2 + c9 * df[tmp_2m]**2 * df[rh]**2)
    
    return df

def categorize_heat_index(df: pd.DataFrame):
    """
    Categorizes the heat index into different levels of discomfort and adds a 'year' column.

    Parameters:
    df (DataFrame): The DataFrame containing the heat index data.

    Returns:
    None
    """
    df['heat_index_category'] = df['heat_index'].apply(classify_heat_index)
    df['year'] = df.index.year

    category_order = ['Low Discomfort', 'Moderate Discomfort', 'High Discomfort', 'Very High Discomfort']
    df['heat_index_category'] = pd.Categorical(df['heat_index_category'], categories=category_order, ordered=True)


def plot_bar(category_counts, x, y, x_label, y_label):
    fig = px.bar(
        category_counts,
        x=x,
        y=y,
        color='heat_index_category',
        title=f"Heat Index Through {x_label}",      
        labels={x: x_label, y: f"{y_label} (days)"},
        color_discrete_map={
            'Low Discomfort': 'green',
            'Moderate Discomfort': 'yellow',
            'High Discomfort': 'orange',
            'Very High Discomfort': 'red'
        }
    )
    return fig



def plot_bar_stack_count(df: pd.DataFrame, periods):
    """
    Plots a stacked bar chart of heat index categories by year.

    Parameters:
    df (DataFrame): The DataFrame containing the heat index data.

    Returns:
    None
    """
    
    # Yearly bar plot 
    category_counts = df.groupby(['year', 'heat_index_category'], observed=False).size().reset_index(name='count')
    fig1 = plot_bar(category_counts, "year", "count", 'Years', 'Count of Days')
    add_vertical_line(fig1, datetime.now().year)
    update_plot_layout(fig1)
    st.plotly_chart(fig1)
    
    
    # Adding period to category_counts
    category_counts = add_periods_to_df(category_counts, periods)
    category_counts['period'] = category_counts['period'].apply(lambda x: f"{x[0]}-{x[1]}")  # Ensure periods are strings

    # Creating the periods list for the plot layout
    periods = list(category_counts['period'].unique())

    # Periodically bar plot
    category_counts_periods = category_counts.groupby(['period', 'heat_index_category'], observed=False).mean().reset_index()
    fig2 = plot_bar(category_counts_periods, "period", "count", 'Periods', 'Count of Days')
    add_vertical_line(fig2, datetime.now().year, periods=periods)
    update_plot_layout(fig2)
    st.plotly_chart(fig2)

    # Indicator part ??
    max_category_per_period = (category_counts_periods.loc[category_counts_periods.groupby('period')['count'].idxmax()])
    fig3 = plot_bar(max_category_per_period, "period", "count", 'Periods', 'Max Count per Period')
    add_vertical_line(fig3, datetime.now().year, periods=periods)
    update_plot_layout(fig3)
    st.plotly_chart(fig3)
    return fig1, fig2, fig3

def update_plot_layout(fig:go.Figure):
    """
    Updates the layout of the Plotly figure.

    Parameters:
    fig (Figure): The Plotly figure to update.

    Returns:
    None
    """
    fig.update_layout(
        width=1500, height=500,
        barmode='stack',
        title=dict(
                    x=0.5,
                    xanchor="center",
                    yanchor = "middle",
                    font = dict(size=25, weight=900)),
        xaxis=dict(tickfont_size=15,
                   nticks = 10,
                   ticklabeloverflow="hide past div",
                    title = dict(
                        font_size=17,
                        standoff=50),       
                    ticklabelstandoff =20),
        yaxis=dict(tickfont_size=15,
                    title=dict(
                        font_size=17,
                        standoff=50),
                    ticklabelstandoff = 20),
        legend=dict(title=dict(text="Heat Index Category",
                                font=dict(size=20, color="white",weight=900),
                                side="top center"
                               ),
                    
                    orientation="v", 
                    traceorder="reversed",
                    x=1.05,           
                    y=0.5,
                    ),
        font=dict(size=17, weight=700),
        )
    
def from_fahrenheit_to_celsius(fahrenheit):
    """
    Converts temperature from degree Fahrenheit to degree Celsius.

    Args:
    fahrenheit (float): Temperature in Fahrenheit.

    Returns:
    float: Temperature in Celsius.
    """
    celsius = (fahrenheit - 32) * 5/9
    return celsius

def from_celsius_to_fahrenheit(celsius):
    """
    Converts temperature from degree Celsius to degree Fahrenheit.

    Args:
    celsius (float): Temperature in Celsius.

    Returns:
    float: Temperature in Fahrenheit.
    """
    fahrenheit = celsius * 9/5 + 32
    return fahrenheit


def heat_index_indicator(df, df_all, key, periods):
    """
    Processes the seasonal data to calculate and categorize the heat index, then plots the results.

    Parameters:
    df_season (DataFrame): The DataFrame containing the seasonal data.

    Returns:
    None
    """

    set_title_1("Variable filter")

    if "relative_humidity_2m_min" in df_all.columns:
        relative_humidity_min = "relative_humidity_2m_min"
        temperature_max = "temperature_2m_max"
    elif "relative_humidity_2m" in df_all.columns:  
        relative_humidity_min = "relative_humidity_2m" 
        temperature_max = "temperature_2m_mean"

    heat_index = "heat_index"
    if relative_humidity_min not in df or temperature_max not in df:
        if relative_humidity_min not in df:
            st.error(f"{relative_humidity_min} was not provided in the indicator variable. You should add it and update")
        if temperature_max not in df:
            st.error(f"{temperature_max} was not provided in the indicator variable. You should add it and update")
    else:
        df_heat_index = df[[temperature_max, relative_humidity_min]]

        # Calculate the heat index 
        df_heat_index[temperature_max] = df_heat_index[temperature_max].apply(from_celsius_to_fahrenheit)
        df_heat_index = heat_index_calculation(df_heat_index, relative_humidity_min, temperature_max)
        df_heat_index[[heat_index, temperature_max]] = df_heat_index[[heat_index, temperature_max]].apply(from_fahrenheit_to_celsius)
        
        
        # Display the dataframe 
        st.dataframe(df_heat_index, height=DATAFRAME_HEIGHT, use_container_width=True)

        # Categorize the heat index
        categorize_heat_index(df_heat_index)

        fig_list = list()
        # Plot the heat index categories by year
        fig1 = plot_daily_data(df_heat_index, relative_humidity_min, key)
        fig2 = plot_daily_data(df_heat_index, temperature_max, key)
        fig_list.extend([fig1, fig2])
        fig1, fig2, fig3 = plot_bar_stack_count(df_heat_index, periods)
        fig_list.extend([fig1, fig2, fig3])
        pdf = wrap_indicator_into_pdf(fig_list=fig_list)
        # Provide a button to download the generated PDF
        st.download_button(
            label="Download PDF",
            data=pdf,
            file_name="Heat Index.pdf",
            mime="application/pdf",
            key= key
        )


def heat_index_spatial_indicator(df, periods):
    """
    Calculate the spatial heat index for given periods based on temperature and relative humidity
    Args:
        df (pd.DataFrame): Input DataFrame containing temperature and relative humidity data along with latitude and longitude.
        df_key (str): Key to identify the DataFrame (not used in the function but kept for consistency).
        periods (list of tuples): List of period tuples where each tuple contains start and end period.

    Returns:
        pd.DataFrame: A pivot table DataFrame with latitude and longitude as index, periods as columns, and mean heat index values.
    """

    if "relative_humidity_2m_min" in df.columns:
        relative_humidity_min = "relative_humidity_2m_min"
    elif "relative_humidity_2m" in df.columns:  
        relative_humidity_min = "relative_humidity_2m" 
    temperature_max = "temperature_2m_mean"
    heat_index = "heat_index"
    df_heat_index = df[[temperature_max, relative_humidity_min, "lat", "lon"]]

    # Calculate the heat index 
    df_heat_index[temperature_max] = df_heat_index[temperature_max].apply(from_celsius_to_fahrenheit)
    df_heat_index = heat_index_calculation(df_heat_index, relative_humidity_min, temperature_max)
    df_heat_index[[heat_index, temperature_max]] = df_heat_index[[heat_index, temperature_max]].apply(from_fahrenheit_to_celsius)
    categorize_heat_index(df_heat_index)
    df_heat_index = add_periods_to_df(df_heat_index, periods)
    df_heat_index["period"] = df_heat_index["period"].apply(lambda x: f"{x[0]}-{x[1]}")
    df_period = df_heat_index.groupby(["period", "lat", "lon"], as_index=False, observed=False)[heat_index].mean()
    sumup_df = df_period.pivot_table(
        index=['lat', 'lon'], 
        columns='period',
        values='heat_index', # ['absolute_score', 'category', 'color', 'exposure_prob'], 
        aggfunc='first',
        observed=False
    )
    return sumup_df


def display_raster_with_slider_heat_index(score_name, periods):
    """
    Display a multi-band raster with a slider to switch between epochs using Plotly.

    Args:
        periods (list(tuple)) : Contains the list of the periods encapsulated in tuples
    """
    periods = [f"{period[0]}-{period[1]}" for period in periods]
    # Open the raster file

    grid_score_list, _ = st.session_state.raster_params[score_name]
    bands = grid_score_list

    # Colorscale min and max
    data_min = 20
    data_max = 40

    fig = px.imshow(
        bands[0], 
        color_continuous_scale=["green", "yellow", "orange","red"],
        zmin=data_min,  # Use the actual min value from the data
        zmax=data_max,  # Use the actual max value from the data
        title=f"{score_name} Exposure through Periods",
        height=800
    )

    # Building each step of the slider
    steps = []
    for i, band in enumerate(bands):
        step = {
            "args": [{"z": [band]}],
            "label": periods[i],
            "method": "update",
        }
        steps.append(step)

    # Creating the slider for the raster
    sliders = [dict(active= 0,
                    pad={"t": 120, "r":50, "l":50, "b":50},
                    steps = steps,
                    font=dict(size=17,
                              weight=800),
                    name = "Periods")]

    fig.update_layout(sliders=sliders,
                        title=dict(x=0.5,
                                    xanchor="center",
                                    font_size=25),
                        coloraxis_colorbar=dict(
                                    title=dict(text="Exposure",
                                                font=dict(size=20, color="white",weight=900),
                                                        side="top",
                                                        ),   
                                    ticks="outside",  
                                    tickvals=[22, 27, 32, 39],  # Custom tick values
                                    ticktext=['Low Discomfort', 'Moderate Discomfort', 'High Discomfort', 'Very High Discomfort'],  # Custom tick labels
                                    lenmode="fraction",            # Control the length of the colorbar
                                    len=0.8, 
                                    yanchor="middle",
                                    y=0.5,
                               ),
                        xaxis=dict(tickfont_size=15,
                                tickangle=0 ,
                                    title = dict(
                                        text="Longitude",
                                        font_size=17,
                                        standoff=50), 
                                    ticklabelstandoff =15),
                        yaxis=dict(tickfont_size=15,
                                    range=[0,1],
                                    title=dict(
                                        text="Latitude",
                                        font_size=17,
                                        standoff=50),
                                    ticklabelstandoff = 15),
                        font=dict(size=17, weight=800),
                        autosize=True)
                        

    # Display the map in Streamlit
    st.plotly_chart(fig, use_container_width=True)