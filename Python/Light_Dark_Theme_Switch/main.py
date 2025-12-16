from tkinter import *
import os

class ThemeToggleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Toggle Switch")
        self.root.geometry("400x600")
        self.root.resizable(False, False)

        # Light and Dark background colors
        self.light_bg = "white"
        self.dark_bg = "#26242f"

        # Set default mode
        self.button_mode = True  # True = Light, False = Dark
        self.root.config(bg=self.light_bg)

        # Base directory
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.assets_path = os.path.join(self.BASE_DIR, "assets")

        # Load images
        self.on_image = self.load_image("light.png")
        self.off_image = self.load_image("dark.png")

        # Label for theme status
        self.label = Label(self.root, text="Light Mode", font=("Arial", 16), bg=self.light_bg, fg="black")
        self.label.pack(pady=(100, 20))

        # Toggle Button
        self.button = Button(self.root, image=self.on_image, bd=0,
                             bg=self.light_bg, activebackground=self.light_bg,
                             command=self.toggle_theme)
        self.button.pack(pady=10)

    def load_image(self, filename):
        path = os.path.join(self.assets_path, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Image not found: {path}")
        return PhotoImage(file=path)

    def toggle_theme(self):
        if self.button_mode:
            # Switch to Dark Mode
            self.button.config(image=self.off_image, bg=self.dark_bg, activebackground=self.dark_bg)
            self.root.config(bg=self.dark_bg)
            self.label.config(text="Dark Mode", bg=self.dark_bg, fg="white")
        else:
            # Switch to Light Mode
            self.button.config(image=self.on_image, bg=self.light_bg, activebackground=self.light_bg)
            self.root.config(bg=self.light_bg)
            self.label.config(text="Light Mode", bg=self.light_bg, fg="black")
        self.button_mode = not self.button_mode


if __name__ == "__main__":
    root = Tk()
    app = ThemeToggleApp(root)
    root.mainloop()
