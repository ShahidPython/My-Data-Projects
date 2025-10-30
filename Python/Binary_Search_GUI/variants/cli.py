"""
Command Line Interface for Advanced Binary Search
"""
import sys
import time
from simple_chalk import chalk
from pyfiglet import Figlet
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

def print_header(title):
    """Print a formatted header with styling"""
    f = Figlet(font='small')
    print("\n" + chalk.blue("═" * 60))
    print(chalk.green(f.renderText(title)))
    print(chalk.blue("═" * 60))

def print_result(label, value, success=True):
    """Print a formatted result with coloring"""
    if success:
        print(f"{chalk.green('✅')} {chalk.bold(label):<25}: {chalk.cyan(value)}")
    else:
        print(f"{chalk.red('❌')} {chalk.bold(label):<25}: {chalk.red(value)}")

def print_warning(message):
    """Print a warning message"""
    print(f"{chalk.yellow('⚠️')} {chalk.yellow(message)}")

def print_option(key, description):
    """Print a menu option with styling"""
    print(f"   {chalk.green(key+'.')} {description}")

def validate_sorted_array(arr):
    """Check if array is sorted"""
    return all(arr[i] <= arr[i+1] for i in range(len(arr)-1))

def animate_processing():
    """Show processing animation"""
    print(f"\n{chalk.yellow('Processing')}", end="", flush=True)
    for i in range(3):
        time.sleep(0.3)
        print(f"{chalk.yellow('.')}", end="", flush=True)
    print()

def ask_to_sort_array(arr):
    """Ask user if they want to sort the array"""
    print(f"\n{chalk.yellow('⚠️  The array you entered is not sorted.')}")
    print(f"{chalk.yellow('   Binary search algorithms require sorted arrays for accurate results.')}")
    print(f"\nOriginal array: {arr}")
    print(f"Sorted array: {sorted(arr)}")
    
    while True:
        response = input(f"\n{chalk.magenta('➤ Would you like to sort it? (y/n): ')}").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print(f"{chalk.red('❌ Please enter y or n.')}")

