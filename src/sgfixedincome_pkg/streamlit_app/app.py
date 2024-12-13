import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sgfixedincome_pkg import consolidate, analysis
from sgfixedincome_pkg.mas_api_client import MAS_bondsandbills_APIClient

def main():
    st.set_page_config(page_title="Singapore Fixed Income Analysis", page_icon="💰", layout="wide")
    
    st.title("🏦 Singapore Retail Fixed Income Products Analysis")
    
    # Sidebar for navigation
    page = st.sidebar.selectbox("Pages", [
        "Home", 
        "Data Overview",
        "Best Rates and Returns",
        "Provider Offerings",
        "Rate Comparisons"
    ])
    
    # Fetch combined dataframe
    @st.cache_data
    def load_combined_data():
        try:
            combined_df, fetch_failures, warnings = consolidate.create_combined_df()
            
            # Display warnings and fetch failures
            if warnings:
                st.sidebar.warning("Warnings:")
                for warning in warnings:
                    st.sidebar.warning(warning)
            
            if fetch_failures:
                st.sidebar.error("Data Fetch Failures:")
                for failure in fetch_failures:
                    st.sidebar.error(f"{failure['product']}: {failure['error']}")
            
            return combined_df
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return None
    
    combined_df = load_combined_data()
    
    if combined_df is None:
        st.error("Could not load financial data. Please check your internet connection or try again later.")
        return
    
    # Investment amount input (common across most analyses)
    investment_amount = st.sidebar.number_input(
        "Investment Amount (SGD)", 
        value=10000, 
        step=500
    )
    
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
        1. Enter your investment amount (in SGD) in the sidebar.
            The entire analysis is dependent on your investment amount.
        2. Use the navigation menu to access pages that analyse the data.
        3. Adjust inputs (tenure/ product selection) as needed to customize your analysis.
        
        **Pages:**
        - **Data Overview**: Overview of all available data including a summary, a plot,
                    and a raw data table with tenures, rates, deposit ranges, required 
                    investment multiples across products.
        - **Best Rates and Returns**: Find highest return investments and 
                    best rates across tenures
        - **Provider Offerings**: View individual provider rates across deposit ranges and tenures
        - **Rate Comparisons**: View rates across deposit ranges and providers for a given tenure
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
        st.subheader(f"Plot of Available Rates for S${investment_amount}")
        st.markdown(f"Use the tenure selector below to control the x-axis range of the plot:")
        # Tenure range selector
        col1, col2 = st.columns(2)
        with col1:
            min_tenure = st.number_input("Minimum Tenure (months)", min_value=0, max_value=60, value=0)
        with col2:
            max_tenure = st.number_input("Maximum Tenure (months)", min_value=0, max_value=60, value=60)
        
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
            min_tenure = st.number_input("Minimum Tenure (months)", min_value=0, max_value=60, value=0)
        with col2:
            max_tenure = st.number_input("Maximum Tenure (months)", min_value=0, max_value=60, value=60)
        
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
        st.subheader(f"Best Returns for S${investment_amount}")
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
        st.subheader(f"Best Rates for S${investment_amount}")
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
        tenure = st.number_input("Select Tenure (months)", min_value=0, max_value=60, value=6)
        
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