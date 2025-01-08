from utils.imports import *
from utils.variables import *
from indicators.calculation import categorize_both
from lib.plot import add_vertical_line


# --------------------------------------------
# --- Plot daily data for a given variable ---
# --------------------------------------------

# Plot function
def daily_data_plot(df:pd.DataFrame, fig:go.Figure, variable:str):
    
    # Add a scatter plot trace for the variable
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df[variable],
            marker=dict(color="skyblue"),
            name=variable
        )
    )

# Layout function
def daily_data_update_layout(fig:go.Figure, variable:str):

    # Update the layout of the figure
    fig.update_layout(
        title=dict(
            text=f"Distribution of Daily {' '.join(variable.split('_')).title()}",
            x=0.5,
            xanchor="center",
            font_size=25
        ),
        xaxis=dict(
            tickfont_size=15,
            title=dict(
                text="Date",
                font_size=17,
                standoff=50
            ),
            ticklabelstandoff=20
        ),
        yaxis=dict(
            tickfont_size=15,
            title=dict(
                text=f"Daily {' '.join(variable.split('_')).title()}",
                font_size=17,
                standoff=50
            ),
            ticklabelstandoff=20
        ),
        legend=dict(
            title=dict(
                text="Risk Levels",
                font=dict(size=20, color="white", weight=900),
                side="top center"
            ),
            orientation="v",
            traceorder="reversed",
            x=1.05,
            y=0.5,
        ),
        font=dict(size=17),
        autosize=True
    )

# Main function
def plot_daily_data(df, variable, zoom=None):
    """
    Plots the daily data for a given variable using Plotly and Streamlit.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        variable (str): The variable to plot.
    """
    # Reset the index and extract the relevant data
    df = df[variable].reset_index()

    fig = go.Figure()
    daily_data_plot(df, fig, variable)
    add_vertical_line(fig, year=datetime.now(pytz.utc))
    daily_data_update_layout(fig, variable)
    st.plotly_chart(fig)
    


# -----------------------------------------
# --- Plot yearly exposure through time ---
# -----------------------------------------

## Plot part
def yearly_exposure_plot(fig: go.Figure, df, aggregated_column_name, score_name):
    """
    Plots the yearly exposure data for each category over time.

    Args:
        fig (go.Figure): The Plotly figure to add the traces to.
        df (pd.DataFrame): The DataFrame containing the data.
        aggregated_column_name (str): The name of the column containing the aggregated data.
        score_name (str): The name of the score to display.
    """

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
                    color=category_data["color"],
                    opacity=0.9,
                    line=dict(width=1, color="grey")
                ),
                text=category_data["category"],
                customdata=category_data["year"],
                hovertemplate=(
                    f"{score_name}: %{{y}}<br>" +
                    "Category: %{text}<br>" +
                    "Year: %{customdata}<br>"
                ),
                name=category,
                showlegend=True
            )
        )


# Background part
def add_last_threshold(min_thresholds, max_thresholds, data_min, data_max, diff):    
    """
    Adds the last threshold to the list of thresholds in order to build all background frames.
    
    Args:
        min_thresholds (list): The list of minimum thresholds.
        max_thresholds (list): The list of maximum thresholds.
        data_min (float): The minimum value of the data.
        data_max (float): The maximum value of the data.
        diff (float): The difference between the maximum and minimum values.
    """
    # Adding another threshold to make the background cover all the data
    if min_thresholds!=[]:
        last_min=data_min-diff*0.05
    if max_thresholds!=[]:
        last_max=data_max+diff*0.05

    if min_thresholds!= [] and len(min_thresholds)<5:
        min_thresholds.append(last_min)
    if max_thresholds!= [] and len(max_thresholds)<5:
        max_thresholds.append(last_max)

def add_background_color(fig:go.Figure, threshold_index, y0, y1):
    """
    Adds a background color to the plot based on the given threshold index and y-values.

    Args:
        fig (go.Figure): The Plotly figure to add the background to.
        threshold_index (int): The index of the threshold.
        y0 (float): The lower y-value of the background.
        y1 (float): The upper y-value of the background.
    """
    fig.add_shape(
        type="rect",
        xref="paper",  # Use entire plot width for the rectangles
        x0=0, x1=1,  # Entire plot width
        yref="y",
        y0=y0,  
        y1=y1,  
        fillcolor=THRESHOLD_COLORS[threshold_index],  
        opacity=0.25,
        layer="below",  # Place below the scatter points
        line_width=0,  # No border
    )

