from responses import get_responses
import tkinter as tk
from tkinter import scrolledtext, font
from PIL import Image, ImageTk
import os
import sys
from pyfiglet import Figlet
import threading
import time
import json

# Theme colors
DARK_THEME = {
    'bg': '#121212',
    'text': '#ffffff',
    'input_bg': '#333333',
    'input_fg': '#ffffff',
    'button_bg': '#2c7be5',
    'button_fg': '#ffffff',
    'chat_bg': '#1e1e1e'
}

LIGHT_THEME = {
    'bg': '#f5f5f5',
    'text': '#000000',
    'input_bg': '#ffffff',
    'input_fg': '#000000',
    'button_bg': '#4CAF50',
    'button_fg': '#ffffff',
    'chat_bg': '#ffffff'
}

current_theme = DARK_THEME

def run_cli():
    fig = Figlet(font="slant")
    print(fig.renderText("CHATPY"))
    print("✨ Welcome to ChatPy CLI! Type 'exit' to quit.\n")
    
    # Auto-introduction
    print("\033[92mChatPy:\033[0m Hi there! I'm your intelligent assistant. How can I help you today?")
    
    while True:
        try:
            user_input = input("\033[94mYou:\033[0m ").strip()
            if not user_input:
                continue
                
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\033[91mChatPy: Goodbye! 👋 It was nice chatting with you!\033[0m")
                break
            
            response = get_responses(user_input)
            print(f"\033[92mChatPy:\033[0m {response}")
            
        except KeyboardInterrupt:
            print("\n\033[91mChatPy: Session ended! Hope to see you again!\033[0m")
            break
        except Exception as e:
            print(f"\033[91mChatPy: Error ({e}). Try again.\033[0m")

def run_gui():
    window = tk.Tk()
    window.title("ChatPy - Intelligent Assistant")
    window.geometry("700x800")
    window.configure(bg=current_theme['bg'])
    
    # Load window icon
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
        if os.path.exists(icon_path):
            img = Image.open(icon_path)
            window.iconphoto(True, ImageTk.PhotoImage(img))
    except Exception as e:
        print(f"Icon error: {e}")

    # Auto-welcome message
    def show_welcome():
        chat_window.config(state='normal')
        chat_window.insert(tk.END, "ChatPy: Hi! I'm your intelligent assistant. I can help with questions, chat, tell jokes, and more! How can I assist you today?\n", ("left", "bot"))
        chat_window.config(state='disabled')
        chat_window.see(tk.END)

    # Theme toggle
    def toggle_theme():
        global current_theme
        current_theme = LIGHT_THEME if current_theme == DARK_THEME else DARK_THEME
        apply_theme()
    
    def apply_theme():
        window.configure(bg=current_theme['bg'])
        main_frame.configure(bg=current_theme['bg'])
        chat_window.configure(
            bg=current_theme['chat_bg'],
            fg=current_theme['text']
        )
        entry.configure(
            bg=current_theme['input_bg'],
            fg=current_theme['input_fg']
        )
        send_button.configure(
            bg=current_theme['button_bg'],
            fg=current_theme['button_fg']
        )
        theme_button.configure(
            bg=current_theme['button_bg'],
            fg=current_theme['button_fg']
        )
        clear_button.configure(
            bg=current_theme['button_bg'],
            fg=current_theme['button_fg']
        )

    # Create main frame
    main_frame = tk.Frame(window, bg=current_theme['bg'])
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Chat window
    chat_window = scrolledtext.ScrolledText(
        main_frame,
        wrap=tk.WORD,
        width=60,
        height=25,
        font=("Arial", 11),
        bg=current_theme['chat_bg'],
        fg=current_theme['text'],
        padx=10,
        pady=10,
        bd=0,
        highlightthickness=0
    )
    chat_window.pack(fill=tk.BOTH, expand=True)
    chat_window.config(state='disabled')

    # Configure tags
    chat_window.tag_config("left", justify='left', lmargin1=10, lmargin2=10, rmargin=200)
    chat_window.tag_config("right", justify='right', lmargin1=200, lmargin2=200, rmargin=10)
    chat_window.tag_config("user", foreground="#2c7be5", font=("Arial", 11, "bold"))
    chat_window.tag_config("bot", foreground="#00ac69", font=("Arial", 11, "bold"))
    chat_window.tag_config("system", foreground="#888888", font=("Arial", 10, "italic"))

    # Typing indicator
    typing_label = tk.Label(
        main_frame,
        text="",
        bg=current_theme['bg'],
        fg=current_theme['text'],
        font=("Arial", 10, "italic")
    )
    typing_label.pack()

    def show_typing():
        typing_label.config(text="ChatPy is typing...")
        window.update()

    def hide_typing():
        typing_label.config(text="")
        window.update()

    def clear_chat():
        chat_window.config(state='normal')
        chat_window.delete(1.0, tk.END)
        chat_window.config(state='disabled')
        show_welcome()

    def send_message(event=None):
        user_input = entry.get().strip()
        if not user_input:
            return
            
        chat_window.config(state='normal')
        chat_window.insert(tk.END, f"You: {user_input}\n", ("right", "user"))
        chat_window.config(state='disabled')
        entry.delete(0, tk.END)
        chat_window.see(tk.END)
        
        # Process response in background
        threading.Thread(target=process_response, args=(user_input,), daemon=True).start()

    def process_response(user_input):
        show_typing()
        time.sleep(0.5)  # Simulate thinking
        response = get_responses(user_input)
        hide_typing()
        
        chat_window.config(state='normal')
        chat_window.insert(tk.END, f"ChatPy: {response}\n", ("left", "bot"))
        chat_window.config(state='disabled')
        chat_window.see(tk.END)

    # Input frame
    input_frame = tk.Frame(window, bg=current_theme['bg'])
    input_frame.pack(pady=(0, 10), padx=10, fill=tk.X)

    entry = tk.Entry(
        input_frame,
        width=50,
        font=("Arial", 11),
        bg=current_theme['input_bg'],
        fg=current_theme['input_fg'],
        relief=tk.GROOVE,
        borderwidth=2
    )
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    entry.focus()
    entry.bind("<Return>", send_message)

    # Buttons frame
    buttons_frame = tk.Frame(input_frame, bg=current_theme['bg'])
    buttons_frame.pack(side=tk.RIGHT)

    send_button = tk.Button(
        buttons_frame,
        text="Send",
        command=send_message,
        bg=current_theme['button_bg'],
        fg=current_theme['button_fg'],
        font=("Arial", 10, "bold"),
        padx=15,
        relief=tk.FLAT
    )
    send_button.pack(side=tk.LEFT, padx=(5,0))

    clear_button = tk.Button(
        buttons_frame,
        text="Clear",
        command=clear_chat,
        bg=current_theme['button_bg'],
        fg=current_theme['button_fg'],
        font=("Arial", 10),
        padx=10,
        relief=tk.FLAT
    )
    clear_button.pack(side=tk.LEFT, padx=(5,0))

    theme_button = tk.Button(
        buttons_frame,
        text="☀️" if current_theme == DARK_THEME else "🌙",
        command=toggle_theme,
        bg=current_theme['button_bg'],
        fg=current_theme['button_fg'],
        font=("Arial", 10),
        padx=5,
        relief=tk.FLAT
    )
    theme_button.pack(side=tk.LEFT, padx=(5,0))

    apply_theme()
    
    # Show welcome message after a short delay
    window.after(500, show_welcome)
    
    window.mainloop()

if __name__ == "__main__":
    print("\nChoose interface:")
    print("1. 💻 Command Line (CLI)")
    print("2. 🖥️  Graphical (GUI)")
    
    try:
        choice = input("Enter choice (1/2): ").strip()
        if choice == "1":
            run_cli()
        elif choice == "2":
            run_gui()
        else:
            print("Invalid choice. Exiting.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)