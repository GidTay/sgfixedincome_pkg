sgfixedincome_pkg
=================

.. py:module:: sgfixedincome_pkg

.. autoapi-nested-parse::

   A python package to aggregate and analyse data on
   SGD-denominated retail fixed income products in Singapore.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/sgfixedincome_pkg/analysis/index
   /autoapi/sgfixedincome_pkg/consolidate/index
   /autoapi/sgfixedincome_pkg/equations/index
   /autoapi/sgfixedincome_pkg/mas_api_client/index
   /autoapi/sgfixedincome_pkg/scraper/index


Attributes
----------

.. autoapisummary::

   sgfixedincome_pkg.__version__


Classes
-------

.. autoapisummary::

   sgfixedincome_pkg.MAS_bondsandbills_APIClient
   sgfixedincome_pkg.MAS_bondsandbills_APIClient


Functions
---------

.. autoapisummary::

   sgfixedincome_pkg.filter_df
   sgfixedincome_pkg.best_returns
   sgfixedincome_pkg.best_rates
   sgfixedincome_pkg.products
   sgfixedincome_pkg.plot_rates_vs_tenure
   sgfixedincome_pkg.plot_best_rates
   sgfixedincome_pkg.plot_bank_offerings_with_fuzz
   sgfixedincome_pkg.merge_dataframes
   sgfixedincome_pkg.create_banks_df
   sgfixedincome_pkg.add_ssb_details
   sgfixedincome_pkg.create_ssb_df
   sgfixedincome_pkg.create_tbill_df
   sgfixedincome_pkg.create_combined_df
   sgfixedincome_pkg.calculate_dollar_return
   sgfixedincome_pkg.calculate_per_annum_rate
   sgfixedincome_pkg.fetch_webpage
   sgfixedincome_pkg.extract_table
   sgfixedincome_pkg.table_to_df
   sgfixedincome_pkg.parse_bounds
   sgfixedincome_pkg.parse_tenure
   sgfixedincome_pkg.clean_rate_value
   sgfixedincome_pkg.reshape_table
   sgfixedincome_pkg.scrape_deposit_rates


Package Contents
----------------

.. py:data:: __version__

.. py:function:: filter_df(combined_df, investment_amount=None, min_tenure=0, max_tenure=999, min_rate=None, consider_tbills=True, consider_ssbs=True, consider_fd=True, include_providers=None, exclude_providers=None)

   Filters the combined_df based on provided criteria, including investment amount, tenure, rate,
   product provider, product, and whether to consider T-bills and SSBs.

   :param combined_df: DataFrame containing columns 'Tenure', 'Rate', 'Deposit lower bound',
                       'Deposit upper bound', 'Required multiples', 'Product provider', 'Product'.
   :type combined_df: pd.DataFrame
   :param investment_amount: The investment amount to filter available rates and products for that amount.
   :type investment_amount: float, optional
   :param min_tenure: The minimum tenure (in months) to filter. Default is 0.
   :type min_tenure: int, optional
   :param max_tenure: The maximum tenure (in months) to filter. Default is 999.
   :type max_tenure: int, optional
   :param min_rate: The minimum rate (% p.a.) to filter. Default is None (no filtering).
   :type min_rate: float, optional
   :param consider_tbills: Whether to consider T-bills. Default is True.
   :type consider_tbills: bool, optional
   :param consider_ssbs: Whether to consider SSBs. Default is True.
   :type consider_ssbs: bool, optional
   :param consider_fd: Whether to consider fixed deposits. Default is True.
   :type consider_fd: bool, optional
   :param include_providers: Exclusive list of providers to include. Default is None.
   :type include_providers: list, optional
   :param exclude_providers: List of providers to exclude. Default is None.
   :type exclude_providers: list, optional

   :returns: The filtered DataFrame based on the provided criteria.
   :rtype: pd.DataFrame


