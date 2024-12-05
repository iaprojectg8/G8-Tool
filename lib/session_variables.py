from utils.imports import * 

if "start_date" not in st.session_state:
    st.session_state.start_date = None

if "end_date" not in st.session_state:
    st.session_state.end_date = None


if "indicator" not in st.session_state:
    st.session_state.indicator = {
        "Name": "",
        "Variable": None,
        "Indicator Type": None,
        "Daily Threshold Min": None,
        "Daily Threshold Max": None,
        "Yearly Threshold Min": None,
        "Yearly Threshold Max": None,
        "Yearly Aggregation": None,
        "Season Start Shift": None,
        "Season End Shift": None
    }

if 'df_indicators' not in st.session_state:
    st.session_state.df_indicators = pd.DataFrame(columns=st.session_state.indicator.keys())

if "checkbox_defaults" not in st.session_state:
    st.session_state.checkbox_defaults = {
        "min_daily_checkbox": False,
        "max_daily_checkbox": False,
        "min_yearly_checkbox": False,
        "max_yearly_checkbox": False,
        "shift_start_checkbox": False,
        "shift_end_checkbox": False
    }

if "df_checkbox" not in st.session_state:
    st.session_state.df_checkbox = pd.DataFrame(columns=st.session_state.checkbox_defaults.keys())
    


def delete_indicator(index):
# Remove the row with index 2
    print("index", index)
    st.session_state.df_indicators = st.session_state.df_indicators.drop(index).reset_index(drop=True)




def reset_indicator():
    st.session_state.indicator = {
        "Name": "",
        "Variable": None,
        "Indicator Type": None,
        "Daily Threshold Min": None,
        "Daily Threshold Max": None,
        "Yearly Threshold Min": None,
        "Yearly Threshold Max": None,
        "Yearly Aggregation": None,
        "Season Start Shift": None,
        "Season End Shift": None
    }
    st.session_state.min_daily_checkbox = False
    st.session_state.max_daily_checkbox = False
    st.session_state.min_yearly_checkbox = False
    st.session_state.max_yearly_checkbox = False
    st.session_state.shift_start_checkbox = False
    st.session_state.shift_end_checkbox = False
    

    