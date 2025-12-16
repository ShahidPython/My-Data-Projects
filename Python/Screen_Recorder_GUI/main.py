from tkinter import *
import pyscreenrec
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

root = Tk()
root.geometry("400x600")
root.title("Screen Recorder")
root.config(bg="#fff")
root.resizable(False, False)

def start_rec():
    file = Filename.get()
    recording_dir = os.path.join(BASE_DIR, "recordings")

    if not os.path.exists(recording_dir):
        os.makedirs(recording_dir)

    save_path = os.path.join(recording_dir, file+".mp4")
    rec.start_recording(save_path,5)

def pause_rec():
    rec.pause_recording()
def resume_rec():
    rec.resume_recording()
def stop_rec():
    rec.stop_recording()

rec = pyscreenrec.ScreenRecorder()

# icon
image = PhotoImage(file=os.path.join(BASE_DIR, "assets", "icon.png"))
root.iconphoto(False, image)

# background images
image1 = PhotoImage(file=os.path.join(BASE_DIR, "assets", "yellow.png"))
Label(root, image=image1, bg="#fff").place(x=-2, y=35)

image2 = PhotoImage(file=os.path.join(BASE_DIR, "assets", "blue.png"))
Label(root, image=image2, bg="#fff").place(x=223, y=200)

# heading
lbl = Label(root, text="Screen Recorder", bg="#fff", font="arial 15 bold")
lbl.pack(pady = 20)

image3 = PhotoImage(file=os.path.join(BASE_DIR, "assets", "recording.png"))
Label(root, image=image3, bd = 0).pack(pady=30)

Filename = StringVar()
entry = Entry(root, textvariable=Filename, width=18, font="arial 15")
entry.place(x=100,y=350)
Filename.set("Recording")

# buttons
start = Button(root, text="Start", font="arial 22", bd=0,command= start_rec)
start.place(x=140, y=250)

image4 = PhotoImage(file=os.path.join(BASE_DIR, "assets", "pause.png"))
pause = Button(root, image=image4, bd=0,bg = "#fff",command= pause_rec)
pause.place(x=50, y=450)

image5 = PhotoImage(file=os.path.join(BASE_DIR, "assets", "resume.png"))
resume = Button(root, image=image5, bd=0,bg = "#fff",command= resume_rec)
resume.place(x=150, y=450)

image6 = PhotoImage(file=os.path.join(BASE_DIR, "assets", "stop.png"))
stop = Button(root, image=image6, bd=0,bg = "#fff",command= stop_rec)
stop.place(x=250, y=450)

root.mainloop()