import requests
import pandas as pd
import warnings
from datetime import datetime
import pytz
from sgfixedincome_pkg import equations

class MAS_bondsandbills_APIClient:
    """
    API client for interacting with Monetary Authority of Singapore (MAS) bonds and bills endpoints.
    """

    def __init__(self):
        """
        Initialize the API client.

        Args:
            base_url (str): Base URL for the MAS API.
        """
        base_url = "https://eservices.mas.gov.sg/statistics/api/v1/bondsandbills/m/"
        self.base_url = base_url

    def fetch_data(self, endpoint, params=None):
        """
        Fetch data from the MAS API.

        Args:
            endpoint (str): The API endpoints (e.g., listbondsandbills, 
                            pricesandyields_chart, savingbondsinterest, listsavingbonds)
            params (dict, optional): Query parameters for the request.

        Returns:
            dict: The JSON response from the API.

        Raises:
            requests.HTTPError: If the request fails.
        """        
        url = self.base_url + endpoint
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_latest_ssb_details(self):
        """
        Get details of the latest Singapore Savings Bond (SSB).

        Returns:
            dict: details of the latest SSB bond.
        
        Raises:
            Exception: If API request fails to fetch latest SSB data.
        """
        try:
            response = self.fetch_data(
                "listsavingbonds", 
                params={"rows": 1, "sort": "issue_date desc"}
                )
        except Exception as e:
            raise Exception(f"Failed to fetch latest SSB data: {e}")

        return response["result"]["records"][0]
    
    def get_latest_ssb_issue_code(self):
        """
        Get the latest Singapore Savings Bond (SSB) issue code.

        Returns:
            str: The issue code of the latest bond.
        """
        response = self.get_latest_ssb_details()
        return response["issue_code"]
    
    def get_latest_ssb_last_day_to_apply(self):
        """
        Get the latest Singapore Savings Bond's (SSB) last day to apply.

        Returns:
            str: The last day to apply to the latest SSB bond.
        """
        response = self.get_latest_ssb_details()
        return response["last_day_to_apply"]

    def get_ssb_interest(self, issue_code):
        """
        Get interest details for a specific Singapore Savings Bond (SSB) issue.

        Args:
            issue_code (str): The bond's issue code.

        Returns:
            dict: Interest details for the bond.
        
        Raises:
            Exception: If API request fails to fetch SSB rates and returns data.
        """
        try:
            response = self.fetch_data(
                "savingbondsinterest",
                params={"rows": 1, "filters": f"issue_code:{issue_code}"}
            )
        except Exception as e:
            raise Exception(f"Failed to fetch SSB rates and returns data: {e}")
    
        return response["result"]["records"][0]
    
    def get_ssb_coupons(self, issue_code):
        """
        Get list of year 1 to 10 coupon rates for a specific Singapore Savings Bond (SSB) issue.

        Args:
            issue_code (str): The bond's issue code.

        Returns:
            list: List of coupon rates for each year (year 1 to 10).
        """
        interest_details = self.get_ssb_interest(issue_code)
        coupons = [interest_details[f"year{i}_coupon"] for i in range(1, 11)]
        return coupons
    
    @staticmethod
    def calculate_ssb_tenure_rates(coupons):
        """
        Calculate Singapore Savings Bond's (SSB) monthly tenure rates given coupons.

        Args:
            coupons (list): List of coupon rates for each year (year 1 to 10).

        Returns:
            pd.DataFrame: DataFrame containing tenure and corresponding annual rates.
        
        Raises:
            ValueError: If the coupon list provided does not have exactly 10 elements corresponding
                        to coupon rates for 10 years.
        """
        # Ensure coupons list input is a valid list of SSB coupon rates
        if len(coupons) != 10: # 
            raise ValueError(
                f"Coupons list must have 10 elements for coupon rates over 10 years, "
                f"but it has {len(coupons)} elements.")
        if not all(coupons[i] <= coupons[i+1] for i in range(len(coupons)-1)):
            raise ValueError("Coupon rates must be monotonically increasing.")

        records = []
        for i in range(120): # Iterate through all 120 months (10yrs)
            tenure = i + 1  # Tenure in months (starting from 1)
            n_years = tenure // 12  # Full years completed
            month_of_yr = tenure % 12  # Months into the current year

            # Calculate total percentage return on the invested amount
            if month_of_yr == 0:  # If tenure is a multiple of 12
                total_percentage_return = sum(coupons[:n_years])  # Sum of all full year coupons
            else: # If tenure is not a multiple of 12, prorate returns for current year
                total_percentage_return = sum(coupons[:n_years]) + coupons[n_years] * month_of_yr / 12

            # Calculate the annualized rate
            annual_rate = equations.calculate_per_annum_rate(total_percentage_return, tenure)
            records.append({"Tenure": tenure, "Rate": annual_rate})

        return pd.DataFrame(records)
    
    def get_most_recent_6m_tbill(self):
        """
        Fetches the most recent 6-month T-bill where the auction has occured.
        
        This function sends a request to the MAS API to retrieve the most recent T-bill
        (tenor of 6 months) where the auction has occured so total_bids>0.001. Otherwise,
        the endpoint also provides information on upcoming T-bills with auctions that have
        yet to occur, in which case total_bids=0.0.
        
        Returns:
            dict: The most recent 6-month T-bill's record containing details such as 
            issue code, auction date, cutoff yield etc.
        
        Raises:
            Exception: If API request fails to fetch latest T-bill data.
        """
        # Prepare the API request parameters
        filters = (
            'bill_bond_ind:"bill" AND ' # Get T-bills only not bonds
            'product_type:"B" AND '     # Get retail T-bills not institutional MAS bills
            'auction_tenor:"0.5" AND '  # 6-month tenor (0.5 years)
            'total_bids:[0.001 TO *]'   # Ignore upcoming T-bills with auction yet to occur (total_bids=0.0)
        )

        # Fetch and return the data 
        try:
            response = self.fetch_data(
                "listbondsandbills",
                params={
                    "rows": 1,                  # Only get the most recent 6mo T-bill
                    "filters": filters,
                    "sort": "auction_date desc" # To get the most recent 6mo T-bill first
                    }
                )
        except Exception as e:
            raise Exception(f"Failed to fetch latest T-bill data: {e}")
        
        return response["result"]["records"][0]
    
    def get_6m_tbill_bid_yield(self):
        """
        Fetch the yield of the most recent bid on the most recent 6-month T-bill 
        from the "pricesandyields_chart" endpoint.
        
        Returns:
            float: The bid yield for the most recent 6-month T-bill.
        
        Raises:
            Exception: If API request fails to fetch the most recent bid price and yield data.
        """
        try:
            response = self.fetch_data(
                "pricesandyields_chart",
                params={
                    "rows": 1,                   # Only get bid data from the most recent day
                    "filters": "product_type:B", # Get retail T-bills, not institutional MAS bills
                    "sort": "end_of_period desc" # To get the most recent bids
                }
            )
        except Exception as e:
            raise Exception(f"Failed to fetch most recent bid price and yield data: {e}")
        
        return response["result"]["records"][0]["bid_6m_tbill_yield"]

    
    def sudden_6m_tbill_yield_change_warning(self, threshold=10):
        """
        Check if the yield difference between the most recent bid on the most recent 6-month T-bill 
        and its cutoff yield exceeds the threshold. If it does, issue a warning.
        
        Since the Monetary Authority of Singapore typically issues two 6-month T-bills per month,
        the remaining tenor for the most recent 6-month T-bill will never fall below
        5 months. Hence, it should not be too different from the cut-off yield of this T-bill,
        unless there have been sudden unexpected changes in the macroeconomic environment.

        Parameters:
            threshold (int): he threshold for the yield difference in basis points (default is 10).

        Returns:
            None: This function only issues a warning if the yield difference exceeds the threshold
            or if we fail to sucessfully check if the yield difference exceeds the threshold.
        """
        # Fetch the most recent 6-month T-bill bid yield
        try:
            bid_yield = self.get_6m_tbill_bid_yield()

            # Fetch the most recent 6-month T-bill cutoff yield
            tbill_details = self.get_most_recent_6m_tbill()
            cutoff_yield = tbill_details["cutoff_yield"]
            
            # Issue a warning if yield difference exceeds threshold
            yield_difference = abs(bid_yield - cutoff_yield) * 100  # In basis points
            if yield_difference >= threshold:
                warning_message = (
                    f"The difference between the bid yield and the cutoff yield is large "
                    f"({yield_difference} bps). "
                    "The previous 6-month T-bill's cutoff yield may not be a good estimate "
                    "of the upcoming cutoff-yield."
                )
                warnings.warn(warning_message)

        except Exception as e:
            warnings.warn(f"Failed to check for sudden T-bill yield changes: {str(e)}")
    
    def past_last_day_to_apply_ssb_warning(self):
        """
        Checks if the current date (in Singapore time) is past 23:59 on the last day to apply for the latest SSB.
        If it is, issues a warning. 
        
        In that case, users are unable to invest into the SSB in the dataset. However, the data is nevertheless useful
        as a benchmark for the next SSB's rates. Hence, we still allow it to be in the dataset. This warning is unlikely
        to be triggered, since details on the next SSB is often provided promptly within day(s) of the prior SSB's last 
        day of application.

        Returns:
            None: The function only issues a warning if the current date is past the application deadline or if we fail
            to successfully check if the current date is past the application deadline.
        """
        try:
            # Get the last day to apply for the latest SSB and convert to datetime object in SGT
            last_day_str = self.get_latest_ssb_last_day_to_apply()
            singapore_tz = pytz.timezone("Asia/Singapore")
            last_day = singapore_tz.localize(datetime.strptime(last_day_str, '%Y-%m-%d'))
            last_day_end = last_day.replace(hour=23, minute=59, second=59) # Add time 23:59:59

            # Get the current date and time in Singapore timezone
            current_datetime = datetime.now(tz=singapore_tz)

            # Check if the current date is past 23:59 on the last day to apply
            if current_datetime > last_day_end:
                warnings.warn(
                    f"The last day to apply for the latest SSB ({last_day.strftime('%Y-%m-%d')}) has passed. "
                    "You may not be able to apply for this SSB."
                )

        except Exception as e:
            warnings.warn(f"Failed to check if the last day to apply for SSB has passed: {str(e)}")