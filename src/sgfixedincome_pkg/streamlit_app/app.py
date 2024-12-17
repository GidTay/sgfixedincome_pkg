import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import requests
import base64
import json
from zoneinfo import ZoneInfo
from sgfixedincome_pkg import consolidate, analysis

class GitHubCache:
    def __init__(self, repo_owner, repo_name, branch="main"):
        """Initialize GitHub cache system"""
        self.owner = repo_owner
        self.repo = repo_name
        self.branch = branch
        self.base_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents"
        
        # Silently tries to get token from secrets, otherwise mark as unavailable
        try:  
            token = st.secrets["GITHUB_TOKEN"]
            self.headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            self.available = True
            st.sidebar.success("GitHub token found successfully")
        except (KeyError, FileNotFoundError) as e:
            self.headers = None
            self.available = False
            st.sidebar.error(f"GitHub token not available: {str(e)}")

    def is_available(self):
        """Check if GitHub cache is available"""
        # Should be unavailable if streamlit app is run locally
        # Only available for my community cloud streamlit app as I provided my secret GITHUB TOKEN
        return self.available
    
    def _get_file_content(self, path):
        """Get file content from GitHub"""
        try:
            response = requests.get(f"{self.base_url}/{path}", headers=self.headers)
            if response.status_code == 200:
                content = base64.b64decode(response.json()["content"]).decode("utf-8")
                return json.loads(content)
            st.sidebar.error(f"GitHub API error: Status {response.status_code}")
            if response.status_code == 404:
                st.sidebar.error("Cache files not found. Check repository name and path.")
            elif response.status_code == 401:
                st.sidebar.error("GitHub API authentication failed. Check token.")
            return None
        except Exception:
            st.sidebar.error(f"Error fetching from GitHub: {str(e)}")
            return None
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def _fetch_fresh_data(_self, reason=None):
        """Helper method to fetch fresh data and format it consistently"""
        message = f"{reason}, fetching fresh data..." if reason else "Fetching fresh data..."
        with st.spinner(message):
            df, failures, warnings = consolidate.create_combined_df()
            return {
                'source': 'direct',
                'current': {
                    'df': df,
                    'failures': failures,
                    'warnings': warnings,
                    'timestamp': datetime.now(ZoneInfo("Asia/Singapore"))
                }
            }

    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def get_data(_self): # _self so streamlit ignores parameter for hashing when caching. Self cannot be hashed.
        """
        Get fixed income data either from GitHub cache or direct fetch.
        
        This method implements the following logic:
        1. If cache is not available (local installation):
        - Directly fetch fresh data
        
        2. If cache is available:
            a. Try to get metadata and current data from cache
            b. If metadata or data is missing:
                - Fallback to direct fetch
            c. If data exists but is more than 2 days old:
                - Fallback to direct fetch
            d. If current data has failures and a successful version exists:
                - Return both versions to allow user selection
        
        3. On any error during cache access:
            - Fallback to direct fetch
        
        Returns:
            dict: A dictionary containing data source and version information:
            {
                'source': str,  # Either 'cache' or 'direct'
                'current': {    # Always present
                    'df': pandas.DataFrame,    # The data
                    'failures': list,          # Any fetch failures
                    'warnings': list,          # Any warnings
                    'timestamp': datetime      # When data was fetched/cached
                },
                'latest_successful': {         # Only present if current has failures
                    'df': pandas.DataFrame,    # The last successful fetch
                    'failures': list,          # Empty by definition
                    'warnings': list,          # Any warnings from that fetch
                    'timestamp': datetime      # When this version was fetched
                }
            }

        Notes:
            - All timestamps are in Singapore timezone (UTC+8)
            - Data is cached per user session for 1 hour (ttl=3600)
        """
        try:
            # If cache is not available (local installation)
            if not _self.available:
                return _self._fetch_fresh_data()

            # Get metadata from cache
            metadata = _self._get_file_content("cache/metadata.json")
            if not metadata:
                return _self._fetch_fresh_data("Cache unavailable")
            
            # Get most recent version
            current_version = metadata["current_version"]
            current_data = _self._get_file_content("cache/data_current.json")
            
            if current_data is None:
                return _self._fetch_fresh_data("Cache data unavailable")
            
            # Process current version
            current_df = pd.DataFrame(current_data)
            current_timestamp = datetime.strptime(current_version["timestamp"], "%Y%m%d_%H%M%S")
            current_timestamp = current_timestamp.replace(tzinfo=ZoneInfo("Asia/Singapore"))
            
            # Check if data is too old (more than 2 days)
            now = datetime.now(ZoneInfo("Asia/Singapore"))
            cache_age = now - current_timestamp
            if cache_age > timedelta(days=2):
                return _self._fetch_fresh_data("Cached data too old")

            result = {
                'source': 'cache',
                'current': {
                    'df': current_df,
                    'failures': current_version["fetch_failures"],
                    'warnings': current_version["warnings"],
                    'timestamp': current_timestamp
                }
            }
            
            # If there are failures and a successful version exists, get it too
            if current_version["fetch_failures"] and metadata.get("latest_successful"):
                latest_successful_data = self._get_file_content("cache/data_latest_successful.json")
                if latest_successful_data:
                    successful_timestamp = datetime.strptime(
                        metadata['latest_successful']["timestamp"], 
                        "%Y%m%d_%H%M%S"
                    ).replace(tzinfo=ZoneInfo("Asia/Singapore"))
                    
                    result['latest_successful'] = {
                        'df': pd.DataFrame(latest_successful_data),
                        'failures': [],  # By definition, latest successful has no failures
                        'warnings': metadata['latest_successful']["warnings"],
                        'timestamp': successful_timestamp
                    }
            
            return result

        except Exception as e:
            # On any error, fallback to direct fetch
            st.error(f"Error accessing cache: {e}")
            return _self._fetch_fresh_data("Error accessing cache")


