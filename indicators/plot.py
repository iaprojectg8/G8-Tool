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
        data["Period"] = data.index.astype(str)
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
            xaxis=dict(tickangle=45),
            showlegend=True,
            legend_title="Exposure Level",
        )

        # Display the chart
        st.plotly_chart(fig)