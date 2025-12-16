from tkinter import *
from tkinter import messagebox
from playsound import playsound
import time
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

root = Tk()
root.title("Countdown Timer")
root.geometry("400x600")
root.config(bg="#000")
root.resizable(False, False)

# Header
heading = Label(root, text="Countdown Timer", font="Arial 30 bold", bg="#000", fg="#ea3548")
heading.pack(pady=10)

# Clock Label
Label(root, font=("arial", 15, "bold"), text="current time:", bg="papaya whip").place(x=65, y=70)

def update_clock():
    clock_time = time.strftime("%H:%M:%S %p")
    current_time.config(text=clock_time)
    root.after(1000, update_clock)

current_time = Label(root, font=("arial", 15, "bold"), text="", fg="#000", bg="#fff")
current_time.place(x=190, y=70)
update_clock()

# Time input
hrs = StringVar(value="00")
mins = StringVar(value="00")
sec = StringVar(value="00")

Entry(root, textvariable=hrs, width=2, font="arial 50", bg="#000", fg="#fff", bd=0).place(x=30, y=155)
Entry(root, textvariable=mins, width=2, font="arial 50", bg="#000", fg="#fff", bd=0).place(x=150, y=155)
Entry(root, textvariable=sec, width=2, font="arial 50", bg="#000", fg="#fff", bd=0).place(x=270, y=155)

Label(root, text="hours", font="arial 12", bg="#000", fg="#fff").place(x=105, y=200)
Label(root, text="mins", font="arial 12", bg="#000", fg="#fff").place(x=225, y=200)
Label(root, text="secs", font="arial 12", bg="#000", fg="#fff").place(x=345, y=200)

# Timer function
timer_running = False

def start_timer():
    global timer_running
    if timer_running:
        return

    try:
        total_seconds = int(hrs.get()) * 3600 + int(mins.get()) * 60 + int(sec.get())
        if total_seconds <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid time values.")
        return

    timer_running = True
    start_button.config(state=DISABLED)
    count_down(total_seconds)

def count_down(t):
    global timer_running
    if t < 0:
        timer_running = False
        start_button.config(state=NORMAL)
        try:
            sound_path = os.path.join(BASE_DIR, "alarm.mp3")
            if os.path.exists(sound_path):
                playsound(sound_path)
            else:
                messagebox.showinfo("Time's Up", "Timer completed!")
        except:
            messagebox.showwarning("Sound Error", "Failed to play sound.")
        return

    mins_set, secs_set = divmod(t, 60)
    hrs_set, mins_set = divmod(mins_set, 60)

    hrs.set(f"{hrs_set:02}")
    mins.set(f"{mins_set:02}")
    sec.set(f"{secs_set:02}")

    root.after(1000, count_down, t - 1)

def reset_timer():
    global timer_running
    timer_running = False
    hrs.set("00")
    mins.set("00")
    sec.set("00")
    start_button.config(state=NORMAL)

# Pre-set Buttons
def brush(): hrs.set("00"); mins.set("02"); sec.set("00")
def face(): hrs.set("00"); mins.set("15"); sec.set("00")
def eggs(): hrs.set("00"); mins.set("10"); sec.set("00")

# Start and Reset Buttons
start_button = Button(root, text="START", bg="#ea3548", bd=0, fg="#fff", width=20, height=2,font="arial 10 bold", command=start_timer)
start_button.pack(padx=5, pady=10, side=BOTTOM)

reset_button = Button(root, text="RESET", bg="#555", bd=0, fg="#fff", width=20, height=2,font="arial 10 bold", command=reset_timer)
reset_button.pack(padx=5, pady=5, side=BOTTOM)

# Image Buttons
Image1 = PhotoImage(file=os.path.join(BASE_DIR, "assets", "brush.png"))
Image2 = PhotoImage(file=os.path.join(BASE_DIR, "assets", "face.png"))
Image3 = PhotoImage(file=os.path.join(BASE_DIR, "assets", "eggs.png"))

Button(root, image=Image1, bg="#000", bd=0, command=brush).place(x=7, y=300)
Button(root, image=Image2, bg="#000", bd=0, command=face).place(x=137, y=300)
Button(root, image=Image3, bg="#000", bd=0, command=eggs).place(x=267, y=300)

root.mainloop()
