from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font
from .core import compute_tip, format_money

class ModernTipCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("✨ Elegant Tip Calculator")
        self.root.geometry("550x650")
        self.root.configure(bg='#f5f7fa')
        self.root.resizable(False, False)
        
        # Custom fonts
        self.title_font = Font(family="Helvetica", size=16, weight="bold")
        self.header_font = Font(family="Helvetica", size=12, weight="bold")
        self.normal_font = Font(family="Helvetica", size=10)
        self.result_font = Font(family="Helvetica", size=12, weight="bold")
        
        # Colors
        self.primary_color = "#4f46e5"
        self.secondary_color = "#818cf8"
        self.accent_color = "#f97316"
        self.light_bg = "#f8fafc"
        self.dark_text = "#1e293b"
        
        # Store rounding widgets for easy access
        self.rounding_widgets = []
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Header
        header = ttk.Label(
            main_frame, 
            text="✨ Elegant Tip Calculator", 
            font=self.title_font,
            foreground=self.primary_color,
            background=self.light_bg
        )
        header.pack(pady=(0, 20))
        
        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text=" Bill Details ", padding="15")
        input_frame.pack(fill="x", pady=(0, 15))
        
        # Bill amount
        ttk.Label(input_frame, text="Bill Amount ($):", font=self.header_font).grid(
            row=0, column=0, sticky="w", pady=5
        )
        self.bill_var = tk.StringVar(value="0.00")
        bill_entry = ttk.Entry(input_frame, textvariable=self.bill_var, font=self.normal_font, width=20)
        bill_entry.grid(row=0, column=1, sticky="w", pady=5, padx=(10, 0))
        
        # Tip percentage
        ttk.Label(input_frame, text="Tip Percentage (%):", font=self.header_font).grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.tip_var = tk.StringVar(value="15")
        tip_frame = ttk.Frame(input_frame)
        tip_frame.grid(row=1, column=1, sticky="w", pady=5, padx=(10, 0))
        
        tip_entry = ttk.Entry(tip_frame, textvariable=self.tip_var, font=self.normal_font, width=5)
        tip_entry.pack(side="left")
        
        # Tip slider
        self.tip_scale = tk.Scale(
            tip_frame, 
            from_=0, 
            to=30, 
            orient="horizontal",
            variable=self.tip_var,
            showvalue=False,
            length=150,
            background=self.light_bg,
            highlightthickness=0
        )
        self.tip_scale.pack(side="left", padx=(10, 0))
        ttk.Label(tip_frame, text="%", font=self.normal_font).pack(side="left", padx=(5, 0))
        
        # People
        ttk.Label(input_frame, text="Number of People:", font=self.header_font).grid(
            row=2, column=0, sticky="w", pady=5
        )
        self.people_var = tk.IntVar(value=1)
        people_frame = ttk.Frame(input_frame)
        people_frame.grid(row=2, column=1, sticky="w", pady=5, padx=(10, 0))
        
        ttk.Button(people_frame, text="-", width=3, 
                  command=lambda: self.update_people(-1)).pack(side="left")
        people_label = ttk.Label(people_frame, textvariable=self.people_var, 
                                width=3, font=self.header_font, anchor="center")
        people_label.pack(side="left", padx=5)
        ttk.Button(people_frame, text="+", width=3, 
                  command=lambda: self.update_people(1)).pack(side="left")
        
        # Rounding options
        rounding_frame = ttk.LabelFrame(main_frame, text=" Rounding Options ", padding="15")
        rounding_frame.pack(fill="x", pady=(0, 15))
        
        self.round_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            rounding_frame, 
            text="Enable Rounding", 
            variable=self.round_enabled,
            command=self.toggle_rounding
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        ttk.Label(rounding_frame, text="Round to:", font=self.normal_font).grid(
            row=1, column=0, sticky="w", pady=2
        )
        self.round_to_var = tk.StringVar(value="0.05")
        self.round_combo = ttk.Combobox(
            rounding_frame, 
            textvariable=self.round_to_var, 
            values=["0.01", "0.05", "0.10", "0.25", "0.50", "1.00"],
            state="readonly",
            width=8
        )
        self.round_combo.grid(row=1, column=1, sticky="w", pady=2, padx=(10, 0))
        self.rounding_widgets.append(self.round_combo)
        
        ttk.Label(rounding_frame, text="Round target:", font=self.normal_font).grid(
            row=2, column=0, sticky="w", pady=2
        )
        self.round_target_var = tk.StringVar(value="per_person")
        self.target_combo = ttk.Combobox(
            rounding_frame, 
            textvariable=self.round_target_var, 
            values=["total", "per_person", "tip"],
            state="readonly",
            width=12
        )
        self.target_combo.grid(row=2, column=1, sticky="w", pady=2, padx=(10, 0))
        self.rounding_widgets.append(self.target_combo)
        
        ttk.Label(rounding_frame, text="Round mode:", font=self.normal_font).grid(
            row=3, column=0, sticky="w", pady=2
        )
        self.round_mode_var = tk.StringVar(value="nearest")
        self.mode_combo = ttk.Combobox(
            rounding_frame, 
            textvariable=self.round_mode_var, 
            values=["nearest", "up", "down"],
            state="readonly",
            width=12
        )
        self.mode_combo.grid(row=3, column=1, sticky="w", pady=2, padx=(10, 0))
        self.rounding_widgets.append(self.mode_combo)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(0, 15))
        
        self.calc_btn = ttk.Button(
            button_frame, 
            text="Calculate Tip", 
            command=self.calculate
        )
        self.calc_btn.pack(side="right", padx=(5, 0))
        
        ttk.Button(
            button_frame, 
            text="Clear", 
            command=self.clear
        ).pack(side="right")
        
        # Results
        results_frame = ttk.LabelFrame(main_frame, text=" Calculation Results ", padding="15")
        results_frame.pack(fill="both", expand=True)
        
        # Style for result labels
        style = ttk.Style()
        style.configure("Result.TLabel", font=self.result_font, background=self.light_bg)
        
        # Tip amount
        ttk.Label(results_frame, text="Tip Amount:", font=self.normal_font).grid(
            row=0, column=0, sticky="w", pady=5
        )
        self.tip_result = ttk.Label(
            results_frame, 
            text="$0.00", 
            style="Result.TLabel",
            foreground=self.accent_color
        )
        self.tip_result.grid(row=0, column=1, sticky="e", pady=5)
        
        # Total amount
        ttk.Label(results_frame, text="Total Amount:", font=self.normal_font).grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.total_result = ttk.Label(
            results_frame, 
            text="$0.00", 
            style="Result.TLabel",
            foreground=self.primary_color
        )
        self.total_result.grid(row=1, column=1, sticky="e", pady=5)
        
        # Per person
        ttk.Label(results_frame, text="Per Person:", font=self.normal_font).grid(
            row=2, column=0, sticky="w", pady=5
        )
        self.person_result = ttk.Label(
            results_frame, 
            text="$0.00", 
            style="Result.TLabel",
            foreground=self.secondary_color
        )
        self.person_result.grid(row=2, column=1, sticky="e", pady=5)
        
        # Rounding info
        self.rounding_info = ttk.Label(
            results_frame, 
            text="", 
            font=("Helvetica", 9, "italic"),
            foreground="#64748b"
        )
        self.rounding_info.grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))
        
        # Configure grid weights
        results_frame.columnconfigure(1, weight=1)
        
        # Set initial state
        self.toggle_rounding()
        
        # Bind events
        bill_entry.bind("<KeyRelease>", lambda e: self.calculate())
        tip_entry.bind("<KeyRelease>", lambda e: self.calculate())
        self.tip_scale.config(command=lambda e: self.update_tip_from_slider())
        self.round_combo.bind("<<ComboboxSelected>>", lambda e: self.calculate())
        self.target_combo.bind("<<ComboboxSelected>>", lambda e: self.calculate())
        self.mode_combo.bind("<<ComboboxSelected>>", lambda e: self.calculate())
        
        # Initial calculation
        self.calculate()
    
    def update_tip_from_slider(self):
        self.tip_var.set(str(self.tip_scale.get()))
        self.calculate()
    
    def update_people(self, change):
        current = self.people_var.get()
        new_value = max(1, current + change)
        self.people_var.set(new_value)
        self.calculate()
    
    def toggle_rounding(self):
        state = "normal" if self.round_enabled.get() else "disabled"
        for widget in self.rounding_widgets:
            widget.configure(state=state)
        self.calculate()
    
    def calculate(self, event=None):
        try:
            bill = float(self.bill_var.get()) if self.bill_var.get() else 0.0
            tip_pct = float(self.tip_var.get()) if self.tip_var.get() else 0.0
            people = self.people_var.get()
            
            round_to = None
            round_target = "none"
            round_mode = "nearest"
            
            if self.round_enabled.get():
                round_to = float(self.round_to_var.get())
                round_target = self.round_target_var.get()
                round_mode = self.round_mode_var.get()
            
            res = compute_tip(
                bill=bill,
                tip_pct=tip_pct,
                people=people,
                round_to=round_to,
                round_target=round_target,
                round_mode=round_mode,
            )
            
            # Update results
            self.tip_result.config(text=format_money(res.tip_amount))
            self.total_result.config(text=format_money(res.total))
            self.person_result.config(text=format_money(res.per_person))
            
            # Update rounding info
            if res.rounded:
                rounding_text = f"Rounded {res.round_mode} to {res.round_step} on {res.round_target}"
                self.rounding_info.config(text=rounding_text)
            else:
                self.rounding_info.config(text="")
                
        except (ValueError, TypeError) as e:
            # Don't show error for empty inputs
            if str(self.bill_var.get()) and str(self.tip_var.get()):
                messagebox.showerror("Input Error", "Please enter valid numbers")
    
    def clear(self):
        self.bill_var.set("0.00")
        self.tip_var.set("15")
        self.people_var.set(1)
        self.round_enabled.set(False)
        self.round_to_var.set("0.05")
        self.round_target_var.set("per_person")
        self.round_mode_var.set("nearest")
        self.toggle_rounding()
        self.calculate()

def run():
    root = tk.Tk()
    app = ModernTipCalculator(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    run()