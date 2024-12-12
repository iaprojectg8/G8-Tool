from utils.imports import *
from utils.variables import *


def plot_exposure_through_period(df:pd.DataFrame,score_name):
    
    score_counts  = df.groupby('period')[f"yearly_indicator_{score_name}"].value_counts().unstack(fill_value=0)
    periods_size = df.groupby('period').size().max()
    # Split the DataFrame into negatives, positives, and zeros
    negative_df = score_counts[score_counts.columns[score_counts.columns.astype(int) < 0]]
    positive_df = score_counts[score_counts.columns[score_counts.columns.astype(int) > 0]]
    zero_df = score_counts[score_counts.columns[score_counts.columns.astype(int) == 0]]

    # Sort the negative DataFrame for stacking
    negative_df = negative_df[sorted(negative_df.columns, key=int, reverse=True)]
    print(negative_df)

    # Plot negative scores
    fig = go.Figure()
    for column in negative_df.columns:
        values = negative_df[column]
        score = int(column)  # Get the score as an integer
        risk_level = CATEGORY_TO_RISK[score]  # Map the score to a risk level
        color_scale = px.colors.diverging.RdBu_r

        fig.add_trace(
            go.Bar(
                x=negative_df.index,
                y=-values,  # Negative values go below zero
                customdata=values,
                name=risk_level,
                marker_color=color_scale[GET_RIGHT_COLOR[score]],
                legendgroup=risk_level,  # Group by risk level
                showlegend=True,
                hovertemplate=(
                    f"Category: {risk_level}<br>" +
                    "Count: %{customdata}<br>"),
            )
        )

    # Plot positive scores
    for column in positive_df.columns:
        values = positive_df[column]
        score = int(column)  # Get the score as an integer
        risk_level = CATEGORY_TO_RISK[score]  # Map the score to a risk level
        color_scale = px.colors.diverging.RdBu_r 

        fig.add_trace(
            go.Bar(
                x=positive_df.index,
                y=values,
                name=risk_level,
                marker_color=color_scale[GET_RIGHT_COLOR[score]],
                legendgroup=risk_level,  # Group by risk level
                showlegend=True,
                hovertemplate=(
                    f"Category: {risk_level}<br>" +
                    "Count: %{y}<br>"),
            )
        )

    # Plot zero scores as a line
    if not zero_df.empty:
        zero_values = zero_df.iloc[:, 0]  # Assuming only one column for zeros
        fig.add_trace(
            go.Scatter(
                x=zero_df.index,
                y=zero_values,
                mode="lines+markers",
                name="No Risk",
                line=dict(color="green"),
                marker=dict(size=6),
                showlegend=True,
                hovertemplate=(
                    "Category: No Risk<br>" +
                    "Count: %{y}<br>"),
            )
        )

    # Customize layout
    fig.update_layout(
        barmode="relative",  # Stack bars relatively
        title=dict(text="Stacked Bar Chart with Line for Zero Scores",
                    x=0.5,
                    xanchor="center",
                    font_size=25),
        xaxis=dict(tickfont_size=15,
                    title = dict(
                        text="Periods",
                        font_size=17,
                        standoff=50),       
                    ticklabelstandoff =20),
        yaxis=dict(tickfont_size=15,
                    range=[-periods_size, periods_size],
                    title=dict(
                        text="Year Count",
                        font_size=17,
                        standoff=50),
                    ticklabelstandoff = 20),
        legend=dict(title=dict(text="Risk Levels \t",
                               font=dict(size=20, color="white",weight=900),
                               side="top center",
    
                               ),
                    
                    orientation="v", 
                    traceorder="grouped",
                    x=1.05,           
                    y=0.5,
                    ),
        font=dict(
            size=17),
        autosize=True,
        # paper_bgcolor="purple"
    )

    st.plotly_chart(fig)




