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

def better_allocation(df, investment_amount, tenure):
    """
    Returns a better strategy to improve effective rate by allocating investment across 
    different products. 
    
    Strategy:
    1. First sorts all available products by interest rate in descending order
    2. For each provider-product pair, only allows investment in one deposit range 
       (the one with highest rate that we can afford given remaining funds)
    3. Allocates maximum possible amount to each product while respecting:
       - Deposit range bounds (lower and upper limits)
       - Required multiples (if any)
       - Available remaining investment amount
    4. Continues allocation until either:
       - The entire investment amount is allocated, or
       - No more valid products are available

    Note that while this strategy often produces returns at least as good as 
    investing in any single product, it may sometimes produce lower returns,
    and may also be different from the globally optimal allocation. For example,
    consider the case where we 'use up' a provider-product pair by allocating 
    the full amount to a low deposit range with high rates, and because of that
    forfeit the ability to invest in the same provider-product at a higher deposit
    range but a slightly lower rate. The overall return may be higher by allocating
    more to a slightly lower rate deposit range.

    Parameters:
        df (pd.DataFrame): DataFrame containing 'Tenure', 'Rate', 'Deposit lower bound', 
                            'Deposit upper bound', 'Product provider', 'Product'.
        investment_amount (float): The total investment amount to allocate across different products.
        tenure (int): The tenure in months for the investment.

    Returns:
        pd.DataFrame: A DataFrame containing:

            - Product provider: Provider offering the product
            - Product: Type of investment product
            - Allocated amount: Amount invested in this product
            - Rate (% p.a.): Annual interest rate as percentage
            - Expected return ($): Expected dollar return from this allocation
            Plus a summary row with totals and effective overall rate
    """
    
    # Filter rows by the investment amount and the given tenure
    filtered_df = df[
        (df['Deposit lower bound'] <= investment_amount) & 
        (df['Tenure'] == tenure)
    ]

    # Raise an exception if no valid rows remain after filtering
    if filtered_df.empty:
        raise ValueError(f"No data available for the investment amount of {investment_amount} and tenure of {tenure} months.")
    
    # Sort products by rate in descending order (highest rate first)
    filtered_df = filtered_df.sort_values(by='Rate', ascending=False)

    remaining_amount = investment_amount
    allocations = []
    total_return = 0
    used_provider_products = set()  # Track which provider-product pairs we've used

    # Allocate the investment to the products
    for _, product in filtered_df.iterrows():
        # Check how much we can allocate to this product
        if remaining_amount <= 0:
            break

        # Create unique identifier for provider-product pair
        provider_product = (product['Product provider'], product['Product'])
        
        # Skip if we've already allocated to this provider-product pair
        if provider_product in used_provider_products:
            continue

        max_allocatable = min(
            product['Deposit upper bound'],
            remaining_amount
        )
        
        # If we can't meet the minimum deposit, skip this product
        if max_allocatable < product['Deposit lower bound']:
            continue

        # Calculate the allocation
        allocation = max_allocatable

        # Handle required multiples if they exist
        if pd.notna(product['Required multiples']) and product['Required multiples'] > 0:
            # Calculate maximum number of multiples we can allocate
            num_multiples = int(allocation // product['Required multiples'])
            allocation = num_multiples * product['Required multiples']
            
            # If we can't meet even one multiple, skip this product
            if allocation < product['Required multiples']:
                continue
        
        # Calculate return for this allocation
        product_return = equations.calculate_dollar_return(allocation, product['Rate'], tenure)
        
        # Track the allocation
        allocations.append({
            'Product provider': product['Product provider'],
            'Product': product['Product'],
            'Allocated amount': allocation,
            'Rate (% p.a.)': product['Rate'],
            'Expected return ($)': product_return
        })

        # Mark this provider-product pair as used
        used_provider_products.add(provider_product)
        
        # Deduct the allocated amount and update total return
        remaining_amount -= allocation
        total_return += product_return

    # If we have allocations, calculate summary statistics
    if allocations:
        # Calculate per annum rate
        total_percentage_return = (total_return / investment_amount) * 100
        per_annum_rate = equations.calculate_per_annum_rate(total_percentage_return, tenure)
        
        # Convert allocations to a DataFrame
        allocation_df = pd.DataFrame(allocations)

        # Add total summary row
        summary_row = pd.DataFrame([{
            'Product provider': 'Total',
            'Product': 'All Products',
            'Allocated amount': investment_amount - remaining_amount,
            'Rate (% p.a.)': per_annum_rate,
            'Expected return ($)': total_return
        }])

        allocation_df = pd.concat([allocation_df, summary_row], ignore_index=True)
        
        return allocation_df
    else:
        raise ValueError("Could not find any valid allocations with the given constraints.")

def plot_better_allocation_strategy(df, investment_amount, min_tenure=0, max_tenure=999):
    """
    Plot the Rate (% p.a.) against Tenure (Months) for the better allocation strategy 
    across all tenures available in the dataframe.

    Parameters:
        df (pd.DataFrame): DataFrame containing 'Tenure', 'Rate', 'Deposit lower bound', 
                            'Deposit upper bound', 'Product provider', 'Product'.
        investment_amount (float): The total investment amount to allocate across different products.
        min_tenure (int, optional): The minimum tenure (in months) to include. Default is 0.
        max_tenure (int, optional): The maximum tenure (in months) to include. Default is 999.
    """
    # Extract all unique tenures from the dataframe and sort them
    tenures = sorted(df['Tenure'].unique())
    tenures = [t for t in tenures if min_tenure <= t <= max_tenure]
    rates = []

    for tenure in tenures:
        try:
            # Get a better allocation for the given tenure
            allocation_df = better_allocation(df, investment_amount, tenure)
            # Extract the total Rate (% p.a.) from the summary row
            total_rate = allocation_df.loc[allocation_df['Product provider'] == 'Total', 'Rate (% p.a.)'].values[0]
            rates.append(total_rate)
        except ValueError:
            # Append NaN if no valid data for the tenure
            rates.append(None)

    # Plot the results
    plt.figure(figsize=(10, 6))
    plt.plot(tenures, rates, marker='o', linestyle='-', color='blue', label='Effective Rate (% p.a.)')
    plt.title('Better Allocation Strategy: Rate (% p.a.) vs. Tenure (Months)', fontsize=16)
    plt.xlabel('Tenure (Months)', fontsize=12)
    plt.ylabel('Rate (% p.a.)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(tenures, rotation=45)
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.show()

def plot_pure_and_better_allocation_strategy_rates(df, investment_amount, min_tenure=0, max_tenure=999):
    """
    Overlay plot for best rates (% p.a.) and effective better allocation strategy rates for each tenure.

    Parameters:
        df (pd.DataFrame): DataFrame containing 'Tenure', 'Rate', 'Deposit lower bound', 
                            'Deposit upper bound', 'Product provider', 'Product'.
        investment_amount (float): The investment amount to filter available rates and products.
        min_tenure (int, optional): The minimum tenure (in months) to include. Default is 0.
        max_tenure (int, optional): The maximum tenure (in months) to include. Default is 999.
    """
    # Get best rates DataFrame
    best_rates_df = best_rates(df, investment_amount, min_tenure, max_tenure)
    
    # Combine 'Product provider' and 'Product' for unique identification
    best_rates_df['Provider-Product'] = best_rates_df['Product provider'] + " - " + best_rates_df['Product']
    
    # Extract tenures for the better allocation strategy and filter by min/max tenure
    tenures = sorted(df['Tenure'].unique())
    tenures = [t for t in tenures if min_tenure <= t <= max_tenure]
    
    # Calculate rates for better allocation strategy
    better_allocation_rates = []
    for tenure in tenures:
        try:
            allocation_df = better_allocation(df, investment_amount, tenure)
            total_rate = allocation_df.loc[allocation_df['Product provider'] == 'Total', 'Rate (% p.a.)'].values[0]
            better_allocation_rates.append(total_rate)
        except ValueError:
            better_allocation_rates.append(None)
    
    # Create the combined plot
    plt.figure(figsize=(12, 8))
    
    # Plot the best individual rates
    sns.scatterplot(
        data=best_rates_df,
        x='Tenure',
        y='Rate',
        hue='Provider-Product',
        palette='tab10',
        s=100,
        edgecolor='black'
    )
    plt.plot(best_rates_df['Tenure'], best_rates_df['Rate'], 
             linestyle='-', color='black', linewidth=2, alpha=0.4, label='Best Individual Rates (Line)')
    
    # Plot the better allocation strategy rates as a continuous line
    plt.plot(tenures, better_allocation_rates, 
             linestyle='-', color='blue', marker='o', alpha=0.4, label='Better Allocation Strategy Rates', linewidth=2)
    
    # Add labels, legend, and grid
    plt.title("Comparison of Best Individual Rates and Better Allocation Strategy Rates", fontsize=16)
    plt.xlabel("Tenure (Months)", fontsize=14)
    plt.ylabel("Rate (% p.a.)", fontsize=14)
    plt.grid(alpha=0.3)
    plt.legend(fontsize=12, bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    # Show the plot
    plt.show()