def add_all_background(min_thresholds, max_thresholds, data_min, data_max, diff, fig):
    """
    Adds all background colors to the plot based on the given thresholds.

    Args:
        min_thresholds (list): The list of minimum thresholds.
        max_thresholds (list): The list of maximum thresholds.
        data_min (float): The minimum value of the data.
        data_max (float): The maximum value of the data.
        diff (float): The difference between the maximum and minimum values.
        fig (go.Figure): The Plotly figure to add the background to.
    """
    # Iterates over the thresholds to add the background colors
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
                

# Layout part
def yearly_exposure_update_layout(fig:go.Figure, data_min, data_max, diff, df,score_name, unit):
    """
    Updates the layout of the yearly exposure plot.
    
    Args:
        fig (go.Figure): The Plotly figure to update the layout of.
        data_min (float): The minimum value of the data.
        data_max (float): The maximum value of the data.
        diff (float): The difference between the maximum and minimum values.
        df (pd.DataFrame): The DataFrame containing the data.
        score_name (str): The name of the score to display.
        unit (str): The unit of the score
    """
    legend_name = f"{score_name} ({unit})"
    
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
                                side="top center"
                               ),
                    
                    orientation="v", 
                    traceorder="reversed",
                    x=1.05,           
                    y=0.5,
                    ),
        font=dict(
            size=17))

# Main function
def plot_years_exposure(df, aggregated_column_name, min_thresholds, max_thresholds, score_name, unit):
    """
    Plots the yearly exposure data for each category over time using Plotly and Streamlit.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        aggregated_column_name (str): The name of the column containing the aggregated data.
        min_thresholds (list): The list of minimum thresholds.
        max_thresholds (list): The list of maximum thresholds.
        score_name (str): The name of the score to display.
        unit (str): The unit of the score
    """

    fig = go.Figure()

    # Main plot
    yearly_exposure_plot(fig, df, aggregated_column_name, score_name)

    # Get the min and max values of the data and make the difference
    data_min=df[aggregated_column_name].min()
    data_max=df[aggregated_column_name].max()
    diff = abs(data_max-data_min)
    
    # Background
    add_last_threshold(min_thresholds, max_thresholds, data_min, data_max, diff)
    add_all_background(min_thresholds, max_thresholds, data_min, data_max, diff, fig)
    
    # Layout
    yearly_exposure_update_layout(fig, data_min, data_max, diff, df, score_name, unit)
        
    st.plotly_chart(fig)




# ----------------------------------------
# --- Plot deficit and excess exposure ---
# ----------------------------------------

def no_risk_plot(zero_df, fig:go.Figure):
    """
    Plots the zero values as a line for the "No Risk" category.

    Args:
        zero_df (pd.DataFrame): The DataFrame containing the zero values.
        fig (go.Figure): The Plotly figure to add the zero values to.
    """

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

def excess_exposure_plot(positive_df, fig:go.Figure):
    """
    Plots the positive values as bars for the excess exposure.

    Args:
        positive_df (pd.DataFrame): The DataFrame containing the positive values.
        fig (go.Figure): The Plotly figure to add the positive values to. 
    """
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
def deficit_exposure_plot(negative_df, fig:go.Figure):
    """
    Plots the negative values as bars for the deficit exposure.

    Args:  
        negative_df (pd.DataFrame): The DataFrame containing the negative values.
        fig (go.Figure): The Plotly figure to add the negative values to.
    """
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


def deficit_and_excess_exposure_update_layout(fig:go.Figure, periods_size, score_name):
    """
    Updates the layout of the deficit and excess exposure plot.

    Args:
        fig (go.Figure): The Plotly figure to update the layout of.
        periods_size (int): The maximum number of periods in the data.
        score_name (str): The name of the score to display.
    """
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
    )