.. py:function:: best_returns(combined_df, investment_amount, min_tenure=0, max_tenure=999)

   Calculate the highest total dollar return achievable for each possible tenure,
   considering that the offered rates and available products differ across invested amounts.

   This function assumes you only can select one product to invest in, and finds the highest dollar return
   attainable for each tenure. For products which only accept investment in specific multiples, we allocate the
   maximum amount of investment to them given the investment amount, and assume the remaining cash earns no return.

   As such, for each tenure, the product delivering the best return (our concern here) may differ from the product
   with the highest rates. For example, product 'A' with a higher rate but which has required multiples of investment
   may produce lower total dollar return compared to product 'B' with a lower rate but no required multiples, as the
   full amount of cash cannot be invested in product 'A' but can be fully invested into product 'B'.

   :param combined_df: DataFrame containing columns 'Tenure', 'Rate', 'Deposit lower bound',
                       'Deposit upper bound', 'Required multiples', 'Product provider', 'Product'.
   :type combined_df: pd.DataFrame
   :param investment_amount: The investment amount to filter available rates and products for that amount.
   :type investment_amount: float
   :param min_tenure: The minimum tenure (in months) to consider. Default is 0.
   :type min_tenure: int, optional
   :param max_tenure: The maximum tenure (in months) to consider. Default is 999.
   :type max_tenure: int, optional

   :returns: A DataFrame with products that deliver the highest dollar return for each tenure,
             product details, and total dollar return from the investment.
   :rtype: pd.DataFrame


.. py:function:: best_rates(combined_df, investment_amount, min_tenure=0, max_tenure=999)

   Display the highest rates offered for each possible tenure given an investment amount.

   :param combined_df: DataFrame containing columns 'Tenure', 'Rate', 'Deposit lower bound',
                       'Deposit upper bound', 'Required multiples', 'Product provider', 'Product'.
   :type combined_df: pd.DataFrame
   :param investment_amount: The investment amount to filter available rates and products for that amount.
   :type investment_amount: float
   :param min_tenure: The minimum tenure (in months) to consider. Default is 0.
   :type min_tenure: int, optional
   :param max_tenure: The maximum tenure (in months) to consider. Default is 999.
   :type max_tenure: int, optional

   :returns: A DataFrame with the products offering the best rate (in % p.a.) for each tenure.
   :rtype: pd.DataFrame


.. py:function:: products(combined_df)

   Returns a list of unique products in the dataset by joining the 'Product provider' and 'Product' columns.
   It considers unique combinations of these joined strings.

   :param combined_df: DataFrame containing the columns 'Product provider' and 'Product'.
   :type combined_df: pd.DataFrame

   :returns: A list of unique product combinations in the format 'Product provider - Product'.
   :rtype: list


.. py:function:: plot_rates_vs_tenure(df, investment_amount, min_tenure=0, max_tenure=999)

   Plots a graph of Rate (% p.a.) vs Tenure (in months) for a given investment amount
   with optional filtering by tenure range. Each unique 'Product provider - Product'
   pair is plotted as a separate line.

   :param df: DataFrame containing the data to plot. Must include columns:
              'Tenure', 'Rate', 'Deposit lower bound', 'Deposit upper bound',
              'Product provider', 'Product'.
   :type df: pd.DataFrame
   :param investment_amount: The investment amount to filter rows for the plot.
   :type investment_amount: float
   :param min_tenure: Minimum tenure (in months) to include. Default is 0.
   :type min_tenure: int, optional
   :param max_tenure: Maximum tenure (in months) to include. Default is 999.
   :type max_tenure: int or float, optional

   :raises ValueError: If no valid rows remain after filtering based on the investment amount and tenure.


