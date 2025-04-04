#External Imports
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from datetime import datetime

# Example placeholders: adjust or remove these imports as needed.
import matplotlib
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mplcursors
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# My Imports
from database import Database
from components import BasePage, Dialog, Container
from sidebar import Sidebar


class DecksPage(BasePage):
    def __init__(self, master, user_id, switch_page):
        # Set up the BasePage (which creates sidebar, main_content, etc.)
        super().__init__(master, user_id, switch_page)
        self.selected_decks = set()

        # Header
        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 0))
        ctk.CTkLabel(header_frame, text="My Decks", font=("Inter", 24, "bold"), text_color="black").pack(side="left")

        # Filter frame (search and priority)
        filter_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        filter_frame.pack(side="right", padx=10)
        self.deck_search_var = ctk.StringVar()
        self.deck_search_entry = ctk.CTkEntry(filter_frame, textvariable=self.deck_search_var,
                                              placeholder_text="Search deck", placeholder_text_color="#D1D1D1",
                                              text_color="#000000", fg_color="white", border_color="#e5e7eb", width=200)
        self.deck_search_entry.pack(side="left", padx=5)
        self.deck_priority_filter_var = ctk.StringVar(value="All")
        self.deck_priority_filter_menu = ctk.CTkOptionMenu(filter_frame,
                                                          values=["All", "High", "Medium", "Low"],
                                                          variable=self.deck_priority_filter_var,
                                                          width=120, fg_color="white",
                                                          button_color="#F3F4F6",
                                                          button_hover_color="#E5E7EB",
                                                          text_color="#111827")
        self.deck_priority_filter_menu.pack(side="left", padx=5)
        self.deck_search_var.trace_add("write", lambda *args: self.display_decks())
        self.deck_priority_filter_var.trace_add("write", lambda *args: self.display_decks())

        # Buttons container
        buttons = ctk.CTkFrame(header_frame, fg_color="transparent")
        buttons.pack(side="right")
        ctk.CTkButton(buttons, text="+ Add", width=70, height=32, corner_radius=16,
                      fg_color="#F3F4F6", text_color="black", hover_color="#E5E7EB",
                      command=self.add_deck).pack(side="left", padx=5)
        self.delete_button = ctk.CTkButton(buttons, text="Delete Selected", width=70, height=32,
                                           corner_radius=16, fg_color="#FEE2E2", text_color="#DC2626",
                                           hover_color="#FECACA", state="disabled",
                                           command=self.delete_selected_decks)
        self.delete_button.pack(side="left", padx=5)

        separator = ctk.CTkFrame(self.main_content, height=1, fg_color="#E5E7EB")
        separator.pack(fill="x", padx=30, pady=(20, 0))

        # Scrollable decks frame
        self.decks_frame = ctk.CTkScrollableFrame(self.main_content, fg_color="transparent",
                                                   scrollbar_button_color="#E5E7EB",
                                                   scrollbar_button_hover_color="#D1D5DB")
        self.decks_frame.pack(fill="both", expand=True, padx=30, pady=20)
        self.decks_frame.grid_columnconfigure((0, 1, 2), weight=1, pad=10)

        self.display_decks()

    def display_decks(self):
        # Clear current deck containers
        for widget in self.decks_frame.winfo_children():
            widget.destroy()

        db = Database()
        deck_list = []
        decks = db.get_decks(self.user_id)

        # Build deck_list as tuples: (deck_id, deck_name, avg_ef, card_count)
        for deck_id, deck_name in decks:
            cards = db.get_cards(deck_id)
            if cards:
                total_ef = sum(db.get_card_easiness(self.user_id, c[0]) for c in cards)
                avg_ef = total_ef / len(cards)
            else:
                avg_ef = 2.5
            card_count = db.get_card_count(deck_id)
            deck_list.append((deck_id, deck_name, avg_ef, card_count))

        # Filter by search query
        search_query = self.deck_search_var.get().lower().strip()
        if search_query:
            deck_list = [d for d in deck_list if search_query in d[1].lower()]

        # Filter by priority (using avg_ef)
        priority_filter = self.deck_priority_filter_var.get().lower()
        if priority_filter != "all":
            if priority_filter == "high":
                deck_list = [d for d in deck_list if d[2] < 2.0]
            elif priority_filter == "medium":
                deck_list = [d for d in deck_list if 2.0 <= d[2] < 2.5]
            elif priority_filter == "low":
                deck_list = [d for d in deck_list if d[2] >= 2.5]

        if not deck_list:
            no_decks_frame = ctk.CTkFrame(self.decks_frame, fg_color="transparent")
            no_decks_frame.pack(fill="both", expand=True)
            ctk.CTkLabel(no_decks_frame, text="No decks found", font=("Inter", 16, "bold"),
                         text_color="#4B5563").pack(expand=True, pady=50)
            return

        # Sort decks using BST (based on avg_ef)
        from graph import DeckNode, insert_node, in_order_traversal
        root = None
        for deck in deck_list:
            node = DeckNode(deck_id=deck[0], deck_name=deck[1], avg_ef=deck[2], card_count=deck[3])
            root = insert_node(root, node)
        sorted_nodes = in_order_traversal(root)

        # Display decks in a 3-column grid
        row, col = 0, 0
        for node in sorted_nodes:
            deck_container = DeckContainer(self.decks_frame, deck_id=node.deck_id,
                                             deck_name=node.deck_name, card_count=node.card_count,
                                             selection_callback=self.toggle_deck_selection,
                                             avg_ef=node.avg_ef, edit_callback=self.edit_deck,
                                             delete_callback=self.delete_deck)
            deck_container.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            col += 1
            if col == 3:
                col = 0
                row += 1

    def add_deck(self):
        dialog = AddDeckDialog(self)
        new_deck_name = dialog.get_deck_name()
        if new_deck_name:
            db = Database()
            deck_id = db.create_deck(self.user_id, new_deck_name)
            if deck_id:
                self.display_decks()
                if hasattr(self, 'sidebar'):
                    self.sidebar.display_decks()

    def edit_deck(self, deck_id):
        db = Database()
        deck_info = db.get_deck_info(deck_id)
        current_name = deck_info["name"]
        dialog = EditDeckDialog(self, deck_id, current_name)

    def delete_deck(self, deck_id):
        if messagebox.askyesno("Delete Deck", "Are you sure you want to delete this deck?"):
            db = Database()
            db.delete_deck(deck_id)
            self.display_decks()
            if hasattr(self, 'sidebar'):
                self.sidebar.display_decks()

    def toggle_deck_selection(self, deck_id, is_selected):
        if is_selected:
            self.selected_decks.add(deck_id)
        else:
            self.selected_decks.discard(deck_id)
        self.delete_button.configure(state="normal" if self.selected_decks else "disabled")

    def delete_selected_decks(self):
        if not self.selected_decks:
            return
        if messagebox.askyesno("Delete Decks", f"Are you sure you want to delete {len(self.selected_decks)} deck(s)?"):
            db = Database()
            for deck_id in self.selected_decks:
                db.delete_deck(deck_id)
            self.selected_decks.clear()
            self.display_decks()
            if hasattr(self, 'sidebar'):
                self.sidebar.display_decks()
            self.delete_button.configure(state="disabled")

