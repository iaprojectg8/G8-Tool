import streamlit as st
from unittest.mock import patch, MagicMock
import pytest
from src.welcome.widget import centered_logo, stream_data, manage_welcome_text, mode_choice  # Adjust import path
from src.utils.variables import MODE

# |Warning| :  the decorators are LIFO, so the last one is the first to be called

# Mock the different widget used in the functions
@patch("streamlit.image") 
@patch("streamlit.columns") 
def test_centered_logo(mock_st_columns:MagicMock, mock_st_image:MagicMock):
    # Arrange
    mock_column = MagicMock()  
    mock_st_columns.return_value = [None, mock_column, None] 
    logo_path = "path/to/logo.png"  

    # Act
    centered_logo(logo_path)

    # Assert how the function was called
    mock_st_columns.assert_called_once_with(3)  
    mock_st_image.assert_called_once_with(logo_path) 
    # Verify the context manager entry and exit was called
    mock_column.__enter__.assert_called_once()  
    mock_column.__exit__.assert_called_once()  

def test_stream_data():
    welcome_text = "Hello"
    
    # Mock time.sleep to prevent delays during the test
    with patch("time.sleep", return_value=None):
        # Convert generator to a list to consume it and check output
        result = list(stream_data(welcome_text))
        
    # Assert that the result matches the expected output
    assert result == list(welcome_text)

@patch("streamlit.session_state")
@patch("streamlit.write")
@patch("streamlit.write_stream")
@patch("streamlit.markdown")
@patch("streamlit.columns", return_value=[MagicMock(), MagicMock(), MagicMock()])
def test_manage_welcome_text(mock_st_columns: MagicMock,
                             mock_st_markdown: MagicMock, 
                             mock_st_write_stream: MagicMock,
                             mock_st_write:MagicMock, 
                             mock_session_state:MagicMock):
    """Test welcome text rendering with session state."""
    mock_session_state.last_page = "About"
    manage_welcome_text("Welcome!", "Home")
    
    # Check if markdown is applied
   
    mock_st_columns.assert_called_once_with([1, 3, 1])
    mock_st_markdown.assert_called()

    mock_st_write_stream.assert_called()
    assert mock_session_state.last_page == "Home"
    manage_welcome_text("Welcome!", "Home")
    mock_st_write.assert_called()

    assert mock_session_state.last_page == "Home"


@patch("streamlit.markdown")
@patch("streamlit.session_state")
@patch("streamlit.radio")
@patch("streamlit.columns", return_value=[MagicMock(), MagicMock(), MagicMock()])
def test_mode_choice(mock_st_columns:MagicMock, 
                     mock_st_radio:MagicMock, 
                     mock_session_state:MagicMock, 
                     mock_st_markdown:MagicMock):
    """Test mode selection and session state update."""
    mock_session_state.mode = "Beginner"
    mock_st_radio.return_value = "Expert"  # Simulate user selecting "Expert"
    mode_choice(MODE)
    mock_st_columns.assert_called_once_with([1, 1, 1])
    mock_st_radio.assert_called()
    assert mock_session_state.mode == "Expert"
    
    # Check if markdown was applied for styling
    mock_st_markdown.assert_called()

    mock_session_state.mode = "Expert"
    mock_st_radio.return_value = "Beginner"  # Simulate user selecting "Expert"
    mode_choice(MODE)
    mock_st_columns.assert_called_with([1, 1, 1])
    mock_st_radio.assert_called()
    # Ensure session state is updated
    assert mock_session_state.mode == "Beginner"
    
    # Check if markdown was applied for styling
    mock_st_markdown.assert_called()
