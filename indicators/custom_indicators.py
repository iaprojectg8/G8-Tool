from utils.imports import *
from utils.variables import *
from layouts.layout import *
from indicators.plot import plot_daily_data, wrap_indicator_into_pdf
from lib.plot import add_vertical_line, add_periods_to_df


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
    print(max_category_per_period.size)
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



def heat_index_indicator(df,df_key, periods):
    """
    Processes the seasonal data to calculate and categorize the heat index, then plots the results.

    Parameters:
    df_season (DataFrame): The DataFrame containing the seasonal data.

    Returns:
    None
    """
    set_title_1("Variable filter")
    st.write("We are keeping only the daily max temperature and the daily mean relative humidity")

    # Get the right variable
    relative_humidity_min = "relative_humidity_2m_min"
    temperature_max = "temperature_2m_max"
    heat_index = "heat_index"
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
    fig1 = plot_daily_data(df_heat_index, relative_humidity_min)
    fig2 = plot_daily_data(df_heat_index, temperature_max)
    fig_list.extend([fig1, fig2])
    fig1, fig2, fig3 = plot_bar_stack_count(df_heat_index, periods)
    fig_list.extend([fig1, fig2, fig3])
    pdf = wrap_indicator_into_pdf(fig_list=fig_list)
    # Provide a button to download the generated PDF
    st.download_button(
        label="Download PDF",
        data=pdf,
        file_name="whatever.pdf",
        mime="application/pdf",
        key= df_key
    )

