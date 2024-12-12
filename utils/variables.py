DATAFRAME_HEIGHT = 200

MONTHS_LIST = [
    "January", "February", "March", "April", "May", "June", 
    "July", "August", "September", "October", "November", "December"
]
AVAILABLE_VARIABLES = ["Temperature", "Precipitation", "Wind", "Shortwave Radiation", "Relative Humidity", "Soil Moisture"]
UNIT_DICT={"Temperature":"°C","Precipitation":"mm", "Wind":"km/h", "Shortwave Radiation":"MJ/m²","Relative Humidity":"%","Soil Moisture": "m³/m³"}

PERIOD_LENGTH = [10,15,20,25,30,35,40,45,50,55,60]

PDF_FILENAME = "general_plot_export.pdf"

COLORSCALE = ["Spectral", "RdYlBu", "RdYlGn", "Picnic"]
VARIATION_THRESHOLD = 0.05

AGG_FUNC = ["mean", "sum", "min", "max"]
INDICATOR_TYPES = ["Outlier Days", "Consecutive Outlier Days", "Season Aggregation", "Monthly Variation Coefficient"]

# This is very useful to chose the right indicator in the function
INDICATOR_AGG = {"Outlier Days":[1, 1], "Consecutive Outlier Days": [3,1], "Season Aggregation": [1, 0], "Monthly Variation Coefficient":[0,0]}
NUM_THRESHOLDS = 3

# Plot variable
RISK_MAP = {
        "red": "Very High Risk",
        "orange": "High Risk",
        "yellow": "Moderate Risk",
        "green": "Low Risk",
        "blue": "No Risk",
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

EXPOSURE_AGGREGATION=["Category Max", "Variable Mean Category" ]