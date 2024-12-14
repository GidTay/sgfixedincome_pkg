from sgfixedincome_pkg import mas_api_client
import pytest
import pandas as pd
import requests
from unittest.mock import patch, Mock
from datetime import datetime
import pytz

def test_initialization():
    """
    Test that MAS_bondsandbills_APIClient correctly initializes an API
    client for Monetary Authority of Singapore (MAS) bonds and bills endpoints.
    """
    client = mas_api_client.MAS_bondsandbills_APIClient()
    assert client.base_url == "https://eservices.mas.gov.sg/statistics/api/v1/bondsandbills/m/"

def test_fetch_data_success():
    """
    Test successful API data fetching with fetch_data method.
    Verifies both the returned data and that the correct URL and parameters were used.
    """
    client = mas_api_client.MAS_bondsandbills_APIClient()
    base_url = "https://eservices.mas.gov.sg/statistics/api/v1/bondsandbills/m/"
    
    # Mock the requests.get response
    mock_response = Mock()
    mock_response.json.return_value = {
        "success": True,
        "result": {
            "total": 1,
            "records": [{"test": "data"}]
        }
    }
    mock_response.raise_for_status.return_value = None
    
    with patch('requests.get', return_value=mock_response) as mock_get:
        # Test with no parameters
        endpoint = "test_endpoint"
        result = client.fetch_data(endpoint)
        assert result == mock_response.json.return_value
        
        # Verify requests.get was called with correct URL
        mock_get.assert_called_with(f"{base_url}{endpoint}", params=None)
        
        # Test with parameters
        params = {"param1": "value1", "param2": "value2"}
        result = client.fetch_data(endpoint, params=params)
        assert result == mock_response.json.return_value
        
        # Verify requests.get was called with correct URL and parameters
        mock_get.assert_called_with(f"{base_url}{endpoint}", params=params)
        
        # Verify the total number of calls
        assert mock_get.call_count == 2

def test_fetch_data_http_error():
    """
    Test fetch_data method handling of HTTP errors.
    """
    client = mas_api_client.MAS_bondsandbills_APIClient()
    
    # Mock requests.get to raise an HTTPError
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("404 Client Error")
    
    with patch('requests.get', return_value=mock_response):
        with pytest.raises(requests.HTTPError):
            client.fetch_data("test_endpoint")

@patch.object(mas_api_client.MAS_bondsandbills_APIClient, "fetch_data")
def test_get_latest_ssb_details(mock_fetch_data):
    """
    Test that get_latest_ssb_details extracts dictionary record from 
    nested dictionary structure obtained from API get request.
    """
    client = mas_api_client.MAS_bondsandbills_APIClient()
    mock_fetch_data.return_value = { # Mock the return from fetch_data()
        "success": True,
        "result": {
            "total": 1,
            "records": [{
                "issue_code": "GX25010E",
                "isin_code": "SGXZ30907869",
                "last_day_to_apply": "2024-12-26"
            }]
        }
    }
    ssb_details = client.get_latest_ssb_details()
    assert ssb_details == {
        "issue_code": "GX25010E",
        "isin_code": "SGXZ30907869",
        "last_day_to_apply": "2024-12-26"
    }

@patch.object(mas_api_client.MAS_bondsandbills_APIClient, "get_latest_ssb_details")
def test_get_latest_ssb_issue_code(mock_get_latest_ssb_details):
    """
    Test that get_latest_ssb_issue_code extracts issue code from dictionary.
    """
    client = mas_api_client.MAS_bondsandbills_APIClient()
    mock_get_latest_ssb_details.return_value = { # Mock the return from get_latest_ssb_details()
        "issue_code": "GX25010E",
        "isin_code": "SGXZ30907869",
        "last_day_to_apply": "2024-12-26"
    }
    issue_code = client.get_latest_ssb_issue_code()
    assert issue_code == "GX25010E"

