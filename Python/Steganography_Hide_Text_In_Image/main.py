from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
from stegano import lsb
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

root = Tk()
root.title("Steganography - Hide a Secret Text in an Image")
root.geometry("700x500+250+180")
root.resizable(False, False)
root.configure(bg="#2f4155")

filename = ""
secret = None

def open_image():
    global filename
    filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select Image File",
                                          filetypes=(("PNG file", "*.png"), ("JPG file", "*.jpg"), ("All Files", "*.*")))
    if filename:
        img = Image.open(filename)
        img = ImageTk.PhotoImage(img)
        lbl.configure(image=img, width=250, height=250)
        lbl.image = img

def hide_text():
    global secret
    if filename:
        message = text1.get(1.0, END).strip()
        if message:
            try:
                secret = lsb.hide(filename, message)
                text1.delete(1.0, END)
                text1.insert(END, "Text hidden successfully! Now save the image.")
            except Exception as e:
                text1.delete(1.0, END)
                text1.insert(END, f"Error hiding text: {e}")
        else:
            text1.delete(1.0, END)
            text1.insert(END, "Please type some message to hide.")
    else:
        text1.delete(1.0, END)
        text1.insert(END, "Please open an image first.")

def show_text():
    if filename:
        try:
            hidden_msg = lsb.reveal(filename)
            text1.delete(1.0, END)
            if hidden_msg:
                text1.insert(END, hidden_msg)
            else:
                text1.insert(END, "No hidden message found in this image.")
        except Exception as e:
            text1.delete(1.0, END)
            text1.insert(END, f"Error reading message: {e}")
    else:
        text1.delete(1.0, END)
        text1.insert(END, "Please open an image first.")

def save_image():
    if secret:
        try:
            original_dir = os.path.dirname(filename)
            original_name = os.path.splitext(os.path.basename(filename))[0]
            save_path = os.path.join(original_dir, original_name + "_secret.png")

            secret.save(save_path)
            text1.delete(1.0, END)
            text1.insert(END, f"Image saved at:\n{save_path}")
        except Exception as e:
            text1.delete(1.0, END)
            text1.insert(END, f"Error saving image: {e}")
    else:
        text1.delete(1.0, END)
        text1.insert(END, "Nothing to save. Hide a message first.")

# Icon
image_icon = PhotoImage(file=os.path.join(BASE_DIR, "assets/logo.jpg"))
root.iconphoto(False, image_icon)

# Logo
logo = PhotoImage(file=os.path.join(BASE_DIR, "assets/logo.png"))
Label(root, image=logo, bg="#2f4155").place(x=10, y=0)
Label(root, text="CYBER SCIENCE", bg="#2f4155", fg="white", font="arial 25 bold").place(x=100, y=20)

# Frame 1
f = Frame(root, bg="black", width=340, height=280, relief=GROOVE)
f.place(x=10, y=80)
lbl = Label(f, bg="black")
lbl.place(x=40, y=10)

# Frame 2
frame2 = Frame(root, bd=3, width=340, height=280, bg="white", relief=GROOVE)
frame2.place(x=350, y=80)
text1 = Text(frame2, font="Robote 20", bg="white", fg="black", relief=GROOVE, wrap=WORD)
text1.place(x=0, y=0, width=320, height=290)
scrollbar1 = Scrollbar(frame2)
scrollbar1.place(x=320, y=0, height=300)
scrollbar1.configure(command=text1.yview)
text1.configure(yscrollcommand=scrollbar1.set)

# Frame 3
frame3 = Frame(root, bd=3, bg="#2f4155", width=330, height=100, relief=GROOVE)
frame3.place(x=10, y=370)
Button(frame3, text="Open Image", width=10, height=2, font="arial 14 bold", command=open_image).place(x=20, y=30)
Button(frame3, text="Save Image", width=10, height=2, font="arial 14 bold", command=save_image).place(x=180, y=30)
Label(frame3, text="Open or Save Image File", bg="#2f4155", fg="yellow").place(x=20, y=5)

# Frame 4
frame4 = Frame(root, bd=3, bg="#2f4155", width=330, height=100, relief=GROOVE)
frame4.place(x=360, y=370)
Button(frame4, text="Hide Text", width=10, height=2, font="arial 14 bold", command=hide_text).place(x=20, y=30)
Button(frame4, text="Show Text", width=10, height=2, font="arial 14 bold", command=show_text).place(x=180, y=30)
Label(frame4, text="Hide or Reveal Message", bg="#2f4155", fg="yellow").place(x=20, y=5)

root.mainloop()
