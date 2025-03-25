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
        # Call BasePage to set up sidebar, main_content, etc.
        super().__init__(master, user_id, switch_page)

        self.selected_decks = set()

        # Header (like before)
        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 0))

        ctk.CTkLabel(
            header_frame,
            text="My Decks",
            font=("Inter", 24, "bold"),
            text_color="black"
        ).pack(side="left")

        # Filter frame on the right
        filter_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        filter_frame.pack(side="right", padx=10)

        self.deck_search_var = ctk.StringVar()
        self.deck_search_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.deck_search_var,
            placeholder_text="Search deck",
            placeholder_text_color="#D1D1D1",
            text_color="#000000",
            fg_color="white",
            border_color="#e5e7eb",
            width=200
        )
        self.deck_search_entry.pack(side="left", padx=5)

        self.deck_priority_filter_var = ctk.StringVar(value="All")
        self.deck_priority_filter_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=["All", "High", "Medium", "Low"],
            variable=self.deck_priority_filter_var,
            width=120,
            fg_color="white",
            button_color="#F3F4F6",
            button_hover_color="#E5E7EB",
            text_color="#111827"
        )
        self.deck_priority_filter_menu.pack(side="left", padx=5)

        # Traces for search/priority changes
        self.deck_search_var.trace_add("write", lambda *args: self.display_decks())
        self.deck_priority_filter_var.trace_add("write", lambda *args: self.display_decks())

        # Buttons container
        buttons = ctk.CTkFrame(header_frame, fg_color="transparent")
        buttons.pack(side="right")

        ctk.CTkButton(
            buttons,
            text="+ Add",
            width=70,
            height=32,
            corner_radius=16,
            fg_color="#F3F4F6",
            text_color="black",
            hover_color="#E5E7EB",
            command=self.add_deck
        ).pack(side="left", padx=5)

        self.delete_button = ctk.CTkButton(
            buttons,
            text="Delete Selected",
            width=70,
            height=32,
            corner_radius=16,
            fg_color="#FEE2E2",
            text_color="#DC2626",
            hover_color="#FECACA",
            state="disabled",
            command=self.delete_selected_decks
        )
        self.delete_button.pack(side="left", padx=5)

        separator = ctk.CTkFrame(self.main_content, height=1, fg_color="#E5E7EB")
        separator.pack(fill="x", padx=30, pady=(20, 0))

        # Scrollable frame for decks
        self.decks_frame = ctk.CTkScrollableFrame(
            self.main_content,
            fg_color="transparent",
            scrollbar_button_color="#E5E7EB",
            scrollbar_button_hover_color="#D1D5DB"
        )
        self.decks_frame.pack(fill="both", expand=True, padx=30, pady=20)
        self.decks_frame.grid_columnconfigure((0, 1, 2), weight=1, pad=10)

        self.display_decks()

    def edit_deck(self, deck_id, current_name):
        dialog = EditDeckDialog(self, deck_id, current_name)

    def display_decks(self):
        # Clear existing deck containers
        for widget in self.decks_frame.winfo_children():
            widget.destroy()

        db = Database()
        deck_list = []
        decks = db.get_decks(self.user_id)

        # Calculate EF, etc. (same as before)
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

        # Filter by priority
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

        # Build BST, traverse in-order
        from graph import DeckNode, insert_node, in_order_traversal
        root = None
        for deck in deck_list:
            node = DeckNode(deck_id=deck[0], deck_name=deck[1], avg_ef=deck[2], card_count=deck[3])
            root = insert_node(root, node)

        sorted_nodes = in_order_traversal(root)

        # Display each deck using DeckContainer
        row, col = 0, 0
        for node in sorted_nodes:
            deck_container = DeckContainer(
                self.decks_frame,
                deck_id=node.deck_id,
                deck_name=node.deck_name,
                card_count=node.card_count,
                selection_callback=self.toggle_deck_selection,
                avg_ef=node.avg_ef,
                edit_callback=self.edit_deck,  # edit callback function
                delete_callback=self.delete_deck  # delete callback function
            )

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
        # Retrieve the current deck name from the database (or from your deck list)
        db = Database()
        deck_info = db.get_deck_info(deck_id)  # expects a dict with "name" key
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

        self.delete_button.configure(
            state="normal" if self.selected_decks else "disabled"
        )

    def delete_selected_decks(self):
        if not self.selected_decks:
            return
        if messagebox.askyesno(
            "Delete Decks",
            f"Are you sure you want to delete {len(self.selected_decks)} deck(s)?"
        ):
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
        # Call BasePage to set up self.sidebar, self.main_content, self.db, etc.
        super().__init__(master, user_id, switch_page)

        self.deck_id = deck_id
        self.selected_cards = set()  # For multi-selection tracking

        # Retrieve deck info from the database
        self.deck_info = self.db.get_deck_info(self.deck_id)

        # Header area with deck name, card count, search filters, and buttons
        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=20)

        # Left side: deck name and card count
        ctk.CTkLabel(
            header_frame,
            text=self.deck_info["name"],
            font=("Inter", 24, "bold"),
            text_color="black"
        ).pack(side="left")

        ctk.CTkLabel(
            header_frame,
            text=f"{self.deck_info['card_count']} cards",
            font=("Inter", 14),
            text_color="#6B7280"
        ).pack(side="left", padx=(10, 0))

        # Right side: filter frame (search + priority)
        filter_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        filter_frame.pack(side="right", padx=10)

        self.card_search_var = ctk.StringVar()
        self.card_search_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.card_search_var,
            placeholder_text="Search card",
            placeholder_text_color="#D1D1D1",
            text_color="#000000",
            fg_color="white",
            border_color="#e5e7eb",
            width=200
        )
        self.card_search_entry.pack(side="left", padx=5)

        self.card_priority_filter_var = ctk.StringVar(value="All")
        self.card_priority_filter_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=["All", "High", "Medium", "Low"],
            variable=self.card_priority_filter_var,
            width=120,
            fg_color="white",
            button_color="#F3F4F6",
            button_hover_color="#E5E7EB",
            text_color="#111827"
        )
        self.card_priority_filter_menu.pack(side="left", padx=5)

        # Trigger display_cards() whenever search or priority changes
        self.card_search_var.trace_add("write", lambda *args: self.display_cards())
        self.card_priority_filter_var.trace_add("write", lambda *args: self.display_cards())

        # Buttons: Delete Selected + Add Card
        self.delete_cards_button = ctk.CTkButton(
            header_frame,
            text="Delete Selected",
            width=120,
            height=32,
            corner_radius=16,
            fg_color="#FEE2E2",
            text_color="#DC2626",
            hover_color="#FECACA",
            state="disabled",
            command=self.delete_selected_cards
        )
        self.delete_cards_button.pack(side="right", padx=5)

        ctk.CTkButton(
            header_frame,
            text="+ Add Card",
            width=70,
            height=32,
            corner_radius=16,
            fg_color="#F3F4F6",
            text_color="black",
            hover_color="#E5E7EB",
            command=self.add_card
        ).pack(side="right", padx=5)

        # Scrollable frame for displaying cards
        self.cards_frame = ctk.CTkScrollableFrame(
            self.main_content,
            fg_color="transparent",
            scrollbar_button_color="#E5E7EB",
            scrollbar_button_hover_color="#D1D5DB"
        )
        self.cards_frame.pack(fill="both", expand=True, padx=30, pady=20)

        # Finally, load the cards
        self.display_cards()

    def display_cards(self):
        # Clear existing card containers
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        raw_cards = self.db.get_cards(self.deck_id)  # (card_id, deck_id, question, answer)
        cards = []
        for card in raw_cards:
            card_id, _, question, answer = card
            ef = self.db.get_card_easiness(self.user_id, card_id)
            cards.append((card_id, question, answer, ef))

        # Sort cards by question
        cards.sort(key=lambda x: x[1].lower())

        # Filter by search
        search_query = self.card_search_var.get().lower().strip()
        if search_query:
            cards = [c for c in cards if search_query in c[1].lower()]

        # Filter by priority
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
            ctk.CTkLabel(
                no_cards_frame,
                text="No cards found",
                font=("Inter", 16, "bold"),
                text_color="#4B5563"
            ).pack(expand=True, pady=50)
            return

        # Create a CardContainer for each card
        for card_id, question, answer, ef in cards:
            card_container = CardContainer(
                self.cards_frame,
                card_id=card_id,
                question=question,
                answer=answer,
                edit_callback=self.edit_card,
                delete_callback=self.delete_card,
                ef=ef,
                user_id=self.user_id,
                selection_callback=self.toggle_card_selection
            )
            card_container.pack(fill="x", pady=10)

    def add_card(self):
        dialog = AddCardDialog(self, deck_id=self.deck_id)
        dialog.grab_set()

    def edit_card(self, card_id):
        try:
            card_info = self.db.get_card(card_id)  # e.g. {'question':..., 'answer':...}
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
        self.delete_cards_button.configure(
            state="normal" if self.selected_cards else "disabled"
        )

    def delete_selected_cards(self):
        if not self.selected_cards:
            return
        if messagebox.askyesno(
            "Delete Cards",
            f"Are you sure you want to delete {len(self.selected_cards)} card(s)?"
        ):
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
        QuizSession(self.master, self.user_id, self.selected_deck, [self.selected_deck], self.switch_page)

