from utils.imports import *
from lib.session_variables import * 
from utils.variables import *
from layouts.layout import *


def create_empty_dataframe():
    df = pd.DataFrame()
    return df



def create_dynamic_dataframe(df:pd.DataFrame,columns_chosen):
    if df is None or df.empty:
        df = pd.DataFrame(columns=["Name","Type", "Variable", 
                                    "Daily Threshold Min","Daily Threshold Max", "Monthly Agg", 
                                    "Yearly Threshold Min", "Yearly Threshold Max", "Yearly Agg", 
                                    "Cumulated Days Threshold",
                                    'Season Shift Start', 'Season Shift End'
                            ])
        
    column_config={
        'Name': st.column_config.TextColumn(
            max_chars=50,
            default=str(),
        ),
        'Type': st.column_config.TextColumn(
            max_chars=50,
            default=str(),
        ),
        'Variable': st.column_config.SelectboxColumn(
            options=columns_chosen,
            default=columns_chosen[0]),

        'Daily Threshold Min': st.column_config.NumberColumn(),  # Boolean checkbox
        'Daily Threshold Max': st.column_config.NumberColumn(),  # Boolean checkbox

        # Is it really necessary ?
        'Monthly Agg': st.column_config.SelectboxColumn(
            options=AGG_FUNC,
            default=AGG_FUNC[0]),

        'Yearly Threshold Min': st.column_config.NumberColumn(),  # Boolean checkbox
        'Yearly Threshold Max': st.column_config.NumberColumn(),  # Boolean checkbox

        'Yearly Agg': st.column_config.SelectboxColumn(
            options=AGG_FUNC,
            default=AGG_FUNC[0]),

        'Cumulated Days Threshold': st.column_config.NumberColumn(default=None),

        'Season Shift Start': st.column_config.NumberColumn(default=None),
        'Season Shift End': st.column_config.NumberColumn(default=None),
    }
    df_indicator_parameters = st.data_editor(df, use_container_width=True, num_rows="dynamic", column_config=column_config)
    return df_indicator_parameters
    




def variable_choice():
    st.write("Choose the climate variable you are interested in: ")
    variables_choice = []
    col1, col2 = st.columns(2)
    for index, variable in enumerate(AVAILABLE_VARIABLES):
        if index%2 == 0:
            with col1:
                if st.checkbox(label=variable):
                    variables_choice.append(variable)
        else:
            with col2:
                if st.checkbox(label=variable):
                    variables_choice.append(variable)

    return variables_choice

def invert_month_choice(inverted, options, start_date, end_date):
    if inverted.lower() == "yes":
        # Create an inverted range by splitting the months
        selected_months = list(options[end_date-1:]) + list(options[:start_date])
    else:
        # Normal range
        selected_months = list(options[start_date-1:end_date])
    return selected_months

def select_season():
    # Create a list of months with placeholder year 2000 (leap year)

    # The year here is random, it is just to have the format that work on datetime object
    start=1
    end=12
    options =  np.arange(start, end+1)

    start_date, end_date = st.select_slider(
        "Select a date range:",
        options = options,
        value=(6, 10),
        format_func=lambda x:MONTHS_LIST[x-1]  # Displays full month name, day, and year
    )
    selected_months = list(options[start_date-1:end_date])

    # Display the selected range
    st.write(f"The period chosen goes from {MONTHS_LIST[selected_months[0]-1]} to {MONTHS_LIST[selected_months[-1]-1]}")
    return start_date, end_date

def select_data_contained_in_season(data, season_start, season_end):

    return data[(data.index.month >= season_start) & (data.index.month <= season_end)].copy()



# Real part start there
# -------------------------
# --- Handle input part ---
# -------------------------


# Template for creating a new indicator
def handle_checkbox_and_input(label : str, checkbox_key):
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        st.session_state.checkbox_defaults[checkbox_key] = st.checkbox(label=label, key=checkbox_key)
        
    if st.session_state.checkbox_defaults[checkbox_key]:
        with col2:
            st.session_state.indicator[label] = st.number_input(label, value=None, label_visibility="collapsed", key="_".join(label.lower().split(" ")))
    else:
        st.session_state.indicator[label] = None

