from tkinter import *
import socket
from tkinter import filedialog
from tkinter import messagebox
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

root = Tk()
root.title("File Transfer App")
root.geometry("450x560+500+200")
root.configure(bg="#f4fdfe")
root.resizable(False, False)

def Send():
    window = Toplevel(root)
    window.title("Send")
    window.geometry("450x560+500+200")
    window.configure(bg="#f4fdfe")
    window.resizable(False, False)

    filename = "" 

    def select_file():
        nonlocal filename
        filename = filedialog.askopenfilename(
            initialdir=os.getcwd(), 
            title="Select File", 
            filetype=(('All files', '*.*'), ('Text files', '*.txt'))
        )
        if filename:
            messagebox.showinfo("Success", f"Selected: {os.path.basename(filename)}")

    def sender():
        nonlocal filename
        if not filename:
            messagebox.showerror("Error", "Please select a file first")
            return
            
        try:
            s = socket.socket()
            host = socket.gethostname()
            port = 8080
            s.bind((host, port))
            s.listen(1)
            print("Waiting for any incoming connections...")
            conn, addr = s.accept()
            
            # Send filename first
            conn.send(os.path.basename(filename).encode())
            
            # Send file data
            with open(filename, 'rb') as file:
                while True:
                    file_data = file.read(1024)
                    if not file_data:
                        break
                    conn.send(file_data)
            
            messagebox.showinfo("Success", "File sent successfully!")
            print("File has been sent successfully...")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send file: {e}")
        finally:
            if 'conn' in locals(): conn.close()
            if 's' in locals(): s.close()

    # icon
    image_icon1 = PhotoImage(file=os.path.join(BASE_DIR, "assets/send.png"))
    window.iconphoto(False, image_icon1)

    Sbackground = PhotoImage(file=os.path.join(BASE_DIR, "assets/sender.png"))
    Label(window, image=Sbackground).place(x=-2, y=0)

    Mbackground = PhotoImage(file=os.path.join(BASE_DIR, "assets/id.png"))
    Label(window, image=Mbackground).place(x=100, y=260)

    host = socket.gethostname()
    Label(window, text=f'ID: {host}', bg='white', fg='black').place(x=140, y=290)

    Button(window, text=" + select file", width=10, height=1, font="arial 14 bold", fg="#fff", bg="#000", command=select_file).place(x=160, y=150)
    Button(window, text="SEND", width=8, height=1, font='arial 14 bold', bg='#000', fg='#fff', command=sender).place(x=300, y=150)

    window.mainloop()

def Receive():
    main = Toplevel(root)
    main.title("Receive")
    main.geometry("450x560+500+200")
    main.configure(bg="#f4fdfe")
    main.resizable(False, False)

    save_path = os.getcwd()  # Default save location

    def select_save_location():
        nonlocal save_path
        save_path = filedialog.askdirectory(
            initialdir=os.getcwd(),
            title="Select folder to save received files"
        )
        if save_path:
            messagebox.showinfo("Info", f"Files will be saved to: {save_path}")

    def receiver():
        nonlocal save_path
        ID = SenderID.get()
        
        if not ID:
            messagebox.showerror("Error", "Please enter sender ID")
            return

        try:
            s = socket.socket()
            port = 8080
            s.connect((ID, port))
            
            # Receive filename first
            filename = s.recv(1024).decode()
            if not filename:
                messagebox.showerror("Error", "No filename received")
                return
            
            # Ask user to confirm save location
            save_file_path = os.path.join(save_path, filename)
            
            # Check if file exists
            if os.path.exists(save_file_path):
                if not messagebox.askyesno("Confirm", f"{filename} already exists. Overwrite?"):
                    return
            
            # Receive file data
            with open(save_file_path, "wb") as file:
                while True:
                    file_data = s.recv(1024)
                    if not file_data:
                        break
                    file.write(file_data)
            
            messagebox.showinfo("Success", f"File saved to:\n{save_file_path}")
            print("File has been received successfully...")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to receive file: {e}")
        finally:
            s.close()

    # icon
    image_icon1 = PhotoImage(file=os.path.join(BASE_DIR, "assets/receive.png"))
    main.iconphoto(False, image_icon1)

    Hbackground = PhotoImage(file=os.path.join(BASE_DIR, "assets/receiver.png"))
    Label(main, image=Hbackground).place(x=-2, y=0)

    logo = PhotoImage(file=os.path.join(BASE_DIR, "assets/profile.png"))
    Label(main, image=logo, bg="#f4fdfe").place(x=10, y=250)

    Label(main, text="Receive", font=("arial", 20), bg="#f4fdfe").place(x=100, y=280)

    Button(main, text="Save Location", width=12, height=1, font="arial 10 bold", 
          fg="#fff", bg="#4a7a8c", command=select_save_location).place(x=300, y=340)

    Label(main, text="Input sender id", font=('arial', 10, 'bold'), bg="#f4fdfe").place(x=20, y=340)
    SenderID = Entry(main, width=25, fg='black', border=2, bg='white', font=('arial', 15))
    SenderID.place(x=20, y=370)
    SenderID.focus()

    Label(main, text="File will be saved to:", font=('arial', 10, 'bold'), bg="#f4fdfe").place(x=20, y=420)
    save_location_label = Label(main, text=save_path, font=('arial', 8), bg="white", width=40, anchor='w')
    save_location_label.place(x=20, y=450)

    def update_save_location_label():
        save_location_label.config(text=save_path)

    imageicon = PhotoImage(file=os.path.join(BASE_DIR, "assets/arrow.png"))
    rr = Button(main, text="Receive", compound=LEFT, image=imageicon, width=130, bg="#39c790", font="arial 14 bold", command=receiver)
    rr.place(x=20, y=500)

    main.mainloop()

# icon
image_icon = PhotoImage(file=os.path.join(BASE_DIR, "assets/icon.png"))
root.iconphoto(False, image_icon)

Label(root, text="File Transfer", font=("Acumin Variable Concept", 20, "bold"), bg="#f4fdfe").place(x=20, y=30)

Frame(root, width=400, height=2, bg="#f3f5f6").place(x=25, y=80)

send_image = PhotoImage(file=os.path.join(BASE_DIR, "assets/send.png"))
send = Button(root, image=send_image, bg="#f4fdfe", bd=0, command=Send)
send.place(x=50, y=100)

receive_image = PhotoImage(file=os.path.join(BASE_DIR, "assets/receive.png"))
receive = Button(root, image=receive_image, bg="#f4fdfe", bd=0, command=Receive)
receive.place(x=300, y=100)

# label
Label(root, text="Send", font=("Acumin Variable Concept", 17, "bold"), bg="#f4fdfe").place(x=65, y=200)
Label(root, text="Receive", font=("Acumin Variable Concept", 17, "bold"), bg="#f4fdfe").place(x=300, y=200)

background = PhotoImage(file=os.path.join(BASE_DIR, "assets/background.png"))
Label(root, image=background).place(x=-2, y=323)
root.mainloop()