def get_score_then_exposure(df, score_name):
    """
    Calculates the counts of the scores for each period and splits the DataFrame into negatives, positives, and zeros.

    Args:  
        df (pd.DataFrame): The DataFrame containing the data.
        score_name (str): The name of the score to display.
    """
    # Calculate the counts of the scores for each period
    score_counts  = df.groupby('period', observed=False)[f"yearly_indicator_{score_name}"].value_counts().unstack(fill_value=0)
    periods_size = df.groupby('period', observed=False).size().max()
    
    # Split the DataFrame into negatives, positives, and zeros
    negative_df = score_counts[score_counts.columns[score_counts.columns.astype(int) < 0]]
    positive_df = score_counts[score_counts.columns[score_counts.columns.astype(int) > 0]]
    zero_df = score_counts[score_counts.columns[score_counts.columns.astype(int) == 0]]

    # Sort the negative DataFrame for stacking
    negative_df = negative_df[sorted(negative_df.columns, key=int, reverse=True)]

    return periods_size, negative_df, positive_df, zero_df

def plot_deficit_and_excess_exposure(df:pd.DataFrame,score_name):
    """
    Plots the deficit and excess exposure data for each category over time using Plotly and Streamlit.

    Args:  
        df (pd.DataFrame): The DataFrame containing the data.
        score_name (str): The name of the score to display.
    """
    fig = go.Figure()

    # Get the score counts and split the DataFrame follwing the exposure sign
    periods_size, negative_df, positive_df, zero_df = get_score_then_exposure(df, score_name)

    # Plot exposure
    no_risk_plot(zero_df, fig)
    deficit_exposure_plot(negative_df, fig)
    excess_exposure_plot(positive_df, fig)

    # Layout
    deficit_and_excess_exposure_update_layout(fig, periods_size, score_name)
    st.plotly_chart(fig)



# ----------------------------------------
# --- Plot global exposure through agg ---
# ----------------------------------------

# Util functions
def calculate_category_score(value):
    """
    Calculate the category score based on the value.

    Args:
        value (float): The value to categorize.

    Returns:
        int: The category score.
    """
    if value<0:
        return -value
    else :
        return value
        

# Aggregation functions
def category_mean_aggregation(df_yearly: pd.DataFrame, score_column: str) -> pd.DataFrame:
    """
    Calculate the mean category score for each period.

    Args:
        df_yearly (pd.DataFrame): DataFrame containing yearly data.
        score_column (str): The column name of the score to be aggregated.

    Returns:
        pd.DataFrame: DataFrame with the mean category score and corresponding risk category for each period.
    """
    # Get all the score positive to make them global and be able to calculate the mean
    df_yearly["absolute_score"] = df_yearly[score_column].apply(calculate_category_score)
    df_period = df_yearly.groupby("period", as_index=False, observed=False)["absolute_score"].mean().round()
    # Map the mean absolute score to the corresponding risk category
    df_period["category"] = df_period["absolute_score"].apply(CATEGORY_TO_RISK.get)
    
    return df_period

def variable_mean_category_aggregation(df_yearly: pd.DataFrame, variable: str, below_thresholds: list, above_thresholds: list) -> pd.DataFrame:
    """
    Calculate the mean value of a variable for each period and categorize it.

    Args:
        df_yearly (pd.DataFrame): DataFrame containing yearly data.
        variable (str): The column name of the variable to be aggregated.
        below_thresholds (list): List of thresholds for categorizing below values.
        above_thresholds (list): List of thresholds for categorizing above values.

    Returns:
        pd.DataFrame: DataFrame with the mean variable value, absolute score, and corresponding risk category for each period.
    """
    df_period = df_yearly.groupby("period", observed=False)[variable].mean().reset_index()
    # Gives a score to the period variable mean
    df_period["absolute_score"] = df_period[variable].apply(lambda x: categorize_both(x, below_thresholds, above_thresholds))
    # Map the absolute score to the corresponding risk category
    df_period["category"] = df_period["absolute_score"].apply(CATEGORY_TO_RISK.get)
    
    return df_period

def most_frequent_category_aggregation(df_yearly: pd.DataFrame, score_column: str) -> pd.DataFrame:
    """
    Calculate the most frequent category score for each period.

    Args:
        df_yearly (pd.DataFrame): DataFrame containing yearly data.
        score_column (str): The column name of the score to be aggregated.

    Returns:
        pd.DataFrame: DataFrame with the most frequent category score and corresponding risk category for each period.
    """
    # Get all the score positive to make them global and be able to calculate the mode
    df_yearly["absolute_score"] = df_yearly[score_column].apply(calculate_category_score)
    # Calculating the mode
    df_period = df_yearly.groupby('period', observed=False)['absolute_score'].agg(lambda x: max(x.mode())).round().reset_index()
    # Map the absolute score to the corresponding risk category
    df_period["category"] = df_period["absolute_score"].apply(CATEGORY_TO_RISK.get)
    
    return df_period

