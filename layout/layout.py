from utils.imports import *

def set_page_width(width):
    st.markdown(
        f"""
        <style>
            .main .block-container {{
                max-width: {width}px;  /* Adjust width as desired */
                padding-left: 2rem;
                padding-right: 2rem;
            }}
        </style>
        """, 
        unsafe_allow_html=True
    )

def set_page_title(title):
    st.markdown(
        """
        <h1 style="text-align: center;font-size:60px">General Information</h1>
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
    st.markdown(f"##### {title}")