def plot_years_exposure(df, aggregated_column_name, min_thresholds, max_thresholds, variable):
    
    

    # print(df["precipitation_sum_sum_season_precipitation"].min())
    fig = go.Figure()
    main_scatter_plot(fig, df, aggregated_column_name)

    # Customize Layout
    data_min=df[aggregated_column_name].min()
    data_max=df[aggregated_column_name].max()
    diff = abs(data_max-data_min)
    
    
    
    # Add threshold backgrounds as shapes
    
    last_min=min_thresholds[-1]-abs(min_thresholds[-1]-max_thresholds[-1])
    last_max=max_thresholds[-1]+abs(min_thresholds[-1]-max_thresholds[-1])

    if len(min_thresholds)<5:
        min_thresholds.append(last_min)
    if len(max_thresholds)<5:
        max_thresholds.append(last_max)

    for threshold_index in range(len(max_thresholds)):
        if threshold_index == 0 :
            add_background_color(fig, threshold_index, 
                                 y0=min_thresholds[threshold_index], 
                                 y1=max_thresholds[threshold_index])
        
        else:
            

            add_background_color(fig, threshold_index, 
                                 y0=min_thresholds[threshold_index], 
                                 y1=min_thresholds[threshold_index-1])
    
            add_background_color(fig, threshold_index, 
                                 y0=max_thresholds[threshold_index-1], 
                                 y1=max_thresholds[threshold_index])
    update_scatter_layout(fig, data_min, data_max, diff, aggregated_column_name, variable)
        
    st.plotly_chart(fig)



def main_scatter_plot(fig:go.Figure, df, aggregated_column_name):

    legend_column_name = " ".join(aggregated_column_name.split("_")).title()
    for category in df["category"].unique():
        category_data = df[df["category"] == category]
        fig.add_trace(
            go.Scatter(
                x=category_data["period"],
                y=category_data[aggregated_column_name],
                mode="markers",
                marker=dict(
                    # symbol="x",
                    size=10,
                    color=category_data["color"],  # Assuming color column exists
                    opacity=0.9,
                    line=dict(width=1, color="grey")
                ),
                text=category_data["category"],  # Hover text
                customdata=category_data["year"],
                hovertemplate=(
                    f"{legend_column_name}: %{{y}}<br>" +
                    "Category: %{text}<br>" +
                    "Year: %{customdata}<br>"
                ),
                name=category,  # Use category as the legend name
                showlegend=True
            )
        )

def add_background_color(fig:go.Figure, threshold_index, y0, y1):
    fig.add_shape(
        type="rect",
        xref="paper",  # Use entire plot width for the rectangles
        x0=0, x1=1,  # Entire plot width
        yref="y",
        y0=y0,  # Bottom of the threshold
        y1=y1,  # Top of the threshold
        fillcolor=THRESHOLD_COLORS[threshold_index],  # Background color
        opacity=0.25,
        layer="below",  # Place below the scatter points
        line_width=0,  # No border
    )

def update_scatter_layout(fig:go.Figure, data_min, data_max, diff, aggregated_column_name, variable):
    legend_name = " ".join(aggregated_column_name.split("_")).title()
    variable_legend_name = " ".join(variable.split("_")).title()
    fig.update_layout(
        title=dict(text=f"Yearly {variable_legend_name} Exposure over Periods ",
                    x=0.5,
                    xanchor="center",
                    font_size=25),
        xaxis=dict(tickfont_size=15,
                    title = dict(
                        text="Periods",
                        font_size=17,
                        standoff=50),       
                    ticklabelstandoff =20),
        yaxis=dict(tickfont_size=15,
                    range=[data_min - 0.05 * diff, data_max + 0.05 * diff],
                    title=dict(
                        text=legend_name,
                        font_size=17,
                        standoff=50),
                    ticklabelstandoff = 20),
        legend=dict(
            title="Categories",
            orientation="v", 
            x=1.05,            
            y=0.5),
        font=dict(
            size=17),
    )



def calculate_category_score(value):
    if value<0:
        return -value
    else :
        return value