class DeckContainer(Container):
    def __init__(self, master, deck_id, deck_name, card_count, selection_callback, avg_ef, edit_callback, delete_callback):
        super().__init__(master)
        self.deck_id = deck_id
        self.selection_callback = selection_callback  # For single-select tracking
        self.selected = False
        self.avg_ef = avg_ef
        self.edit_callback = edit_callback
        self.delete_callback = delete_callback

        # Main content container
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=20, pady=20)

        # Left: deck info
        self.info_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.info_frame.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(
            self.info_frame,
            text=deck_name,
            font=("Inter", 16, "bold"),
            text_color="black"
        ).pack(anchor="w")
        ctk.CTkLabel(
            self.info_frame,
            text=f"{card_count} cards",
            font=("Inter", 14),
            text_color="#6B7280"
        ).pack(anchor="w", pady=(5, 0))

        # Display due count (example)
        db = Database()
        due_count = (
            db.get_due_cards_count(self.selection_callback.__self__.user_id, deck_id)
            if hasattr(self.selection_callback, '__self__') else 0
        )
        ctk.CTkLabel(
            self.info_frame,
            text=f"{due_count} available for review",
            font=("Inter", 12),
            text_color="#DC2626"
        ).pack(anchor="w", pady=(5, 0))

        # Priority indicator
        if self.avg_ef < 2.0:
            priority_text = "High Priority"
            tag_color = "red"
        elif self.avg_ef < 2.5:
            priority_text = "Medium Priority"
            tag_color = "orange"
        else:
            priority_text = "Low Priority"
            tag_color = "green"
        ctk.CTkLabel(
            self.info_frame,
            text=priority_text,
            font=("Inter", 12, "bold"),
            text_color=tag_color
        ).pack(anchor="w", pady=(5, 0))

        # Buttons container (Edit/Delete) at bottom (only if callbacks provided)
        if self.edit_callback is not None and self.delete_callback is not None:
            btn_container = ctk.CTkFrame(self.content, fg_color="transparent")
            btn_container.pack(side="bottom", fill="x", pady=(10, 0))
            ctk.CTkButton(
                btn_container,
                text="Edit",
                width=70,
                height=32,
                corner_radius=16,
                fg_color="#F3F4F6",
                text_color="black",
                hover_color="#E5E7EB",
                command=lambda: self.edit_callback(self.deck_id)
            ).pack(side="left", padx=(5, 2), pady=5)
            ctk.CTkButton(
                btn_container,
                text="Delete",
                width=70,
                height=32,
                corner_radius=16,
                fg_color="#FEE2E2",
                text_color="#DC2626",
                hover_color="#FECACA",
                command=lambda: self.delete_callback(self.deck_id)
            ).pack(side="left", padx=(2, 5), pady=5)

        # Single‐selection checkbox at TOP RIGHT
        self.checkbox = ctk.CTkCheckBox(
            self,
            text="",
            width=24,
            height=24,
            corner_radius=6,
            command=self.on_checkbox_toggle,
            hover_color="#ffffff"
        )
        self.checkbox.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)


    def toggle_selection(self, event=None):
        if event.widget == self.checkbox:
            return
        self.selected = not self.selected
        if self.selected:
            self.checkbox.select()
        else:
            self.checkbox.deselect()
        if self.selection_callback:
            self.selection_callback(self.deck_id, self.selected)
        self.configure(fg_color="#F5F3FF" if self.selected else "white")

    def on_checkbox_toggle(self):
        self.selected = self.checkbox.get()
        if self.selection_callback:
            self.selection_callback(self.deck_id, self.selected)
        if self.selected:
            self.configure(fg_color="#F5F3FF")
            self.checkbox.configure(
                fg_color="#636ae8",
                checkmark_color="white"
            )
        else:
            self.configure(fg_color="white")
            self.checkbox.configure(
                fg_color="white",
                checkmark_color="black"
            )

class CardContainer(Container):
    
    def __init__(self, master, card_id, question, answer,
                 edit_callback, delete_callback, ef, user_id,
                 selection_callback=None):
        super().__init__(master)
        self.card_id = card_id
        self.selection_callback = selection_callback
        self.selected = False

        # Main container for card content
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            self.content,
            text=question,
            font=("Inter", 16, "bold"),
            text_color="black"
        ).pack(anchor="w")
        ctk.CTkLabel(
            self.content,
            text=answer,
            font=("Inter", 14),
            text_color="black"
        ).pack(anchor="w", pady=(5, 0))

        # Priority indicator
        if ef < 2.0:
            priority_text = "High Priority"
            color = "red"
        elif ef < 2.5:
            priority_text = "Medium Priority"
            color = "orange"
        else:
            priority_text = "Low Priority"
            color = "green"
        ctk.CTkLabel(
            self.content,
            text=priority_text,
            font=("Inter", 12, "bold"),
            text_color=color
        ).pack(anchor="w", pady=(5, 10))

        # Buttons container (Edit/Delete)
        buttons = ctk.CTkFrame(self.content, fg_color="transparent")
        buttons.pack(side="bottom", fill="x")
        btn_container = ctk.CTkFrame(buttons, fg_color="transparent")
        btn_container.pack(side="right", padx=5, pady=5)

        ctk.CTkButton(
            btn_container,
            text="Edit",
            width=70,
            height=32,
            corner_radius=16,
            fg_color="#F3F4F6",
            text_color="black",
            hover_color="#E5E7EB",
            command=lambda: edit_callback(self.card_id)
        ).pack(side="left", padx=(5, 2))
        ctk.CTkButton(
            btn_container,
            text="Delete",
            width=70,
            height=32,
            corner_radius=16,
            fg_color="#FEE2E2",
            text_color="#DC2626",
            hover_color="#FECACA",
            command=lambda: delete_callback(self.card_id)
        ).pack(side="left", padx=(2, 5))

        # Multi‐selection checkbox at TOP RIGHT
        self.checkbox = ctk.CTkCheckBox(
            self,
            text="",
            width=24,
            height=24,
            corner_radius=6,
            command=self.on_checkbox_toggle,
            hover_color="#ffffff"

        )
        self.checkbox.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

        # Bind clicks on the container to toggle selection

    def toggle_selection(self, event=None):
        # Avoid toggling if the click came directly from the checkbox
        if event.widget == self.checkbox:
            return
        self.selected = not self.selected
        if self.selected:
            self.checkbox.select()
        else:
            self.checkbox.deselect()
        if self.selection_callback:
            self.selection_callback(self.card_id, self.selected)
        self.configure(fg_color="#F5F3FF" if self.selected else "white")

    def on_checkbox_toggle(self):
        self.selected = self.checkbox.get()
        if self.selection_callback:
            self.selection_callback(self.card_id, self.selected)
        if self.selected:
            self.configure(fg_color="#F5F3FF")
            self.checkbox.configure(
                fg_color="#636ae8",
                border_color="#636ae8",
                checkmark_color="white"
            )
        else:
            self.configure(fg_color="white")
            self.checkbox.configure(fg_color="white", checkmark_color="black", hover_color="white")
