import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, Mock
from sgfixedincome_pkg import analysis, equations

# Fixture for common test data
@pytest.fixture
def sample_df():
    return pd.DataFrame({
        'Tenure': [1, 1, 6, 6, 12, 12, 6, 12, 24],
        'Rate': [0.3, 0.05, 2.9, 0.3, 3.2, 1.5, 2.74, 2.73, 2.77],
        'Deposit lower bound': [1000, 20000, 1000, 1000, 1000, 1000, 500, 500, 500],
        'Deposit upper bound': [9999, 49999, 9999, 49999, 9999, 49999, 200000, 200000, 200000],
        'Required multiples': [None, None, None, None, None, None, 500, 500, 500],
        'Product provider': ['DBS', 'DBS', 'DBS', 'UOB', 'DBS', 'UOB', 'MAS', 'MAS', 'MAS'],
        'Product': ['Fixed Deposit', 'Fixed Deposit', 'Fixed Deposit', 'Fixed Deposit', 
                   'Fixed Deposit', 'Fixed Deposit', 'T-bill BS24124Z', 'SSB GX25010E', 'SSB GX25010E']
    })

# Tests for filter_df function
def test_filter_df_investment_amount(sample_df):
    """Test filtering by investment amount"""
    result = analysis.filter_df(sample_df, investment_amount=5000)
    assert len(result) == 8  # All products accept 5000
    assert all(result['Deposit lower bound'] <= 5000)
    assert all(result['Deposit upper bound'] >= 5000)
    
    with pytest.raises(ValueError):
        result = analysis.filter_df(sample_df, investment_amount=400)  # Too low for any product

def test_filter_df_tenure_range(sample_df):
    """Test filtering by tenure range"""
    # Test min tenure
    result = analysis.filter_df(sample_df, min_tenure=6)
    assert len(result) == 7
    assert all(result['Tenure'] >= 6)
    
    # Test max tenure
    result = analysis.filter_df(sample_df, max_tenure=12)
    assert len(result) == 8
    assert all(result['Tenure'] <= 12)
    
    # Test both min and max tenure
    result = analysis.filter_df(sample_df, min_tenure=6, max_tenure=12)
    assert len(result) == 6
    assert all((result['Tenure'] >= 6) & (result['Tenure'] <= 12))

def test_filter_df_min_rate(sample_df):
    """Test filtering by minimum rate"""
    result = analysis.filter_df(sample_df, min_rate=2.0)
    assert all(result['Rate'] >= 2.0)
    
    # Test no products meet rate criteria
    with pytest.raises(ValueError, match="No products found matching the provided criteria"):
        analysis.filter_df(sample_df, min_rate=5.0)

def test_filter_df_product_types(sample_df):
    """Test filtering by product types"""
    # Test excluding T-bills
    result = analysis.filter_df(sample_df, consider_tbills=False)
    assert not any('T-bill' in product for product in result['Product'])
    
    # Test excluding SSBs
    result = analysis.filter_df(sample_df, consider_ssbs=False)
    assert not any('SSB' in product for product in result['Product'])
    
    # Test excluding Fixed Deposits
    result = analysis.filter_df(sample_df, consider_fd=False)
    assert not any('Fixed Deposit' in product for product in result['Product'])
    
    # Test excluding all product types
    with pytest.raises(ValueError):
        analysis.filter_df(sample_df, consider_tbills=False, consider_ssbs=False, consider_fd=False)

def test_filter_df_providers(sample_df):
    """Test filtering by providers"""
    # Test including specific providers
    result = analysis.filter_df(sample_df, include_providers=['DBS'])
    assert all(result['Product provider'] == 'DBS')
    
    # Test excluding specific providers
    result = analysis.filter_df(sample_df, exclude_providers=['UOB'])
    assert not any(result['Product provider'] == 'UOB')
    
    # Test excluding all providers
    with pytest.raises(ValueError, match="No products found matching the provided criteria"):
        analysis.filter_df(sample_df, exclude_providers=['DBS', 'UOB', 'MAS'])

# Tests for best_returns function
def test_best_returns_basic(sample_df):
    """Test basic functionality of best_returns"""
    result = analysis.best_returns(sample_df, investment_amount=10000)
    # Check structure
    assert not result.empty
    assert 'Total Dollar Return' in result.columns
    assert 'Invested amount' in result.columns
    # Check logic
    assert all(result['Total Dollar Return'] >= 0)
    assert all(result['Invested amount'] <= 10000)

def test_best_returns_multiple_constraints(sample_df):
    """Test that required multiples are properly handled"""
    investment_amount = 9800
    result = analysis.best_returns(sample_df, investment_amount=investment_amount)
    
    # Check that invested amounts respect required multiples
    for _, row in result.iterrows():
        if pd.notna(row['Required multiples']):
            assert row['Invested amount'] % row['Required multiples'] == 0
            assert row['Invested amount'] <= investment_amount