.. py:function:: plot_best_rates(df, investment_amount, min_tenure=0, max_tenure=999)

   Plot of best rates (% p.a.) for each tenure for a given investment amount, across
   available products. The plot color-codes the points by provider-product pair.

   :param df: DataFrame containing columns 'Tenure', 'Rate', 'Deposit lower bound',
              'Deposit upper bound', 'Required multiples', 'Product provider', 'Product'.
   :type df: pd.DataFrame
   :param investment_amount: The investment amount to filter available rates and products for that amount and
                             to calculate the total return.
   :type investment_amount: float
   :param min_tenure: The minimum tenure (in months) to consider. Default is 0.
   :type min_tenure: int, optional
   :param max_tenure: The maximum tenure (in months) to consider. Default is 999.
   :type max_tenure: int, optional


.. py:function:: plot_bank_offerings_with_fuzz(df, product_provider, fuzz_factor=0.02)

   Plots a graph of Rate (% p.a.) vs Tenure (in months) for a given bank, where each line represents a
   different deposit range (created by joining 'Deposit lower bound' and 'Deposit upper bound').
   Adds small fuzz to the points to avoid overlap.

   :param df: DataFrame containing columns 'Tenure', 'Rate', 'Deposit lower bound',
              'Deposit upper bound', 'Product provider'.
   :type df: pd.DataFrame
   :param product_provider: The bank name (Product provider) to filter the data for.
   :type product_provider: str
   :param fuzz_factor: The amount of fuzz (random noise) to add to the points. Default is 0.02.
   :type fuzz_factor: float, optional

   :raises ValueError: If no data is available for the given product_provider.


.. py:class:: MAS_bondsandbills_APIClient

   API client for interacting with Monetary Authority of Singapore (MAS) bonds and bills endpoints.


   .. py:attribute:: base_url
      :value: 'https://eservices.mas.gov.sg/statistics/api/v1/bondsandbills/m/'



   .. py:method:: fetch_data(endpoint, params=None)

      Fetch data from the MAS API.

      :param endpoint: The API endpoints (e.g., listbondsandbills,
                       pricesandyields_chart, savingbondsinterest, listsavingbonds)
      :type endpoint: str
      :param params: Query parameters for the request.
      :type params: dict, optional

      :returns: The JSON response from the API.
      :rtype: dict

      :raises requests.HTTPError: If the request fails.



   .. py:method:: get_latest_ssb_details()

      Get details of the latest Singapore Savings Bond (SSB).

      :returns: details of the latest SSB bond.
      :rtype: dict



   .. py:method:: get_latest_ssb_issue_code()

      Get the latest Singapore Savings Bond (SSB) issue code.

      :returns: The issue code of the latest bond.
      :rtype: str



   .. py:method:: get_latest_ssb_last_day_to_apply()

      Get the latest Singapore Savings Bond's (SSB) last day to apply.

      :returns: The last day to apply to the latest SSB bond.
      :rtype: str



   .. py:method:: get_ssb_interest(issue_code)

      Get interest details for a specific Singapore Savings Bond (SSB) issue.

      :param issue_code: The bond's issue code.
      :type issue_code: str

      :returns: Interest details for the bond.
      :rtype: dict



   .. py:method:: get_ssb_coupons(issue_code)

      Get list of year 1 to 10 coupon rates for a specific Singapore Savings Bond (SSB) issue.

      :param issue_code: The bond's issue code.
      :type issue_code: str

      :returns: List of coupon rates for each year (year 1 to 10).
      :rtype: list



   .. py:method:: calculate_ssb_tenure_rates(coupons)
      :staticmethod:


      Calculate Singapore Savings Bond's (SSB) monthly tenure rates given coupons.

      :param coupons: List of coupon rates for each year (year 1 to 10).
      :type coupons: list

      :returns: DataFrame containing tenure and corresponding annual rates.
      :rtype: pd.DataFrame



   .. py:method:: get_most_recent_6m_tbill()

      Fetches the most recent 6-month T-bill where the auction has occured.

      This function sends a request to the MAS API to retrieve the most recent T-bill
      (tenor of 6 months) where the auction has occured so total_bids>0.001. Otherwise,
      the endpoint also provides information on upcoming T-bills with auctions that have
      yet to occur, in which case total_bids=0.0.

      :returns: The most recent 6-month T-bill's record containing details such as
                issue code, auction date, cutoff yield etc.
      :rtype: dict



   .. py:method:: get_6m_tbill_bid_yield()

      Fetch the yield of the most recent bid on the most recent 6-month T-bill
      from the "pricesandyields_chart" endpoint.

      :returns: The bid yield for the most recent 6-month T-bill.
      :rtype: float



   .. py:method:: sudden_6m_tbill_yield_change_warning(threshold=10)

      Check if the yield difference between the most recent bid on the most recent 6-month T-bill
      and its cutoff yield exceeds the threshold. If it does, issue a warning.

      Since the Monetary Authority of Singapore typically issues two 6-month T-bills per month,
      the remaining tenor for the most recent 6-month T-bill will never fall below
      5 months. Hence, it should not be too different from the cut-off yield of this T-bill,
      unless there have been sudden unexpected changes in the macroeconomic environment.

      :param threshold: he threshold for the yield difference in basis points (default is 10).
      :type threshold: int

      :returns: This function only issues a warning if the yield difference exceeds the threshold
                or if we fail to sucessfully check if the yield difference exceeds the threshold.
      :rtype: None



   .. py:method:: past_last_day_to_apply_ssb_warning()

      Checks if the current date (in Singapore time) is past 23:59 on the last day to apply for the latest SSB.
      If it is, issues a warning.

      In that case, users are unable to invest into the SSB in the dataset. However, the data is nevertheless useful
      as a benchmark for the next SSB's rates. Hence, we still allow it to be in the dataset. This warning is unlikely
      to be triggered, since details on the next SSB is often provided promptly within day(s) of the prior SSB's last
      day of application.

      :returns: The function only issues a warning if the current date is past the application deadline or if we fail
                to successfully check if the current date is past the application deadline.
      :rtype: None