@patch.object(mas_api_client.MAS_bondsandbills_APIClient, "get_latest_ssb_details")
def test_get_latest_ssb_last_day_to_apply(mock_get_latest_ssb_details):
    """
    Test that get_latest_ssb_last_day_to_apply extracts last day to apply from dictionary.
    """
    client = mas_api_client.MAS_bondsandbills_APIClient()
    mock_get_latest_ssb_details.return_value = { # Mock the return from get_latest_ssb_details()
        "issue_code": "GX25010E",
        "isin_code": "SGXZ30907869",
        "last_day_to_apply": "2024-12-26"
    }
    last_day_to_apply = client.get_latest_ssb_last_day_to_apply()
    assert last_day_to_apply == "2024-12-26"

@patch.object(mas_api_client.MAS_bondsandbills_APIClient, "fetch_data")
def test_get_ssb_interest(mock_fetch_data):
    """
    Test that get_ssb_interest extracts dictionary record from nested dictionary structure.
    """
    client = mas_api_client.MAS_bondsandbills_APIClient()
    mock_fetch_data.return_value = { # Mock the return from fetch_data()
        "success": True,
        "result": {
            "total": 1,
            "records": [{
                "issue_code": "GX25010E",
                "year1_coupon": 2.73,
                "year1_return": 2.73,
                "year2_coupon": 2.82,
                "year2_return": 2.77,
                "year3_coupon": 2.82,
                "year3_return": 2.79,
                "year4_coupon": 2.82,
                "year4_return": 2.8,
                "year5_coupon": 2.82,
                "year5_return": 2.8,
                "year6_coupon": 2.85,
                "year6_return": 2.81,
                "year7_coupon": 2.9,
                "year7_return": 2.82,
                "year8_coupon": 2.95,
                "year8_return": 2.84,
                "year9_coupon": 2.99,
                "year9_return": 2.85,
                "year10_coupon": 3.01,
                "year10_return": 2.86
            }]
        }
    }
    interest_details = client.get_ssb_interest("GX25010E")
    assert interest_details == {
        "issue_code": "GX25010E",
        "year1_coupon": 2.73,
        "year1_return": 2.73,
        "year2_coupon": 2.82,
        "year2_return": 2.77,
        "year3_coupon": 2.82,
        "year3_return": 2.79,
        "year4_coupon": 2.82,
        "year4_return": 2.8,
        "year5_coupon": 2.82,
        "year5_return": 2.8,
        "year6_coupon": 2.85,
        "year6_return": 2.81,
        "year7_coupon": 2.9,
        "year7_return": 2.82,
        "year8_coupon": 2.95,
        "year8_return": 2.84,
        "year9_coupon": 2.99,
        "year9_return": 2.85,
        "year10_coupon": 3.01,
        "year10_return": 2.86
    }

@patch.object(mas_api_client.MAS_bondsandbills_APIClient, "get_ssb_interest")
def test_get_ssb_coupons(mock_get_ssb_interest):
    """
    Test that get_ssb_coupons function extracts coupon list from a SSB coupon and returns dictionary.
    """
    client = mas_api_client.MAS_bondsandbills_APIClient()
    mock_get_ssb_interest.return_value = { # Mock the return from get_ssb_interest()
        "issue_code": "GX25010E",
        "year1_coupon": 2.73,
        "year1_return": 2.73,
        "year2_coupon": 2.82,
        "year2_return": 2.77,
        "year3_coupon": 2.82,
        "year3_return": 2.79,
        "year4_coupon": 2.82,
        "year4_return": 2.8,
        "year5_coupon": 2.82,
        "year5_return": 2.8,
        "year6_coupon": 2.85,
        "year6_return": 2.81,
        "year7_coupon": 2.9,
        "year7_return": 2.82,
        "year8_coupon": 2.95,
        "year8_return": 2.84,
        "year9_coupon": 2.99,
        "year9_return": 2.85,
        "year10_coupon": 3.01,
        "year10_return": 2.86
    }
    coupons = client.get_ssb_coupons("GX25010E")
    assert coupons == [2.73, 2.82, 2.82, 2.82, 2.82, 2.85, 2.9, 2.95, 2.99, 3.01]

