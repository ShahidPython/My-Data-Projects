"""
Unit tests for advanced binary search variants
"""
import unittest
from variants.core import (
    first_occurrence, 
    last_occurrence, 
    lower_bound, 
    upper_bound, 
    sqrt_binary,
    count_occurrences,
    find_rotation_point,
    search_rotated_array
)

class TestAdvancedBinarySearch(unittest.TestCase):
    """Test class for advanced binary search functions"""
    
    def test_first_occurrence(self):
        """Test first occurrence function"""
        arr = [1, 2, 2, 2, 3, 4]
        self.assertEqual(first_occurrence(arr, 2), 1)
        self.assertEqual(first_occurrence(arr, 3), 4)
        self.assertEqual(first_occurrence(arr, 5), -1)
        self.assertEqual(first_occurrence([], 5), -1)
    
    def test_last_occurrence(self):
        """Test last occurrence function"""
        arr = [1, 2, 2, 2, 3, 4]
        self.assertEqual(last_occurrence(arr, 2), 3)
        self.assertEqual(last_occurrence(arr, 3), 4)
        self.assertEqual(last_occurrence(arr, 5), -1)
    
    def test_lower_bound(self):
        """Test lower bound function"""
        arr = [1, 2, 4, 6, 8]
        self.assertEqual(lower_bound(arr, 3), 2)  # First element >= 3 is 4 at index 2
        self.assertEqual(lower_bound(arr, 5), 3)  # First element >= 5 is 6 at index 3
        self.assertEqual(lower_bound(arr, 9), -1) # No element >= 9
        self.assertEqual(lower_bound(arr, 0), 0)  # First element >= 0 is 1 at index 0
    
    def test_upper_bound(self):
        """Test upper bound function"""
        arr = [1, 2, 4, 6, 8]
        self.assertEqual(upper_bound(arr, 3), 2)  # First element > 3 is 4 at index 2
        self.assertEqual(upper_bound(arr, 5), 3)  # First element > 5 is 6 at index 3
        self.assertEqual(upper_bound(arr, 8), -1) # No element > 8
        self.assertEqual(upper_bound(arr, 0), 0)  # First element > 0 is 1 at index 0
    
    def test_sqrt_binary(self):
        """Test square root function"""
        self.assertEqual(sqrt_binary(16), 4)
        self.assertEqual(sqrt_binary(20), 4)  # floor(sqrt(20)) = 4
        self.assertEqual(sqrt_binary(1), 1)
        self.assertEqual(sqrt_binary(0), 0)
        with self.assertRaises(ValueError):
            sqrt_binary(-5)
    
    def test_count_occurrences(self):
        """Test count occurrences function"""
        arr = [1, 2, 2, 2, 3, 4, 4, 5]
        self.assertEqual(count_occurrences(arr, 2), 3)
        self.assertEqual(count_occurrences(arr, 4), 2)
        self.assertEqual(count_occurrences(arr, 6), 0)
        self.assertEqual(count_occurrences([], 5), 0)
    
    def test_find_rotation_point(self):
        """Test find rotation point function"""
        # Test case 1: Normal rotation
        arr1 = [4, 5, 6, 7, 0, 1, 2]
        self.assertEqual(find_rotation_point(arr1), 4)
        
        # Test case 2: No rotation
        arr2 = [0, 1, 2, 3, 4, 5]
        self.assertEqual(find_rotation_point(arr2), 0)
        
        # Test case 3: Single element
        arr3 = [5]
        self.assertEqual(find_rotation_point(arr3), 0)
    
    def test_search_rotated_array(self):
        """Test search rotated array function"""
        arr = [4, 5, 6, 7, 0, 1, 2]
        
        # Test cases for elements present in array
        self.assertEqual(search_rotated_array(arr, 4), 0)
        self.assertEqual(search_rotated_array(arr, 5), 1)
        self.assertEqual(search_rotated_array(arr, 6), 2)
        self.assertEqual(search_rotated_array(arr, 7), 3)
        self.assertEqual(search_rotated_array(arr, 0), 4)
        self.assertEqual(search_rotated_array(arr, 1), 5)
        self.assertEqual(search_rotated_array(arr, 2), 6)
        
        # Test cases for elements not present
        self.assertEqual(search_rotated_array(arr, 3), -1)
        self.assertEqual(search_rotated_array(arr, 8), -1)
        
        # Test case for empty array
        self.assertEqual(search_rotated_array([], 5), -1)

if __name__ == "__main__":
    unittest.main()