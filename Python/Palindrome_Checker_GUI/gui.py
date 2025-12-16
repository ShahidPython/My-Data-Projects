"""
Modern Tkinter GUI for palindrome checker with sleek design
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import tkinter.font as tkfont
from tkinter import PhotoImage
from core import is_palindrome, explain

class ModernPalindromeCheckerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Palindrome Checker Pro")
        self.root.geometry("800x700")
        self.root.minsize(700, 600)
        self.root.configure(bg="#2c3e50")
        
        # Set application icon (if available)
        try:
            self.root.iconbitmap("palindrome.ico")
        except:
            pass
        
        # Configure styles
        self.setup_styles()
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="20", style="Dark.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create widgets
        self.create_widgets()
        
        # Initialize history
        self.history = []
        
    def setup_styles(self):
        """Configure ttk styles for a modern dark theme"""
        style = ttk.Style()
        
        # Import ttk themes if available
        try:
            from ttkthemes import ThemedStyle
            style = ThemedStyle(self.root)
            style.set_theme("equilux")
        except ImportError:
            # Fallback to custom style
            self.root.configure(bg="#2c3e50")
            
            # Configure custom styles
            style.configure('Dark.TFrame', background='#34495e')
            style.configure('Title.TLabel', 
                           font=('Segoe UI', 20, 'bold'),
                           foreground='#ecf0f1',
                           background='#34495e')
            
            style.configure('Custom.TButton',
                           font=('Segoe UI', 10, 'bold'),
                           padding=8,
                           background='#3498db',
                           foreground='white')
            
            style.map('Custom.TButton',
                     background=[('active', '#2980b9'), ('pressed', '#21618c')],
                     foreground=[('active', 'white')])
            
            style.configure('Custom.TEntry',
                           fieldbackground='#ecf0f1',
                           foreground='#2c3e50',
                           padding=5,
                           font=('Segoe UI', 11))
            
            style.configure('Result.TLabel',
                           font=('Segoe UI', 14, 'bold'))
            
            style.configure('History.Treeview',
                           background='#ecf0f1',
                           foreground='#2c3e50',
                           fieldbackground='#ecf0f1',
                           rowheight=25)
            
            style.configure('History.Treeview.Heading',
                           background='#3498db',
                           foreground='white',
                           font=('Segoe UI', 10, 'bold'))
            
            style.map('History.Treeview',
                     background=[('selected', '#3498db')],
                     foreground=[('selected', 'white')])
    
    def create_widgets(self):
        """Create and arrange all GUI widgets with modern design"""
        # Header frame
        header_frame = ttk.Frame(self.main_frame, style="Dark.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title with icon
        title_frame = ttk.Frame(header_frame, style="Dark.TFrame")
        title_frame.pack(fill=tk.X)
        
        # Try to add an icon (using text as fallback)
        try:
            # You would need an actual icon file for this
            title_icon = ttk.Label(title_frame, text="⇄", font=('Segoe UI', 24), 
                                  foreground='#3498db', background='#34495e')
            title_icon.pack(side=tk.LEFT, padx=(0, 10))
        except:
            pass
            
        title = ttk.Label(title_frame, 
                         text="Palindrome Checker Pro", 
                         style='Title.TLabel')
        title.pack(side=tk.LEFT)
        
        # Tagline
        tagline = ttk.Label(header_frame, 
                           text="Check texts for palindromic properties with advanced analysis",
                           font=('Segoe UI', 10),
                           foreground='#bdc3c7',
                           background='#34495e')
        tagline.pack(fill=tk.X, pady=(0, 10))
        
        # Input frame
        input_frame = ttk.LabelFrame(self.main_frame, 
                                   text=" Input Text ",
                                   padding=15,
                                   style="Dark.TFrame")
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(input_frame, 
                                    textvariable=self.input_var,
                                    style='Custom.TEntry',
                                    font=('Segoe UI', 11))
        self.input_entry.pack(fill=tk.X, pady=(5, 10))
        self.input_entry.bind('<Return>', self.on_check)
        self.input_entry.bind('<KeyRelease>', self.on_key_release)
        
        # Options frame
        options_frame = ttk.Frame(input_frame, style="Dark.TFrame")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.live_var = tk.BooleanVar(value=True)
        live_check = ttk.Checkbutton(options_frame, 
                                    text="Live checking", 
                                    variable=self.live_var,
                                    command=self.toggle_live_check,
                                    style='Dark.TCheckbutton')
        live_check.pack(side=tk.LEFT)
        
        self.detail_var = tk.BooleanVar(value=False)
        detail_check = ttk.Checkbutton(options_frame, 
                                      text="Show details", 
                                      variable=self.detail_var,
                                      style='Dark.TCheckbutton')
        detail_check.pack(side=tk.LEFT, padx=(20, 0))
        
        # Button frame
        button_frame = ttk.Frame(input_frame, style="Dark.TFrame")
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, 
                  text="Check Palindrome", 
                  command=self.on_check,
                  style='Custom.TButton').pack(side=tk.LEFT)
        
        ttk.Button(button_frame, 
                  text="Clear", 
                  command=self.on_clear,
                  style='Custom.TButton').pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Button(button_frame, 
                  text="Copy Result", 
                  command=self.on_copy,
                  style='Custom.TButton').pack(side=tk.RIGHT)
        
        # Result frame
        result_frame = ttk.LabelFrame(self.main_frame, 
                                     text=" Result ",
                                     padding=15,
                                     style="Dark.TFrame")
        result_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.result_var = tk.StringVar(value="Enter text to check")
        self.result_label = ttk.Label(result_frame, 
                                     textvariable=self.result_var,
                                     style='Result.TLabel',
                                     foreground='#7f8c8d')
        self.result_label.pack(anchor=tk.W)
        
        # Details frame (initially hidden)
        self.details_frame = ttk.Frame(result_frame, style="Dark.TFrame")
        self.details_text = scrolledtext.ScrolledText(self.details_frame,
                                                     height=8,
                                                     font=('Consolas', 10),
                                                     wrap=tk.WORD,
                                                     bg='#ecf0f1',
                                                     fg='#2c3e50',
                                                     insertbackground='#2c3e50',
                                                     selectbackground='#3498db')
        self.details_text.pack(fill=tk.BOTH, expand=True)
        self.details_text.configure(state=tk.DISABLED)
        
        # History frame
        history_frame = ttk.LabelFrame(self.main_frame, 
                                      text=" History ",
                                      padding=15,
                                      style="Dark.TFrame")
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for history
        columns = ('text', 'result', 'normalized')
        self.history_tree = ttk.Treeview(history_frame, 
                                        columns=columns, 
                                        show='headings',
                                        height=8,
                                        style='History.Treeview')
        
        # Define headings
        self.history_tree.heading('text', text='Text')
        self.history_tree.heading('result', text='Result')
        self.history_tree.heading('normalized', text='Normalized')
        
        # Define columns
        self.history_tree.column('text', width=250, anchor=tk.W)
        self.history_tree.column('result', width=80, anchor=tk.CENTER)
        self.history_tree.column('normalized', width=200, anchor=tk.W)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(history_frame, 
                                 orient=tk.VERTICAL, 
                                 command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click event
        self.history_tree.bind('<Double-1>', self.on_history_select)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.main_frame, 
                              textvariable=self.status_var,
                              relief=tk.SUNKEN,
                              anchor=tk.W,
                              style='Dark.TLabel')
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Set focus to input entry
        self.input_entry.focus()
    
    def toggle_live_check(self):
        """Toggle live checking functionality"""
        if self.live_var.get():
            self.input_entry.bind('<KeyRelease>', self.on_key_release)
        else:
            self.input_entry.unbind('<KeyRelease>')
    
    def on_key_release(self, event):
        """Handle key release events for live checking"""
        if self.live_var.get():
            self.check_text()
    
    def on_check(self, event=None):
        """Handle check button click"""
        self.check_text(detailed=self.detail_var.get())
    
    def check_text(self, detailed=False):
        """Check if text is palindrome and update UI"""
        text = self.input_var.get().strip()
        
        if not text:
            self.result_var.set("Please enter some text")
            self.result_label.configure(foreground='#7f8c8d')
            self.hide_details()
            self.status_var.set("Ready")
            return
        
        self.status_var.set("Checking...")
        self.root.update()
        
        is_pal = is_palindrome(text)
        
        # Update result label
        if is_pal:
            self.result_var.set("PALINDROME ✓")
            self.result_label.configure(foreground='#27ae60')  # Green
        else:
            self.result_var.set("NOT A PALINDROME ✗")
            self.result_label.configure(foreground='#e74c3c')  # Red
        
        # Add to history
        norm_text = explain(text).normalized
        self.history.append((text, is_pal, norm_text))
        self.update_history()
        
        # Show details if requested
        if detailed:
            self.show_details(text)
        else:
            self.hide_details()
            
        self.status_var.set("Ready")
    
    def show_details(self, text):
        """Show detailed analysis of the text"""
        info = explain(text, find_substrings=True)
        
        details = f"Original text: {info.original}\n"
        details += f"Normalized: {info.normalized}\n"
        details += f"Length: {info.length} characters\n"
        details += f"Reversed: {info.reversed}\n\n"
        
        if info.is_palindrome:
            details += "✓ The text reads the same forwards and backwards.\n"
        else:
            details += "✗ The text does not read the same forwards and backwards.\n\n"
            
            if info.substrings:
                details += f"Found {len(info.substrings)} palindromic substring(s):\n"
                for start, end, substring in info.substrings[:5]:  # Show top 5
                    details += f"  '{substring}' (positions {start}-{end-1})\n"
                if len(info.substrings) > 5:
                    details += f"  ... and {len(info.substrings) - 5} more\n"
            else:
                details += "No significant palindromic substrings found.\n"
        
        self.details_text.configure(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, details)
        self.details_text.configure(state=tk.DISABLED)
        
        self.details_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
    
    def hide_details(self):
        """Hide details frame"""
        self.details_frame.pack_forget()
    
    def update_history(self):
        """Update history treeview"""
        # Clear current items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Add items in reverse order (newest first)
        for text, result, normalized in reversed(self.history[-50:]):  # Keep last 50 items
            result_text = "✓" if result else "✗"
            # Truncate long text for display
            display_text = text if len(text) <= 40 else text[:37] + "..."
            display_norm = normalized if len(normalized) <= 30 else normalized[:27] + "..."
            self.history_tree.insert('', tk.END, values=(display_text, result_text, display_norm))
    
    def on_history_select(self, event):
        """Handle history item selection"""
        selection = self.history_tree.selection()
        if selection:
            item = self.history_tree.item(selection[0])
            text = self.history[[h[0] for h in self.history].index(item['values'][0])]
            self.input_var.set(text[0])
            self.check_text(detailed=self.detail_var.get())
    
    def on_clear(self):
        """Clear input and results"""
        self.input_var.set("")
        self.result_var.set("Enter text to check")
        self.result_label.configure(foreground='#7f8c8d')
        self.hide_details()
        self.input_entry.focus()
        self.status_var.set("Cleared")
    
    def on_copy(self):
        """Copy result to clipboard"""
        result = self.result_var.get()
        if result != "Enter text to check":
            self.root.clipboard_clear()
            self.root.clipboard_append(result)
            self.status_var.set("Result copied to clipboard")
            messagebox.showinfo("Copied", "Result copied to clipboard")

def main():
    """Main GUI entry point"""
    root = tk.Tk()
    app = ModernPalindromeCheckerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()