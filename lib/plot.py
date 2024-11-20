from utils.imports import *
from utils.variables import *



def plot_monthly_variation_over_periods(df:pd.DataFrame, column):
    

    # Add decade and month information
    df["decade_start"] = (df["date"].dt.year // 10) * 10
    df["decade_end"] = df["decade_start"] + 9
    df["decade"] = df["decade_start"].astype(str) + "-" + df["decade_end"].astype(str)

    df["month"] = df.index.dt.month
    df["year"] = df.index.dt.year

    # Overall and decade-specific monthly averages
    overall_monthly_mean = df.groupby("month")[column].mean().reset_index()
    year_month_data = df.groupby(["decade", "year", "month"]).agg({column: "mean"}).reset_index()

    # Merge both of them and make the difference
    year_month_data = year_month_data.merge(overall_monthly_mean, on="month", suffixes=("_year", "_overall"))

    # Create the Plotly figure
    fig = go.Figure()

    # Scatter plot for decade-specific data
    for decade in year_month_data['decade'].unique():
        decade_data = year_month_data[year_month_data['decade'] == decade]
        fig.add_trace(go.Scatter(
            x=decade_data['month'],
            y=decade_data['temperature_2m_mean_year'],
            mode='markers',
            name=f"Decade {decade}",
            marker=dict(size=10),
            hovertemplate=(
                "Temperature: %{y:.2f}°C<br>" +
                "Year: %{text}<br>" +
                "Decade: %{customdata[0]}"
            ),
            text=decade_data['year'],
            customdata=decade_data[['decade']],
            showlegend=True
        ))

    # Line plot for the overall monthly mean
    fig.add_trace(go.Scatter(
        x=overall_monthly_mean['month'],
        y=overall_monthly_mean['temperature_2m_mean'],
        mode='lines',
        name="Overall Monthly Mean",
        line=dict(color='green'),
        hoverinfo='skip'
    ))

    # Update layout for titles and axis labels
    fig.update_layout(
        title="Mean Temperature per Month, Colored by Decade",
        xaxis_title="Month",
        yaxis_title="Temperature (°C)",
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1, 13)),
            ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        ),
        template="plotly_dark",
        legend_title="Decade"
    )

    # Show the plot in Streamlit
    st.plotly_chart(fig)

def calculate_mothly_mean_through_year(data:pd.DataFrame, periods):
    data["month"] = data.index.month
    data["year"] = data.index.year
    monthly_mean = data.resample("ME").mean()
    monthly_data = monthly_mean.groupby("month").mean().reset_index()
    return monthly_data, monthly_mean


def add_periods_to_df(df:pd.DataFrame, periods):
    df["period"] = df["year"].apply(lambda x: next((period for period in periods if period[0] <= x <= period[1]), None))
    print(df)
    return df

def add_month_to_df(df):
    df["month_name"] = df["month"].apply(lambda x:MONTHS_LIST[int(x-1)])
    return df

def plot_monthly_means(data:pd.DataFrame, periods):
    """
    Plots monthly mean, max, and min for each variable in the list 'variables' using Plotly and displays it in Streamlit.
    
    Args:
        data (pd.DataFrame): The input DataFrame with daily data.
        variables (list): List of column names in the DataFrame to calculate the monthly means.
    """
    columns_to_keep = data.columns
    # Ensure that the index is a datetime type
    # data.index = pd.to_datetime(data.index)
    
        # Create a figure for the plots
        
    monthly_data, monthly_mean = calculate_mothly_mean_through_year(data, periods)
    monthly_mean = add_month_to_df(monthly_mean)
    add_periods_to_df(monthly_mean, periods)
    monthly_data = add_month_to_df(monthly_data)
    monthly_mean["period_index"] = monthly_mean["period"].apply(lambda p: periods.index(p))
    print(monthly_mean)

    # Monthly_mean have in its own the mean
    
    st.dataframe(monthly_mean, use_container_width=True) 

    for column in data.columns:
        if column in columns_to_keep:
            fig = go.Figure()
         
            fig.add_trace(go.Scatter(
                x=monthly_data["month_name"], 
                y=monthly_data[column], 
                mode='lines', 
                # name=f'Monthly Mean of {column}', 
                line=dict(color='blue')
            ))

            fig.add_trace(go.Scatter(
                x=monthly_mean['month_name'],
                y=monthly_mean[column],
                mode='markers',
                marker=dict(
                    size=10,
                    color=monthly_mean["period_index"],  # Color by the period_index
                    colorscale="Viridis",  # Use correct colorscale name
                    showscale=True  # Show color scale
                ),
                text=monthly_mean["year"],
                customdata=monthly_mean["period"],
                hovertemplate=(
                    "Temperature: %{y:.2f}°C<br>" +
                    "Year: %{text}<br>"+
                    "Decade: %{customdata}<br>"
                ),
                
    
                # customdata=monthly_mean[['year']],
                showlegend=True
            ))

            # Update layout with titles and labels
            fig.update_layout(
                title=f'mean {column} variation trough month and time',
                xaxis_title='Month',
                yaxis_title='Value',
                legend_title='Variable',
                xaxis_tickformat='%b %Y',  # Display month and year
                template='plotly_dark',
                autosize=True
            )
            
            # Display the plot in Streamlit
            st.plotly_chart(fig)