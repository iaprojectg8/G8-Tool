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
INDICATOR_TYPES = ["Outlier Days", "Consecutive Outlier Days", "Season Sum", "Monthly Variation Coefficient"]

# This is very useful to chose the right indicator in the function
INDICATOR_AGG = {"Outlier Days":[1, 1], "Consecutive Outlier Days": [3,1], "Season Sum": [1, 1], "Monthly Variation Coefficient":[0,0]}