def apply_my_dict(value):
    return CATEGORY_TO_RISK[value]


def plot_global_exposure(df_yearly:pd.DataFrame, score_name):
    score_column = f"yearly_indicator_{score_name}"
    st.selectbox(label="Aggregation Type", options=EXPOSURE_AGGREGATION )
    print(df_yearly)
    df_yearly["absolute_score"] = df_yearly[score_column].apply(calculate_category_score)
    
    df_period = df_yearly.groupby("period", as_index=False)["absolute_score"].mean()

    # Apply np.ceil to round the scores to the next integer
    df_period["absolute_score"] = np.round(df_period["absolute_score"])
    
    # Map the "absolute_score" to the category
    df_period["category"] = df_period["absolute_score"].apply(apply_my_dict)
    st.dataframe(df_period)
    return 0



# --- Draft made on different plot


# This function could be useful when working with
def plot_hazard_intervals(value_range, threshold, intervals, colors):
    """
    Plot a hazard scale with different levels and colors.
    
    Args:
        value_range (tuple): The full range of values to display (min, max).
        threshold (float): The base threshold separating good data.
        intervals (list of tuples): List of (start, end) for each hazard interval.
        colors (list of str): Colors corresponding to each interval.
    """
    fig = go.Figure()

    # Add the "Good" range (below threshold)
    fig.add_trace(go.Scatter(
        x=[value_range[0], threshold],
        y=[0, 0],
        mode="lines",
        line=dict(color="blue", width=10),
        name="Good (Below Threshold)"
    ))

    # Add hazard intervals
    for i, (start, end) in enumerate(intervals):
        fig.add_trace(go.Scatter(
            x=[start, end],
            y=[0, 0],
            mode="lines",
            line=dict(color=colors[i], width=10),
            name=f"Hazard Level {i + 1} ({start}-{end})"
        ))

    # Customize layout
    fig.update_layout(
        title="Hazard Scale",
        xaxis=dict(
            range=value_range,
            title="Cumulative Temperature (°C)",
            tickvals=[value_range[0], threshold] + [end for _, end in intervals],
            ticktext=[str(value_range[0]), f"Threshold ({threshold})"] + [str(end) for _, end in intervals],
        ),
        yaxis=dict(visible=False),  # Hide y-axis since it’s a horizontal scale
        showlegend=True,
        height=800,
    )

    st.plotly_chart(fig)



def plot_period_categorization(df):
    color_map = {
            "No Risk": "blue",
            "Low Risk": "green",
            "Moderate Risk": "yellow",
            "High Risk": "orange",
            "Very High Risk": "red",
        }

    risk_map = {
        -4: "Very High Risk",
        -3: "High Risk",
        -2: "Moderate Risk",
        -1: "Low Risk",
        0: "No Risk",
        1: "Low Risk",
        2: "Moderate Risk",
        3: "High Risk",
        4: "Very High Risk",
    }

    # Create the figure
    fig = go.Figure()

    # Add bars for each score
    for column in df.columns:
        values = df[column]
        score = int(column)  # Get the score as an integer
        risk_level = risk_map[score]  # Map the score to a risk level

        if score < 0:
            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=-values,  # Negative values go below zero
                    name=risk_level,
                    marker_color=color_map[risk_level],
                    legendgroup=risk_level,  # Group by risk level
                    showlegend=True if risk_level not in [trace.name for trace in fig.data] else False
                )
            )
        else:
            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=values,
                    name=risk_level,
                    marker_color=color_map[risk_level],
                    legendgroup=risk_level,  # Group by risk level
                    showlegend=True if risk_level not in [trace.name for trace in fig.data] else False
                )
            )

    # Update layout
    fig.update_layout(
        barmode="relative",  # Stack bars relative to the axis
        title="Stacked Bar Chart of Risk Levels by Period",
        xaxis=dict(title="Period"),
        yaxis=dict(title="Count"),
        legend=dict(title="Risk Level"),
    )
    st.plotly_chart(fig)