from utils.imports import *
from utils.variables import *



## Yearly
def handle_checkbox_and_input_yearly_agg_min(label : str, checkbox_key):
    """
    Handles the creation of a checkbox and a number input for setting a minimum yearly aggregation threshold.
    Allows defining additional thresholds below the entered value by specifying step values.

    Args:
        label (str): The label for the checkbox and number input.
        checkbox_key (str): A unique key for the checkbox in the session state.
    """
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        st.session_state.checkbox_defaults[checkbox_key] = st.checkbox(label=label, key=checkbox_key)
        
    if st.session_state.checkbox_defaults[checkbox_key]:
        with col2:
            st.session_state.indicator[label] = st.number_input(label, value=None, label_visibility="collapsed", key="_".join(label.lower().split(" ")))
        if st.session_state.indicator[label] is not None:
            st.subheader("Step below")
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.write("""
                            Specify a step value to create additional thresholds above the main threshold. 
                            These thresholds will represent distinct hazard levels (e.g., Low, Moderate, High, Very High). 
                            Each range is calculated by adding multiples of the step value to the current threshold.
                        """)
            
            with col2:
                st.session_state.indicator[label+ " Step"] = step = st.number_input(label="Step",key="step below", label_visibility="collapsed")

                st.session_state.indicator[label+" List"] = [st.session_state.indicator[label] - step * i for i in range(NUM_THRESHOLDS + 1)]
        st.write("Your ohter threshold will be the ones there ", st.session_state.indicator[label+" List"])
    else:
        st.session_state.indicator[label] = None


def handle_checkbox_and_input_yearly_agg_max(label : str, checkbox_key):    
    """
    Handles the creation of a checkbox and a number input for setting a maximum yearly aggregation threshold.
    Allows defining additional thresholds above the entered value by specifying step values.

    Args:
        label (str): The label for the checkbox and number input.
        checkbox_key (str): A unique key for the checkbox in the session state.
    """

    # Basic threshold part
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        st.session_state.checkbox_defaults[checkbox_key] = st.checkbox(label=label, key=checkbox_key)
        
    if st.session_state.checkbox_defaults[checkbox_key]:
        with col2:
            st.session_state.indicator[label] = step = st.number_input(label, value=None, label_visibility="collapsed", key="_".join(label.lower().split(" ")))
        
        # Step part
        if st.session_state.indicator[label] is not None:
            st.subheader("Step above")
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.write(f"""
                            Specify a step value to create additional thresholds above the main threshold. 
                            These thresholds will represent distinct hazard levels (e.g., Low, Moderate, High, Very High). 
                            Each range is calculated by adding multiples of the step value to the current threshold.
                        """)
            
            with col2:
                st.session_state.indicator[label+ " Step"] = step = st.number_input(label="Step", key="step above", label_visibility="collapsed")

                st.session_state.indicator[label+" List"] = [st.session_state.indicator[label] + step * i for i in range(NUM_THRESHOLDS + 1)]

        # Here maybe an animation could be find to better present the different threshold built by his choices
        st.write("Your ohter threshold will be the ones there ", st.session_state.indicator[label+" List"])
    else:
        st.session_state.indicator[label] = None

## Season shift
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