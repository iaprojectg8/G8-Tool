import streamlit as st
import os
from utils.variables import PAGE_FILES, BEGINNER_MODE, EXPERT_MODE


def home():
    # Show a navigation menu for unauthenticated users
    st.sidebar.page_link("Welcome.py", label="Welcome on Klim")

def menu():
    # Determine if a user is logged in or not, then show the correct
    # navigation menu
    if "mode" not in st.session_state or st.session_state.mode == None:
        home()
    choice_menu()


def choice_menu():
    # Show a navigation menu for authenticated users
    st.sidebar.page_link("Welcome.py", label="Welcome on Klim")
    if st.session_state.mode == "Beginner":
        st.sidebar.page_link("pages/Beginner Request.py", label="Request")
        st.sidebar.page_link("pages/Beginner Results.py", label="General Results")
    elif st.session_state.mode == "Expert":

        st.sidebar.page_link("pages/1 - General Information & Requests.py")
        st.sidebar.page_link("pages/2 - Indicators Parametrization.py")
        st.sidebar.page_link("pages/3 - General Results.py")
        st.sidebar.page_link("pages/4 - Specific Results.py")
        st.sidebar.page_link("pages/5 - Extreme Analysis.py")