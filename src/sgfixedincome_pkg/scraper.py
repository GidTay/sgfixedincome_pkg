# Import necessary libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Fetch webpage content
def fetch_webpage(url):
    """
    Fetches webpage content from the given URL.
    
    Parameters:
        url (str): The URL of the website to scrape.

    Returns:
        BeautifulSoup: Parsed HTML content of the page.

    Raises:
        Exception: If the webpage cannot be fetched or parsed.
    """
    try:
        response = requests.get(url) # Fetch the webpage
        response.raise_for_status() # Check for request errors
        return BeautifulSoup(response.text, "html.parser") # Parse the webpage content
    except Exception as e:
        raise Exception(f"Failed to fetch or parse the webpage: {e}")

# Extract tables from soup
def extract_table(soup, table_class):
    """
    Locates tables with the specified class in the parsed HTML.

    Parameters:
        soup (BeautifulSoup): Parsed HTML content.
        table_class (str): Class name of the table(s) to locate.

    Returns:
        list: A list of located <table> elements.

    Raises:
        Exception: If no tables with the specified class are found.
    """
    tables = soup.find_all('table', class_=table_class)
    if not tables:
        raise Exception("No tables found with the specified class.")
    return tables

# Extract table data
def table_to_df(table):
    """
    Converts an HTML <table> element into a pandas DataFrame.

    This function takes in a BeautifulSoup Tag object representing a table and extracts the rows and columns of data.
    It can handle both traditional tables where headers are inside <th> tags, as well as tables where the header row is 
    indistinguishable from the other rows. In such cases, the header row would simply be the first row in <tbody>, and contents
    would be found within <td> tags in the first <tr> row. Each row’s data is stored as a list of cell values, which are then 
    used to construct a pandas DataFrame.

    Parameters:
        table (Tag): A BeautifulSoup Tag object representing the <table>.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the extracted table data.

    Raises:
        Exception: If the table data extraction fails. For example, when there is an issue during the row data extraction process, 
                   such as missing <tbody>, <tr>, <td> tags or malformed rows.
    """
    # Extract table header cell contents found in <th> tags
    headers_data = [header.text.strip() for header in table.find_all('th')]
    
    # Extract rows and store it in a list of lists (one list per row)
    rows_data = []
    try:
        rows = table.find('tbody').find_all('tr') # Rows are in <tr> tags
        for row in rows:
            # Each cell's contents is in <td> tags
            rows_data.append([cell.text.strip() for cell in row.find_all('td')])
    except Exception as e:
        raise Exception(f"Failed to extract data from table: {e}")
    
    # If headers are not defined, assume the first row is the header
    if not headers_data: 
        # .pop(0) removes and returns first item on rows_data list
        headers_data = rows_data.pop(0) if rows_data else []

    return pd.DataFrame(rows_data, columns=headers_data)

