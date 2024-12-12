from sgfixedincome_pkg import mas_api_client
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

def test_initialization():
    """
    Test that MAS_bondsandbills_APIClient correctly initializes an API
    client for Monetary Authority of Singapore (MAS) bonds and bills endpoints.
    """
    client = mas_api_client.MAS_bondsandbills_APIClient()
    assert client.base_url == "https://eservices.mas.gov.sg/statistics/api/v1/bondsandbills/m/"

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