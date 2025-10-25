from tkinter import *
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

root = Tk()
root.title("BMI Calculator")
root.geometry("470x580+300+200")
root.resizable(False, False)
root.configure(bg="#f0f1f5")

def BMI():
    h = float(Height.get())
    w = float(Weight.get())

    # convert height into meter
    m = h/100
    bmi = round(float(w/m**2),1)
    label1.config(text=bmi)

    if bmi <= 18.5:
        label2.config(text="Underweight!")
        label3.config(text="You have lower weight than normal body!")
    elif bmi > 18.5 and bmi <= 25:
        label2.config(text="Normal!")
        label3.config(text="It indicates you are healthy!")
    elif bmi > 25 and bmi <= 30:
        label2.config(text="Overweight!")
        label3.config(text="It indicates that a person is\n slightly overweight!\n A doctor may advise to lose some\n weight.")
    else:
        label2.config(text="Obese!")
        label3.config(text="Health may be at risk, if they do not \n lose weight!")

# ==================== icon ====================
imag_icon = PhotoImage(file=os.path.join(BASE_DIR, "assets/icon.png"))
root.iconphoto(False, imag_icon)

# ==================== top ====================
top = PhotoImage(file=os.path.join(BASE_DIR, "assets/top.png"))
top_image = Label(root, image=top, background="#f0f1f5")
top_image.place(x=-10, y=-10)

# ==================== bottom boxes ====================
Label(root,width=72, height=18, bg="lightblue").pack(side=BOTTOM)

# two boxes
box = PhotoImage(file=os.path.join(BASE_DIR, "assets/box.png"))
Label(root, image=box).place(x=20, y=100)
Label(root, image=box).place(x=240, y=100)

# ==================== Labels for boxes ====================
Label(root, text="HEIGHT (cm)", font="arial 12 bold", bg="#fff", fg="#000").place(x=40, y=110)
Label(root, text="WEIGHT (kg)", font="arial 12 bold", bg="#fff", fg="#000").place(x=260, y=110)

# ==================== scale ====================
scale = PhotoImage(file=os.path.join(BASE_DIR, "assets/scale.png"))
Label(root, image=scale, bg="lightblue").place(x=20, y=310)

###################### Slider 1 ######################
current_value = tk.DoubleVar()

def get_current_value():
    return '{: .2f}'.format(current_value.get())

def slider_changed(event):
    Height.set(get_current_value())

    size = int(float(get_current_value()))
    img = Image.open(os.path.join(BASE_DIR, "assets/man.png"))
    resized_image = img.resize((50,10+size))
    photo2 = ImageTk.PhotoImage(resized_image)
    secondimage.config(image=photo2)
    secondimage.place(x=70, y=550-size)
    secondimage.image = photo2

# Command to change background color of scale
style = ttk.Style()
style.configure("TScale", background="white")
slider = ttk.Scale(root, from_=0, to=220, orient='horizontal',style = "TScale",
                   command=slider_changed, variable=current_value)
slider.place(x=80,y=250)

# Label for height slider
Label(root, text="Height Slider", font="arial 10 bold", bg="#f0f1f5").place(x=100, y=220)

######################################################

###################### Slider 2 ######################
current_value2 = tk.DoubleVar()

def get_current_value2():
    return '{: .2f}'.format(current_value2.get())

def slider_changed2(event):
    Weight.set(get_current_value2())

# Command to change background color of scale
style2 = ttk.Style()
style2.configure("TScale", background="white")
slider2 = ttk.Scale(root, from_=0, to=220, orient='horizontal',style = "TScale",
                   command=slider_changed2, variable=current_value2)
slider2.place(x=300,y=250)

# Label for weight slider
Label(root, text="Weight Slider", font="arial 10 bold", bg="#f0f1f5").place(x=320, y=220)

######################################################
# ==================== Entry box ====================
Height = StringVar()
Weight = StringVar()

height = Entry(root, textvariable=Height,width = 5, font="arial 50",bg = "#fff",fg = "#000",bd=0,justify=CENTER)
height.place(x=35, y=160)
Height.set(get_current_value())

weight = Entry(root, textvariable=Weight,width = 5, font="arial 50",bg = "#fff",fg = "#000",bd=0,justify=CENTER)
weight.place(x=255, y=160)
Weight.set(get_current_value2())

# ==================== man image ====================
secondimage = Label(root, bg="lightblue")
secondimage.place(x=70,y=530)

# ==================== View Report Button - Adjusted Position ====================
Button(root, text="View Report", width=15, height=2, font="arial 10 bold", 
       bg="#1f6e68", fg="white", command=BMI).place(x=300, y=400)

label1 = Label(root, font = "arial 60 bold", bg = "light blue", fg = "#3b3a3a")
label1.place(x=125,y=305)

label2 = Label(root, font = "arial 20 bold", bg = "light blue", fg = "#3b3a3a")
label2.place(x=280,y=430)

label3 = Label(root, font = "arial 10", bg = "light blue")
label3.place(x=200,y=500)

root.mainloop()