import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from sgfixedincome_pkg import equations

def filter_df(combined_df, investment_amount=None, min_tenure=0, max_tenure=999, 
              min_rate=None, consider_tbills=True, consider_ssbs=True, consider_fd=True, 
              include_providers=None, exclude_providers=None):
    """
    Filters the combined_df based on provided criteria, including investment amount, tenure, rate, 
    product provider, product, and whether to consider T-bills and SSBs.

    Parameters:
        combined_df (pd.DataFrame): DataFrame containing columns 'Tenure', 'Rate', 'Deposit lower bound', 
                                    'Deposit upper bound', 'Required multiples', 'Product provider', 'Product'.
        investment_amount (float, optional): The investment amount to filter available rates and products for that amount.
        min_tenure (int, optional): The minimum tenure (in months) to filter. Default is 0.
        max_tenure (int, optional): The maximum tenure (in months) to filter. Default is 999.
        min_rate (float, optional): The minimum rate (% p.a.) to filter. Default is None (no filtering).
        consider_tbills (bool, optional): Whether to consider T-bills. Default is True.
        consider_ssbs (bool, optional): Whether to consider SSBs. Default is True.
        consider_fd (bool, optional): Whether to consider fixed deposits. Default is True.
        include_providers (list, optional): Exclusive list of providers to include. Default is None.
        exclude_providers (list, optional): List of providers to exclude. Default is None.

    Returns:
        pd.DataFrame: The filtered DataFrame based on the provided criteria.
    """
    filtered_df = combined_df.copy()

    # Filter based on investment amount (if provided)
    if investment_amount is not None:
        filtered_df = filtered_df[(filtered_df['Deposit lower bound'] <= investment_amount) & 
                                   (filtered_df['Deposit upper bound'] >= investment_amount)]

    # Filter based on tenure range
    filtered_df = filtered_df[(filtered_df['Tenure'] >= min_tenure) & 
                               (filtered_df['Tenure'] <= max_tenure)]
    
    # Filter based on rate range (if provided)
    if min_rate is not None:
        filtered_df = filtered_df[filtered_df['Rate'] >= min_rate]

    # Filter based on product (SSB, T-bill, Fixed Deposit)
    if not consider_tbills:
        filtered_df = filtered_df[~filtered_df['Product'].str.contains("T-bill", case=False, na=False)]
    if not consider_ssbs:
        filtered_df = filtered_df[~filtered_df['Product'].str.contains("SSB", case=False, na=False)]
    if not consider_fd:
        filtered_df = filtered_df[~filtered_df['Product'].str.contains("Fixed Deposit", case=False, na=False)]

    # Filter based on product provider (if provided)
    if include_providers:
        filtered_df = filtered_df[filtered_df['Product provider'].isin(include_providers)]
    
    # Filter based on product provider (if provided)
    if exclude_providers:
        filtered_df = filtered_df[~filtered_df['Product provider'].isin(exclude_providers)]

    # If no rows remain after filtering, raise an exception
    if filtered_df.empty:
        raise ValueError("No products found matching the provided criteria.")
    
    return filtered_df.reset_index(drop=True)

def best_returns(combined_df, investment_amount, min_tenure=0, max_tenure=999):
    """
    Calculate the highest total dollar return achievable for each possible tenure,
    considering that the offered rates and available products differ across invested amounts. 

    This function assumes you only can select one product to invest in, and finds the highest dollar return
    attainable for each tenure. For products which only accept investment in specific multiples, we allocate the
    maximum amount of investment to them given the investment amount, and assume the remaining cash earns no return.
    
    As such, for each tenure, the product delivering the best return (our concern here) may differ from the product 
    with the highest rates. For example, product 'A' with a higher rate but which has required multiples of investment
    may produce lower total dollar return compared to product 'B' with a lower rate but no required multiples, as the 
    full amount of cash cannot be invested in product 'A' but can be fully invested into product 'B'.

    Parameters:
        combined_df (pd.DataFrame): DataFrame containing columns 'Tenure', 'Rate', 'Deposit lower bound', 
                                    'Deposit upper bound', 'Required multiples', 'Product provider', 'Product'.
        investment_amount (float): The investment amount to filter available rates and products for that amount.
        min_tenure (int, optional): The minimum tenure (in months) to consider. Default is 0.
        max_tenure (int, optional): The maximum tenure (in months) to consider. Default is 999.

    Returns:
        pd.DataFrame: A DataFrame with products that deliver the highest dollar return for each tenure, 
        product details, and total dollar return from the investment.
    """
    # Filter rows where the investment_amount and Tenure is within the allowed bounds
    valid_inv_df = filter_df(
        combined_df,
        investment_amount=investment_amount, 
        min_tenure=min_tenure, 
        max_tenure=max_tenure
        ).copy()
    
    # If no valid rows remain after filtering, raise an exception
    if valid_inv_df.empty:
        raise ValueError(f"Cannot find valid products for an investment amount of {investment_amount}.")
    
    # Calculate the maximum investable amount based on required multiples
    def calculate_invested_amount(row):
        if pd.isna(row['Required multiples']):
            return investment_amount  # No multiples restriction, use the entire amount
        max_multiple = investment_amount // row['Required multiples']
        return max_multiple * row['Required multiples']  # Maximum valid investable amount
    
    valid_inv_df['Invested amount'] = valid_inv_df.apply(
        calculate_invested_amount, axis=1
        )

    # Calculate the total dollar return for each row using the 'Invested amount'
    valid_inv_df.loc[:, 'Total Dollar Return'] = valid_inv_df.apply(
        lambda row: equations.calculate_dollar_return(
            row['Invested amount'],
            row['Rate'],
            row['Tenure']
        ),
        axis=1
    )

    # Group by tenure and get the row with the maximum total return for each tenure
    best_returns_df = valid_inv_df.loc[
        valid_inv_df.groupby('Tenure')['Total Dollar Return'].idxmax()
        ]
    best_returns_df.sort_values(by='Tenure', inplace=True) # Sort by tenure

    return best_returns_df.reset_index(drop=True)

