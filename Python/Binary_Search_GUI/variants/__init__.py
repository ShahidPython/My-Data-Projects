from .core import (
    first_occurrence,
    last_occurrence, 
    lower_bound,
    upper_bound,
    sqrt_binary,
    count_occurrences,
    find_rotation_point,
    search_rotated_array
)

from .cli import run_cli
from .gui import run_gui

__version__ = "1.0.0"
__author__ = "Binary Search Project"
__all__ = [
    'first_occurrence',
    'last_occurrence',
    'lower_bound', 
    'upper_bound',
    'sqrt_binary',
    'count_occurrences',
    'find_rotation_point',
    'search_rotated_array',
    'run_cli',
    'run_gui'
]