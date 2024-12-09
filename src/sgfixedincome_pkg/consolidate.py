from sgfixedincome_pkg import scraper
from sgfixedincome_pkg.mas_api_client import MAS_bondsandbills_APIClient
import pandas as pd

# Used to merge dataframes from scraping bank websites and constructed from MAS APIs
def merge_dataframes(df_list):
    """
    Merges a list of DataFrames by appending rows, with validation of input.

    Parameters:
        df_list (list of pd.DataFrame): A list of pandas DataFrames to be merged. Each DataFrame must either
                                        be empty, or contain exactly the following columns: 
                                        'Tenure', 'Rate', 'Deposit lower bound', 'Deposit upper bound',
                                        'Required multiples', 'Product provider', 'Product'.

    Returns:
        pd.DataFrame: A single DataFrame with all rows from the input DataFrames. Returns an empty DataFrame
        with the required columns if all input DataFrames are empty.

    Raises:
        TypeError: If the input is not a list or does not contain pandas DataFrames.
        ValueError: If any DataFrame in the list does not have exactly the required columns.
    """
    # Check that the input is a list
    if not isinstance(df_list, list):
        raise TypeError(f"Expected a list, but got {type(df_list).__name__}.")

    # Define the required columns
    required_columns = [
        'Tenure', 'Rate', 'Deposit lower bound', 'Deposit upper bound', 
        'Required multiples', 'Product provider', 'Product'
    ]

    # Filter out empty DataFrames
    validated_dfs = []
    for idx, df in enumerate(df_list):
        # Ensure each entry is a pandas DataFrame
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Item at index {idx} is not a DataFrame. Got {type(df).__name__}.")
        
        # Skip empty DataFrames
        if df.empty:
            continue

        # Check for exact columns in non-empty DataFrames
        if list(df.columns) != required_columns:
            raise ValueError(
                f"DataFrame at index {idx} must have columns exactly as: {required_columns}. "
                f"Found columns: {list(df.columns)}"
            )
        
        validated_dfs.append(df)

    # Return an empty DataFrame if all input DataFrames are empty
    if not validated_dfs:
        return pd.DataFrame(columns=required_columns)

    # Merge the DataFrames
    combined_df = pd.concat(validated_dfs, ignore_index=True)
    return combined_df

# Used to scrape multiple bank websites and produce a dataframe
def create_banks_df(scrape_inputs):
    """
    Scrapes deposit rates from multiple bank websites and combines them into a single DataFrame.

    Even if scraping fails for some websites, a DataFrame containing data from successfully scraped sites
    is still returned. The function also provides a list of dictionaries with information on websites
    it failed to scrape from. The function also validates the input before running its main task. If we fail
    to scrape from all websites, the function returns an empty dataframe.

    Parameters:
        scrape_inputs (list of tuples): Each tuple contains:

            - URL (str): The webpage to scrape.
            - Table class (str): The class of the table to locate.
            - Provider (str): The name of the bank/provider.
            - Required multiples (float or None, optional): Value to populate the "Required multiples" column. Defaults to None if omitted.

    Returns:
        tuple: A tuple containing:

            - pd.DataFrame: Combined DataFrame with all successfully scraped deposit rates.

            - list of dict: Each dict contains details of failed scrapes with:

                - product (str): Name of the provider and product that failed (e.g. DBS bank fixed deposit)
                - error (str): Error message describing the failure.

    Raises:
        ValueError: If the input is not a list of tuples with the expected structure.
    """
    # Input validation
    if not isinstance(scrape_inputs, list):
        raise ValueError("scrape_inputs must be a list.")
    
    for entry in scrape_inputs:
        if not isinstance(entry, tuple):
            raise ValueError(f"Each entry in scrape_inputs must be a tuple, found {type(entry).__name__}.")
        if not isinstance(entry[0], str) or not isinstance(entry[1], str) or not isinstance(entry[2], str):
            raise ValueError("The first three elements of each tuple must be strings (URL, table class, provider).")
        if len(entry) == 4 and not (isinstance(entry[3], (float, int)) or entry[3] is None):
            raise ValueError("The fourth element (if present) must be a float, int, or None.")

    combined_df = pd.DataFrame()  # Initialize an empty DataFrame
    failed_providers = []  # List to track failed scrapes

    for scrape_input in scrape_inputs:
        # Unpack with a default value for req_multiples
        if len(scrape_input) == 3:
            url, table_class, provider = scrape_input
            req_multiples = None  # Default value
        elif len(scrape_input) == 4:
            url, table_class, provider, req_multiples = scrape_input
        else:
            raise ValueError(f"Each input tuple must have 3 or 4 elements. Found {len(scrape_input)} elements.")

        try:
            # Scrape data for each input
            df = scraper.scrape_deposit_rates(url, table_class, provider, req_multiples=req_multiples)
            combined_df = pd.concat([combined_df, df], ignore_index=True)
        except Exception as e:
            error_details = {'product': provider + ' bank fixed deposit', 'error': str(e)}
            failed_providers.append(error_details)

    return combined_df, failed_providers