def main():
    st.set_page_config(page_title="Singapore Fixed Income Analysis", page_icon="💰", layout="wide")

    st.title("🏦 Singapore Retail Fixed Income Products Analysis")
    
    # Sidebar for navigation
    page = st.sidebar.selectbox("Pages", [
        "Home", 
        "Data Overview",
        "Best Rates and Returns",
        "Better Allocation",
        "Provider Offerings",
        "Rate Comparisons"
    ])
    
    # Sidebar investment amount input (common across most analyses)
    investment_amount = st.sidebar.number_input(
        "Investment Amount (SGD)", 
        min_value=500,
        value=10000, 
        step=500,
        help="Enter the amount you intend to invest."
    )

    # Sidebar current SSB holding input (used to update available SSB deposit ranges)
    current_ssb_holdings = st.sidebar.number_input(
        "Current SSB Holdings (SGD)",
        min_value=0.0,
        max_value=200000.0,
        value=0.0,
        step=500.0,
        help="Enter your current Singapore Savings Bonds (SSB) holdings. This affects your maximum possible investment in new SSBs."
    )

    # Function to update SSB bounds
    def update_ssb_bounds(df, ssb_holdings):
        """Update SSB bounds based on current holdings"""
        # Create a copy to avoid modifying the cached dataframe
        df = df.copy()
        
        # Update only SSB rows
        ssb_mask = df['Product'].str.contains('SSB', case=False, na=False)
        
        # Calculate new bounds and update bounds in dataframe
        deposit_upper = max(200000 - ssb_holdings, 0)
        deposit_lower = 500 if deposit_upper >= 500 else 0
        df.loc[ssb_mask, 'Deposit upper bound'] = deposit_upper
        df.loc[ssb_mask, 'Deposit lower bound'] = deposit_lower
        
        return df

    # Initialize cache instance
    @st.cache_resource
    def get_cache_instance():
        return GitHubCache(
            repo_owner="GidTay",
            repo_name="sgfixedincome_cache"
        )
    cache = get_cache_instance()

    # Get data and initialize variables
    versions = cache.get_data()
    combined_df = versions['current']['df']
    fetch_failures = versions['current']['failures']
    warnings = versions['current']['warnings']
    data_timestamp = versions['current']['timestamp']

    # Only show option to use latest successful version if:
    # 1. We're using cached data, not direct fetch (cahched data available and not old)
    # 2. Current version has failures
    # 3. A successful version exists
    if (versions['source'] == 'cache' and 
        fetch_failures and 
        'latest_successful' in versions):
        
        use_latest_successful = st.sidebar.checkbox(
            "Use latest successful version (no fetch failures)",
            value=False,
            help="Current version has some fetch failures. Check this to use the latest version with no failures."
        )
        
        if use_latest_successful:
            successful_version = versions['latest_successful']
            combined_df = successful_version['df']
            fetch_failures = successful_version['failures']
            warnings = successful_version['warnings']
            data_timestamp = successful_version['timestamp']
    
    # Display data source and timestamp in sidebar
    source_text = "Directly fetched" if versions['source'] == 'direct' else "From cache"
    st.sidebar.info(f"Data source: {source_text}\nTimestamp: {data_timestamp.strftime('%Y-%m-%d %H:%M:%S')} SGT")

    # Display any warnings or failures
    if warnings:
        st.sidebar.warning("Warnings:")
        for warning in warnings:
            st.sidebar.warning(warning)
    
    if fetch_failures:
        st.sidebar.error("Data Fetch Failures:")
        for failure in fetch_failures:
            st.sidebar.error(f"{failure['product']}: {failure['error']}")

    # Update SSB bounds
    if combined_df is not None:
        combined_df = update_ssb_bounds(combined_df, current_ssb_holdings)
    else:
        st.error("Could not load financial data. Please check your internet connection or try again later.")
        return
    
    # Page-specific analyses
    if page == "Home":
        st.header("🏠 Home")
        st.markdown("""
            This page aggregates data on SGD-denominated retail fixed income products
            in Singapore, and provides basic tools for analysis.
            
            We only include risk-free and ultra-low risk products:
            - Fixed deposit products from SDIC-insured banks (assets up to a S$100,000 are government insured)
            - Central bank issued treasury bills (T-bills): zero default risk, no capital losses if held to maturity
            - Singapore Savings Bonds (SSB): zero default risk, no capital losses regardless of redemption date.
                        
            **Note**: for bank fixed deposits, we only include standard board rates for new placements.
                        Promotional rates are not considered. Rates are all quoted in % p.a. (compounded).
        """)
        
        st.subheader("🔍 How to Use This Tool")
        st.markdown("""
            **Investment Analysis Steps:**
            1. Enter your investment amount and current SSB holdings (in SGD) in the sidebar.
                The entire analysis is dependent on your investment amount. Your current SSB
                holdings help us determine the maximum additional SSB investments you can make.
            2. Use the navigation menu to access pages that analyse the data.
            3. Adjust inputs (tenure/ product selection) as needed to customize your analysis.
            
            **Pages:**
            - **Data Overview**: Overview of all available data including a summary, a plot,
                        and a raw data table with tenures, rates, deposit ranges, required 
                        investment multiples across products.
            - **Best Rates and Returns**: Find highest return investments and 
                        best rates across tenures
            - **Better Allocation**: Find a possibly better investment strategy that allows for allocation
                        across multiple products, rather than investing the full sum to a single product.
            - **Provider Offerings**: View individual provider rates across deposit ranges and tenures
            - **Rate Comparisons**: View rates across deposit ranges and providers for a given tenure
        """)

        st.subheader("🗂️ Data fetching & Caching Logic")
        st.markdown("""
            To optimize performance and reliability:
            1. Data is scraped and stored in a central cache once every 24 hours, using this [Github repository](https://github.com/GidTay/sgfixedincome_cache).
            2. If the cached data has any fetch failures but a previous successful version exists (no failures), you'll see an option to use that version instead.
            3. If the cached data is more than 2 days old, the tool will fetch fresh data directly.

            When running the tool:
            - If you're using the hosted web app, you'll see whether the data is from the cache or freshly fetched
            - If you're running locally (streamlit run after pip install), the tool will always fetch fresh data
            - The data timestamp (in Singapore time) is always displayed in the sidebar

            If present, warnings and failures will be shown in the sidebar to highlight any data fetching issues.  
        """)

        st.subheader("💫 Like this project?")
        st.markdown("""
            - ⭐ Star the project on [Github](https://github.com/GidTay/sgfixedincome_pkg)
            - 👨‍💻 Contribute to development on [Github](https://github.com/GidTay/sgfixedincome_pkg)
            - 🔗 [Connect with me](https://linktr.ee/gideon.tay)
            - ☕ Buy me a [coffee](https://ko-fi.com/gideontay)
        """)

    elif page == "Data Overview":
        st.header("Data Overview")
        
        # Display unique products
        st.subheader("Unique Products in our Dataset")
        products_list = analysis.products(combined_df)
        st.write(products_list)

        # Plot all rates
        st.subheader(f"Plot of Available Rates for S${investment_amount:,}")
        st.markdown(f"Use the tenure selector below to control the x-axis range of the plot:")
        # Tenure range selector
        col1, col2 = st.columns(2)
        with col1:
            min_tenure = st.number_input("Minimum Tenure (months)", min_value=0, max_value=120, value=0)
        with col2:
            max_tenure = st.number_input("Maximum Tenure (months)", min_value=0, max_value=120, value=60)
        
        # Plot. Limit size of plot to center 3/5 of page width
        try:
            analysis.plot_rates_vs_tenure(combined_df, investment_amount, min_tenure, max_tenure)
            col1, col2, col3 = st.columns([1,3,1])
            with col2:
                st.pyplot(plt.gcf())
            plt.close()
        except ValueError as e:
            st.error(str(e))
        
        # Display raw data
        st.subheader("Raw Data Table")
        st.markdown(f"No. of rows: {combined_df.shape[0]}")
        st.dataframe(combined_df)
    
    elif page == "Best Rates and Returns":
        st.header("💰 Best Rates and Returns")
        
        # Tenure range selector
        st.markdown("**Select Tenures to Consider:**")
        col1, col2 = st.columns(2)
        with col1:
            min_tenure = st.number_input("Minimum Tenure (months)", min_value=0, max_value=120, value=0)
        with col2:
            max_tenure = st.number_input("Maximum Tenure (months)", min_value=0, max_value=120, value=60)
        
        # Add product selection checkboxes
        st.markdown("**Select Products to Include:**")
        products_list = analysis.products(combined_df)
        product_selections = {}
        col1, col2 = st.columns(2)
        for i, product in enumerate(products_list):
            with col1 if i < len(products_list)/2 else col2:
                product_selections[product] = st.checkbox(product, value=True)

        # Filter dataframe based on selections
        filtered_df = combined_df[combined_df.apply(lambda row: 
            product_selections[f"{row['Product provider']} - {row['Product']}"], axis=1)]

        # Best returns section
        st.subheader(f"Best Returns for S${investment_amount:,}")
        st.markdown("""
        Find the highest total dollar return attainable for each tenure, considering that the
        offered rates and available products differ across invested amounts.
        
        Assumptions:
        - We assume you only can select one product to invest in. Often, especially for larger
        investment sums, it is optimal to split the sum into multiple products as fixed deposit 
        rates offered for higher sums are lower.
        - For products which only accept investment in specific multiples, we allocate the maximum 
        amount of investment to them given the investment amount, and assume the remaining cash 
        earns no return.
        """)
        try:
            best_returns_df = analysis.best_returns(filtered_df, investment_amount, min_tenure, max_tenure)
            st.dataframe(best_returns_df)
        except ValueError as e:
            st.error(str(e))
    
        # Best rates section
        st.subheader(f"Best Rates for S${investment_amount:,}")
        st.markdown("""
        While usually identical to the best returns table above, this may not always be the case.
        For example, product A with a higher rate but which has required multiples of investment may produce 
        lower total dollar return compared to product B with a slightly lower rate but no required multiples, 
        as the full amount of cash cannot be invested in product A but can be fully invested into product B.
        """)
        try:
            best_rates_df = analysis.best_rates(filtered_df, investment_amount, min_tenure, max_tenure)
            st.dataframe(best_rates_df)

            # Plot best rates
            st.markdown("**Plot of best rates**")
            analysis.plot_best_rates(filtered_df, investment_amount, min_tenure, max_tenure)
            col1, col2, col3 = st.columns([1,3,1])
            with col2:
                st.pyplot(plt.gcf())
            plt.close()

        except ValueError as e:
            st.error(str(e))
    
    elif page == "Better Allocation":
        st.header("🤓 Better Allocation")

        # Tenure selector
        tenure = st.number_input("Select Tenure (months)", min_value=0, max_value=120, value=12)
        
        # Add product selection checkboxes
        st.markdown("**Select Products to Include:**")
        products_list = analysis.products(combined_df)
        product_selections = {}
        col1, col2 = st.columns(2)
        for i, product in enumerate(products_list):
            with col1 if i < len(products_list)/2 else col2:
                product_selections[product] = st.checkbox(product, value=True)

        # Filter dataframe based on selections
        filtered_df = combined_df[combined_df.apply(lambda row: 
            product_selections[f"{row['Product provider']} - {row['Product']}"], axis=1)]

        # Better Allocation section
        st.subheader(f"Best Allocation for S${investment_amount:,}")
        st.markdown("""
        Returns a better strategy to improve effective rate by allocating investment across 
        different products. Refer to documentation for details.
                    
        Note: while this strategy often produces returns at least as good as investing in any 
        single product, it may sometimes produce lower returns, and may also be different 
        from the globally optimal allocation. 
        """)
        try:
            allocation_df = analysis.better_allocation(filtered_df, investment_amount, tenure)
            st.dataframe(allocation_df)
        except ValueError as e:
            st.error(str(e))

        # Plot better_allocation strategy rates
        st.subheader(f"Plot of 'better allocation' strategy rates for S${investment_amount:,}")
        
        # Tenure range selector
        st.markdown("**Select Tenures to Plot:**")
        col1, col2 = st.columns(2)
        with col1:
            min_tenure = st.number_input("Minimum Tenure (months)", min_value=0, max_value=120, value=0)
        with col2:
            max_tenure = st.number_input("Maximum Tenure (months)", min_value=0, max_value=120, value=60)
        
        # Plot better_allocation strategy rates alone
        try:
            analysis.plot_better_allocation_strategy(filtered_df, investment_amount, min_tenure, max_tenure)
            col1, col2, col3 = st.columns([1,3,1])
            with col2:
                st.pyplot(plt.gcf())
            plt.close()
        except ValueError as e:
            st.error(str(e))
        
        # Plot better_allocation strategy and pure rates
        try:
            analysis.plot_pure_and_better_allocation_strategy_rates(filtered_df, investment_amount, min_tenure, max_tenure)
            col1, col2, col3 = st.columns([1,3,1])
            with col2:
                st.pyplot(plt.gcf())
            plt.close()
        except ValueError as e:
            st.error(str(e))

    elif page == "Provider Offerings":
        st.header("🏦 Provider Rate Offerings")
        st.markdown("View rates offered across deposit ranges for any given provider:")

        # Provider selector
        providers = combined_df['Product provider'].unique()
        selected_provider = st.selectbox("Select Provider", providers)
        
        # Plot provider-specific offerings
        try:
            analysis.plot_bank_offerings_with_fuzz(combined_df, selected_provider)
            col1, col2, col3 = st.columns([1,3,1])
            with col2:
                st.pyplot(plt.gcf())
            plt.close()
        except ValueError as e:
            st.error(str(e))
    
    elif page == "Rate Comparisons":
        st.header("⚖️ Rate Comparisons")
        st.markdown("View rates across deposit ranges and providers for a given tenure:")
        
        # Tenure selector
        tenure = st.number_input("Select Tenure (months)", min_value=0, max_value=120, value=6)
        
        # Filter dataframe for selected tenure
        tenure_df = combined_df[combined_df['Tenure'] == tenure]
        
        st.subheader(f"Rates for {tenure} Months")
        st.dataframe(tenure_df[[
            'Product provider', 'Product', 'Rate', 
            'Deposit lower bound', 'Deposit upper bound'
            ]])
        
        # Bar plot of rates
        st.markdown(f"**Plot of rate ranges across providers for {tenure} months tenure**")
        st.markdown("Each dot represents a rate offered for a specific deposit range:")
        plt.figure(figsize=(9, 4))
        sns.stripplot(x='Product provider', y='Rate', data=tenure_df, size=4)
        plt.title(f'Rates for {tenure} Months Across Providers')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(plt.gcf())
        plt.close()

if __name__ == "__main__":
    main()