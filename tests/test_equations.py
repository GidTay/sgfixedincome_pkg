from sgfixedincome_pkg import equations
import pytest

# Test valid cases for calculate_dollar_return
@pytest.mark.parametrize(
    "investment, rate, tenure, expected",
    [
        (5000, 1.5, 6, 37.36),  # Regular case
        (8000, 0, 12, 0.0),     # Zero rate of return
        (0, 3.1, 10, 0.0)       # Zero investment
    ]
)
def test_calculate_dollar_return_valid(investment, rate, tenure, expected):
    """
    Test calculate_dollar_return with valid inputs to verify correct results.
    """
    actual = equations.calculate_dollar_return(investment, rate, tenure)
    # This should be fine despite float imprecision in python as our function rounds off to 2 d.p.
    assert actual == expected

# Test invalid cases for calculate_dollar_return
def test_calculate_dollar_return_invalid():
    """
    Test calculate_dollar_return with invalid inputs to ensure it raises ValueError.
    """
    with pytest.raises(ValueError):
        equations.calculate_dollar_return(-1000, 1.2, 12)  # Negative investment
    with pytest.raises(ValueError):
        equations.calculate_dollar_return(1000, -1.2, 12)  # Negative rate
    with pytest.raises(ValueError):
        equations.calculate_dollar_return(1000, 1.2, -12)  # Negative tenure
    with pytest.raises(ValueError):
        equations.calculate_dollar_return(1000, 1.2, 0)    # Zero tenure

# Test valid cases for calculate_per_annum_rate
@pytest.mark.parametrize(
    "total_percentage_return, tenure, expected",
    [
        (3.1, 16, 2.32),  # Regular case
        (0, 2, 0.0)       # Zero total_percentage_return
    ]
)
def test_calculate_per_annum_rate_valid(total_percentage_return, tenure, expected):
    """
    Test calculate_per_annum_rate with valid inputs to verify correct results.
    """
    actual = equations.calculate_per_annum_rate(total_percentage_return, tenure)
    # This should be fine despite float imprecision in python as our function rounds off to 2 d.p.
    assert actual == expected

# Test invalid cases for calculate_per_annum_rate
def test_calculate_per_annum_rate_invalid():
    """
    Test calculate_per_annum_rate with invalid inputs to ensure it raises ValueError.
    """
    with pytest.raises(ValueError):
        equations.calculate_per_annum_rate(3.1, 0)    # Tenure is zero.
    with pytest.raises(ValueError):
        equations.calculate_per_annum_rate(1.3, -12)  # Tenure is negative.