def add_ssb_details(df, current_ssb_holdings, issue_code):
    """
    Add additional details to the DataFrame with SSB tenure and rate data.

    Parameters:
        df (pd.DataFrame): DataFrame with SSB tenure month and rates.
        current_ssb_holdings (float): Current SSB holdings in Singapore dollars.
        issue_code (str): The SSB's issue code.

    Returns:
        pd.DataFrame: Updated DataFrame with additional SSB information.
    """
    deposit_upper = max(200000 - current_ssb_holdings, 0)
    deposit_lower = 500 if deposit_upper >= 500 else 0

    df["Deposit lower bound"] = deposit_lower
    df["Deposit upper bound"] = deposit_upper
    df["Required multiples"] = 500
    df["Product provider"] = "MAS"
    df["Product"] = f"SSB {issue_code}"

    return df

def create_ssb_df(client, current_ssb_holdings=0.0):
    """
    Create a dataframe containing the details and rates for the latest Singapore Savings Bond (SSB).

    Parameters:
        client: An initialized instance of the MAS_bondsandbills_APIClient.
        current_ssb_holdings (float, optional): The amount of SSBs you currently hold in Singapore dollars. Defaults to 0.0.

    Returns:
        pandas.DataFrame: A dataframe with SSB tenure rates and additional details.
    """
    # Fetch the issue code of the latest SSB
    issue_code = client.get_latest_ssb_issue_code()

    # Fetch the coupon rates for the latest SSB issue
    coupons = client.get_ssb_coupons(issue_code)

    # Calculate the tenure rates for the SSB based on the coupon rates
    df = client.calculate_ssb_tenure_rates(coupons)

    # Add additional details to the dataframe
    df = add_ssb_details(df, current_ssb_holdings, issue_code)

    return df

def create_tbill_df(tbill_details):
    """
    Create a pandas DataFrame with details about a T-bill.

    Parameters:
        tbill_details (dict): A dictionary containing details about a T-bill. Expected keys include: 
        
            - cutoff_yield (float): in percentage.
            - issue_code (str): identifies the T-bill.
            - auction_tenor (float): specifies if it is a 6-month (0.5) or 12-month (1.0) T-bill.

    Returns:
        pd.DataFrame: A DataFrame with the following columns:

            - Tenure (int): The tenure of the T-bill in months.
            - Rate (float): The cutoff yield of the T-bill.
            - Deposit lower bound (int): The minimum investment amount (fixed at 1000).
            - Deposit upper bound (int): The maximum investment amount (fixed at 99999999).
            - Required multiples (int): The required investment increments (fixed at 1000).
            - Product provider (str): The provider of the product (fixed as "MAS").
            - Product (str): A description of the T-bill, including its issue code.

    Example:
        >>> tbill_details = {"cutoff_yield": 3.08, "issue_code": "BS24123F", "auction_tenor": 0.5}
        >>> df = create_tbill_df(tbill_details)
        >>> df
           Tenure  Rate  Deposit lower bound  Deposit upper bound  Required multiples Product provider          Product
        0       6  3.08                 1000             99999999                1000              MAS  T-bill BS24123F
    """
    # Convert auction_tenor to tenure in months
    tenure_mapping = {
        0.5: 6,
        1.0: 12
    }
    tenure = tenure_mapping.get(tbill_details["auction_tenor"])
    if tenure is None:
        raise ValueError(f"Unknown T-bill tenure: {tbill_details['auction_tenor']}")
    
    data = {
        "Tenure": tenure,
        "Rate": [tbill_details["cutoff_yield"]],
        "Deposit lower bound": 1000,
        "Deposit upper bound": 99999999,
        "Required multiples": 1000,
        "Product provider": "MAS",
        "Product": f'T-bill {tbill_details["issue_code"]}'
    }
    return pd.DataFrame(data)

