from utils.imports import * 
from utils.variables import ZIP_FOLDER, REQUEST_TYPE, TOOL_LOGO, G8_LOGO, TRANSPARENT_TOOL_LOGO, WELCOME_TEXT
from layouts.layout import *
from lib.session_variables import *
from requests_api.helpers import *
from requests_api.open_meteo_request import open_meteo_request
from requests_api.cmip6_requests import cmip6_request
from parametrization.widgets_parametrization import page_config, increase_logo
from lib.menu import menu




def main():
    """Basic Streamlit app with a title."""
    # Set some layout parameters for the page 
    page_config(TRANSPARENT_TOOL_LOGO)
    st.logo(G8_LOGO, size="large", link="https://groupehuit.com/")
    increase_logo()
    set_page_title("Welcome on :")
    page_name = "Welcome page"
    
    def stream_data():
        for char in WELCOME_TEXT:
            yield char 
            time.sleep(0.004)


    _, col, _ = st.columns(3)
    with col:
        st.image(TOOL_LOGO)
    _, col, _ = st.columns([1, 3, 1])
    with col:
        st.markdown("""
            <style>
            .stHorizontalBlock {
                text-align: justify;
            }
            </style>
        """, unsafe_allow_html=True)
        if st.session_state.last_page != page_name:
            st.write_stream(stream_data)
            st.session_state.last_page = page_name
        else: 
            st.write(WELCOME_TEXT)
    if "mode" not in st.session_state:
        st.session_state.mode = "None"  # Default mode
    _, col, _ = st.columns([1, 1, 1])
    with col:
        mode = st.radio("Choose a mode:", ["Beginner", "Expert"],
                        on_change=set_mode,
                         horizontal=True, 
                         label_visibility="collapsed",
                         key="_mode",
                         )

    # Update session state if mode changes
    if st.session_state.mode != mode:
        st.session_state.mode = mode
    st.markdown(
        """
        <style>
            .stRadio [role="radiogroup"] {
                display: flex;
                justify-content: center;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    menu()



    

        
        
        


if "__main__":
    main()