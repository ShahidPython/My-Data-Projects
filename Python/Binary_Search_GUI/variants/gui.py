"""
Graphical User Interface for Advanced Binary Search using Tkinter
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import tkinter.font as tkfont
from PIL import Image, ImageTk
import sv_ttk

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

# Modern color scheme
COLORS = {
    "primary": "#3B82F6",      # Blue
    "secondary": "#10B981",    # Green
    "accent": "#F59E0B",       # Amber
    "success": "#10B981",      # Green
    "warning": "#F59E0B",      # Amber
    "error": "#EF4444",        # Red
    "bg": "#F3F4F6",           # Light gray
    "card_bg": "#FFFFFF",      # White
    "text": "#1F2937",         # Dark gray
    "text_light": "#6B7280",   # Medium gray
    "border": "#E5E7EB"        # Light border
}

# Font settings
FONTS = {
    "title": ("Segoe UI", 16, "bold"),
    "subtitle": ("Segoe UI", 11),
    "body": ("Segoe UI", 9),
    "button": ("Segoe UI", 9, "bold"),
    "result": ("Consolas", 9)
}

def run_gui():
    """Run the GUI interface with modern design"""
    root = tk.Tk()
    root.title("Advanced Binary Search")
    root.geometry("750x650")
    root.configure(bg=COLORS["bg"])
    
    # Set theme
    sv_ttk.set_theme("light")
    
    # Custom styles
    style = ttk.Style()
    style.configure('Primary.TButton', background=COLORS["primary"], foreground='black')
    style.configure('Accent.TButton', background=COLORS["accent"], foreground='black')
    style.configure('Card.TFrame', background=COLORS["card_bg"])
    style.configure('Title.TLabel', background=COLORS["bg"], foreground=COLORS["primary"], 
                   font=FONTS["title"])
    style.configure('Subtitle.TLabel', background=COLORS["bg"], foreground=COLORS["text"], 
                   font=FONTS["subtitle"])
    style.configure('Body.TLabel', background=COLORS["card_bg"], foreground=COLORS["text"], 
                   font=FONTS["body"])
    
    # Create a main frame with scrollbar
    main_frame = ttk.Frame(root, padding="15")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Create a canvas and scrollbar for the main frame
    canvas = tk.Canvas(main_frame, bg=COLORS["bg"], highlightthickness=0)
    scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Header with title
    header_frame = ttk.Frame(scrollable_frame, style='Card.TFrame', padding="10")
    header_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
    header_frame.columnconfigure(0, weight=1)
    
    title_label = ttk.Label(header_frame, text="Advanced Binary Search", style='Title.TLabel')
    title_label.grid(row=0, column=0, sticky=tk.W)
    
    subtitle_label = ttk.Label(header_frame, text="Powerful search algorithms made easy", 
                              style='Subtitle.TLabel')
    subtitle_label.grid(row=1, column=0, sticky=tk.W, pady=(2, 0))
    
    # Card for input fields
    input_card = ttk.Frame(scrollable_frame, style='Card.TFrame', padding="12")
    input_card.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
    input_card.columnconfigure(1, weight=1)
    
    ttk.Label(input_card, text="Array (space separated numbers):", 
             style='Body.TLabel').grid(row=0, column=0, sticky=tk.W, pady=4)
    array_entry = ttk.Entry(input_card, width=35, font=FONTS["body"])
    array_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=4, padx=(8, 0))
    
    ttk.Label(input_card, text="Target Value:", 
             style='Body.TLabel').grid(row=1, column=0, sticky=tk.W, pady=4)
    target_entry = ttk.Entry(input_card, width=20, font=FONTS["body"])
    target_entry.grid(row=1, column=1, sticky=tk.W, pady=4, padx=(8, 0))
    
    # Card for operation selection
    op_card = ttk.Frame(scrollable_frame, style='Card.TFrame', padding="12")
    op_card.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
    op_card.columnconfigure(0, weight=1)
    
    ttk.Label(op_card, text="Select Operation:", 
             style='Body.TLabel', font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
    
    operation = tk.StringVar(value="first")
    
    operations = [
        ("First Occurrence", "first"),
        ("Last Occurrence", "last"),
        ("Lower Bound", "lower"),
        ("Upper Bound", "upper"),
        ("Count Occurrences", "count"),
        ("Square Root", "sqrt"),
        ("Find Rotation Point", "rotation"),
        ("Search Rotated Array", "rotated_search")
    ]
    
    # Create a frame for radio buttons with two columns
    radio_frame = ttk.Frame(op_card)
    radio_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
    
    # Create radio buttons in two columns
    for i, (text, value) in enumerate(operations):
        row = i // 2
        col = i % 2
        rb = ttk.Radiobutton(radio_frame, text=text, variable=operation, value=value)
        rb.grid(row=row, column=col, sticky=tk.W, padx=(0, 15), pady=3)
    
    # Card for results
    result_card = ttk.Frame(scrollable_frame, style='Card.TFrame', padding="12")
    result_card.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
    result_card.columnconfigure(0, weight=1)
    result_card.rowconfigure(1, weight=1)
    
    ttk.Label(result_card, text="Results:", 
             style='Body.TLabel', font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
    
    result_text = scrolledtext.ScrolledText(result_card, width=55, height=10, 
                                          font=FONTS["result"], relief="flat", borderwidth=1,
                                          bg=COLORS["card_bg"], fg=COLORS["text"])
    result_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    result_text.config(state=tk.DISABLED)
    
    # Button frame
    button_frame = ttk.Frame(scrollable_frame)
    button_frame.grid(row=4, column=0, columnspan=2, pady=8)
    
    def is_sorted(arr):
        """Check if array is sorted"""
        return all(arr[i] <= arr[i+1] for i in range(len(arr)-1))
    
    def sort_array_dialog(arr):
        """Ask user if they want to sort the array"""
        response = messagebox.askyesno(
            "Unsorted Array", 
            "The array you entered is not sorted. Would you like to sort it before proceeding?\n\n" +
            f"Original: {arr}\nSorted: {sorted(arr)}"
        )
        return response
    
    def execute_search():
        """Execute the selected search operation"""
        op = operation.get()
        
        # Clear previous result
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        
        try:
            if op == "sqrt":
                n = int(target_entry.get())
                if n < 0:
                    messagebox.showerror("Error", "Square root not defined for negative numbers")
                    return
                result = sqrt_binary(n)
                result_text.insert(tk.END, f"Square Root (floor) of {n} = {result}\n\n")
                result_text.insert(tk.END, f"Verification:\n")
                result_text.insert(tk.END, f"{result}² = {result*result} ≤ {n}")
                if (result+1)*(result+1) > n:
                    result_text.insert(tk.END, f" < {(result+1)*(result+1)}")
                
            elif op == "rotation":
                arr_str = array_entry.get().strip()
                if not arr_str:
                    messagebox.showerror("Error", "Array cannot be empty")
                    return
                arr = list(map(int, arr_str.split()))
                
                # Check if array is sorted for rotation operations
                if not is_sorted(arr) and not messagebox.askyesno(
                    "Confirm", 
                    "The rotation point algorithm works best on sorted arrays that have been rotated. " +
                    "Your array doesn't appear to be sorted. Continue anyway?"
                ):
                    return
                    
                result_idx = find_rotation_point(arr)
                result_text.insert(tk.END, f"Array: {arr}\n\n")
                result_text.insert(tk.END, f"Rotation Point Index: {result_idx}\n")
                result_text.insert(tk.END, f"Value at Index: {arr[result_idx]}")
                
            else:
                # Validate array input
                arr_str = array_entry.get().strip()
                if not arr_str:
                    messagebox.showerror("Error", "Array cannot be empty")
                    return
                    
                arr = list(map(int, arr_str.split()))
                
                # Check if array is sorted and offer to sort it
                if not is_sorted(arr) and op not in ["rotated_search"]:
                    if sort_array_dialog(arr):
                        arr.sort()
                        array_entry.delete(0, tk.END)
                        array_entry.insert(0, " ".join(map(str, arr)))
                        messagebox.showinfo("Array Sorted", "Array has been sorted successfully.")
                    else:
                        messagebox.showwarning("Warning", 
                            "Binary search algorithms require sorted arrays for accurate results. " +
                            "Proceeding with unsorted array may yield incorrect results.")
                
                # Validate target for operations that need it
                if op != "rotation":
                    target_str = target_entry.get().strip()
                    if not target_str:
                        messagebox.showerror("Error", "Target value required for this operation")
                        return
                    target = int(target_str)
                
                # Execute the selected operation
                if op == "first":
                    result = first_occurrence(arr, target)
                    result_text.insert(tk.END, f"Array: {arr}\n\n")
                    if result != -1:
                        result_text.insert(tk.END, f"First occurrence of {target} at index: {result}")
                    else:
                        result_text.insert(tk.END, f"Target {target} not found in array")
                    
                elif op == "last":
                    result = last_occurrence(arr, target)
                    result_text.insert(tk.END, f"Array: {arr}\n\n")
                    if result != -1:
                        result_text.insert(tk.END, f"Last occurrence of {target} at index: {result}")
                    else:
                        result_text.insert(tk.END, f"Target {target} not found in array")
                    
                elif op == "lower":
                    result = lower_bound(arr, target)
                    result_text.insert(tk.END, f"Array: {arr}\n\n")
                    if result != -1:
                        result_text.insert(tk.END, f"Lower bound of {target} at index: {result}\n")
                        result_text.insert(tk.END, f"Value at index: {arr[result]}")
                    else:
                        result_text.insert(tk.END, f"No lower bound found for {target}")
                        
                elif op == "upper":
                    result = upper_bound(arr, target)
                    result_text.insert(tk.END, f"Array: {arr}\n\n")
                    if result != -1:
                        result_text.insert(tk.END, f"Upper bound of {target} at index: {result}\n")
                        result_text.insert(tk.END, f"Value at index: {arr[result]}")
                    else:
                        result_text.insert(tk.END, f"No upper bound found for {target}")
                        
                elif op == "count":
                    result = count_occurrences(arr, target)
                    result_text.insert(tk.END, f"Array: {arr}\n\n")
                    result_text.insert(tk.END, f"Number of occurrences of {target}: {result}")
                    
                elif op == "rotated_search":
                    # For rotated search, we don't require the array to be sorted
                    # as it's specifically designed for rotated sorted arrays
                    target = int(target_entry.get().strip())
                    result = search_rotated_array(arr, target)
                    result_text.insert(tk.END, f"Array: {arr}\n\n")
                    if result != -1:
                        result_text.insert(tk.END, f"Target {target} found at index: {result}")
                    else:
                        result_text.insert(tk.END, f"Target {target} not found in array")
        
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        
        result_text.config(state=tk.DISABLED)
    
    def clear_fields():
        """Clear all input fields and results"""
        array_entry.delete(0, tk.END)
        target_entry.delete(0, tk.END)
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.config(state=tk.DISABLED)
        operation.set("first")
    
    # Buttons with modern style and black text
    search_btn = ttk.Button(button_frame, text="Execute Search", command=execute_search, 
                           style='Primary.TButton')
    search_btn.grid(row=0, column=0, padx=4)
    
    clear_btn = ttk.Button(button_frame, text="Clear All", command=clear_fields)
    clear_btn.grid(row=0, column=1, padx=4)
    
    exit_btn = ttk.Button(button_frame, text="Exit", command=root.destroy, style='Accent.TButton')
    exit_btn.grid(row=0, column=2, padx=4)
    
    # Configure grid weights for responsive layout
    scrollable_frame.columnconfigure(0, weight=1)
    for i in range(5):
        scrollable_frame.rowconfigure(i, weight=0)
    
    # Center the window and make it responsive
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    # Bind mouse wheel to scroll for all widgets
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    root.mainloop()