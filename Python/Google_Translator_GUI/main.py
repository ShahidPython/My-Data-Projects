import os
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from deep_translator import GoogleTranslator

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

root = Tk()
root.title("Google Translator")
root.geometry("1080x400")
root.configure(bg="white")

# language list
languageV = list(GoogleTranslator().get_supported_languages(as_dict=False))
languageV.insert(0, "auto")  # auto detect option

def label_change():
    c = combo1.get()
    c1 = combo2.get()
    label1.configure(text=c.upper())
    label2.configure(text=c1.upper())
    root.after(1000, label_change)

def translate_now():
    try:
        text = text1.get(1.0, END).strip()
        c1 = combo1.get().lower()
        c2 = combo2.get().lower()

        if not text:
            messagebox.showwarning("Warning", "Please enter some text.")
            return

        translated = GoogleTranslator(source=c1, target=c2).translate(text)
        text2.delete(1.0, END)
        text2.insert(END, translated)

    except Exception as e:
        messagebox.showerror("Translation Error", str(e))

# icon
try:
    logo_image = Image.open(os.path.join(BASE_DIR, "assets", "google.png"))
    resized_logo = logo_image.resize((64, 64))
    image_icon = ImageTk.PhotoImage(resized_logo)
    root.iconphoto(False, image_icon)
except:
    pass

# arrow
try:
    arrow = Image.open(os.path.join(BASE_DIR, "assets", "arrows.png"))
    resized_arrow = arrow.resize((90, 90))
    arrow_image = ImageTk.PhotoImage(resized_arrow)
    arrow_label = Label(root, image=arrow_image, bg="white")
    arrow_label.place(x=490, y=60)
except:
    pass

# language combobox - from
combo1 = ttk.Combobox(root, values=languageV, font="Roboto 14", state="readonly")
combo1.place(x=110, y=20)
combo1.set("english")

label1 = Label(root, text="ENGLISH", font="segoe 30 bold", bg="white", width=18, bd=5, relief=GROOVE)
label1.place(x=10, y=50)

f = Frame(root, bg="black", bd=5)
f.place(x=10, y=118, width=440, height=210)

text1 = Text(f, font="Roboto 20", bg="white", relief=GROOVE, wrap=WORD)
text1.place(x=0, y=0, width=430, height=200)

scrollbar1 = Scrollbar(f)
scrollbar1.pack(side="right", fill="y")
scrollbar1.configure(command=text1.yview)
text1.configure(yscrollcommand=scrollbar1.set)

# language combobox - to
combo2 = ttk.Combobox(root, values=languageV, font="Roboto 14", state="readonly")
combo2.place(x=730, y=20)
combo2.set("urdu")

label2 = Label(root, text="URDU", font="segoe 30 bold", bg="white", width=18, bd=5, relief=GROOVE)
label2.place(x=620, y=50)

f1 = Frame(root, bg="black", bd=5)
f1.place(x=620, y=118, width=440, height=210)

text2 = Text(f1, font="Roboto 20", bg="white", relief=GROOVE, wrap=WORD)
text2.place(x=0, y=0, width=430, height=200)

scrollbar2 = Scrollbar(f1)
scrollbar2.pack(side="right", fill="y")
scrollbar2.configure(command=text2.yview)
text2.configure(yscrollcommand=scrollbar2.set)

# translate button
translate = Button(root,text="Translate",font="Roboto 15 bold italic",activebackground="purple",cursor="hand2",bd=5,bg="red",fg="white",command=translate_now)
translate.place(x=480, y=250)

label_change()
root.mainloop()
