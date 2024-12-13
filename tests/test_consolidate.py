import pytest
import pandas as pd
from unittest.mock import Mock, patch
from sgfixedincome_pkg import consolidate

# Fixtures for common test data
@pytest.fixture
def valid_df():
    return pd.DataFrame({
        'Tenure': [12],
        'Rate': [3.0],
        'Deposit lower bound': [1000],
        'Deposit upper bound': [50000],
        'Required multiples': [1000],
        'Product provider': ['Test Bank'],
        'Product': ['Fixed Deposit']
    })

# Tests for merge_dataframes function
@pytest.mark.parametrize("test_input,expected_rows", [
    (lambda valid_df: [valid_df, valid_df.copy()], 2),
    (lambda valid_df: [valid_df, pd.DataFrame()], 1),
    (lambda valid_df: [pd.DataFrame(), pd.DataFrame()], 0)
])
def test_merge_dataframes_success(valid_df, test_input, expected_rows):
    result = consolidate.merge_dataframes(test_input(valid_df))
    assert len(result) == expected_rows
    assert list(result.columns) == list(valid_df.columns)

def test_merge_dataframes_invalid_input(valid_df):
    with pytest.raises(TypeError): # Input is not a list
        consolidate.merge_dataframes("not a list")
    
    with pytest.raises(TypeError): # Input is not a list of pd.Dataframes
        consolidate.merge_dataframes([1, 2, 3])
    
    invalid_df = pd.DataFrame({'wrong_column': [1, 2, 3]}) 
    with pytest.raises(ValueError): # Input dataframe does not have required columns
        consolidate.merge_dataframes([invalid_df, valid_df])

# Tests for create_banks_df function
def test_create_banks_df_valid_input():
    test_inputs = [
        ("http://test.com", "table-class", "Test Bank", 1000)
    ]
    
    with patch('sgfixedincome_pkg.scraper.scrape_deposit_rates') as mock_scrape:
        mock_df = pd.DataFrame({
            'Tenure': [12],
            'Rate': [3.0],
            'Deposit lower bound': [1000],
            'Deposit upper bound': [50000],
            'Required multiples': [1000],
            'Product provider': ['Test Bank'],
            'Product': ['Fixed Deposit']
        })
        mock_scrape.return_value = mock_df
        
        result_df, failed_providers = consolidate.create_banks_df(test_inputs)
        assert len(result_df) == 1
        assert not failed_providers

def test_create_banks_df_scraping_failure():
    test_inputs = [
        ("http://test.com", "table-class", "Test Bank")
    ]
    
    with patch('sgfixedincome_pkg.scraper.scrape_deposit_rates') as mock_scrape:
        mock_scrape.side_effect = Exception("Scraping failed")
        
        result_df, failed_providers = consolidate.create_banks_df(test_inputs)
        assert result_df.empty
        assert len(failed_providers) == 1
        assert failed_providers[0]['product'] == 'Test Bank bank fixed deposit'

def test_create_banks_df_invalid_input():
    with pytest.raises(ValueError):
        consolidate.create_banks_df("not a list")
    
    with pytest.raises(ValueError):
        consolidate.create_banks_df([(1, 2)])  # Invalid tuple contents

# Tests for add_ssb_details function
def test_add_ssb_details():
    input_df = pd.DataFrame({
        'Tenure': [1, 2, 6, 12, 24],
        'Rate': [1.5, 1.6, 2.3, 2.55, 3.01]
    })
    
    result = consolidate.add_ssb_details(input_df, 10000, "GX24060A")

    # Verify original columns were preserved
    assert (result['Tenure'] == input_df['Tenure']).all()
    assert (result['Rate'] == input_df['Rate']).all()
    
    # For each new column, check all rows and provide clear error messages
    for column, expected_value in {
        'Deposit lower bound': 500,
        'Deposit upper bound': 190000,
        'Product': "SSB GX24060A",
        'Product provider': "MAS",
        'Required multiples': 500
    }.items():
        assert (result[column] == expected_value).all(), \
            f"Not all rows in column '{column}' have value {expected_value}. " \
            f"Found values: {result[column].unique()}"