def handle_checkbox_and_input_yearly_agg_min(label : str, checkbox_key):
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        st.session_state.checkbox_defaults[checkbox_key] = st.checkbox(label=label, key=checkbox_key)
        print(st.session_state.checkbox_defaults)
        
    if st.session_state.checkbox_defaults[checkbox_key]:
        with col2:
            st.session_state.indicator[label] = st.number_input(label, value=None, label_visibility="collapsed", key="_".join(label.lower().split(" ")))
        if st.session_state.indicator[label] is not None:
            st.subheader("Step below")
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.write("""Choose a step value to define additional thresholds below the current one. 
                         Each step will determine the range for hazard levels (e.g., Low, Moderate, High, Very High).
                         Starting from the current threshold, each subsequent range will be created by substracting the step value.""")
            
            with col2:
                st.session_state.indicator[label+ " Step"] = step = st.number_input(label="Step",key="step below", label_visibility="collapsed")

                st.session_state.indicator[label+" List"] = [st.session_state.indicator[label] - step * i for i in range(NUM_THRESHOLDS + 1)]
        st.write("Your ohter threshold will be the ones there ", st.session_state.indicator[label+" List"])
    else:
        st.session_state.indicator[label] = None

def handle_checkbox_and_input_yearly_agg_max(label : str, checkbox_key):
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        st.session_state.checkbox_defaults[checkbox_key] = st.checkbox(label=label, key=checkbox_key)
        
    if st.session_state.checkbox_defaults[checkbox_key]:
        with col2:
            st.session_state.indicator[label] = step = st.number_input(label, value=None, label_visibility="collapsed", key="_".join(label.lower().split(" ")))
        if st.session_state.indicator[label] is not None:
            col1, col2 = st.columns([0.8, 0.2])
            st.subheader("Step above")
            with col1:
                st.write("""Choose a step value to define additional thresholds above the current one. 
                         Each step will determine the range for hazard levels (e.g., Low, Moderate, High, Very High).
                         Starting from the current threshold, each subsequent range will be created by adding the step value.""")
            
            with col2:
                st.session_state.indicator[label+ " Step"] = step = st.number_input(label="Step", key="step above", label_visibility="collapsed")

                st.session_state.indicator[label+" List"] = [st.session_state.indicator[label] + step * i for i in range(NUM_THRESHOLDS + 1)]
        st.write("Your ohter threshold will be the ones there ", st.session_state.indicator[label+" List"])
    else:
        st.session_state.indicator[label] = None


def handle_checkbox_input_season_shift_start(label:str, checkbox_key, season_start):
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        st.session_state.checkbox_defaults[checkbox_key] = st.checkbox(label=label, key=checkbox_key)
        
    if st.session_state.checkbox_defaults[checkbox_key]:
        with col2:
            st.session_state.indicator[label] = st.number_input(label, value=None,
                                                                 min_value=0, max_value=season_start,
                                                                 label_visibility="collapsed", 
                                                                 key="_".join(label.lower().split(" ")))
    else:
        st.session_state.indicator[label] = None

def handle_checkbox_input_season_shift_end(label:str, checkbox_key, season_end):
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        st.session_state.checkbox_defaults[checkbox_key] = st.checkbox(label=label, key=checkbox_key)
        
    if st.session_state.checkbox_defaults[checkbox_key]:
        with col2:
            st.session_state.indicator[label] = st.number_input(label, value=None,
                                                                 min_value=0, max_value=12 - season_end,
                                                                 label_visibility="collapsed", 
                                                                 key="_".join(label.lower().split(" ")))
    else:
        st.session_state.indicator[label] = None

def handle_threshold_input():

    # Thresholds init
    
    handle_daily_threshold_input()
    handle_yearly_threshold_input()


def handle_daily_threshold_input():
    st.subheader("Daily Thresholds")
    handle_checkbox_and_input(label="Daily Threshold Min", checkbox_key="min_daily_checkbox")
    handle_checkbox_and_input(label="Daily Threshold Max", checkbox_key="max_daily_checkbox")

def handle_yearly_threshold_input():
    st.subheader("Yearly Thresholds")
    handle_checkbox_and_input_yearly_agg_min(label="Yearly Threshold Min", checkbox_key="min_yearly_checkbox")
    handle_checkbox_and_input_yearly_agg_max(label="Yearly Threshold Max", checkbox_key="max_yearly_checkbox")


def handle_season_shift_input(season_start, season_end):

    # Season shift init 
    st.subheader("Season shift")
    if season_start is not None and season_end is not None:
        handle_checkbox_input_season_shift_start(label="Season Start Shift", checkbox_key="shift_start_checkbox",season_start=season_start )
        handle_checkbox_input_season_shift_end(label="Season End Shift", checkbox_key="shift_end_checkbox", season_end=season_end)


