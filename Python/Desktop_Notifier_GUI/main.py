#!/usr/bin/env python3
"""
Desktop Notifier - Clean Dark Theme Version

Features:
✔ Persistent dark theme
✔ Cross-platform notifications
✔ Clean interface
✔ Fixed all known errors
"""

import os
import json
import time
import logging
import threading
import platform
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

# Auto-install missing dependencies
try:
    from plyer import notification as plyer_notification
    HAS_PLYER = True
except ImportError:
    try:
        import pip
        pip.main(['install', 'plyer'])
        from plyer import notification as plyer_notification
        HAS_PLYER = True
    except Exception:
        HAS_PLYER = False

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="notifier.log"
)
logger = logging.getLogger(__name__)

# Constants
SETTINGS_FILE = "notifier_settings.json"
DARK_THEME = {
    "bg": "#2d2d2d",
    "fg": "#ffffff",
    "button_bg": "#3e3e3e",
    "entry_bg": "#424242",
    "text_bg": "#333333"
}

class NotifierApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Desktop Notifier")
        self.root.geometry("500x450")
        self.root.resizable(False, False)
        
        # Always use dark theme
        self.current_theme = DARK_THEME
        
        # Variables
        self.title_var = tk.StringVar(value="Reminder")
        self.message_var = tk.StringVar(value="Time to take a break!")
        self.interval_var = tk.StringVar(value="30")
        self.unit_var = tk.StringVar(value="minutes")
        self.running = False
        self.job_id = None
        self.countdown_job = None
        
        # Load settings
        self.load_settings()
        
        # Build UI
        self.setup_ui()
        self.apply_theme()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def setup_ui(self):
        """Create the user interface using grid layout only."""
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        
        # Header
        header_frame = tk.Frame(self.root)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        
        tk.Label(
            header_frame,
            text="Desktop Notifier",
            font=("Helvetica", 16, "bold")
        ).pack(side="left")
        
        # Main content
        content_frame = tk.Frame(self.root)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        content_frame.columnconfigure(1, weight=1)
        
        # Title
        tk.Label(
            content_frame,
            text="Title",
            font=("Helvetica", 10)
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        title_entry = tk.Entry(
            content_frame,
            textvariable=self.title_var,
            font=("Helvetica", 10)
        )
        title_entry.grid(row=0, column=1, sticky="ew", pady=(0, 5))
        
        # Message
        tk.Label(
            content_frame,
            text="Message",
            font=("Helvetica", 10)
        ).grid(row=1, column=0, sticky="nw", pady=(5, 0))
        
        self.message_text = tk.Text(
            content_frame,
            height=5,
            width=50,
            wrap="word",
            font=("Helvetica", 10),
            padx=5,
            pady=5
        )
        self.message_text.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self.message_text.insert("1.0", self.message_var.get())
        
        # Interval
        interval_frame = tk.Frame(content_frame)
        interval_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        
        tk.Label(
            interval_frame,
            text="Interval:",
            font=("Helvetica", 10)
        ).pack(side="left")
        
        interval_entry = tk.Entry(
            interval_frame,
            textvariable=self.interval_var,
            width=8,
            font=("Helvetica", 10),
            justify="center"
        )
        interval_entry.pack(side="left", padx=5)
        
        self.unit_menu = ttk.Combobox(
            interval_frame,
            textvariable=self.unit_var,
            values=["seconds", "minutes", "hours"],
            state="readonly",
            width=8,
            font=("Helvetica", 10)
        )
        self.unit_menu.pack(side="left")
        
        # Buttons
        button_frame = tk.Frame(content_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(5, 15))
        
        self.start_btn = tk.Button(
            button_frame,
            text="▶ Start",
            command=self.start_notifications,
            font=("Helvetica", 10, "bold"),
            padx=10
        )
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = tk.Button(
            button_frame,
            text="⏹ Stop",
            command=self.stop_notifications,
            state="disabled",
            font=("Helvetica", 10),
            padx=10
        )
        self.stop_btn.pack(side="left", padx=5)
        
        self.test_btn = tk.Button(
            button_frame,
            text="🔔 Test",
            command=self.test_now,
            font=("Helvetica", 10),
            padx=10
        )
        self.test_btn.pack(side="left", padx=5)
        
        # Status
        status_frame = tk.Frame(content_frame)
        status_frame.grid(row=5, column=0, columnspan=2, pady=(10, 0))
        
        self.status_label = tk.Label(
            status_frame,
            text="Status: Ready",
            font=("Helvetica", 10)
        )
        self.status_label.pack()
        
        self.countdown_label = tk.Label(
            status_frame,
            text="Next notification: --:--:--",
            font=("Courier New", 12, "bold")
        )
        self.countdown_label.pack(pady=(5, 0))
    
    def apply_theme(self):
        """Apply the dark theme colors."""
        # Apply to root window first
        self.root.configure(bg=self.current_theme["bg"])
        
        # Apply to all widgets
        for widget in self.root.winfo_children():
            self.apply_theme_to_widget(widget, self.current_theme)
    
    def apply_theme_to_widget(self, widget, theme):
        """Recursively apply theme to widget and its children."""
        if isinstance(widget, tk.Frame):
            try:
                widget.configure(bg=theme["bg"])
            except:
                pass
        
        elif isinstance(widget, (tk.Label, tk.Button)):
            try:
                widget.configure(
                    bg=theme["bg"] if isinstance(widget, tk.Label) else theme["button_bg"],
                    fg=theme["fg"]
                )
            except:
                pass
        
        elif isinstance(widget, tk.Entry):
            try:
                widget.configure(
                    bg=theme["entry_bg"],
                    fg=theme["fg"],
                    insertbackground=theme["fg"],
                    selectbackground="#4a98f7",
                    selectforeground="white"
                )
            except:
                pass
        
        elif isinstance(widget, tk.Text):
            try:
                widget.configure(
                    bg=theme["text_bg"],
                    fg=theme["fg"],
                    insertbackground=theme["fg"],
                    selectbackground="#4a98f7",
                    selectforeground="white"
                )
            except:
                pass
        
        for child in widget.winfo_children():
            self.apply_theme_to_widget(child, theme)
    
    def send_notification(self, title, message):
        """Send a system notification."""
        try:
            if HAS_PLYER:
                plyer_notification.notify(
                    title=title,
                    message=message,
                    app_name="Desktop Notifier",
                    timeout=10
                )
                return
        except Exception as e:
            logger.error(f"Notification failed: {e}")
        
        # Fallback methods
        system = platform.system()
        try:
            if system == "Windows":
                subprocess.run(['powershell', '-command', f'[System.Windows.Forms.MessageBox]::Show("{message}", "{title}")'])
            elif system == "Darwin":
                subprocess.run(['osascript', '-e', f'display notification "{message}" with title "{title}"'])
            else:
                subprocess.run(['notify-send', title, message])
        except Exception as e:
            logger.error(f"Fallback failed: {e}")
            messagebox.showinfo(title, message)
    
    def start_notifications(self):
        """Start the notification cycle."""
        if self.running:
            return
        
        # Validate input
        try:
            interval = float(self.interval_var.get())
            if interval <= 0:
                raise ValueError("Interval must be positive")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid interval: {e}")
            return
        
        message = self.message_text.get("1.0", "end").strip()
        if not message:
            messagebox.showerror("Error", "Message cannot be empty!")
            return
        
        # Calculate interval in seconds
        unit = self.unit_var.get()
        if unit == "minutes":
            interval_sec = interval * 60
        elif unit == "hours":
            interval_sec = interval * 3600
        else:
            interval_sec = interval
        
        # Save settings
        self.save_settings()
        
        # Start notifications
        self.running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.next_notification = time.time() + interval_sec
        
        self.status_label.config(text="Status: Running", fg="#4CAF50")
        self.update_countdown()
        self.schedule_notification(interval_sec)
    
    def schedule_notification(self, interval_sec):
        """Schedule the next notification."""
        if not self.running:
            return
        
        self.job_id = self.root.after(
            int(interval_sec * 1000),
            self.send_scheduled_notification,
            interval_sec
        )
    
    def send_scheduled_notification(self, interval_sec):
        """Send notification and reschedule."""
        title = self.title_var.get() or "Reminder"
        message = self.message_text.get("1.0", "end").strip()
        
        threading.Thread(
            target=self.send_notification,
            args=(title, message),
            daemon=True
        ).start()
        
        if self.running:
            self.next_notification = time.time() + interval_sec
            self.schedule_notification(interval_sec)
    
    def update_countdown(self):
        """Update the countdown display."""
        if not self.running:
            return
        
        remaining = max(0, int(self.next_notification - time.time()))
        h, m, s = remaining // 3600, (remaining % 3600) // 60, remaining % 60
        self.countdown_label.config(text=f"Next: {h:02d}:{m:02d}:{s:02d}")
        
        self.countdown_job = self.root.after(1000, self.update_countdown)
    
    def stop_notifications(self):
        """Stop all notifications."""
        if not self.running:
            return
        
        self.running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        
        if self.job_id:
            self.root.after_cancel(self.job_id)
        if self.countdown_job:
            self.root.after_cancel(self.countdown_job)
        
        self.status_label.config(text="Status: Stopped", fg="#F44336")
        self.countdown_label.config(text="Next notification: --:--:--")
    
    def test_now(self):
        """Send a test notification."""
        title = self.title_var.get() or "Reminder"
        message = self.message_text.get("1.0", "end").strip() or "Test notification"
        threading.Thread(
            target=self.send_notification,
            args=(title, message),
            daemon=True
        ).start()
    
    def save_settings(self):
        """Save current settings to file."""
        settings = {
            "title": self.title_var.get(),
            "message": self.message_text.get("1.0", "end").strip(),
            "interval": self.interval_var.get(),
            "unit": self.unit_var.get()
        }
        
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(settings, f)
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
    
    def load_settings(self):
        """Load settings from file."""
        if not os.path.exists(SETTINGS_FILE):
            return
        
        try:
            with open(SETTINGS_FILE, "r") as f:
                settings = json.load(f)
                self.title_var.set(settings.get("title", "Reminder"))
                self.message_var.set(settings.get("message", "Time to take a break!"))
                self.interval_var.set(settings.get("interval", "30"))
                self.unit_var.set(settings.get("unit", "minutes"))
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
    
    def on_close(self):
        """Handle window closing."""
        self.stop_notifications()
        self.save_settings()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = NotifierApp(root)
    root.mainloop()