import streamlit as st
import plotly.graph_objects as go

# Initialize session state to store axis range
st.set_page_config(layout="wide")
if "x_range" not in st.session_state:
    st.session_state["x_range"] = None

# Callback function to update session state with new x-axis range
def update_ranges(value):
    if value:
        print(value)
    else:
        print("ciao")
    # fig2.update_xaxes(range=[min(x), max(x)])
    # fig2.update_yaxes(range=[min(y1), max(y1)])

# Create two example figures
x = [1, 2, 3, 4, 5]
y1 = [10, 20, 10, 15, 10]
y2 = [5, 15, 10, 10, 20]

fig1 = go.Figure(data=[go.Scatter(x=x, y=y1, mode="lines", name="Graph 1")])
fig2 = go.Figure(data=[go.Scatter(x=x, y=y2, mode="lines", name="Graph 2")])

fig1.update_xaxes(range=[2, 3])
fig1.update_yaxes(range=[min(y1), max(y1)])

    

# Display the first graph
what = st.plotly_chart(fig1, use_container_width=True,
                selection_mode=["box", "points"])
print("what", what)
print(what.selection)

st.plotly_chart(fig2, use_container_width=True)

