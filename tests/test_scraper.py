from sgfixedincome_pkg import scraper
import pytest
from unittest.mock import Mock, patch
import requests
from bs4 import BeautifulSoup
import pandas as pd

def test_fetch_webpage_success(mocker):
    """
    Test that fetch_webpage successfully retrieves and parses HTML content.
    
    This test mocks the requests.get function to simulate a successful HTTP response
    and verifies that the function returns a BeautifulSoup object containing the expected content.
    """
    # Mock the requests.get to return a fake response
    mock_response = Mock() # creates a mock object to simulate a real HTTP object
    mock_response.status_code = 200 # simulate a successful HTTP request
    mock_response.text = "<html><body><h1>Test Content</h1></body></html>"
    mocker.patch('requests.get', return_value=mock_response)

    # Since requests.get is mocked, it returns the mock_response instead of making a real network request
    url = "http://example.com"
    soup = scraper.fetch_webpage(url)  # Call the function

    # Check if BeautifulSoup parsed the HTML content correctly
    assert isinstance(soup, BeautifulSoup)
    assert soup.h1.text == "Test Content"

def test_fetch_webpage_failure(mocker):
    """
    Test that fetch_webpage raises an exception when an HTTP request fails.
    
    This test mocks the requests.get function to raise a RequestException and
    verifies that fetch_webpage raises an Exception.
    """
    # Mock requests.get to raise an HTTPError
    mocker.patch('requests.get', side_effect=requests.exceptions.HTTPError("404 Not Found"))

    url = "http://example.com"
    with pytest.raises(Exception): # Check if any Exception is raised
        scraper.fetch_webpage(url)

