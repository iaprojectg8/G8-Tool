from utils.imports import *
from utils.variables import * 
from layouts.layout import * 


def reset_cumsum(group):
    cumsum = 0
    result = []
    for val in group:
        if val == 0:
            cumsum = 0
        else:
            cumsum += val
        result.append(cumsum)
    return result

def calculate_score(df, df_indicators_parameters: pd.DataFrame):
    
    # Store all newly created columns in a dictionary to merge later

    df_yearly = pd.DataFrame()
    for _, row in df_indicators_parameters.iterrows():
        variable = row["Variable"]
        score_name = row["Name"]
        if row["Indicator Type"] == "Season Sum":
            # Perform yearly aggregation
            df_yearly_var, aggregated_column_name = make_yearly_agg(df, score_name,variable, row["Yearly Aggregation"])
            df_yearly_var = indicator_score(
                df_yearly_var,
                aggregated_column_name,
                score_name,
                row["Yearly Threshold Min"],
                row["Yearly Threshold Max"]
            )

        elif row["Indicator Type"] == "Outlier Days":
            df_daily, indicator_column = daily_indicators(df, variable,score_name, row["Daily Threshold Min"], row["Daily Threshold Max"])
            # st.dataframe(df_daily, use_container_width=True)
            df_yearly_var, aggregated_column_name = make_yearly_agg(df, score_name,indicator_column, row["Yearly Aggregation"])
            df_yearly_var = indicator_score(
                df_yearly_var,
                aggregated_column_name,
                score_name,
                row["Yearly Threshold Min"],
                row["Yearly Threshold Max"]
            )

        elif row["Indicator Type"] == "Consecutive Outlier Days":
            df_daily, indicator_column = daily_indicators(df, variable,score_name, row["Daily Threshold Min"], row["Daily Threshold Max"])
            df_daily["cumulated_days_sum"] = df.groupby(df.index.year)[indicator_column].transform(reset_cumsum)
                                        
            # st.dataframe(df_daily, use_container_width=True)
            df_yearly_var, aggregated_column_name = make_yearly_agg(df, score_name,"cumulated_days_sum", row["Yearly Aggregation"])
            df_yearly_var = indicator_score(
                df_yearly_var,
                aggregated_column_name,
                score_name,
                row["Yearly Threshold Min"],
                row["Yearly Threshold Max"]
            )
  
        df_yearly = pd.concat([df_yearly, df_yearly_var],axis=1)    

    set_title_2("Yearly result for the moment")    
    st.dataframe(df_yearly, height=DATAFRAME_HEIGHT, use_container_width=True)
    return df_yearly


def make_yearly_agg(df: pd.DataFrame,score, variable, yearly_aggregation):
    
    # Resample to yearly frequency and perform aggregation
    # st.dataframe(df)
    # st.write(yearly_aggregation)
    # st.write(variable)

    df_yearly = df.resample("YE").agg({variable: yearly_aggregation})
    df_yearly = df_yearly.rename(columns={variable: f"{variable}_{yearly_aggregation}_{score}"})
    # st.dataframe(df_yearly)
    return df_yearly, f"{variable}_{yearly_aggregation}_{score}"

def daily_indicators(df:pd.DataFrame, variable,score, daily_thresh_min, daily_thresh_max):
    indicator_column = f"daily_indicator"
    if daily_thresh_min is not None and daily_thresh_max is not None:
        df[indicator_column] =  (~df[variable].between(daily_thresh_min, daily_thresh_max)).astype(int)   
    elif daily_thresh_min is not None:
        df[indicator_column] =  (df[variable] < daily_thresh_min).astype(int)
    elif daily_thresh_max is not None:
        df[indicator_column] =  (df[variable] > daily_thresh_max).astype(int)
    else:
        df = df
    return df, indicator_column

def indicator_score(df: pd.DataFrame, variable, score, yearly_tresh_min, yearly_thresh_max):
    # Create a new column for the yearly indicator
    if yearly_tresh_min is not None and yearly_thresh_max is not None:
        df[f"yearly_indicator_{score}"] = (~df[variable].between(yearly_tresh_min, yearly_thresh_max)).astype(int)
    elif yearly_tresh_min is not None:
        df[f"yearly_indicator_{score}"] = (df[variable] < yearly_tresh_min).astype(int)
    elif yearly_thresh_max is not None:
        df[f"yearly_indicator_{score}"] = (df[variable] > yearly_thresh_max).astype(int)

    return df


def classify_exposure(frequency, threshold1, threshold2, threshold3):

    if 0 <= frequency < threshold1:
        return "Low"
    
    elif  threshold1 <= frequency < threshold2:
        return "Moderate"
    
    elif  threshold2 <= frequency < threshold3:
        return "High"
    
    elif  threshold3 <= frequency <= 1:
        return "Very High"
    
def classify_frequency_by_exposure(frequency, threshold1, threshold2, threshold3):

    if 0 <= frequency < threshold1:
        return ("Low", frequency)
    
    elif  threshold1 <= frequency < threshold2:
        return ("Moderate", frequency)
    
    elif  threshold2 <= frequency < threshold3:
        return ("High", frequency)
    
    elif  threshold3 <= frequency <= 1:
        return ("Very High", frequency)
    
def classify_desirability_score(frequency):
    """
    Classifies the risk based on the given frequency.
    
    Arg:
    frequency (float): Risk frequency between 0 and 1.
    
    Returns:
    tuple: A tuple containing the risk category (str) and the frequency (float).
    """
    if 0.84 < frequency <= 1:
        return "Virtually certain", frequency
    elif 0.67 < frequency <= 0.84:
        return "Very probable", frequency
    elif 0.5 < frequency <= 0.67:
        return "Probable", frequency
    elif 0.34 < frequency <= 0.5:
        return "As likely as not", frequency
    elif 0.17 < frequency <= 0.34:
        return "Unlikely", frequency
    elif 0 < frequency <= 0.17:
        return "Very unlikely", frequency
    else:
        return "Exceptionally improbable", frequency


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


# Info Dans la cumulated sum les suites que nous avons sont calculé à partir des 1
# Les 1 correpondent dans tous les cas à ce que l'on considère viable c'est à dire dans les intervalles
# Définis, c'est à dire en dessous des seuils max et au dessus de seuils min