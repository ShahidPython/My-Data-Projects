import pytest
from odd_even_checker.core import is_even, classify, check_range


class TestIsEven:
    """Test is_even function."""
    
    def test_even_numbers(self):
        """Test that even numbers return True."""
        assert is_even(2) is True
        assert is_even(0) is True
        assert is_even(-4) is True
        assert is_even(100) is True
        
    def test_odd_numbers(self):
        """Test that odd numbers return False."""
        assert is_even(1) is False
        assert is_even(-3) is False
        assert is_even(99) is False
        
    def test_invalid_input(self):
        """Test that non-integers raise TypeError."""
        with pytest.raises(TypeError):
            is_even("not a number")
        with pytest.raises(TypeError):
            is_even(3.14)
        with pytest.raises(TypeError):
            is_even([1, 2, 3])


class TestClassify:
    """Test classify function."""
    
    def test_even_classification(self):
        """Test that even numbers are classified correctly."""
        assert classify(10) == "even"
        assert classify(0) == "even"
        assert classify(-6) == "even"
        
    def test_odd_classification(self):
        """Test that odd numbers are classified correctly."""
        assert classify(7) == "odd"
        assert classify(-3) == "odd"
        assert classify(101) == "odd"
        
    def test_invalid_input(self):
        """Test that non-integers raise TypeError."""
        with pytest.raises(TypeError):
            classify("not a number")


class TestCheckRange:
    """Test check_range function."""
    
    def test_positive_range(self):
        """Test range with positive numbers."""
        result = check_range(1, 5)
        expected = {1: "odd", 2: "even", 3: "odd", 4: "even", 5: "odd"}
        assert result == expected
        
    def test_negative_range(self):
        """Test range with negative numbers."""
        result = check_range(-3, -1)
        expected = {-3: "odd", -2: "even", -1: "odd"}
        assert result == expected
        
    def test_mixed_range(self):
        """Test range with both negative and positive numbers."""
        result = check_range(-2, 2)
        expected = {-2: "even", -1: "odd", 0: "even", 1: "odd", 2: "even"}
        assert result == expected
        
    def test_reversed_range(self):
        """Test that range works when start > end."""
        result = check_range(5, 1)
        expected = {1: "odd", 2: "even", 3: "odd", 4: "even", 5: "odd"}
        assert result == expected
        
    def test_single_number_range(self):
        """Test range with same start and end."""
        result = check_range(7, 7)
        expected = {7: "odd"}
        assert result == expected