# List of possible HTML structures and expected outputs with extract_table
@pytest.mark.parametrize(
    "html_content, table_class, expected_tables, raises_exception",
    [
        # Test case 1: Table exists and is found
        (
            """
            <html>
                <body>
                    <table class="rates-table">
                        <thead>
                            <tr>
                                <th><strong>Period</strong></th>
                                <th><strong>$1,000 - $9,999</strong></th>
                                <th><strong>$10,000 - $19,999</strong></th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>1 mth</td>
                                <td>0.3000</td>
                                <td>0.0500</td>
                            </tr>
                        </tbody>
                    </table>
                </body>
            </html>
            """,
            "rates-table",  # table_class
            1,  # One table should be found
            False  # No exception should be raised
        ),
        # Test case 2: Table class does not exist
        (
            """
            <html>
                <body>
                    <table class="other-table">
                        <tbody>
                            <tr>
                                <td><strong>Tenure (months)</strong></td>
                                <td><strong>Below S$50,000</strong></td>
                                <td><strong>S$50,000 - S$249,999</strong></td>
                            </tr>
                        </tbody>
                    </table>
                </body>
            </html>
            """,
            "rates-table",  # table_class (doesn't exist in the HTML)
            0,  # No tables should be found
            True  # An exception should be raised
        ),
        # Test case 3: Two tables with the same class (e.g. UOB website Dec 2024)
        (
            """
            <html>
                <body>
                    <table class="rates-table">
                        <tbody>
                            <tr>
                                <td><strong>Tenor</strong></td>
                                <td><strong>Deposit Amount</strong></td>
                                <td><strong>Promotional Rate (p.a.)</strong></td>
                            </tr>
                            <tr>
                                <td>6-month</td>
                                <td>S$10,000</td>
                                <td>2.50% p.a.</td>
                            </tr>
                        </tbody>
                    </table>
                    <table class="rates-table">
                        <tbody>
                            <tr>
                                <td><strong>Tenor (% p.a.)</strong></td>
                                <td><strong>Below S$50,000</strong></td>
                                <td><strong>S$50,000 - S$249,999</strong></td>
                            </tr>
                            <tr>
                                <td>1-month</td>
                                <td>0.05</td>
                                <td>0.06</td>
                            </tr>
                        </tbody>
                    </table>
                </body>
            </html>
            """,
            "rates-table",  # table_class
            2,  # Two tables should be found
            False  # No exception should be raised
        )
    ]
)
def test_extract_table(html_content, table_class, expected_tables, raises_exception):
    """
    Test extract_table() to ensure it handles finding tables with a given class correctly.

    Parameters:
        html_content (str): The HTML content input as a string.
        table_class (str): The class name of the table to locate in the HTML.
        expected_tables (int): The expected number of tables that should be found with the specified class.
        raises_exception (bool): Whether you expect an exception to be raised (True if exception expected, False if not).
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    if raises_exception:
        with pytest.raises(Exception):
            scraper.extract_table(soup, table_class)
    else:
        tables = scraper.extract_table(soup, table_class)
        assert len(tables) == expected_tables, f"Expected {expected_tables} tables, but got {len(tables)}"

# List of possible HTML structures and expected outputs with extract_table
@pytest.mark.parametrize(
    "html_content, table_class, expected_df, raises_exception",
    [
        # Test case 1: Table with headers in <th>
        (
            """
            <html>
                <body>
                    <table class="rates-table">
                        <thead>
                            <tr>
                                <th><strong>Period</strong></th>
                                <th><strong>$1,000 - $9,999</strong></th>
                                <th><strong>$10,000 - $19,999</strong></th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>1 mth</td>
                                <td>0.3000</td>
                                <td>0.0500</td>
                            </tr>
                            <tr>
                                <td>2 mths</td>
                                <td>0.0500</td>
                                <td>0.0500</td>
                            </tr>
                        </tbody>
                    </table>
                </body>
            </html>
            """,
            "rates-table", # table_class
            pd.DataFrame({
                "Period": ["1 mth", "2 mths"],
                "$1,000 - $9,999": ["0.3000", "0.0500"],
                "$10,000 - $19,999": ["0.0500", "0.0500"]
            }),
            False # No exception should be raised
        ),
        # Test case 2: Table with headers in the first row of <tbody>
        (
            """
            <html>
                <body>
                    <table class="rates-table">
                        <tbody>
                            <tr>
                                <td><strong>Tenor (% p.a.)</strong></td>
                                <td><strong>Below S$50,000</strong></td>
                                <td><strong>S$50,000 - S$249,999</strong></td>
                            </tr>
                            <tr>
                                <td>1-month</td>
                                <td>0.05</td>
                                <td>0.05</td>
                            </tr>
                            <tr>
                                <td>2-month</td>
                                <td>0.10</td>
                                <td>0.10</td>
                            </tr>
                        </tbody>
                    </table>
                </body>
            </html>
            """,
            "rates-table", # table_class
            pd.DataFrame({
                "Tenor (% p.a.)": ["1-month", "2-month"],
                "Below S$50,000": ["0.05", "0.10"],
                "S$50,000 - S$249,999": ["0.05", "0.10"]
            }),
            False # No exception should be raised
        )
    ]
)
def test_table_to_df(html_content, table_class, expected_df, raises_exception):
    """
    Parametrized test for extract_table, covering cases with:
    - Headers in <th> tags. Such a table is seen in the DBS website as of December 2024.
    - Headers in the first <tr> row of <tbody>. Such a table is seen in the UOB and OCBC websites as of December 2024.

    Note that we have to manually pass in html_content and table_class here since it is hard to directly 
    write out and pass in a BeautifulSoup table object.

    Parameters:
        html_content (str): HTML content input as a string.
        table_class (str): Input class name of table to locate in the HTML structure.
        expected_df (pd.DataFrame): The expected output raw pandas DataFrame with raw table data.
        raises_exception (boolean): Whether you expect an exception to be raised.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', class_=table_class)
    
    if raises_exception: 
        with pytest.raises(Exception):
            scraper.table_to_df(table)
    else:
        actual_df = scraper.table_to_df(table)
        pd.testing.assert_frame_equal(actual_df, expected_df)

# List of deposit range formats to input into parse_bounds and expected results 
@pytest.mark.parametrize(
    "deposit_range, expected_result, raises_exception",
    [
        # Valid deposit ranges
        ("$1,000 - $9,999", (1000.0, 9999.0), False),
        (">S$20,000 - S$50,000", (20000.01, 50000.0), False),
        ("Below S$50,000", (0.0, 49999.99), False),
        ("S$50,000 - S$249,999", (50000.0, 249999.0), False),
        (">$5,000", (5000.01, 99999999.0), False),
        ("Above 30,000", (30000.01, 99999999.0), False),
        
        # Invalid deposit ranges (should raise exceptions)
        ("$abc-xyz", None, True),  # Invalid format (non-numeric values)
        ("period", None, True),  # Invalid format (non-numeric values)
        ("<$10000-$20000", None, True),  # Invalid format (lower bound cannot start with '<')
        ("10000 - >20000", None, True),  # Invalid format (upper bound cannot start with '>')
        ("$50,000", None, True),  # Single value, not a range
        ("S$10000-S$5,000", None, True)  # Invalid range (upper bound is lower than lower bound)
    ]
)
def test_parse_bounds(deposit_range, expected_result, raises_exception):
    """
    Parametrized test for `parse_bounds` function.
    Tests various valid and invalid deposit range formats.

    Parameters:
        deposit_range (str): Deposit range string input value.
        expected_result (tuple): The expected output tuple with lower and upper bounds as floats.
        raises_exception (boolean): Whether you expect an exception to be raised.
    """
    if raises_exception: # Check that exception is raised for invalid deposit ranges
        with pytest.raises(ValueError):
            scraper.parse_bounds(deposit_range)
    else: # Check result is as expected for valid deposit ranges
        result = scraper.parse_bounds(deposit_range)
        assert result == expected_result

