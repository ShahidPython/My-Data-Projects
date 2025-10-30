"""
Core implementation of advanced binary search variants
"""
from typing import List, Union

def first_occurrence(arr: List[int], target: int) -> int:
    """
    Find the first occurrence of target in sorted array.
    Returns index of first occurrence or -1 if not found.
    """
    if not arr:
        return -1
        
    left, right, ans = 0, len(arr) - 1, -1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            ans = mid
            right = mid - 1  # Continue searching left half
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return ans

def last_occurrence(arr: List[int], target: int) -> int:
    """
    Find the last occurrence of target in sorted array.
    Returns index of last occurrence or -1 if not found.
    """
    if not arr:
        return -1
        
    left, right, ans = 0, len(arr) - 1, -1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            ans = mid
            left = mid + 1  # Continue searching right half
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return ans

def lower_bound(arr: List[int], target: int) -> int:
    """
    Find the first element >= target.
    Returns index of element or -1 if not found.
    """
    if not arr:
        return -1
        
    left, right, ans = 0, len(arr) - 1, -1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] >= target:
            ans = mid
            right = mid - 1
        else:
            left = mid + 1
    return ans

def upper_bound(arr: List[int], target: int) -> int:
    """
    Find the first element > target.
    Returns index of element or -1 if not found.
    """
    if not arr:
        return -1
        
    left, right, ans = 0, len(arr) - 1, -1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] > target:
            ans = mid
            right = mid - 1
        else:
            left = mid + 1
    return ans

def sqrt_binary(n: int) -> int:
    """
    Find integer square root using binary search.
    Returns floor(sqrt(n)).
    """
    if n < 0:
        raise ValueError("Square root not defined for negative numbers")
    if n in (0, 1):
        return n
    
    left, right, ans = 1, n, -1
    while left <= right:
        mid = (left + right) // 2
        if mid * mid == n:
            return mid
        elif mid * mid < n:
            ans = mid
            left = mid + 1
        else:
            right = mid - 1
    return ans

def count_occurrences(arr: List[int], target: int) -> int:
    """
    Count occurrences of target in sorted array using binary search.
    """
    if not arr:
        return 0
        
    first = first_occurrence(arr, target)
    if first == -1:
        return 0
    last = last_occurrence(arr, target)
    return last - first + 1

def find_rotation_point(arr: List[int]) -> int:
    """
    Find the rotation point in a rotated sorted array.
    Returns index of the smallest element.
    """
    if not arr:
        return -1
        
    left, right = 0, len(arr) - 1
    
    # If array is not rotated
    if arr[left] <= arr[right]:
        return left
        
    while left < right:
        mid = (left + right) // 2
        if arr[mid] > arr[right]:
            left = mid + 1
        else:
            right = mid
    return left

def search_rotated_array(arr: List[int], target: int) -> int:
    """
    Search for target in a rotated sorted array.
    Returns index of target or -1 if not found.
    """
    if not arr:
        return -1
        
    rotation_point = find_rotation_point(arr)
    
    # Determine which segment to search
    if target >= arr[0] and rotation_point > 0:
        # Search in left segment (before rotation)
        left, right = 0, rotation_point - 1
    else:
        # Search in right segment (after rotation)
        left, right = rotation_point, len(arr) - 1
    
    # Regular binary search in the selected segment
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1