def aggregate_category(aggregation_type, df_yearly, score_column, variable, below_thresholds, above_thresholds):
    """
    Aggregate the data based on the chosen aggregation type.

    Args:
        aggregation_type (str): The chosen aggregation type.
        df_yearly (pd.DataFrame): DataFrame containing yearly data.
        score_column (str): The column name of the score to be aggregated.
        variable (str): The column name of the variable to be aggregated.
        below_thresholds (list): List of thresholds for categorizing below values.
        above_thresholds (list): List of thresholds for categorizing above values.
    
    Returns:
        pd.DataFrame: DataFrame with the aggregated data.
    """
    if aggregation_type == "Category Mean":
        df_period = category_mean_aggregation(df_yearly, score_column)
    elif aggregation_type == "Variable Mean Category":
        df_period = variable_mean_category_aggregation(df_yearly, variable, below_thresholds, above_thresholds)
    elif aggregation_type == "Most Frequent Category":
        df_period = most_frequent_category_aggregation(df_yearly, score_column)
    return df_period


# Work on the df_period
def work_on_df_period(df_period):
    df_period["color"] = df_period["category"].apply(RISK_TO_COLOR.get)
    df_period["exposure_prob"] = df_period["category"].apply(PROB_MAP.get)

    # Sorts the periods and risk levels
    desired_order = list(df_period["period"].unique())
    risk_order  = sorted(PROB_MAP, key=PROB_MAP.get)

    # Makes some columns categorical for ordering in the plot
    df_period["period"] = pd.Categorical(df_period["period"], categories=sorted(df_period["period"].unique()), ordered=True)
    df_period["category"] = pd.Categorical(df_period["category"], categories=risk_order, ordered=True)
    return desired_order, risk_order

# Plot function
def global_exposure_plot(risk_order, df_period, traces):
    """
    Plots the global exposure data for each category over time.

    Args:
        risk_order (list): The order of the risk levels.
        df_period (pd.DataFrame): The DataFrame containing the data.
        traces (list): The list of traces to add the data to.
    """
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

# Layout function
def global_exposure_update_layout(fig:go.Figure, score_name, desired_order):
    """
    Updates the layout of the global exposure plot.

    Args:
        fig (go.Figure): The Plotly figure to update the layout of.
        score_name (str): The name of the score to display.
        desired_order (list): The desired order of the periods
    """
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
            size=17))
    
# Main function
def plot_global_exposure(df_yearly:pd.DataFrame, score_name, index, variable, below_thresholds, above_thresholds):
    """
    Plots the global exposure data for each category over time using Plotly and Streamlit.

    Args:
        df_yearly (pd.DataFrame): The DataFrame containing the data.
        score_name (str): The name of the score to display.
        index (int): The index of the plot.
        variable (str): The variable to plot.
        below_thresholds (list): List of thresholds for categorizing below values.
        above_thresholds (list): List of thresholds for categorizing above values.
    """
    # Get the score_column
    score_column = f"yearly_indicator_{score_name}"
    
    # Asks the user to choose the aggregation type and then aggregates the data
    aggregation_type = st.selectbox(label="Aggregation Type", options=EXPOSURE_AGGREGATION, key=f"aggregation_type_{index}")
    df_period = aggregate_category(aggregation_type, df_yearly, score_column, variable, below_thresholds, above_thresholds)

    # Sorts the periods and risk levels
    desired_order, risk_order = work_on_df_period(df_period)

     # Offers the possibility to show the dataframe
    with st.expander("Show Exposure Dataframe"):
        st.dataframe(df_period, height=DATAFRAME_HEIGHT, use_container_width=True)

    # Plots the global exposure
    traces = []
    global_exposure_plot(risk_order, df_period, traces)
    fig = go.Figure(data=traces)

    # Updates the layout
    global_exposure_update_layout(fig, score_name, desired_order)
    st.plotly_chart(fig)

