def calculate_dollar_return(investment, rate, tenure):
    """
    Calculate the dollar return from an investment based on its rate of return 
    and the tenure (in months).

    Parameters:
        investment (float): The initial amount invested in dollars.
        rate (float): The annual rate of return in percentage (%).
        tenure (int): The investment tenure in months.

    Returns:
        float: The dollar return from the investment after the given tenure.

    Raises:
        ValueError: If investment or rate is negative, or tenure is non-positive (zero or negative).
    """
    if investment < 0 or rate < 0 or tenure <= 0:
        raise ValueError("Investment and rate must be more than or equal zero. Tenure must be more than zero.")

    total_percentage_return = (1 + rate / 100) ** (tenure / 12) - 1
    dollar_return = investment * total_percentage_return
    return round(dollar_return, 2)

def calculate_per_annum_rate(total_percentage_return, tenure):
    """
    Calculate the equivalent annual rate of return (in percentage) based on 
    a given total percentage return over a specific tenure (in months).

    Parameters:
        total_percentage_return (float): The total percentage return over the entire investment period.
        tenure (int): The tenure of the investment in months.

    Returns:
        float: The annualized rate of return (in percentage).

    Raises:
        ValueError: If tenure is not positive.
    """
    if tenure <= 0:
        raise ValueError("Tenure must be a positive value.")
    
    per_annum_rate = ((total_percentage_return / 100 + 1) ** (12 / tenure) - 1) * 100
    return round(per_annum_rate, 2)