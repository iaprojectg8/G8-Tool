from utils.imports import *
from utils.variables import *
from layouts.layout import *


def classify_heat_index(heat_index):
    if heat_index < 27:
        return 'Low Discomfort'
    elif 27 <= heat_index < 32:
        return 'Moderate Discomfort'
    elif 32 <= heat_index < 39:
        return 'High Discomfort'
    else:
        return 'Very High Discomfort'
    
def heat_index(df, rh, tmp_2m):
    c1, c2, c3, c4, c5, c6, c7, c8, c9 = (-42.379, 2.04901523, 10.14333127, -0.22475541, -0.00683783,
                                      -0.05481717, 0.00122874, 0.00085282, -0.00000199)

    df["heat_index"] = (c1 + c2 * df[tmp_2m] + c3 * df[rh] + c4 * df[tmp_2m] * df[rh] + c5 * df[tmp_2m]**2 +
      c6 * df[rh]**2 + c7 * df[tmp_2m]**2 * df[rh] + c8 * df[tmp_2m] * df[rh]**2 + c9 * df[tmp_2m]**2 * df[rh]**2)
    return df

def plot_bar_stack_count(df):
    category_counts = df.groupby(['year', 'heat_index_category']).size().reset_index(name='count')

    # Create a stacked bar plot using Plotly
    fig = px.bar(
        category_counts,
        x='year',
        y='count',
        color='heat_index_category',
        title="Heat Index Categories by Year",
        labels={'count': 'Count of Days', 'year': 'Year'},
        color_discrete_map={
            'Low Discomfort': '#A0D3F1',
            'Moderate Discomfort': '#FFD700',
            'High Discomfort': '#FF6347',
            'Very High Discomfort': '#FF0000'
        }
    )



    fig.update_layout(
        barmode='stack',
        title=dict(text=f"Heat Index Through Years",
                    x=0.5,
                    xanchor="center",
                    font_size=25),
        xaxis=dict(tickfont_size=15,
                    title = dict(
                        text="Year",
                        font_size=17,
                        standoff=50),       
                    ticklabelstandoff =20),
        yaxis=dict(tickfont_size=15,
                    title=dict(
                        text="Count of Days",
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
        font=dict(
            size=17))

    # Show the Plotly chart in Streamlit
    st.plotly_chart(fig)

def categorize_heat_index(df):
    
    df['heat_index_category'] = df['heat_index'].apply(classify_heat_index)
    df['year'] = df.index.year

    category_order = ['Low Discomfort', 'Moderate Discomfort', 'High Discomfort', 'Very High Discomfort']
    df['heat_index_category'] = pd.Categorical(df['heat_index_category'], categories=category_order, ordered=True)



def main():
    set_page_title("Moroni Calculaltion")
    set_title_1("Variable filter")
    st.write("We are keeping only the daily max temperature and the daily mean relative humidity")
    df = pd.read_csv("Overall_Average.csv", index_col="date", parse_dates=True)
    print(df.head())

    rh = "relative_humidity_2m_mean"
    tmp_2m = "temperature_2m_max"
    prec = "precipitation_sum"
    df_hi = df[[tmp_2m, rh]]
    print("max temp",df_hi[tmp_2m].max())
    st.dataframe(df_hi, height=DATAFRAME_HEIGHT, use_container_width=True)

    df_hi[tmp_2m] = df_hi[tmp_2m]  * 9/5 + 32  # Convert Celsius to Fahrenheit

    df_hi = heat_index(df_hi, rh, tmp_2m)
    st.dataframe(df_hi, height=DATAFRAME_HEIGHT, use_container_width=True)
    df_hi["heat_index"] = (df_hi["heat_index"]-32)*5/9
    df_hi[tmp_2m] = (df_hi[tmp_2m]-32)*5/9
    st.dataframe(df_hi, height=DATAFRAME_HEIGHT, use_container_width=True)
    print(df_hi["heat_index"].max())
    categorize_heat_index(df_hi)
    plot_bar_stack_count(df_hi)

if "__main__":
    main()