# Tests for create_tbill_df function
def test_create_tbill_df_valid_input():
    tbill_details = {
        "issue_code": "BS24123F",
        "auction_tenor": 0.5,
        "cutoff_yield": 3.08
    }
    
    result = consolidate.create_tbill_df(tbill_details)
    assert len(result) == 1 # 1 row in dataframe
    assert result['Tenure'].iloc[0] == 6
    assert result['Rate'].iloc[0] == 3.08
    assert result['Deposit lower bound'].iloc[0] == 1000
    assert result['Required multiples'].iloc[0] == 1000
    assert result['Product provider'].iloc[0] == "MAS"
    assert result['Product'].iloc[0] == "T-bill BS24123F"

def test_create_tbill_df_invalid_tenor():
    tbill_details = {
        "issue_code": "BS24123F",
        "auction_tenor": 0.75, # Invalid tenor
        "cutoff_yield": 3.08
    }
    
    with pytest.raises(ValueError):
        consolidate.create_tbill_df(tbill_details)

@pytest.fixture
def sample_df_columns():
    return [
        'Tenure', 'Rate', 'Deposit lower bound', 'Deposit upper bound',
        'Required multiples', 'Product provider', 'Product'
    ]

# Tests for create_combined_df function
@patch('sgfixedincome_pkg.consolidate.MAS_bondsandbills_APIClient')
def test_create_combined_df_success(mock_client, sample_df_columns):
    # Mock the API client responses
    mock_client_instance = Mock()
    mock_client.return_value = mock_client_instance
    
    # Mock SSB related methods
    mock_client_instance.get_latest_ssb_issue_code.return_value = "GX24060A"
    mock_client_instance.get_ssb_coupons.return_value = [2.5, 3.0]
    mock_client_instance.calculate_ssb_tenure_rates.return_value = pd.DataFrame({
        'Tenure': [12, 24],
        'Rate': [2.5, 3.0]
    })
    
    # Mock T-bill related methods
    mock_client_instance.get_most_recent_6m_tbill.return_value = {
        "issue_code": "BS24123F",
        "auction_tenor": 0.5,
        "cutoff_yield": 3.08
    }
    
    with patch('sgfixedincome_pkg.scraper.scrape_deposit_rates') as mock_scrape:
        mock_df = pd.DataFrame({
            'Tenure': [12],
            'Rate': [3.0],
            'Deposit lower bound': [1000],
            'Deposit upper bound': [50000],
            'Required multiples': [1000],
            'Product provider': ['Test Bank'],
            'Product': ['Fixed Deposit']
        })
        mock_scrape.return_value = mock_df
        
        result_df, failures, warnings = consolidate.create_combined_df(
            scrape_inputs=[("http://test.com", "table-class", "Test Bank")],
            current_ssb_holdings=10000
        )
        
        assert not result_df.empty
        assert list(result_df.columns) == sample_df_columns
        assert not failures
        assert isinstance(warnings, list)

@patch('sgfixedincome_pkg.consolidate.MAS_bondsandbills_APIClient')
def test_create_combined_df_mixed_success_failure(mock_client):
    """Test scenario where bank scraping succeeds but SSB and T-bill API calls fail"""
    mock_client_instance = Mock()
    mock_client.return_value = mock_client_instance
    
    # Mock SSB API failure
    mock_client_instance.get_latest_ssb_issue_code.side_effect = Exception("SSB API Error")
    
    # Mock T-bill API failure
    mock_client_instance.get_most_recent_6m_tbill.side_effect = Exception("T-bill API Error")
    
    test_bank = "Test Bank"
    
    with patch('sgfixedincome_pkg.scraper.scrape_deposit_rates') as mock_scrape:
        # Mock successful bank scraping
        mock_df = pd.DataFrame({
            'Tenure': [12, 24],
            'Rate': [3.0, 3.2],
            'Deposit lower bound': [1000, 1000],
            'Deposit upper bound': [50000, 50000],
            'Required multiples': [1000, 1000],
            'Product provider': [test_bank, test_bank],
            'Product': ['Fixed Deposit', 'Fixed Deposit']
        })
        mock_scrape.return_value = mock_df
        
        result_df, failures, warnings = consolidate.create_combined_df(
            scrape_inputs=[("http://test.com", "table-class", test_bank)],
            current_ssb_holdings=10000
        )
        
        # Verify DataFrame contains only bank data
        assert not result_df.empty, "Result DataFrame should contain bank data"
        assert all(result_df['Product provider'] == test_bank)
        assert all(result_df['Product'] == 'Fixed Deposit')
        assert len(result_df) == 2  # Two tenure periods from bank
        
        # Verify the exact content of the bank data
        pd.testing.assert_frame_equal(result_df, mock_df)
        
        # Verify we got exactly 2 failures (SSB and T-bill)
        assert len(failures) == 2, f"Expected 2 failures, got {len(failures)}"
        
        # Verify specific failures
        ssb_failure = next(f for f in failures if f['product'] == 'MAS SSB')
        assert ssb_failure['error'] == "SSB API Error"
        
        tbill_failure = next(f for f in failures if f['product'] == 'MAS T-bill')
        assert tbill_failure['error'] == "T-bill API Error"
        
        # Verify warnings list is empty (since API calls failed)
        assert len(warnings) == 0, "No warnings should be generated when API calls fail"

