"""Modern Tkinter GUI for Email Slicer."""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from tkinter import font as tkfont
import threading
from typing import Dict, List
import json
from pathlib import Path
import webbrowser

from email_slicer.core import parse_email, EmailSliceError, batch_parse_emails
from email_slicer.validators import suggest_domain, get_email_provider_type

class ModernTheme:
    """Modern color theme for the application."""
    PRIMARY = "#2563eb"
    PRIMARY_HOVER = "#1d4ed8"
    SECONDARY = "#64748b"
    SECONDARY_HOVER = "#475569"
    SUCCESS = "#10b981"
    SUCCESS_HOVER = "#059669"
    WARNING = "#f59e0b"
    DANGER = "#ef4444"
    LIGHT = "#f8fafc"
    DARK = "#1e293b"
    TEXT_LIGHT = "#ffffff"
    TEXT_DARK = "#1e293b"
    CARD_BG = "#ffffff"
    BORDER = "#e2e8f0"
    ACCENT = "#8b5cf6"

class ModernButton(tk.Frame):
    """Modern styled button with hover effects."""
    def __init__(self, parent, text, command, style="primary", width=120, height=40):
        super().__init__(parent, bg=ModernTheme.LIGHT)
        
        self.style = style
        self.command = command
        self.width = width
        self.height = height
        
        # Configure colors based on style
        if style == "primary":
            self.bg = ModernTheme.PRIMARY
            self.hover_bg = ModernTheme.PRIMARY_HOVER
        elif style == "secondary":
            self.bg = ModernTheme.SECONDARY
            self.hover_bg = ModernTheme.SECONDARY_HOVER
        elif style == "success":
            self.bg = ModernTheme.SUCCESS
            self.hover_bg = ModernTheme.SUCCESS_HOVER
        else:
            self.bg = ModernTheme.PRIMARY
            self.hover_bg = ModernTheme.PRIMARY_HOVER
            
        self.btn = tk.Canvas(self, height=height, width=width, bg=self.bg, 
                           highlightthickness=0, relief='flat', cursor="hand2")
        self.btn.pack(fill=tk.BOTH, expand=True)
        
        # Add text with shadow effect
        self.text_id = self.btn.create_text(
            width//2, height//2, 
            text=text, fill=ModernTheme.TEXT_LIGHT,
            font=('Arial', 10, 'bold'),
            justify='center'
        )
        
        # Bind events
        self.btn.bind("<Enter>", self.on_enter)
        self.btn.bind("<Leave>", self.on_leave)
        self.btn.bind("<Button-1>", self.on_click)
        self.btn.bind("<ButtonRelease-1>", self.on_release)
        
    def on_enter(self, event):
        """Handle mouse enter event."""
        self.btn.config(bg=self.hover_bg)
        
    def on_leave(self, event):
        """Handle mouse leave event."""
        self.btn.config(bg=self.bg)
        
    def on_click(self, event):
        """Handle click event."""
        self.btn.config(relief='sunken')
        
    def on_release(self, event):
        """Handle button release."""
        self.btn.config(relief='flat')
        self.command()