def test_calculate_ssb_tenure_rates_valid():
    """
    Test calculate_ssb_tenure_rates with a standard set of coupons.
    Verifies generated DataFrame structure and values aligns with expectations.
    """
    client = mas_api_client.MAS_bondsandbills_APIClient()
    coupons = [2.73, 2.82, 2.82, 2.82, 2.82, 2.85, 2.9, 2.95, 2.99, 3.01]
    result = client.calculate_ssb_tenure_rates(coupons)
    
    # Check DataFrame properties
    assert isinstance(result, pd.DataFrame), "Result should be a pandas DataFrame"
    assert len(result) == 120, "DataFrame should have exactly 120 rows"
    assert list(result.columns) == ["Tenure", "Rate"], "DataFrame should have Tenure and Rate columns"
    
    expected_rates = [
        2.76, 2.76, 2.76, 2.75, 2.75, 2.75, 2.75, 2.74, 2.74, 2.74, 2.73, 2.73, # First year
        2.73, 2.74, 2.74, 2.74, 2.74, 2.74, 2.74, 2.74, 2.74, 2.74, 2.74, 2.74,
        2.74, 2.73, 2.73, 2.73, 2.73, 2.73, 2.73, 2.72, 2.72, 2.72, 2.72, 2.72, 
        2.71, 2.71, 2.71, 2.71, 2.7, 2.7, 2.7, 2.7, 2.69, 2.69, 2.69, 2.69,
        2.68, 2.68, 2.68, 2.68, 2.67, 2.67, 2.67, 2.67, 2.66, 2.66, 2.66, 2.66, # Fifth year
        2.65, 2.65, 2.65, 2.65, 2.65, 2.64, 2.64, 2.64, 2.64, 2.64, 2.63, 2.63,
        2.63, 2.63, 2.63, 2.62, 2.62, 2.62, 2.62, 2.62, 2.62, 2.61, 2.61, 2.61,
        2.61, 2.61, 2.61, 2.6, 2.6, 2.6, 2.6, 2.6, 2.6, 2.59, 2.59, 2.59, 
        2.59, 2.59, 2.59, 2.59, 2.58, 2.58, 2.58, 2.58, 2.58, 2.58, 2.58, 2.57, 
        2.57, 2.57, 2.57, 2.57, 2.57, 2.57, 2.56, 2.56, 2.56, 2.56, 2.56, 2.56  # Tenth year                     
    ]
    
    for i, (_, row) in enumerate(result.iterrows()):
        assert row['Tenure'] == i + 1, f"Tenure for row {i} should be {i+1}"
        assert row['Rate'] == expected_rates[i], f"Rate for tenure {row['Tenure']} does not match expected value {expected_rates[i]}."
    
@pytest.mark.parametrize(
    "coupons",
    [
        # Invalid coupon lists
        [2.73, 2.82, 2.82], # Need 10 elements
        [2.7, 2.7, 2.7, 2.8, 2.8, 2.8, 2.9, 2.9, 2.9, 1.0] # Not monotonically increasing
    ]
)
def test_calculate_ssb_tenure_rates_invalid(coupons):
    """
    Test that calculate_ssb_tenure_rates raises a ValueError with invalid inputs.
    """
    client = mas_api_client.MAS_bondsandbills_APIClient()
    with pytest.raises(ValueError):
        client.calculate_ssb_tenure_rates(coupons)

