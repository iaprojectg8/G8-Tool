from utils.imports import *
from utils.variables import * 
from layouts.layout import * 

def calculate_score(df, df_indicators_parameters: pd.DataFrame):
    
    # Store all newly created columns in a dictionary to merge later

    df_yearly = pd.DataFrame()
    for _, row in df_indicators_parameters.iterrows():
        variable = row["Variable"]
        score_name = row["Name"]

        # If daily thresholds are provided, you can calculate daily scores here if needed
        if row["Daily Threshold Min"] or row["Daily Threshold Max"]:
            print("You should calculate something about day (optional)")

        # If yearly thresholds are provided, calculate the yearly score
        if row["Yearly Threshold Min"] or row["Yearly Threshold Max"]:
            print("You should calculate yearly score")

            # Perform yearly aggregation
            df_yearly_var = make_yearly_agg(df, variable, row["Yearly Agg"])

            # Calculate indicator score based on yearly thresholds
            df_yearly_var = indicator_score(
                df_yearly_var,
                variable,
                score_name,
                row["Yearly Threshold Min"],
                row["Yearly Threshold Max"]
            )
            print(df_yearly_var)
            df_yearly = pd.concat([df_yearly, df_yearly_var],axis=1)    

    set_title_2("Yearly result for the moment")    
    st.dataframe(df_yearly, height=DATAFRAME_HEIGHT, use_container_width=True)


def make_yearly_agg(df: pd.DataFrame, variable, yearly_aggregation):
    
    # Resample to yearly frequency and perform aggregation
    df_yearly = df.resample("YE").agg({variable: yearly_aggregation})
    return df_yearly


def indicator_score(df: pd.DataFrame, variable, score, yearly_tresh_min, yearly_thresh_max):
    # Create a new column for the yearly indicator
    if yearly_tresh_min is not None and yearly_thresh_max is not None:
        df[f"yearly_indicator_{score}"] = df[variable].between(yearly_tresh_min, yearly_thresh_max).astype(int)
    elif yearly_tresh_min is not None:
        df[f"yearly_indicator_{score}"] = (df[variable] >= yearly_tresh_min).astype(int)
    elif yearly_thresh_max is not None:
        df[f"yearly_indicator_{score}"] = (df[variable] <= yearly_thresh_max).astype(int)

    return df


# Nettoyer un peu mais là ça peut être bientot bien