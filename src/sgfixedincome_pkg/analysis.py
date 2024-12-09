import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import equations


def best_rates(combined_df, investment_amount, min_tenure=0, max_tenure=999):
    """
    Calculate the best yield and total return for each possible tenure,
    considering that the offered rates and available products differ across 
    invested amounts.

    Parameters:
    - combined_df (pd.DataFrame): DataFrame containing columns 'Tenure', 'Rate', 'Deposit lower bound', 
                                   'Deposit upper bound', 'Required multiples', 'Product provider', 'Product'.
    - investment_amount (float): The investment amount to filter available rates and products for that amount and
                                 to calculate the total return.
    - min_tenure (int, optional): The minimum tenure (in months) to consider. Default is 0.
    - max_tenure (int, optional): The maximum tenure (in months) to consider. Default is 999.

    Returns:
    - pd.DataFrame: A DataFrame with the best rate (in % p.a.) and total return (in dollars) for each tenure.
    """
    # Filter rows where the investment_amount and Tenure is within the allowed bounds
    valid_inv_df = combined_df[
        (combined_df['Deposit lower bound'] <= investment_amount) & 
        (combined_df['Deposit upper bound'] >= investment_amount) &
        (combined_df['Tenure'] >= min_tenure) & 
        (combined_df['Tenure'] <= max_tenure)
    ]
    
    # If no valid rows remain after filtering, raise an exception
    if valid_inv_df.empty:
        raise ValueError(f"Cannot find valid products for an investment amount of {investment_amount}.")

    # Calculate the total dollar return for each row
    total_return = equations.calculate_dollar_return(
        investment_amount, 
        valid_inv_df['Rate'], 
        valid_inv_df['Tenure']
        )
    valid_inv_df['Total Dollar Return'] = round(total_return, 2)

    # Group by tenure and get the row with the maximum total return for each tenure
    best_rates_df = valid_inv_df.loc[valid_inv_df.groupby('Tenure')['Total Dollar Return'].idxmax()]
    best_rates_df = best_rates_df.sort_values(by='Tenure') # Sort by tenure

    return best_rates_df.reset_index(drop=True)

