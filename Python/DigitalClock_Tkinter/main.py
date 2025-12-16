import tkinter as tk
import time
from PIL import Image, ImageTk

def create_round_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
    points = [x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius,
              x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2,
              x1, y2, x1, y2-radius, x1, y1+radius, x1, y1]
    return self.create_polygon(points, **kwargs, smooth=True)

tk.Canvas.create_round_rect = create_round_rect

def update_time():
    time_label.config(text=time.strftime("%I:%M:%S"))
    ampm_label.config(text=time.strftime("%p"))
    window.after(1000, update_time)

window = tk.Tk()
window.title("Digital Clock")
window.geometry("450x220")
window.resizable(0, 0)
window.config(bg="#001a33")

# Create canvas with shadow effect
shadow = tk.Canvas(window, bg="#001a33", highlightthickness=0, width=380, height=140)
shadow.create_round_rect(15, 15, 365, 125, radius=30, fill="#111111")
shadow.place(x=35, y=35)

main_canvas = tk.Canvas(window, bg="#001a33", highlightthickness=0, width=380, height=140)
main_canvas.create_round_rect(10, 10, 370, 130, radius=30, fill="black")
main_canvas.place(x=30, y=30)

# Time display
time_label = tk.Label(window, font=("Arial", 48), bg="black", fg="cyan")
time_label.place(in_=main_canvas, relx=0.5, rely=0.5, anchor="center", x=-30)

# AM/PM indicator
ampm_label = tk.Label(window, font=("Arial", 20), bg="black", fg="red")
ampm_label.place(in_=main_canvas, relx=0.5, rely=0.5, anchor="center", x=130, y=10)

try:
    window.iconphoto(False, ImageTk.PhotoImage(Image.open("icon.png")))
except: pass

update_time()
window.mainloop()