# For data requests
VARIABLES_LIST = ["temperature_2m_mean", "temperature_2m_max", "temperature_2m_min", "wind_speed_10m_mean",
          "wind_speed_10m_max", "shortwave_radiation_sum", "relative_humidity_2m_mean", "relative_humidity_2m_max", 
          "relative_humidity_2m_min", "precipitation_sum", "soil_moisture_0_to_10cm_mean"]

DATASET_FOLDER ="Moroni_Dataset"
COORDINATES_FILE="coordinates_to_extract/Sundarbans_02.csv"

FILENAME_BASE="era5_daily_sundarbans"


# Some other things

DATAFRAME_HEIGHT = 200

MONTHS_LIST = [
    "January", "February", "March", "April", "May", "June", 
    "July", "August", "September", "October", "November", "December"
]
AVAILABLE_VARIABLES = ["Temperature", "Precipitation", "Wind", "Shortwave Radiation", "Relative Humidity", "Soil Moisture"]
UNIT_DICT= {
    "temperature_2m_mean": "°C",
    "temperature_2m_max": "°C",
    "temperature_2m_min": "°C",
    "wind_speed_10m_mean": "m/s",
    "wind_speed_10m_max": "m/s",
    "shortwave_radiation_sum": "MJ/m²",
    "relative_humidity_2m_mean": "%",
    "relative_humidity_2m_max": "%",
    "relative_humidity_2m_min": "%",
    "precipitation_sum": "mm",
    "soil_moisture_0_to_10cm_mean": "m³/m³"
}



FILENAME = "North_Bengal_coords_mean.csv"


UNIT_FROM_VARIABLE = {
    "temperature_2m_mean": "°C",  # Mean temperature at 2 meters above ground
    "temperature_2m_max": "°C",   # Maximum temperature at 2 meters
    "temperature_2m_min": "°C",   # Minimum temperature at 2 meters
    "wind_speed_10m_mean": "m/s", # Mean wind speed at 10 meters above ground
    "wind_speed_10m_max": "m/s",  # Maximum wind speed at 10 meters
    "shortwave_radiation_sum": "W/m²", # Sum of shortwave radiation (solar energy)
    "relative_humidity_2m_mean": "%",  # Mean relative humidity at 2 meters
    "relative_humidity_2m_max": "%",   # Maximum relative humidity at 2 meters
    "relative_humidity_2m_min": "%",   # Minimum relative humidity at 2 meters
    "precipitation_sum": "mm",         # Total precipitation
    "soil_moisture_0_to_10cm_mean": "m³/m³" # Volumetric soil moisture content (0-10cm depth)
}

PERIOD_LENGTH = [10,15,20,25,30,35,40,45,50,55,60]

PDF_FILENAME = "general_plot_export.pdf"

COLORSCALE = ["Spectral", "RdYlBu", "RdYlGn", "Picnic"]
VARIATION_THRESHOLD = 0.05

AGG_FUNC = ["mean", "sum", "min", "max"]
INDICATOR_TYPES = ["Outlier Days", "Consecutive Outlier Days", "Season Aggregation", "Monthly Variation Coefficient", "Sliding Windows Aggregation"]

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
        "blue": "No Risk",
    }


PROB_MAP = {
        "Very High Risk": 1,
        "High Risk":0.75,
        "Moderate Risk":  0.5,
        "Low Risk":  0.25,
        "No Risk" :0.01,
    }


RISK_TO_COLOR = {
        "Very High Risk": "red",
        "High Risk":"orange",
        "Moderate Risk":  "yellow",
        "Low Risk":  "green",
        "No Risk" : "blue",
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
        0: "No Risk",
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
        0: "blue",
        1: "green",
        2: "yellow",
        3: "orange",
        4: "red",
    }
THRESHOLD_COLORS = ["blue", "green", "yellow", "orange", "red"]

EXPOSURE_AGGREGATION=["Category Mean", "Most Frequent Category", "Variable Mean Category" ]


# For everything in the map part
ZIP_FOLDER = "zip_files"

MODEL_NAMES = [
        "CMCC_CM2_VHR4 (30 km)",
        "FGOALS_f3_H (28 km)",
        "HiRAM_SIT_HR (25 km)",
        "MRI_AGCM3_2_S (20 km)",
        "EC_Earth3P_HR (29 km)",
        "MPI_ESM1_2_XR (51 km)",
        "NICAM16_8S (31 km)"
    ]