def best_rates(combined_df, investment_amount, min_tenure=0, max_tenure=999):
    """
    Display the highest rates offered for each possible tenure given an investment amount.

    Parameters:
        combined_df (pd.DataFrame): DataFrame containing columns 'Tenure', 'Rate', 'Deposit lower bound', 
                                    'Deposit upper bound', 'Required multiples', 'Product provider', 'Product'.
        investment_amount (float): The investment amount to filter available rates and products for that amount.
        min_tenure (int, optional): The minimum tenure (in months) to consider. Default is 0.
        max_tenure (int, optional): The maximum tenure (in months) to consider. Default is 999.

    Returns:
        pd.DataFrame: A DataFrame with the products offering the best rate (in % p.a.) for each tenure.
    """
    # Filter rows where the investment_amount and Tenure is within the allowed bounds
    valid_inv_df = filter_df(
        combined_df,
        investment_amount=investment_amount, 
        min_tenure=min_tenure, 
        max_tenure=max_tenure
        ).copy()
    
    # If no valid rows remain after filtering, raise an exception
    if valid_inv_df.empty:
        raise ValueError(f"Cannot find valid products for an investment amount of {investment_amount}.")

    # Group by tenure and get the row with the highest rate for each tenure
    best_rates_df = valid_inv_df.loc[
        valid_inv_df.groupby('Tenure')['Rate'].idxmax()
        ]
    best_rates_df.sort_values(by='Tenure', inplace=True) # Sort by tenure

    return best_rates_df.reset_index(drop=True)

def products(combined_df):
    """
    Returns a list of unique products in the dataset by joining the 'Product provider' and 'Product' columns.
    It considers unique combinations of these joined strings.

    Parameters:
        combined_df (pd.DataFrame): DataFrame containing the columns 'Product provider' and 'Product'.

    Returns:
        list: A list of unique product combinations in the format 'Product provider - Product'.
    """
    # Combine 'Product provider' and 'Product' into a single string for each row
    product_combinations = combined_df['Product provider'] + ' - ' + combined_df['Product']
    
    # Get the unique combinations and return them as a list
    unique_products = product_combinations.unique().tolist()

    return unique_products

def plot_rates_vs_tenure(df, investment_amount, min_tenure=0, max_tenure=999):
    """
    Plots a graph of Rate (% p.a.) vs Tenure (in months) for a given investment amount
    with optional filtering by tenure range. Each unique 'Product provider - Product' 
    pair is plotted as a separate line.

    Parameters:
        df (pd.DataFrame): DataFrame containing the data to plot. Must include columns:
                            'Tenure', 'Rate', 'Deposit lower bound', 'Deposit upper bound', 
                            'Product provider', 'Product'.
        investment_amount (float): The investment amount to filter rows for the plot.
        min_tenure (int, optional): Minimum tenure (in months) to include. Default is 0.
        max_tenure (int or float, optional): Maximum tenure (in months) to include. Default is 999.

    Raises:
        ValueError: If no valid rows remain after filtering based on the investment amount and tenure.
    """
    # Filter rows by investment amount and tenure range
    filtered_df = filter_df(
        df,
        investment_amount=investment_amount, 
        min_tenure=min_tenure, 
        max_tenure=max_tenure
        ).copy()

    # Raise an exception if no valid rows remain
    if filtered_df.empty:
        raise ValueError(f"No data available for the investment amount of {investment_amount} "
                         f"and tenure range {min_tenure}-{max_tenure} months.")

    # Create a unique identifier for each product provider-product pair
    filtered_df['Product Combination'] = (
        filtered_df['Product provider'] + ' - ' + filtered_df['Product']
    )

    # Plotting
    plt.figure(figsize=(12, 8))
    sns.lineplot(
        data=filtered_df,
        x='Tenure',
        y='Rate',
        hue='Product Combination',
        marker='o'
    )

    # Customizing the plot
    plt.title(
        f'Rate (% p.a.) vs Tenure for Investment Amount: {investment_amount}\n'
        f'Filtered by Tenure: {min_tenure} to {max_tenure} months',
        fontsize=16
    )
    plt.xlabel('Tenure (Months)', fontsize=14)
    plt.ylabel('Rate (% p.a.)', fontsize=14)
    plt.legend(title='Product Provider - Product', fontsize=12, title_fontsize=14, loc='best')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    # Show the plot
    plt.show()

