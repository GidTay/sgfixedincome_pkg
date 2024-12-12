import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sgfixedincome_pkg import consolidate, analysis
from sgfixedincome_pkg.mas_api_client import MAS_bondsandbills_APIClient

def main():
    st.set_page_config(page_title="Singapore Fixed Income Analysis", page_icon="💰", layout="wide")
    
    st.title("🏦 Singapore Fixed Income Investment Analysis")
    
    # Sidebar for navigation
    page = st.sidebar.selectbox("Choose an Analysis", [
        "Data Overview", 
        "Best Returns Analysis", 
        "Best Rates Analysis", 
        "Rate Comparisons", 
        "Provider Offerings"
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
        min_value=500, 
        max_value=200000, 
        value=10000, 
        step=500
    )
    
    # Page-specific analyses
    if page == "Data Overview":
        st.header("Data Overview")
        
        # Display unique products
        st.subheader("Available Products")
        products_list = analysis.products(combined_df)
        st.write(products_list)
        
        # Display raw data
        st.subheader("Raw Data")
        st.dataframe(combined_df)
    
    elif page == "Best Returns Analysis":
        st.header("Best Returns Analysis")
        
        # Tenure range selector
        col1, col2 = st.columns(2)
        with col1:
            min_tenure = st.number_input("Minimum Tenure (months)", min_value=0, max_value=60, value=0)
        with col2:
            max_tenure = st.number_input("Maximum Tenure (months)", min_value=0, max_value=60, value=60)
        
        try:
            best_returns_df = analysis.best_returns(combined_df, investment_amount, min_tenure, max_tenure)
            st.dataframe(best_returns_df)
            
            # Plot best returns
            analysis.plot_best_rates(combined_df, investment_amount, min_tenure, max_tenure)
            st.pyplot(plt.gcf())
            plt.close()
        
        except ValueError as e:
            st.error(str(e))
    
    elif page == "Best Rates Analysis":
        st.header("Best Rates Analysis")
        
        # Tenure range selector
        col1, col2 = st.columns(2)
        with col1:
            min_tenure = st.number_input("Minimum Tenure (months)", min_value=0, max_value=60, value=0)
        with col2:
            max_tenure = st.number_input("Maximum Tenure (months)", min_value=0, max_value=60, value=60)
        
        try:
            best_rates_df = analysis.best_rates(combined_df, investment_amount, min_tenure, max_tenure)
            st.dataframe(best_rates_df)
            
            # Plot best rates
            analysis.plot_rates_vs_tenure(combined_df, investment_amount, min_tenure, max_tenure)
            st.pyplot(plt.gcf())
            plt.close()
        
        except ValueError as e:
            st.error(str(e))
    
    elif page == "Rate Comparisons":
        st.header("Rate Comparisons")
        
        # Tenure selector
        tenure = st.number_input("Select Tenure (months)", min_value=0, max_value=60, value=12)
        
        # Filter dataframe for selected tenure
        tenure_df = combined_df[combined_df['Tenure'] == tenure]
        
        st.subheader(f"Rates for {tenure} Months")
        st.dataframe(tenure_df[['Product provider', 'Product', 'Rate']])
        
        # Bar plot of rates
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Product provider', y='Rate', hue='Product', data=tenure_df)
        plt.title(f'Rates for {tenure} Months Across Providers')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(plt.gcf())
        plt.close()
    
    elif page == "Provider Offerings":
        st.header("Provider Rate Offerings")
        
        # Provider selector
        providers = combined_df['Product provider'].unique()
        selected_provider = st.selectbox("Select Provider", providers)
        
        # Plot provider-specific offerings
        try:
            analysis.plot_bank_offerings_with_fuzz(combined_df, selected_provider)
            st.pyplot(plt.gcf())
            plt.close()
        except ValueError as e:
            st.error(str(e))

if __name__ == "__main__":
    main()