# List of header and first column values to input into parse_tenure and expected results
@pytest.mark.parametrize(
    "period_str, header_str, expected_result, raises_exception",
    [
        # Valid cases
        ("1 mth", "Period", [1], False), # In DBS website as of Dec 2024
        ("9 mths", "Period", [9], False), # In DBS website as of Dec 2024
        ("6-month", "Tenor (% p.a.)", [6], False), # In UOB website as of Dec 2024
        ("6-8", "Tenure (months)", [6, 7, 8], False), # In OCBC website as of Dec 2024
        ("12", "Tenure (months)", [12], False), # In OCBC website as of Dec 2024
        
        # Invalid cases (should raise ValueError)
        ("6-12 weeks", "Tenure in weeks", None, True),
        ("1 year", "Tenure", None, True),
        ("invalid tenure", "Period", None, True),
        ("6-8 years", "Tenure (years)", None, True)
    ]
)
def test_parse_tenure(period_str, header_str, expected_result, raises_exception):
    """
    Parametrized test for the `parse_tenure` function to validate its behavior with 
    both valid and invalid cases of tenure strings and headers.

    Parameters:
        period_str (str): Tenure period input value.
        header_str (str): Column header input value.
        expected_result (list): The expected output list of integer months.
        raises_exception (boolean): Whether you expect an exception to be raised.
    """
    if raises_exception: # Check that ValueError is raised for invalid cases
        with pytest.raises(ValueError):
            scraper.parse_tenure(period_str, header_str)
    else: # Check result is as expected for valid cases
        assert scraper.parse_tenure(period_str, header_str) == expected_result

# List of possible inputs into clean_rate_value and expected results
@pytest.mark.parametrize(
    "rate_value, expected_result, raises_exception",
    [
        # Valid cases
        ("1.40%", 1.4, False),     # Format seen in OCBC website
        ("2.9000", 2.9, False),    # Format seen in DBS website              
        ("0.90", 0.9, False),      # Format seen in UOB website
        
        # 'N.A' cases
        ("N.A", None, False),      # Format seen in OCBC website
        ("n.a.", None, False),
        ("N/a", None, False), 
        ("na", None, False),

        # Invalid cases (should raise ValueError)
        ("Invalid", None, True),   # Invalid string, should raise ValueError
        ("$500", None, True),      # String with '$', should raise ValueError
        ("", None, True),          # Empty string, should raise ValueError
    ]
)
def test_clean_rate_value(rate_value, expected_result, raises_exception):
    """
    Parametrized test for the `clean_rate_value` function to validate its behavior with 
    valid, invalid, and N.A. cases of rate values.

    Parameters:
        rate_value (str or float): The rate value input which may include non-numeric characters
                                   (e.g., '%', 'N.A.') or be a valid numeric value.
        expected_result (float or None): The expected output, a cleaned rate value or None.
        raises_exception (boolean): Whether you expect an exception to be raised. 
    """
    if raises_exception: # Check that ValueError is raised for invalid cases
        with pytest.raises(ValueError):
            scraper.clean_rate_value(rate_value)
    else: # Check result is as expected for valid cases
        assert scraper.clean_rate_value(rate_value) == expected_result

