"""
Extended unit tests for core palindrome functionality
"""
import pytest
from core import is_palindrome, normalize_text, explain, find_palindromic_substrings

class TestPalindromeChecker:
    # Test cases for basic palindrome functionality
    def test_true_cases(self):
        assert is_palindrome("level")
        assert is_palindrome("Never odd or even")
        assert is_palindrome("A man, a plan, a canal: Panama!")
        assert is_palindrome("12321")
        assert is_palindrome("")
        assert is_palindrome("   ")
    
    def test_false_cases(self):
        assert not is_palindrome("hello")
        assert not is_palindrome("python")
        assert not is_palindrome("12345")
    
    def test_unicode_diacritics(self):
        assert is_palindrome("Åna")  # diacritic stripped → "ana"
        assert is_palindrome("Café")  # Not a palindrome
        assert is_palindrome("Lüül")  # Should work with diacritics
    
    def test_case_insensitivity(self):
        assert is_palindrome("RaceCar")
        assert is_palindrome("MaDaM")
    
    def test_punctuation_ignored(self):
        assert is_palindrome("A man, a plan, a canal: Panama!")
        assert is_palindrome("Was it a car or a cat I saw?")
        assert is_palindrome("No 'x' in Nixon")
    
    def test_normalize_text(self):
        assert normalize_text("Nurse! I spy gypsies—run!") == "nurseispygypsiesrun"
        assert normalize_text("Hello123") == "hello123"
        assert normalize_text("Hello123", keep_digits=False) == "hello"
        assert normalize_text("Test Case", keep_case=True) == "TestCase"
        assert normalize_text("Café") == "cafe"
        assert normalize_text(None) == ""
    
    def test_explain_function(self):
        info = explain("abc")
        assert info.original == "abc"
        assert info.normalized == "abc"
        assert info.is_palindrome is False
        assert info.length == 3
        assert info.reversed == "cba"
        
        info = explain("Aba")
        assert info.normalized == "aba"
        assert info.is_palindrome is True
        assert info.reversed == "aba"
    
    def test_find_palindromic_substrings(self):
        # Test with simple palindrome
        result = find_palindromic_substrings("aba")
        assert len(result) == 2  # "a", "b", "a", "aba" but duplicates removed
        assert any("aba" in substr for _, _, substr in result)
        
        # Test with non-palindrome containing substrings
        result = find_palindromic_substrings("abacaba")
        assert len(result) > 0
        assert any("aba" in substr for _, _, substr in result)
        
        # Test with minimum length
        result = find_palindromic_substrings("abcba", min_length=4)
        assert all(len(substr) >= 4 for _, _, substr in result)
        
        # Test empty string
        result = find_palindromic_substrings("")
        assert len(result) == 0
        
        # Test string with no palindromic substrings of minimum length
        result = find_palindromic_substrings("abc", min_length=3)
        assert len(result) == 0

class TestEdgeCases:
    def test_numbers_only(self):
        assert is_palindrome("12321")
        assert not is_palindrome("12345")
    
    def test_mixed_alphanumeric(self):
        assert is_palindrome("a1b2b1a")
        assert not is_palindrome("a1b2c3d")
    
    def test_special_characters(self):
        assert is_palindrome("!@#$% %$#@!")  # Only alphanumeric matters
        assert normalize_text("!@#$%") == ""  # No alphanumeric characters
    
    def test_whitespace(self):
        assert is_palindrome("   a   b   a   ")
        assert normalize_text("   a   b   a   ") == "aba"
    
    def test_long_strings(self):
        # Test with a long palindrome
        long_palindrome = "a" * 1000
        assert is_palindrome(long_palindrome)
        
        # Test with a long non-palindrome
        long_non_palindrome = "a" * 500 + "b" + "a" * 499
        assert not is_palindrome(long_non_palindrome)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])