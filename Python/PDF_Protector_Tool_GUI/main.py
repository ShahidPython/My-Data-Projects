import os
import sys
import tempfile
from pathlib import Path

# Set environment variables to prevent X11 issues at the very beginning
os.environ['DISPLAY'] = ':0'
os.environ['QT_X11_NO_MITSHM'] = '1'
os.environ['TK_SILENCE_DEPRECATION'] = '1'

try:
    from tkinter import *
    from tkinter import filedialog, messagebox
    GUI_AVAILABLE = True
except ImportError as e:
    print(f"GUI not available: {e}")
    GUI_AVAILABLE = False

try:
    from PyPDF2 import PdfReader, PdfWriter
    PYPDF2_AVAILABLE = True
except ImportError:
    print("PyPDF2 not available")
    PYPDF2_AVAILABLE = False

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    print("PIL/Pillow not available")
    PIL_AVAILABLE = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class PDFProtector:
    """PDF protection functionality (works with or without GUI)"""
    
    @staticmethod
    def protect_pdf(input_path, password, output_path):
        """Protect a PDF file with password"""
        if not PYPDF2_AVAILABLE:
            raise ImportError("PyPDF2 is required for PDF protection")
        
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        if not password:
            raise ValueError("Password cannot be empty")
        
        out = PdfWriter()
        file = PdfReader(input_path)

        for page in file.pages:
            out.add_page(page)

        # Encrypt with password
        out.encrypt(password)

        # Save protected PDF
        with open(output_path, "wb") as f:
            out.write(f)
        
        return output_path