.. py:function:: merge_dataframes(df_list)

   Merges a list of DataFrames by appending rows, with validation of input.

   :param df_list: A list of pandas DataFrames to be merged. Each DataFrame must either
                   be empty, or contain exactly the following columns:
                   'Tenure', 'Rate', 'Deposit lower bound', 'Deposit upper bound',
                   'Required multiples', 'Product provider', 'Product'.
   :type df_list: list of pd.DataFrame

   :returns: A single DataFrame with all rows from the input DataFrames. Returns an empty DataFrame
             with the required columns if all input DataFrames are empty.
   :rtype: pd.DataFrame

   :raises TypeError: If the input is not a list or does not contain pandas DataFrames.
   :raises ValueError: If any DataFrame in the list does not have exactly the required columns.


.. py:function:: create_banks_df(scrape_inputs)

   Scrapes deposit rates from multiple bank websites and combines them into a single DataFrame.

   Even if scraping fails for some websites, a DataFrame containing data from successfully scraped sites
   is still returned. The function also provides a list of dictionaries with information on websites
   it failed to scrape from. The function also validates the input before running its main task. If we fail
   to scrape from all websites, the function returns an empty dataframe.

   :param scrape_inputs: Each tuple contains:

                         - URL (str): The webpage to scrape.
                         - Table class (str): The class of the table to locate.
                         - Provider (str): The name of the bank/provider.
                         - Required multiples (float or None, optional): Value to populate the "Required multiples" column. Defaults to None if omitted.
   :type scrape_inputs: list of tuples

   :returns:

             A tuple containing:

                 - pd.DataFrame: Combined DataFrame with all successfully scraped deposit rates.

                 - list of dict: Each dict contains details of failed scrapes with:

                     - product (str): Name of the provider and product that failed (e.g. DBS bank fixed deposit)
                     - error (str): Error message describing the failure.
   :rtype: tuple

   :raises ValueError: If the input is not a list of tuples with the expected structure.


