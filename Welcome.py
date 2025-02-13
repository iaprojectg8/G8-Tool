from utils.imports import * 
from utils.variables import TOOL_LOGO, G8_LOGO, TRANSPARENT_TOOL_LOGO, WELCOME_TEXT

from lib.session_variables import *
from lib.layout import set_page_title, page_config_and_menu

from src.welcome.widget import centered_logo, manage_welcome_text, mode_choice



def main():
    """
    Welcome page of the tool.
    """
    page_name = "Welcome page"
    page_config_and_menu(TRANSPARENT_TOOL_LOGO, G8_LOGO)

    set_page_title("Welcome on :")
    centered_logo(TOOL_LOGO)
    manage_welcome_text(WELCOME_TEXT, page_name)
    mode_choice()


if "__main__":
    main()