import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import tkinter.font as tkfont
from odd_even_checker.core import classify, check_range


class OddEvenCheckerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🔢 Odd or Even Checker")
        self.root.geometry("500x500")
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f0f0")
        
        # Set application icon (if available)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        self.setup_styles()
        self.create_widgets()
        
    def setup_styles(self):
        """Configure widget styles."""
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("Title.TLabel", 
                            background="#f0f0f0", 
                            foreground="#2c3e50",
                            font=("Arial", 16, "bold"))
        
        self.style.configure("Accent.TButton",
                            background="#3498db",
                            foreground="white",
                            font=("Arial", 10, "bold"))
        
        self.bold_font = tkfont.Font(family="Arial", size=12, weight="bold")
        self.normal_font = tkfont.Font(family="Arial", size=10)
        
    def create_widgets(self):
        """Create and arrange GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, 
                               text="🔢 Odd or Even Checker", 
                               style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Single number tab
        self.single_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.single_frame, text="Single Number")
        
        # Range tab
        self.range_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.range_frame, text="Number Range")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        self.setup_single_tab()
        self.setup_range_tab()
        
    def setup_single_tab(self):
        """Setup the single number tab."""
        # Input frame
        input_frame = ttk.Frame(self.single_frame)
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(input_frame, text="Enter a number:", 
                 font=self.normal_font).grid(row=0, column=0, sticky=tk.W)
        
        self.number_var = tk.StringVar()
        self.number_entry = ttk.Entry(input_frame, 
                                     textvariable=self.number_var,
                                     font=self.normal_font,
                                     width=20)
        self.number_entry.grid(row=0, column=1, padx=(10, 0))
        self.number_entry.bind('<Return>', lambda e: self.check_single_number())
        
        # Button
        ttk.Button(input_frame, 
                  text="Check", 
                  style="Accent.TButton",
                  command=self.check_single_number).grid(row=0, column=2, padx=(10, 0))
        
        # Result display
        self.result_var = tk.StringVar()
        self.result_var.set("Result will appear here")
        result_label = ttk.Label(self.single_frame, 
                                textvariable=self.result_var,
                                font=self.bold_font,
                                foreground="#2c3e50")
        result_label.grid(row=1, column=0, pady=20)
        
        # Configure grid
        input_frame.columnconfigure(1, weight=1)
        
    def setup_range_tab(self):
        """Setup the number range tab."""
        # Range input frame
        range_input_frame = ttk.Frame(self.range_frame)
        range_input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(range_input_frame, text="From:", 
                 font=self.normal_font).grid(row=0, column=0, sticky=tk.W)
        
        self.range_start_var = tk.StringVar()
        range_start_entry = ttk.Entry(range_input_frame, 
                                     textvariable=self.range_start_var,
                                     font=self.normal_font,
                                     width=10)
        range_start_entry.grid(row=0, column=1, padx=(5, 10))
        
        ttk.Label(range_input_frame, text="To:", 
                 font=self.normal_font).grid(row=0, column=2, sticky=tk.W)
        
        self.range_end_var = tk.StringVar()
        range_end_entry = ttk.Entry(range_input_frame, 
                                   textvariable=self.range_end_var,
                                   font=self.normal_font,
                                   width=10)
        range_end_entry.grid(row=0, column=3, padx=(5, 0))
        
        # Button
        ttk.Button(range_input_frame, 
                  text="Check Range", 
                  style="Accent.TButton",
                  command=self.check_range).grid(row=0, column=4, padx=(10, 0))
        
        # Results text area
        ttk.Label(self.range_frame, text="Results:", 
                 font=self.normal_font).grid(row=1, column=0, sticky=tk.W, pady=(10, 5))
        
        self.results_text = scrolledtext.ScrolledText(self.range_frame,
                                                     width=50,
                                                     height=15,
                                                     font=("Consolas", 10))
        self.results_text.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.results_text.config(state=tk.DISABLED)
        
        # Configure grid
        self.range_frame.columnconfigure(0, weight=1)
        self.range_frame.rowconfigure(2, weight=1)
        range_input_frame.columnconfigure(3, weight=1)
        
    def check_single_number(self):
        """Check if a single number is odd or even."""
        try:
            number = int(self.number_var.get())
            result = classify(number)
            
            # Update result with color coding
            color = "#27ae60" if result == "even" else "#e74c3c"
            self.result_var.set(f"{number} is {result}.")
            
            # Find the result label and update its color
            for child in self.single_frame.winfo_children():
                if isinstance(child, ttk.Label) and child.cget("textvariable") == self.result_var._name:
                    child.configure(foreground=color)
                    break
                    
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer.")
            self.number_entry.focus()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
    def check_range(self):
        """Check a range of numbers."""
        try:
            start = int(self.range_start_var.get())
            end = int(self.range_end_var.get())
            
            results = check_range(start, end)
            
            # Display results in the text widget
            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete(1.0, tk.END)
            
            for num, classification in results.items():
                color_tag = "even" if classification == "even" else "odd"
                self.results_text.tag_config(color_tag, 
                                            foreground="#27ae60" if classification == "even" else "#e74c3c")
                
                self.results_text.insert(tk.END, f"{num:>6} : ", "normal")
                self.results_text.insert(tk.END, f"{classification}\n", color_tag)
                
            self.results_text.config(state=tk.DISABLED)
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid integers for the range.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


def main():
    """Main GUI entry point."""
    root = tk.Tk()
    app = OddEvenCheckerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()