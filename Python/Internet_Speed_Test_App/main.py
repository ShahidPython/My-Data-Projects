from tkinter import *
import speedtest
import os
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

root = Tk()
root.title("Internet Speed Test")
root.geometry("360x600")
root.resizable(False, False)
root.configure(bg="#1a212d")

def Check():
    # Show testing in progress
    download.config(text="...")
    upload.config(text="...")
    ping.config(text="...")
    Download.config(text="...")
    Button.config(state=DISABLED)  # Disable button during test
    root.update()
    
    max_retries = 3
    success = False
    
    for attempt in range(max_retries):
        try:
            print(f"Speed test attempt {attempt + 1}...")
            
            # Initialize speedtest
            st = speedtest.Speedtest()
            
            # Method 1: Try getting best server directly
            print("Finding best server...")
            st.get_best_server()
            
            # Test download speed
            print("Testing download speed...")
            download_speed = st.download()
            download_mbps = round(download_speed / (1024 * 1024), 2)
            
            # Test upload speed
            print("Testing upload speed...")
            upload_speed = st.upload()
            upload_mbps = round(upload_speed / (1024 * 1024), 2)
            
            # Get ping
            ping_ms = round(st.results.ping, 2)
            
            # Update UI with results
            download.config(text=download_mbps)
            Download.config(text=download_mbps)
            upload.config(text=upload_mbps)
            ping.config(text=ping_ms)
            
            print(f"Success! Download: {download_mbps} Mbps, Upload: {upload_mbps} Mbps, Ping: {ping_ms} ms")
            success = True
            break
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            
            if attempt < max_retries - 1:
                # Wait before retry
                for i in range(3, 0, -1):
                    download.config(text=f"Retry in {i}")
                    upload.config(text="")
                    ping.config(text="")
                    Download.config(text="")
                    root.update()
                    time.sleep(1)
            else:
                # All attempts failed
                download.config(text="Error")
                upload.config(text="Error")
                ping.config(text="Error")
                Download.config(text="Error")
                print("All speed test attempts failed")
    
    # Re-enable button
    Button.config(state=NORMAL)

# Load images with error handling
try:
    # icon
    image_icon = PhotoImage(file=os.path.join(BASE_DIR, "assets", "logo.png"))
    root.iconphoto(False, image_icon)

    # images
    Top = PhotoImage(file=os.path.join(BASE_DIR, "assets", "top.png"))
    Label(root, image=Top, bg="#1a212d").pack()

    Main = PhotoImage(file=os.path.join(BASE_DIR, "assets", "main.png"))
    Label(root, image=Main, bg="#1a212d").pack(pady=(40, 0))

    button = PhotoImage(file=os.path.join(BASE_DIR, "assets", "button.png"))
    Button = Button(root, image=button, bg="#1a212d", bd=0, activebackground='#1a212d', cursor="hand2", command=Check)
    Button.pack(pady=10)

except Exception as e:
    print(f"Error loading images: {e}")
    # Create a simple text button if images fail to load
    Button = Button(root, text="START TEST", font=("arial", 16, "bold"), bg="#384056", fg="white", 
                   bd=0, activebackground='#384056', cursor="hand2", command=Check)
    Button.pack(pady=10)

# Labels
Label(root, text="PING", font="arial 10 bold", bg="#384056").place(x=50, y=0)
Label(root, text="DOWNLOAD", font="arial 10 bold", bg="#384056").place(x=140, y=0)
Label(root, text="UPLOAD", font="arial 10 bold", bg="#384056").place(x=260, y=0)

Label(root, text="MS", font="arial 7 bold", bg="#384056", fg="white").place(x=60, y=80)
Label(root, text="MBPS", font="arial 7 bold", bg="#384056", fg="white").place(x=165, y=80)
Label(root, text="MBPS", font="arial 7 bold", bg="#384056", fg="white").place(x=275, y=80)

Label(root, text="DOWNLOAD", font="arial 15 bold", bg="#384056", fg="white").place(x=140, y=280)
Label(root, text="MBPS", font="arial 15 bold", bg="#384056", fg="white").place(x=155, y=380)

# Result labels
ping = Label(root, text="00", font="arial 13 bold", bg="#384056", fg="white")
ping.place(x=70, y=60, anchor="center")

download = Label(root, text="00", font="arial 13 bold", bg="#384056", fg="white")
download.place(x=180, y=60, anchor="center")

upload = Label(root, text="00", font="arial 13 bold", bg="#384056", fg="white")
upload.place(x=290, y=60, anchor="center")

Download = Label(root, text="00", font="arial 40 bold", bg="#384056")
Download.place(x=185, y=345, anchor="center")

# Add status label
status = Label(root, text="Ready to test", font="arial 8", bg="#1a212d", fg="white")
status.place(x=180, y=580, anchor="center")

def update_status(message):
    status.config(text=message)
    root.update()

print("Internet Speed Test Application Started")
print("Make sure you have an active internet connection")
root.mainloop()