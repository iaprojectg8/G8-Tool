from utils.imports import *


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

def set_frequency_label(title):
    st.markdown(
        f"""
        <p style="text-align: center;font-size:20px">{title}</p>
        """, 
        unsafe_allow_html=True
    )