import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from tkcalendar import DateEntry
import os
from PIL import Image, ImageTk
import webbrowser

class ModernExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("💰 Expense Tracker Pro")
        
        # Window settings to ensure title bar is visible
        self.root.attributes('-fullscreen', False)
        self.root.overrideredirect(False)
        self.root.resizable(True, True)
        
        # Set initial window size and position
        window_width = 1400
        window_height = 900
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_right = int(screen_width/2 - window_width/2)
        position_down = int(screen_height/2 - window_height/2)
        self.root.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")
        
        # Set dark theme colors
        self.bg_color = "#1e1e1e"
        self.card_bg = "#2d2d2d"
        self.accent_color = "#4fc3f7"
        self.primary_color = "#4a6fa5"
        self.secondary_color = "#166088"
        self.success_color = "#4CAF50"
        self.danger_color = "#f44336"
        self.warning_color = "#FFA500"
        self.text_color = "#ffffff"
        self.subtext_color = "#b0b0b0"
        self.border_color = "#3d3d3d"
        self.highlight_color = "#3a3a3a"
        
        # Configure root window background
        self.root.configure(bg=self.bg_color)
        self.root.option_add('*tearOff', False)  # Disable tear-off menus
        
        # Default database path
        self.db_path = "expenses.db"
        self.db_conn = None
        self.initialize_database()
        
        # Create style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Configure styles
        self.configure_styles()
        
        # Create main container with gradient background
        self.main_container = ttk.Frame(root, style="Main.TFrame")
        self.main_container.pack(fill="both", expand=True)
        
        # Setup UI components
        self.create_top_bar()
        self.create_left_panel()
        self.create_right_panel()
        
        # Load initial data
        self.load_expenses()
        self.update_stats()
        self.update_chart()
        
        # Bind keyboard shortcuts
        self.root.bind("<Control-n>", lambda e: self.add_expense())
        self.root.bind("<Control-e>", lambda e: self.edit_expense())
        self.root.bind("<Delete>", lambda e: self.delete_expense())

    def configure_styles(self):
        """Configure custom styles for widgets"""
        # Main frame style
        self.style.configure("Main.TFrame", background=self.bg_color)
        
        # Card styles
        self.style.configure("Card.TFrame", background=self.card_bg, borderwidth=2, relief="solid")
        self.style.configure("Card.TLabelframe", 
                            background=self.card_bg, 
                            foreground=self.accent_color,
                            bordercolor=self.border_color,
                            borderwidth=2,
                            font=("Segoe UI", 11, "bold"))
        self.style.configure("Card.TLabelframe.Label", 
                           background=self.card_bg,
                           foreground=self.accent_color)
        
        # Label styles
        self.style.configure("TLabel", 
                           background=self.card_bg, 
                           foreground=self.text_color,
                           font=("Segoe UI", 9))
        self.style.configure("Subtitle.TLabel", 
                           background=self.card_bg, 
                           foreground=self.subtext_color,
                           font=("Segoe UI", 8))
        self.style.configure("Header.TLabel", 
                           background=self.bg_color,
                           foreground=self.text_color,
                           font=("Segoe UI", 14, "bold"))
        self.style.configure("Stats.TLabel", 
                           background=self.card_bg,
                           foreground=self.text_color,
                           font=("Segoe UI", 10, "bold"))
        self.style.configure("Total.TLabel", 
                           background=self.card_bg,
                           foreground=self.accent_color,
                           font=("Segoe UI", 12, "bold"))
        
        # Button styles
        self.style.configure("TButton", 
                           background=self.primary_color, 
                           foreground="white",
                           font=("Segoe UI", 9),
                           padding=6,
                           borderwidth=0,
                           focusthickness=0,
                           focuscolor="none")
        self.style.map("TButton",
                     background=[("active", self.secondary_color), 
                                ("disabled", "#555555")],
                     foreground=[("disabled", "#888888")])
        self.style.configure("Primary.TButton", 
                           background=self.primary_color,
                           foreground="white",
                           font=("Segoe UI", 10, "bold"))
        self.style.configure("Success.TButton", 
                           background=self.success_color,
                           foreground="white")
        self.style.configure("Danger.TButton", 
                           background=self.danger_color,
                           foreground="white")
        self.style.configure("Accent.TButton", 
                           background=self.accent_color,
                           foreground="white")
        self.style.configure("Warning.TButton", 
                           background=self.warning_color,
                           foreground="white")
        
        # Entry and Combobox styles
        self.style.configure("TEntry", 
                           fieldbackground=self.card_bg,
                           foreground=self.text_color,
                           insertcolor=self.text_color,
                           padding=5,
                           bordercolor=self.border_color,
                           lightcolor=self.border_color,
                           darkcolor=self.border_color)
        self.style.configure("TCombobox", 
                           fieldbackground=self.card_bg,
                           foreground=self.text_color,
                           selectbackground=self.highlight_color,
                           selectforeground=self.text_color)
        self.style.map("TCombobox",
                     fieldbackground=[("readonly", self.card_bg)],
                     selectbackground=[("readonly", self.highlight_color)])
        
        # Treeview styles
        self.style.configure("Treeview", 
                           background=self.card_bg,
                           foreground=self.text_color,
                           fieldbackground=self.card_bg,
                           rowheight=28,
                           bordercolor=self.border_color,
                           borderwidth=0)
        self.style.configure("Treeview.Heading", 
                           background=self.primary_color,
                           foreground="white",
                           font=("Segoe UI", 9, "bold"),
                           relief="flat")
        self.style.map("Treeview", 
                     background=[("selected", self.highlight_color)],
                     foreground=[("selected", self.text_color)])
        
        # Scrollbar styles
        self.style.configure("Vertical.TScrollbar", 
                           background=self.card_bg,
                           troughcolor=self.bg_color,
                           bordercolor=self.bg_color,
                           arrowcolor=self.text_color,
                           gripcount=0)
        self.style.configure("Horizontal.TScrollbar", 
                           background=self.card_bg,
                           troughcolor=self.bg_color,
                           bordercolor=self.bg_color,
                           arrowcolor=self.text_color,
                           gripcount=0)
        
        # DateEntry style
        self.style.configure("DateEntry", 
                           fieldbackground=self.card_bg,
                           foreground=self.text_color,
                           bordercolor=self.border_color,
                           arrowcolor=self.text_color)

    def initialize_database(self):
        if self.db_conn:
            self.db_conn.close()
        
        try:
            self.db_conn = sqlite3.connect(self.db_path)
            self.create_tables()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to initialize database:\n{str(e)}")
            self.root.destroy()

    def create_tables(self):
        try:
            cursor = self.db_conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    amount REAL NOT NULL
                )
            ''')
            self.db_conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to create tables:\n{str(e)}")

    def create_top_bar(self):
        """Create the top navigation bar with modern design"""
        top_bar = ttk.Frame(self.main_container, style="Main.TFrame")
        top_bar.pack(fill="x", pady=(10, 5), padx=10)
        
        # App title with logo
        title_frame = ttk.Frame(top_bar, style="Main.TFrame")
        title_frame.pack(side="left", padx=10)
        
        # Logo placeholder (you can replace with actual image)
        logo_label = ttk.Label(title_frame, 
                             text="💰", 
                             font=("Segoe UI", 18),
                             style="Header.TLabel")
        logo_label.pack(side="left")
        
        title_label = ttk.Label(title_frame, 
                              text="Expense Tracker Pro", 
                              style="Header.TLabel")
        title_label.pack(side="left", padx=5)
        
        # Spacer
        ttk.Frame(top_bar, style="Main.TFrame", width=20).pack(side="left")
        
        # Action buttons with icons
        btn_frame = ttk.Frame(top_bar, style="Main.TFrame")
        btn_frame.pack(side="right", padx=10)
        
        # Help button
        help_btn = ttk.Button(btn_frame, 
                            text="❓ Help", 
                            command=self.show_help,
                            style="Accent.TButton")
        help_btn.pack(side="left", padx=5)
        
        # Export button
        export_btn = ttk.Button(btn_frame, 
                              text="📊 Export", 
                              command=self.export_data,
                              style="Accent.TButton")
        export_btn.pack(side="left", padx=5)
        
        # Database button
        db_btn = ttk.Button(btn_frame, 
                          text="🗂 Database", 
                          command=self.browse_db_location,
                          style="Accent.TButton")
        db_btn.pack(side="left", padx=5)
        
        # Database label with icon
        db_info_frame = ttk.Frame(btn_frame, style="Main.TFrame")
        db_info_frame.pack(side="left", padx=10)
        
        db_icon = ttk.Label(db_info_frame, text="🗃", font=("Segoe UI", 10))
        db_icon.pack(side="left")
        
        self.db_label = ttk.Label(db_info_frame, 
                                text=f"{os.path.basename(self.db_path)}",
                                style="Subtitle.TLabel")
        self.db_label.pack(side="left", padx=2)

    def create_left_panel(self):
        """Create the left panel for expense management"""
        left_container = ttk.Frame(self.main_container, style="Main.TFrame")
        left_container.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=5)
        
        # Expense input frame with card design
        input_frame = ttk.LabelFrame(left_container, 
                                   text="➕ Add New Expense",
                                   style="Card.TLabelframe")
        input_frame.pack(fill="x", pady=(0, 10))
        
        # Date row
        date_row = ttk.Frame(input_frame, style="Card.TFrame")
        date_row.pack(fill="x", pady=5, padx=5)
        ttk.Label(date_row, text="Date:").pack(side="left", padx=5)
        self.date_entry = DateEntry(date_row, 
                                  date_pattern="yyyy-mm-dd", 
                                  width=12,
                                  background=self.card_bg,
                                  foreground=self.text_color,
                                  bordercolor=self.border_color,
                                  selectbackground=self.highlight_color)
        self.date_entry.pack(side="left", padx=5)
        self.date_entry.set_date(datetime.now())
        
        # Category row
        category_row = ttk.Frame(input_frame, style="Card.TFrame")
        category_row.pack(fill="x", pady=5, padx=5)
        ttk.Label(category_row, text="Category:").pack(side="left", padx=5)
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(
            category_row,
            textvariable=self.category_var,
            values=self.get_categories(),
            width=22,
            style="TCombobox"
        )
        self.category_dropdown.pack(side="left", padx=5)
        
        # Description row
        desc_row = ttk.Frame(input_frame, style="Card.TFrame")
        desc_row.pack(fill="x", pady=5, padx=5)
        ttk.Label(desc_row, text="Description:").pack(side="left", padx=5)
        self.desc_entry = ttk.Entry(desc_row, width=30)
        self.desc_entry.pack(side="left", padx=5)
        
        # Amount row
        amount_row = ttk.Frame(input_frame, style="Card.TFrame")
        amount_row.pack(fill="x", pady=5, padx=5)
        ttk.Label(amount_row, text="Amount ($):").pack(side="left", padx=5)
        self.amount_entry = ttk.Entry(amount_row, width=10)
        self.amount_entry.pack(side="left", padx=5)
        
        # Add button with icon
        add_btn = ttk.Button(
            input_frame, 
            text="💾 Add Expense", 
            command=self.add_expense,
            style="Success.TButton"
        )
        add_btn.pack(pady=5, padx=5, ipadx=10)
        
        # Expense list frame with card design
        list_frame = ttk.LabelFrame(left_container, 
                                  text="📋 Expense History",
                                  style="Card.TLabelframe")
        list_frame.pack(fill="both", expand=True)
        
        # Treeview with Scrollbars
        tree_frame = ttk.Frame(list_frame, style="Card.TFrame")
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", style="Vertical.TScrollbar")
        h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", style="Horizontal.TScrollbar")

        columns = ("ID", "Date", "Category", "Description", "Amount")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="extended",
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set,
            style="Treeview"
        )
        
        # Configure columns
        self.tree.heading("ID", text="ID", anchor="center")
        self.tree.heading("Date", text="Date", anchor="center")
        self.tree.heading("Category", text="Category", anchor="center")
        self.tree.heading("Description", text="Description", anchor="center")
        self.tree.heading("Amount", text="Amount ($)", anchor="center")
        
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Date", width=100, anchor="center")
        self.tree.column("Category", width=120, anchor="center")
        self.tree.column("Description", width=200, anchor="center")
        self.tree.column("Amount", width=100, anchor="center")

        v_scroll.config(command=self.tree.yview)
        h_scroll.config(command=self.tree.xview)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        v_scroll.grid(row=0, column=1, sticky="ns", padx=0, pady=0)
        h_scroll.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        
        # Configure grid weights
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Right-click Menu with modern icons
        self.context_menu = tk.Menu(self.root, tearoff=0, 
                                  bg=self.card_bg, fg=self.text_color,
                                  activebackground=self.highlight_color,
                                  activeforeground=self.text_color,
                                  bd=0)
        self.context_menu.add_command(label="✏️ Edit", command=self.edit_expense)
        self.context_menu.add_command(label="🗑️ Delete", command=self.delete_expense)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📋 Copy", command=self.copy_to_clipboard)
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Double-click to edit
        self.tree.bind("<Double-1>", lambda e: self.edit_expense())

    def create_right_panel(self):
        """Create the right panel for dashboard and statistics"""
        right_container = ttk.Frame(self.main_container, style="Main.TFrame")
        right_container.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=5)
        
        # Stats frame with card design
        stats_frame = ttk.LabelFrame(right_container, 
                                   text="📊 Statistics",
                                   style="Card.TLabelframe")
        stats_frame.pack(fill="x", pady=(0, 10))
        
        # Stats display
        stats_display = ttk.Frame(stats_frame, style="Card.TFrame")
        stats_display.pack(fill="x", pady=10, padx=10)
        
        # Total expenses card
        total_card = ttk.Frame(stats_display, style="Card.TFrame")
        total_card.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        
        ttk.Label(total_card, 
                text="Total Expenses", 
                style="Subtitle.TLabel").pack(anchor="w")
        self.total_label = ttk.Label(total_card, 
                                   text="$0.00", 
                                   style="Total.TLabel")
        self.total_label.pack(anchor="w")
        
        # Monthly filter card
        filter_card = ttk.Frame(stats_display, style="Card.TFrame")
        filter_card.pack(side="right", padx=10, pady=5)
        
        ttk.Label(filter_card, 
                text="Filter Month", 
                style="Subtitle.TLabel").pack(anchor="e")
        
        filter_row = ttk.Frame(filter_card, style="Card.TFrame")
        filter_row.pack(anchor="e")
        
        ttk.Label(filter_row, text="Month:").pack(side="left", padx=5)
        self.month_var = tk.StringVar()
        self.month_dropdown = ttk.Combobox(
            filter_row,
            textvariable=self.month_var,
            values=self.get_months(),
            width=10,
            style="TCombobox"
        )
        self.month_dropdown.pack(side="left", padx=5)
        self.month_dropdown.bind("<<ComboboxSelected>>", lambda e: self.load_expenses())
        
        # Charts frame with card design
        chart_frame = ttk.LabelFrame(right_container, 
                                   text="📈 Expense Analysis",
                                   style="Card.TLabelframe")
        chart_frame.pack(fill="both", expand=True)
        
        # Create figure with dark theme
        plt.style.use('dark_background')
        self.fig = plt.figure(figsize=(10, 8), dpi=100)
        self.fig.patch.set_facecolor(self.card_bg)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def browse_db_location(self):
        new_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")],
            title="Select database save location",
            initialfile="expenses.db"
        )
        
        if new_path:
            self.db_path = new_path
            self.db_label.config(text=f"{os.path.basename(self.db_path)}")
            self.initialize_database()
            self.load_expenses()
            self.update_stats()
            messagebox.showinfo("Success", f"Database location set to:\n{self.db_path}")

    def add_expense(self):
        if not self.db_conn:
            messagebox.showerror("Error", "Database not connected!")
            return

        date = self.date_entry.get()
        category = self.category_var.get()
        description = self.desc_entry.get()
        amount = self.amount_entry.get()

        if not (date and category and amount):
            messagebox.showerror("Error", "Date, Category, and Amount are required!")
            return

        try:
            datetime.strptime(date, "%Y-%m-%d")
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Invalid Date or Amount!")
            return

        try:
            cursor = self.db_conn.cursor()
            cursor.execute(
                "INSERT INTO expenses (date, category, description, amount) VALUES (?, ?, ?, ?)",
                (date, category, description, amount)
            )
            self.db_conn.commit()
            self.load_expenses()
            self.update_stats()
            self.update_chart()
            self.clear_fields()
            messagebox.showinfo("Success", "Expense added successfully!")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add expense:\n{str(e)}")

    def clear_fields(self):
        self.date_entry.set_date(datetime.now())
        self.category_var.set("")
        self.desc_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)

    def edit_expense(self):
        if not self.db_conn:
            messagebox.showerror("Error", "Database not connected!")
            return

        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        expense_id = item['values'][0]
        
        edit_win = tk.Toplevel(self.root)
        edit_win.title("Edit Expense")
        edit_win.geometry("400x300")
        edit_win.resizable(False, False)
        edit_win.configure(bg=self.card_bg)
        
        # Center the window
        window_width = edit_win.winfo_reqwidth()
        window_height = edit_win.winfo_reqheight()
        position_right = int(edit_win.winfo_screenwidth()/2 - window_width/2)
        position_down = int(edit_win.winfo_screenheight()/2 - window_height/2)
        edit_win.geometry(f"+{position_right}+{position_down}")
        
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT * FROM expenses WHERE id=?", (expense_id,))
            data = cursor.fetchone()
            
            if not data:
                messagebox.showerror("Error", "Expense not found!")
                edit_win.destroy()
                return
                
            # Date
            ttk.Label(edit_win, text="Date:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
            date_entry = DateEntry(edit_win, date_pattern="yyyy-mm-dd")
            date_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
            date_entry.set_date(datetime.strptime(data[1], "%Y-%m-%d"))
            
            # Category
            ttk.Label(edit_win, text="Category:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
            category_var = tk.StringVar(value=data[2])
            category_dropdown = ttk.Combobox(
                edit_win,
                textvariable=category_var,
                values=self.get_categories(),
                width=20
            )
            category_dropdown.grid(row=1, column=1, padx=10, pady=10, sticky="w")
            
            # Description
            ttk.Label(edit_win, text="Description:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
            desc_entry = ttk.Entry(edit_win, width=30)
            desc_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
            desc_entry.insert(0, data[3])
            
            # Amount
            ttk.Label(edit_win, text="Amount:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
            amount_entry = ttk.Entry(edit_win, width=15)
            amount_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")
            amount_entry.insert(0, data[4])
            
            # Button frame
            btn_frame = ttk.Frame(edit_win, style="Card.TFrame")
            btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
            
            def save_changes():
                new_date = date_entry.get()
                new_category = category_var.get()
                new_desc = desc_entry.get()
                new_amount = amount_entry.get()
                
                try:
                    datetime.strptime(new_date, "%Y-%m-%d")
                    new_amount = float(new_amount)
                except ValueError:
                    messagebox.showerror("Error", "Invalid Date or Amount!")
                    return
                    
                try:
                    cursor.execute(
                        "UPDATE expenses SET date=?, category=?, description=?, amount=? WHERE id=?",
                        (new_date, new_category, new_desc, new_amount, expense_id)
                    )
                    self.db_conn.commit()
                    edit_win.destroy()
                    self.load_expenses()
                    self.update_stats()
                    self.update_chart()
                    messagebox.showinfo("Success", "Expense updated successfully!")
                except sqlite3.Error as e:
                    messagebox.showerror("Database Error", f"Failed to update expense:\n{str(e)}")
            
            ttk.Button(btn_frame, text="💾 Save", command=save_changes, style="Success.TButton").pack(side="left", padx=10)
            ttk.Button(btn_frame, text="✖ Cancel", command=edit_win.destroy, style="Danger.TButton").pack(side="left", padx=10)
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch expense:\n{str(e)}")
            edit_win.destroy()

    def delete_expense(self):
        if not self.db_conn:
            messagebox.showerror("Error", "Database not connected!")
            return

        selected = self.tree.selection()
        if not selected:
            return
        
        if messagebox.askyesno("Confirm", "Delete selected expenses?", icon="warning"):
            try:
                cursor = self.db_conn.cursor()
                for item in selected:
                    expense_id = self.tree.item(item)['values'][0]
                    cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
                self.db_conn.commit()
                self.load_expenses()
                self.update_stats()
                self.update_chart()
                messagebox.showinfo("Success", "Expenses deleted successfully!")
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Failed to delete expenses:\n{str(e)}")

    def export_data(self):
        if not self.db_conn:
            messagebox.showerror("Error", "Database not connected!")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx"), ("CSV", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("SELECT * FROM expenses")
                df = pd.DataFrame(cursor.fetchall(), columns=["ID", "Date", "Category", "Description", "Amount"])
                
                if file_path.endswith(".xlsx"):
                    df.to_excel(file_path, index=False)
                elif file_path.endswith(".csv"):
                    df.to_csv(file_path, index=False)
                messagebox.showinfo("Success", f"Data exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export data:\n{str(e)}")

    def update_chart(self):
        if not self.db_conn:
            return

        try:
            cursor = self.db_conn.cursor()
            self.fig.clf()
            
            # Set figure background color
            self.fig.patch.set_facecolor(self.card_bg)
            
            # Get monthly data
            cursor.execute('''
                SELECT strftime('%Y-%m', date) AS month, SUM(amount) 
                FROM expenses 
                GROUP BY month 
                ORDER BY month
            ''')
            monthly_data = cursor.fetchall()
            
            # Get category data
            cursor.execute('''
                SELECT category, SUM(amount)
                FROM expenses
                GROUP BY category
                ORDER BY SUM(amount) DESC
            ''')
            category_data = cursor.fetchall()
            
            # Monthly spending bar chart
            ax1 = self.fig.add_subplot(121)
            if monthly_data:
                months = [row[0] for row in monthly_data]
                amounts = [row[1] for row in monthly_data]
                
                # Customize bar chart appearance
                bars = ax1.bar(months, amounts, color=self.accent_color, edgecolor=self.border_color)
                ax1.set_title("Monthly Spending", pad=20, color=self.text_color)
                ax1.set_ylabel("Amount ($)", labelpad=10, color=self.text_color)
                ax1.tick_params(axis='x', rotation=45, colors=self.text_color)
                ax1.tick_params(axis='y', colors=self.text_color)
                ax1.set_facecolor(self.card_bg)
                
                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    ax1.text(bar.get_x() + bar.get_width()/2., height,
                            f'${height:.2f}',
                            ha='center', va='bottom', color=self.text_color)
            
            # Category spending pie chart
            ax2 = self.fig.add_subplot(122)
            if category_data:
                categories = [row[0] for row in category_data]
                amounts = [row[1] for row in category_data]
                
                # Customize pie chart appearance
                colors = plt.cm.Pastel1(range(len(categories)))
                wedges, texts, autotexts = ax2.pie(
                    amounts, 
                    labels=categories, 
                    autopct='%1.1f%%', 
                    startangle=90,
                    colors=colors,
                    wedgeprops={'edgecolor': self.border_color, 'linewidth': 1}
                )
                ax2.set_title("Spending by Category", pad=20, color=self.text_color)
                ax2.axis('equal')
                
                # Style text in pie chart
                for text in texts:
                    text.set_color(self.text_color)
                for autotext in autotexts:
                    autotext.set_color(self.text_color)
            
            # Adjust layout
            self.fig.tight_layout(pad=3.0)
            self.canvas.draw()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load chart data:\n{str(e)}")

    def get_categories(self):
        return [
            "Food", "Transport", "Housing", "Utilities", "Healthcare",
            "Insurance", "Education", "Entertainment", "Shopping",
            "Personal Care", "Gifts", "Travel", "Debt", "Savings",
            "Investments", "Charity", "Other"
        ]

    def get_months(self):
        if not self.db_conn:
            return ["All"]
            
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT DISTINCT strftime('%Y-%m', date) FROM expenses ORDER BY date DESC")
            return ["All"] + [row[0] for row in cursor.fetchall()]
        except sqlite3.Error:
            return ["All"]

    def load_expenses(self):
        if not self.db_conn:
            return

        for row in self.tree.get_children():
            self.tree.delete(row)
            
        month_filter = self.month_var.get()
        query = "SELECT id, date, category, description, amount FROM expenses"
        params = ()
        
        if month_filter and month_filter != "All":
            query += " WHERE strftime('%Y-%m', date) = ?"
            params = (month_filter,)
            
        query += " ORDER BY date DESC"
        
        try:
            cursor = self.db_conn.cursor()
            cursor.execute(query, params)
            
            for row in cursor.fetchall():
                self.tree.insert("", tk.END, values=row)
            
            self.update_stats()
            self.update_chart()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load expenses:\n{str(e)}")

    def update_stats(self):
        if not self.db_conn:
            self.total_label.config(text="$0.00")
            return

        try:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT SUM(amount) FROM expenses")
            total = cursor.fetchone()[0] or 0.0
            self.total_label.config(text=f"${total:.2f}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to calculate totals:\n{str(e)}")

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def copy_to_clipboard(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        item = self.tree.item(selected[0])
        self.root.clipboard_clear()
        self.root.clipboard_append("\t".join(str(x) for x in item['values']))
    
    def show_help(self):
        help_text = """Expense Tracker Pro - Help

1. Add Expense:
   - Fill in all fields and click "Add Expense"
   - Shortcut: Ctrl+N

2. Edit Expense:
   - Right-click an expense and select "Edit"
   - Double-click an expense
   - Shortcut: Ctrl+E

3. Delete Expense:
   - Right-click an expense and select "Delete"
   - Shortcut: Delete key

4. Filter Data:
   - Use the month dropdown to filter by month

5. Export Data:
   - Click "Export" to save data as Excel or CSV
"""
        messagebox.showinfo("Help", help_text)

if __name__ == "__main__":
    root = tk.Tk()
    
    # Set window icon
    try:
        img = Image.open("icon.png")  # Replace with your icon path
        photo = ImageTk.PhotoImage(img)
        root.iconphoto(False, photo)
    except:
        pass  # Use default icon if custom icon not found
    
    # Ensure window controls are visible
    root.attributes('-fullscreen', False)
    root.overrideredirect(False)
    root.resizable(True, True)
    
    app = ModernExpenseTracker(root)
    root.mainloop()