# Final key function that produces main dataframe output with all data
def create_combined_df(
    scrape_inputs=[
        (
            "https://www.dbs.com.sg/personal/rates-online/fixed-deposit-rate-singapore-dollar.page",
            "tbl-primary mBot-24",
            "DBS"
        ),
        (
            "https://www.uob.com.sg/personal/online-rates/singapore-dollar-time-fixed-deposit-rates.page",
            "table__carousel-table",
            "UOB"
        ),
        (
            "https://www.ocbc.com/personal-banking/deposits/fixed-deposit-sgd-interest-rates.page",
            "table__comparison-table",
            "OCBC"
        )
    ],
    current_ssb_holdings=0.0,
    tbill_threshold=10
):
    """
    Creates a combined DataFrame by aggregating data from banks, MAS Singapore Savings Bonds (SSBs),
    and Treasury Bills (T-bills), and providing information on cases where data fetching failed.

    Parameters:
        scrape_inputs (list of tuples, optional): Input parameters for scraping bank data. Each tuple contains:

            - URL (str): The webpage to scrape.
            - Table class (str): The class of the table to locate.
            - Provider (str): The name of the bank/provider.
            - Required multiples (float or None, optional): Value to populate the "Required multiples" column. Defaults to None if omitted.
            Default value includes DBS, UOB, and OCBC bank details.
        
        current_ssb_holdings (float, optional): The amount of SSBs you currently hold in Singapore dollars. Defaults to 0.0.
        
        tbill_threshold (int, optional): The threshold for the yield difference in basis points for
                                         the T-bill warning. Default is 10.


    Returns:
        tuple: A tuple containing:

            - pd.DataFrame: Combined DataFrame containing data from banks, SSBs, and T-bills.
            
            - list of dict: List of fetch failures, where each entry is a dictionary with two keys:
                
                - product: the product-provider pair (e.g., 'MAS SSB', 'MAS T-bill') 
                - error: the error message.
            
            - list of str: List of warning messages generated during the process.
    """
    fetch_failures = [] # Initialize a list to store fetch failures
    warnings_list = []  # Initialize a list to store warnings
    client = MAS_bondsandbills_APIClient() # Initialize the MAS API client

    # Create dataframe with combined bank data by scraping
    banks_df, bank_fetch_failures = create_banks_df(scrape_inputs)
    fetch_failures.extend(bank_fetch_failures)  # Add bank failures to the list
    
    # Create dataframe with SSB data from MAS API
    try:
        SSB_df = create_ssb_df(client, current_ssb_holdings)
    except Exception as e:
        SSB_df = pd.DataFrame()  # Empty dataframe for SSB
        fetch_failures.append({'product': 'MAS SSB', 'error': str(e)})

    # Create dataframe with T-bill data from MAS API
    try:
        tbill_details = client.get_most_recent_6m_tbill()
        tbill_df = create_tbill_df(tbill_details)

        # Run sudden_6m_tbill_yield_change_warning
        try:
            client.sudden_6m_tbill_yield_change_warning(threshold=tbill_threshold)
        except Warning as warning:
            warnings_list.append(str(warning))
        except Exception as e:
            warnings_list.append(
                f"Could not check for sudden T-bill yield changes: {str(e)}"
            )
    except Exception as e:
        tbill_df = pd.DataFrame()  # Empty dataframe for T-bills
        fetch_failures.append({'product': 'MAS T-bill', 'error': str(e)})

    # Merge the three dataframes
    df_list = [banks_df, SSB_df, tbill_df]
    combined_df = merge_dataframes(df_list)

    return combined_df, fetch_failures, warnings_list