def handle_yearly_aggregation_input():
    st.subheader("Aggregation functions")
    st.session_state.indicator["Yearly Aggregation"] = st.selectbox(
            label="Yearly Aggregation",
            options=AGG_FUNC,
            index=INDICATOR_AGG[st.session_state.indicator["Indicator Type"]][0], 
            key="yearly_aggregation", 
            disabled=INDICATOR_AGG[st.session_state.indicator["Indicator Type"]][1]
        )
    
def handle_buttons():
    if st.button(label="Add Indicator"):
        if st.session_state.indicator["Name"] is None:
            st.error("Your indicator is empty, you can't add it to your indicators list")

        elif st.session_state.indicator["Name"] not in st.session_state.df_indicators["Name"].values:
            
            # Add new row
            st.session_state.df_indicators = st.session_state.df_indicators._append(st.session_state.indicator, ignore_index=True)
            st.session_state.df_checkbox = st.session_state.df_checkbox._append(st.session_state.checkbox_defaults, ignore_index=True)
        else:
            st.warning("This indicator already exists in your indicators list")
    st.button(label="Reset Indicator", on_click=reset_indicator)

def general_information(df_chosen :pd.DataFrame):
    st.subheader("General Information")
    st.session_state.indicator["Name"] = st.text_input("Indicator Name", value=st.session_state.indicator["Name"])
    st.session_state.indicator["Variable"] = st.selectbox("Variable", options=df_chosen.columns,key="variable")
    indicator_type = st.session_state.indicator["Indicator Type"] = st.selectbox("Indicator Type", options=INDICATOR_TYPES, key="indicator_type")
    return indicator_type

def indicator_building(df_chosen:pd.DataFrame, season_start, season_end):
    st.subheader("Create indicators")
    with st.expander("Indicator template",expanded=True):
        
        indicator_type = general_information(df_chosen)
        if indicator_type in ["Outlier Days", "Consecutive Outlier Days"]:
            handle_threshold_input()
        elif indicator_type == "Season Aggregation":
            handle_yearly_threshold_input()
            print(st.session_state.indicator)
            print(st.session_state.checkbox_defaults)

        handle_yearly_aggregation_input()
        handle_season_shift_input(season_start, season_end)

        # Button 
        handle_buttons()



# ---------------------------
# --- Handle upadate part ---
# ---------------------------

def general_information_update(updated_indicator,i, df_chosen:pd.DataFrame):
    
    updated_indicator["Name"] = st.text_input("Indicator Name", updated_indicator["Name"], key=f"edit_name_{i}")
    updated_indicator["Variable"] = st.selectbox("Variable", options =df_chosen.columns,
                                                 index=list(df_chosen.columns).index(updated_indicator["Variable"]), 
                                                 key=f"edit_variable_{i}")
    
    updated_indicator["Indicator Type"] = st.selectbox("Indicator Type", options=INDICATOR_TYPES, 
                                                       index=INDICATOR_TYPES.index(updated_indicator["Indicator Type"]), 
                                                       key=f"edit_indicator_type_{i}")


def handle_input_update(updated_indicator, updated_checkbox_value,label, i):
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        
        if st.checkbox(label=label, value=updated_checkbox_value, key=f"edit_{"_".join(label.lower().split(" "))}_checkbox_{i}"):
            with col2:
                updated_indicator[label] = st.number_input(label=label, 
                                                           value=updated_indicator[label], 
                                                           label_visibility="collapsed", 
                                                           key=f"edit_{"_".join(label.lower().split(" "))}_{i}")
        else:
            updated_indicator[label] = None

    
def handle_input_update_season_shift_start(updated_indicator, updated_checkbox_value,label, i, season_start):
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        
        if st.checkbox(label=label, value=updated_checkbox_value, key=f"edit_{"_".join(label.lower().split(" "))}_checkbox_{i}"):
            with col2:
                updated_indicator[label] = st.number_input(label=label, 
                                                           value=updated_indicator[label], 
                                                           min_value=0,
                                                           max_value = season_start,
                                                           label_visibility="collapsed", 
                                                           key=f"edit_{"_".join(label.lower().split(" "))}_{i}")
        else:
            updated_indicator[label] = None

def handle_input_update_season_shift_end(updated_indicator, updated_checkbox_value,label, i, season_end):
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        
        if st.checkbox(label=label, value=updated_checkbox_value, key=f"edit_{"_".join(label.lower().split(" "))}_checkbox_{i}"):
            with col2:
                updated_indicator[label] = st.number_input(label=label, 
                                                           value=updated_indicator[label], 
                                                           min_value=0,
                                                           max_value = 12 - season_end,
                                                           label_visibility="collapsed", 
                                                           key=f"edit_{"_".join(label.lower().split(" "))}_{i}")
        else:
            updated_indicator[label] = None

