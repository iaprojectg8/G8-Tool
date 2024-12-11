from utils.imports import *
from utils.variables import *


def plot_exposure_through_period(df : pd.DataFrame  ):
    color_map = {
                "Low": "green",
                "Moderate": "yellow",
                "High": "orange",
                "Very High": "red"
            }
    for column in df.columns:
        # Extract periods, exposures, and values for the current column
        data = pd.DataFrame(df[column].tolist(), index=df.index, columns=["Exposure", "Value"])
        data["Period"] = data.index
        data["Period"] = data["Period"].apply(lambda x: f"{x[0]}-{x[1]}")
        print(data)

        # Create the plot for the current column
        fig = px.bar(
            data,
            x="Period",
            y="Value",
            color="Exposure",
            color_discrete_map=color_map,
            title=f"Exposure Levels for {column}",
            labels={"Value": "Frequency", "Period": "Time Period"}
        )

        # Customize layout for readability
        fig.update_layout(
            showlegend=True,
            legend_title="Exposure Level",
            yaxis=dict(range=[0,1], constrain="range"),
            xaxis=dict(
                categoryorder="array",
                categoryarray=list(data["Period"])  # Use the exact order from your data
            )
        )

        # Display the chart
        st.plotly_chart(fig)


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
            height=400,
        )

        st.plotly_chart(fig)


    # Example Usage
    value_range = (450, 1000)
    threshold = 600
    intervals = [(600, 650), (650, 700), (700, 750), (750, 1000)]
    colors = ["green", "yellow", "orange", "red"]

    plot_hazard_intervals(value_range, threshold, intervals, colors)


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


def plot_exposure(df, score_name, min_thresholds, max_thresholds):
    
    score_name = " ".join(score_name.split("_")).title()

    df["color"] = df["yearly_indicator_season_precipitation"].apply(lambda category:CATEGORY_TO_COLOR_MAP[category])
    df["category"] = df["color"].apply(lambda color: RISK_MAP[color])
    # print(df["precipitation_sum_sum_season_precipitation"].min())
    fig = go.Figure()
    main_scatter_plot(fig, df, score_name)

    # Customize Layout
    data_min=df["precipitation_sum_sum_season_precipitation"].min()
    data_max=df["precipitation_sum_sum_season_precipitation"].max()
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
        fig.update_layout(
            title="Scatter Plot Template",
            xaxis=dict(title="X-axis Label"),
            yaxis=dict(
                title="Y-axis Label",
                range=[data_min - 0.05 * diff, data_max + 0.05 * diff]
            ),
            legend=dict(title="Legend Title"),
            template="plotly_white"
        )
            
       
        
    st.plotly_chart(fig)



def main_scatter_plot(fig:go.Figure, df, score_name):
    fig.add_trace(
        go.Scatter(
            x=df["period"],
            y=df["precipitation_sum_sum_season_precipitation"],
            mode="markers",  # Choose between "lines", "markers", or "lines+markers"
            marker=dict(
                size=15,  # Adjust marker size
                color=df["color"],  # Apply color mapping
                opacity=0.8,
                line=dict(width=1, color="black")  # Add border to markers
            ),
            text=df["category"],  # Hover text for each point
            customdata=df["year"],
            hovertemplate=(
                f"{score_name}: %{{y}}<br>" +
                "Category: %{text}<br>"+
                "Year: %{customdata}<br>"
            ),
            name=""  # Legend name
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
        opacity=0.5,
        layer="below",  # Place below the scatter points
        line_width=0  # No border
    )

def update_scatter_layout(fig:go.Figure, data_min, data_max, diff):
    fig.update_layout(
        title="Scatter Plot Template",
        xaxis=dict(title="X-axis Label"),
        yaxis=dict(
            title="Y-axis Label",
            range=[data_min - 0.05 * diff, data_max + 0.05 * diff]
        ),
        legend=dict(title="Legend Title"),
        template="plotly_white"
    )
