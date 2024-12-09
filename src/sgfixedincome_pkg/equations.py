def calculate_dollar_return(investment, rate, tenure):
    """
    Calculate the dollar return from an investment based on its rate of return 
    and the tenure (in months).

    Parameters:
    - investment (float): The initial amount invested.
    - rate (float): The annual rate of return in percentage (%).
    - tenure (int): The investment tenure in months.

    Returns:
    - float: The dollar return from the investment after the given tenure.
    """
    total_percentage_return = (1 + rate / 100) ** (tenure / 12) - 1
    return investment * total_percentage_return

def calculate_per_annum_rate(total_percentage_return, tenure):
    """
    Calculate the equivalent annual rate of return (in percentage) based on 
    a given total percentage return over a specific tenure (in months).

    Parameters:
    - total_percentage_return (float): The total percentage return over the entire investment period.
    - tenure (int): The tenure of the investment in months.

    Returns:
    - float: The annualized rate of return (in percentage).
    """
    return ((total_percentage_return / 100 + 1) ** (12 / tenure) - 1) * 100