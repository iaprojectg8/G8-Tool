from utils.imports import *
from utils.variables import *

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
    monthly_mean["customdata"] = monthly_mean["period"].apply(lambda x: "-".join([str(list(x)[0]),str(list(x)[1])]))
    print(monthly_mean)

    # Monthly_mean have in its own the mean
    
    st.dataframe(monthly_mean, use_container_width=True) 

    for column in data.columns:
        if column in columns_to_keep and "min" not in column and "max" not in column:
            fig = go.Figure()

            # Mean line
            fig.add_trace(go.Scatter(
                x=monthly_data["month_name"], 
                name="Monthly mean over years", 
                y=monthly_data[column], 
                mode='lines', 
                line=dict(color='blue')
            ))

            # 
            fig.add_trace(go.Scatter(
                x=monthly_mean['month_name'],
                y=monthly_mean[column],
                name="Year month mean", 
                mode='markers',
                marker=dict(
                    size=10,
                    color=monthly_mean["period_index"],  # Color by the period_index
                    colorscale="sunset",  # Use correct colorscale name
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
                    "Temperature: %{y:.2f}°C<br>" +
                    "Year: %{text}<br>"+
                    "Decade: %{customdata}<br>"
                ),
                showlegend=False

            ))

            # Update layout with titles and labels
            # I need to make function for that
            variable = [variable for variable in AVAILABLE_VARIABLES if "_".join(variable.lower().split()) in column][0]
            fig.update_layout(
                title=dict(text=f'Monthly Mean {variable} through years',
                        x=0.5,
                        xanchor="center",
                        font_size=25),
                xaxis_title='Month',
                yaxis_title='Value',
                legend_title='',
                template='plotly_dark',
                autosize=True
            )
            
            # Display the plot in Streamlit
            st.plotly_chart(fig)