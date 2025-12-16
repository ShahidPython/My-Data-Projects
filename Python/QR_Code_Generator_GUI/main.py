from tkinter import *
from PIL import Image, ImageTk
import qrcode
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QR_FOLDER = os.path.join(BASE_DIR, "Qrcode")
os.makedirs(QR_FOLDER, exist_ok=True)

root = Tk()
root.title("QR Code Generator")
root.geometry("1000x500")
root.config(bg="#AE2321")
root.resizable(False, False)

# ✅ BEST SOLUTION: Set window icon using iconphoto (works on Windows, Linux, Mac)
icon_path = os.path.join(BASE_DIR, "assets", "icon.png")
try:
    icon_image = Image.open(icon_path)
    icon_photo = ImageTk.PhotoImage(icon_image)
    root.iconphoto(True, icon_photo)  # True = also apply to future toplevel windows
except Exception as e:
    print(f"Note: Could not load window icon: {e}")

# ✅ Load and resize the PNG image for display inside the window
image_path = os.path.join(BASE_DIR, "assets", "icon.png")
original_img = Image.open(image_path)
resized_img = original_img.resize((250, 250), Image.LANCZOS)
logo_image = ImageTk.PhotoImage(resized_img)

# ✅ Show image inside window
Image_view = Label(root, image=logo_image, bg="#AE2321")
Image_view.pack(padx=30, pady=30, side=RIGHT)

# QR generation function
def generate():
    name = title.get().strip()
    text = entry.get().strip()
    if name and text:
        qr = qrcode.make(text)
        save_path = os.path.join(QR_FOLDER, name + ".png")
        qr.save(save_path)

# GUI
Label(root, text="Title", fg="white", bg="#AE2321", font=15).place(x=50, y=170)
title = Entry(root, width=13, font="arial 15")
title.place(x=50, y=200)
entry = Entry(root, width=28, font="arial 15")
entry.place(x=50, y=250)
Button(root, text="Generate", width=20, height=2, bg="black", fg="white", command=generate).place(x=50, y=300)

root.mainloop()