def handle_update_checkbox_and_input_yearly_agg_min(updated_indicator, updated_checkbox_value, label, i):
    col1, col2 = st.columns([0.2, 0.8])
    print(updated_indicator[label])
    with col1:
        if st.checkbox(label=label,value=updated_checkbox_value, key=f"edit_{"_".join(label.lower().split(" "))}_checkbox_{i}"):
            with col2:
                st.write(updated_indicator[label])
                updated_indicator[label] = st.number_input(label, value=updated_indicator[label], label_visibility="collapsed", key=f"edit{"_".join(label.lower().split(" "))}_{i}")
        else:
            updated_indicator[label] = None
            updated_indicator[label+" Step"] = None
            updated_indicator[label+" List"] = None
    if updated_indicator[label] is not None:
        st.subheader("Step below")
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            st.write("""Choose a step value to define additional thresholds below the current one. 
                    Each step will determine the range for hazard levels (e.g., Low, Moderate, High, Very High).
                    Starting from the current threshold, each subsequent range will be created by substracting the step value.""")
        
        with col2:
            updated_indicator[label+" Step"] = step = st.number_input(label="Step",
                                                                        value=updated_indicator[label+" Step"],
                                                                        key=f"edit step below {i}",
                                                                        label_visibility="collapsed")

            updated_indicator[label+" List"] = [updated_indicator[label] - step * i for i in range(NUM_THRESHOLDS + 1)]
        st.write("Your ohter threshold will be the ones there ", updated_indicator[label+" List"])
    else:
        updated_indicator[label] = None

def handle_update_checkbox_and_input_yearly_agg_max(updated_indicator, updated_checkbox_value, label, i):
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
 
        if st.checkbox(label=label, value=updated_checkbox_value, key=f"edit_{"_".join(label.lower().split(" "))}_checkbox_{i}"):
            with col2:
                st.write(updated_indicator[label])
                updated_indicator[label] = st.number_input(label, value=updated_indicator[label], label_visibility="collapsed",  key=f"edit{"_".join(label.lower().split(" "))}_{i}")
        else:
            updated_indicator[label] = None
            updated_indicator[label+" Step"] = None
            updated_indicator[label+" List"] = None
    if updated_indicator[label] is not None:
        col1, col2 = st.columns([0.8, 0.2])
        st.subheader("Step above")
        with col1:
            st.write("""Choose a step value to define additional thresholds above the current one. 
                    Each step will determine the range for hazard levels (e.g., Low, Moderate, High, Very High).
                    Starting from the current threshold, each subsequent range will be created by adding the step value.""")
        
        with col2:
            st.write(updated_indicator[label+" Step"])
            updated_indicator[label+" Step"] = step = st.number_input(label="Step",
                                                                        value=updated_indicator[label+" Step"],
                                                                        key=f"edit step above {i}",
                                                                        label_visibility="collapsed")

            updated_indicator[label+" List"] = [updated_indicator[label] + step * i for i in range(NUM_THRESHOLDS + 1)]
        st.write("Your ohter threshold will be the ones there ", updated_indicator[label+" List"])
    
    print(updated_indicator)


def handle_threshold_update(updated_indicator, updated_checkbox, i):

    # Handle all the threshold update
    if updated_indicator["Indicator Type"] in ["Outlier Days", "Consecutive Outlier Days"]:
        
        handle_threshold_daily_update(updated_indicator, updated_checkbox, i)
        handle_threshold_yearly_update(updated_indicator, updated_checkbox, i)
    elif updated_indicator["Indicator Type"] == "Season Aggregation":
        handle_threshold_yearly_update(updated_indicator, updated_checkbox, i)

def handle_threshold_daily_update(updated_indicator, updated_checkbox, i):
    st.subheader("Daily Thresholds")
    handle_input_update(updated_indicator, updated_checkbox["min_daily_checkbox"],"Daily Threshold Min", i)
    handle_input_update(updated_indicator, updated_checkbox["max_daily_checkbox"],"Daily Threshold Max", i)

def handle_threshold_yearly_update(updated_indicator, updated_checkbox, i):
    st.subheader("Yearly Thresholds")
    print("\n In the upadated part")
    print(updated_indicator)
    print(updated_checkbox)
    handle_update_checkbox_and_input_yearly_agg_min(updated_indicator, updated_checkbox["min_yearly_checkbox"],"Yearly Threshold Min", i)
    handle_update_checkbox_and_input_yearly_agg_max(updated_indicator, updated_checkbox["max_yearly_checkbox"],"Yearly Threshold Max", i)




