from tkinter import *
from tkinter import filedialog
from pdf2image import convert_from_path
from PIL import Image, ImageTk
import os
import sys

# === Setup correct base directory for .ico and other resources === #
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS  # When bundled with PyInstaller
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# === Initialize main window === #
root = Tk()
root.geometry("800x600")
root.title("PDF Viewer")
root.iconbitmap(os.path.join(BASE_DIR, "pdfviewer.ico"))
root.configure(bg="white")

# === Frame + Canvas + Scrollbar Setup === #
main_frame = Frame(root, bg="white")
main_frame.pack(fill=BOTH, expand=1)

canvas = Canvas(main_frame, bg="white")
canvas.pack(side=LEFT, fill=BOTH, expand=1)

v_scrollbar = Scrollbar(main_frame, orient=VERTICAL, command=canvas.yview)
v_scrollbar.pack(side=RIGHT, fill=Y)

canvas.configure(yscrollcommand=v_scrollbar.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

content_frame = Frame(canvas, bg="white")
canvas.create_window((0, 0), window=content_frame, anchor="nw")

# === PDF Open & Render === #
def open_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        # Clear previous content
        for widget in content_frame.winfo_children():
            widget.destroy()

        # Convert PDF to image
        images = convert_from_path(file_path, dpi=100)

        for i, image in enumerate(images):
            max_width = 700
            w_percent = (max_width / float(image.width))
            h_size = int((float(image.height) * float(w_percent)))
            img = image.resize((max_width, h_size), Image.Resampling.LANCZOS)

            photo = ImageTk.PhotoImage(img)
            label = Label(content_frame, image=photo, bg="white")
            label.image = photo  # prevent garbage collection
            label.pack(pady=10)

        canvas.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

# === Button to Load PDF === #
Button(root, text="Open PDF", command=open_pdf, font=("Arial", 16),
       bg="skyblue", fg="black").pack(pady=10)

root.mainloop()
