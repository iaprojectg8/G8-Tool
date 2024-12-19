from utils.imports import *
from utils.variables import * 
from layouts.layout import * 
from lib.plot import add_periods_to_df

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




def map_risk(score):
    if score in [-4, 4]:
        return "Very High Risk"
    elif score in [-3, 3]:
        return "High Risk"
    elif score in [-2, 2]:
        return "Moderate Risk"
    elif score in [-1, 1]:
        return "Low Risk"
    elif score == 0:
        return "Very Low Risk"


def make_yearly_agg(df: pd.DataFrame,score, variable, yearly_aggregation):
    
    # Resample to yearly frequency and perform aggregation
    # st.dataframe(df)
    # st.write(yearly_aggregation)
    # st.write(variable)

    df_yearly = df.resample("YE").agg({variable: yearly_aggregation})
    df_yearly = df_yearly.rename(columns={variable: f"yearly_{yearly_aggregation}_{variable}"})
    # st.dataframe(df_yearly)
    return df_yearly, f"yearly_{yearly_aggregation}_{variable}"

def daily_indicators(df:pd.DataFrame, variable, daily_thresh_min, daily_thresh_max):
    indicator_column = f"daily_indicator"
  
    if daily_thresh_min is not None and not math.isnan(daily_thresh_min) and daily_thresh_max is not None and not math.isnan(daily_thresh_max):

        df[indicator_column] =  (df[variable].between(daily_thresh_min, daily_thresh_max)).astype(int)   
    elif  daily_thresh_min is not None and not math.isnan(daily_thresh_min):
       
        df[indicator_column] =  (df[variable] < daily_thresh_min).astype(int)
    elif  daily_thresh_max is not None and not math.isnan(daily_thresh_max):
     
        df[indicator_column] =  (df[variable] > daily_thresh_max).astype(int)
    else:
        df = df
    return df, indicator_column

def rolling_period_indicator(df:pd.DataFrame, variable, window_length, window_aggregation):
    indicator_column = f"{variable}_window_{window_aggregation}"
    df[indicator_column] = df[variable].rolling(window=window_length).agg(window_aggregation)


    return df, indicator_column



# Create a new column for the yearly indicator
def categorize_above(value, above_thresholds):
    if above_thresholds[0] <= value < above_thresholds[1]:
        return 1
    elif above_thresholds[1] <= value < above_thresholds[2]:
        return 2
    elif above_thresholds[2] <= value < above_thresholds[3]:
        return 3
    elif value > above_thresholds[3]:
        return 4
    else :
        return 0

def categorize_below(value, below_thresholds):
    if below_thresholds[0] >= value > below_thresholds[1]:
        return -1
    elif below_thresholds[1] >= value > below_thresholds[2]:
        return -2
    elif below_thresholds[2] >= value > below_thresholds[3]:
        return -3
    elif value < below_thresholds[3]:
        return -4
    else: 
        return 0
    
def categorize_both(value, below_thresholds=None,above_thresholds=None):
    """
    Categorizes a value based on both above and below thresholds.
    
    Args:
        value (float): The value to categorize.
        above_thresholds (list, optional): A sorted list of thresholds for values above the normal range.
        below_thresholds (list, optional): A sorted list of thresholds for values below the normal range (in descending order).
    
    Returns:
        int: The category, positive for above thresholds, negative for below thresholds, and 0 for normal.
    """
    # Check if value is above thresholds
    if above_thresholds:
        if above_thresholds[0] <= value < above_thresholds[1]:
            return 1
        elif above_thresholds[1] <= value < above_thresholds[2]:
            return 2
        elif above_thresholds[2] <= value < above_thresholds[3]:
            return 3
        elif value >= above_thresholds[3]:
            return 4

    # Check if value is below thresholds
    if below_thresholds:
        if below_thresholds[0] >= value > below_thresholds[1]:
            return -1
        elif below_thresholds[1] >= value > below_thresholds[2]:
            return -2
        elif below_thresholds[2] >= value > below_thresholds[3]:
            return -3
        elif value <= below_thresholds[3]:
            return -4

    # Value is within the normal range
    return 0

def indicator_score(df: pd.DataFrame, variable, score, yearly_trehsholds_min: list, yearly_trehsholds_max:list):
    below_thresholds = yearly_trehsholds_min
    above_thresholds = yearly_trehsholds_max
    
    df[f"yearly_indicator_{score}"] =(df[variable].apply(lambda x:categorize_both(x,below_thresholds, above_thresholds) )).astype(int)
    # elif yearly_tresh_min is not None:
    #     df[f"yearly_indicator_{score}"] = (df[variable] < yearly_tresh_min).astype(int)
    # elif yearly_thresh_max is not None:
    #     df[f"yearly_indicator_{score}"] = (df[variable] > yearly_thresh_max).astype(int)

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


# Info Dans la cumulated sum les suites que nous avons calculé à partir des 1
# Les 1 correpondent dans tous les cas à ce que l'on considère viable c'est à dire dans les intervalles
# Définis, c'est à dire en dessous des seuils max et au dessus de seuils min