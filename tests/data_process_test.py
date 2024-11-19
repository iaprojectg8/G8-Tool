from utils.imports import *
from lib.data_process import loads_data, column_choice

# Test for the loads_data function
def test_loads_data():
    # Prepare mock data for the CSV
    mock_data = pd.DataFrame({
        'date': [datetime(2020, 1, 1), datetime(2020, 1, 2)],
        'lat': [12.34, 12.34],
        'lon': [56.78, 56.78],
        'temperature': [20.5, 21.0]
    })

    # Mock the pd.read_csv to return mock_data instead of reading from a file
    with mock.patch('pandas.read_csv', return_value=mock_data):
        # Call the function with any filename (it doesn't matter because we mock read_csv)
        data, lat, lon = loads_data('fake_file.csv')

    # Assertions to check if the function works as expected
    assert isinstance(data, pd.DataFrame)
    assert lat == 12.34
    assert lon == 56.78
    assert data.index.name == 'date'
    assert 'temperature' in data.columns


# Test for the column_choice function
def test_column_choice():
    # Create mock data
    mock_data = pd.DataFrame({
        'date': [datetime(2020, 1, 1), datetime(2020, 1, 2)],
        'lat': [12.34, 12.34],
        'lon': [56.78, 56.78],
        'temperature': [20.5, 21.0],
        'humidity': [60, 65]
    })
               
    # Mock Streamlit's multiselect to return a chosen column
    with mock.patch('streamlit.multiselect', return_value=['temperature']):
        # Call the function with mock data
        selected_column = column_choice(mock_data)

    # Assertions to check if the correct column is selected 
    assert isinstance(selected_column, pd.DataFrame)
    assert 'temperature' in selected_column.columns
    assert len(selected_column) == 2  # Check if two rows are returned