def test_best_returns_invalid_amount(sample_df):
    """Test that appropriate error is raised for invalid investment amounts"""
    with pytest.raises(ValueError):
        analysis.best_returns(sample_df, investment_amount=100)  # Too low for any product

# Tests for best_rates function
def test_best_rates_basic(sample_df):
    """Test basic functionality of best_rates"""
    investment_amount=10000
    result = analysis.best_rates(sample_df, investment_amount)
    assert not result.empty
    
    # Check that we get the highest rate for each tenure
    for tenure in result['Tenure'].unique():
        tenure_data = sample_df[
            (sample_df['Tenure'] == tenure) & 
            (sample_df['Deposit lower bound'] <= investment_amount) & 
            (sample_df['Deposit upper bound'] >= investment_amount)
        ]
        max_rate = tenure_data['Rate'].max()
        result_rate = result[result['Tenure'] == tenure]['Rate'].iloc[0]
        assert result_rate == max_rate

def test_best_rates_tenure_filter(sample_df):
    """Test tenure filtering in best_rates"""
    result = analysis.best_rates(
        sample_df, 
        investment_amount=10000, 
        min_tenure=6, 
        max_tenure=12
    )
    assert all(result['Tenure'] >= 6)
    assert all(result['Tenure'] <= 12)

# Tests for products function
def test_products(sample_df):
    """Test products function"""
    result = analysis.products(sample_df)
    
    # Check basic structure
    assert isinstance(result, list)
    assert len(result) == len(pd.unique(sample_df['Product provider'] + ' - ' + sample_df['Product']))
    
    # Check expected products are present
    expected_products = [
        'DBS - Fixed Deposit',
        'UOB - Fixed Deposit',
        'MAS - T-bill BS24124Z',
        'MAS - SSB GX25010E'
    ]
    for product in expected_products:
        assert product in result

# Tests for plotting functions
@patch('matplotlib.pyplot.show')
@patch('seaborn.lineplot')
def test_plot_rates_vs_tenure(mock_lineplot, mock_show, sample_df):
    """Test that plot_rates_vs_tenure runs with correct arguments"""
    
    # Use context manager to suppress expected UserWarning about legend
    with pytest.warns(UserWarning, match="No artists with labels found to put in legend"):
        analysis.plot_rates_vs_tenure(sample_df, investment_amount=10000)

    # Check essential plot arguments
    args, kwargs = mock_lineplot.call_args
    assert kwargs['x'] == 'Tenure'
    assert kwargs['y'] == 'Rate'
    assert kwargs['hue'] == 'Product Combination'
    assert kwargs['marker'] == 'o'
    
    # Verify show was called
    mock_show.assert_called_once()

@patch('matplotlib.pyplot.show')
@patch('matplotlib.pyplot.plot')
@patch('seaborn.scatterplot')
def test_plot_best_rates(mock_scatterplot, mock_plot, mock_show, sample_df):
    """Test that plot_best_rates runs with correct arguments"""
    
    # Use context manager to suppress expected UserWarning about legend
    with pytest.warns(UserWarning, match="No artists with labels found to put in legend"):
        analysis.plot_best_rates(sample_df, investment_amount=10000)
    
    # Check essential scatter plot arguments
    scatter_args, scatter_kwargs = mock_scatterplot.call_args
    assert scatter_kwargs['x'] == 'Tenure'
    assert scatter_kwargs['y'] == 'Rate'
    assert scatter_kwargs['hue'] == 'Provider-Product'
    
    # Verify continuous line plot was called
    mock_plot.assert_called_once()
    
    # Verify show was called
    mock_show.assert_called_once()

@patch('matplotlib.pyplot.show')
@patch('seaborn.lineplot')
def test_plot_bank_offerings_with_fuzz(mock_lineplot, mock_show, sample_df):
    """Test that plot_bank_offerings_with_fuzz runs with correct arguments"""
    
    # Use context manager to suppress expected UserWarning about legend
    with pytest.warns(UserWarning, match="No artists with labels found to put in legend"):
        analysis.plot_bank_offerings_with_fuzz(sample_df, product_provider='DBS')
    
    # Check essential plot arguments
    args, kwargs = mock_lineplot.call_args
    assert kwargs['x'] == 'Tenure_fuzzed'
    assert kwargs['y'] == 'Rate_fuzzed'
    assert kwargs['hue'] == 'Deposit_Range'
    assert kwargs['style'] == 'Deposit_Range'
    
    # Verify show was called
    mock_show.assert_called_once()

def test_plot_bank_offerings_invalid_provider(sample_df):
    """Test that appropriate error is raised for invalid provider"""
    with pytest.raises(ValueError):
        analysis.plot_bank_offerings_with_fuzz(sample_df, product_provider='INVALID_BANK')