def filter_df(combined_df, investment_amount=None, min_tenure=0, max_tenure=999, 
              min_rate=None, consider_tbills=True, consider_ssbs=True, consider_fd=True, 
              include_providers=None, exclude_providers=None):
    """
    Filters the combined_df based on provided criteria, including investment amount, tenure, rate, 
    product provider, product, and whether to consider T-bills and SSBs.

    Parameters:
    - combined_df (pd.DataFrame): DataFrame containing columns 'Tenure', 'Rate', 'Deposit lower bound', 
                                   'Deposit upper bound', 'Required multiples', 'Product provider', 'Product'.
    - investment_amount (float, optional): The investment amount to filter available rates and products for that amount.
    - min_tenure (int, optional): The minimum tenure (in months) to filter. Default is 0.
    - max_tenure (int, optional): The maximum tenure (in months) to filter. Default is 999.
    - min_rate (float, optional): The minimum rate (% p.a.) to filter. Default is None (no filtering).
    - consider_tbills (bool, optional): Whether to consider T-bills. Default is True.
    - consider_ssbs (bool, optional): Whether to consider SSBs. Default is True.
    - consider_fd (bool, optional): Whether to consider fixed deposits. Default is True.
    - include_providers (list, optional): Exclusive list of providers to include. Default is None.
    - exclude_providers (list, optional): List of providers to exclude. Default is None.

    Returns:
    - pd.DataFrame: The filtered DataFrame based on the provided criteria.
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

def products(combined_df):
    """
    Returns a list of unique products in the dataset by joining the 'Product provider' and 'Product' columns.
    It considers unique combinations of these joined strings.

    Parameters:
    - combined_df (pd.DataFrame): DataFrame containing the columns 'Product provider' and 'Product'.

    Returns:
    - list: A list of unique product combinations in the format 'Product provider - Product'.
    """
    # Combine 'Product provider' and 'Product' into a single string for each row
    combined_df['Product Combination'] = combined_df['Product provider'] + ' - ' + combined_df['Product']
    
    # Get the unique combinations and return them as a list
    unique_products = combined_df['Product Combination'].unique().tolist()

    return unique_products

def plot_rates_vs_tenure(df, investment_amount, min_tenure=0, max_tenure=999):
    """
    Plots a graph of Rate (% p.a.) vs Tenure (in months) for a given investment amount
    with optional filtering by tenure range. Each unique 'Product provider - Product' 
    pair is plotted as a separate line.

    Parameters:
    - df (pd.DataFrame): DataFrame containing the data to plot. Must include columns:
                         'Tenure', 'Rate', 'Deposit lower bound', 'Deposit upper bound', 
                         'Product provider', 'Product'.
    - investment_amount (float): The investment amount to filter rows for the plot.
    - min_tenure (int, optional): Minimum tenure (in months) to include. Default is 0.
    - max_tenure (int or float, optional): Maximum tenure (in months) to include. Default is 999.

    Raises:
    - ValueError: If no valid rows remain after filtering based on the investment amount and tenure.
    """
    # Filter rows by investment amount and tenure range
    filtered_df = df[
        (df['Deposit lower bound'] <= investment_amount) &
        (df['Deposit upper bound'] >= investment_amount) &
        (df['Tenure'] >= min_tenure) &
        (df['Tenure'] <= max_tenure)
    ]

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

def plot_best_rates(combined_df, investment_amount, min_tenure=0, max_tenure=999):
    """
    Plot of best rates (% p.a.) for each tenure for a given investment amount, across
    available products. The plot color-codes the points by provider-product pair.

    Parameters:
    - combined_df (pd.DataFrame): DataFrame containing columns 'Tenure', 'Rate', 'Deposit lower bound', 
                                   'Deposit upper bound', 'Required multiples', 'Product provider', 'Product'.
    - investment_amount (float): The investment amount to filter available rates and products for that amount and
                                 to calculate the total return.
    - min_tenure (int, optional): The minimum tenure (in months) to consider. Default is 0.
    - max_tenure (int, optional): The maximum tenure (in months) to consider. Default is 999.
    """
    # Get best rates DataFrame
    best_rates_df = best_rates(combined_df, investment_amount, min_tenure, max_tenure)
    
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
    - df (pd.DataFrame): DataFrame containing columns 'Tenure', 'Rate', 'Deposit lower bound', 
                         'Deposit upper bound', 'Product provider'.
    - product_provider (str): The bank name (Product provider) to filter the data for.
    - fuzz_factor (float, optional): The amount of fuzz (random noise) to add to the points. Default is 0.02.

    Raises:
    - ValueError: If no data is available for the given product_provider.
    """
    # Filter rows for the specified product provider
    filtered_df = df[df['Product provider'] == product_provider]

    # Raise an exception if no valid rows remain after filtering
    if filtered_df.empty:
        raise ValueError(f"No data available for the product provider {product_provider}.")

    # Create a unique identifier for each deposit range (Deposit lower bound - Deposit upper bound)
    filtered_df['Deposit Range'] = filtered_df['Deposit lower bound'].astype(str) + '-' + filtered_df['Deposit upper bound'].astype(str)

    # Adding small random fuzz to the 'Tenure' and 'Rate' columns
    filtered_df['Tenure (fuzzed)'] = filtered_df['Tenure'] + np.random.uniform(-fuzz_factor, fuzz_factor, len(filtered_df))
    filtered_df['Rate (fuzzed)'] = filtered_df['Rate'] + np.random.uniform(-fuzz_factor, fuzz_factor, len(filtered_df))

    # Plotting
    plt.figure(figsize=(12, 8))

    # Plot a separate line for each deposit range
    sns.lineplot(
        data=filtered_df,
        x='Tenure (fuzzed)',
        y='Rate (fuzzed)',
        hue='Deposit Range',
        style='Deposit Range',
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

def best_mixed_strategy(df, investment_amount, tenure):
    """
    Returns the best strategy to maximize effective rate by allocating investment across 
    different products. Allocates the investment first to products with the highest rates 
    and within each product's deposit range. Continues allocation to the next product with 
    the highest rate until the entire investment is allocated.

    Parameters:
    - df (pd.DataFrame): DataFrame containing 'Tenure', 'Rate', 'Deposit lower bound', 
                         'Deposit upper bound', 'Product provider', 'Product'.
    - investment_amount (float): The total investment amount to allocate across different products.
    - tenure (int): The tenure in months for the investment.

    Returns:
    - pd.DataFrame: A DataFrame containing the investment allocation for each product,
                    total expected dollar return, and annualized percentage return.
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

    # Allocate the investment to the products
    for _, product in filtered_df.iterrows():
        # Check how much we can allocate to this product
        if remaining_amount <= 0:
            break

        max_allocatable = product['Deposit upper bound']
        
        if remaining_amount > max_allocatable:
            allocation = max_allocatable
        else:
            allocation = remaining_amount
        
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
        
        # Deduct the allocated amount and update total return
        remaining_amount -= allocation
        total_return += product_return

    # Calculate per annum rate
    total_percentage_return = (total_return / investment_amount) * 100
    per_annum_rate = equations.calculate_per_annum_rate(total_percentage_return, tenure)
    
    # Convert allocations to a DataFrame
    allocation_df = pd.DataFrame(allocations)

    # Add total summary row to the allocation DataFrame using pd.concat()
    summary_row = pd.DataFrame([{
        'Product provider': 'Total',
        'Product': 'All Products',
        'Allocated amount': investment_amount,
        'Rate (% p.a.)': per_annum_rate,
        'Expected return ($)': total_return
    }])

    allocation_df = pd.concat([allocation_df, summary_row], ignore_index=True)

    return allocation_df

def plot_best_mixed_strategy(df, investment_amount, min_tenure=0, max_tenure=999):
    """
    Plot the Rate (% p.a.) against Tenure (Months) for the best mixed strategy 
    across all tenures available in the dataframe.

    Parameters:
    - df (pd.DataFrame): DataFrame containing 'Tenure', 'Rate', 'Deposit lower bound', 
                         'Deposit upper bound', 'Product provider', 'Product'.
    - investment_amount (float): The total investment amount to allocate across different products.
    - min_tenure (int, optional): The minimum tenure (in months) to include. Default is 0.
    - max_tenure (int, optional): The maximum tenure (in months) to include. Default is 999.
    """
    # Extract all unique tenures from the dataframe and sort them
    tenures = sorted(df['Tenure'].unique())
    tenures = [t for t in tenures if min_tenure <= t <= max_tenure]
    rates = []

    for tenure in tenures:
        try:
            # Get the best mixed strategy for the given tenure
            allocation_df = best_mixed_strategy(df, investment_amount, tenure)
            # Extract the total Rate (% p.a.) from the summary row
            total_rate = allocation_df.loc[allocation_df['Product provider'] == 'Total', 'Rate (% p.a.)'].values[0]
            rates.append(total_rate)
        except ValueError:
            # Append NaN if no valid data for the tenure
            rates.append(None)

    # Plot the results
    plt.figure(figsize=(10, 6))
    plt.plot(tenures, rates, marker='o', linestyle='-', color='blue', label='Effective Rate (% p.a.)')
    plt.title('Best Mixed Strategy: Rate (% p.a.) vs. Tenure (Months)', fontsize=16)
    plt.xlabel('Tenure (Months)', fontsize=12)
    plt.ylabel('Rate (% p.a.)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(tenures, rotation=45)
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.show()

def plot_pure_and_mixed_strategy_rates(df, investment_amount, min_tenure=0, max_tenure=999):
    """
    Overlay plot for best rates (% p.a.) and effective mixed strategy rates for each tenure.

    Parameters:
    - df (pd.DataFrame): DataFrame containing 'Tenure', 'Rate', 'Deposit lower bound', 
                         'Deposit upper bound', 'Product provider', 'Product'.
    - investment_amount (float): The investment amount to filter available rates and products.
    - min_tenure (int, optional): The minimum tenure (in months) to include. Default is 0.
    - max_tenure (int, optional): The maximum tenure (in months) to include. Default is 999.
    """
    # Get best rates DataFrame
    best_rates_df = best_rates(df, investment_amount, min_tenure, max_tenure)
    
    # Combine 'Product provider' and 'Product' for unique identification
    best_rates_df['Provider-Product'] = best_rates_df['Product provider'] + " - " + best_rates_df['Product']
    
    # Extract tenures for the mixed strategy and filter by min/max tenure
    tenures = sorted(df['Tenure'].unique())
    tenures = [t for t in tenures if min_tenure <= t <= max_tenure]
    
    # Calculate rates for mixed strategy
    mixed_rates = []
    for tenure in tenures:
        try:
            allocation_df = best_mixed_strategy(df, investment_amount, tenure)
            total_rate = allocation_df.loc[allocation_df['Product provider'] == 'Total', 'Rate (% p.a.)'].values[0]
            mixed_rates.append(total_rate)
        except ValueError:
            mixed_rates.append(None)
    
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
    
    # Plot the mixed strategy rates as a continuous line
    plt.plot(tenures, mixed_rates, 
             linestyle='-', color='blue', marker='o', alpha=0.4, label='Mixed Strategy Rates', linewidth=2)
    
    # Add labels, legend, and grid
    plt.title("Comparison of Best Individual Rates and Mixed Strategy Rates", fontsize=16)
    plt.xlabel("Tenure (Months)", fontsize=14)
    plt.ylabel("Rate (% p.a.)", fontsize=14)
    plt.grid(alpha=0.3)
    plt.legend(fontsize=12, bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    # Show the plot
    plt.show()