.. py:function:: add_ssb_details(df, current_ssb_holdings, issue_code)

   Add additional details to the DataFrame with SSB tenure and rate data.

   :param df: DataFrame with SSB tenure month and rates.
   :type df: pd.DataFrame
   :param current_ssb_holdings: Current SSB holdings in Singapore dollars.
   :type current_ssb_holdings: float
   :param issue_code: The SSB's issue code.
   :type issue_code: str

   :returns: Updated DataFrame with additional SSB information.
   :rtype: pd.DataFrame


.. py:function:: create_ssb_df(client, current_ssb_holdings=0.0)

   Create a dataframe containing the details and rates for the latest Singapore Savings Bond (SSB).

   :param client: An initialized instance of the MAS_bondsandbills_APIClient.
   :param current_ssb_holdings: The amount of SSBs you currently hold in Singapore dollars. Defaults to 0.0.
   :type current_ssb_holdings: float, optional

   :returns: A dataframe with SSB tenure rates and additional details.
   :rtype: pandas.DataFrame


.. py:function:: create_tbill_df(tbill_details)

   Create a pandas DataFrame with details about a T-bill.

   :param tbill_details: A dictionary containing details about a T-bill. Expected keys include:

                         - cutoff_yield (float): in percentage.
                         - issue_code (str): identifies the T-bill.
                         - auction_tenor (float): specifies if it is a 6-month (0.5) or 12-month (1.0) T-bill.
   :type tbill_details: dict

   :returns:

             A DataFrame with the following columns:

                 - Tenure (int): The tenure of the T-bill in months.
                 - Rate (float): The cutoff yield of the T-bill.
                 - Deposit lower bound (int): The minimum investment amount (fixed at 1000).
                 - Deposit upper bound (int): The maximum investment amount (fixed at 99999999).
                 - Required multiples (int): The required investment increments (fixed at 1000).
                 - Product provider (str): The provider of the product (fixed as "MAS").
                 - Product (str): A description of the T-bill, including its issue code.
   :rtype: pd.DataFrame

   .. rubric:: Example

   >>> tbill_details = {"cutoff_yield": 3.08, "issue_code": "BS24123F", "auction_tenor": 0.5}
   >>> df = create_tbill_df(tbill_details)
   >>> df
      Tenure  Rate  Deposit lower bound  Deposit upper bound  Required multiples Product provider          Product
   0       6  3.08                 1000             99999999                1000              MAS  T-bill BS24123F


.. py:function:: create_combined_df(scrape_inputs=[('https://www.dbs.com.sg/personal/rates-online/fixed-deposit-rate-singapore-dollar.page', 'tbl-primary mBot-24', 'DBS'), ('https://www.uob.com.sg/personal/online-rates/singapore-dollar-time-fixed-deposit-rates.page', 'table__carousel-table', 'UOB'), ('https://www.ocbc.com/personal-banking/deposits/fixed-deposit-sgd-interest-rates.page', 'table__comparison-table', 'OCBC')], current_ssb_holdings=0.0, tbill_threshold=10)

   Creates a combined DataFrame by aggregating data from banks, MAS Singapore Savings Bonds (SSBs),
   and Treasury Bills (T-bills), and providing information on cases where data fetching failed.

   :param scrape_inputs: Input parameters for scraping bank data. Each tuple contains:

                         - URL (str): The webpage to scrape.
                         - Table class (str): The class of the table to locate.
                         - Provider (str): The name of the bank/provider.
                         - Required multiples (float or None, optional): Value to populate the "Required multiples" column. Defaults to None if omitted.
                         Default value includes DBS, UOB, and OCBC bank details.
   :type scrape_inputs: list of tuples, optional
   :param current_ssb_holdings: The amount of SSBs you currently hold in Singapore dollars. Defaults to 0.0.
   :type current_ssb_holdings: float, optional
   :param tbill_threshold: The threshold for the yield difference in basis points for
                           the T-bill warning. Default is 10.
   :type tbill_threshold: int, optional

   :returns:

             A tuple containing:

                 - pd.DataFrame: Combined DataFrame containing data from banks, SSBs, and T-bills.

                 - list of dict: List of fetch failures, where each entry is a dictionary with two keys:

                     - product: the product-provider pair (e.g., 'MAS SSB', 'MAS T-bill')
                     - error: the error message.

                 - list of str: List of warning messages generated during the process.
   :rtype: tuple


