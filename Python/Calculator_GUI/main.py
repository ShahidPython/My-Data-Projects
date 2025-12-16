from tkinter import *
from PIL import Image, ImageDraw, ImageTk
from simpleeval import simple_eval

class CircularImageButtonCalculator:
    def __init__(self, root):

        self.root = root
        self.root.title("Calculator App")
        self.root.geometry("370x540")
        self.root.resizable(False, False)

        self.light_mode = False
        self.bg_dark = "#222222"
        self.bg_light = "#f0f0f0"
        self.fg_dark = "#ffffff"
        self.fg_light = "#000000"

        self.expression = ""
        self.result_var = StringVar()
        self.history = []

        self.images = {}
        self.button_refs = {}

        # Build the UI
        self._build_ui()

    def _build_ui(self):
        # Initial background setup
        self.root.configure(bg=self.bg_dark)

        # Display calculation history (top)
        self.history_label = Label(
            self.root, text="", anchor="e", justify="right",
            bg=self.bg_dark, fg="#bbbbbb", font=("Arial", 10)
        )
        self.history_label.pack(fill="x", padx=10)

        # Entry field for current expression/result
        entry = Entry(
            self.root, textvariable=self.result_var,
            font=("Arial", 22), bd=10, relief="sunken",
            justify="right", bg="#116f7b", fg="#ffffff"
        )
        entry.pack(fill="both", padx=10, pady=5, ipady=10)

        # Light/Dark Mode Toggle Button
        Button(
            self.root, text="🌓 Toggle Theme",
            command=self._toggle_theme,
            cursor="hand2"
        ).pack(pady=(0, 5))

        # Canvas area for calculator buttons
        self.canvas = Canvas(
            self.root, width=370, height=400,
            bg=self.bg_dark, highlightthickness=0
        )
        self.canvas.pack()

        # Place all buttons
        self._place_buttons()

    def _create_button_image(self, radius, color, shadow=True):
        upscale = 6
        size = (radius * 2 * upscale, radius * 2 * upscale)
        image = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Optional drop shadow
        if shadow:
            draw.ellipse((4, 4, size[0]-4, size[1]-4), fill=(0, 0, 0, 90))

        margin = 10
        draw.ellipse((margin, margin, size[0]-margin, size[1]-margin), fill=color)

        # Resize to actual button size
        return ImageTk.PhotoImage(image.resize((radius * 2, radius * 2), Image.LANCZOS))

    def _brighten_color(self, hex_color, factor):
        hex_color = hex_color.lstrip('#')
        r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
        bright = lambda c: min(int(c + (255 - c) * factor), 255)
        return f'#{bright(r):02x}{bright(g):02x}{bright(b):02x}'

    def _darken_color(self, hex_color, factor):
        hex_color = hex_color.lstrip('#')
        r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
        dark = lambda c: max(int(c * (1 - factor)), 0)
        return f'#{dark(r):02x}{dark(g):02x}{dark(b):02x}'

    def _place_buttons(self):
        layout = [
            ('(', 50, 40), (')', 130, 40), ('%', 210, 40), ('C', 290, 40),
            ('7', 50, 110), ('8', 130, 110), ('9', 210, 110), ('/', 290, 110),
            ('4', 50, 180), ('5', 130, 180), ('6', 210, 180), ('*', 290, 180),
            ('1', 50, 250), ('2', 130, 250), ('3', 210, 250), ('-', 290, 250),
            ('0', 50, 320), ('.', 130, 320), ('=', 210, 320), ('+', 290, 320),
        ]
        for text, x, y in layout:
            self._draw_button(text, x, y)

    def _draw_button(self, label, x, y):
        radius = 32

        # Assign base and text colors
        if label == "=":
            base_color = "#ff6600"
            text_color = "#ffffff"
        elif label in ['*', '(', ')', '-', '+', 'C', '/', '%']:
            base_color = "#ffffff"
            text_color = "#000000"
        else:
            base_color = "#1b8e95"
            text_color = "#ffffff"

        img = self._create_button_image(radius, base_color, shadow=True)
        self.images[label] = img

        img_id = self.canvas.create_image(x, y, image=img)
        label_id = self.canvas.create_text(x, y, text=label, font=('Arial', 16, 'bold'), fill=text_color)
        self.button_refs[label] = (img_id, label_id, base_color, text_color)

        # Bind mouse events
        def handle_click(event, key=label):
            if key == "=":
                try:
                    result = simple_eval(self.expression)
                    self.history.append(self.expression)
                    self.result_var.set(result)
                    self.expression = str(result)
                    self._update_history()
                except Exception:
                    self.result_var.set("Error")
                    self.expression = ""
            elif key == "C":
                self.expression = ""
                self.result_var.set("")
            else:
                if len(self.expression) < 30:
                    self.expression += "/100" if key == "%" else str(key)
                    self.result_var.set(self.expression)
            self._flash_button(label)

        def on_hover(event, key=label):
            bright_color = self._brighten_color(base_color, 0.3)
            bright_img = self._create_button_image(radius, bright_color, shadow=True)
            self.canvas.itemconfig(self.button_refs[key][0], image=bright_img)
            self.images[f"{key}_hover"] = bright_img

        def on_leave(event, key=label):
            self.canvas.itemconfig(self.button_refs[key][0], image=self.images[key])

        # Attach events
        self.canvas.tag_bind(img_id, "<Button-1>", handle_click)
        self.canvas.tag_bind(label_id, "<Button-1>", handle_click)
        self.canvas.tag_bind(img_id, "<Enter>", on_hover)
        self.canvas.tag_bind(label_id, "<Enter>", on_hover)
        self.canvas.tag_bind(img_id, "<Leave>", on_leave)
        self.canvas.tag_bind(label_id, "<Leave>", on_leave)

    def _flash_button(self, label):
        img_id, _, color, _ = self.button_refs[label]
        dark_img = self._create_button_image(32, self._darken_color(color, 0.3), shadow=True)
        self.canvas.itemconfig(img_id, image=dark_img)
        self.images[f"{label}_click"] = dark_img
        self.root.after(100, lambda: self.canvas.itemconfig(img_id, image=self.images[label]))

    def _toggle_theme(self):
        self.light_mode = not self.light_mode
        bg = self.bg_light if self.light_mode else self.bg_dark
        fg = self.fg_light if self.light_mode else self.fg_dark
        self.root.configure(bg=bg)
        self.canvas.configure(bg=bg)
        self.history_label.configure(bg=bg, fg=fg)

    def _update_history(self):
        if len(self.history) > 5:
            self.history = self.history[-5:]
        self.history_label.config(text="\n".join(self.history[::-1]))


# --- App Launch ---
if __name__ == "__main__":
    root = Tk()
    app = CircularImageButtonCalculator(root)
    root.mainloop()