class EmailSlicerGUI:
    """Modern GUI for Email Slicer application."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Email Slicer Pro v1.0.0")
        self.root.geometry("1000x750")
        self.root.configure(bg=ModernTheme.LIGHT)
        self.root.minsize(900, 650)
        
        # Center the window on screen
        self.center_window()
        
        # Set application icon (if available)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # Configure styles
        self.setup_styles()
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding=0)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create header
        self.create_header()
        
        # Create notebook
        self.setup_ui()
        
        # Store last parsed emails for batch export
        self.last_parsed_emails = []
        
    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_header(self):
        """Create application header with gradient effect."""
        header = tk.Frame(self.main_frame, bg=ModernTheme.PRIMARY, height=80)
        header.pack(fill=tk.X, pady=(0, 10))
        
        # Title with icon
        title_frame = tk.Frame(header, bg=ModernTheme.PRIMARY)
        title_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Icon label
        icon_label = tk.Label(title_frame, text="📧", font=('Arial', 24), 
                            bg=ModernTheme.PRIMARY, fg=ModernTheme.TEXT_LIGHT)
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Title
        title = tk.Label(title_frame, text="Email Slicer Pro", 
                       font=('Arial', 20, 'bold'), 
                       fg=ModernTheme.TEXT_LIGHT, 
                       bg=ModernTheme.PRIMARY)
        title.pack(side=tk.LEFT)
        
        # Version
        version = tk.Label(header, text="v1.0.0", 
                         font=('Arial', 10), 
                         fg=ModernTheme.TEXT_LIGHT, 
                         bg=ModernTheme.PRIMARY)
        version.place(relx=0.95, rely=0.5, anchor='e')
    
    def setup_styles(self):
        """Configure modern ttk styles."""
        style = ttk.Style()
        
        # Configure theme
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TFrame', background=ModernTheme.LIGHT)
        style.configure('TLabel', background=ModernTheme.LIGHT, foreground=ModernTheme.DARK, font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10), padding=(10, 5))
        style.configure('TEntry', font=('Arial', 11), fieldbackground=ModernTheme.CARD_BG)
        style.configure('TLabelframe', background=ModernTheme.LIGHT, bordercolor=ModernTheme.BORDER)
        style.configure('TLabelframe.Label', background=ModernTheme.LIGHT, foreground=ModernTheme.DARK, font=('Arial', 11, 'bold'))
        
        style.configure('TNotebook', background=ModernTheme.LIGHT)
        style.configure('TNotebook.Tab', 
                       background=ModernTheme.LIGHT,
                       foreground=ModernTheme.DARK,
                       padding=[20, 8],
                       font=('Arial', 10, 'bold'))
        style.map('TNotebook.Tab',
                 background=[('selected', ModernTheme.PRIMARY)],
                 foreground=[('selected', ModernTheme.TEXT_LIGHT)])
        
        # Progress bar style
        style.configure("Custom.Horizontal.TProgressbar", 
                       thickness=20,
                       background=ModernTheme.SUCCESS,
                       troughcolor=ModernTheme.BORDER)
    
    def setup_ui(self):
        """Setup the main user interface."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Single email tab
        self.single_frame = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.single_frame, text="🔍 Single Email")
        
        # Batch processing tab
        self.batch_frame = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.batch_frame, text="📁 Batch Processing")
        
        # About tab
        self.about_frame = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.about_frame, text="ℹ️ About")
        
        self.setup_single_tab()
        self.setup_batch_tab()
        self.setup_about_tab()
        
    def setup_single_tab(self):
        """Setup the single email processing tab."""
        # Input section
        input_card = ttk.LabelFrame(self.single_frame, text="📧 Email Input", padding=20)
        input_card.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(input_card, text="Enter email address to analyze:", 
                 font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(0, 15))
        
        input_row = ttk.Frame(input_card)
        input_row.pack(fill=tk.X, pady=5)
        
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(input_row, textvariable=self.email_var, font=('Arial', 12))
        self.email_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        self.email_entry.bind('<Return>', lambda e: self.process_single_email())
        
        # Process Button - FIXED: Now properly connected
        process_btn = ttk.Button(input_row, text="🔍 Process", 
                               command=self.process_single_email,
                               width=12)
        process_btn.pack(side=tk.RIGHT)
        
        # Quick examples
        examples_frame = ttk.Frame(input_card)
        examples_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(examples_frame, text="Quick examples:", 
                 font=('Arial', 9), foreground=ModernTheme.SECONDARY).pack(anchor=tk.W)
        
        examples_text = tk.Text(examples_frame, height=2, font=('Arial', 9), 
                               bg=ModernTheme.LIGHT, fg=ModernTheme.SECONDARY,
                               wrap=tk.WORD, relief='flat')
        examples_text.insert('1.0', "user@gmail.com • user+tag@company.co.uk • admin@sub.domain.org")
        examples_text.config(state=tk.DISABLED)
        examples_text.pack(fill=tk.X, pady=(5, 0))
        
        # Results section
        results_card = ttk.LabelFrame(self.single_frame, text="📊 Analysis Results", padding=20)
        results_card.pack(fill=tk.BOTH, expand=True)
        
        # Create results notebook for organized display
        results_notebook = ttk.Notebook(results_card)
        results_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Basic info tab
        basic_frame = ttk.Frame(results_notebook, padding=15)
        results_notebook.add(basic_frame, text="📋 Basic Info")
        
        self.setup_basic_results(basic_frame)
        
        # Advanced info tab
        advanced_frame = ttk.Frame(results_notebook, padding=15)
        results_notebook.add(advanced_frame, text="🔧 Advanced")
        
        self.setup_advanced_results(advanced_frame)
        
        # Validation tab
        validation_frame = ttk.Frame(results_notebook, padding=15)
        results_notebook.add(validation_frame, text="✅ Validation")
        
        self.setup_validation_results(validation_frame)
    
    def setup_basic_results(self, parent):
        """Setup basic results display."""
        # Create a frame with better organization
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        fields = [
            ("📧 Original Email", "original"),
            ("✨ Normalized", "normalized"),
            ("👤 Local Part", "local_part"),
            ("🔑 Base Username", "base_username"),
            ("🌐 Domain", "domain")
        ]
        
        for i, (label, field) in enumerate(fields):
            # Create card for each field
            field_frame = ttk.LabelFrame(main_frame, text=label, padding=10)
            field_frame.pack(fill=tk.X, pady=8, padx=5)
            
            row = ttk.Frame(field_frame)
            row.pack(fill=tk.X)
            
            var = tk.StringVar()
            entry = ttk.Entry(row, textvariable=var, state='readonly', 
                            font=('Arial', 10), style='TEntry')
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
            
            # Copy button with modern style
            copy_btn = ttk.Button(row, text="📋 Copy", width=8,
                                command=lambda v=var: self.copy_to_clipboard(v.get()))
            copy_btn.pack(side=tk.RIGHT)
            
            setattr(self, f"single_{field}_var", var)
    
    def setup_advanced_results(self, parent):
        """Setup advanced results display."""
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        fields = [
            ("🏷️ Tag", "tag"),
            ("🔗 Subdomain", "subdomain"),
            ("🏢 Root Domain", "root_domain"),
            ("🌍 TLD", "tld")
        ]
        
        for i, (label, field) in enumerate(fields):
            field_frame = ttk.LabelFrame(main_frame, text=label, padding=10)
            field_frame.pack(fill=tk.X, pady=8, padx=5)
            
            row = ttk.Frame(field_frame)
            row.pack(fill=tk.X)
            
            var = tk.StringVar()
            entry = ttk.Entry(row, textvariable=var, state='readonly', 
                            font=('Arial', 10))
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
            
            copy_btn = ttk.Button(row, text="📋 Copy", width=8,
                                command=lambda v=var: self.copy_to_clipboard(v.get()))
            copy_btn.pack(side=tk.RIGHT)
            
            setattr(self, f"single_{field}_var", var)
        
        # Disposable email warning
        self.disposable_var = tk.StringVar()
        warning_frame = ttk.Frame(main_frame)
        warning_frame.pack(fill=tk.X, pady=15, padx=5)
        
        warning_label = ttk.Label(warning_frame, textvariable=self.disposable_var, 
                                 foreground=ModernTheme.DANGER,
                                 font=('Arial', 11, 'bold'),
                                 background=ModernTheme.LIGHT)
        warning_label.pack(anchor=tk.CENTER)
    
    def setup_validation_results(self, parent):
        """Setup validation results display."""
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Provider type card
        provider_card = ttk.LabelFrame(main_frame, text="🏢 Provider Type", padding=15)
        provider_card.pack(fill=tk.X, pady=10, padx=5)
        
        self.provider_var = tk.StringVar(value="Not analyzed")
        provider_label = ttk.Label(provider_card, textvariable=self.provider_var, 
                                 font=('Arial', 12, 'bold'),
                                 foreground=ModernTheme.PRIMARY)
        provider_label.pack(anchor=tk.W)
        
        # Suggestion card
        suggestion_card = ttk.LabelFrame(main_frame, text="💡 Suggestions", padding=15)
        suggestion_card.pack(fill=tk.X, pady=10, padx=5)
        
        self.suggestion_var = tk.StringVar(value="No email analyzed")
        suggestion_label = ttk.Label(suggestion_card, textvariable=self.suggestion_var, 
                                   font=('Arial', 10),
                                   foreground=ModernTheme.WARNING,
                                   wraplength=600)
        suggestion_label.pack(anchor=tk.W, fill=tk.X)
        
        # Validation status card
        status_card = ttk.LabelFrame(main_frame, text="✅ Validation Status", padding=15)
        status_card.pack(fill=tk.X, pady=10, padx=5)
        
        self.validation_var = tk.StringVar(value="Waiting for email input...")
        status_label = ttk.Label(status_card, textvariable=self.validation_var, 
                               font=('Arial', 10),
                               foreground=ModernTheme.SUCCESS)
        status_label.pack(anchor=tk.W)
    
    def setup_batch_tab(self):
        """Setup the batch processing tab."""
        # File selection
        file_card = ttk.LabelFrame(self.batch_frame, text="📁 File Selection", padding=20)
        file_card.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(file_card, text="Select file containing email addresses (one per line):", 
                 font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(0, 15))
        
        file_row = ttk.Frame(file_card)
        file_row.pack(fill=tk.X, pady=5)
        
        self.file_var = tk.StringVar()
        file_entry = ttk.Entry(file_row, textvariable=self.file_var, font=('Arial', 11))
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        
        browse_btn = ttk.Button(file_row, text="📂 Browse Files", 
                               command=self.browse_file, width=15)
        browse_btn.pack(side=tk.RIGHT)
        
        # Options
        options_card = ttk.LabelFrame(self.batch_frame, text="⚙️ Processing Options", padding=20)
        options_card.pack(fill=tk.X, pady=(0, 20))
        
        self.check_disposable = tk.BooleanVar(value=True)
        disposable_cb = ttk.Checkbutton(options_card, text="Check for disposable email domains",
                                       variable=self.check_disposable)
        disposable_cb.pack(anchor=tk.W, pady=8)
        
        self.export_json = tk.BooleanVar(value=True)
        export_cb = ttk.Checkbutton(options_card, text="Export results as JSON format",
                                   variable=self.export_json)
        export_cb.pack(anchor=tk.W, pady=8)
        
        # Action buttons - FIXED: Now using regular ttk.Button that works
        action_frame = ttk.Frame(self.batch_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        # Process button - FIXED: Now properly connected
        process_btn = ttk.Button(action_frame, text="🚀 Process Batch", 
                               command=self.process_batch,
                               width=15)
        process_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button
        clear_btn = ttk.Button(action_frame, text="🗑️ Clear Results", 
                             command=self.clear_batch_results,
                             width=15)
        clear_btn.pack(side=tk.LEFT)
        
        # Results
        results_card = ttk.LabelFrame(self.batch_frame, text="📊 Batch Results", padding=20)
        results_card.pack(fill=tk.BOTH, expand=True)
        
        # Summary
        summary_frame = ttk.Frame(results_card)
        summary_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.summary_var = tk.StringVar(value="👆 Select a file and click 'Process Batch' to start")
        summary_label = ttk.Label(summary_frame, textvariable=self.summary_var, 
                                 font=('Arial', 11, 'bold'),
                                 foreground=ModernTheme.PRIMARY)
        summary_label.pack(anchor=tk.W)
        
        # Progress bar
        progress_frame = ttk.Frame(results_card)
        progress_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(progress_frame, text="Progress:", font=('Arial', 10)).pack(anchor=tk.W)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100,
                                          style="Custom.Horizontal.TProgressbar")
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
        
        # Results text area
        results_label_frame = ttk.Frame(results_card)
        results_label_frame.pack(fill=tk.X, pady=(10, 5))
        
        ttk.Label(results_label_frame, text="📧 Processed Emails:", 
                 font=('Arial', 11, 'bold')).pack(side=tk.LEFT)
        
        # Results counter
        self.results_count_var = tk.StringVar(value="(0 emails)")
        ttk.Label(results_label_frame, textvariable=self.results_count_var,
                 font=('Arial', 10),
                 foreground=ModernTheme.SECONDARY).pack(side=tk.LEFT, padx=(10, 0))
        
        self.results_text = scrolledtext.ScrolledText(results_card, height=12, 
                                                    font=('Consolas', 10), 
                                                    wrap=tk.WORD,
                                                    bg=ModernTheme.CARD_BG)
        self.results_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Export button
        export_frame = ttk.Frame(results_card)
        export_frame.pack(fill=tk.X, pady=10)
        
        export_btn = ttk.Button(export_frame, text="💾 Export Results", 
                              command=self.export_results,
                              width=15)
        export_btn.pack(side=tk.RIGHT)
    
    def setup_about_tab(self):
        """Setup the about tab."""
        main_frame = ttk.Frame(self.about_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        icon_label = tk.Label(header_frame, text="📧", font=('Arial', 48), 
                            bg=ModernTheme.LIGHT, fg=ModernTheme.PRIMARY)
        icon_label.pack(side=tk.LEFT, padx=(0, 20))
        
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        title = tk.Label(title_frame, text="Email Slicer Pro", 
                       font=('Arial', 24, 'bold'), 
                       fg=ModernTheme.DARK, 
                       bg=ModernTheme.LIGHT)
        title.pack(anchor=tk.W)
        
        version = tk.Label(title_frame, text="Version 1.0.0", 
                         font=('Arial', 14), 
                         fg=ModernTheme.SECONDARY, 
                         bg=ModernTheme.LIGHT)
        version.pack(anchor=tk.W, pady=(5, 0))
        
        # Description
        desc_frame = ttk.LabelFrame(main_frame, text="📖 Description", padding=20)
        desc_frame.pack(fill=tk.X, pady=(0, 20))
        
        desc_text = """
Email Slicer Pro is a powerful Python application designed for parsing, analyzing, 
and validating email addresses. It provides both graphical and command-line interfaces 
for comprehensive email address analysis.

Whether you're a developer working with user authentication, a marketer analyzing 
email lists, or just curious about email structure, this tool provides detailed 
insights into email address components.
        """
        
        desc_widget = scrolledtext.ScrolledText(desc_frame, font=('Arial', 11), 
                                              wrap=tk.WORD, height=6)
        desc_widget.insert('1.0', desc_text.strip())
        desc_widget.config(state=tk.DISABLED, bg=ModernTheme.CARD_BG)
        desc_widget.pack(fill=tk.BOTH, expand=True)
        
        # Features
        features_frame = ttk.LabelFrame(main_frame, text="✨ Features", padding=20)
        features_frame.pack(fill=tk.X, pady=(0, 20))
        
        features_text = """
• 🔍 Extract email components (username, domain, TLD, tags)
• ✅ Validate email formats and identify providers  
• 📧 Handle +tag addressing and subdomains
• 🚫 Detect disposable/temporary email services
• 📁 Batch process multiple emails from files
• 🎨 Modern, intuitive graphical interface
• 💻 Powerful command-line interface
• 📊 Export results in JSON format
• 🎯 Domain suggestions for common typos
        """
        
        features_widget = scrolledtext.ScrolledText(features_frame, font=('Arial', 11), 
                                                  wrap=tk.WORD, height=8)
        features_widget.insert('1.0', features_text.strip())
        features_widget.config(state=tk.DISABLED, bg=ModernTheme.CARD_BG)
        features_widget.pack(fill=tk.BOTH, expand=True)
        
        # Links
        links_frame = ttk.Frame(main_frame)
        links_frame.pack(fill=tk.X, pady=10)
        
        # GitHub link
        github_frame = ttk.Frame(links_frame)
        github_frame.pack(anchor=tk.W, pady=5)
        
        ttk.Label(github_frame, text="GitHub Repository: ", 
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        
        github_link = ttk.Label(github_frame, text="https://github.com/yourusername/email-slicer", 
                               foreground=ModernTheme.PRIMARY, cursor="hand2", 
                               font=('Arial', 10, 'underline'))
        github_link.pack(side=tk.LEFT)
        github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/yourusername/email-slicer"))
        
        # License
        license_frame = ttk.Frame(links_frame)
        license_frame.pack(anchor=tk.W, pady=5)
        
        ttk.Label(license_frame, text="License: ", 
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        
        ttk.Label(license_frame, text="MIT License", 
                 font=('Arial', 10)).pack(side=tk.LEFT)
    
    def process_single_email(self):
        """Process a single email address."""
        email = self.email_var.get().strip()
        if not email:
            messagebox.showerror("Error", "❌ Please enter an email address to analyze.")
            return
        
        try:
            pe = parse_email(email, check_disposable=True)
            
            # Update basic fields
            for field in ['original', 'normalized', 'local_part', 'base_username', 'domain']:
                var = getattr(self, f'single_{field}_var')
                var.set(getattr(pe, field))
            
            # Update advanced fields
            for field in ['tag', 'subdomain', 'root_domain', 'tld']:
                var = getattr(self, f'single_{field}_var')
                value = getattr(pe, field)
                var.set(value if value is not None else "N/A")
            
            # Update validation info
            provider_type = get_email_provider_type(pe.domain)
            self.provider_var.set(f"{provider_type.title()} Email Provider")
            
            suggestion = suggest_domain(pe.domain)
            if suggestion:
                self.suggestion_var.set(f"💡 Did you mean '{suggestion}'?")
            else:
                self.suggestion_var.set("✅ Domain looks correct")
            
            # Show disposable warning if needed
            if pe.is_disposable:
                self.disposable_var.set("⚠️ WARNING: This appears to be a disposable/temporary email address")
                self.validation_var.set("❌ Invalid: Disposable email service detected")
            else:
                self.disposable_var.set("")
                self.validation_var.set("✅ Valid email address")
                
            # Show success message
            self.show_toast("✅ Email analyzed successfully!", ModernTheme.SUCCESS)
                
        except EmailSliceError as e:
            messagebox.showerror("Error", f"❌ Invalid email address:\n{e}")
            self.validation_var.set("❌ Invalid email format")
    
    def browse_file(self):
        """Open file dialog to select input file."""
        filename = filedialog.askopenfilename(
            title="Select email list file",
            filetypes=[
                ("Text files", "*.txt"), 
                ("CSV files", "*.csv"), 
                ("All files", "*.*")
            ]
        )
        if filename:
            self.file_var.set(filename)
            self.summary_var.set(f"📁 Selected file: {Path(filename).name}")
    
    def process_batch(self):
        """Process batch of emails from file."""
        filename = self.file_var.get()
        if not filename:
            messagebox.showerror("Error", "❌ Please select a file first.")
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                emails = [line.strip() for line in f if line.strip()]
        except Exception as e:
            messagebox.showerror("Error", f"❌ Could not read file:\n{e}")
            return
        
        if not emails:
            messagebox.showwarning("Warning", "📭 The selected file is empty.")
            return
        
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.summary_var.set(f"🔄 Processing {len(emails)} emails...")
        
        # Process in background to avoid UI freeze
        def process_thread():
            total = len(emails)
            parsed_emails = []
            
            for i, email in enumerate(emails):
                try:
                    parsed = parse_email(email, self.check_disposable.get())
                    parsed_emails.append(parsed)
                    
                    # Update progress
                    progress = (i + 1) / total * 100
                    self.root.after(0, lambda p=progress: self.progress_var.set(p))
                    
                except EmailSliceError:
                    continue
            
            invalid_count = total - len(parsed_emails)
            self.last_parsed_emails = parsed_emails
            
            # Update UI in main thread
            self.root.after(0, lambda: self.update_batch_results(parsed_emails, invalid_count, total))
        
        threading.Thread(target=process_thread, daemon=True).start()
    
    def update_batch_results(self, parsed_emails, invalid_count, total_count):
        """Update batch processing results."""
        # Update summary
        self.summary_var.set(
            f"✅ Processed: {len(parsed_emails)} valid, ❌ {invalid_count} invalid out of {total_count} total emails"
        )
        
        # Update results counter
        self.results_count_var.set(f"({len(parsed_emails)} emails)")
        
        # Clear results text
        self.results_text.delete(1.0, tk.END)
        
        # Add results with formatting
        for i, pe in enumerate(parsed_emails, 1):
            self.results_text.insert(tk.END, f"📧 {i}. {pe.original}\n")
            self.results_text.insert(tk.END, f"   👤 Local: {pe.local_part}\n")
            self.results_text.insert(tk.END, f"   🌐 Domain: {pe.domain}\n")
            
            if pe.tag:
                self.results_text.insert(tk.END, f"   🏷️ Tag: {pe.tag}\n")
            
            if pe.is_disposable:
                self.results_text.insert(tk.END, f"   ⚠️ Disposable email\n")
            
            provider_type = get_email_provider_type(pe.domain)
            self.results_text.insert(tk.END, f"   🏢 Provider: {provider_type.title()}\n")
            
            self.results_text.insert(tk.END, "─" * 50 + "\n\n")
        
        # Show completion toast
        self.show_toast(f"✅ Batch processing complete! {len(parsed_emails)} emails analyzed.", ModernTheme.SUCCESS)
    
    def clear_batch_results(self):
        """Clear batch processing results."""
        self.results_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.summary_var.set("👆 Select a file and click 'Process Batch' to start")
        self.results_count_var.set("(0 emails)")
        self.last_parsed_emails = []
        self.show_toast("🗑️ Results cleared", ModernTheme.SECONDARY)
    
    def export_results(self):
        """Export batch results to JSON file."""
        if not self.last_parsed_emails:
            messagebox.showinfo("Info", "📭 No results to export. Process a batch first.")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Save results as JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                results = [pe.__dict__ for pe in self.last_parsed_emails]
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Success", f"✅ Results exported to:\n{filename}")
                self.show_toast("💾 Results exported successfully!", ModernTheme.SUCCESS)
            except Exception as e:
                messagebox.showerror("Error", f"❌ Could not export results:\n{e}")
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard."""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.show_toast("📋 Copied to clipboard!", ModernTheme.SUCCESS)
    
    def show_toast(self, message, bg_color):
        """Show a toast notification."""
        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True)
        toast.geometry("300x60+{}+{}".format(
            self.root.winfo_rootx() + self.root.winfo_width() // 2 - 150,
            self.root.winfo_rooty() + self.root.winfo_height() // 2 - 30
        ))
        toast.configure(bg=bg_color)
        toast.attributes('-alpha', 0.9)
        
        label = tk.Label(toast, text=message, 
                        fg=ModernTheme.TEXT_LIGHT, bg=bg_color,
                        font=('Arial', 10, 'bold'))
        label.pack(expand=True)
        
        # Auto-close after 2 seconds
        toast.after(2000, toast.destroy)

def main():
    """Main entry point for the GUI."""
    root = tk.Tk()
    app = EmailSlicerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()