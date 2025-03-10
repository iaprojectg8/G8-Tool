from src.utils.imports import *
from src.utils.variables import PAGE_FILES, BEGINNER_MODE, EXPERT_MODE


def home():
    # Show a navigation menu for unauthenticated users
    st.sidebar.page_link("Welcome.py", label="Welcome on Klim")

def menu():
    if "mode" not in st.session_state or st.session_state.mode is None:
        home()
    choice_menu()


def choice_menu():
    # Show a navigation menu for authenticated users
    st.sidebar.page_link("Welcome.py", label="Welcome on Klim")
    if st.session_state.mode == "Beginner":
        st.sidebar.page_link("pages/beginner_request.py", label="Request")
        st.sidebar.page_link("pages/beginner_results.py", label="General Results")
    elif st.session_state.mode == "Expert":

        st.sidebar.page_link("pages/general_information_and_request.py", label="General Information and Request")
        st.sidebar.page_link("pages/indicator_parametrization.py", label="Indicator Parametrization")
        st.sidebar.page_link("pages/general_results.py", label="General Results")
        st.sidebar.page_link("pages/specific_results.py", label="Specific Results")
        st.sidebar.page_link("pages/extreme_analysis.py", label="Extreme Analysis")