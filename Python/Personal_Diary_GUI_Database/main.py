import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

# ---------------------------- DATABASE SETUP ---------------------------- #
def setup_db():
    conn = sqlite3.connect("diary.db")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_text TEXT NOT NULL,
        entry_date TEXT NOT NULL
    )
    """)
    conn.close()

setup_db()

# ---------------------------- STYLING CONSTANTS ---------------------------- #
BG_COLOR = "#2d3436"  # Dark background
TEXT_BG = "#dfe6e9"  # Light text area
BUTTON_COLOR = "#0984e3"  # Blue buttons
ACCENT_COLOR = "#00cec9"  # Teal accent
FONT = ("Segoe UI", 12)  # Modern font
TITLE_FONT = ("Segoe UI", 24, "bold")  # Title font
BUTTON_FONT = ("Segoe UI", 12, "bold")  # Button font

# ---------------------------- MAIN APPLICATION ---------------------------- #
class DiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("✨ My Secret Diary")
        self.root.geometry("800x700")
        self.root.configure(bg=BG_COLOR)
        
        # Make the window resizable
        self.root.minsize(700, 600)
        
        # Custom title
        title_frame = tk.Frame(root, bg=BG_COLOR)
        title_frame.pack(pady=(20, 10))
        
        self.title_label = tk.Label(
            title_frame, 
            text="My Secret Diary ✍️", 
            font=TITLE_FONT, 
            bg=BG_COLOR, 
            fg="white"
        )
        self.title_label.pack()
        
        # Date display
        self.date_label = tk.Label(
            title_frame,
            text=datetime.now().strftime("%A, %B %d, %Y"),
            font=("Segoe UI", 12),
            bg=BG_COLOR,
            fg=ACCENT_COLOR
        )
        self.date_label.pack(pady=(5, 0))
        
        # Text Area with Scrollbar
        text_frame = tk.Frame(root, bg=BG_COLOR)
        text_frame.pack(padx=30, pady=(10, 20), fill="both", expand=True)
        
        # Add border to text area
        text_border = tk.Frame(text_frame, bg=ACCENT_COLOR)
        text_border.pack(fill="both", expand=True, padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(text_border)
        scrollbar.pack(side="right", fill="y")
        
        self.text_area = tk.Text(
            text_border, 
            wrap="word", 
            height=15, 
            font=FONT, 
            bg=TEXT_BG, 
            fg="black",
            insertbackground="black",
            selectbackground=ACCENT_COLOR,
            yscrollcommand=scrollbar.set,
            padx=10,
            pady=10,
            relief="flat"
        )
        self.text_area.pack(fill="both", expand=True)
        scrollbar.config(command=self.text_area.yview)
        
        # Buttons Frame (Styled with custom buttons)
        btn_frame = tk.Frame(root, bg=BG_COLOR)
        btn_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        # Save Button
        self.save_btn = tk.Button(
            btn_frame, 
            text="💾 Save Entry", 
            command=self.save_entry, 
            bg=BUTTON_COLOR, 
            fg="white",
            font=BUTTON_FONT,
            borderwidth=0,
            padx=20,
            pady=8,
            activebackground="#74b9ff",
            relief="raised",
            cursor="hand2"
        )
        self.save_btn.pack(side="left", padx=5, expand=True, fill="x")
        
        # View Button
        self.view_btn = tk.Button(
            btn_frame, 
            text="📖 View Entries", 
            command=self.view_entries, 
            bg="#00b894", 
            fg="white",
            font=BUTTON_FONT,
            borderwidth=0,
            padx=20,
            pady=8,
            activebackground="#55efc4",
            relief="raised",
            cursor="hand2"
        )
        self.view_btn.pack(side="left", padx=5, expand=True, fill="x")
        
        # Search Button
        self.search_btn = tk.Button(
            btn_frame, 
            text="🔍 Search", 
            command=self.open_search_window, 
            bg="#6c5ce7", 
            fg="white",
            font=BUTTON_FONT,
            borderwidth=0,
            padx=20,
            pady=8,
            activebackground="#a29bfe",
            relief="raised",
            cursor="hand2"
        )
        self.search_btn.pack(side="left", padx=5, expand=True, fill="x")
        
        # Export Button
        self.export_btn = tk.Button(
            btn_frame, 
            text="📤 Export", 
            command=self.export_entries, 
            bg="#e84393", 
            fg="white",
            font=BUTTON_FONT,
            borderwidth=0,
            padx=20,
            pady=8,
            activebackground="#fd79a8",
            relief="raised",
            cursor="hand2"
        )
        self.export_btn.pack(side="left", padx=5, expand=True, fill="x")
        
        # Add hover effects
        self.setup_hover_effects()
    
    def setup_hover_effects(self):
        # Save button hover effect
        self.save_btn.bind("<Enter>", lambda e: self.save_btn.config(bg="#74b9ff"))
        self.save_btn.bind("<Leave>", lambda e: self.save_btn.config(bg=BUTTON_COLOR))
        
        # View button hover effect
        self.view_btn.bind("<Enter>", lambda e: self.view_btn.config(bg="#55efc4"))
        self.view_btn.bind("<Leave>", lambda e: self.view_btn.config(bg="#00b894"))
        
        # Search button hover effect
        self.search_btn.bind("<Enter>", lambda e: self.search_btn.config(bg="#a29bfe"))
        self.search_btn.bind("<Leave>", lambda e: self.search_btn.config(bg="#6c5ce7"))
        
        # Export button hover effect
        self.export_btn.bind("<Enter>", lambda e: self.export_btn.config(bg="#fd79a8"))
        self.export_btn.bind("<Leave>", lambda e: self.export_btn.config(bg="#e84393"))
    
    # ---------------------------- CORE FUNCTIONS ---------------------------- #
    def save_entry(self):
        text = self.text_area.get("1.0", tk.END).strip()
        if text:
            conn = sqlite3.connect("diary.db")
            conn.execute("INSERT INTO entries (entry_text, entry_date) VALUES (?, ?)", 
                         (text, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Entry saved securely! 🔒")
            self.text_area.delete("1.0", tk.END)
        else:
            messagebox.showwarning("Oops!", "Write something before saving! ✏️")
    
    def view_entries(self):
        conn = sqlite3.connect("diary.db")
        cursor = conn.execute("SELECT id, entry_date, entry_text FROM entries ORDER BY id DESC")
        entries = cursor.fetchall()
        conn.close()
        
        view_win = tk.Toplevel(self.root)
        view_win.title("📚 Your Diary Entries")
        view_win.geometry("900x700")
        view_win.configure(bg=BG_COLOR)
        
        # Stylish Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                      background="#dfe6e9", 
                      fieldbackground="#dfe6e9", 
                      foreground="black",
                      font=FONT,
                      rowheight=30)
        style.configure("Treeview.Heading", 
                      background=BUTTON_COLOR, 
                      foreground="white",
                      font=BUTTON_FONT,
                      padding=5)
        style.map("Treeview", 
                background=[("selected", ACCENT_COLOR)])
        
        tree_frame = tk.Frame(view_win, bg=BG_COLOR)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tree = ttk.Treeview(tree_frame, columns=("Date", "Text"), show="headings")
        tree.heading("Date", text="📅 Date")
        tree.heading("Text", text="📝 Entry Preview")
        tree.column("Date", width=200, anchor="center")
        tree.column("Text", width=600, anchor="w")
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)
        
        for entry_id, date, text in entries:
            tree.insert("", "end", values=(date, text[:100] + "..." if len(text) > 100 else text))
        
        # Action Buttons
        action_frame = tk.Frame(view_win, bg=BG_COLOR)
        action_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        edit_btn = tk.Button(
            action_frame, 
            text="✏️ Edit Selected", 
            command=lambda: self.edit_entry(tree),
            bg="#fdcb6e", 
            fg="black",
            font=BUTTON_FONT,
            borderwidth=0,
            padx=15,
            pady=8,
            activebackground="#ffeaa7",
            cursor="hand2"
        )
        edit_btn.pack(side="left", padx=5, expand=True, fill="x")
        
        delete_btn = tk.Button(
            action_frame, 
            text="🗑️ Delete Selected", 
            command=lambda: self.delete_entry(tree),
            bg="#d63031", 
            fg="white",
            font=BUTTON_FONT,
            borderwidth=0,
            padx=15,
            pady=8,
            activebackground="#ff7675",
            cursor="hand2"
        )
        delete_btn.pack(side="left", padx=5, expand=True, fill="x")
        
        # Add hover effects
        edit_btn.bind("<Enter>", lambda e: edit_btn.config(bg="#ffeaa7"))
        edit_btn.bind("<Leave>", lambda e: edit_btn.config(bg="#fdcb6e"))
        delete_btn.bind("<Enter>", lambda e: delete_btn.config(bg="#ff7675"))
        delete_btn.bind("<Leave>", lambda e: delete_btn.config(bg="#d63031"))
    
    def edit_entry(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No entry selected!")
            return
        
        selected_date = tree.item(selected_item)["values"][0]
        conn = sqlite3.connect("diary.db")
        cursor = conn.execute("SELECT id, entry_text FROM entries WHERE entry_date=?", (selected_date,))
        entry = cursor.fetchone()
        conn.close()
        
        if entry:
            edit_win = tk.Toplevel(self.root)
            edit_win.title("✏️ Edit Entry")
            edit_win.geometry("600x500")
            edit_win.configure(bg=BG_COLOR)
            
            # Text Area with Scrollbar
            text_frame = tk.Frame(edit_win, bg=BG_COLOR)
            text_frame.pack(padx=20, pady=20, fill="both", expand=True)
            
            text_border = tk.Frame(text_frame, bg=ACCENT_COLOR)
            text_border.pack(fill="both", expand=True, padx=5, pady=5)
            
            scrollbar = tk.Scrollbar(text_border)
            scrollbar.pack(side="right", fill="y")
            
            text_area = tk.Text(
                text_border, 
                wrap="word", 
                height=15, 
                font=FONT, 
                bg=TEXT_BG, 
                fg="black",
                yscrollcommand=scrollbar.set,
                padx=10,
                pady=10
            )
            text_area.insert("1.0", entry[1])
            text_area.pack(fill="both", expand=True)
            scrollbar.config(command=text_area.yview)
            
            # Save Button
            save_frame = tk.Frame(edit_win, bg=BG_COLOR)
            save_frame.pack(pady=(0, 20))
            
            save_btn = tk.Button(
                save_frame, 
                text="💾 Save Changes", 
                command=lambda: self.update_entry(entry[0], text_area.get("1.0", tk.END).strip(), edit_win),
                bg=BUTTON_COLOR, 
                fg="white",
                font=BUTTON_FONT,
                borderwidth=0,
                padx=20,
                pady=8,
                activebackground="#74b9ff",
                cursor="hand2"
            )
            save_btn.pack()
            
            # Add hover effect
            save_btn.bind("<Enter>", lambda e: save_btn.config(bg="#74b9ff"))
            save_btn.bind("<Leave>", lambda e: save_btn.config(bg=BUTTON_COLOR))
    
    def update_entry(self, entry_id, new_text, window):
        if new_text:
            conn = sqlite3.connect("diary.db")
            conn.execute("UPDATE entries SET entry_text=? WHERE id=?", (new_text, entry_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Entry updated! ✨")
            window.destroy()
        else:
            messagebox.showwarning("Warning", "Cannot save an empty entry!")
    
    def delete_entry(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No entry selected!")
            return
        
        selected_date = tree.item(selected_item)["values"][0]
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this entry?"):
            conn = sqlite3.connect("diary.db")
            conn.execute("DELETE FROM entries WHERE entry_date=?", (selected_date,))
            conn.commit()
            conn.close()
            tree.delete(selected_item)
            messagebox.showinfo("Success", "Entry deleted! 🗑️")
    
    def open_search_window(self):
        search_win = tk.Toplevel(self.root)
        search_win.title("🔍 Search Entries")
        search_win.geometry("500x300")
        search_win.configure(bg=BG_COLOR)
        
        search_frame = tk.Frame(search_win, bg=BG_COLOR)
        search_frame.pack(pady=30)
        
        tk.Label(
            search_frame, 
            text="Search by Keyword or Date (YYYY-MM-DD):", 
            font=FONT, 
            bg=BG_COLOR, 
            fg="white"
        ).pack(pady=10)
        
        self.search_entry = tk.Entry(
            search_frame, 
            width=40, 
            font=FONT,
            bg=TEXT_BG,
            fg="black",
            insertbackground="black"
        )
        self.search_entry.pack(pady=10, ipady=5)
        
        search_btn = tk.Button(
            search_frame, 
            text="🔍 Search Now", 
            command=lambda: self.search_entries(self.search_entry.get(), search_win),
            bg="#6c5ce7", 
            fg="white",
            font=BUTTON_FONT,
            borderwidth=0,
            padx=20,
            pady=8,
            activebackground="#a29bfe",
            cursor="hand2"
        )
        search_btn.pack(pady=10)
        
        # Add hover effect
        search_btn.bind("<Enter>", lambda e: search_btn.config(bg="#a29bfe"))
        search_btn.bind("<Leave>", lambda e: search_btn.config(bg="#6c5ce7"))
    
    def search_entries(self, keyword, window):
        if not keyword:
            messagebox.showwarning("Warning", "Please enter a search term!")
            return
        
        conn = sqlite3.connect("diary.db")
        if keyword.replace("-", "").isdigit():  # If input is a date
            cursor = conn.execute("SELECT entry_date, entry_text FROM entries WHERE entry_date LIKE ? ORDER BY id DESC", 
                                (f"%{keyword}%",))
        else:  # If input is a keyword
            cursor = conn.execute("SELECT entry_date, entry_text FROM entries WHERE entry_text LIKE ? ORDER BY id DESC", 
                                (f"%{keyword}%",))
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            messagebox.showinfo("No Results", "No matching entries found. 🧐")
            return
        
        result_win = tk.Toplevel(window)
        result_win.title("🔍 Search Results")
        result_win.geometry("800x600")
        result_win.configure(bg=BG_COLOR)
        
        # Create a canvas with scrollbar
        canvas = tk.Canvas(result_win, bg=BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(result_win, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG_COLOR)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Display results
        for date, text in results:
            entry_frame = tk.Frame(scrollable_frame, bg=BG_COLOR)
            entry_frame.pack(fill="x", padx=20, pady=10)
            
            date_label = tk.Label(
                entry_frame,
                text=date,
                font=("Segoe UI", 12, "bold"),
                bg=BG_COLOR,
                fg=ACCENT_COLOR,
                anchor="w"
            )
            date_label.pack(fill="x")
            
            text_label = tk.Label(
                entry_frame,
                text=text,
                font=FONT,
                bg=BG_COLOR,
                fg="white",
                wraplength=700,
                justify="left",
                anchor="w"
            )
            text_label.pack(fill="x", pady=(5, 0))
            
            # Separator
            tk.Frame(
                entry_frame,
                height=1,
                bg="#636e72"
            ).pack(fill="x", pady=10)
    
    def export_entries(self):
        conn = sqlite3.connect("diary.db")
        cursor = conn.execute("SELECT entry_date, entry_text FROM entries ORDER BY id DESC")
        entries = cursor.fetchall()
        conn.close()
        
        if not entries:
            messagebox.showwarning("Warning", "No entries to export!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Save Diary Export"
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write("=== My Diary Export ===\n\n")
                    for date, text in entries:
                        file.write(f"📅 {date}\n")
                        file.write(f"{text}\n\n")
                        file.write("―" * 50 + "\n\n")
                messagebox.showinfo("Success", f"Diary exported successfully!\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export:\n{str(e)}")

# ---------------------------- RUN THE APP ---------------------------- #
if __name__ == "__main__":
    root = tk.Tk()
    
    # Set window icon (if available)
    try:
        root.iconbitmap("diary.ico")  # Replace with your icon file
    except:
        pass
    
    app = DiaryApp(root)
    root.mainloop()