def handle_shift_update(updated_indicator, updated_checkbox, i,season_start, season_end):
    
    # Handle all the shift update
    st.subheader("Season shift")
    handle_input_update_season_shift_start(updated_indicator, updated_checkbox["shift_start_checkbox"],"Season Start Shift", i, season_start)
    handle_input_update_season_shift_end(updated_indicator, updated_checkbox["shift_end_checkbox"],"Season End Shift", i, season_end)



def handle_aggregation_update(updated_indicator, i):
    
    # Handle aggregation function
    st.subheader("Aggregation functions")
    updated_indicator["Yearly Aggregation"] = st.selectbox(label="Yearly Aggregation",
                                                            options=AGG_FUNC,
                                                            index=INDICATOR_AGG[updated_indicator["Indicator Type"]][0],
                                                            key=f"edit_yearly_aggregation_{i}",
                                                            disabled=INDICATOR_AGG[updated_indicator["Indicator Type"]][1])
    
def handle_button_update(updated_indicator, row, i):
    if st.button(f"Update Indicator: {row['Name']}", key=f"edit_update_{i}"):
        st.session_state.df_indicators.loc[i] = updated_indicator

    st.button(label = "Delete Indicator",key=f"delete_{i}",on_click=lambda index=i: delete_indicator(index))

    
    
def indicator_editing(df_chosen : pd.DataFrame, season_start, season_end):
    if not st.session_state.df_indicators.empty:
        st.subheader("Edit Indicators")
        for (i, row), (j, row_checkbox) in zip(st.session_state.df_indicators.iterrows(), st.session_state.df_checkbox.iterrows()):
            with st.expander(f"Edit Indicator: {row['Name']}"):

                updated_indicator = row.to_dict()
                updated_checkbox = row_checkbox.to_dict()
    
                general_information_update(updated_indicator, i, df_chosen)
                handle_threshold_update(updated_indicator, updated_checkbox, i)
                handle_aggregation_update(updated_indicator, i)
                handle_shift_update(updated_indicator, updated_checkbox, i, season_start, season_end)
                handle_button_update(updated_indicator, row, i)
                
    else:
        st.write("No indicators available yet.")

def get_frequency_threshold_inputs():
    col1, col2, col3 = st.columns([1,5,1])
    with col2:
        with st.container(border=True):
            set_title_5("Set your frequency threshold as you wish")
            col11, col12, col13 = st.columns(3)
            with col11:
                st.number_input(label="Low_bottom", min_value=0.0, max_value=1.0, value=0.0, disabled=True, label_visibility="collapsed")
            with col12:
                set_frequency_label("Low")
            with col13:
                threshold1 = st.number_input(label="Low_top", min_value=0.0, max_value=1.0, value=0.25, disabled=False, label_visibility="collapsed")

            col11, col12, col13 = st.columns(3)
            with col11:
                st.number_input(label="Moderate_bottom", min_value=0.0, max_value=1.0, value=threshold1, disabled=True, label_visibility="collapsed")
            with col12:
                set_frequency_label("Moderate")
            with col13:
                threshold2 = st.number_input(label="Moderate_top", min_value=0.0, max_value=1.0, value=0.5, disabled=False, label_visibility="collapsed")

            col11, col12, col13 = st.columns(3)
            with col11:
                st.number_input(label="High_bottom", min_value=0.0, max_value=1.0, value=threshold2, disabled=True, label_visibility="collapsed")
            with col12:
                set_frequency_label("High")
            with col13:
                threshold3 = st.number_input(label="High_top", min_value=0.0, max_value=1.0, value=0.75, disabled=False, label_visibility="collapsed")

            col11, col12, col13 = st.columns(3)
            with col11:
                st.number_input(label="Very_High_bottom", min_value=0.0, max_value=1.0, value=threshold3, disabled=True, label_visibility="collapsed")
            with col12:
                set_frequency_label("Very High")
            with col13:
                st.number_input(label="Very_High_top", min_value=0.0, max_value=1.0, value=1.0, disabled=True, label_visibility="collapsed")
    return threshold1, threshold2, threshold3

# Indicateurs
# Les basiques
#     compte le nombre de jour
#     compte le nombre de jour consécutifs
# Pour les variables à cumul
#     Faire la sum de toute la growing season et voir si c'est entre des seuil
# A voir pour mettre un shift (growing season)
# + indicateur de variabilité


# Classe pour les yearly threshold:
# Low hazard
# Lets add so much thresholds that we will not be able to go back there