@patch.object(mas_api_client.MAS_bondsandbills_APIClient, "fetch_data")
def test_get_most_recent_6m_tbill(mock_fetch_data):
    """
    Test that get_most_recent_6m_tbill extracts dictionary record from 
    nested dictionary structure obtained from API get request.
    """
    client = mas_api_client.MAS_bondsandbills_APIClient()
    mock_fetch_data.return_value = { # Mock the return from fetch_data()
        "success": True,
        "result": {
            "total": 1,
            "records": [{
                "issue_code": "BS24124Z",
                "isin_code": "SGXZ29257813",
                "cutoff_yield": "3.0"
            }]
        }
    }
    tbill_details = client.get_most_recent_6m_tbill()
    assert tbill_details == {
        "issue_code": "BS24124Z",
        "isin_code": "SGXZ29257813",
        "cutoff_yield": "3.0"
    }

@patch.object(mas_api_client.MAS_bondsandbills_APIClient, "fetch_data")
def test_get_6m_tbill_bid_yield(mock_fetch_data):
    """
    Test that get_6m_tbill_bid_yield extracts bid yield from dictionary.
    """
    client = mas_api_client.MAS_bondsandbills_APIClient()
    mock_fetch_data.return_value =  { # Mock the return from fetch_data() priceandyields endpoint
        "success": True,
        "result": {
            "total": 1,
            "records": [{
                "end_of_period": "2024-11-14",
                "product_type": "B",
                "bid_6m_tbill_yield": 3.01,
                "bid_1y_tbill_yield": 2.73,
                "bid_2y_bond_yield": 2.84
            }]
        }
    }
    bid_yield = client.get_6m_tbill_bid_yield()
    assert bid_yield == 3.01

import pytest
from unittest.mock import patch, MagicMock

@pytest.mark.parametrize(
    "bid_yield, cutoff_yield, threshold, expected_warning",
    [
        # No warning scenarios
        (3.50, 3.52, 10, False),   # Within threshold (2bps difference)
        (3.35, 3.50, 20, False),   # Within larger threshold
        (3.45, 3.55, 10, False),   # Exactly at threshold
        
        # Warning scenarios
        (3.50, 3.65, 10, True),    # Above threshold (positive difference)
        (3.65, 3.50, 10, True),    # Above threshold (negative difference)
        (3.30, 3.50, 15, True)     # Exceeds larger threshold
    ],
)
@patch("warnings.warn")
@patch.object(mas_api_client.MAS_bondsandbills_APIClient, "get_6m_tbill_bid_yield")
@patch.object(mas_api_client.MAS_bondsandbills_APIClient, "get_most_recent_6m_tbill")
def test_sudden_6m_tbill_yield_change_warning(
    mock_get_most_recent_6m_tbill, mock_get_6m_tbill_bid_yield, 
    mock_warn, bid_yield, cutoff_yield, threshold, expected_warning
):
    """
    Parameterized test for sudden T-bill yield change warning.

    The test uses parameterized inputs to cover multiple scenarios, 
    including cases where warnings are and are not expected.
    
    Args:
        mock_get_most_recent_6m_tbill: Mock for the `get_most_recent_6m_tbill` method 
            of the `MAS_bondsandbills_APIClient` class, simulating the retrieval of 
            details for the most recent T-bill.
        mock_get_6m_tbill_bid_yield: Mock for the `get_6m_tbill_bid_yield` method 
            of the `MAS_bondsandbills_APIClient` class, simulating the retrieval of 
            the bid yield for the most recent T-bill.
        mock_warn: Mock for the `warnings.warn` function, used to check 
            whether warnings are issued correctly and to capture the warning messages.
        bid_yield: Simulated bid yield for the most recent 6-month T-bill
        cutoff_yield: Simulated cutoff yield for the most recent 6-month T-bill
        threshold: Threshold for yield difference
        expect_warning: Whether a warning is expected
    """
    # Mocking the client methods
    client = mas_api_client.MAS_bondsandbills_APIClient()
    mock_get_6m_tbill_bid_yield.return_value = bid_yield
    mock_get_most_recent_6m_tbill.return_value = {
        "issue_code": "BS24124Z",
        "isin_code": "SGXZ29257813",
        "cutoff_yield": cutoff_yield
    }

    # Call the method
    client.sudden_6m_tbill_yield_change_warning(threshold=threshold)

    # Assert if warnings.warn was called correctly
    if expected_warning:
        # Check if any call contains the relevant part of the warning
        assert any(
            "The difference between the bid yield and the cutoff yield is large"
            in str(call.args[0])
            for call in mock_warn.call_args_list
        ), "Expected warning not found in warnings.warn calls"
    else:
        mock_warn.assert_not_called()