class PDFProtectorGUI:
    """GUI version of PDF Protector"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Protector")
        self.root.geometry("600x500+300+100")  # Increased window height from 430 to 500
        self.root.resizable(False, False)
        self.root.configure(bg='#f5f5f5')
        
        # Set window icon
        self.set_window_icon()
        
        self.filename = ""
        self.images_loaded = False
        
        # Initialize UI
        self.setup_ui()
        
    def set_window_icon(self):
        """Set window icon with fallback"""
        try:
            # Try to use built-in icon first
            self.root.iconbitmap()  # This might work on some systems
        except:
            try:
                # Try to create a simple icon using tkinter
                icon = PhotoImage(width=16, height=16)
                self.root.iconphoto(True, icon)
            except:
                pass  # Icon setting is optional
    
    def safe_load_image(self, image_path, default_width=None, default_height=None):
        """Safely load images with multiple fallback strategies"""
        try:
            if PIL_AVAILABLE and os.path.exists(image_path):
                pil_image = Image.open(image_path)
                
                if default_width and default_height:
                    pil_image = pil_image.resize((default_width, default_height), Image.Resampling.LANCZOS)
                
                return ImageTk.PhotoImage(pil_image)
            else:
                print(f"Image not available: {image_path}")
                return None
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return None
    
    def setup_ui(self):
        """Setup the user interface with safe image handling"""
        # Create header
        self.create_header()
        
        # Create main input frame
        self.create_main_frame()
        
        # Create protect button
        self.create_protect_button()
        
        # Create status bar
        self.create_status_bar()
        
        # Force initial render
        self.root.update_idletasks()
    
    def create_header(self):
        """Create header section"""
        header_frame = Frame(self.root, bg='#2c3e50', height=130)
        header_frame.pack(fill=X)
        header_frame.pack_propagate(False)
        
        # Icon
        icon_label = Label(header_frame, text="🔒", font=("Arial", 24),
                          fg="white", bg="#2c3e50")
        icon_label.pack(pady=(10, 0))
        
        # Title
        title_label = Label(header_frame, text="PDF PROTECTOR", 
                          font=("Arial", 20, "bold"), 
                          fg="white", bg="#2c3e50")
        title_label.pack(pady=(5, 0))
        
        # Subtitle
        subtitle_label = Label(header_frame, 
                             text="Secure Your PDF Files with Password Protection",
                             font=("Arial", 10), 
                             fg="#ecf0f1", bg="#2c3e50")
        subtitle_label.pack(pady=(0, 10))
    
    def create_main_frame(self):
        """Create the main input frame"""
        self.main_frame = Frame(self.root, width=580, height=230, 
                               bg="white", bd=2, relief=GROOVE)
        self.main_frame.place(x=10, y=140)
        self.main_frame.pack_propagate(False)
        
        # File selection section
        self.create_file_section()
        
        # Password section
        self.create_password_section()
        
        # Instructions
        self.create_instructions()
    
    def create_file_section(self):
        """Create file selection section"""
        # Label
        file_label = Label(self.main_frame, text="Select PDF File:", 
                          font=("Arial", 11, "bold"), 
                          fg="#2c3e50", bg="white")
        file_label.place(x=30, y=40)
        
        # Entry field
        self.file_entry = Entry(self.main_frame, width=32, 
                               font=("Arial", 12), 
                               bd=1, relief=SOLID, highlightthickness=1,
                               highlightcolor="#3498db", highlightbackground="#bdc3c7")
        self.file_entry.place(x=160, y=38)
        
        # Browse button - Adjusted position to be properly aligned
        browse_btn = Button(self.main_frame, text="BROWSE", 
                          font=("Arial", 9, "bold"),
                          bg="#3498db", fg="white", 
                          command=self.browse, cursor="hand2",
                          width=8, height=1)
        browse_btn.place(x=470, y=36)  # Changed from x=500 to x=470
    
    def create_password_section(self):
        """Create password input section"""
        # Label
        pass_label = Label(self.main_frame, text="Set Password:", 
                          font=("Arial", 11, "bold"), 
                          fg="#2c3e50", bg="white")
        pass_label.place(x=30, y=100)
        
        # Password entry
        self.pass_entry = Entry(self.main_frame, width=32, 
                               font=("Arial", 12), show="•",
                               bd=1, relief=SOLID, highlightthickness=1,
                               highlightcolor="#3498db", highlightbackground="#bdc3c7")
        self.pass_entry.place(x=160, y=98)
        
        # Show password checkbox
        self.show_pass_var = BooleanVar()
        show_pass_cb = Checkbutton(self.main_frame, text="Show password",
                                 variable=self.show_pass_var,
                                 command=self.toggle_password_visibility,
                                 bg="white", font=("Arial", 9))
        show_pass_cb.place(x=160, y=125)
        
        # Bind Enter key to protect function
        self.pass_entry.bind('<Return>', lambda e: self.protect_pdf())
    
    def create_instructions(self):
        """Create instructions section - Adjusted position"""
        instructions = [
            "• Select a PDF file to protect",
            "• Set a strong password", 
            "• Choose save location for protected file"
        ]
        
        for i, instruction in enumerate(instructions):
            label = Label(self.main_frame, text=instruction,
                         font=("Arial", 9), fg="#7f8c8d", bg="white",
                         justify=LEFT)
            label.place(x=30, y=150 + i*20)  # Changed from 160 to 150 to move up
    
    def create_protect_button(self):
        """Create the main protect button - Moved further down"""
        self.protect_btn = Button(self.root, 
                                text="🔒 PROTECT PDF FILE", 
                                font=("Arial", 14, "bold"),
                                fg="white", bg="#e74c3c",
                                command=self.protect_pdf,
                                cursor="hand2",
                                width=20, height=2)
        # Moved the button much further down with increased pady
        self.protect_btn.pack(side=BOTTOM, pady=50)  # Changed from pady=20 to pady=50
    
    def create_status_bar(self):
        """Create status bar - positioned above the protect button"""
        self.status_var = StringVar()
        self.status_var.set("Ready")
        
        status_bar = Label(self.root, textvariable=self.status_var,
                         font=("Arial", 8), fg="#7f8c8d", bg="#f5f5f5",
                         bd=1, relief=SUNKEN, anchor=W)
        status_bar.pack(side=BOTTOM, fill=X, before=self.protect_btn)  # Added before parameter
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.show_pass_var.get():
            self.pass_entry.config(show="")
        else:
            self.pass_entry.config(show="•")
    
    def browse(self):
        """Handle file browsing"""
        filename = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Select PDF File",
            filetypes=(("PDF Files", "*.pdf"), ("All Files", "*.*"))  # FIXED: Changed filetype to filetypes
        )
        if filename:
            self.filename = filename
            self.file_entry.delete(0, END)
            self.file_entry.insert(END, filename)
            self.status_var.set(f"Selected: {os.path.basename(filename)}")
    
    def protect_pdf(self):
        """Protect the PDF with password"""
        mainfile = self.file_entry.get()
        code = self.pass_entry.get()    

        if not mainfile:
            messagebox.showerror("Error", "Please select a PDF file first!")
            return
            
        if not code:
            messagebox.showerror("Error", "Please enter a password!")
            return

        # Ask for save location
        protectfile = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],  # FIXED: This one was already correct
            title="Save Protected PDF As"
        )
        
        if not protectfile:
            return

        try:
            # Update UI to show processing
            original_text = self.protect_btn.cget('text')
            self.protect_btn.config(text="🔄 Processing...", state=DISABLED)
            self.status_var.set("Protecting PDF...")
            self.root.update()
            
            # Process PDF
            PDFProtector.protect_pdf(mainfile, code, protectfile)

            # Success message
            messagebox.showinfo("Success", 
                              f"✅ PDF Protected Successfully!\n\n"
                              f"📁 Saved at: {protectfile}\n"
                              f"🔑 Password has been set successfully!\n\n"
                              f"Keep your password safe!")
            
            # Reset form
            self.pass_entry.delete(0, END)
            self.status_var.set("Ready - PDF protected successfully!")

        except Exception as e:
            error_msg = str(e)
            messagebox.showerror("Error", 
                               f"❌ Failed to protect PDF:\n\n{error_msg}")
            self.status_var.set(f"Error: {error_msg}")
        finally:
            # Reset button state
            self.protect_btn.config(text="🔒 PROTECT PDF FILE", state=NORMAL)

class PDFProtectorCLI:
    """Command Line Interface version"""
    
    @staticmethod
    def get_input(prompt, password=False):
        """Get user input with optional password masking"""
        if password:
            try:
                import getpass
                return getpass.getpass(prompt)
            except:
                print("Warning: Password will be visible")
                return input(prompt)
        return input(prompt).strip()
    
    @staticmethod
    def run():
        """Run the CLI version"""
        print("\n" + "="*50)
        print("           PDF PROTECTOR (CLI VERSION)")
        print("="*50)
        
        if not PYPDF2_AVAILABLE:
            print("❌ Error: PyPDF2 is required but not available.")
            print("Install it with: pip install PyPDF2")
            return
        
        # Get input file
        while True:
            input_file = PDFProtectorCLI.get_input("\n📁 Enter path to PDF file: ")
            if os.path.exists(input_file):
                if input_file.lower().endswith('.pdf'):
                    break
                else:
                    print("❌ Please select a PDF file (.pdf extension)")
            else:
                print("❌ File not found. Please check the path.")
        
        # Get password
        while True:
            password = PDFProtectorCLI.get_input("🔑 Enter password: ", password=True)
            confirm_password = PDFProtectorCLI.get_input("🔑 Confirm password: ", password=True)
            
            if password == confirm_password:
                if password:
                    break
                else:
                    print("❌ Password cannot be empty.")
            else:
                print("❌ Passwords don't match. Please try again.")
        
        # Get output file
        default_output = "protected_" + os.path.basename(input_file)
        output_file = PDFProtectorCLI.get_input(f"\n💾 Output filename [{default_output}]: ")
        if not output_file:
            output_file = default_output
        if not output_file.lower().endswith('.pdf'):
            output_file += '.pdf'
        
        try:
            print("\n🔄 Protecting PDF...")
            
            # Process PDF
            output_path = PDFProtector.protect_pdf(input_file, password, output_file)
            
            print(f"✅ PDF Protected Successfully!")
            print(f"📁 Saved at: {os.path.abspath(output_path)}")
            print("🔑 Password has been set successfully!")
            print("\n⚠️  Keep your password safe and secure!")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def check_dependencies():
    """Check and report on required dependencies"""
    print("Checking dependencies...")
    
    if not PYPDF2_AVAILABLE:
        print("❌ PyPDF2 is not installed.")
        print("   Install with: pip install PyPDF2")
        return False
    
    print("✅ PyPDF2 is available")
    
    if not GUI_AVAILABLE:
        print("❌ GUI (tkinter) is not available.")
        print("   On Ubuntu/Debian, install with: sudo apt-get install python3-tk")
        return False
    
    print("✅ GUI (tkinter) is available")
    return True

def main():
    """Main function with comprehensive error handling"""
    print("Starting PDF Protector Application...")
    
    # Check if we're in a GUI-capable environment
    if GUI_AVAILABLE and 'DISPLAY' in os.environ:
        try:
            # Try to create GUI version
            root = Tk()
            
            # Additional safety measures
            root.attributes('-type', 'dialog')  # Try to force window type
            root.update_idletasks()
            
            # Center the window
            root.update_idletasks()
            x = (root.winfo_screenwidth() // 2) - (600 // 2)
            y = (root.winfo_screenheight() // 2) - (500 // 2)  # Updated for new height
            root.geometry(f"+{x}+{y}")
            
            app = PDFProtectorGUI(root)
            
            print("✅ GUI version started successfully!")
            print("💡 Tip: If GUI has issues, run with --cli flag")
            
            # Start main loop
            root.mainloop()
            return
            
        except Exception as e:
            print(f"❌ GUI failed: {e}")
            print("🔄 Falling back to CLI version...")
    
    # Use CLI version
    PDFProtectorCLI.run()

if __name__ == "__main__":
    # Handle command line arguments
    if len(sys.argv) > 1 and sys.argv[1] in ['--cli', '-c']:
        PDFProtectorCLI.run()
    elif len(sys.argv) > 1 and sys.argv[1] in ['--check', '-ch']:
        check_dependencies()
    elif len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("PDF Protector Usage:")
        print("  python pdf_protector.py          # Auto-detect (GUI/CLI)")
        print("  python pdf_protector.py --cli    # Force CLI version")
        print("  python pdf_protector.py --check  # Check dependencies")
        print("  python pdf_protector.py --help   # Show this help")
    else:
        main()