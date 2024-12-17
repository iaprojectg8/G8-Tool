from utils.imports import *
from utils.variables import *
from indicators.calculation import *
from indicators.plot import *

def calculate_score(df_season, df_indicators_parameters: pd.DataFrame,all_year_data, season_start, season_end,periods):
    
    # Store all newly created columns in a dictionary to merge later

    df_yearly = pd.DataFrame()
    tabs = st.tabs(list(df_indicators_parameters["Name"].values))



    for i, row in df_indicators_parameters.iterrows():
        with tabs[i]:
            variable = row["Variable"]
            score_name = row["Name"]
            season_start_shift=row["Season Start Shift"]
            season_end_shift= row["Season End Shift"]
            below_thresholds=row["Yearly Threshold Min List"]
            above_thresholds= row["Yearly Threshold Max List"]

            df_season_temp=df_season[[variable]]
            # if row["Season Shift Start"] is not None:
            if season_start_shift is not None and season_end_shift is not None:
                st.dataframe(all_year_data, height=DATAFRAME_HEIGHT, use_container_width=True) 
                df_season_temp = all_year_data[(all_year_data.index.month >= season_start-season_start_shift) 
                                        & (all_year_data.index.month <= season_end+season_end_shift)]
            elif season_start_shift is not None:
                st.dataframe(all_year_data, height=DATAFRAME_HEIGHT, use_container_width=True) 
                df_season_temp = all_year_data[(all_year_data.index.month >= season_start-season_start_shift) & (all_year_data.index.month <= season_end)]
            elif season_end_shift is not None:
                st.dataframe(all_year_data, height=DATAFRAME_HEIGHT, use_container_width=True) 
                df_season_temp = all_year_data[(all_year_data.index.month >= season_start) & (all_year_data.index.month <= season_end+season_end_shift)]


            if row["Indicator Type"] == "Season Aggregation":
                # Perform yearly aggregation

                df_yearly_var, aggregated_column_name = make_yearly_agg(df_season_temp, score_name,variable, row["Yearly Aggregation"])

        
                df_yearly_var = indicator_score(
                    df_yearly_var,
                    aggregated_column_name,
                    score_name,
                    row["Yearly Threshold Min List"],
                    row["Yearly Threshold Max List"]
                )

            elif row["Indicator Type"] == "Outlier Days":
                df_daily, indicator_column = daily_indicators(df_season_temp, variable, row["Daily Threshold Min"], row["Daily Threshold Max"])
                with st.expander("Show Daily Dataframe"):
                    st.dataframe(df_daily, height=DATAFRAME_HEIGHT,use_container_width=True)

                df_yearly_var, aggregated_column_name = make_yearly_agg(df_season_temp, score_name,indicator_column, row["Yearly Aggregation"])
                df_yearly_var = indicator_score(
                    df_yearly_var,
                    aggregated_column_name,
                    score_name,
                    row["Yearly Threshold Min List"],
                    row["Yearly Threshold Max List"]
                )
                

            elif row["Indicator Type"] == "Consecutive Outlier Days":
                df_daily, indicator_column = daily_indicators(df_season_temp, variable, row["Daily Threshold Min"], row["Daily Threshold Max"])
                df_daily["cumulated_days_sum"] = df_season_temp.groupby(df_season_temp.index.year)[indicator_column].transform(reset_cumsum)

                with st.expander("Show Daily Dataframe"):
                    st.dataframe(df_daily, height=DATAFRAME_HEIGHT,use_container_width=True)

                df_yearly_var, aggregated_column_name = make_yearly_agg(df_season_temp, score_name,"cumulated_days_sum", row["Yearly Aggregation"])
                df_yearly_var = indicator_score(
                    df_yearly_var,
                    aggregated_column_name,
                    score_name,
                    row["Yearly Threshold Min List"],
                    row["Yearly Threshold Max List"]
                )

            # print(df_yearly_var)
            df_yearly_var["year"] = df_yearly_var.index.year
            df_yearly_var = add_periods_to_df(df_yearly_var, periods)
            df_yearly_var["period"] = df_yearly_var["period"].apply(lambda x: f"{x[0]}-{x[1]}")
            df_yearly_var["color"] = df_yearly_var[f"yearly_indicator_{score_name}"].apply(lambda category:CATEGORY_TO_COLOR_MAP[category])
            df_yearly_var["category"] = df_yearly_var["color"].apply(lambda color: RISK_MAP[color])

            
            # Define color and risk mapping
            
            # plot_period_categorization(score_counts)
            with st.expander("Show Yearly Dataframe"):
                st.dataframe(df_yearly_var, height=DATAFRAME_HEIGHT, use_container_width=True)

            plot_years_exposure(df_yearly_var, aggregated_column_name, row["Yearly Threshold Min List"], row["Yearly Threshold Max List"], variable)
            plot_exposure_through_period(df_yearly_var, score_name)
            plot_global_exposure(df_yearly_var, score_name, i, aggregated_column_name, below_thresholds, above_thresholds)

    return df_yearly