class CardsPage(BasePage):
    def __init__(self, master, user_id, deck_id, switch_page):
        super().__init__(master, user_id, switch_page)
        self.deck_id = deck_id
        self.selected_cards = set()
        self.deck_info = self.db.get_deck_info(self.deck_id)

        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=20)
        ctk.CTkLabel(header_frame, text=self.deck_info["name"], font=("Inter", 24, "bold"), text_color="black").pack(side="left")
        ctk.CTkLabel(header_frame, text=f"{self.deck_info['card_count']} cards", font=("Inter", 14), text_color="#6B7280").pack(side="left", padx=(10,0))

        filter_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        filter_frame.pack(side="right", padx=10)
        self.card_search_var = ctk.StringVar()
        self.card_search_entry = ctk.CTkEntry(filter_frame, textvariable=self.card_search_var,
                                              placeholder_text="Search card", placeholder_text_color="#D1D1D1",
                                              text_color="#000000", fg_color="white", border_color="#e5e7eb", width=200)
        self.card_search_entry.pack(side="left", padx=5)
        self.card_priority_filter_var = ctk.StringVar(value="All")
        self.card_priority_filter_menu = ctk.CTkOptionMenu(filter_frame,
                                                          values=["All", "High", "Medium", "Low"],
                                                          variable=self.card_priority_filter_var,
                                                          width=120, fg_color="white",
                                                          button_color="#F3F4F6",
                                                          button_hover_color="#E5E7EB",
                                                          text_color="#111827")
        self.card_priority_filter_menu.pack(side="left", padx=5)
        self.card_search_var.trace_add("write", lambda *args: self.display_cards())
        self.card_priority_filter_var.trace_add("write", lambda *args: self.display_cards())

        self.delete_cards_button = ctk.CTkButton(header_frame, text="Delete Selected", width=120, height=32,
                                                 corner_radius=16, fg_color="#FEE2E2", text_color="#DC2626",
                                                 hover_color="#FECACA", state="disabled", command=self.delete_selected_cards)
        self.delete_cards_button.pack(side="right", padx=5)
        ctk.CTkButton(header_frame, text="+ Add Card", width=70, height=32, corner_radius=16,
                      fg_color="#F3F4F6", text_color="black", hover_color="#E5E7EB",
                      command=self.add_card).pack(side="right", padx=5)

        self.cards_frame = ctk.CTkScrollableFrame(self.main_content, fg_color="transparent",
                                                   scrollbar_button_color="#E5E7EB",
                                                   scrollbar_button_hover_color="#D1D5DB")
        self.cards_frame.pack(fill="both", expand=True, padx=30, pady=20)
        self.display_cards()

    def display_cards(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        raw_cards = self.db.get_cards(self.deck_id)
        cards = []
        for card in raw_cards:
            card_id, _, question, answer = card
            ef = self.db.get_card_easiness(self.user_id, card_id)
            cards.append((card_id, question, answer, ef))

        # First filter by search and priority
        search_query = self.card_search_var.get().lower().strip()
        if search_query:
            cards = [c for c in cards if search_query in c[1].lower()]
        priority_filter = self.card_priority_filter_var.get().lower()
        if priority_filter != "all":
            if priority_filter == "high":
                cards = [c for c in cards if c[3] < 2.0]
            elif priority_filter == "medium":
                cards = [c for c in cards if 2.0 <= c[3] < 2.5]
            elif priority_filter == "low":
                cards = [c for c in cards if c[3] >= 2.5]

        if not cards:
            no_cards_frame = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
            no_cards_frame.pack(fill="both", expand=True)
            ctk.CTkLabel(no_cards_frame, text="No cards found", font=("Inter", 16, "bold"),
                         text_color="#4B5563").pack(expand=True, pady=50)
            return

        # Sort cards using merge sort based on EF (lower EF means higher priority)
        from misc import MiscFunctions
        sorted_cards = MiscFunctions.merge_sort_cards(cards)
        for card in sorted_cards:
            card_container = CardContainer(self.cards_frame,
                                           card_id=card[0],
                                           question=card[1],
                                           answer=card[2],
                                           edit_callback=self.edit_card,
                                           delete_callback=self.delete_card,
                                           ef=card[3],
                                           user_id=self.user_id,
                                           selection_callback=self.toggle_card_selection)
            card_container.pack(fill="x", pady=10)

    def add_card(self):
        dialog = AddCardDialog(self, deck_id=self.deck_id)
        dialog.grab_set()

    def edit_card(self, card_id):
        try:
            card_info = self.db.get_card(card_id)
            edit_dialog = EditCardDialog(self, card_id, card_info['question'], card_info['answer'])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit card: {str(e)}")

    def delete_card(self, card_id):
        if messagebox.askyesno("Delete Card", "Are you sure you want to delete this card?"):
            self.db.delete_card(card_id)
            self.display_cards()

    def toggle_card_selection(self, card_id, selected):
        if selected:
            self.selected_cards.add(card_id)
        else:
            self.selected_cards.discard(card_id)
        self.delete_cards_button.configure(state="normal" if self.selected_cards else "disabled")

    def delete_selected_cards(self):
        if not self.selected_cards:
            return
        if messagebox.askyesno("Delete Cards", f"Are you sure you want to delete {len(self.selected_cards)} card(s)?"):
            for card_id in self.selected_cards:
                self.db.delete_card(card_id)
            self.selected_cards.clear()
            self.display_cards()
            self.delete_cards_button.configure(state="disabled")

class EditCardDialog(Dialog):
    def __init__(self, parent, card_id, current_question, current_answer):
        # Set dialog size for editing a card
        super().__init__(title="Edit Card", width=500, height=500)
        self.parent = parent
        self.card_id = card_id

        # Create UI sections using the base container
        # (You can add multimedia sections here as needed)
        self.create_title("Edit Card")

        ctk.CTkLabel(
            self.container,
            text="Question",
            font=("Inter", 14, "bold"),
            text_color="black"
        ).pack(fill="x", pady=(10, 5))
        self.question_entry = ctk.CTkTextbox(
            self.container,
            height=100,
            border_width=1,
            border_color="#E5E7EB",
            text_color="black",
            fg_color="white"
        )
        self.question_entry.pack(fill="x", pady=(0, 10), padx=10)
        self.question_entry.insert("1.0", current_question)

        ctk.CTkLabel(
            self.container,
            text="Answer",
            font=("Inter", 14, "bold"),
            text_color="black"
        ).pack(fill="x", pady=(10, 5))
        self.answer_entry = ctk.CTkTextbox(
            self.container,
            height=100,
            border_width=1,
            border_color="#E5E7EB",
            text_color="black",
            fg_color="white"
        )
        self.answer_entry.pack(fill="x", pady=(0, 10), padx=10)
        self.answer_entry.insert("1.0", current_answer)

        # (Optionally, add multimedia upload/preview sections here)

        self.create_button("Save Changes", self.save_card)

        self.wait_window()

    def save_card(self):
        new_question = self.question_entry.get("1.0", "end-1c").strip()
        new_answer = self.answer_entry.get("1.0", "end-1c").strip()
        if not new_question or not new_answer:
            messagebox.showwarning("Warning", "Please fill in both question and answer")
            return
        try:
            db = Database()
            db.update_card(self.card_id, new_question, new_answer)
            if hasattr(self.parent, 'display_cards'):
                self.parent.display_cards()
            self.cancel_event()  # releases grab and closes
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update card: {str(e)}")

class EditDeckDialog(Dialog):
    def __init__(self, parent, deck_id, current_deck_name):
        # Set dialog size for editing a deck name
        super().__init__(title="Edit Deck", width=400, height=300)
        self.parent = parent
        self.deck_id = deck_id

        # Create title label
        self.create_title("Edit Deck")

        # Label for deck name
        ctk.CTkLabel(
            self.container,
            text="Deck Name",
            font=("Inter", 14, "bold"),
            text_color="black"
        ).pack(fill="x", pady=(10, 5))

        # Input field pre-populated with the current deck name
        self.deck_entry = ctk.CTkEntry(
            self.container,
            placeholder_text="Enter deck name",
            width=300,
            height=45,
            corner_radius=16,
            border_color="#E5E7EB",
            fg_color="white",
            text_color="black",
            placeholder_text_color="#6B7280"
        )
        self.deck_entry.pack(pady=(0, 10), padx=10)
        self.deck_entry.insert(0, current_deck_name)

        # Save changes button
        self.create_button("Save Changes", self.save_deck)

        # Wait until the dialog is closed
        self.wait_window()

    def save_deck(self):
        new_deck_name = self.deck_entry.get().strip()
        if not new_deck_name:
            messagebox.showwarning("Warning", "Please enter a deck name")
            return
        try:
            db = Database()
            db.update_deck_name(self.deck_id, new_deck_name)
            if hasattr(self.parent, 'display_decks'):
                self.parent.display_decks()
            self.cancel_event()  # Close the dialog
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update deck: {str(e)}")

class AddCardDialog(Dialog):
    def __init__(self, parent, deck_id):
        super().__init__(title="New Card", width=500, height=500)
        self.deck_id = deck_id
        self.parent = parent
        self.create_title("New Card")

        # Create question section
        ctk.CTkLabel(
            self.container,
            text="Question",
            font=("Inter", 14, "bold"),
            text_color="black"
        ).pack(pady=(10, 5))
        self.question_entry = ctk.CTkTextbox(
            self.container,
            height=100,
            border_width=1,
            border_color="#E5E7EB",
            text_color="black",
            fg_color = "white"

        )
        self.question_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Create answer section
        ctk.CTkLabel(
            self.container,
            text="Answer",
            font=("Inter", 14, "bold"),
            text_color="black"
        ).pack(pady=(10, 5))
        self.answer_entry = ctk.CTkTextbox(
            self.container,
            height=100,
            border_width=1,
            border_color="#E5E7EB",
            text_color="black",
            fg_color = "white"
        )
        self.answer_entry.pack(fill="x", padx=10, pady=(0, 10))

        # (Optionally add multimedia fields here)

        self.create_button("Save Card", self.save_card)
        self.wait_window()

    def save_card(self):
        question = self.question_entry.get("1.0", "end-1c").strip()
        answer = self.answer_entry.get("1.0", "end-1c").strip()
        if not question or not answer:
            messagebox.showwarning("Warning", "Please fill in both question and answer")
            return
        db = Database()
        db.create_card(self.deck_id, question, answer)
        if hasattr(self.parent, 'display_cards'):
            self.parent.display_cards()
        self.cancel_event()

class AddDeckDialog(Dialog):
    def __init__(self, parent):
        super().__init__(title="New Deck", width=400, height=300)
        self.create_title("New Deck")
        ctk.CTkLabel(
            self.container,
            text="Enter deck name",
            font=("Inter", 14, "bold"),
            text_color="black"
        ).pack(pady=(10, 5))
        self.deck_entry = self.create_input_field("")
        self.create_button("Add Deck", self.save_deck)
        self.wait_window()

    def save_deck(self):
        new_deck = self.deck_entry.get().strip()
        if not new_deck:
            messagebox.showwarning("Warning", "Please enter a deck name")
            return
        self.result = new_deck
        self.cancel_event()

    def get_deck_name(self):
        return self.result

class QuizPage(BasePage):
    def __init__(self, master, user_id, switch_page):
        super().__init__(master, user_id, switch_page)
        self.selected_deck = None  # Only one deck can be selected
        self.deck_containers = {}  # To store references to deck containers

        # Header for quiz page (deck selection)
        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 0))
        ctk.CTkLabel(header_frame, text="Quiz", font=("Inter", 24, "bold"), text_color="black").pack(side="left")

        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.pack(side="right")

        self.deck_search_var = ctk.StringVar()
        self.deck_search_entry = ctk.CTkEntry(
            controls_frame,
            textvariable=self.deck_search_var,
            placeholder_text="Search deck",
            placeholder_text_color="#D1D1D1",
            text_color="#000000",
            fg_color="white",
            border_color="#e5e7eb",
            width=150
        )
        self.deck_search_entry.pack(side="left", padx=(0, 20))

        self.deck_priority_filter_var = ctk.StringVar(value="All")
        self.deck_priority_filter_menu = ctk.CTkOptionMenu(
            controls_frame,
            values=["All", "High", "Medium", "Low"],
            variable=self.deck_priority_filter_var,
            width=120,
            fg_color="white",
            button_color="#F3F4F6",
            button_hover_color="#E5E7EB",
            text_color="#111827"
        )
        self.deck_priority_filter_menu.pack(side="left", padx=(0, 20))

        self.deck_search_var.trace_add("write", lambda *args: self.display_decks())
        self.deck_priority_filter_var.trace_add("write", lambda *args: self.display_decks())

        self.start_button = ctk.CTkButton(
            controls_frame,
            text="Start Quiz",
            width=120,
            height=32,
            corner_radius=16,
            fg_color="#F3F4F6",
            text_color="black",
            hover_color="#E5E7EB",
            state="disabled",
            command=self.start_quiz
        )
        self.start_button.pack(side="left", padx=(0, 10))

        separator = ctk.CTkFrame(self.main_content, height=1, fg_color="#E5E7EB")
        separator.pack(fill="x", padx=30, pady=(20, 0))

        self.selection_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.selection_frame.pack(fill="both", expand=True, padx=30, pady=20)

        ctk.CTkLabel(
            self.selection_frame,
            text="Select a deck to quiz yourself on",
            font=("Inter", 16, "bold"),
            text_color="black"
        ).pack(anchor="w", pady=(0, 10))

        self.decks_frame = ctk.CTkScrollableFrame(
            self.selection_frame,
            fg_color="transparent",
            scrollbar_button_color="#E5E7EB",
            scrollbar_button_hover_color="#D1D5DB"
        )
        self.decks_frame.pack(fill="both", expand=True)
        self.decks_frame.grid_columnconfigure((0, 1), weight=1, pad=20)

        self.display_decks()

    def display_decks(self):
        # Clear existing decks and container references
        for widget in self.decks_frame.winfo_children():
            widget.destroy()
        self.deck_containers = {}

        # Configure 3 columns to have the same weight & uniform width
        for i in range(3):
            self.decks_frame.grid_columnconfigure(i, weight=1, uniform="deck_col")

        db = self.db
        decks = db.get_decks(self.user_id)
        deck_list = []

        # Build deck_list with average EF, card count, etc.
        for deck_id, deck_name in decks:
            cards = db.get_cards(deck_id)
            if cards:
                total_ef = sum(db.get_card_easiness(self.user_id, c[0]) for c in cards)
                avg_ef = total_ef / len(cards)
            else:
                avg_ef = 2.5
            card_count = db.get_card_count(deck_id)
            deck_list.append((deck_id, deck_name, avg_ef, card_count))

        # Apply search filter
        search_query = self.deck_search_var.get().lower().strip()
        if search_query:
            deck_list = [d for d in deck_list if search_query in d[1].lower()]

        # Apply priority filter
        priority_filter = self.deck_priority_filter_var.get().lower()
        if priority_filter != "all":
            if priority_filter == "high":
                deck_list = [d for d in deck_list if d[2] < 2.0]
            elif priority_filter == "medium":
                deck_list = [d for d in deck_list if 2.0 <= d[2] < 2.5]
            elif priority_filter == "low":
                deck_list = [d for d in deck_list if d[2] >= 2.5]

        if not deck_list:
            no_decks_frame = ctk.CTkFrame(self.decks_frame, fg_color="transparent")
            no_decks_frame.pack(fill="both", expand=True)
            ctk.CTkLabel(
                no_decks_frame,
                text="No decks found",
                font=("Inter", 16, "bold"),
                text_color="#4B5563"
            ).pack(expand=True, pady=50)
            return

        # Build a BST based on avg_ef
        from graph import DeckNode, insert_node, in_order_traversal
        root = None
        for d in deck_list:
            node = DeckNode(deck_id=d[0], deck_name=d[1], avg_ef=d[2], card_count=d[3])
            root = insert_node(root, node)

        # Sort the decks by in-order traversal
        sorted_nodes = in_order_traversal(root)

        # Place deck containers in a 3-column grid
        row, col = 0, 0
        for node in sorted_nodes:
            deck_container = DeckContainer(
                self.decks_frame,
                deck_id=node.deck_id,
                deck_name=node.deck_name,
                card_count=node.card_count,
                selection_callback=self.toggle_deck_selection,
                avg_ef=node.avg_ef,
                edit_callback=None,  # Added callback for editing deck
                delete_callback=None  # Added callback for deleting deck
            )
            deck_container.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            self.deck_containers[node.deck_id] = deck_container

            col += 1
            if col == 3:
                col = 0
                row += 1

        # Enable/disable start button based on whether a deck is selected
        self.start_button.configure(state="normal" if self.selected_deck is not None else "disabled")



    def toggle_deck_selection(self, deck_id, selected):
        # When a deck is selected, deselect any previously selected deck
        if selected:
            if self.selected_deck is not None and self.selected_deck != deck_id:
                # Deselect the previously selected deck container
                prev_container = self.deck_containers.get(self.selected_deck)
                if prev_container:
                    prev_container.selected = False
                    prev_container.checkbox.deselect()
                    prev_container.configure(fg_color="white")
            self.selected_deck = deck_id
        else:
            if self.selected_deck == deck_id:
                self.selected_deck = None

        # Enable/disable start button based on whether a deck is selected
        self.start_button.configure(state="normal" if self.selected_deck is not None else "disabled")

    def start_quiz(self):
        if self.selected_deck is None:
            messagebox.showwarning("Warning", "Please select a deck")
            return
        for widget in self.master.winfo_children():
            widget.destroy()
        # Start quiz session with the selected deck
        QuizSession(self.master, self.user_id, self.selected_deck, self.switch_page)