# Parse lower and upper bounds for deposits
def parse_bounds(deposit_range):
    """
    Parses deposit range to extract lower and upper bounds, ensuring inclusive bounds.

    Parameters:
        deposit_range (str): String representing the deposit range 

    Returns:
        tuple: A tuple containing the lower and upper bounds as floats. If only upper bound exists, 
        lower bound is set to 0. If only the lower bound exists, upper bound is set to 99,999,999.

    Raises:
        ValueError: If the range cannot be parsed, if the lower bound is greater than the upper bound,
                    or if the range is nonsensical (e.g., "<10000 - 20000" or '10000 - >20000').
    
    Examples:
        - "$1,000 - $9,999" -> (1000.0, 9999.0)
        - ">S$20,000 - S$50,000" -> (20000.01, 50000.0)
        - "Below S$50,000" -> (0.0, 49999.99)
        - "S$50,000 - S$249,999" -> (50000.0, 249999.0)
        - ">$5,000" -> (5000.01, 99999999.0)
        - "Above 30,000" -> (30000.01, 99999999.0)
    """
    # Clean the string: remove unwanted characters (e.g., "$", "S$", commas, spaces, letters)
    cleaned_range = re.sub(r'[A-Za-z$\s,]', '', deposit_range)

    # Handle ranges (e.g., "10000-20000", ">20000-50000")
    if '-' in cleaned_range:
        bounds = cleaned_range.split('-') # Extract lower and upper bounds
        try:
            # Process lower bound
            if bounds[0].startswith('>'):
                lower = float(bounds[0][1:]) + 0.01  # Inclusive adjustment for '>', ignore first character
            elif bounds[0].startswith('<'):
                raise ValueError(f"Invalid range: Lower bound cannot start with '<'")
            else:
                lower = float(bounds[0])

            # Process upper bound
            if bounds[1].startswith('<'):
                upper = float(bounds[1][1:]) - 0.01  # Inclusive adjustment for '<', ignore first character
            elif bounds[1].startswith('>'):
                raise ValueError(f"Invalid range: Upper bound cannot start with '>'")
            else:
                upper = float(bounds[1])

            if lower > upper:
                raise ValueError(f"Invalid range: Lower bound {lower} is greater than upper bound {upper}")
            
            return lower, upper
        except ValueError:
            raise ValueError(f"Invalid range format: {deposit_range}")

    # Handle "Below X" or "<X" (only upper bound is defined)
    if 'below' in deposit_range.lower() or cleaned_range.startswith('<'):
        try:
            upper = float(re.sub(r'[><]', '', cleaned_range)) - 0.01
            return 0.0, upper
        except ValueError:
            raise ValueError(f"Invalid 'below' format: {deposit_range}")

    # Handle "Above X" or ">X" (only lower bound is defined)
    if 'above' in deposit_range.lower() or cleaned_range.startswith('>'):
        try:
            lower = float(re.sub(r'[><]', '', cleaned_range)) + 0.01
            return lower, 99999999.0
        except ValueError:
            raise ValueError(f"Invalid 'above' format: {deposit_range}")
    
    # If no conditions are met, raise an error
    raise ValueError(f"Could not parse deposit range: {deposit_range}")

# Parse tenures
def parse_tenure(period_str, header_str):
    """
    Ensure the tenure period is in months and parse it.

    This function extracts the tenure information from `period_str`. The tenure is 
    expected to be in months and indicated by keywords such as "month" or "mth" in 
    either `period_str` or the `header_str`.

    Parameters:
        period_str (str): Tenure period as a string (e.g., "6-12 months").
        header_str (str): Column header to verify if data represents months.

    Returns:
        list: List of integer months if the tenure is valid.

    Raises:
        ValueError: If the tenure cannot be parsed or is not in months.
    
    Examples:
        >>> parse_tenure("9 mths", header_str="Period")
        [9]

        >>> parse_tenure("6-month", header_str="Tenor (% p.a.)")
        [6]

        >>> parse_tenure("6-8", header_str="Tenure (months)")
        [6, 7, 8]

        >>> parse_tenure("12", header_str="Tenure (months)")
        [12]

        >>> parse_tenure("6-12 weeks", header_str="Tenure in weeks")
        ValueError: Neither header 'Tenure in weeks' nor content '6-12 weeks' indicates months.
    """
    # Check if the column header or cell content indicates months
    keywords = ['month', 'mth']
    header_valid = any(keyword in header_str.lower() for keyword in keywords)
    content_valid = any(keyword in period_str.lower() for keyword in keywords)
    if not (header_valid or content_valid):
        raise ValueError(f"Neither header '{header_str}' nor content '{period_str}' indicates months.")
    
    # Match range (e.g., "6 - 8", "6-12 months")
    range_match = re.match(r"(\d+)\s*-\s*(\d+)", period_str)
    if range_match:
        start, end = map(int, range_match.groups())
        return list(range(start, end + 1))
    
    # Match single value (e.g., "12-months", "12 mths")
    single_match = re.match(r"(\d+)", period_str)
    if single_match:
        return [int(single_match.group(1))]
    
    # If parsing fails, raise an error
    raise ValueError(f"Unable to parse tenure: '{period_str}'")

def clean_rate_value(rate_value):
    """
    Cleans the rate value by removing any non-numeric characters and converting to a float.
    
    If the rate value is a string representing 'N.A', 'N.A.', or similar (case-insensitive),
    it returns None.

    Parameters:
        rate_value (str or float): The rate value which may include non-numeric characters
                                   (e.g., '%', 'N.A.') or be a valid numeric value.

    Returns:
        float or None: The cleaned rate value as a float, or None if the value represents 'N.A'.
    
    Raises:
        ValueError: If the rate value cannot be converted to a float and isn't a valid 'N.A.' string.
    
    Examples:
        - clean_rate_value("5%") -> 5.0
        - clean_rate_value("N.A.") -> None
        - clean_rate_value("3.5") -> 3.5
    """
    if isinstance(rate_value, str):
        rate_value = rate_value.strip().replace('%', '') # Remove '%' sign if present
        
        # Check if the value represents 'N.A' or similar (case-insensitive)
        if rate_value.lower() in ['n.a', 'n.a.', 'n/a', 'na']:
            return None
    
    try:
        return float(rate_value)
    except ValueError:
        raise ValueError(f"Invalid rate value: {rate_value}")

