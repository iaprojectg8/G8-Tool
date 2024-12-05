from utils.imports import * 

if "start_date" not in st.session_state:
    st.session_state.start_date = None

if "end_date" not in st.session_state:
    st.session_state.end_date = None

if "df_indicators" not in st.session_state:
    st.session_state.df_indicators = pd.DataFrame()

if "indicator" not in st.session_state:
    st.session_state.indicator = dict()

if "checkbox" not in st.session_state:
    st.session_state.checkbox = 0

# def add_indicator_to_df():

    
    


def delete_indicator(index):
# Remove the row with index 2
    print("index", index)
    st.session_state.df_indicators = st.session_state.df_indicators.drop(index).reset_index(drop=True)

# def reset_indicator():

#     st.session_state.checkbox_defaults = {
#         "min_daily_checkbox": False,
#         "max_daily_checkbox": False,
#         "min_yearly_checkbox": False,
#         "max_yearly_checkbox": False,
#         "shift_start_checkbox": False,
#         "shift_end_checkbox": False
#     }
#     st.session_state.checkbox_defaults["min_daily_checkbox"] = 0
#     print("in the session_state file",st.session_state.checkbox_defaults)
#     st.session_state.checkbox = 0
#     st.session_state.indicator = {
#         "Name": None,
#         "Variable": None,
#         "Indicator Type": None,
#         "Daily Threshold Min": None,
#         "Daily Threshold Max": None,
#         "Yearly Threshold Min": None,
#         "Yearly Threshold Max": None,
#         "Yearly Aggregation": None,
#         "Season Start Shift": None,
#         "Season End Shift": None
#     }
    