@patch('sgfixedincome_pkg.consolidate.MAS_bondsandbills_APIClient')
def test_create_combined_df_tbill_warning_only(mock_client):
    """Test scenario where all data is retrieved successfully but only T-bill warning is raised"""
    mock_client_instance = Mock()
    mock_client.return_value = mock_client_instance
    
    # Mock successful SSB API calls
    mock_client_instance.get_latest_ssb_issue_code.return_value = "GX24060A"
    mock_client_instance.get_ssb_coupons.return_value = [2.5, 3.0]
    mock_client_instance.calculate_ssb_tenure_rates.return_value = pd.DataFrame({
        'Tenure': [12, 24],
        'Rate': [2.5, 3.0]
    })
    
    # Mock successful T-bill API call but with warning
    mock_client_instance.get_most_recent_6m_tbill.return_value = {
        "issue_code": "BS24123F",
        "auction_tenor": 0.5,
        "cutoff_yield": 3.08
    }
    mock_client_instance.sudden_6m_tbill_yield_change_warning.side_effect = Warning("Sudden yield change detected")
    
    # No SSB warning
    mock_client_instance.past_last_day_to_apply_ssb_warning.return_value = None
    
    test_bank = "Test Bank"
    
    with patch('sgfixedincome_pkg.scraper.scrape_deposit_rates') as mock_scrape:
        # Mock successful bank scraping
        bank_df = pd.DataFrame({
            'Tenure': [12, 24],
            'Rate': [3.0, 3.2],
            'Deposit lower bound': [1000, 1000],
            'Deposit upper bound': [50000, 50000],
            'Required multiples': [1000, 1000],
            'Product provider': [test_bank, test_bank],
            'Product': ['Fixed Deposit', 'Fixed Deposit']
        })
        mock_scrape.return_value = bank_df
        
        result_df, failures, warnings = consolidate.create_combined_df(
            scrape_inputs=[("http://test.com", "table-class", test_bank)],
            current_ssb_holdings=10000,
            tbill_threshold=10
        )
        
        # Verify all data was retrieved successfully
        assert not result_df.empty, "Result DataFrame should contain data"
        
        # Verify we have data from all three sources
        providers = result_df['Product provider'].unique()
        assert len(providers) == 2, "Should have data from both bank and MAS"
        assert test_bank in providers, "Should have bank data"
        assert "MAS" in providers, "Should have MAS data"
        
        # Verify specific product types exist
        products = result_df['Product'].unique()
        assert any('Fixed Deposit' in p for p in products), "Should have bank fixed deposit"
        assert any('SSB' in p for p in products), "Should have SSB"
        assert any('T-bill' in p for p in products), "Should have T-bill"
        
        # Verify no failures occurred
        assert len(failures) == 0, "Expected no failures"
        
        # Verify only T-bill warning was raised
        assert len(warnings) == 1, "Expected exactly one warning"
        assert warnings[0] == "Sudden yield change detected"