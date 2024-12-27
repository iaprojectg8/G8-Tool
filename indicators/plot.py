from utils.imports import *
from utils.variables import *
from indicators.calculation import categorize_both



def plot_daily_data(df, variable):
    df = df[variable].reset_index()
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df[variable],
            marker=dict(color="skyblue"),
            name= variable
        )
    )

    fig.update_layout(
        title=f"Daily {variable}",
        xaxis_title="Date",
        yaxis_title=variable,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True),
        template="plotly_white"
    )
    st.plotly_chart(fig)




def plot_years_exposure(df, aggregated_column_name, min_thresholds, max_thresholds, score_name, unit):
    
    

    # print(df["precipitation_sum_sum_season_precipitation"].min())
    fig = go.Figure()
    main_scatter_plot(fig, df, aggregated_column_name, score_name, unit)

    # Customize Layout
    data_min=df[aggregated_column_name].min()
    data_max=df[aggregated_column_name].max()
    diff = abs(data_max-data_min)
    
    
    # Add threshold backgrounds as shapes
    if min_thresholds!=[]:
        last_min=data_min-diff*0.05
    if max_thresholds!=[]:
        last_max=data_max+diff*0.05

    if min_thresholds!= [] and len(min_thresholds)<5:
        min_thresholds.append(last_min)
    if max_thresholds!= [] and len(max_thresholds)<5:
        max_thresholds.append(last_max)

    for threshold_index in range(max(len(max_thresholds), len(min_thresholds))):
        if threshold_index == 0 :
            if max_thresholds==[]:
                add_background_color(fig, threshold_index, 
                                 y0=min_thresholds[threshold_index], 
                                 y1=data_max+diff*0.05)
            elif min_thresholds==[]:
                add_background_color(fig, threshold_index, 
                                 y0=data_min-diff*0.05, 
                                 y1=max_thresholds[threshold_index])
            
            else:
                add_background_color(fig, threshold_index, 
                                    y0=min_thresholds[threshold_index], 
                                    y1=max_thresholds[threshold_index])
            
        else:
            
            if min_thresholds:
                add_background_color(fig, threshold_index, 
                                    y0=min_thresholds[threshold_index], 
                                    y1=min_thresholds[threshold_index-1])
            if max_thresholds:
                add_background_color(fig, threshold_index, 
                                    y0=max_thresholds[threshold_index-1], 
                                    y1=max_thresholds[threshold_index])
    update_scatter_layout(fig, data_min, data_max, diff, df, score_name, unit)
        
    st.plotly_chart(fig)




