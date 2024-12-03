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
        if row["Daily Threshold Min"]!="nan" or row["Daily Threshold Max"]!="nan":
            print(row["Daily Threshold Min"], row["Daily Threshold Max"])
            print("You should calculate something about day (optional)")
            df_daily = daily_indicators(df, variable,score_name, row["Daily Threshold Min"], row["Daily Threshold Max"])
            st.dataframe(df_daily,height=DATAFRAME_HEIGHT, use_container_width=True)
        # If yearly thresholds are provided, calculate the yearly score
        if row["Yearly Threshold Min"] or row["Yearly Threshold Max"]:
            print("You should calculate yearly score")

            # Perform yearly aggregation
            df_yearly_var = make_yearly_agg(df, score_name,variable, row["Yearly Agg"])

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


def make_yearly_agg(df: pd.DataFrame,score, variable, yearly_aggregation):
    
    # Resample to yearly frequency and perform aggregation
    st.dataframe(df)
    if f"daily_indicators_{score}" in df:
        df_yearly = df.resample("YE").agg({f"daily_indicators_{score}": yearly_aggregation})
    else:
        df_yearly = df.resample("YE").agg({variable: yearly_aggregation})
    df_yearly = df_yearly.rename(columns={variable: f"{variable}_{score}"})
    st.dataframe(df_yearly)
    return df_yearly

def daily_indicators(df:pd.DataFrame, variable,score, daily_thresh_min, daily_thresh_max):
    if daily_thresh_min is not None and daily_thresh_max is not None:
        df[f"daily_indicator_{score}"] = df[variable].between(daily_thresh_min, daily_thresh_max).astype(int)   
    elif daily_thresh_min is not None:
        df[f"daily_indicator_{score}"] = (df[variable] >= daily_thresh_min).astype(int)
    elif daily_thresh_max is not None:
        df[f"daily_indicator_{score}"] = (df[variable] <= daily_thresh_max).astype(int)
    else:
        df = df
    return df

def indicator_score(df: pd.DataFrame, variable, score, yearly_tresh_min, yearly_thresh_max):
    # Create a new column for the yearly indicator
    if yearly_tresh_min is not None and yearly_thresh_max is not None:
        df[f"yearly_indicator_{score}"] = df[f"{variable}_{score}"].between(yearly_tresh_min, yearly_thresh_max).astype(int)
    elif yearly_tresh_min is not None:
        df[f"yearly_indicator_{score}"] = (df[f"{variable}_{score}"] >= yearly_tresh_min).astype(int)
    elif yearly_thresh_max is not None:
        df[f"yearly_indicator_{score}"] = (df[f"{variable}_{score}"] <= yearly_thresh_max).astype(int)

    return df


# Nettoyer un peu mais là ça peut être bientot bien

# indicateur annuel
# coeff de variation mensuel
# indicateur whole period (period indicators)
# cumulated daily indicator
# - aditionner le nombre de jours dans la periode en dehors des intervalles
# - case à cocher : max consecutive days 

# shift = décalage en mois, un mois avant par example pour la précipitation
# jour qui ne correspond pas aux conditions
# Ajouter les types d'indicateurs, cumulated days, consecutive days max, monthly coeff variation, 
# Mais dans les types cumulated days il y a deux sous-types:
#- celui où l'on calcule directement la somme des valeurs
#- celui où l'on calcule la somme des jours qui dépassent un certain seuil 