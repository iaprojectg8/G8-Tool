from utils.imports import *
from utils.variables import DATAFRAME_HEIGHT
from lib.data_process import loads_data, column_choice
from indicators.parametrization import * 
from layouts.layout import *
from lib.widget import * 
from indicators.calculation import *
from lib.session_variables import *
from lib.data_process import *
from lib.plot import *
from indicators.plot import *


def main():
    """Basic Streamlit app with a title."""
    # Set some layout parameters for the page 
    st.set_page_config(layout="wide")
    set_page_title("Indicators Customization")
    set_title_2("Period")
    # Loading CSV 
    long_period = (long_period_start, long_period_end) = select_period()

    # Period cut
    smaller_period_length  = st.select_slider("Choose the length of smaller period to see the evolution of your data on them:",options=PERIOD_LENGTH)
    periods = split_into_periods_indicators(smaller_period_length, long_period_start, long_period_end)
    filename = "CSV_files/cmip6_era5_data_daily_0.csv"
    all_data = loads_data(filename=filename)
    data_long_period_filtered = period_filter(all_data, period=long_period)
    st.dataframe(data_long_period_filtered, height=DATAFRAME_HEIGHT, use_container_width=True)
    

    set_title_2("Variable Choice")
    df_chosen = column_choice(data_long_period_filtered)

    season_start, season_end = None, None
    all_year_data = pd.DataFrame()
    if not df_chosen.empty:
        print(type(df_chosen))
        st.dataframe(df_chosen, height=DATAFRAME_HEIGHT, use_container_width=True)
        all_year_data = df_chosen  
        

        set_title_2("Season Choice")
        if st.checkbox("Need a season or a period study", value=True):
            season_start, season_end = select_season()
            df_season = select_data_contained_in_season(df_chosen, season_start, season_end)
        else:
            df_season = df_chosen
        st.dataframe(df_season, height=DATAFRAME_HEIGHT, use_container_width=True)

        
        
        # Initialize indicators
        set_title_2("Parametrize Indictors")
        # Create tabs to separate the two parts
        tab1, tab2 = st.tabs(["Create/Update Indicator", "Edit Existing Indicators"])

        # Tab 1: Create or Update an Indicator
        with tab1:
            indicator_building(df_season, season_start, season_end)

        # Tab 2: Display and Edit Existing Indicators
        with tab2:
            indicator_editing(df_season, season_start, season_end)

        # Show the dataframe
        if not st.session_state.df_indicators.empty:
            st.dataframe(st.session_state.df_indicators, use_container_width=True)




        # file_upload = st.checkbox(label="Upload your CSV indicator configuration")
        # if file_upload :
        #     df = upload_csv_file()
        # else :
        #     df = create_empty_dataframe()
        # df_indicator_paramters = create_dynamic_dataframe(df, df_season.columns)

        # Need to calculate score with this parameters
        set_title_2("Indicators calculation")
        df_yearly = calculate_score(df_season, st.session_state.df_indicators,all_year_data, season_start, season_end, periods)
        # if not df_yearly.empty:
        #     df_yearly["year"] = df_yearly.index.year
        #     df_yearly = add_periods_to_df(df_yearly, periods)

            # set_title_2("Frequency thresholds")
            # threshold1, threshold2, threshold3 = get_frequency_threshold_inputs()
        
            # df_yearly = df_yearly.groupby("period").sum().filter(like="yearly_indicator").div(df_yearly.groupby("period").size(), axis=0)
            # score_counts = df_yearly.groupby('period')[f"yearly_indicator{score}"].value_counts().unstack(fill_value=0)
            # st.dataframe(df_yearly, height=DATAFRAME_HEIGHT, use_container_width=True)

            # Apply the function and separate results
            # This is just for the user 
            # df_yearly_background = copy(df_yearly)
            # for col in df_yearly.columns:
            #     df_yearly[f"{col}_Category"] = df_yearly[col].apply(
            #         lambda x: classify_exposure(x, threshold1, threshold2, threshold3)
            #     )
            # df_yearly_background = df_yearly_background.map(lambda x: classify_frequency_by_exposure(x, threshold1, threshold2, threshold3))

            # if not df_yearly_background.empty :# df_yearly = df_yearly.applymap(lambda x: classify_frequency_by_exposure(x, threshold1, threshold2, threshold3))
            #     st.dataframe(df_yearly,height=DATAFRAME_HEIGHT, use_container_width=True)      

            #     # df_yearly = df_yearly.apply(classify_desirability_score)

            #     set_title_2("Exposure Plot")
            #     plot_exposure_through_period(df_yearly_background)


if "__main__":
    main()