from utils.imports import *
from utils.variables import *

def calculate_mothly_mean_through_year(data:pd.DataFrame, periods):
    data["month"] = data.index.month
    data["year"] = data.index.year
    monthly_mean = data.resample("ME").agg({
        **{col: "mean" for col in data.columns if "precipitation" not in col.lower()},
        **{col: "sum" for col in data.columns if "precipitation" in col.lower()}
    })
    monthly_data = monthly_mean.groupby("month").mean().reset_index()
    monthly_data = add_month_to_df(monthly_data)

    # Adding month string and periods to the df
    monthly_mean = add_month_to_df(monthly_mean)
    monthly_mean =  add_periods_to_df(monthly_mean, periods)

    monthly_mean["period_index"] = monthly_mean["period"].apply(lambda p: periods.index(p))
    monthly_mean["customdata"] = monthly_mean["period"].apply(lambda x: "-".join([str(list(x)[0]),str(list(x)[1])]))

    return monthly_data, monthly_mean

def calculate_yearly_mean_through_year(data:pd.DataFrame, periods):
    data["year"] = data.index.year 
    yearly_mean = data.resample("YE").agg({
        **{col: "mean" for col in data.columns if "precipitation" not in col.lower()},
        **{col: "sum" for col in data.columns if "precipitation" in col.lower()}
    })  
    yearly_mean = add_periods_to_df(yearly_mean, periods)
    return yearly_mean


def add_periods_to_df(df:pd.DataFrame, periods):
    df["period"] = df["year"].apply(lambda x: next((period for period in periods if period[0] <= x <= period[1]), None))
    return df

def add_month_to_df(df):
    df["month_name"] = df["month"].apply(lambda x:MONTHS_LIST[int(x-1)])
    return df


    


def plot_monthly_mean(column, columns_to_keep, monthly_mean, monthly_data):
    
        fig = go.Figure()

        # Mean line
        fig.add_trace(go.Scatter(
            x=monthly_data["month_name"], 
            name="Monthly mean over years", 
            y=monthly_data[column], 
            mode='lines', 
            line=dict(color='blue')
        ))

        variable = [variable for variable in AVAILABLE_VARIABLES if "_".join(variable.lower().split()) in column][0]
        unit=UNIT_DICT[variable]
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
            showlegend=False

        ))

        # Update layout with titles and labels
        fig.update_layout(
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
        
        # Display the plot in Streamlit
        st.plotly_chart(fig)

def get_period_trend(df : pd.DataFrame,column, start, stop):
    # Calculating the trend lines
    df = df[(df["year"] >= start) & (df["year"]<= stop) ]

    if not df.empty:
        years = np.array(df["year"])
        annual_properties = df[column]
        slope, intercept, r_value, p_value, std_err = linregress(years, annual_properties)
        
        # Create the trend line using the slope and intercept
        trend_line = slope * years + intercept
        print(trend_line)
        return trend_line, years

def build_trend_plot(year_mean_df, periods, column):
    trend_lines = []
    years_all = []
    
    for i, period in enumerate(periods): 
        start, end = period
        print(start, end)

        trend_line, years = get_period_trend(year_mean_df,column, int(start), int(end))
        trend_lines.append(trend_line)
        years_all.append(years)
        
    return trend_lines, years_all

def plot_periods_trend(yearly_mean, column, columns_to_keep, periods):
    fig = go.Figure()
    variable = [variable for variable in AVAILABLE_VARIABLES if "_".join(variable.lower().split()) in column][0]
    # Plotting the year average temperatures (as a line)
    fig.add_trace(go.Scatter(
        x=yearly_mean["year"],
        y=yearly_mean[column],
        mode='lines',
        name=f"Year Average {variable}",
        line=dict(color="blue"),
    ))

    # Define periods for trends
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
    # Update layout with titles and labels
    fig.update_layout(
        title=dict(text=f'Mean Year {variable} and Trends from Different Periods',
                    x=0.5,
                    xanchor="center",
                    font_size=25),
        xaxis_title="Year",
        yaxis_title=f"{variable} - {UNIT_DICT[variable]}",
        # template="plotly_dark",
        autosize=True,
        showlegend=True,
        legend=dict(
            orientation="v",  # Horizontal orientation
            x=1.05,            # Center the legend horizontally
            y=0.5,           # Position the legend below the plot (adjust as needed)
        )
    )
    st.plotly_chart(fig)
    # Display the plot in Streamlit or standalone


def general_plot(data:pd.DataFrame, periods, chosen_variable):
    """
    Plots monthly mean, max, and min for each variable in the list 'variables' using Plotly and displays it in Streamlit.
    
    Args:
        data (pd.DataFrame): The input DataFrame with daily data.
        variables (list): List of column names in the DataFrame to calculate the monthly means.
    """
    columns_to_keep = data.columns

    monthly_data, monthly_mean = calculate_mothly_mean_through_year(copy(data), periods)
    yearly_mean = calculate_yearly_mean_through_year(data, periods)
    
    variable_choice = st.selectbox("Choose the variable on which you want to see the plot", options=chosen_variable)
    for column in data.columns:
        if column in columns_to_keep and "min" not in column and "max" not in column and "_".join(variable_choice.lower().split(" ")) in column:
            
            plot_monthly_mean(column, columns_to_keep, monthly_mean, monthly_data)
            plot_periods_trend(yearly_mean, column,columns_to_keep, periods)
            