import os
from tkinter import *
from tkinter import messagebox
import sounddevice as sound            # pip install sounddevice
from scipy.io.wavfile import write     # pip install scipy
import time

base_dir = os.path.dirname(os.path.abspath(__file__))

root = Tk()
root.geometry("600x700+400+80")
root.title("Voice Recorder")
root.config(bg="#4a4a4a")
root.resizable(False, False)

def Record():
    freq = 44100
    dur = int(duration.get())
    recording = sound.rec(int(dur * freq), samplerate=freq, channels=2)
    
# timer
    try:
        temp = int(duration.get())
    except:
        print("Please enter the right value")

    while temp>=0:
        root.update()
        time.sleep(1)
        temp -= 1

        if (temp==0):
            messagebox.showinfo("Time Countdown", "Time's Up")
        Label(text = f"{str(temp)}", font="arial 40", width = 4, bg="#4a4a4a").place(x=240, y=590)

    save_path = os.path.join(base_dir, "recording.wav")
    write(save_path, freq, recording)
    messagebox.showinfo("Recording Saved", f"Saved to:\n{save_path}")

# icon
image_icon = PhotoImage(file=os.path.join(base_dir, "assets", "Record.png"))
root.iconphoto(False, image_icon)

# logo
photo = PhotoImage(file=os.path.join(base_dir, "assets", "Record.png"))
myimage = Label(root, image=photo, bg="#4a4a4a")
myimage.pack(padx=5,pady=5)

# name
Label(text="Voice Recorder", font="arial 30 bold", bg="#4a4a4a", fg="white").pack()

# entry box
duration = StringVar()
entry = Entry(root, textvariable=duration, font="arial 30", width=15).pack(pady=10)
Label(text="Enter time in seconds", font="arial 15", bg="#4a4a4a", fg="white").pack()

# button
record = Button(root, font = "arial 20", text="Record", bg="#111111", fg="white",border = 0,command = Record ).pack(pady=30)

root.mainloop()