def main_scatter_plot(fig: go.Figure, df, aggregated_column_name, score_name, unit):
    """
    Add scatter plot traces to the given figure for each category, ensuring
    that the legend is ordered according to the provided `risk_order`.

    Args:
        fig (go.Figure): The figure to which the traces are added.
        df (pd.DataFrame): DataFrame containing the data to be plotted.
        aggregated_column_name (str): The column in the DataFrame to be plotted on the Y-axis.
        risk_order (list): The desired order of the categories for the legend (e.g., ["Low", "Medium", "High"]).
    """
    legend_column_name = " ".join(aggregated_column_name.split("_")).title()

    # Ensure that the 'category' column is ordered according to risk_order
    risk_order  = sorted(PROB_MAP, key=PROB_MAP.get)
    df["category"] = pd.Categorical(df["category"], categories=risk_order, ordered=True)
    df["period"] = pd.Categorical(df["period"], categories=sorted(df["period"].unique()), ordered=True)

    # Iterate over the categories in the desired order (risk_order)
    for category in risk_order:
        category_data = df[df["category"] == category]
        
        fig.add_trace(
            go.Scatter(
                x=category_data["period"],
                y=category_data[aggregated_column_name],
                mode="markers",
                marker=dict(
                    size=10,
                    color=category_data["color"],  # Assuming color column exists
                    opacity=0.9,
                    line=dict(width=1, color="grey")
                ),
                text=category_data["category"],  # Hover text
                customdata=category_data["year"],
                hovertemplate=(
                    f"{score_name}: %{{y}}<br>" +
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


def update_scatter_layout(fig:go.Figure, data_min, data_max, diff, df,score_name, unit):
    legend_name = f"{score_name} ({unit})"
    # variable_legend_name = " ".join(variable.split("_")).title()
    fig.update_layout(
        title=dict(text=f"Yearly {score_name} over Periods ",
                    x=0.5,
                    xanchor="center",
                    font_size=25),
        xaxis=dict(tickfont_size=15,
                    tickangle=37 ,
                    categoryorder="array",
                    categoryarray=list(df["period"].cat.categories),  # Explicit period order
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
        legend=dict(title=dict(text="Categories",
                       font=dict(size=20, color="white",weight=900),
                               side="top center",
    
                               ),
                    
                    orientation="v", 
                    traceorder="reversed",
                    x=1.05,           
                    y=0.5,
                    ),
        font=dict(
            size=17),
    )











# ----------------------------------------
# --- Plot deficit and excess exposure ---
# ----------------------------------------

def plot_exposure_through_period(df:pd.DataFrame,score_name):
    
    score_counts  = df.groupby('period')[f"yearly_indicator_{score_name}"].value_counts().unstack(fill_value=0)
    periods_size = df.groupby('period').size().max()
    # Split the DataFrame into negatives, positives, and zeros
    negative_df = score_counts[score_counts.columns[score_counts.columns.astype(int) < 0]]
    positive_df = score_counts[score_counts.columns[score_counts.columns.astype(int) > 0]]
    zero_df = score_counts[score_counts.columns[score_counts.columns.astype(int) == 0]]

    # Sort the negative DataFrame for stacking
    negative_df = negative_df[sorted(negative_df.columns, key=int, reverse=True)]

    # Plot negative scores
    fig = go.Figure()

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

    

    # Customize layout
    fig.update_layout(
        barmode="relative",  # Stack bars relatively
        title=dict(text=f"Period Budget about {score_name}",
                    x=0.5,
                    xanchor="center",
                    font_size=25),
        xaxis=dict(tickfont_size=15,
                   tickangle=37,
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
        legend=dict(title=dict(text="Risk Levels",
                               font=dict(size=20, color="white",weight=900),
                               side="top center",
    
                               ),
                    
                    orientation="v", 
                    traceorder="reversed",
                    x=1.05,           
                    y=0.5,
                    ),
        font=dict(
            size=17),
        autosize=True,
        # paper_bgcolor="purple"
    )

    st.plotly_chart(fig)





# ----------------------------------------
# --- Plot global exposure through agg ---
# ----------------------------------------


def calculate_category_score(value):
    if value<0:
        return -value
    else :
        return value
def apply_my_dict(value, dico):
    return dico[value]


def plot_global_exposure(df_yearly:pd.DataFrame, score_name, index, variable, below_thresholds, above_thresholds):
    score_column = f"yearly_indicator_{score_name}"
    
    aggregation_type = st.selectbox(label="Aggregation Type", options=EXPOSURE_AGGREGATION, key=f"aggregation_type{index}")
    if aggregation_type == "Category Mean":
        df_yearly["absolute_score"] = df_yearly[score_column].apply(calculate_category_score)
        df_period = df_yearly.groupby("period", as_index=False)["absolute_score"].mean()

        # Apply np.ceil to round the scores to the next integer
        df_period["absolute_score"] = np.round(df_period["absolute_score"])
        # Map the "absolute_score" to the category
        df_period["category"] = df_period["absolute_score"].apply(lambda x : apply_my_dict(x, CATEGORY_TO_RISK))
    elif aggregation_type == "Variable Mean Category":
        df_period=pd.DataFrame()
        df_period[variable+"_mean"] = df_yearly.groupby("period")[variable].mean()
        df_period=df_period.reset_index()
        df_period[f"absolute_score"] = (df_period[variable+"_mean"].apply(lambda x:categorize_both(x,below_thresholds, above_thresholds) )).astype(int)
        df_period["category"] = df_period["absolute_score"].apply(lambda x : apply_my_dict(x, CATEGORY_TO_RISK))
    elif aggregation_type == "Most Frequent Category":
        df_yearly["absolute_score"] = df_yearly[score_column].apply(calculate_category_score)
        df_period =  df_yearly.groupby('period')['absolute_score'].agg(lambda x: max(x.mode()))
        df_period = df_period.reset_index()
        # Apply np.ceil to round the scores to the next integer
        df_period["absolute_score"] = np.round(df_period["absolute_score"])
        # Map the "absolute_score" to the category
        df_period["category"] = df_period["absolute_score"].apply(lambda x : apply_my_dict(x, CATEGORY_TO_RISK))
        

    df_period["color"] = df_period["category"].apply(lambda x : apply_my_dict(x, RISK_TO_COLOR))
    df_period["exposure_prob"] = df_period["category"].apply(lambda x : apply_my_dict(x, PROB_MAP))

    with st.expander("Show Exposure Dataframe"):
        st.dataframe(df_period, height=DATAFRAME_HEIGHT, use_container_width=True)

    desired_order = list(df_period["period"].unique())
    # Create a list of traces (one for each category)
    traces = []
    # categories = df_period["category"].unique()
    risk_order  = sorted(PROB_MAP, key=PROB_MAP.get)

    # df_period["category"] = pd.Categorical(df_period["category"], categories=categories, ordered=True)
    df_period["period"] = pd.Categorical(df_period["period"], categories=sorted(df_period["period"].unique()), ordered=True)

    # Ensure 'category' is ordered correctly for the legend (risk order)
    df_period["category"] = pd.Categorical(df_period["category"], categories=risk_order, ordered=True)

    # print(categories)
    for category in risk_order:
        filtered_data = df_period[df_period["category"] == category]
        traces.append(
            go.Bar(
                x=filtered_data["period"],
                y=filtered_data["exposure_prob"],
                name=category,  # Use category as the legend name
                marker_color=RISK_TO_COLOR.get(category, "#000000"),  # Map color or fallback to black
                hovertemplate=(
                    f"Category: {category}<br>" +
                    "Probability: %{y}<br>")
            ),
        )

    # Create the figure
    fig = go.Figure(data=traces)

    fig.update_layout(
        title=dict(text=f"{score_name} Exposure over Periods",
                    x=0.5,
                    xanchor="center",
                    font_size=25),
        xaxis=dict(tickfont_size=15,
                   tickangle=37 ,
                    title = dict(
                        text="Periods",
                        font_size=17,
                        standoff=50), 
                        # categoryorder="array", 
                        categoryarray=desired_order,     
                    ticklabelstandoff =20),
        yaxis=dict(tickfont_size=15,
                    range=[0,1],
                    title=dict(
                        text="Exposure Probability",
                        font_size=17,
                        standoff=50),
                    ticklabelstandoff = 20),
        legend=dict(title=dict(text="Risk Levels",
                       font=dict(size=20, color="white",weight=900),
                               side="top center",
    
                               ),
        
                    orientation="v", 
                    traceorder="reversed",
                    x=1.05,           
                    y=0.5,
                    ),
        font=dict(
            size=17),
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig)


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


