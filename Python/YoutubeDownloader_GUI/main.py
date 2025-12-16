import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import yt_dlp
import sys
from PIL import Image, ImageTk
import subprocess

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.quality_var = tk.StringVar(value="best")  # Initialize first
        self.download_path = os.path.expanduser("~/Downloads")
        self.cancel_requested = False
        self.setup_dark_theme()
        self.create_widgets()
        
    def setup_dark_theme(self):
        self.root.title("YouTube Downloader")
        self.root.geometry("650x450")
        self.root.configure(bg='#121212')
        self.root.resizable(False, False)
        
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TFrame', background='#121212')
        style.configure('TLabel', background='#121212', foreground='white')
        style.configure('TButton', 
                      background='#333333', 
                      foreground='white',
                      bordercolor='#444444')
        
        style.map('Red.TButton',
                background=[('active', '#FF0000'), ('!active', '#FF3333')],
                foreground=[('active', 'white'), ('!disabled', 'white')])
        
        style.configure('Red.TButton', 
                      background='#FF3333',
                      foreground='white',
                      font=('Helvetica', 10, 'bold'),
                      bordercolor='#FF0000',
                      focusthickness=3,
                      focuscolor='#121212')
        
        style.configure('TEntry', 
                      fieldbackground='#333333', 
                      foreground='white',
                      bordercolor='#87CEEB',
                      lightcolor='#87CEEB',
                      darkcolor='#87CEEB')
        
        style.configure('TRadiobutton',
                      background='#121212',
                      foreground='white')
        
        style.configure('Horizontal.TProgressbar', 
                      background='#4CAF50',
                      troughcolor='#333333',
                      bordercolor='#121212',
                      lightcolor='#4CAF50',
                      darkcolor='#4CAF50')
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        # Header
        header = ttk.Label(main_frame, 
                         text="YouTube Video Downloader",
                         font=('Helvetica', 16, 'bold'),
                         foreground='#FF3333')
        header.pack(pady=(0, 15))
        
        # URL Entry
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill='x', pady=10)
        ttk.Label(url_frame, text="YouTube URL:", foreground='#87CEEB').pack(side='left')
        self.url_entry = ttk.Entry(url_frame, width=50, style='TEntry')
        self.url_entry.pack(side='left', fill='x', expand=True, padx=10)
        
        # Quality Selection
        quality_frame = ttk.Frame(main_frame)
        quality_frame.pack(fill='x', pady=10)
        ttk.Label(quality_frame, text="Quality:", foreground='#87CEEB').pack(side='left')
        
        qualities = [
            ("Best Quality", "best"),
            ("1080p", "1080"),
            ("720p", "720"),
            ("480p", "480"),
            ("360p", "360"),
            ("Audio Only", "audio")
        ]
        
        for text, quality in qualities:
            ttk.Radiobutton(
                quality_frame,
                text=text,
                variable=self.quality_var,
                value=quality,
                style='TRadiobutton'
            ).pack(side='left', padx=5)
        
        # Save Location
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill='x', pady=10)
        ttk.Button(
            path_frame,
            text="Browse Save Location",
            command=self.choose_download_path,
            style='TButton'
        ).pack(side='left')
        self.path_label = ttk.Label(
            path_frame,
            text=self.download_path,
            foreground='white',
            wraplength=400
        )
        self.path_label.pack(side='left', padx=10, fill='x', expand=True)
        
        # Progress Frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill='x', pady=15)
        
        self.progress = ttk.Progressbar(
            progress_frame,
            style='Horizontal.TProgressbar',
            length=500,
            mode='determinate'
        )
        self.progress.pack(side='left', fill='x', expand=True)
        
        self.percent_label = ttk.Label(
            progress_frame,
            text="0%",
            foreground='white',
            width=5
        )
        self.percent_label.pack(side='left', padx=10)
        
        # Status
        self.status = ttk.Label(
            main_frame,
            text="Ready to download",
            foreground='#4CAF50',
            wraplength=500
        )
        self.status.pack(pady=10)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)
        
        self.download_btn = ttk.Button(
            btn_frame,
            text="DOWNLOAD",
            style='Red.TButton',
            command=self.start_download
        )
        self.download_btn.grid(row=0, column=0, padx=10)
        
        self.cancel_btn = ttk.Button(
            btn_frame,
            text="Cancel",
            command=self.cancel_download,
            state='disabled'
        )
        self.cancel_btn.grid(row=0, column=1, padx=10)
    
    def choose_download_path(self):
        path = filedialog.askdirectory(initialdir=self.download_path)
        if path:
            self.download_path = path
            self.path_label.config(text=path)
    
    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
            
        if "youtube.com" not in url and "youtu.be" not in url:
            messagebox.showerror("Error", "Invalid YouTube URL")
            return
            
        self.status.config(text="Connecting...", foreground='#FFA500')
        self.download_btn.config(state='disabled')
        self.cancel_btn.config(state='normal')
        self.progress['value'] = 0
        self.percent_label.config(text="0%")
        self.cancel_requested = False
        
        import threading
        threading.Thread(
            target=self.download_video,
            args=(url,),
            daemon=True
        ).start()
        
    def download_video(self, url):
        try:
            quality = self.quality_var.get()
            ydl_opts = {
                'progress_hooks': [self.ytdlp_progress_hook],
                'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_color': True,
                'format': self.get_format_selector(quality),
                'noplaylist': True,
                # Anti-bot measures
                'extractor_retries': 3,
                'ignoreerrors': True,
                'no_warnings': False,
                'sleep_interval': 1,
                'max_sleep_interval': 5,
                # Use modern YouTube extractor
                'extract_flat': False,
            }

            # Add ffmpeg location if available
            ffmpeg_path = self.find_ffmpeg()
            if ffmpeg_path:
                ydl_opts['ffmpeg_location'] = ffmpeg_path

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # First get video info
                self.root.after(0, lambda: self.status.config(
                    text="Getting video information...",
                    foreground='#1E90FF'
                ))
                
                info = ydl.extract_info(url, download=False)
                self.video_title = info.get('title', 'video')
                self.file_path = os.path.join(
                    self.download_path,
                    ydl.prepare_filename(info)
                )
                
                # Then download if not cancelled
                if not self.cancel_requested:
                    self.root.after(0, lambda: self.status.config(
                        text=f"Starting download: {self.video_title[:40]}...",
                        foreground='#1E90FF'
                    ))
                    ydl.download([url])
                    
                    if not self.cancel_requested:
                        self.root.after(0, lambda: self.status.config(
                            text=f"Download completed: {os.path.basename(self.file_path)}",
                            foreground='#4CAF50'
                        ))
                        self.root.after(0, lambda: messagebox.showinfo(
                            "Success",
                            f"Saved to:\n{self.file_path}"
                        ))

        except Exception as e:
            if not self.cancel_requested:
                error_message = str(e)
                # Provide more user-friendly error messages
                if "Sign in" in error_message or "bot" in error_message:
                    error_message = "YouTube is blocking automated downloads. Please try again later or update yt-dlp."
                elif "Unsupported URL" in error_message:
                    error_message = "Unsupported URL or video not available."
                
                self.root.after(0, lambda msg=error_message: [
                    self.status.config(text=f"Error: {msg}", foreground='#FF6347'),
                    messagebox.showerror("Download Error", msg)
                ])
        finally:
            self.root.after(0, lambda: [
                self.download_btn.config(state='normal'),
                self.cancel_btn.config(state='disabled')
            ])
    
    def find_ffmpeg(self):
        """Find FFmpeg executable"""
        possible_paths = [
            '/usr/bin/ffmpeg',
            '/usr/local/bin/ffmpeg',
            '/bin/ffmpeg',
            'ffmpeg'
        ]
        
        for path in possible_paths:
            try:
                if os.path.exists(path) or subprocess.run(['which', 'ffmpeg'], capture_output=True).returncode == 0:
                    return path
            except:
                continue
        return None
    
    def get_format_selector(self, quality):
        """Get format selector that avoids complex merging"""
        if quality == "best":
            # Prefer single file downloads
            return "best[ext=mp4]/best[height<=1080]/best"
        elif quality == "audio":
            return "bestaudio[ext=m4a]/bestaudio/best"
        elif quality == "1080":
            return "best[height<=1080][ext=mp4]/best[height<=1080]/best"
        elif quality == "720":
            return "best[height<=720][ext=mp4]/best[height<=720]/best"
        elif quality == "480":
            return "best[height<=480][ext=mp4]/best[height<=480]/best"
        elif quality == "360":
            return "best[height<=360][ext=mp4]/best[height<=360]/best"
        else:
            return "best"
    
    def ytdlp_progress_hook(self, d):
        if d['status'] == 'downloading' and not self.cancel_requested:
            try:
                percent_str = d.get('_percent_str', '0%').strip().replace('%', '')
                if percent_str and percent_str != 'NA':
                    percent = float(percent_str)
                    self.root.after(0, lambda p=percent: [
                        self.progress.config(value=p),
                        self.percent_label.config(text=f"{p:.1f}%"),
                        self.status.config(
                            text=f"Downloading: {self.video_title[:40]}..." if len(self.video_title) > 40 else f"Downloading: {self.video_title}",
                            foreground='#1E90FF'
                        )
                    ])
            except (ValueError, TypeError):
                pass
        elif d['status'] == 'finished' and not self.cancel_requested:
            self.root.after(0, lambda: [
                self.progress.config(value=100),
                self.percent_label.config(text="100%")
            ])
    
    def cancel_download(self):
        self.cancel_requested = True
        self.status.config(text="Cancelling download...", foreground='#FF6347')
        self.cancel_btn.config(state='disabled')

def load_app_icon(root):
    """Robust icon loading that works in all environments"""
    try:
        # Get correct base path (works for .py and packaged .exe)
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        
        # Try different icon formats and locations
        icon_paths = [
            os.path.join(base_path, "icon.ico"),  # Windows preferred
            os.path.join(base_path, "assets", "icon.ico"),  # Common alternative
            os.path.join(base_path, "icon.png"),  # Cross-platform
            os.path.join(base_path, "assets", "icon.png")
        ]
        
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                if icon_path.endswith('.ico'):
                    root.iconbitmap(icon_path)  # Windows native method
                    return True
                else:
                    try:
                        img = Image.open(icon_path)
                        photo = ImageTk.PhotoImage(img)
                        root.iconphoto(True, photo)  # Cross-platform method
                        root._icon = photo  # Prevent garbage collection
                        return True
                    except Exception as e:
                        print(f"Couldn't load {icon_path}: {str(e)}")
        
        print("Warning: No suitable icon file found")
        return False
    except Exception as e:
        print(f"Icon loading failed: {str(e)}")
        return False

if __name__ == "__main__":
    root = tk.Tk()
    load_app_icon(root)
    app = YouTubeDownloader(root)
    root.mainloop()