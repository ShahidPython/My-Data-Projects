def is_even(number: int) -> bool:
    """Return True if the number is even, False if odd.
    
    Args:
        number (int): The number to check
        
    Returns:
        bool: True if even, False if odd
        
    Raises:
        TypeError: If input is not an integer
    """
    if not isinstance(number, int):
        raise TypeError("Input must be an integer")
    
    return number % 2 == 0


def classify(number: int) -> str:
    """Classify the number as 'even' or 'odd'.
    
    Args:
        number (int): The number to classify
        
    Returns:
        str: 'even' or 'odd'
        
    Raises:
        TypeError: If input is not an integer
    """
    return "even" if is_even(number) else "odd"


def check_range(start: int, end: int) -> dict:
    """Check a range of numbers and return their classifications.
    
    Args:
        start (int): Starting number of the range
        end (int): Ending number of the range
        
    Returns:
        dict: Dictionary with numbers as keys and classifications as values
    """
    if start > end:
        start, end = end, start  # Swap if start is greater than end
        
    return {num: classify(num) for num in range(start, end + 1)}