# For data requests
VARIABLES_LIST = ["temperature_2m_mean", "temperature_2m_max", "temperature_2m_min", "wind_speed_10m_mean",
          "wind_speed_10m_max", "shortwave_radiation_sum", "relative_humidity_2m_mean", "relative_humidity_2m_max", 
          "relative_humidity_2m_min", "precipitation_sum", "soil_moisture_0_to_10cm_mean"]

CMIP6_VARIABLE = ["hurs", "huss", "pr", "rlds", "rsds", "sfcWind", "tas", "tasmax", "tasmin"]
READABLE_VARIABLE = [
        "relative_humidity_2m","specific_humidity_2m","precipitation_sum","longwave_radiation","shortwave_radiation",
        "wind_speed_10m_mean","temperature_2m_mean","temperature_2m_max","temperature_2m_min"]

DATASET_FOLDER ="Moroni_Dataset"
COORDINATES_FILE="coordinates_to_extract/Sundarbans_02.csv"

FILENAME_BASE="era5_daily_sundarbans"


# Some other things

DATAFRAME_HEIGHT = 200

MONTHS_LIST = [
    "January", "February", "March", "April", "May", "June", 
    "July", "August", "September", "October", "November", "December"
]
AVAILABLE_VARIABLES = ["Temperature", "Precipitation", "Wind", "Shortwave Radiation", 
                       "Relative Humidity", "Soil Moisture", "Longwave Radiation", "Specific Humidity" ]
UNIT_DICT= {
    "temperature_2m_mean": "°C",
    "temperature_2m_max": "°C",
    "temperature_2m_min": "°C",
    "wind_speed_10m_mean": "m/s",
    "wind_speed_10m_max": "m/s",
    "shortwave_radiation_sum": "MJ/m²",
    "longwave_radiation": "W/m²",         # Longwave downward radiation
    "shortwave_radiation": "W/m²",        # Shortwave downward radiation
    "relative_humidity_2m": "%",
    "relative_humidity_2m_mean": "%",
    "relative_humidity_2m_max": "%",
    "relative_humidity_2m_min": "%",
    "specific_humidity_2m": "",
    "precipitation_sum": "mm",
    "soil_moisture_0_to_10cm_mean": "m³/m³"
}

# CMIP6_UNIT = {
#     "relative_humidity_2m": "%",           # Relative humidity at 2m
#     "specific_humidity_2m": "",           # Specific humidity at 2m
#     "precipitation_sum": "mm",      # Precipitation average flux
#     "longwave_radiation": "W/m²",         # Longwave downward radiation
#     "shortwave_radiation": "W/m²",        # Shortwave downward radiation
#     "wind_speed_10m_mean": "km/h",         # Wind speed at 10m
#     "temperature_2m_mean": "°C",             # Air temperature at 2m
#     "temperature_2m_max": "°C",           # Daily maximum air temperature
#     "temperature_2m_min": "°C"            # Daily minimum air temperature
# }


FILENAME = "Moroni_coords_mean.csv"


PERIOD_LENGTH = [10,15,20,25,30,35,40,45,50,55,60]

PDF_FILENAME = "general_plot_export.pdf"

COLORSCALE = ["Spectral", "RdYlBu", "RdYlGn", "Picnic"]
VARIATION_THRESHOLD = 0.05

AGG_FUNC = ["mean", "sum", "min", "max"]
INDICATOR_TYPES = ["Outlier Days", "Consecutive Outlier Days", "Season Aggregation", "Monthly Variation Coefficient",
                   "Sliding Windows Aggregation", "Crossed Variables"]

# This is very useful to chose the right indicator in the function
INDICATOR_AGG = {"Outlier Days":[1, 1], 
                 "Consecutive Outlier Days": [3,1], 
                 "Season Aggregation": [1, 0], 
                 "Monthly Variation Coefficient":[0,0], 
                 "Sliding Windows Aggregation": [0,0]
                }
 
NUM_THRESHOLDS = 3

# Plot variable
RISK_MAP = {
        "red": "Very High Risk",
        "orange": "High Risk",
        "yellow": "Moderate Risk",
        "green": "Low Risk",
    }