class QuizSession(ctk.CTkFrame):
    def __init__(self, master, user_id, deck_id, deck_ids, switch_page):
        super().__init__(master, corner_radius=0, fg_color="white")
        self.pack(fill="both", expand=True)

        self.user_id = user_id
        self.deck_id = deck_id
        self.deck_ids = deck_ids
        self.switch_page = switch_page

        self.current_index = 0
        self.start_time = datetime.now()
        self.card_start_time = None
        self.correct_count = 0
        self.total_time = 0

        db = Database()
        # Load due cards based on SM2 scheduling (production mode)
        self.cards = db.get_due_cards(self.user_id, self.deck_id, testing=False)
        if not self.cards:
            self.show_no_cards_message()
            return

        deck_names = []
        for d in deck_ids:
            info = db.get_deck_info(d)
            if info:
                deck_names.append(info["name"])
        self.session_title = "Quiz Session - " + ", ".join(deck_names)

        self.setup_ui()
        self.update_timer()
        self.display_card()

    def predict_interval(self, quality):
        if quality <= 2:
            mapping = {0: 2, 2: 10}
            mins = mapping.get(quality, 2)
            return f"{mins} min{'s' if mins != 1 else ''}"
        else:
            days = {3: 1, 4: 2, 5: 3}[quality]
            return f"{days} day{'s' if days != 1 else ''}"

    def setup_ui(self):
        self.header = ctk.CTkFrame(self, fg_color="#F3F4F6", height=60)
        self.header.pack(fill="x", pady=(0, 20))
        self.header.pack_propagate(False)

        self.title_label = ctk.CTkLabel(
            self.header,
            text=self.session_title,
            font=("Inter", 18, "bold"),
            text_color="black"
        )
        self.title_label.pack(side="left", padx=30)

        right_frame = ctk.CTkFrame(self.header, fg_color="#F3F4F6", width=200)
        right_frame.pack(side="right", padx=30)
        right_frame.pack_propagate(False)

        self.progress_label = ctk.CTkLabel(
            right_frame,
            text=f"Card 1/{len(self.cards)}",
            font=("Inter", 14),
            text_color="#4B5563"
        )
        self.progress_label.pack()

        self.timer_label = ctk.CTkLabel(
            right_frame,
            text="Time Elapsed: 00:00:00",
            font=("Inter", 14),
            text_color="#4B5563"
        )
        self.timer_label.pack()

        self.content = ctk.CTkFrame(self, fg_color="white")
        self.content.pack(fill="both", expand=True, padx=30, pady=20)

        self.question_label = ctk.CTkLabel(
            self.content,
            text="",
            font=("Inter", 16),
            text_color="black",
            wraplength=600
        )
        self.question_label.pack(pady=20)

        self.answer_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.answer_label = ctk.CTkLabel(
            self.answer_frame,
            text="",
            font=("Inter", 16),
            text_color="black",
            wraplength=600
        )
        self.answer_label.pack(pady=20)

        self.show_answer_btn = ctk.CTkButton(
            self.content,
            text="Show Answer",
            width=120,
            height=32,
            fg_color="#F3F4F6",
            text_color="black",
            hover_color="#E5E7EB",
            corner_radius=16,
            command=self.show_answer
        )
        self.show_answer_btn.pack(pady=20)

        self.rating_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        # Options: Very Hard (0) and Hard (2) use red; Medium (3), Easy (4), Very Easy (5) use white.
        options = [
            ("Very Hard", 0),
            ("Hard", 2),
            ("Medium", 3),
            ("Easy", 4),
            ("Very Easy", 5)
        ]
        for label, quality in options:
            predicted = self.predict_interval(quality)
            btn_text = f"{label} ({predicted})"
            if label in ("Very Hard", "Hard"):
                fg_color = "#FEE2E2"
                text_color = "#DC2626"
                hover_color = "#FECACA"
            else:
                fg_color = "#F3F4F6"
                text_color = "black"
                hover_color = "#E5E7EB"
            btn = ctk.CTkButton(
                self.rating_frame,
                text=btn_text,
                width=120,
                height=32,
                corner_radius=16,
                fg_color=fg_color,
                text_color=text_color,
                hover_color=hover_color,
                command=lambda q=quality: self.rate_card_difficulty(q)
            )
            btn.pack(side="left", padx=5)

    def display_card(self):
        self.answer_frame.pack_forget()
        self.rating_frame.pack_forget()
        self.show_answer_btn.pack(pady=20)

        card = self.cards[self.current_index]
        self.current_card_id = card[0]
        self.question_label.configure(text=card[1])
        self.answer_label.configure(text=card[2])
        self.progress_label.configure(text=f"Card {self.current_index + 1}/{len(self.cards)}")
        self.card_start_time = datetime.now()

    def show_answer(self):
        self.show_answer_btn.pack_forget()
        self.answer_frame.pack()
        self.rating_frame.pack(pady=20)

    def rate_card_difficulty(self, quality):
        # Measure incremental time for the current card
        time_taken = (datetime.now() - self.card_start_time).total_seconds()
        card_id = self.current_card_id
        db = Database()
        new_params = db.update_spaced_repetition(self.user_id, card_id, quality)
        is_correct = False if quality <= 2 else True
        total_cards = len(self.cards)
        avg_time = self.total_time / total_cards if total_cards > 0 else 0

        # Pass time_taken as the deck_time to record the incremental time for this card
        db.save_quiz_result(self.user_id, self.deck_id, card_id, is_correct, self.total_time, avg_time, time_taken)

        if is_correct:
            self.correct_count += 1
        self.total_time += time_taken
        self.current_index += 1
        if self.current_index < len(self.cards):
            self.display_card()
        else:
            self.end_quiz()

    def end_quiz(self):
        total_cards = len(self.cards)
        accuracy = (self.correct_count / total_cards) * 100
        avg_time = self.total_time / total_cards
        db = Database()
        db.save_quiz_attempt(self.user_id, self.deck_id, self.current_card_id, self.total_time, self.correct_count >= 1)
        self.show_summary(accuracy, avg_time)

    def show_summary(self, accuracy, avg_time):
        total_cards = len(self.cards)
        wrong_answers = total_cards - self.correct_count
        for widget in self.winfo_children():
            widget.destroy()
        summary = ctk.CTkFrame(self, fg_color="#F3F4F6")
        summary.pack(expand=True, fill="both", padx=30, pady=20)
        ctk.CTkLabel(
            summary,
            text="Quiz Complete!",
            font=("Inter", 24, "bold"),
            text_color="black"
        ).pack(pady=(40, 20))
        stats = [
            ("Cards Reviewed", f"{total_cards}"),
            ("Correct Answers", f"{self.correct_count}"),
            ("Wrong Answers", f"{wrong_answers}"),
            ("Accuracy", f"{accuracy:.1f}%"),
            ("Total Time", f"{self.total_time:.1f}s"),
            ("Avg Time per Card", f"{avg_time:.1f}s")
        ]
        for label, value in stats:
            stat_frame = ctk.CTkFrame(summary, fg_color="transparent")
            stat_frame.pack(pady=10)
            ctk.CTkLabel(stat_frame, text=label, font=("Inter", 14), text_color="#4B5563").pack(side="left", padx=5)
            ctk.CTkLabel(stat_frame, text=value, font=("Inter", 14, "bold"), text_color="black").pack(side="left",
                                                                                                      padx=5)
        # Return button now returns to the QuizPage (deck selection), ending the current session.
        ctk.CTkButton(
            summary,
            text="Return to Quiz",
            corner_radius=16,
            fg_color="#F3F4F6",
            text_color="black",
            hover_color="#E5E7EB",
            command=lambda: self.switch_page(QuizPage, user_id=self.user_id,
                                             switch_page=self.switch_page)
        ).pack(pady=40)

    def show_no_cards_message(self):
        for widget in self.winfo_children():
            widget.destroy()
        message_frame = ctk.CTkFrame(self, fg_color="white")
        message_frame.pack(expand=True, fill="both", padx=30, pady=20)
        ctk.CTkLabel(message_frame, text="No cards available for review!", font=("Inter", 18, "bold"),
                     text_color="black").pack(expand=True)
        ctk.CTkButton(
            message_frame,
            text="Return to Quiz",
            width=200,
            height=40,
            command=lambda: self.switch_page(QuizPage, user_id=self.user_id,
                                             switch_page=self.switch_page)
        ).pack(pady=20)

    def update_timer(self):
        if not self.timer_label.winfo_exists():
            return
        elapsed = datetime.now() - self.start_time
        total_seconds = int(elapsed.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        timer_text = f"Time Elapsed: {hours:02d}:{minutes:02d}:{seconds:02d}"
        try:
            self.timer_label.configure(text=timer_text)
        except Exception:
            return
        self.after(1000, self.update_timer)

matplotlib.use("Agg")  # For use with Tkinter
class AnalyticsPage(BasePage):
    def __init__(self, master, user_id, switch_page):
        super().__init__(master, user_id, switch_page)
        self.stats = self.db.get_aggregated_quiz_stats(self.user_id)

        # Header
        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 0))
        ctk.CTkLabel(
            header_frame,
            text="Analytics",
            font=("Inter", 24, "bold"),
            text_color="black"
        ).pack(side="left")

        # Separator
        separator = ctk.CTkFrame(self.main_content, height=1, fg_color="#E5E7EB")
        separator.pack(fill="x", padx=30, pady=(10, 0))

        # Scrollable container
        self.content_container = ctk.CTkScrollableFrame(
            self.main_content,
            fg_color="white",
            border_width=1,
            border_color="#E5E7EB"
        )
        self.content_container.pack(fill="both", expand=True, padx=30, pady=20)

        # Create sections
        self.create_stats_section()
        self.create_deck_performance_section()
        self.create_graph_controls()
        self.create_return_button()

    ######################
    # 1) Stats Section
    ######################
    def create_stats_section(self):
        stats_container = ctk.CTkFrame(
            self.content_container,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color="#E5E7EB"
        )
        stats_container.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            stats_container,
            text="Overall Statistics",
            font=("Inter", 18, "bold"),
            text_color="#111827"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        stats_parent = ctk.CTkFrame(stats_container, fg_color="white")
        stats_parent.pack(fill="x", padx=20, pady=(0, 15))

        stat_items = [
            ("Total Sessions", f"{self.stats['session_count']}", "📊"),
            ("Total Cards", f"{self.stats['total_cards']}", "📄"),
            ("Correct Answers", f"{self.stats['total_correct']}", "✅"),
            ("Overall Accuracy", f"{self.stats['avg_accuracy']:.1f}%", "🎯"),
            ("Total Time", f"{self.stats['total_time']:.1f}s", "⏱️"),
            ("Avg Time/Card", f"{self.stats['overall_avg_time_per_card']:.1f}s", "⚡")
        ]

        # 2 columns, uniform widths
        for i in range(0, len(stat_items), 2):
            row_frame = ctk.CTkFrame(stats_parent, fg_color="white")
            row_frame.pack(fill="x", pady=5)
            row_frame.grid_columnconfigure(0, weight=1, uniform="stats_col")
            row_frame.grid_columnconfigure(1, weight=1, uniform="stats_col")

            for j in range(2):
                if i + j < len(stat_items):
                    col = j
                    label_text, value, icon = stat_items[i + j]
                    self.create_stat_card(row_frame, label_text, value, icon, col)

    def create_stat_card(self, parent, label_text, value, icon, col):
        cell_frame = ctk.CTkFrame(parent, fg_color="white")
        cell_frame.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")

        stat_card = ctk.CTkFrame(
            cell_frame,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color="#E5E7EB",
        )
        stat_card.pack(fill="both", expand=True, padx=5, pady=5)

        card_content = ctk.CTkFrame(stat_card, fg_color="white")
        card_content.pack(fill="both", expand=True, padx=10, pady=10)

        header_frame = ctk.CTkFrame(card_content, fg_color="white")
        header_frame.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(
            header_frame,
            text=icon,
            font=("Inter", 16),
            text_color="#4B5563"
        ).pack(side="left")

        ctk.CTkLabel(
            header_frame,
            text=label_text,
            font=("Inter", 12),
            text_color="#4B5563"
        ).pack(side="left", padx=(5, 0))

        value_frame = ctk.CTkFrame(card_content, fg_color="white")
        value_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(
            value_frame,
            text=value,
            font=("Inter", 22, "bold"),
            text_color="#111827"
        ).pack(expand=True)

    ######################
    # 2) Deck Performance
    ######################
    def create_deck_performance_section(self):
        decks = self.db.get_decks(self.user_id)
        if not decks:
            return

        perf_container = ctk.CTkFrame(
            self.content_container,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color="#E5E7EB"
        )
        perf_container.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            perf_container,
            text="Deck Performance Scores",
            font=("Inter", 18, "bold"),
            text_color="#111827"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        decks_frame = ctk.CTkFrame(perf_container, fg_color="white")
        decks_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.deck_expanded = {}
        decks_list = []
        for deck_id, deck_name in decks:
            score = self.db.get_deck_performance_score(self.user_id, deck_id)
            decks_list.append((deck_id, deck_name, score))
        decks_list.sort(key=lambda x: x[2], reverse=True)

        for deck_id, deck_name, score in decks_list:
            self.create_deck_score_card(decks_frame, deck_id, deck_name, score)

    def create_deck_score_card(self, parent, deck_id, deck_name, score):
        deck_container = ctk.CTkFrame(parent, fg_color="white")
        deck_container.pack(fill="x", pady=5)

        score_card = ctk.CTkFrame(
            deck_container,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color="#E5E7EB"
        )
        score_card.pack(fill="x")

        content = ctk.CTkFrame(score_card, fg_color="white")
        content.pack(fill="x", padx=15, pady=10)

        # Left: deck name
        name_frame = ctk.CTkFrame(content, fg_color="white")
        name_frame.pack(side="left", fill="y")

        ctk.CTkLabel(
            name_frame,
            text=deck_name,
            font=("Inter", 14, "bold"),
            text_color="#111827"
        ).pack(anchor="w")

        # Right: score + "View Details"
        right_frame = ctk.CTkFrame(content, fg_color="white")
        right_frame.pack(side="right", fill="x", expand=False)

        if score < 50:
            color = "#DC2626"
        elif score < 75:
            color = "#F59E0B"
        else:
            color = "#10B981"

        ctk.CTkLabel(
            right_frame,
            text=f"{score:.1f}/100",
            font=("Inter", 14, "bold"),
            text_color=color
        ).pack(side="right", padx=(10, 0))

        view_stats_button = ctk.CTkButton(
            right_frame,
            text="View Details",
            width=100,
            height=32,
            corner_radius=16,
            fg_color="#F3F4F6",
            text_color="black",
            hover_color="#E5E7EB",
            command=lambda d_id=deck_id: self.toggle_deck_details(d_id)
        )
        view_stats_button.pack(side="right", padx=(10, 0))

        details_frame = ctk.CTkFrame(
            deck_container,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color="#E5E7EB"
        )
        details_frame.pack_forget()
        self.deck_expanded[deck_id] = details_frame

    def toggle_deck_details(self, deck_id):
        details_frame = self.deck_expanded.get(deck_id)
        if details_frame is None:
            return

        if details_frame.winfo_ismapped():
            details_frame.pack_forget()
        else:
            for widget in details_frame.winfo_children():
                widget.destroy()

            deck_stats = self.db.get_deck_stats(self.user_id, deck_id)

            stats_parent = ctk.CTkFrame(details_frame, fg_color="white")
            stats_parent.pack(fill="both", expand=True, padx=15, pady=15)

            deck_stat_items = [
                ("Sessions", f"{deck_stats.get('session_count', 0)}", "📊"),
                ("Cards", f"{deck_stats.get('total_cards', 0)}", "📄"),
                ("Correct", f"{deck_stats.get('total_correct', 0)}", "✅"),
                ("Accuracy", f"{deck_stats.get('avg_accuracy', 0):.1f}%", "🎯"),
                ("Total Time", f"{deck_stats.get('total_time', 0):.1f}s", "⏱️"),
                ("Avg Time/Card", f"{deck_stats.get('avg_time_per_card', 0):.1f}s", "⚡")
            ]

            for i in range(0, len(deck_stat_items), 2):
                row_frame = ctk.CTkFrame(stats_parent, fg_color="white")
                row_frame.pack(fill="x", pady=5)
                row_frame.grid_columnconfigure(0, weight=1, uniform="deck_stat_col")
                row_frame.grid_columnconfigure(1, weight=1, uniform="deck_stat_col")

                for j in range(2):
                    if i + j < len(deck_stat_items):
                        col = j
                        self.create_stat_card(
                            row_frame,
                            deck_stat_items[i + j][0],
                            deck_stat_items[i + j][1],
                            deck_stat_items[i + j][2],
                            col
                        )

            details_frame.pack(fill="x", pady=(5, 10))

    ######################
    # 3) Graph Controls
    ######################
    def create_graph_controls(self):
        graph_container = ctk.CTkFrame(
            self.content_container,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color="#E5E7EB"
        )
        graph_container.pack(fill="both", expand=True, pady=(0, 20))

        ctk.CTkLabel(
            graph_container,
            text="Performance Graphs",
            font=("Inter", 18, "bold"),
            text_color="#111827"
        ).pack(anchor="w", padx=20, pady=(15, 5))

        controls_row = ctk.CTkFrame(graph_container, fg_color="white")
        controls_row.pack(fill="x", padx=20, pady=(0, 5))

        # "Select Deck" label
        ctk.CTkLabel(
            controls_row,
            text="Select Deck",
            font=("Inter", 14, "bold"),
            text_color="#111827"
        ).pack(side="left", padx=(0, 5))

        decks = self.db.get_decks(self.user_id)
        self.deck_options = {}
        self.deck_id_to_name = {}
        for deck_id, deck_name in decks:
            self.deck_options[deck_name] = str(deck_id)
            self.deck_id_to_name[str(deck_id)] = deck_name

        default_deck_name = list(self.deck_options.keys())[0] if self.deck_options else ""
        self.selected_deck_name = ctk.StringVar(value=default_deck_name)

        self.deck_menu = ctk.CTkOptionMenu(
            controls_row,
            values=list(self.deck_options.keys()),
            variable=self.selected_deck_name,
            width=140,
            corner_radius=8,
            dropdown_font=("Inter", 12),
            font=("Inter", 12),
            fg_color="white",
            button_color="#F3F4F6",
            button_hover_color="#E5E7EB",
            text_color="#111827"
        )
        self.deck_menu.pack(side="left", padx=(0, 20))

        # "Select Graph Type"
        ctk.CTkLabel(
            controls_row,
            text="Select Graph Type",
            font=("Inter", 14, "bold"),
            text_color="#111827"
        ).pack(side="left", padx=(0, 5))

        self.selected_graph = ctk.StringVar(value="Accuracy Over Time")
        self.graph_menu = ctk.CTkOptionMenu(
            controls_row,
            values=["Accuracy Over Time", "Avg Time Per Card", "Cumulative Retention"],
            variable=self.selected_graph,
            width=160,
            corner_radius=8,
            dropdown_font=("Inter", 12),
            font=("Inter", 12),
            fg_color="white",
            button_color="#F3F4F6",
            button_hover_color="#E5E7EB",
            text_color="#111827"
        )
        self.graph_menu.pack(side="left", padx=(0, 20))

        # Show Graph button, styled
        show_graph_btn = ctk.CTkButton(
            controls_row,
            text="Show Graph",
            width=100,
            height=32,
            corner_radius=30,   # more rounded
            font=("Inter", 14),
            fg_color="#F3F4F6",
            text_color="black",
            hover_color="#E5E7EB",
            command=self.show_graph
        )
        show_graph_btn.pack(side="left")

        self.graph_display_frame = ctk.CTkFrame(graph_container, fg_color="white", corner_radius=8)
        self.graph_display_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

    def show_graph(self):
        try:
            deck_name = self.selected_deck_name.get()
            deck_id_str = self.deck_options.get(deck_name, None)
            if deck_id_str is None:
                self.show_no_data_message()
                return
            deck_id = int(deck_id_str)

            graph_type = self.selected_graph.get()

            # Clear old graph
            for widget in self.graph_display_frame.winfo_children():
                widget.destroy()

            # Retrieve data
            dates, y_values = [], []
            ylabel = ""
            title = ""
            # Single line color #6572f8
            line_color = "#636ae8"

            if graph_type == "Accuracy Over Time":
                dates, y_values = self.db.get_deck_accuracy_over_time(self.user_id, deck_id)
                ylabel = "Accuracy (%)"
                title = f"Accuracy Over Time - {deck_name}"
            elif graph_type == "Avg Time Per Card":
                dates, y_values = self.db.get_deck_avg_time_over_time(self.user_id, deck_id)
                ylabel = "Avg Time (s)"
                title = f"Avg Time Per Card - {deck_name}"
            elif graph_type == "Cumulative Retention":
                dates, y_values = self.db.get_deck_cumulative_retention(self.user_id, deck_id)
                ylabel = "Cumulative Retention (%)"
                title = f"Cumulative Retention - {deck_name}"

            if not dates or not y_values:
                self.show_no_data_message()
                return

            # Convert date strings if needed
            if isinstance(dates[0], str):
                dates = [datetime.strptime(d, "%Y-%m-%d") for d in dates]

            plt.close("all")
            plt.style.use("seaborn-v0_8-whitegrid")

            fig, ax = plt.subplots(figsize=(8, 5))

            # 1) Plot the line with no picking
            ax.plot(dates, y_values, marker=None, linestyle="-", linewidth=2, color=line_color, zorder=2)

            # 2) Plot the points (scatter) with picking
            points = ax.scatter(dates, y_values, color=line_color, s=40, zorder=3, picker=True)

            ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
            ax.set_xlabel("Date", fontsize=12, labelpad=10)
            ax.set_ylabel(ylabel, fontsize=12, labelpad=10)

            date_format = mdates.DateFormatter("%b %d")
            ax.xaxis.set_major_formatter(date_format)
            if len(dates) > 8:
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=len(dates) // 8))
            ax.grid(True, linestyle="--", alpha=0.7)

            # Y-limits
            if graph_type in ["Accuracy Over Time", "Cumulative Retention"]:
                ax.set_ylim([0, 100])
            else:
                y_min = min(y_values) * 0.8
                y_max = max(y_values) * 1.2
                ax.set_ylim([y_min, y_max])

            # Use mplcursors on the scatter, so only the dots are hoverable
            cursor = mplcursors.cursor(points, hover=True)

            @cursor.connect("add")
            def on_add(sel):
                # x_val, y_val from the scatter
                x_val, y_val = sel.target
                # Convert x_val to datetime if needed
                if not isinstance(x_val, datetime):
                    x_val = mdates.num2date(x_val)
                date_str = x_val.strftime("%Y-%m-%d")

                # Grayish hover container with partial transparency & border radius
                # boxstyle="round,pad=0.3" for corner radius
                sel.annotation.set_bbox(dict(facecolor="#f3f4f6",
                                             edgecolor="none",
                                             alpha=0.9,
                                             boxstyle="round,pad=0.3"))

                if graph_type in ["Accuracy Over Time", "Cumulative Retention"]:
                    sel.annotation.set_text(f"{date_str}\n{y_val:.1f}%")
                else:
                    sel.annotation.set_text(f"{date_str}\n{y_val:.1f}s")

            fig.patch.set_facecolor("#F9FAFB")
            ax.set_facecolor("#FFFFFF")
            fig.tight_layout(pad=3.0)

            canvas = FigureCanvasTkAgg(fig, master=self.graph_display_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        except Exception as e:
            self.show_error_message(str(e))

    ######################
    # 4) No Data & Error
    ######################
    def show_no_data_message(self):
        message_frame = ctk.CTkFrame(self.graph_display_frame, fg_color="transparent")
        message_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(
            message_frame,
            text="No data available for this selection",
            font=("Inter", 16, "bold"),
            text_color="#4B5563"
        ).pack(expand=True)

        ctk.CTkLabel(
            message_frame,
            text="Complete some quizzes with this deck to see performance data",
            font=("Inter", 14),
            text_color="#6B7280"
        ).pack(expand=True)

    def show_error_message(self, error_text):
        message_frame = ctk.CTkFrame(self.graph_display_frame, fg_color="transparent")
        message_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(
            message_frame,
            text="Error displaying graph",
            font=("Inter", 16, "bold"),
            text_color="#DC2626"
        ).pack(expand=True)

        ctk.CTkLabel(
            message_frame,
            text=f"Details: {error_text}",
            font=("Inter", 14),
            text_color="#6B7280"
        ).pack(expand=True)

    ######################
    # 5) Return Button
    ######################
    def create_return_button(self):
        button_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        button_container.pack(side="bottom", fill="x", pady=(10, 0))

        ctk.CTkButton(
            button_container,
            text="Return to Dashboard",
            width=200,
            height=40,
            corner_radius=16,
            font=("Inter", 14),
            fg_color="#F3F4F6",
            text_color="black",
            hover_color="#E5E7EB",
            command=lambda: self.switch_page(
                DecksPage,
                user_id=self.user_id,
                switch_page=self.switch_page
            )
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