def plot_best_rates(df, investment_amount, min_tenure=0, max_tenure=999):
    """
    Plot of best rates (% p.a.) for each tenure for a given investment amount, across
    available products. The plot color-codes the points by provider-product pair.

    Parameters:
        df (pd.DataFrame): DataFrame containing columns 'Tenure', 'Rate', 'Deposit lower bound', 
                           'Deposit upper bound', 'Required multiples', 'Product provider', 'Product'.
        investment_amount (float): The investment amount to filter available rates and products for that amount and
                                    to calculate the total return.
        min_tenure (int, optional): The minimum tenure (in months) to consider. Default is 0.
        max_tenure (int, optional): The maximum tenure (in months) to consider. Default is 999.
    """
    # Get best rates DataFrame
    best_rates_df = best_rates(df, investment_amount, min_tenure, max_tenure)
    
    # Combine 'Product provider' and 'Product' for unique identification
    best_rates_df['Provider-Product'] = best_rates_df['Product provider'] + " - " + best_rates_df['Product']
    
    # Create the plot
    plt.figure(figsize=(12, 8))
    
    # Draw a single continuous line
    plt.plot(best_rates_df['Tenure'], best_rates_df['Rate'], 
             linestyle='-', color='black', alpha=0.7)
    
    # Add points, color-coded by Provider-Product
    sns.scatterplot(
        data=best_rates_df,
        x='Tenure',
        y='Rate',
        hue='Provider-Product',
        palette='tab10',  # Customize color palette as needed
        s=100,  # Size of points
        edgecolor='black'
    )
    
    # Add labels and grid
    plt.title("Rate (% p.a.) by Tenure (Color-coded by Provider-Product)", fontsize=16)
    plt.xlabel("Tenure (months)", fontsize=14)
    plt.ylabel("Rate (% p.a.)", fontsize=14)
    plt.grid(alpha=0.3)
    plt.legend(title="Provider-Product", fontsize=14, bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    # Show the plot
    plt.show()

def plot_bank_offerings_with_fuzz(df, product_provider, fuzz_factor=0.02):
    """
    Plots a graph of Rate (% p.a.) vs Tenure (in months) for a given bank, where each line represents a 
    different deposit range (created by joining 'Deposit lower bound' and 'Deposit upper bound').
    Adds small fuzz to the points to avoid overlap.

    Parameters:
        df (pd.DataFrame): DataFrame containing columns 'Tenure', 'Rate', 'Deposit lower bound', 
                            'Deposit upper bound', 'Product provider'.
        product_provider (str): The bank name (Product provider) to filter the data for.
        fuzz_factor (float, optional): The amount of fuzz (random noise) to add to the points. Default is 0.02.

    Raises:
        ValueError: If no data is available for the given product_provider.
    """
    # Filter rows for the specified product provider and create a copy
    filtered_df = df[df['Product provider'] == product_provider].copy()

    # Raise an exception if no valid rows remain after filtering
    if filtered_df.empty:
        raise ValueError(f"No data available for the product provider {product_provider}.")

    # Create a unique identifier for each deposit range and add small random fuzz
    filtered_df = filtered_df.assign(
        Deposit_Range=filtered_df['Deposit lower bound'].astype(str) + '-' + filtered_df['Deposit upper bound'].astype(str),
        Tenure_fuzzed=filtered_df['Tenure'] + np.random.uniform(-fuzz_factor, fuzz_factor, len(filtered_df)),
        Rate_fuzzed=filtered_df['Rate'] + np.random.uniform(-fuzz_factor, fuzz_factor, len(filtered_df))
    )

    # Plotting
    plt.figure(figsize=(12, 8))

    # Plot a separate line for each deposit range
    sns.lineplot(
        data=filtered_df,
        x='Tenure_fuzzed',
        y='Rate_fuzzed',
        hue='Deposit_Range',
        style='Deposit_Range',
        markers=True,
        dashes=False,
        palette='tab10'
    )

    # Customizing the plot
    plt.title(f'Rate (% p.a.) vs Tenure for {product_provider}', fontsize=16)
    plt.xlabel('Tenure (Months)', fontsize=14)
    plt.ylabel('Rate (% p.a.)', fontsize=14)
    plt.legend(title='Deposit Range', fontsize=12, title_fontsize=14, loc='best')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    # Show the plot
    plt.show()