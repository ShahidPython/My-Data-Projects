# gui.py — Modern Tkinter GUI with ttkbootstrap

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
from storage import init_db, get_all_cards, add_card, delete_card, update_card, get_card, get_categories, search_cards

class FlashcardApp:
    def __init__(self):
        self.root = tb.Window(themename="flatly")
        self.root.title("Professional Flashcard App")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Initialize database
        init_db()
        
        # App state
        self.cards = []
        self.current_index = 0
        self.filter_category = None
        self.search_term = ""
        
        self.setup_ui()
        self.load_cards()
        
    def setup_ui(self):
        # Create notebook for tabs
        self.notebook = tb.Notebook(self.root, bootstyle="primary")
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Study tab
        self.study_frame = tb.Frame(self.notebook)
        self.notebook.add(self.study_frame, text="📚 Study")
        self.setup_study_tab()
        
        # Manage tab
        self.manage_frame = tb.Frame(self.notebook)
        self.notebook.add(self.manage_frame, text="📋 Manage")
        self.setup_manage_tab()
        
        # Add tab
        self.add_frame = tb.Frame(self.notebook)
        self.notebook.add(self.add_frame, text="➕ Add")
        self.setup_add_tab()
        
        # Stats tab
        self.stats_frame = tb.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="📊 Statistics")
        self.setup_stats_tab()
        
    def setup_study_tab(self):
        # Header with controls
        header = tb.Frame(self.study_frame)
        header.pack(fill="x", padx=10, pady=10)
        
        tb.Label(header, text="Study Mode", font=("Helvetica", 16, "bold")).pack(side="left")
        
        controls = tb.Frame(header)
        controls.pack(side="right")
        
        self.category_var = tk.StringVar(value="All Categories")
        categories = ["All Categories"] + get_categories()
        self.category_dropdown = tb.Combobox(controls, textvariable=self.category_var, values=categories, width=20)
        self.category_dropdown.pack(side="left", padx=5)
        self.category_dropdown.bind("<<ComboboxSelected>>", self.filter_cards)
        
        tb.Button(controls, text="🔍 Search", command=self.open_search, bootstyle="outline").pack(side="left", padx=5)
        tb.Button(controls, text="🔄 Shuffle", command=self.shuffle_cards, bootstyle="outline").pack(side="left", padx=5)
        
        # Flashcard display
        card_frame = tb.Frame(self.study_frame)
        card_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Card with nice styling
        self.card = tb.Frame(card_frame, bootstyle="light", relief="solid", borderwidth=1)
        self.card.pack(fill="both", expand=True)
        
        self.question_text = scrolledtext.ScrolledText(
            self.card, wrap="word", font=("Helvetica", 14), height=6,
            relief="flat", bg="#f8f9fa", padx=20, pady=20
        )
        self.question_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.question_text.config(state="disabled")
        
        self.answer_text = scrolledtext.ScrolledText(
            self.card, wrap="word", font=("Helvetica", 14), height=6,
            relief="flat", bg="#e9ecef", padx=20, pady=20
        )
        self.answer_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.answer_text.config(state="disabled")
        self.answer_text.pack_forget()  # Hidden initially
        
        # Navigation and controls
        nav_frame = tb.Frame(self.study_frame)
        nav_frame.pack(fill="x", padx=10, pady=10)
        
        tb.Button(nav_frame, text="⏮️ Previous", command=self.prev_card, bootstyle="outline").pack(side="left", padx=5)
        self.reveal_btn = tb.Button(nav_frame, text="👁️ Reveal Answer", command=self.reveal_answer, bootstyle="primary")
        self.reveal_btn.pack(side="left", padx=20)
        tb.Button(nav_frame, text="Next ⏭️", command=self.next_card, bootstyle="outline").pack(side="left", padx=5)
        
        # Rating buttons (initially hidden)
        self.rating_frame = tb.Frame(self.study_frame)
        self.rating_frame.pack(fill="x", padx=10, pady=5)
        
        tb.Button(self.rating_frame, text="✅ Knew It", command=lambda: self.rate_card(True), 
                 bootstyle="success-outline").pack(side="left", padx=5)
        tb.Button(self.rating_frame, text="❌ Need Practice", command=lambda: self.rate_card(False), 
                 bootstyle="danger-outline").pack(side="left", padx=5)
        self.rating_frame.pack_forget()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tb.Label(self.study_frame, textvariable=self.status_var, bootstyle="inverse-primary")
        status_bar.pack(fill="x", side="bottom", ipady=5)
        
    def setup_manage_tab(self):
        # Search and filter
        filter_frame = tb.Frame(self.manage_frame)
        filter_frame.pack(fill="x", padx=10, pady=10)
        
        tb.Label(filter_frame, text="Search:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        search_entry = tb.Entry(filter_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<Return>", self.search_cards)
        
        tb.Label(filter_frame, text="Category:").pack(side="left", padx=10)
        self.manage_category_var = tk.StringVar(value="All Categories")
        categories = ["All Categories"] + get_categories()
        category_dropdown = tb.Combobox(filter_frame, textvariable=self.manage_category_var, values=categories, width=20)
        category_dropdown.pack(side="left", padx=5)
        category_dropdown.bind("<<ComboboxSelected>>", self.filter_manage_cards)
        
        tb.Button(filter_frame, text="🔍 Search", command=self.search_cards, bootstyle="outline").pack(side="left", padx=5)
        tb.Button(filter_frame, text="🔄 Refresh", command=self.load_cards, bootstyle="outline").pack(side="left", padx=5)
        
        # Cards table
        columns = ("id", "question", "answer", "category")
        self.tree = tb.Treeview(self.manage_frame, columns=columns, show="headings", bootstyle="primary")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("question", text="Question")
        self.tree.heading("answer", text="Answer")
        self.tree.heading("category", text="Category")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("question", width=300)
        self.tree.column("answer", width=300)
        self.tree.column("category", width=100)
        
        scrollbar = tb.Scrollbar(self.manage_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)
        
        # Context menu for treeview
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self.edit_selected_card)
        self.context_menu.add_command(label="Delete", command=self.delete_selected_card)
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Action buttons
        btn_frame = tb.Frame(self.manage_frame)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        tb.Button(btn_frame, text="✏️ Edit Selected", command=self.edit_selected_card, bootstyle="warning").pack(side="left", padx=5)
        tb.Button(btn_frame, text="🗑️ Delete Selected", command=self.delete_selected_card, bootstyle="danger").pack(side="left", padx=5)
        tb.Button(btn_frame, text="📝 Add New", command=lambda: self.notebook.select(2), bootstyle="success").pack(side="right", padx=5)
        
    def setup_add_tab(self):
        form_frame = tb.Frame(self.add_frame)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tb.Label(form_frame, text="Add New Flashcard", font=("Helvetica", 16, "bold")).pack(pady=10)
        
        # Question
        tb.Label(form_frame, text="Question:", anchor="w").pack(fill="x", pady=(10, 5))
        self.add_question = scrolledtext.ScrolledText(form_frame, height=4, wrap="word", font=("Helvetica", 12))
        self.add_question.pack(fill="x", pady=5)
        
        # Answer
        tb.Label(form_frame, text="Answer:", anchor="w").pack(fill="x", pady=(10, 5))
        self.add_answer = scrolledtext.ScrolledText(form_frame, height=4, wrap="word", font=("Helvetica", 12))
        self.add_answer.pack(fill="x", pady=5)
        
        # Category
        tb.Label(form_frame, text="Category (optional):", anchor="w").pack(fill="x", pady=(10, 5))
        category_frame = tb.Frame(form_frame)
        category_frame.pack(fill="x", pady=5)
        
        self.add_category = tb.Entry(category_frame, font=("Helvetica", 12))
        self.add_category.pack(side="left", fill="x", expand=True)
        
        # Existing categories dropdown
        categories = get_categories()
        if categories:
            self.category_var = tk.StringVar()
            category_dropdown = tb.Combobox(category_frame, textvariable=self.category_var, values=categories, width=15)
            category_dropdown.pack(side="right", padx=(5, 0))
            category_dropdown.bind("<<ComboboxSelected>>", lambda e: self.add_category.insert(0, self.category_var.get()))
        
        # Buttons
        btn_frame = tb.Frame(form_frame)
        btn_frame.pack(fill="x", pady=20)
        
        tb.Button(btn_frame, text="➕ Add Another", command=self.add_new_card, bootstyle="outline").pack(side="left", padx=5)
        tb.Button(btn_frame, text="🗑️ Clear", command=self.clear_add_form, bootstyle="outline").pack(side="left", padx=5)
        tb.Button(btn_frame, text="💾 Save", command=self.add_new_card, bootstyle="primary").pack(side="right", padx=5)
        
    def setup_stats_tab(self):
        stats_frame = tb.Frame(self.stats_frame)
        stats_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tb.Label(stats_frame, text="Flashcard Statistics", font=("Helvetica", 16, "bold")).pack(pady=10)
        
        # Stats cards
        cards_frame = tb.Frame(stats_frame)
        cards_frame.pack(fill="x", pady=10)
        
        # Total cards
        total_cards = len(get_all_cards())
        total_frame = tb.Frame(cards_frame, bootstyle="light", relief="solid", borderwidth=1)
        total_frame.pack(side="left", fill="both", expand=True, padx=5)
        tb.Label(total_frame, text="Total Cards", font=("Helvetica", 12)).pack(pady=(10, 5))
        tb.Label(total_frame, text=str(total_cards), font=("Helvetica", 24, "bold")).pack(pady=(0, 10))
        
        # Categories count
        categories = get_categories()
        cat_frame = tb.Frame(cards_frame, bootstyle="light", relief="solid", borderwidth=1)
        cat_frame.pack(side="left", fill="both", expand=True, padx=5)
        tb.Label(cat_frame, text="Categories", font=("Helvetica", 12)).pack(pady=(10, 5))
        tb.Label(cat_frame, text=str(len(categories)), font=("Helvetica", 24, "bold")).pack(pady=(0, 10))
        
        # Category breakdown
        if categories:
            tb.Label(stats_frame, text="Cards by Category", font=("Helvetica", 14, "bold")).pack(anchor="w", pady=(20, 10))
            
            for category in categories:
                cat_cards = get_all_cards(category)
                frame = tb.Frame(stats_frame)
                frame.pack(fill="x", pady=5)
                
                tb.Label(frame, text=category, width=20, anchor="w").pack(side="left")
                progress = tb.Progressbar(
                    frame, orient="horizontal", 
                    value=len(cat_cards)/total_cards*100,
                    bootstyle="success-striped"
                )
                progress.pack(side="left", fill="x", expand=True, padx=5)
                tb.Label(frame, text=f"{len(cat_cards)} cards", width=10).pack(side="right")
        
    def load_cards(self, category=None):
        self.cards = get_all_cards(category)
        self.current_index = 0
        self.update_card_display()
        self.update_treeview()
        
    def update_card_display(self):
        if not self.cards:
            self.question_text.config(state="normal")
            self.question_text.delete(1.0, tk.END)
            self.question_text.insert(1.0, "No flashcards available. Add some in the Manage tab.")
            self.question_text.config(state="disabled")
            self.reveal_btn.config(state="disabled")
            return
            
        self.reveal_btn.config(state="normal")
        _id, question, answer, category = self.cards[self.current_index]
        
        self.question_text.config(state="normal")
        self.question_text.delete(1.0, tk.END)
        self.question_text.insert(1.0, question)
        self.question_text.config(state="disabled")
        
        self.answer_text.config(state="normal")
        self.answer_text.delete(1.0, tk.END)
        self.answer_text.insert(1.0, answer)
        self.answer_text.config(state="disabled")
        
        # Hide answer and show question
        self.answer_text.pack_forget()
        self.question_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.rating_frame.pack_forget()
        self.reveal_btn.config(text="👁️ Reveal Answer", state="normal")
        
        # Update status
        total = len(self.cards)
        self.status_var.set(f"Card {self.current_index + 1} of {total} | Category: {category if category else 'Uncategorized'}")
        
    def update_treeview(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add cards to treeview
        for card in self.cards:
            self.tree.insert("", "end", values=card)
            
    def next_card(self):
        if not self.cards:
            return
            
        self.current_index = (self.current_index + 1) % len(self.cards)
        self.update_card_display()
        
    def prev_card(self):
        if not self.cards:
            return
            
        self.current_index = (self.current_index - 1) % len(self.cards)
        self.update_card_display()
        
    def reveal_answer(self):
        self.answer_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.question_text.pack_forget()
        self.rating_frame.pack(fill="x", padx=10, pady=5)
        self.reveal_btn.config(state="disabled")
        
    def rate_card(self, knew_it):
        if knew_it:
            messagebox.showinfo("Good job!", "You're making progress!")
        else:
            messagebox.showinfo("Keep practicing", "This will go to your review list.")
        
        self.next_card()
        
    def filter_cards(self, event=None):
        category = self.category_var.get()
        if category == "All Categories":
            self.load_cards()
        else:
            self.load_cards(category)
            
    def filter_manage_cards(self, event=None):
        category = self.manage_category_var.get()
        if category == "All Categories":
            self.load_cards()
        else:
            self.load_cards(category)
            
    def search_cards(self, event=None):
        term = self.search_var.get()
        if term:
            self.cards = search_cards(term)
            self.current_index = 0
            self.update_card_display()
            self.update_treeview()
            
    def open_search(self):
        # Simple search dialog
        dialog = tb.Toplevel(self.root)
        dialog.title("Search Flashcards")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tb.Label(dialog, text="Search term:").pack(pady=(20, 5))
        
        search_var = tk.StringVar()
        entry = tb.Entry(dialog, textvariable=search_var, width=30)
        entry.pack(pady=5)
        entry.focus()
        
        def do_search():
            term = search_var.get()
            if term:
                self.cards = search_cards(term)
                self.current_index = 0
                self.update_card_display()
                self.update_treeview()
                dialog.destroy()
                
        btn_frame = tb.Frame(dialog)
        btn_frame.pack(pady=10)
        
        tb.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)
        tb.Button(btn_frame, text="Search", command=do_search, bootstyle="primary").pack(side="left", padx=5)
        
    def shuffle_cards(self):
        from random import shuffle
        if self.cards:
            shuffle(self.cards)
            self.current_index = 0
            self.update_card_display()
            
    def add_new_card(self):
        question = self.add_question.get(1.0, tk.END).strip()
        answer = self.add_answer.get(1.0, tk.END).strip()
        category = self.add_category.get().strip()
        
        if not question or not answer:
            messagebox.showerror("Error", "Both question and answer are required.")
            return
            
        add_card(question, answer, category if category else None)
        messagebox.showinfo("Success", "Flashcard added successfully!")
        
        # Clear form
        self.clear_add_form()
        
        # Refresh other tabs
        self.load_cards()
        self.setup_stats_tab()
        
    def clear_add_form(self):
        self.add_question.delete(1.0, tk.END)
        self.add_answer.delete(1.0, tk.END)
        self.add_category.delete(0, tk.END)
        
    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def edit_selected_card(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a card to edit.")
            return
            
        item = selection[0]
        card_id = self.tree.item(item, "values")[0]
        
        # Edit dialog
        dialog = tb.Toplevel(self.root)
        dialog.title("Edit Flashcard")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        card = get_card(card_id)
        if not card:
            messagebox.showerror("Error", "Card not found.")
            dialog.destroy()
            return
            
        _id, question, answer, category = card
        
        tb.Label(dialog, text="Edit Flashcard", font=("Helvetica", 14, "bold")).pack(pady=10)
        
        # Question
        tb.Label(dialog, text="Question:").pack(anchor="w", padx=20, pady=(10, 5))
        question_text = scrolledtext.ScrolledText(dialog, height=4, wrap="word")
        question_text.pack(fill="x", padx=20, pady=5)
        question_text.insert(1.0, question)
        
        # Answer
        tb.Label(dialog, text="Answer:").pack(anchor="w", padx=20, pady=(10, 5))
        answer_text = scrolledtext.ScrolledText(dialog, height=4, wrap="word")
        answer_text.pack(fill="x", padx=20, pady=5)
        answer_text.insert(1.0, answer)
        
        # Category
        tb.Label(dialog, text="Category:").pack(anchor="w", padx=20, pady=(10, 5))
        category_var = tk.StringVar(value=category if category else "")
        category_entry = tb.Entry(dialog, textvariable=category_var)
        category_entry.pack(fill="x", padx=20, pady=5)
        
        def save_changes():
            new_question = question_text.get(1.0, tk.END).strip()
            new_answer = answer_text.get(1.0, tk.END).strip()
            new_category = category_var.get().strip()
            
            if not new_question or not new_answer:
                messagebox.showerror("Error", "Both question and answer are required.")
                return
                
            update_card(card_id, new_question, new_answer, new_category if new_category else None)
            messagebox.showinfo("Success", "Flashcard updated successfully!")
            dialog.destroy()
            
            # Refresh data
            self.load_cards()
            self.update_card_display()
            
        btn_frame = tb.Frame(dialog)
        btn_frame.pack(fill="x", pady=10, padx=20)
        
        tb.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side="right", padx=5)
        tb.Button(btn_frame, text="Save", command=save_changes, bootstyle="primary").pack(side="right", padx=5)
        
    def delete_selected_card(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a card to delete.")
            return
            
        item = selection[0]
        card_id = self.tree.item(item, "values")[0]
        question = self.tree.item(item, "values")[1]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete this card?\n\n{question}"):
            if delete_card(card_id):
                messagebox.showinfo("Success", "Card deleted successfully.")
                self.load_cards()
                self.update_card_display()
            else:
                messagebox.showerror("Error", "Failed to delete card.")
                
    def run(self):
        self.root.mainloop()

def run_gui():
    app = FlashcardApp()
    app.run()