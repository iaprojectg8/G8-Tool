from src.utils.imports import *
from src.lib.session_variables import set_mode


def centered_logo(logo_path):
    """
    Display the tool logo in the center of the page.
    Args:
        logo_path (str): Path to the logo image.
    """
    _, col, _ = st.columns(3)
    with col:
        st.image(logo_path)

def stream_data(welcome_text):
    """
    Stream data character by character with a delay.
    Args:
        welcome_text (str): Text to display.
    """
    for char in welcome_text:
        yield char 
        time.sleep(0.007)

def manage_welcome_text(welcome_text, page_name):
    """
    Manage the display of the welcome text on the page. Include a markdown style to justify the text.
    Args:
        welcome_text (str): Text to display.
        page_name (str): Name of the page.
    """
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
            st.write_stream(stream_data(welcome_text))
            st.session_state.last_page = page_name
        else: 
            st.write(welcome_text)


def mode_choice(mode_list: list):
    """
    Display a radio button for mode choice and update session state, including a style to center the radio button.
    """
    _, col, _ = st.columns([1, 1, 1])
    with col:
        mode = st.radio("Choose a mode:", mode_list,
                        on_change=set_mode,
                         horizontal=True, 
                         index=mode_list.index(st.session_state.mode),
                         label_visibility="collapsed",
                         key="_mode",
                         disabled=True
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