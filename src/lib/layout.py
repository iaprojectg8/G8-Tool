from src.utils.imports import *
from src.utils.variables import WELCOME_TEXT
from src.lib.menu import menu

# --------------------
# --- Title layout ---
# --------------------

def set_page_title(title):
    st.markdown(
        f"""
        <h1 style="text-align: center;font-size:60px">{title}</h1>
        """, 
        unsafe_allow_html=True
    )

def set_title_1(title):
    st.markdown(f"# {title}",unsafe_allow_html=True)

def set_title_2(title):
    st.markdown(f"## {title}")

def set_title_3(title):
    st.markdown(f"### {title}")

def set_title_4(title):
    st.markdown(f"#### {title}")

def set_title_5(title):
    st.markdown(
        f"""
        <h5 style="text-align: center">{title}</h5>
        """, 
        unsafe_allow_html=True
    )


# -----------------------------------------------
# --- Managing the branding aspect of the app ---
# -----------------------------------------------


def increase_logo():
    """
    Increase the GroupeHuit logo size on the top left of the page
    """

    st.markdown("""
                <style>
        div[data-testid="stSidebarHeader"] > img, div[data-testid="collapsedControl"] > img {
            height: 3rem;
            width: auto;
        }
        
        div[data-testid="stSidebarHeader"], div[data-testid="stSidebarHeader"] > *,
        div[data-testid="collapsedControl"], div[data-testid="collapsedControl"] > * {
            display: flex;
            align-items: center;
        }
    </style>
                """,unsafe_allow_html=True)
    
    
def page_config_and_menu(tab_logo, sidebar_logo):
    """
    Set page configuraton, menu, and logo
    Args:
        tab_logo (str): Path to the logo to display on the tab
        sidebar_logo (str): Path to the logo to display on the sidebar
    """
    with open(tab_logo, "rb") as file:
        svg_content = file.read()
    st.set_page_config(page_icon=svg_content, layout="wide")

    menu()
    
    st.logo(sidebar_logo, size="large", link="https://groupehuit.com/")
    increase_logo()