@pytest.mark.parametrize(
    "raw_df, expected_df",
    [
        (
            # Test Case 1: DBS website format
            pd.DataFrame({
                "Period": ["1 mth", "2 mths", "3 mths"],
                "$1,000 - $9,999": ["0.1000", "0.4000", "0.7000"],
                "$10,000 - $19,999": ["0.2000", "0.5000", "0.8000"],
                "$20,000 - $49,999": ["0.3000", "0.6000", "0.9000"]
            }),
            pd.DataFrame({
                "Tenure": [1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 3.0],
                "Rate": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
                "Deposit lower bound": [1000.0, 10000.0, 20000.0, 1000.0, 10000.0, 20000.0, 1000.0, 10000.0, 20000.0],
                "Deposit upper bound": [9999.0, 19999.0, 49999.0, 9999.0, 19999.0, 49999.0, 9999.0, 19999.0, 49999.0]
            })
        ),
        (
            # Test Case 2: UOB website format
            pd.DataFrame({
                "Tenor (% p.a.)": ["1-month", "2-month", "3-month"],
                "Below S$50,000": ["0.10", "0.30", "0.50"],
                "S$50,000 - S$249,999": ["0.20", "0.40", "0.60"]
            }),
            pd.DataFrame({
                "Tenure": [1.0, 1.0, 2.0, 2.0, 3.0, 3.0],
                "Rate": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
                "Deposit lower bound": [0.0, 50000.0, 0.0, 50000.0, 0.0, 50000.0],
                "Deposit upper bound": [49999.99, 249999.0, 49999.99, 249999.0, 49999.99, 249999.0]
            })
        ),
        (
            # Test Case 3: OCBC website format
            pd.DataFrame({
                "Tenor (months)": ["1-2", "3-4", "48 (new placements not available*)"],
                "S$5,000 - S$20,000": ["0.10", "0.30", "N.A"],
                ">S$20,000 - S$50,000": ["0.20", "0.40", "N.A"]
            }),
            pd.DataFrame({
                "Tenure": [1.0, 1.0, 2.0, 2.0, 3.0, 3.0, 4.0, 4.0],
                "Rate": [0.1, 0.2, 0.1, 0.2, 0.3, 0.4, 0.3, 0.4],
                "Deposit lower bound": [5000.0, 20000.0, 5000.0, 20000.0, 5000.0, 20000.0, 5000.0, 20000.0],
                "Deposit upper bound": [20000.01, 50000.0, 20000.01, 50000.0, 20000.01, 50000.0, 20000.01, 50000.0]
            })
        )
    ]
)
def test_reshape_table(raw_df, expected_df):
    """
    Tests the `reshape_table` function by verifying its ability to reshape
    raw deposit rate data from multiple input scenarios into a standardized format.

    Since reshape_table uses several other functions including parse_tenure, parse_bounds,
    and clean_rate_value, this is an integration test to see if these functions all work together.

    Parameters:
        raw_df (pd.DataFrame): Input DataFrame containing raw data.
        expected_df (pd.DataFrame): The expected reshaped DataFrame.
    """
    reshaped_df = scraper.reshape_table(raw_df)
    pd.testing.assert_frame_equal(
        reshaped_df.reset_index(drop=True),
        expected_df.reset_index(drop=True)
    )

def test_scrape_deposit_rates():
    """
    Integration test for scrape_deposit_rates.
    
    This test verifies that the function correctly orchestrates the scraping pipeline
    and returns the expected reshaped DataFrame with additional columns. The test uses 
    a predefined HTML structure to simulate a webpage and mock the fetch_webpage function. 
    extract_table and reshape_table are not mocked, allowing the test to validate their 
    integration.
    """
    # Define a mock URL (not actually used since fetch_webpage is mocked)
    mock_url = "http://example.com/deposit-rates"
    table_class = "rates-table"

    # Mock HTML structure of the webpage
    mock_html = """
    <html>
        <body>
            <table class="rates-table">
                <thead>
                    <tr>
                        <th>Period</th>
                        <th><strong>$1,000 - $9,999</strong></th>
                        <th><strong>$10,000 - $19,999</strong></th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>1 mth</td>
                        <td>0.1000</td>
                        <td>0.2000</td>
                    </tr>
                    <tr>
                        <td>2 mths</td>
                        <td>0.3000</td>
                        <td>0.4000</td>
                    </tr>
                </tbody>
            </table>
        </body>
    </html>
    """

    # Expected output DataFrame
    expected_df = pd.DataFrame({
        "Tenure": [1.0, 1.0, 2.0, 2.0],
        "Rate": [0.1, 0.2, 0.3, 0.4],
        "Deposit lower bound": [1000.0, 10000.0, 1000.0, 10000.0],
        "Deposit upper bound": [9999.0, 19999.0, 9999.0, 19999.0],
        "Required multiples": [None, None, None, None],
        "Product provider": ["test provider", "test provider", "test provider", "test provider"],
        "Product": ["Fixed Deposit", "Fixed Deposit", "Fixed Deposit", "Fixed Deposit"]
    })

    # Mock fetch_webpage to return the predefined HTML
    with patch("sgfixedincome_pkg.scraper.fetch_webpage", return_value=BeautifulSoup(mock_html, "html.parser")):
        # Call the scrape_deposit_rates function
        actual_df = scraper.scrape_deposit_rates(mock_url, table_class, "test provider")

        # Validate the result
        pd.testing.assert_frame_equal(
            actual_df.reset_index(drop=True),
            expected_df.reset_index(drop=True)
        )
