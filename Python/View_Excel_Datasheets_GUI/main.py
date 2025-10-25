from tkinter import *
from tkinter import messagebox
from tkinter import ttk, filedialog
import numpy
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

root = Tk()
root.title("Excel Datasheet Viewer")
root.geometry("1100x400+200+200")

def Open():
    filename = filedialog.askopenfilename(title="Open a File",filetypes=(("Excel files", "*.xlsx"),("All files", "*.*")))
    if filename:
        try:
            filename = r"{}".format(filename)
            df = pd.read_excel(filename)
        except:
            messagebox.showerror("Error", "File could not be opened.")

    # now we have to clear previous data to enter new data
    tree.delete(*tree.get_children())

    # datasheet heading
    tree["column"] = list(df.columns)
    tree["show"] = "headings"

    # heading title
    for col in tree["column"]:
        tree.heading(col, text=col)
    # enter data
    df_rows = df.to_numpy().tolist()
    for row in df_rows:
        tree.insert("", "end", values=row)

# icon image
image_icon = PhotoImage(file=os.path.join(BASE_DIR, "assets/logo.png"))
root.iconphoto(False, image_icon)

# frame
frame = Frame(root)
frame.pack(pady=25)

# TreeView
tree = ttk.Treeview(frame)
tree.pack()

# button
button = Button(root, text="Open",width= 60,height=2,font=30,fg = "white",bg = "#0078d7", command=Open)
button.pack(padx=10,pady=20)

root.mainloop()