.. py:function:: calculate_dollar_return(investment, rate, tenure)

   Calculate the dollar return from an investment based on its rate of return
   and the tenure (in months).

   :param investment: The initial amount invested in dollars.
   :type investment: float
   :param rate: The annual rate of return in percentage (%).
   :type rate: float
   :param tenure: The investment tenure in months.
   :type tenure: int

   :returns: The dollar return from the investment after the given tenure.
   :rtype: float

   :raises ValueError: If investment or rate is negative, or tenure is non-positive (zero or negative).


.. py:function:: calculate_per_annum_rate(total_percentage_return, tenure)

   Calculate the equivalent annual rate of return (in percentage) based on
   a given total percentage return over a specific tenure (in months).

   :param total_percentage_return: The total percentage return over the entire investment period.
   :type total_percentage_return: float
   :param tenure: The tenure of the investment in months.
   :type tenure: int

   :returns: The annualized rate of return (in percentage).
   :rtype: float

   :raises ValueError: If tenure is not positive.


.. py:class:: MAS_bondsandbills_APIClient

   API client for interacting with Monetary Authority of Singapore (MAS) bonds and bills endpoints.


   .. py:attribute:: base_url
      :value: 'https://eservices.mas.gov.sg/statistics/api/v1/bondsandbills/m/'



   .. py:method:: fetch_data(endpoint, params=None)

      Fetch data from the MAS API.

      :param endpoint: The API endpoints (e.g., listbondsandbills,
                       pricesandyields_chart, savingbondsinterest, listsavingbonds)
      :type endpoint: str
      :param params: Query parameters for the request.
      :type params: dict, optional

      :returns: The JSON response from the API.
      :rtype: dict

      :raises requests.HTTPError: If the request fails.



   .. py:method:: get_latest_ssb_details()

      Get details of the latest Singapore Savings Bond (SSB).

      :returns: details of the latest SSB bond.
      :rtype: dict



   .. py:method:: get_latest_ssb_issue_code()

      Get the latest Singapore Savings Bond (SSB) issue code.

      :returns: The issue code of the latest bond.
      :rtype: str



   .. py:method:: get_latest_ssb_last_day_to_apply()

      Get the latest Singapore Savings Bond's (SSB) last day to apply.

      :returns: The last day to apply to the latest SSB bond.
      :rtype: str



   .. py:method:: get_ssb_interest(issue_code)

      Get interest details for a specific Singapore Savings Bond (SSB) issue.

      :param issue_code: The bond's issue code.
      :type issue_code: str

      :returns: Interest details for the bond.
      :rtype: dict



   .. py:method:: get_ssb_coupons(issue_code)

      Get list of year 1 to 10 coupon rates for a specific Singapore Savings Bond (SSB) issue.

      :param issue_code: The bond's issue code.
      :type issue_code: str

      :returns: List of coupon rates for each year (year 1 to 10).
      :rtype: list



   .. py:method:: calculate_ssb_tenure_rates(coupons)
      :staticmethod:


      Calculate Singapore Savings Bond's (SSB) monthly tenure rates given coupons.

      :param coupons: List of coupon rates for each year (year 1 to 10).
      :type coupons: list

      :returns: DataFrame containing tenure and corresponding annual rates.
      :rtype: pd.DataFrame



   .. py:method:: get_most_recent_6m_tbill()

      Fetches the most recent 6-month T-bill where the auction has occured.

      This function sends a request to the MAS API to retrieve the most recent T-bill
      (tenor of 6 months) where the auction has occured so total_bids>0.001. Otherwise,
      the endpoint also provides information on upcoming T-bills with auctions that have
      yet to occur, in which case total_bids=0.0.

      :returns: The most recent 6-month T-bill's record containing details such as
                issue code, auction date, cutoff yield etc.
      :rtype: dict



   .. py:method:: get_6m_tbill_bid_yield()

      Fetch the yield of the most recent bid on the most recent 6-month T-bill
      from the "pricesandyields_chart" endpoint.

      :returns: The bid yield for the most recent 6-month T-bill.
      :rtype: float



   .. py:method:: sudden_6m_tbill_yield_change_warning(threshold=10)

      Check if the yield difference between the most recent bid on the most recent 6-month T-bill
      and its cutoff yield exceeds the threshold. If it does, issue a warning.

      Since the Monetary Authority of Singapore typically issues two 6-month T-bills per month,
      the remaining tenor for the most recent 6-month T-bill will never fall below
      5 months. Hence, it should not be too different from the cut-off yield of this T-bill,
      unless there have been sudden unexpected changes in the macroeconomic environment.

      :param threshold: he threshold for the yield difference in basis points (default is 10).
      :type threshold: int

      :returns: This function only issues a warning if the yield difference exceeds the threshold
                or if we fail to sucessfully check if the yield difference exceeds the threshold.
      :rtype: None



   .. py:method:: past_last_day_to_apply_ssb_warning()

      Checks if the current date (in Singapore time) is past 23:59 on the last day to apply for the latest SSB.
      If it is, issues a warning.

      In that case, users are unable to invest into the SSB in the dataset. However, the data is nevertheless useful
      as a benchmark for the next SSB's rates. Hence, we still allow it to be in the dataset. This warning is unlikely
      to be triggered, since details on the next SSB is often provided promptly within day(s) of the prior SSB's last
      day of application.

      :returns: The function only issues a warning if the current date is past the application deadline or if we fail
                to successfully check if the current date is past the application deadline.
      :rtype: None



