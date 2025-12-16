from tkinter import *
from tkinter.colorchooser import askcolor
from tkinter import ttk
import tkinter as tk
from tkinter import filedialog
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

root = Tk()
root.title("Digital Whiteboard")
root.geometry("1050x570+150+50")
root.config(bg="#f2f3f5")
root.resizable(False, False)

current_x = 0
current_y = 0
color = "black"
moving_image = False
my_img = None
f_img = None

def locate_xy(work):
    global current_x, current_y, moving_image
    current_x = work.x
    current_y = work.y
    
    # Check if we clicked on the image
    if my_img and canvas.find_withtag(CURRENT):
        moving_image = True
    else:
        moving_image = False

def addline(work):
    global current_x, current_y
    if not moving_image:
        canvas.create_line((current_x, current_y, work.x, work.y), width=get_current_value(),
                         fill=color, capstyle=ROUND, smooth=TRUE)
        current_x, current_y = work.x, work.y

def show_color(new_color):
    global color
    color = new_color

def new_canvas():
    global my_img, f_img
    canvas.delete("all")
    my_img = None
    f_img = None
    display_pallete()

def inserimage():
    global filename, f_img, my_img
    filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select Image File",
                                        filetypes=(("PNG file", "*.png"), ("All Files","new.txt")))
    if filename:
        f_img = tk.PhotoImage(file=filename)
        my_img = canvas.create_image(180, 50, image=f_img, tags="movable_image")

def move_image(event):
    if my_img and moving_image:
        canvas.coords(my_img, event.x, event.y)

# icon
image_icon = PhotoImage(file=os.path.join(BASE_DIR, "assets", "logo.png"))
root.iconphoto(False, image_icon)

# sidebar
color_box = PhotoImage(file=os.path.join(BASE_DIR, "assets", "color section.png"))
Label(root, image=color_box, bg="#f2f3f5").place(x=10, y=20)

eraser = PhotoImage(file=os.path.join(BASE_DIR, "assets", "eraser.png"))
Button(root, image=eraser, bg="#f2f3f5", command=new_canvas).place(x=30, y=400)

importimage = PhotoImage(file=os.path.join(BASE_DIR, "assets", "addimage.png"))
Button(root, image=importimage, bg="white", command=inserimage).place(x=30, y=450)

######### colors
colors = Canvas(root, bg="#fff", width=37, height=300, bd=0)
colors.place(x=30, y=60)

def display_pallete():
    id = colors.create_rectangle((10,10,30,30), fill="black")
    colors.tag_bind(id, '<Button-1>', lambda x: show_color("black"))

    id = colors.create_rectangle((10,40,30,60), fill="gray")
    colors.tag_bind(id, '<Button-1>', lambda x: show_color("gray"))

    id = colors.create_rectangle((10,70,30,90), fill="brown4")
    colors.tag_bind(id, '<Button-1>', lambda x: show_color("brown4"))

    id = colors.create_rectangle((10,100,30,120), fill="red")
    colors.tag_bind(id, '<Button-1>', lambda x: show_color("red"))

    id = colors.create_rectangle((10,130,30,150), fill="orange")
    colors.tag_bind(id, '<Button-1>', lambda x: show_color("orange"))

    id = colors.create_rectangle((10,160,30,180), fill="yellow")
    colors.tag_bind(id, '<Button-1>', lambda x: show_color("yellow"))

    id = colors.create_rectangle((10,190,30,210), fill="green")
    colors.tag_bind(id, '<Button-1>', lambda x: show_color("green"))

    id = colors.create_rectangle((10,220,30,240), fill="blue")
    colors.tag_bind(id, '<Button-1>', lambda x: show_color("blue"))

    id = colors.create_rectangle((10,250,30,270), fill="purple")
    colors.tag_bind(id, '<Button-1>', lambda x: show_color("purple"))

display_pallete()

# main screen
canvas = Canvas(root, width=930, height=500, background="white", cursor="hand2")
canvas.place(x=100, y=10)

canvas.bind('<Button-1>', locate_xy)
canvas.bind('<B1-Motion>', addline)
canvas.bind('<B1-Motion>', move_image, add='+')

################################## slider ###################################
current_value = tk.DoubleVar()

def get_current_value():
    return '{: .2f}'.format(current_value.get())

def slider_changed(event):
    value_label.configure(text=get_current_value())

slider = ttk.Scale(root, from_=0, to=100, orient="horizontal", command=slider_changed, variable=current_value)
slider.place(x=30, y=530)

value_label = ttk.Label(root, text=get_current_value())
value_label.place(x=27, y=550)

root.mainloop()