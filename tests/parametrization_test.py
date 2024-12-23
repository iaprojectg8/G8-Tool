from utils.imports import *
from indicators.parametrization.parametrization import select_season


# Define the test function
def test_select_season(monkeypatch):
    # Mock the slider to return a specific date range for testing
    monkeypatch.setattr(st, "slider", MagicMock(return_value=(datetime(2000, 3, 1), datetime(2000, 8, 31))))

    # Call the function
    start_month, end_month = select_season()

    # Assert that the returned months are correct
    assert start_month == 3, f"Expected start_month to be 3, but got {start_month}"
    assert end_month == 8, f"Expected end_month to be 8, but got {end_month}"