class QuizSession(ctk.CTkFrame):
    def __init__(self, master, user_id, deck_id, switch_page):
        super().__init__(master, corner_radius=0, fg_color="white")
        self.pack(fill="both", expand=True)
        self.user_id = user_id
        self.deck_id = deck_id
        self.switch_page = switch_page
        self.db = Database()

        # Retrieve due cards for this deck (tuple: card_id, question, answer, next_review_date)
        self.cards = self.db.get_due_cards(self.user_id, self.deck_id, testing=False)
        if not self.cards:
            self.show_no_cards_message()
            return

        self.total_cards = len(self.cards)
        self.correct_count = 0
        self.session_start_time = datetime.now()
        self.current_index = 0

        # Header with title, progress, and timer.
        self.header = ctk.CTkFrame(self, fg_color="#F3F4F6", height=60)
        self.header.pack(fill="x", pady=(0, 20))
        self.title_label = ctk.CTkLabel(self.header, text="Quiz Session", font=("Inter", 18, "bold"), text_color="black")
        self.title_label.pack(side="left", padx=30)
        self.progress_label = ctk.CTkLabel(self.header, text=f"Card 1/{self.total_cards}", font=("Inter", 14), text_color="#4B5563")
        self.progress_label.pack(side="right", padx=30)
        self.timer_label = ctk.CTkLabel(self.header, text="Time Elapsed: 00:00:00", font=("Inter", 14), text_color="#4B5563")
        self.timer_label.pack(side="right", padx=30)

        # Main content for question/answer
        self.content = ctk.CTkFrame(self, fg_color="white")
        self.content.pack(fill="both", expand=True, padx=30, pady=20)
        self.question_label = ctk.CTkLabel(self.content, text="", font=("Inter", 16), text_color="black", wraplength=600)
        self.question_label.pack(pady=20)

        # Answer area (hidden until "Show Answer")
        self.answer_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.answer_label = ctk.CTkLabel(self.answer_frame, text="", font=("Inter", 16), text_color="black", wraplength=600)
        self.answer_label.pack(pady=20)

        self.show_answer_btn = ctk.CTkButton(
            self.content, text="Show Answer", width=120, height=32, corner_radius=16,
            fg_color="#F3F4F6", text_color="black", hover_color="#E5E7EB", command=self.show_answer
        )
        self.show_answer_btn.pack(pady=20)

        # Difficulty Rating Options (new labels with new mapping)
        # Quality 0: Very Hard (2 mins)
        # Quality 1: Hard (6 mins)
        # Quality 2: Medium (10 mins)
        # Quality 3: Easy (1 day)
        # Quality 4: Very Easy (3 days)
        self.rating_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        rating_options = [
            ("Very Hard (2 mins)", 0),
            ("Hard (6 mins)", 1),
            ("Medium (10 mins)", 2),
            ("Easy (1 day)", 3),
            ("Very Easy (3 days)", 4)
        ]
        for text, quality in rating_options:
            btn = ctk.CTkButton(
                self.rating_frame, text=text, width=120, height=32, corner_radius=16,
                fg_color="#F3F4F6", text_color="black", hover_color="#E5E7EB",
                command=lambda q=quality: self.rate_card_difficulty(q)
            )
            btn.pack(side="left", padx=5)
        self.rating_frame.pack_forget()  # Hide until answer is revealed

        self.update_timer()
        self.display_card()

    def update_timer(self):
        if not self.timer_label.winfo_exists():
            return
        elapsed = datetime.now() - self.session_start_time
        total_seconds = int(elapsed.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        self.timer_label.configure(text=f"Time Elapsed: {hours:02d}:{minutes:02d}:{seconds:02d}")
        self.after(1000, self.update_timer)

    def display_card(self):
        if self.current_index >= self.total_cards:
            self.end_quiz()
            return

        # Hide answer and rating; show "Show Answer" button.
        self.answer_frame.pack_forget()
        self.rating_frame.pack_forget()
        self.show_answer_btn.pack(pady=20)

        card = self.cards[self.current_index]
        # card structure: (card_id, question, answer, next_review_date)
        self.current_card_id = card[0]
        self.question_label.configure(text=card[1])
        self.answer_label.configure(text=card[2])
        self.progress_label.configure(text=f"Card {self.current_index + 1}/{self.total_cards}")
        self.card_start_time = datetime.now()

    def show_answer(self):
        self.show_answer_btn.pack_forget()
        self.answer_frame.pack(pady=20)
        self.rating_frame.pack(pady=20)

    def rate_card_difficulty(self, quality):
        # Calculate time taken for current card.
        card_time = (datetime.now() - self.card_start_time).total_seconds()
        # Treat quality >= 2 (Medium, Easy, Very Easy) as correct.
        is_correct = 1 if quality >= 2 else 0
        if is_correct:
            self.correct_count += 1

        # Update spaced repetition with new difficulty mapping.
        self.db.update_spaced_repetition(
            user_id=self.user_id,
            card_id=self.current_card_id,
            quality=quality,
            time_taken=card_time,
            is_correct=is_correct
        )

        self.current_index += 1
        self.display_card()

    def end_quiz(self):
        deck_time = (datetime.now() - self.session_start_time).total_seconds()
        self.total_time = deck_time
        avg_time = deck_time / self.total_cards if self.total_cards > 0 else 0
        self.db.save_quiz_result(
            user_id=self.user_id,
            deck_id=self.deck_id,
            total_cards=self.total_cards,
            correct_count=self.correct_count,
            avg_time=avg_time,
            deck_time=deck_time
        )
        self.show_summary()

    def show_summary(self):
        for widget in self.winfo_children():
            widget.destroy()
        summary_frame = ctk.CTkFrame(self, fg_color="#F3F4F6")
        summary_frame.pack(fill="both", expand=True, padx=30, pady=30)
        ctk.CTkLabel(summary_frame, text="Quiz Complete!", font=("Inter", 24, "bold"), text_color="black").pack(pady=20)
        total_cards = self.total_cards
        wrong = total_cards - self.correct_count
        accuracy = (self.correct_count / total_cards) * 100 if total_cards > 0 else 0
        stats = [
            ("Total Cards", f"{total_cards}"),
            ("Correct Answers", f"{self.correct_count}"),
            ("Wrong Answers", f"{wrong}"),
            ("Accuracy", f"{accuracy:.1f}%"),
            ("Total Time", f"{self.total_time:.1f}s"),
            ("Avg Time/Card", f"{(self.total_time / total_cards):.1f}s" if total_cards else "0s")
        ]
        for label, value in stats:
            stat_frame = ctk.CTkFrame(summary_frame, fg_color="transparent")
            stat_frame.pack(pady=10)
            ctk.CTkLabel(stat_frame, text=label, font=("Inter", 14), text_color="#4B5563").pack(side="left", padx=5)
            ctk.CTkLabel(stat_frame, text=value, font=("Inter", 14, "bold"), text_color="black").pack(side="left", padx=5)
        ctk.CTkButton(
            summary_frame, text="Return to Quiz", width=200, height=40, corner_radius=16,
            fg_color="#F3F4F6", text_color="black", hover_color="#E5E7EB",
            command=lambda: self.switch_page(__import__('app').QuizPage, user_id=self.user_id, switch_page=self.switch_page)
        ).pack(pady=20)

    def show_no_cards_message(self):
        for widget in self.winfo_children():
            widget.destroy()
        msg_frame = ctk.CTkFrame(self, fg_color="white")
        msg_frame.pack(fill="both", expand=True, padx=30, pady=30)
        ctk.CTkLabel(msg_frame, text="No cards available for review!", font=("Inter", 18, "bold"), text_color="black").pack(expand=True)
        ctk.CTkButton(
            msg_frame, text="Return to Quiz", width=200, height=40, corner_radius=16,
            command=lambda: self.switch_page(__import__('app').QuizPage, user_id=self.user_id, switch_page=self.switch_page)
        ).pack(pady=20)

matplotlib.use("Agg")  # For use with Tkinter

# analytics_page.py
import customtkinter as ctk
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates  # not used now since we use numeric x-axis
import mplcursors
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from components import BasePage
from database import Database

class AnalyticsPage(BasePage):
    def __init__(self, master, user_id, switch_page):
        super().__init__(master, user_id, switch_page)
        self.db = Database()
        self.user_id = user_id

        # Retrieve overall session-level stats (must include total_correct & total_reviewed)
        self.stats = self.db.get_quiz_stats(self.user_id)
        self.deck_expanded = {}

        # Header
        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 0))
        ctk.CTkLabel(header_frame, text="Analytics", font=("Inter", 24, "bold"), text_color="black").pack(side="left")
        separator = ctk.CTkFrame(self.main_content, height=1, fg_color="#E5E7EB")
        separator.pack(fill="x", padx=30, pady=(10, 0))

        # Scrollable container for all analytics content
        self.content_scroll = ctk.CTkScrollableFrame(
            self.main_content,
            fg_color="transparent",
            border_width=0,
            scrollbar_button_color="#E5E7EB",
            scrollbar_button_hover_color="#D1D5DB"
        )
        self.content_scroll.pack(fill="both", expand=True, padx=30, pady=20)

        self.create_overall_stats_section()
        self.create_deck_performance_section()
        self.create_graph_controls()
        self.create_return_button()

    ##########################################################
    # 1) Overall Stats Section (3 rows x 2 columns)
    ##########################################################
    def create_overall_stats_section(self):
        container = ctk.CTkFrame(
            self.content_scroll,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color="#E5E7EB"
        )
        container.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(container, text="Overall Statistics", font=("Inter", 18, "bold"), text_color="#111827").pack(anchor="w", padx=20, pady=(15, 10))
        parent_frame = ctk.CTkFrame(container, fg_color="white")
        parent_frame.pack(fill="x", padx=20, pady=(0, 15))

        total_sessions = self.stats.get("total_sessions", 0)
        total_reviewed = self.stats.get("total_reviewed", 0)
        total_correct = self.stats.get("total_correct", 0)
        overall_accuracy = self.stats.get("overall_accuracy", 0.0)
        total_time = self.stats.get("total_time", 0.0)
        avg_time = self.stats.get("overall_avg_time_per_card", 0.0)

        layout = [
            ("Total Sessions", str(total_sessions), "📊"),
            ("Total Cards Reviewed", str(total_reviewed), "📄"),
            ("Total Correct Answers", str(total_correct), "✅"),
            ("Overall Accuracy", f"{overall_accuracy:.1f}%", "🎯"),
            ("Total Quiz Time", f"{total_time:.1f}s", "⏱️"),
            ("Avg Time/Card", f"{avg_time:.1f}s", "⚡"),
        ]
        row_count = 3
        col_count = 2
        idx = 0
        for r in range(row_count):
            row_frame = ctk.CTkFrame(parent_frame, fg_color="white")
            row_frame.pack(fill="x", pady=5)
            row_frame.grid_columnconfigure(0, weight=1, uniform="stats_col")
            row_frame.grid_columnconfigure(1, weight=1, uniform="stats_col")
            for c in range(col_count):
                if idx < len(layout):
                    label_text, val, icon = layout[idx]
                    self.create_stat_card(row_frame, label_text, val, icon, c)
                    idx += 1

    def create_stat_card(self, parent, label_text, value_text, icon, col_index):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=8, border_width=1, border_color="#E5E7EB")
        card.grid(row=0, column=col_index, padx=5, sticky="nsew")
        inner = ctk.CTkFrame(card, fg_color="white")
        inner.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(inner, text=icon, font=("Inter", 18), text_color="#4B5563").pack(anchor="w")
        ctk.CTkLabel(inner, text=label_text, font=("Inter", 12), text_color="#4B5563").pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(inner, text=value_text, font=("Inter", 20, "bold"), text_color="#111827").pack(anchor="w", pady=(5, 0))

    ##########################################################
    # 2) Deck Performance Section
    ##########################################################
    def create_deck_performance_section(self):
        container = ctk.CTkFrame(self.content_scroll, fg_color="white", corner_radius=8, border_width=1, border_color="#E5E7EB")
        container.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(container, text="Deck Performance", font=("Inter", 18, "bold"), text_color="#111827").pack(anchor="w", padx=20, pady=(15, 10))
        decks = self.db.get_decks(self.user_id)
        for deck_id, deck_name in decks:
            d_stats = self.db.get_deck_stats(self.user_id, deck_id)
            perf = self.db.get_deck_performance_score(self.user_id, deck_id)
            deck_card = ctk.CTkFrame(container, fg_color="white", corner_radius=8, border_width=1, border_color="#E5E7EB")
            deck_card.pack(fill="x", padx=20, pady=5)
            row = ctk.CTkFrame(deck_card, fg_color="white")
            row.pack(fill="x", padx=15, pady=10)
            ctk.CTkLabel(row, text=deck_name, font=("Inter", 14, "bold"), text_color="#111827").pack(side="left")
            score_color = "#10B981"
            if perf < 50:
                score_color = "#DC2626"
            elif perf < 75:
                score_color = "#F59E0B"
            ctk.CTkLabel(row, text=f"{perf:.1f}/100", font=("Inter", 14, "bold"), text_color=score_color).pack(side="right", padx=(10, 0))
            view_btn = ctk.CTkButton(row, text="View Details", width=100, height=32, corner_radius=16,
                                      fg_color="#F3F4F6", text_color="black", hover_color="#E5E7EB",
                                      command=lambda d_id=deck_id: self.toggle_deck_details(d_id))
            view_btn.pack(side="right", padx=(10, 0))
            details_frame = ctk.CTkFrame(deck_card, fg_color="white", corner_radius=8, border_width=1, border_color="#E5E7EB")
            details_frame.pack_forget()
            self.deck_expanded[deck_id] = details_frame

    def toggle_deck_details(self, deck_id):
        details_frame = self.deck_expanded.get(deck_id)
        if not details_frame:
            return
        if details_frame.winfo_ismapped():
            details_frame.pack_forget()
        else:
            for w in details_frame.winfo_children():
                w.destroy()
            d_stats = self.db.get_deck_stats(self.user_id, deck_id)
            layout = [
                ("Sessions", f"{d_stats.get('session_count', 0)}", "📊"),
                ("Total Cards Reviewed", f"{d_stats.get('total_reviewed', 0)}", "📄"),
                ("Correct Answers", f"{d_stats.get('total_correct', 0)}", "✅"),
                ("Accuracy", f"{d_stats.get('accuracy', 0):.1f}%", "🎯"),
                ("Total Time (This Deck)", f"{d_stats.get('total_time', 0):.1f}s", "⏱️"),
                ("Avg Time/Card", f"{d_stats.get('avg_time_per_card', 0):.1f}s", "⚡"),
            ]
            parent = ctk.CTkFrame(details_frame, fg_color="white")
            parent.pack(fill="x", expand=True, padx=15, pady=15)
            row_count = 3
            col_count = 2
            idx = 0
            for r in range(row_count):
                rowf = ctk.CTkFrame(parent, fg_color="white")
                rowf.pack(fill="x", pady=5)
                rowf.grid_columnconfigure(0, weight=1, uniform="deck_col")
                rowf.grid_columnconfigure(1, weight=1, uniform="deck_col")
                for c in range(col_count):
                    if idx < len(layout):
                        lbl, val, ic = layout[idx]
                        self.create_stat_card(rowf, lbl, val, ic, c)
                        idx += 1
            details_frame.pack(fill="x", pady=(5, 10))

    ##########################################################
    # 3) Graph Controls (with Interval and Slider)
    ##########################################################
    def create_graph_controls(self):
        graph_box = ctk.CTkFrame(self.content_scroll, fg_color="white", corner_radius=8, border_width=1, border_color="#E5E7EB")
        graph_box.pack(fill="both", expand=True, pady=(0, 20))
        ctk.CTkLabel(graph_box, text="Performance Graphs", font=("Inter", 18, "bold"), text_color="#111827").pack(anchor="w", padx=20, pady=(15, 5))
        controls = ctk.CTkFrame(graph_box, fg_color="white")
        controls.pack(fill="x", padx=20, pady=(0, 5))

        # Deck menu
        decks = self.db.get_decks(self.user_id)
        self.deck_options = {}
        deck_names = []
        for d_id, d_name in decks:
            self.deck_options[d_name] = d_id
            deck_names.append(d_name)
        self.selected_deck_name = ctk.StringVar(value=deck_names[0] if deck_names else "")
        self.deck_menu = ctk.CTkOptionMenu(controls, values=deck_names, variable=self.selected_deck_name,
                                            width=140, corner_radius=8, fg_color="white", button_color="#F3F4F6",
                                            button_hover_color="#E5E7EB", text_color="#111827")
        self.deck_menu.pack(side="left", padx=(0, 20))

        # Metric menu
        self.selected_graph = ctk.StringVar(value="Accuracy Over Time")
        self.graph_menu = ctk.CTkOptionMenu(controls, values=["Accuracy Over Time", "Avg Time Per Card", "Cumulative Retention"],
                                           variable=self.selected_graph, width=160, corner_radius=8,
                                           fg_color="white", button_color="#F3F4F6", button_hover_color="#E5E7EB",
                                           text_color="#111827")
        self.graph_menu.pack(side="left", padx=(0, 20))

        # Interval type
        self.selected_interval = ctk.StringVar(value="Daily")
        self.interval_menu = ctk.CTkOptionMenu(controls, values=["Daily", "Hourly", "Session"],
                                               variable=self.selected_interval, width=90, corner_radius=8,
                                               fg_color="white", button_color="#F3F4F6", button_hover_color="#E5E7EB",
                                               text_color="#111827", command=self.on_interval_change)
        self.interval_menu.pack(side="left", padx=(0, 20))

        # Group step slider – this controls how many days or hours per group.
        self.group_step_var = ctk.IntVar(value=1)
        self.group_step_slider = ctk.CTkSlider(controls, from_=1, to=10, variable=self.group_step_var,
                                               width=100, number_of_steps=10, command=self.on_group_step_change,
                                               fg_color="#F9FAFB", progress_color="#9CA3AF",
                                               button_color="#E5E7EB", button_hover_color="#D1D5DB")
        self.group_step_slider.pack(side="left", padx=(10, 5))
        self.group_step_label = ctk.CTkLabel(controls, text="Group Step: ", font=("Inter", 12), text_color="black")
        self.group_step_label.pack(side="left", padx=(0, 20))

        show_btn = ctk.CTkButton(controls, text="Show Graph", width=100, height=32, corner_radius=30,
                                 font=("Inter", 14), fg_color="#F3F4F6", text_color="black",
                                 hover_color="#E5E7EB", command=self.show_graph)
        show_btn.pack(side="left")

        self.graph_display_frame = ctk.CTkFrame(graph_box, fg_color="white", corner_radius=8)
        self.graph_display_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

    def on_interval_change(self, choice):
        if choice == "Session":
            self.group_step_slider.configure(state="disabled")
            self.group_step_label.configure(text="Grouping by session")
        else:
            self.group_step_slider.configure(state="normal")
            val = self.group_step_var.get()
            if choice == "Daily":
                self.group_step_label.configure(text=f"Group Step: {val} day(s)")
            else:
                self.group_step_label.configure(text=f"Group Step: {val} hour(s)")

    def on_group_step_change(self, value):
        v = int(value)
        interval = self.selected_interval.get()
        if interval == "Daily":
            self.group_step_label.configure(text=f"Group Step: {v} day(s)")
        elif interval == "Hourly":
            self.group_step_label.configure(text=f"Group Step: {v} hour(s)")
        else:
            self.group_step_label.configure(text="Grouping by session")

    def show_graph(self):
        # Clear old widgets in graph_display_frame
        for w in self.graph_display_frame.winfo_children():
            w.destroy()

        # 1. Get user selections
        deck_name = self.selected_deck_name.get()
        if deck_name not in self.deck_options:
            self.show_no_data_message()
            return
        deck_id = self.deck_options[deck_name]

        graph_type = self.selected_graph.get()
        interval_type = self.selected_interval.get()
        group_step = self.group_step_var.get()
        group_by_map = {"Daily": "day", "Hourly": "hour", "Session": "session"}
        group_by = group_by_map.get(interval_type, "day")

        # 2. Fetch data from your DB
        if graph_type == "Accuracy Over Time":
            labels, values = self.db.get_deck_accuracy_over_time(
                self.user_id, deck_id, group_by=group_by, group_step=group_step
            )
            ylabel = "Accuracy (%)"
        elif graph_type == "Avg Time Per Card":
            labels, values = self.db.get_deck_avg_time_over_time(
                self.user_id, deck_id, group_by=group_by, group_step=group_step
            )
            ylabel = "Avg Time (s)"
        else:
            labels, values = self.db.get_deck_cumulative_retention(
                self.user_id, deck_id, group_by=group_by, group_step=group_step
            )
            ylabel = "Cumulative Retention (%)"

        title = f"{deck_name} - {interval_type}"
        if not labels:
            self.show_no_data_message()
            return

        # 3. Convert labels -> numeric x_vals
        x_vals = list(range(len(labels)))
        n_points = len(x_vals)

        # 4. Dynamically expand the figure width based on number of points
        width = 8
        if n_points > 10:
            extra = n_points - 10
            width += extra * 0.3  # 0.3 inches per extra point
            # cap the maximum width if you want
            if width > 30:
                width = 30
        height = 5

        # 5. Create the figure
        plt.close("all")
        matplotlib.use("Agg")
        plt.style.use("seaborn-v0_8-whitegrid")

        fig, ax = plt.subplots(figsize=(width, height))
        color = "#636ae8"

        # Plot the line and scatter
        ax.plot(x_vals, values, color=color, linewidth=2, zorder=2)
        points = ax.scatter(x_vals, values, color=color, s=40, zorder=3, picker=True)

        ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
        ax.set_xlabel("Interval", fontsize=12, labelpad=10)
        ax.set_ylabel(ylabel, fontsize=12, labelpad=10)
        ax.grid(True, linestyle="--", alpha=0.7)

        # 6. Manage too many labels:
        # If we have more than e.g. 20 points, skip some labels so they don't overlap too much.
        skip_threshold = 20
        if n_points > skip_threshold:
            # We'll keep ~ 1 label for every  (n_points // 10) positions
            skip = max(1, n_points // 10)
            new_labels = []
            for i, lab in enumerate(labels):
                if i % skip == 0:
                    new_labels.append(lab)
                else:
                    new_labels.append("")  # blank
            labels = new_labels

        ax.set_xticks(x_vals)
        ax.set_xticklabels(labels, rotation=45, ha="right")

        # 7. Adjust y-limits if needed
        if graph_type in ["Accuracy Over Time", "Cumulative Retention"]:
            ax.set_ylim([0, 100])
        else:
            if values:
                mn = min(values)
                mx = max(values)
                if mn == mx:
                    mn = 0
                ax.set_ylim([mn * 0.8, mx * 1.2])

        fig.patch.set_facecolor("#F9FAFB")
        ax.set_facecolor("#FFFFFF")
        fig.tight_layout(pad=3.0)

        # 8. Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.graph_display_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # 9. Mplcursors for hover
        cursor = mplcursors.cursor(points, hover=True)

        @cursor.connect("add")
        def on_add(sel):
            x_val, y_val = sel.target
            # x_val is the index
            idx = int(round(x_val))
            lbl = labels[idx] if 0 <= idx < len(labels) else str(x_val)
            val_suffix = "%" if graph_type in ["Accuracy Over Time", "Cumulative Retention"] else "s"
            sel.annotation.set_bbox(dict(facecolor="#f3f4f6", edgecolor="none", alpha=0.9, boxstyle="round,pad=0.3"))
            sel.annotation.set_text(f"{lbl}\n{y_val:.1f}{val_suffix}")

        # 10. Explanation
        self.add_graph_explanation(graph_type)

    def add_graph_explanation(self, graph_type):
        frame = ctk.CTkFrame(self.graph_display_frame, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=(5,10))
        if graph_type == "Accuracy Over Time":
            explanation = (
                "Accuracy Over Time shows the ratio of correct answers to total reviewed cards for each interval, "
                "expressed as a percentage. Each interval represents a group (e.g. each day or each hour, depending on your selection)."
            )
        elif graph_type == "Avg Time Per Card":
            explanation = (
                "Average Time Per Card indicates how many seconds, on average, you spent reviewing each card in "
                "each interval. Lower values may suggest you’re reviewing quickly, while higher values may indicate "
                "more thorough review."
            )
        else:
            explanation = (
                "Cumulative Retention is the running total of correct answers divided by the total reviewed cards up to "
                "each interval, multiplied by 100. It provides an overview of your long-term memory retention."
            )
        ctk.CTkLabel(frame, text=explanation, font=("Inter", 12), wraplength=600, justify="left", text_color="#4B5563").pack(anchor="w")

    def show_no_data_message(self):
        msg_frame = ctk.CTkFrame(self.graph_display_frame, fg_color="transparent")
        msg_frame.pack(fill="both", expand=True)
        ctk.CTkLabel(msg_frame, text="No data available for this selection", font=("Inter", 16, "bold"), text_color="#4B5563").pack(expand=True, pady=20)
        ctk.CTkLabel(msg_frame, text="Complete some quizzes with this deck to see performance data", font=("Inter", 14), text_color="#6B7280").pack(expand=True)

    ##########################################################
    # 4) Return to Dashboard
    ##########################################################
    def create_return_button(self):
        container = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        container.pack(side="bottom", fill="x", pady=(10,0))
        ctk.CTkButton(container, text="Return to Dashboard", width=200, height=40, corner_radius=16,
                       font=("Inter", 14), fg_color="#F3F4F6", text_color="black", hover_color="#E5E7EB",
                       command=lambda: self.switch_page(__import__('app').DecksPage, user_id=self.user_id, switch_page=self.switch_page)
                       ).pack(anchor="center", pady=20)

class SettingsPage(BasePage):
    def __init__(self, master, user_id, switch_page):
        # Initialize BasePage (sets up sidebar, main_content, etc.)
        super().__init__(master, user_id, switch_page)
        self.user_id = user_id
        self.switch_page = switch_page

        # Retrieve current user information from the database.
        db = Database()
        try:
            # Assumes get_user returns a dict with keys: "email", "username"
            # Note: We do not display the password.
            user_info = db.get_user(self.user_id)
            current_email = user_info.get("email", "")
            current_username = user_info.get("username", "")
        except Exception as e:
            print(f"Error fetching user info: {e}")
            current_email = ""
            current_username = ""
        finally:
            db.close()

        # Header frame in the main content area.
        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 10))
        ctk.CTkLabel(
            header_frame,
            text="Account Settings",
            font=("Inter", 24, "bold"),
            text_color="black"
        ).pack(side="left")

        # Main content area (non-scrollable).
        main_area = ctk.CTkFrame(self.main_content, fg_color="white")
        main_area.pack(fill="both", expand=True, padx=30, pady=20)

        # Central container to center the settings container within main_area.
        center_container = ctk.CTkFrame(main_area, fg_color="transparent")
        center_container.place(relx=0.5, rely=0.3, anchor="center")

        # Settings container (holds the form).
        self.settings_container = ctk.CTkFrame(
            center_container,
            fg_color="white",
            corner_radius=12,
            width=400,
            height=600
        )
        self.settings_container.pack(expand=True)
        self.settings_container.grid_propagate(False)

        # Title inside settings container.
        ctk.CTkLabel(
            self.settings_container,
            text="Update Your Account Details",
            font=("Inter", 20, "bold"),
            text_color="#000000"
        ).pack(pady=(30, 20))

        # Email Entry (pre-populated with current email).
        ctk.CTkLabel(
            self.settings_container,
            text="Email",
            font=("Inter", 14, "bold"),
            text_color="black"
        ).pack(fill="x", pady=(0, 5))
        self.email_entry = ctk.CTkEntry(
            self.settings_container,
            width=300,
            height=45,
            corner_radius=16,
            border_color="#E5E7EB",
            fg_color="white",
            text_color="black"
        )
        self.email_entry.pack(pady=(0, 10))
        self.email_entry.insert(0, current_email)

        # Username Entry (pre-populated with current username).
        ctk.CTkLabel(
            self.settings_container,
            text="Username",
            font=("Inter", 14, "bold"),
            text_color="black"
        ).pack(fill="x", pady=(0, 5))
        self.username_entry = ctk.CTkEntry(
            self.settings_container,
            width=300,
            height=45,
            corner_radius=16,
            border_color="#E5E7EB",
            fg_color="white",
            text_color="black"
        )
        self.username_entry.pack(pady=(0, 10))
        self.username_entry.insert(0, current_username)

        # Password Entry (left blank so user can enter a new password if desired).
        ctk.CTkLabel(
            self.settings_container,
            text="Password",
            font=("Inter", 14, "bold"),
            text_color="black"
        ).pack(fill="x", pady=(0, 5))
        self.password_entry = ctk.CTkEntry(
            self.settings_container,
            placeholder_text="New Password",
            width=300,
            height=45,
            corner_radius=16,
            border_color="#E5E7EB",
            fg_color="white",
            text_color="black",
            show="•"
        )
        self.password_entry.pack(pady=(0, 10))
        # Do not pre-populate the password field.

        # Update Settings button.
        ctk.CTkButton(
            self.settings_container,
            text="Update",
            width=300,
            height=45,
            corner_radius=16,
            fg_color="#F3F4F6",
            text_color="black",
            hover_color="#E5E7EB",
            command=self.update_settings
        ).pack(pady=20)

        # Delete Account button.
        ctk.CTkButton(
            self.settings_container,
            text="Delete Account",
            width=300,
            height=45,
            corner_radius=16,
            fg_color="#FEE2E2",
            text_color="#DC2626",
            hover_color="#FECACA",
            command=self.delete_account
        ).pack(pady=10)

        # Status label for feedback messages.
        self.status_label = ctk.CTkLabel(
            self.settings_container,
            text="",
            text_color="#DC2626"
        )
        self.status_label.pack(pady=10)

    def update_settings(self):
        new_email = self.email_entry.get().strip()
        new_username = self.username_entry.get().strip()
        new_password = self.password_entry.get().strip()

        # If all fields are empty, show an error.
        if not new_email and not new_username and not new_password:
            self.status_label.configure(text="Please enter at least one field to update.")
            return

        db = Database()
        try:
            # If new_password is blank, update_user should keep the current password.
            updated = db.update_user(self.user_id, new_email, new_username, new_password)
            if updated:
                self.status_label.configure(text="Settings updated successfully.", text_color="#16A34A")
            else:
                self.status_label.configure(text="Failed to update settings.", text_color="#DC2626")
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="#DC2626")
        finally:
            db.close()

    def delete_account(self):
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            "Are you sure you want to delete your account? This action cannot be undone."
        )
        if not confirm:
            return

        db = Database()
        try:
            deleted = db.delete_user(self.user_id)
            if deleted:
                messagebox.showinfo("Account Deleted", "Your account has been deleted.")
                from login import LoginPage
                self.switch_page(LoginPage)
            else:
                messagebox.showerror("Deletion Failed", "Failed to delete your account. Please try again later.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            db.close()
