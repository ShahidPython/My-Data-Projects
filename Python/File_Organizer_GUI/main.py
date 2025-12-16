import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from organizer import load_config, organize_files, undo_organization
import os

class FileOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📁 Ultimate File Organizer")
        self.root.geometry("800x600")
        self.style = ttkb.Style("darkly")  # Themes: "cosmo", "minty", "superhero"

        # Variables
        self.folder_path = tk.StringVar()
        self.moves = []  # Tracks file movements for undo
        self.mapping = self.load_config_safe()

        # GUI Setup
        self.setup_gui()

    def load_config_safe(self):
        """Load config with fallback to default if missing."""
        try:
            return load_config()
        except Exception as e:
            messagebox.showwarning("Config Warning", 
                                f"Using default rules. Error: {str(e)}")
            return {
                "Other_File_Types": []  # Fallback
            }

    def setup_gui(self):
        # Header Frame
        header = ttkb.Frame(self.root)
        header.pack(fill="x", padx=10, pady=10)

        ttkb.Label(
            header,
            text="📂 Ultimate File Organizer",
            font=("Helvetica", 18, "bold"),
        ).pack(side="left")

        # Theme Toggle Button
        ttkb.Button(
            header,
            text="🌙 Dark / ☀️ Light",
            command=self.toggle_theme,
            bootstyle="outline",
        ).pack(side="right")

        # Folder Selection Frame
        folder_frame = ttkb.Frame(self.root)
        folder_frame.pack(fill="x", padx=10, pady=5)

        ttkb.Entry(
            folder_frame,
            textvariable=self.folder_path,
            width=60,
        ).pack(side="left", padx=5)

        ttkb.Button(
            folder_frame,
            text="Browse Folder",
            command=self.browse_folder,
            bootstyle="primary",
        ).pack(side="left")

        # Action Buttons Frame
        button_frame = ttkb.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=10)

        ttkb.Button(
            button_frame,
            text="🔄 Organize Files",
            command=self.organize,
            bootstyle="success",
        ).pack(side="left", padx=5)

        ttkb.Button(
            button_frame,
            text="⏪ Undo Last Move",
            command=self.undo,
            bootstyle="danger",
            state="disabled",
        ).pack(side="left", padx=5)
        self.undo_btn = button_frame.winfo_children()[-1]

        # Progress Bar
        self.progress = ttkb.Progressbar(
            self.root,
            orient="horizontal",
            mode="determinate",
            bootstyle="success-striped",
        )
        self.progress.pack(fill="x", padx=10, pady=5)

        # Log Console
        self.log = scrolledtext.ScrolledText(
            self.root,
            height=20,
            wrap="word",
            font=("Consolas", 10),
            state="disabled",
        )
        self.log.pack(fill="both", expand=True, padx=10, pady=5)

    def browse_folder(self):
        """Open folder dialog and update path."""
        folder = filedialog.askdirectory(title="Select Folder to Organize")
        if folder:
            self.folder_path.set(folder)
            self.log_message(f"📌 Selected folder: {folder}")

    def log_message(self, msg: str):
        """Append message to log console."""
        self.log.config(state="normal")
        self.log.insert("end", f"> {msg}\n")
        self.log.config(state="disabled")
        self.log.see("end")

    def toggle_theme(self):
        """Switch between light/dark themes."""
        current = self.style.theme.name
        new_theme = "cosmo" if current == "darkly" else "darkly"
        self.style.theme_use(new_theme)
        self.log_message(f"🎨 Switched to {new_theme} theme")

    def organize(self):
        """Organize files in the selected folder."""
        folder = self.folder_path.get()
        if not folder:
            messagebox.showwarning("Warning", "Please select a folder first!")
            return

        self.log_message("🔍 Scanning files...")
        self.progress["value"] = 20

        try:
            # Dry run first
            self.moves = organize_files(folder, self.mapping, dry_run=True)
            self.progress["value"] = 50

            if not self.moves:
                self.log_message("ℹ No files to organize.")
                return

            # Show planned moves
            self.log_message("📋 Organization plan:")
            for src, dest in self.moves:
                self.log_message(f"{os.path.basename(src)} → {os.path.dirname(dest)}")

            # Confirm before actual move
            confirm = messagebox.askyesno(
                "Confirm",
                f"Organize {len(self.moves)} files?",
                detail="Backup your files first if unsure."
            )
            if confirm:
                organize_files(folder, self.mapping, dry_run=False)
                self.log_message("✅ Files organized successfully!")
                self.undo_btn.config(state="normal")
                self.progress["value"] = 100
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log_message(f"❌ Error: {str(e)}")
            self.progress["value"] = 0

    def undo(self):
        """Revert the last organization."""
        if not self.moves:
            return

        try:
            undo_organization(self.moves)
            self.log_message("⏪ Undo successful! Files restored.")
            self.undo_btn.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log_message(f"❌ Undo failed: {str(e)}")

if __name__ == "__main__":
    app = ttkb.Window("Ultimate File Organizer")
    FileOrganizerApp(app)
    app.mainloop()