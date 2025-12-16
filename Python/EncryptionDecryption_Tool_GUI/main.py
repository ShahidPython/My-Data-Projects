from tkinter import *
from tkinter import messagebox
import base64

# Function to handle decryption logic
def decrypt():
    password = code.get()

    if not password:
        messagebox.showerror("decryption", "Input Password")
    elif password != "1234":
        messagebox.showerror("decryption", "Invalid Password")
    else:
        # Create a new top-level window for displaying decrypted message
        screen2 = Toplevel(screen)
        screen2.title("Decryption")
        screen2.geometry("400x200")
        screen2.configure(bg="#00bd56")

        # Retrieve the encoded message from the input Text widget
        message = text1.get(1.0, END).strip()
        decode_message = message.encode("ascii")
        base64_bytes = base64.b64decode(decode_message)
        decrypted_text = base64_bytes.decode("ascii")

        # Display the decrypted message in a new Text widget
        Label(screen2, text="DECRYPT", font="Arial 12 bold", fg="white", bg="#00bd56").place(x=10, y=0)
        text2 = Text(screen2, font="Arial 10", bg="white", relief=GROOVE, wrap=WORD, bd=0)
        text2.place(x=10, y=40, width=380, height=150)
        text2.insert(END, decrypted_text)

# Function to handle encryption logic
def encrypt():
    password = code.get()

    if not password:
        messagebox.showerror("encryption", "Input Password")
    elif password != "1234":
        messagebox.showerror("encryption", "Invalid Password")
    else:
        # Create a new top-level window for displaying encrypted message
        screen1 = Toplevel(screen)
        screen1.title("Encryption")
        screen1.geometry("400x200")
        screen1.configure(bg="#ed3833")

        # Read message from input widget and encode it with base64
        message = text1.get(1.0, END).strip()
        encode_message = message.encode("ascii")
        base64_bytes = base64.b64encode(encode_message)
        encrypted_text = base64_bytes.decode("ascii")

        # Show the encrypted text in a new Text widget
        Label(screen1, text="ENCRYPT", font="Arial 12 bold", fg="white", bg="#ed3833").place(x=10, y=0)
        text2 = Text(screen1, font="Arial 10", bg="white", relief=GROOVE, wrap=WORD, bd=0)
        text2.place(x=10, y=40, width=380, height=150)
        text2.insert(END, encrypted_text)

# Function to set up the main GUI window
def main_screen():
    global screen
    global code
    global text1

    screen = Tk()
    screen.geometry("375x398")
    screen.title("PctApp")

    # Internal reset function to clear inputs
    def reset():
        code.set("")
        text1.delete(1.0, END)

    # Text input for message to encrypt/decrypt
    Label(text="Enter text for encryption and decryption", fg="black", font=("Calibri", 13)).place(x=10, y=10)
    text1 = Text(font="Arial 20", bg="white", relief=GROOVE, wrap=WORD, bd=0)
    text1.place(x=10, y=50, width=355, height=100)

    # Input field for secret key/password
    Label(text="Enter secret key for encryption and decryption", fg="black", font=("Calibri", 13)).place(x=10, y=170)
    code = StringVar()
    Entry(textvariable=code, width=19, bd=0, font=("Arial", 25), show="*").place(x=10, y=200)

    # Control buttons for encryption, decryption, and reset
    Button(text="ENCRYPT", height=2, width=23, bg="#ed3833", fg="white", bd=0, command=encrypt).place(x=10, y=250)
    Button(text="DECRYPT", height=2, width=23, bg="#00bd56", fg="white", bd=0, command=decrypt).place(x=200, y=250)
    Button(text="RESET", height=2, width=50, bg="#1089ff", fg="white", bd=0, command=reset).place(x=10, y=300)

    # Start the GUI event loop
    screen.mainloop()

# Launch the main screen when the script runs
main_screen()
