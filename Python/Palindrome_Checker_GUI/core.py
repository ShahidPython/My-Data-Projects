"""
Core palindrome logic with enhanced features
"""
import unicodedata
import re
from dataclasses import dataclass
from typing import List, Tuple

def _strip_diacritics(text: str) -> str:
    """Remove diacritics from text using Unicode normalization"""
    nk = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nk if not unicodedata.combining(c))

def normalize_text(text: str, keep_digits: bool = True, keep_case: bool = False) -> str:
    """
    Normalize text by removing non-alphanumeric characters and diacritics
    
    Args:
        text: Input text to normalize
        keep_digits: Whether to keep digits in the normalized text
        keep_case: Whether to preserve case (default converts to lowercase)
    
    Returns:
        Normalized text string
    """
    if text is None:
        return ""
    
    text = _strip_diacritics(text)
    out = []
    
    for ch in text:
        if ch.isalpha() or (keep_digits and ch.isdigit()):
            if keep_case:
                out.append(ch)
            else:
                out.append(ch.lower())
    
    return "".join(out)

def is_palindrome(text: str, **normalize_kwargs) -> bool:
    """
    Check if text is a palindrome
    
    Args:
        text: Text to check
        **normalize_kwargs: Additional arguments for normalize_text function
    
    Returns:
        Boolean indicating if text is a palindrome
    """
    norm = normalize_text(text, **normalize_kwargs)
    if not norm:
        return False
    return norm == norm[::-1]

def find_palindromic_substrings(text: str, min_length: int = 3) -> List[Tuple[int, int, str]]:
    """
    Find all palindromic substrings in the given text
    
    Args:
        text: Text to search for palindromic substrings
        min_length: Minimum length of substrings to consider
    
    Returns:
        List of tuples (start_index, end_index, substring)
    """
    normalized = normalize_text(text)
    results = []
    n = len(normalized)
    
    # Check all possible centers for palindromes
    for center in range(n):
        # Odd length palindromes
        left, right = center, center
        while left >= 0 and right < n and normalized[left] == normalized[right]:
            length = right - left + 1
            if length >= min_length:
                results.append((left, right + 1, normalized[left:right+1]))
            left -= 1
            right += 1
        
        # Even length palindromes
        left, right = center, center + 1
        while left >= 0 and right < n and normalized[left] == normalized[right]:
            length = right - left + 1
            if length >= min_length:
                results.append((left, right + 1, normalized[left:right+1]))
            left -= 1
            right += 1
    
    # Remove duplicates and sort by length (longest first)
    results = list(set(results))
    results.sort(key=lambda x: len(x[2]), reverse=True)
    return results

@dataclass(frozen=True)
class Explanation:
    """Detailed explanation of palindrome check results"""
    original: str
    normalized: str
    is_palindrome: bool
    length: int
    reversed: str
    substrings: List[Tuple[int, int, str]]

def explain(text: str, find_substrings: bool = False) -> Explanation:
    """
    Generate detailed explanation of palindrome check
    
    Args:
        text: Text to analyze
        find_substrings: Whether to search for palindromic substrings
    
    Returns:
        Explanation object with detailed results
    """
    norm = normalize_text(text)
    is_pal = bool(norm) and norm == norm[::-1]
    
    substrings = []
    if find_substrings and not is_pal and norm:
        substrings = find_palindromic_substrings(text)
    
    return Explanation(
        original=text,
        normalized=norm,
        is_palindrome=is_pal,
        length=len(norm),
        reversed=norm[::-1] if norm else "",
        substrings=substrings
    )