# Reshape DataFrame
def reshape_table(raw_df):
    """
    Reshapes the raw DataFrame into a structured format for analysis.

    Parameters:
        raw_df (pd.DataFrame): The raw DataFrame containing fixed deposit rate data.
            The first column contains tenure in months (e.g., 'Period', 'Tenor', or 'Tenure').
            The other columns contain rates for different deposit ranges (e.g., '$1,000-$9,999').

    Returns:
        pd.DataFrame: A reshaped DataFrame with the following columns:

            - Tenure: The duration in months (as float).
            - Rate: The deposit rates (as float).
            - Deposit lower bound: The lower bound of the deposit range (as float).
            - Deposit upper bound: The upper bound of the deposit range (as float, or None if not specified).
    
    Raises:
        ValueError: If the first column does not contain keywords indicating tenure information.
    """
    # Validate that the first column contains tenure-related data
    first_col = raw_df.columns[0]
    if not any(keyword in first_col.lower() for keyword in ['period', 'tenor', 'tenure']):
        raise ValueError("The first column does not contain 'Period', 'Tenor', or 'Tenure'.")
    
    data = [] # Initialize an empty list to hold the reshaped data
    for _, row in raw_df.iterrows(): # Iterate over each row, don't need row index so '_'
        # Get a list of tenures from first column in each row (e.g., "6-month")
        tenures = parse_tenure(row[first_col], first_col) 

        # Iterate over each tenure in the list
        for tenure in tenures:
            for col in raw_df.columns[1:]: # Iterate over each column in the row
                lower, upper = parse_bounds(col) # Assume all column headers except the first contain deposit ranges
                rate_value = clean_rate_value(row[col])
                data.append({
                    'Tenure': float(tenure),
                    'Rate': rate_value,
                    'Deposit lower bound': lower,
                    'Deposit upper bound': upper,
                })
    
    # Convert to a DataFrame and remove rows where 'Rate' is None
    df = pd.DataFrame(data)
    df = df.dropna(subset=['Rate'])

    return df

# Main function to orchestrate the scraping
def scrape_deposit_rates(url, table_class, provider, req_multiples=None):
    """
    Scrapes deposit rates from the given URL and manually add extra information.

    Sometimes, bank websites use the same class for multiple tables, including the key table of interest with 
    fixed deposit rates. To enable our scraper to work in such cases, we attempt to scrape data for each of these
    tables, starting with the first. We ignore additional tables once we find one that can be successfully scraped.
    The intuition is that we would only be able to successfully scrape tables with our desired data, and attempted scraping
    of tables containing other information would fail.

    Parameters:
        url (str): URL of the website to scrape. The website should contain a table of fixed deposit rates.
        table_class (str): Class name of the table to locate in the website.
        provider (str): The name of the provider offering the fixed deposit products.
        req_multiples (optional, float or None): The required multiples for the deposit, if applicable. Defaults to None.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the reshaped deposit rates data, with additional columns:

            - Required multiples: The value provided in `req_multiples`.
            - Product provider: The value provided in `provider`.
            - Product: A static string "Fixed Deposit" indicating the type of product.
    
    Raises:
        Exception: If the scraping or data extraction process fails, an exception will be raised.
    """
    try:
        soup = fetch_webpage(url)
        tables = extract_table(soup, table_class)

        for table in tables: # Try to process each table
            try:
                raw_df = table_to_df(table)
                reshaped_df = reshape_table(raw_df)

                # Add additional columns
                reshaped_df["Required multiples"] = req_multiples
                reshaped_df["Product provider"] = provider
                reshaped_df["Product"] = "Fixed Deposit"

                return reshaped_df
            except Exception:
                continue # Move silently to the next table, as we just need 1 table to work

        # Raise an exception if all tables fail to process
        raise Exception(f"Failed to process any tables for {provider} from {url}.")

    except Exception as e:
        raise Exception(f"Failed to scrape deposit rates for {provider}: {e}")