PROB_MAP = {
        "Very High Risk": 1,
        "High Risk":0.75,
        "Moderate Risk":  0.5,
        "Low Risk":  0.25,
    }


RISK_TO_COLOR = {
        "Very High Risk": "red",
        "High Risk":"orange",
        "Moderate Risk":  "yellow",
        "Low Risk":  "green",
    }


CATEGORY_TO_RISK = {
        -4: "Very High Risk",
        4: "Very High Risk",
        -3 : "High Risk",
        3: "High Risk",
        -2 : "Moderate Risk",
        2: "Moderate Risk",
        -1 : "Low Risk",
        1: "Low Risk",
    }

GET_RIGHT_COLOR = {
        -4: -1,
        -3: -2,
        -2: -3,
        -1: -4,
        1 : 3,
        2 : 2,
        3 : 1,
        4 : 0
}

CATEGORY_TO_COLOR_MAP = {
        -4: "red",
        -3: "orange",
        -2: "yellow",
        -1: "green",
        1: "green",
        2: "yellow",
        3: "orange",
        4: "red",
    }
THRESHOLD_COLORS = ["green", "yellow", "orange", "red"]

EXPOSURE_AGGREGATION=["Category Mean", "Most Frequent Category", "Variable Mean Category" ]


# For everything in the map part
# ZIP_FOLDER = "zip_files"

ZIP_FOLDER = "zip_folder_test"

MODEL_NAMES = [
        "CMCC_CM2_VHR4 (30 km)",
        "FGOALS_f3_H (28 km)",
        "HiRAM_SIT_HR (25 km)",
        "MRI_AGCM3_2_S (20 km)",
        "EC_Earth3P_HR (29 km)",
        "MPI_ESM1_2_XR (51 km)",
        "NICAM16_8S (31 km)"
    ]
TEMPLATE_COLOR = 'plotly_white'

BUILTIN_INDICATORS = ["Heat Index", "Other"]


# Everything involving the CMIP6 data


CMIP6_TO_READABLE = {
        "hurs": "relative_humidity_2m",   # Relative humidity at 2m
        "huss": "specific_humidity_2m",   # Specific humidity at 2m
        "pr": "precipitation_sum",        # precipitation average flux in kg m-2 s-1 if total preicipitation wanted then need to multiply by 86400
        "rlds": "longwave_radiation",     # Longwave downward radiation
        "rsds": "shortwave_radiation",    # Shortwave downward radiation
        "sfcWind": "wind_speed_10m_mean",       # Wind speed at 10m
        "tas": "temperature_2m_mean",          # Air temperature at 2m
        "tasmax": "temperature_2m_max",   # Daily maximum air temperature
        "tasmin": "temperature_2m_min"    # Daily minimum air temperature
    }

READABLE_TO_CMIP6 = {
    "relative_humidity_2m": "hurs",           # Relative humidity at 2m
    "specific_humidity_2m": "huss",           # Specific humidity at 2m
    "precipitation_sum": "pr",      # Precipitation average flux
    "longwave_radiation": "rlds",             # Longwave downward radiation
    "shortwave_radiation": "rsds",        # Shortwave downward radiation
    "wind_speed_10m_mean": "sfcWind",         # Wind speed at 10m
    "temperature_2m_mean": "tas",             # Air temperature at 2m
    "temperature_2m_max": "tasmax",           # Daily maximum air temperature
    "temperature_2m_min": "tasmin"            # Daily minimum air temperature
}







SSP = ["ssp126", "ssp245", "ssp370", "ssp585"]
MODEL_NAMES_CMIP6 = ["CNRM-ESM2-1"]
EXPERIMENTS = ["r1i1p1f2"]
HISTORICAL_END_YEAR = 2014

NC_FILE_DIR = "nc_files"
WORKING_NC_FILE = "all_variables_nc_1960"
CSV_FILE_DIR = "csv_files"
EMPTY_REQUEST_FOLDER = "empty_request"

REQUEST_TYPE = ["Request data though CMIP6 projections","Request data through Open-Meteo"]