.. py:function:: fetch_webpage(url)

   Fetches webpage content from the given URL.

   :param url: The URL of the website to scrape.
   :type url: str

   :returns: Parsed HTML content of the page.
   :rtype: BeautifulSoup

   :raises Exception: If the webpage cannot be fetched or parsed.


.. py:function:: extract_table(soup, table_class)

   Locates tables with the specified class in the parsed HTML.

   :param soup: Parsed HTML content.
   :type soup: BeautifulSoup
   :param table_class: Class name of the table(s) to locate.
   :type table_class: str

   :returns: A list of located <table> elements.
   :rtype: list

   :raises Exception: If no tables with the specified class are found.


.. py:function:: table_to_df(table)

   Converts an HTML <table> element into a pandas DataFrame.

   This function takes in a BeautifulSoup Tag object representing a table and extracts the rows and columns of data.
   It can handle both traditional tables where headers are inside <th> tags, as well as tables where the header row is
   indistinguishable from the other rows. In such cases, the header row would simply be the first row in <tbody>, and contents
   would be found within <td> tags in the first <tr> row. Each row’s data is stored as a list of cell values, which are then
   used to construct a pandas DataFrame.

   :param table: A BeautifulSoup Tag object representing the <table>.
   :type table: Tag

   :returns: A pandas DataFrame containing the extracted table data.
   :rtype: pd.DataFrame

   :raises Exception: If the table data extraction fails. For example, when there is an issue during the row data extraction process,
       such as missing <tbody>, <tr>, <td> tags or malformed rows.


.. py:function:: parse_bounds(deposit_range)

   Parses deposit range to extract lower and upper bounds, ensuring inclusive bounds.

   :param deposit_range: String representing the deposit range
   :type deposit_range: str

   :returns: A tuple containing the lower and upper bounds as floats. If only upper bound exists,
             lower bound is set to 0. If only the lower bound exists, upper bound is set to 99,999,999.
   :rtype: tuple

   :raises ValueError: If the range cannot be parsed, if the lower bound is greater than the upper bound,
       or if the range is nonsensical (e.g., "<10000 - 20000" or '10000 - >20000').

   .. rubric:: Examples

   - "$1,000 - $9,999" -> (1000.0, 9999.0)
   - ">S$20,000 - S$50,000" -> (20000.01, 50000.0)
   - "Below S$50,000" -> (0.0, 49999.99)
   - "S$50,000 - S$249,999" -> (50000.0, 249999.0)
   - ">$5,000" -> (5000.01, 99999999.0)
   - "Above 30,000" -> (30000.01, 99999999.0)