def run_cli():
    """Run the CLI interface with enhanced UX"""
    options = {
        "1": "First Occurrence",
        "2": "Last Occurrence",
        "3": "Lower Bound",
        "4": "Upper Bound",
        "5": "Count Occurrences",
        "6": "Square Root",
        "7": "Find Rotation Point",
        "8": "Search Rotated Array",
        "9": "Back to Main Menu"
    }
    
    while True:
        print_header("CLI SEARCH")
        
        print(f"{chalk.blue('╔══════════════════════════════════════════════════════╗')}")
        print(f"{chalk.blue('║')}               {chalk.bold('SEARCH OPTIONS')}                         {chalk.blue('║')}")
        print(f"{chalk.blue('╠══════════════════════════════════════════════════════╣')}")
        
        for key, value in options.items():
            print(f"{chalk.blue('║')}  {chalk.green(key+'.')} {value:<48} {chalk.blue('║')}")
        
        print(f"{chalk.blue('╚══════════════════════════════════════════════════════╝')}")
        
        try:
            choice = input(f"\n{chalk.magenta('➤ Select an option (1-9): ')}").strip()
            
            if choice == "9":
                print(f"\n{chalk.blue('Returning to main menu...')}")
                break
            
            if choice not in options:
                print(f"\n{chalk.red('❌ Invalid option. Please try again.')}")
                continue
                
            if choice == "6":  # Square Root
                try:
                    print(f"\n{chalk.yellow('Square Root Calculation')}")
                    print(f"{chalk.yellow('──────────────────────')}")
                    n = int(input(f"{chalk.cyan('Enter a non-negative integer: ')}"))
                    if n < 0:
                        print(f"{chalk.red('❌ Please enter a non-negative integer.')}")
                        continue
                    
                    animate_processing()
                    result = sqrt_binary(n)
                    
                    print_header("RESULT")
                    print_result("Input Number", str(n))
                    print_result("Square Root (floor)", str(result))
                    print_result("Verification", f"{result}² = {result*result} ≤ {n} < {(result+1)*(result+1)}")
                    
                except ValueError:
                    print(f"{chalk.red('❌ Invalid input. Please enter an integer.')}")
                continue
            
            # For array operations
            try:
                print(f"\n{chalk.yellow('Array Input')}")
                print(f"{chalk.yellow('───────────')}")
                arr_input = input(f"{chalk.cyan('Enter numbers (space separated): ')}").strip()
                if not arr_input:
                    print(f"{chalk.red('❌ No input provided.')}")
                    continue
                    
                arr = list(map(int, arr_input.split()))
                
                # Check if array is sorted and offer to sort it
                if not validate_sorted_array(arr) and choice not in ["7", "8"]:
                    if ask_to_sort_array(arr):
                        arr.sort()
                        print(f"{chalk.green('✅ Array has been sorted.')}")
                    else:
                        print_warning("Proceeding with unsorted array. Results may be inaccurate.")
                
                if choice in ["7"]:  # Operations that don't need target
                    if choice == "7":  # Find Rotation Point
                        # Warn about unsorted arrays for rotation point
                        if not validate_sorted_array(arr):
                            print_warning("Rotation point algorithm works best on sorted arrays that have been rotated.")
                            if not input(f"{chalk.magenta('➤ Continue anyway? (y/n): ')}").strip().lower() in ['y', 'yes']:
                                continue
                        
                        animate_processing()
                        result = find_rotation_point(arr)
                        
                        print_header("RESULT")
                        print_result("Array", str(arr))
                        print_result("Rotation Point Index", str(result))
                        print_result("Value at Index", str(arr[result]))
                    continue
                
                # Operations that need target
                target = int(input(f"{chalk.cyan('Enter target value: ')}"))
                
                animate_processing()
                
                print_header("RESULT")
                print_result("Array", str(arr))
                print_result("Target", str(target))
                
                if choice == "1":  # First Occurrence
                    result = first_occurrence(arr, target)
                    if result != -1:
                        print_result("First Occurrence Index", str(result), True)
                    else:
                        print_result("First Occurrence", "Not found", False)
                        
                elif choice == "2":  # Last Occurrence
                    result = last_occurrence(arr, target)
                    if result != -1:
                        print_result("Last Occurrence Index", str(result), True)
                    else:
                        print_result("Last Occurrence", "Not found", False)
                        
                elif choice == "3":  # Lower Bound
                    result = lower_bound(arr, target)
                    if result != -1:
                        print_result("Lower Bound Index", str(result), True)
                        print_result("Value at Index", str(arr[result]), True)
                    else:
                        print_result("Lower Bound", "Not found", False)
                        
                elif choice == "4":  # Upper Bound
                    result = upper_bound(arr, target)
                    if result != -1:
                        print_result("Upper Bound Index", str(result), True)
                        print_result("Value at Index", str(arr[result]), True)
                    else:
                        print_result("Upper Bound", "Not found", False)
                        
                elif choice == "5":  # Count Occurrences
                    result = count_occurrences(arr, target)
                    print_result("Number of Occurrences", str(result), result > 0)
                    
                elif choice == "8":  # Search Rotated Array
                    # For rotated search, we don't require the array to be sorted
                    result = search_rotated_array(arr, target)
                    if result != -1:
                        print_result("Found at Index", str(result), True)
                    else:
                        print_result("Target", "Not found in array", False)
                    
            except ValueError:
                print(f"{chalk.red('❌ Invalid input. Please enter integers only.')}")
                
        except KeyboardInterrupt:
            print(f"\n\n{chalk.yellow('Operation cancelled. Returning to main menu...')}")
            break
            
        # Pause before showing menu again
        input(f"\n{chalk.blue('Press Enter to continue...')}")