@patch("warnings.warn")
@patch.object(mas_api_client.MAS_bondsandbills_APIClient, "get_6m_tbill_bid_yield")
@patch.object(mas_api_client.MAS_bondsandbills_APIClient, "get_most_recent_6m_tbill")
def test_sudden_6m_tbill_yield_change_warning_exception(
    mock_get_most_recent_6m_tbill, mock_get_6m_tbill_bid_yield, mock_warn
):
    """
    Test that a warning is issued when an exception occurs in 
    `sudden_6m_tbill_yield_change_warning`.
    """
    # Mocking the client methods to raise exceptions
    client = mas_api_client.MAS_bondsandbills_APIClient()
    mock_get_6m_tbill_bid_yield.side_effect = Exception("Simulated error")
    mock_get_most_recent_6m_tbill.return_value = {
        "issue_code": "BS24124Z",
        "isin_code": "SGXZ29257813",
        "cutoff_yield": 3.12
    }

    # Call the method
    client.sudden_6m_tbill_yield_change_warning(threshold=10)

    # Assert that the warning was raised with the exception message
    mock_warn.assert_called_once_with(
        "Failed to check for sudden T-bill yield changes: Simulated error"
    )

@patch('warnings.warn')
def test_past_last_day_to_apply_ssb_warning_before_deadline(mock_warn):
    """
    Test past_last_day_to_apply_ssb_warning when current date is before the deadline.
    """
    client = mas_api_client.MAS_bondsandbills_APIClient()
    
    # Mock get_latest_ssb_last_day_to_apply to return a future date
    future_date = (datetime.now().date() + pd.Timedelta(days=7)).strftime('%Y-%m-%d')
    with patch.object(client, 'get_latest_ssb_last_day_to_apply', return_value=future_date):
        client.past_last_day_to_apply_ssb_warning()
        mock_warn.assert_not_called()

@patch('warnings.warn')
def test_past_last_day_to_apply_ssb_warning_after_deadline(mock_warn):
    """
    Test past_last_day_to_apply_ssb_warning when current date is after the deadline.
    """
    client = mas_api_client.MAS_bondsandbills_APIClient()
    
    # Mock get_latest_ssb_last_day_to_apply to return a past date
    past_date = (datetime.now().date() - pd.Timedelta(days=1)).strftime('%Y-%m-%d')
    with patch.object(client, 'get_latest_ssb_last_day_to_apply', return_value=past_date):
        client.past_last_day_to_apply_ssb_warning()
        mock_warn.assert_called_once()
        assert "The last day to apply for the latest SSB" in str(mock_warn.call_args[0][0])

@patch('warnings.warn')
def test_past_last_day_to_apply_ssb_warning_exception(mock_warn):
    """
    Test past_last_day_to_apply_ssb_warning when an exception occurs.
    """
    client = mas_api_client.MAS_bondsandbills_APIClient()
    
    # Mock get_latest_ssb_last_day_to_apply to raise an exception
    with patch.object(
        client, 
        'get_latest_ssb_last_day_to_apply', 
        side_effect=Exception("Test error")
    ):
        client.past_last_day_to_apply_ssb_warning()
        mock_warn.assert_called_once()
        assert "Failed to check if the last day to apply for SSB has passed" in str(
            mock_warn.call_args[0][0]
        )