.. py:function:: parse_tenure(period_str, header_str)

   Ensure the tenure period is in months and parse it.

   This function extracts the tenure information from `period_str`. The tenure is
   expected to be in months and indicated by keywords such as "month" or "mth" in
   either `period_str` or the `header_str`.

   :param period_str: Tenure period as a string (e.g., "6-12 months").
   :type period_str: str
   :param header_str: Column header to verify if data represents months.
   :type header_str: str

   :returns: List of integer months if the tenure is valid.
   :rtype: list

   :raises ValueError: If the tenure cannot be parsed or is not in months.

   .. rubric:: Examples

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


.. py:function:: clean_rate_value(rate_value)

   Cleans the rate value by removing any non-numeric characters and converting to a float.

   If the rate value is a string representing 'N.A', 'N.A.', or similar (case-insensitive),
   it returns None.

   :param rate_value: The rate value which may include non-numeric characters
                      (e.g., '%', 'N.A.') or be a valid numeric value.
   :type rate_value: str or float

   :returns: The cleaned rate value as a float, or None if the value represents 'N.A'.
   :rtype: float or None

   :raises ValueError: If the rate value cannot be converted to a float and isn't a valid 'N.A.' string.

   .. rubric:: Examples

   - clean_rate_value("5%") -> 5.0
   - clean_rate_value("N.A.") -> None
   - clean_rate_value("3.5") -> 3.5


.. py:function:: reshape_table(raw_df)

   Reshapes the raw DataFrame into a structured format for analysis.

   :param raw_df: The raw DataFrame containing fixed deposit rate data.
                  The first column contains tenure in months (e.g., 'Period', 'Tenor', or 'Tenure').
                  The other columns contain rates for different deposit ranges (e.g., '$1,000-$9,999').
   :type raw_df: pd.DataFrame

   :returns:

             A reshaped DataFrame with the following columns:

                 - Tenure: The duration in months (as float).
                 - Rate: The deposit rates (as float).
                 - Deposit lower bound: The lower bound of the deposit range (as float).
                 - Deposit upper bound: The upper bound of the deposit range (as float, or None if not specified).
   :rtype: pd.DataFrame

   :raises ValueError: If the first column does not contain keywords indicating tenure information.


.. py:function:: scrape_deposit_rates(url, table_class, provider, req_multiples=None)

   Scrapes deposit rates from the given URL and manually add extra information.

   Sometimes, bank websites use the same class for multiple tables, including the key table of interest with
   fixed deposit rates. To enable our scraper to work in such cases, we attempt to scrape data for each of these
   tables, starting with the first. We ignore additional tables once we find one that can be successfully scraped.
   The intuition is that we would only be able to successfully scrape tables with our desired data, and attempted scraping
   of tables containing other information would fail.

   :param url: URL of the website to scrape. The website should contain a table of fixed deposit rates.
   :type url: str
   :param table_class: Class name of the table to locate in the website.
   :type table_class: str
   :param provider: The name of the provider offering the fixed deposit products.
   :type provider: str
   :param req_multiples: The required multiples for the deposit, if applicable. Defaults to None.
   :type req_multiples: optional, float or None

   :returns:

             A pandas DataFrame containing the reshaped deposit rates data, with additional columns:

                 - Required multiples: The value provided in `req_multiples`.
                 - Product provider: The value provided in `provider`.
                 - Product: A static string "Fixed Deposit" indicating the type of product.
   :rtype: pd.DataFrame

   :raises Exception: If the scraping or data extraction process fails, an exception will be raised.


