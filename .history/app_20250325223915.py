# external imports
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta

import matplotlib
matplotlib.use("Agg")  # Set backend BEFORE importing pyplot or any submodules that use it

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcursors


# my imports
from database import Database
from components import BasePage, BaseContainer, BaseDialog

db = Database()

class DecksPage(BasePage):
    # initialises decks page with master, user id and switch page
    def __init__(self, master, user_id, switch_page):
        super().__init__(master, user_id, switch_page)
        self.selected_decks = set()
        self.master.db = Database()

        # main header container ("My Decks" title)
        self.header = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.header.pack(fill="x", padx=30, pady=(20, 0))
        ctk.CTkLabel(self.header, text="My Decks", font=("Inter", 24, "bold"), text_color="black").pack(side="left")

        # creates filter and search container and packs to display on the page
        self.filter_by_priority = ctk.CTkFrame(self.header, fg_color="transparent")
        self.filter_by_priority.pack(side="right", padx=10)
        # variable to hold deck search input
        self.deck_search_input = ctk.StringVar()
        # deck search entry field
        self.deck_search_entry = ctk.CTkEntry(
            self.filter_by_priority, 
            textvariable=self.deck_search_input,
            placeholder_text="Search deck",
            placeholder_text_color="#D1D1D1",
            text_color="#000000", 
            fg_color="white", 
            border_color="#e5e7eb", 
            width=200)
        self.deck_search_entry.pack(side="left", padx=5)
        # variable to hold deck priority selection (default "all" to show all decks with all priority types)
        self.deck_priority_input = ctk.StringVar(value="all")
        # creates priority dropdown menu
        self.deck_priority_dropdown = ctk.CTkOptionMenu(
            self.filter_by_priority,
            values=["all", "High", "Medium", "Low"],
            variable=self.deck_priority_input,
            width=120,
            fg_color="white",
            button_color="#F3F4F6",
            button_hover_color="#E5E7EB",
            text_color="#111827")
        self.deck_priority_dropdown.pack(side="left", padx=5)
        # trace_add listens for any changes to search field or priority dropdown
        # and executes update_deck_containers() when a change is detected
        self.deck_search_input.trace_add("write", lambda *args: self.update_deck_containers())
        self.deck_priority_input.trace_add("write", lambda *args: self.update_deck_containers())

        # creates buttons container and packs it with add and delete selected buttons to display on the page
        self.buttons = ctk.CTkFrame(self.header, fg_color="transparent")
        self.buttons.pack(side="right")
        ctk.CTkButton(
            self.buttons, 
            text="+ Add", 
            width=70, 
            height=32, 
            corner_radius=16,       
            fg_color="#F3F4F6", 
            text_color="black", 
            hover_color="#E5E7EB",
            command=self.add_deck).pack(side="left", padx=5)

        self.delete_button = ctk.CTkButton(
            self.buttons, 
            text="Delete Selected", 
            width=70, 
            height=32,                                 
            corner_radius=16, 
            fg_color="#FEE2E2", 
            text_color="#DC2626",
            hover_color="#FECaCa", 
            state="disabled",
            command=self.delete_selected_decks)
        self.delete_button.pack(side="left", padx=5)

        # creates seperator between sidebar and main content area on the right
        self.separator = ctk.CTkFrame(self.main_content, height=1, fg_color="#E5E7EB")
        self.separator.pack(fill="x", padx=30, pady=(20, 0))

        # makes the main_content area where decks are displayed scrollable (incase user has too many decks 
        # to be displayed on the screen at once)
        self.decks_frame = ctk.CTkScrollableFrame(
            self.main_content, 
            fg_color="transparent",
            scrollbar_button_color="#E5E7EB",
            scrollbar_button_hover_color="#D1D5DB")
        self.decks_frame.pack(fill="both", expand=True, padx=30, pady=20)
        self.decks_frame.grid_columnconfigure((0, 1, 2), weight=1, pad=10)

        self.update_deck_containers()

    # updates the deck containers displayed on the page
    def update_deck_containers(self):
        # clear current deck containers
        for widget in self.decks_frame.winfo_children():
            widget.destroy()

        
        deck_containers = []
        decks = db.get_decks(self.user_id)

        # creates deck_containers as tuples: (deck_id, deck_name, avg_ef, card_count)
        # gets avg_ef of each deck by totalling ef for each card and dividing by number of cards
        for deck_id, deck_name in decks:
            cards = db.get_cards(deck_id)
            if cards:
                total_ef = sum(db.get_card_easiness(self.user_id, c[0]) for c in cards)
                avg_ef = total_ef / len(cards)
            else:
                avg_ef = 2.5
            card_count = db.get_card_count(deck_id)
            deck_containers.append((deck_id, deck_name, avg_ef, card_count))

        # filter by search query
        search_query = self.deck_search_input.get().lower().strip()
        if search_query:
            deck_containers = [d for d in deck_containers if search_query in d[1].lower()]

        # filter by priority (using avg_ef)
        priority_filter = self.deck_priority_input.get().lower()
        if priority_filter != "all":
            if priority_filter == "high":
                deck_containers = [d for d in deck_containers if d[2] < 2.0]
            elif priority_filter == "medium":
                deck_containers = [d for d in deck_containers if 2.0 <= d[2] < 2.5]
            elif priority_filter == "low":
                deck_containers = [d for d in deck_containers if d[2] >= 2.5]

        # if user has no decks, a message "No decks found" is displayed
        if not deck_containers:
            no_decks = ctk.CTkFrame(self.decks_frame, fg_color="transparent")
            no_decks.pack(fill="both", expand=True)
            ctk.CTkLabel(no_decks, text="No decks found", font=("Inter", 16, "bold"), text_color="#4B5563").pack(expand=True, pady=50)
            return

        # sort decks using bst (binary search tree) (based on avg_ef) (lowest ef to highest)
        # and so highest to lowest priority
        from graph import DeckNode, insert_node, in_order
        root = None
        for deck in deck_containers:
            node = DeckNode(deck_id=deck[0], deck_name=deck[1], avg_ef=deck[2], card_count=deck[3])
            root = insert_node(root, node)
        sorted_nodes = in_order(root)

        # display decks in a 3-column grid
        row, col = 0, 0
        for node in sorted_nodes:
            deck_container = DeckContainer(
                self.decks_frame,
                deck_id=node.deck_id,
                deck_name=node.deck_name,
                card_count=node.card_count,
                avg_ef=node.avg_ef,
                edit_callback=self.edit_deck,
                delete_callback=self.delete_deck)
            deck_container.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            col += 1
            if col == 3:
                col = 0
                row += 1

    # adds a new deck to database and updates decks displayed on screen
    def add_deck(self):
        # shows add deck dialog on screen
        dialog = AddDeckDialog(self)
        dialog.grab_set()
        new_deck_name = dialog.get_deck_name()
        if new_deck_name:
            
            deck_id = db.create_deck(self.user_id, new_deck_name)
            if deck_id:
                self.update_deck_containers()
                self.sidebar.update_deck_containers()

    # edits an existing deck, saves changes to database and updates decks displayed on screen
    def edit_deck(self, deck_id):
        
        deck_info = db.get_deck_info(deck_id)
        current_name = deck_info["name"]
        # shows edit deck dialog on screen
        dialog = EditDeckDialog(self, deck_id, current_name)
        dialog.grab_set()
    # deletes a deck, after a confirmation message, saves changes to database and updates the decks displayed on screen
    def delete_deck(self, deck_id):
        if messagebox.askyesno("Delete Deck", "are you sure you want to delete this deck?"):
            
            db.delete_deck(deck_id)
            self.update_deck_containers()
            self.sidebar.update_deck_containers()

    # allows user to toggle the deck (select and deselect)
    def toggle_deck(self, deck_id, is_selected):
        if is_selected:
            self.selected_decks.add(deck_id)
        else:
            self.selected_decks.discard(deck_id)
        # delete selected button text looks slightly transparent if no decks are selected
        # otherwise it looks normal
        self.delete_button.configure(state="normal" if self.selected_decks else "disabled")

    # deletes all decks in selected decks, upon clicking delete selected button
    def delete_selected_decks(self):
        if not self.selected_decks:
            return
        if messagebox.askyesno("Delete Decks", f"are you sure you want to delete {len(self.selected_decks)} deck(s)?"):
            
            for deck_id in self.selected_decks:
                db.delete_deck(deck_id)
            self.selected_decks.clear()
            self.update_deck_containers()
            self.sidebar.update_deck_containers()
            self.delete_button.configure(state="disabled")

class DeckContainer(BaseContainer):
    # initialises deck container with master, deck id, deck name, card count, avg ef, edit and delete callbacks
    def __init__(self, master, deck_id, deck_name, card_count, avg_ef, edit_callback, delete_callback):
        super().__init__(master)
        self.deck_id = deck_id
        self.selected = False
        self.avg_ef = avg_ef
        self.edit_callback = edit_callback
        self.delete_callback = delete_callback
        self.master.db = Database()

        # creates a main deck container
        self.deck_container = ctk.CTkFrame(self, fg_color="transparent")
        self.deck_container.pack(fill="both", expand=True, padx=20, pady=20)

        # creates a left container for deck info (name, card count, etc.)
        self.info = ctk.CTkFrame(self.deck_container, fg_color="transparent")
        self.info.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(
            self.info,
            text=deck_name,
            font=("Inter", 16, "bold"),
            text_color="black"
        ).pack(anchor="w")
        ctk.CTkLabel(
            self.info,
            text=f"{card_count} cards",
            font=("Inter", 14),
            text_color="#6B7280"
        ).pack(anchor="w", pady=(5, 0))

        # get and display count of cards available for review 
        self.available_for_review = self.db.get_available_for_review(deck_id)
        ctk.CTkLabel(
            self.info,
            text=f"{self.available_for_review} available for review",
            font=("Inter", 12),
            text_color="#DC2626"
        ).pack(anchor="w", pady=(5, 0))

        # creates a priority indicator (based on avg_ef)
        if self.avg_ef < 2.0:
            self.priority_text = "High Priority"
            self.tag_color = "red"
        elif self.avg_ef < 2.5:
            self.priority_text = "Medium Priority"
            self.tag_color = "orange"
        else:
            self.priority_text = "Low Priority"
            self.tag_color = "green"
        ctk.CTkLabel(
            self.info,
            text=self.priority_text,
            font=("Inter", 12, "bold"),
            text_color=self.tag_color
        ).pack(anchor="w", pady=(5, 0))

        # creates a buttons container (Edit/Delete) at the bottom (only if callbacks provided)
        if self.edit_callback is not None and self.delete_callback is not None:
            self.btn_container = ctk.CTkFrame(self.deck_container, fg_color="transparent")
            self.btn_container.pack(side="bottom", fill="x", pady=(10, 0))
            ctk.CTkButton(
                self.btn_container,
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
                self.btn_container,
                text="Delete",
                width=70,
                height=32,
                corner_radius=16,
                fg_color="#FEE2E2",
                text_color="#DC2626",
                hover_color="#FECaCa",
                command=lambda: self.delete_callback(self.deck_id)
            ).pack(side="left", padx=(2, 5), pady=5)

        # creates a multi-selection checkbox at the top right
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

    # callback for checkbox toggle to change checkbox colour on toggle
    def on_checkbox_toggle(self):
        self.selected = self.checkbox.get()
        if self.selected:
            self.configure(fg_color="#F5F3FF")
            self.checkbox.configure(fg_color="#636ae8", checkmark_color="white")
        else:
            self.configure(fg_color="white")
            self.checkbox.configure(fg_color="white", checkmark_color="black")

class CardsPage(BasePage):
    # initialises cards page with master, user id, deck id and switch page
    def __init__(self, master, user_id, deck_id, switch_page):
        super().__init__(master, user_id, switch_page)
        self.deck_id = deck_id
        self.selected_cards = set()
        self.deck_info = self.db.get_deck_info(self.deck_id)
        self.master.db = Database()

        # creates header with deck name and card count
        self.header = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.header.pack(fill="x", padx=30, pady=20)
        ctk.CTkLabel(
            self.header,
            text=self.deck_info["name"],
            font=("Inter", 24, "bold"),
            text_color="black"
        ).pack(side="left")
        ctk.CTkLabel(
            self.header,
            text=f"{self.deck_info['card_count']} cards",
            font=("Inter", 14),
            text_color="#6B7280"
        ).pack(side="left", padx=(10, 0))

        # creates filter and search sections
        self.filter_by_priority = ctk.CTkFrame(self.header, fg_color="transparent")
        self.filter_by_priority.pack(side="right", padx=10)
        # creates variable to hold card search input
        self.card_search_input = ctk.StringVar()
        # creates card search entry field
        self.card_search_entry = ctk.CTkEntry(
            self.filter_by_priority,
            textvariable=self.card_search_input,
            placeholder_text="Search card",
            placeholder_text_color="#D1D1D1",
            text_color="#000000",
            fg_color="white",
            border_color="#e5e7eb",
            width=200
        )
        self.card_search_entry.pack(side="left", padx=5)
        # creates variable to hold card_priority_filter selection (default "all")
        self.card_priority_filter_var = ctk.StringVar(value="all")
        # creates priority dropdown menu for cards
        self.card_priority_filter_menu = ctk.CTkOptionMenu(
            self.filter_by_priority,
            values=["all", "High", "Medium", "Low"],
            variable=self.card_priority_filter_var,
            width=120,
            fg_color="white",
            button_color="#F3F4F6",
            button_hover_color="#E5E7EB",
            text_color="#111827"
        )
        self.card_priority_filter_menu.pack(side="left", padx=5)
        # trace_add listens for any inputs or selections on search fields or priority selection and then calls update_card_containers accordingly
        self.card_search_input.trace_add("write", lambda *args: self.update_card_containers())
        self.card_priority_filter_var.trace_add("write", lambda *args: self.update_card_containers())

        # creates delete selected cards button
        self.delete_cards_button = ctk.CTkButton(
            self.header,
            text="Delete Selected",
            width=120,
            height=32,
            corner_radius=16,
            fg_color="#FEE2E2",
            text_color="#DC2626",
            hover_color="#FECaCa",
            state="disabled",
            command=self.delete_selected_cards
        )
        self.delete_cards_button.pack(side="right", padx=5)
        # creates add card button
        ctk.CTkButton(
            self.header,
            text="+ Add Card",
            width=70,
            height=32,
            corner_radius=16,
            fg_color="#F3F4F6",
            text_color="black",
            hover_color="#E5E7EB",
            command=self.add_card
        ).pack(side="right", padx=5)

        # creates scrollable container for cards to be displayed in
        self.cards_frame = ctk.CTkScrollableFrame(
            self.main_content,
            fg_color="transparent",
            scrollbar_button_color="#E5E7EB",
            scrollbar_button_hover_color="#D1D5DB"
        )
        self.cards_frame.pack(fill="both", expand=True, padx=30, pady=20)
        self.update_card_containers()

    # updates the card containers displayed on the page
    def update_card_containers(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        raw_cards = self.db.get_cards(self.deck_id)
        cards = []
        for card in raw_cards:
            card_id, _, question, answer = card
            ef = self.db.get_card_easiness(self.user_id, card_id)
            cards.append((card_id, question, answer, ef))

        # creates filtering by search query
        search_query = self.card_search_input.get().lower().strip()
        if search_query:
            cards = [c for c in cards if search_query in c[1].lower()]
        # creates filtering by priority (using ef)
        priority_filter = self.card_priority_filter_var.get().lower()
        if priority_filter != "all":
            if priority_filter == "high":
                cards = [c for c in cards if c[3] < 2.0]
            elif priority_filter == "medium":
                cards = [c for c in cards if 2.0 <= c[3] < 2.5]
            elif priority_filter == "low":
                cards = [c for c in cards if c[3] >= 2.5]

        if not cards:
            self.no_cards_frame = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
            self.no_cards_frame.pack(fill="both", expand=True)
            ctk.CTkLabel(
                self.no_cards_frame,
                text="No cards found",
                font=("Inter", 16, "bold"),
                text_color="#4B5563"
            ).pack(expand=True, pady=50)
            return

        # sorts cards using merge sort based on EF (lower EF means higher priority)
        # split is the first step of the merge sort algorithm (which is in misc.py)
        from misc import MiscFunctions
        sorted_cards = MiscFunctions.split(cards)
        for card in sorted_cards:
            self.card_container = CardContainer(
                self.cards_frame,
                card_id=card[0],
                question=card[1],
                answer=card[2],
                edit_callback=self.edit_card,
                delete_callback=self.delete_card,
                ef=card[3],
                user_id=self.user_id,
            )
            self.card_container.pack(fill="x", pady=10)

    # creates a dialog to add a new card to the deck and updates the cards page
    def add_card(self):
        dialog = AddCardDialog(self, deck_id=self.deck_id)
        dialog.grab_set() # means user can't click anywhere else, only on the dialog area

    # creates a dialog to edit an existing card and updates the card page
    def edit_card(self, card_id):
        try:
            card_info = self.db.get_card(card_id)
            dialog = EditCardDialog(self, card_id, card_info['question'], card_info['answer'])
            dialog.grab_set()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit card: {str(e)}")

    # deletes a card after confirmation and updates the card display
    def delete_card(self, card_id):
        if messagebox.askyesno("Delete Card", "are you sure you want to delete this card?"):
            self.db.delete_card(card_id)
            self.update_card_containers()

    # toggles card selection and updates delete button state
    def toggle_card_selection(self, card_id, selected):
        if selected:
            self.selected_cards.add(card_id)
        else:
            self.selected_cards.discard(card_id)
        self.delete_cards_button.configure(state="normal" if self.selected_cards else "disabled")

    # deletes all selected cards after confirmation and updates the card display
    def delete_selected_cards(self):
        if not self.selected_cards:
            return
        if messagebox.askyesno("Delete Cards", f"are you sure you want to delete {len(self.selected_cards)} card(s)?"):
            for card_id in self.selected_cards:
                self.db.delete_card(card_id)
            self.selected_cards.clear()
            self.update_card_containers()
            self.delete_cards_button.configure(state="disabled")

class CardContainer(BaseContainer):
    # initialises card container with master, card id, question, answer, edit and delete callbacks, ef and user id
    def __init__(self, master, card_id, question, answer, edit_callback, delete_callback, ef, user_id):
        super().__init__(master)
        self.card_id = card_id
        self.selected = False
        self.edit_callback = edit_callback
        self.delete_callback = delete_callback
        self.ef = ef
        self.user_id = user_id
        self.master.db = Database()

        # creates a card container
        self.card_container = ctk.CTkFrame(self, fg_color="transparent")
        self.card_container.pack(fill="x", padx=20, pady=15)

        # creates a label for the question text
        ctk.CTkLabel(
            self.card_container,
            text=question,
            font=("Inter", 16, "bold"),
            text_color="black"
        ).pack(anchor="w")
        # creates a label for the answer text
        ctk.CTkLabel(
            self.card_container,
            text=answer,
            font=("Inter", 14),
            text_color="black"
        ).pack(anchor="w", pady=(5, 0))

        # creates a priority indicator based on ef
        if self.ef < 2.0:
            self.priority_text = "High Priority"
            self.color = "red"
        elif self.ef < 2.5:
            self.priority_text = "Medium Priority"
            self.color = "orange"
        else:
            self.priority_text = "Low Priority"
            self.color = "green"
        ctk.CTkLabel(
            self.card_container,
            text=self.priority_text,
            font=("Inter", 12, "bold"),
            text_color=self.color
        ).pack(anchor="w", pady=(5, 10))

        # creates a buttons container (Edit/Delete) and packs them to display on screen
        self.buttons = ctk.CTkFrame(self.card_container, fg_color="transparent")
        self.buttons.pack(side="bottom", fill="x")
        self.btn_container = ctk.CTkFrame(self.buttons, fg_color="transparent")
        self.btn_container.pack(side="right", padx=5, pady=5)

        ctk.CTkButton(
            self.btn_container,
            text="Edit",
            width=70,
            height=32,
            corner_radius=16,
            fg_color="#F3F4F6",
            text_color="black",
            hover_color="#E5E7EB",
            command=lambda: self.edit_callback(self.card_id)
        ).pack(side="left", padx=(5, 2))
        ctk.CTkButton(
            self.btn_container,
            text="Delete",
            width=70,
            height=32,
            corner_radius=16,
            fg_color="#FEE2E2",
            text_color="#DC2626",
            hover_color="#FECaCa",
            command=lambda: self.delete_callback(self.card_id)
        ).pack(side="left", padx=(2, 5))

        # creates a checkbox at the top right
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

    # callback for checkbox toggle to update selection and appearance (no selection callback used)
    def on_checkbox_toggle(self):
        self.selected = self.checkbox.get()
        if self.selected:
            self.configure(fg_color="#F5F3FF")
            self.checkbox.configure(
                fg_color="#636ae8",
                border_color="#636ae8",
                checkmark_color="white"
            )
        else:
            self.configure(fg_color="white")
            self.checkbox.configure(
                fg_color="white",
                checkmark_color="black",
                hover_color="white"
            )

class AddCardDialog(BaseDialog):
    # initialises add card dialog with parent and deck id
    def __init__(self, parent, deck_id):
        # creates dialog with title "New Card" and specified size
        super().__init__(title="New Card", width=500, height=500)
        self.deck_id = deck_id
        self.parent = parent
        # creates title label "New Card"
        self.create_title("New Card")
        
        self.master.db = Database()

        # creates question section label
        ctk.CTkLabel(
            self.container,
            text="Question",
            font=("Inter", 14, "bold"),
            text_color="black"
        ).pack(pady=(10, 5))
        # creates text box for entering a new question
        self.question_entry = ctk.CTkTextbox(
            self.container,
            height=100,
            border_width=1,
            border_color="#E5E7EB",
            text_color="black",
            fg_color="white"
        )
        self.question_entry.pack(fill="x", padx=10, pady=(0, 10))

        # creates answer section label
        ctk.CTkLabel(
            self.container,
            text="answer",
            font=("Inter", 14, "bold"),
            text_color="black"
        ).pack(pady=(10, 5))
        # creates text box for entering a new answer
        self.answer_entry = ctk.CTkTextbox(
            self.container,
            height=100,
            border_width=1,
            border_color="#E5E7EB",
            text_color="black",
            fg_color="white"
        )
        self.answer_entry.pack(fill="x", padx=10, pady=(0, 10))

        # creates save card button that calls save_card() when clicked
        self.create_button("Save Card", self.save_card)
        # waits until the dialog is closed before returning control to the parent
        self.wait_window()

    # saves the new card to the database and closes the dialog
    def save_card(self):
        question = self.question_entry.get().strip()
        answer = self.answer_entry.get().strip()
        if not question or not answer:
            messagebox.showwarning("Warning", "Please fill in both question and answer")
            return
        
        db.create_card(self.deck_id, question, answer)
        self.parent.update_card_containers()
        self.cancel_event()

class AddDeckDialog(BaseDialog):
    # initialises add deck dialog with parent
    def __init__(self, parent):
        # creates dialog with title "New Deck" and specified size
        super().__init__(title="New Deck", width=400, height=300)
        # creates title label "New Deck"
        self.create_title("New Deck")
        
        self.master.db = Database()

        # creates label for deck name input
        ctk.CTkLabel(
            self.container,
            text="Enter deck name",
            font=("Inter", 14, "bold"),
            text_color="black"
        ).pack(pady=(10, 5))
        # creates entry field for deck name
        self.deck_entry = self.create_input_field("")
        # creates add deck button that calls self.save_deck when clicked
        self.create_button("add Deck", self.save_deck)
        # waits until the dialog is closed before returning control to the parent
        self.wait_window()

    # saves the new deck name to database
    def save_deck(self):
        new_deck = self.deck_entry.get().strip()
        if not new_deck:
            messagebox.showwarning("Warning", "Please enter a deck name")
            return
        self.cancel_event()

class EditCardDialog(BaseDialog):
    # initialises edit card dialog with parent, card id, current question and answer
    def __init__(self, parent, card_id, current_question, current_answer):
        # creates dialog with title "Edit Card" and specified size
        super().__init__(title="Edit Card", width=500, height=500)
        self.parent = parent
        self.card_id = card_id
        self.master.db = Database()

        # creates title label "Edit Card"
        self.create_title("Edit Card")

        # creates label for question section
        ctk.CTkLabel(
            self.container,
            text="Question",
            font=("Inter", 14, "bold"),
            text_color="black"
        ).pack(fill="x", pady=(10, 5))
        # creates text box for editing the question with the current question in it
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

        # creates label for answer section
        ctk.CTkLabel(
            self.container,
            text="answer",
            font=("Inter", 14, "bold"),
            text_color="black"
        ).pack(fill="x", pady=(10, 5))
        # creates text box for editing the answer with current answer in it
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

        # creates save changes button that calls save_card() when clicked
        self.create_button("Save Changes", self.save_card)

        # waits until the dialog is closed before returning control to the parent
        self.wait_window()

    # saves the updated card information to database
    def save_card(self):
        new_question = self.question_entry.get().strip()
        new_answer = self.answer_entry.get().strip()
        if not new_question or not new_answer:
            messagebox.showwarning("Warning", "Please fill in both question and answer")
            return
        try:
            db.update_card(self.card_id, new_question, new_answer)
            self.parent.update_card_containers()
            self.cancel_event() 
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update card: {str(e)}")

class EditDeckDialog(BaseDialog):
    # initialises edit deck dialog with parent, deck id and current deck name
    def __init__(self, parent, deck_id, current_deck_name):
        # creates dialog with title "Edit Deck" and specified size
        super().__init__(title="Edit Deck", width=400, height=300)
        self.parent = parent
        self.deck_id = deck_id
        self.master.db = Database()

        # creates title label "Edit Deck"
        self.create_title("Edit Deck")

        # creates label for deck name input
        ctk.CTkLabel(
            self.container,
            text="Deck Name",
            font=("Inter", 14, "bold"),
            text_color="black"
        ).pack(fill="x", pady=(10, 5))

        # creates entry field with the current deck name in it
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

        # creates save changes button that calls save_deck() when clicked
        self.create_button("Save Changes", self.save_deck)

        # waits until the dialog is closed before returning control to the parent
        self.wait_window()

    # saves the updated deck name to database
    def save_deck(self):
        new_deck_name = self.deck_entry.get().strip()
        if not new_deck_name:
            messagebox.showwarning("Warning", "Please enter a deck name")
            return
        try:
            db.update_deck_name(self.deck_id, new_deck_name)
            self.parent.update_deck_containers()
            self.cancel_event() 
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update deck: {str(e)}")

class QuizPage(BasePage):
    # initialises quiz page as subclass of basepage (inheritance)
    # initialises quiz page with master, user id, switch page
    def __init__(self, master, user_id, switch_page):
        super().__init__(master, user_id, switch_page)
        self.selected_deck = None
        self.deck_containers = {}
        self.master.db = Database()

        # creates header with "Quiz" title and controls on the right
        header = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 0))
        ctk.CTkLabel(header, text="Quiz", font=("Inter", 24, "bold"), text_color="black").pack(side="left")

        controls_frame = ctk.CTkFrame(header, fg_color="transparent")
        controls_frame.pack(side="right")

        # creates deck search bar
        self.deck_search_input = ctk.StringVar()
        self.deck_search_entry = ctk.CTkEntry(
            controls_frame,
            textvariable=self.deck_search_input,
            placeholder_text="Search deck",
            placeholder_text_color="#D1D1D1",
            text_color="#000000",
            fg_color="white",
            border_color="#e5e7eb",
            width=150
        )
        self.deck_search_entry.pack(side="left", padx=(0, 20))

        # creates priority dropdown filter (all, High, Medium, Low)
        self.deck_priority_input = ctk.StringVar(value="all")
        self.deck_priority_dropdown = ctk.CTkOptionMenu(
            controls_frame,
            values=["all", "High", "Medium", "Low"],
            variable=self.deck_priority_input,
            width=120,
            fg_color="white",
            button_color="#F3F4F6",
            button_hover_color="#E5E7EB",
            text_color="#111827"
        )
        self.deck_priority_dropdown.pack(side="left", padx=(0, 20))

        # refresh deck list when filters are updated
        self.deck_search_input.trace_add("write", lambda *args: self.update_deck_containers())
        self.deck_priority_input.trace_add("write", lambda *args: self.update_deck_containers())

        # creates start quiz button (disabled by default)
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

        # adds horizontal separator
        separator = ctk.CTkFrame(self.main_content, height=1, fg_color="#E5E7EB")
        separator.pack(fill="x", padx=30, pady=(20, 0))

        # creates frame that holds deck selection info and deck containers
        self.selection_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.selection_frame.pack(fill="both", expand=True, padx=30, pady=20)

        # creates instruction label
        ctk.CTkLabel(
            self.selection_frame,
            text="Select a deck to quiz yourself on",
            font=("Inter", 16, "bold"),
            text_color="black"
        ).pack(anchor="w", pady=(0, 10))

        # creates scrollable frame to show all available decks
        self.decks_frame = ctk.CTkScrollableFrame(
            self.selection_frame,
            fg_color="transparent",
            scrollbar_button_color="#E5E7EB",
            scrollbar_button_hover_color="#D1D5DB"
        )
        self.decks_frame.pack(fill="both", expand=True)
        self.decks_frame.grid_columnconfigure((0, 1), weight=1, pad=20)

        self.update_deck_containers()

    # updates the deck containers displayed on screen
    def update_deck_containers(self):
        for widget in self.decks_frame.winfo_children():
            widget.destroy()
        self.deck_containers = {}

        for i in range(3):
            self.decks_frame.grid_columnconfigure(i, weight=1, uniform="deck_col")

        decks = db.get_decks(self.user_id)
        deck_containers = []

        # builds list of decks with avg_ef and card count
        for deck_id, deck_name in decks:
            cards = db.get_cards(deck_id)
            if cards:
                total_ef = sum(db.get_card_easiness(self.user_id, c[0]) for c in cards)
                avg_ef = total_ef / len(cards)
            else:
                avg_ef = 2.5
            card_count = db.get_card_count(deck_id)
            deck_containers.append((deck_id, deck_name, avg_ef, card_count))

        # applies deck name search filter
        search_query = self.deck_search_input.get().lower().strip()
        if search_query:
            deck_containers = [d for d in deck_containers if search_query in d[1].lower()]

        # applies priority filter using ef values
        priority_filter = self.deck_priority_input.get().lower()
        if priority_filter != "all":
            if priority_filter == "high":
                deck_containers = [d for d in deck_containers if d[2] < 2.0]
            elif priority_filter == "medium":
                deck_containers = [d for d in deck_containers if 2.0 <= d[2] < 2.5]
            elif priority_filter == "low":
                deck_containers = [d for d in deck_containers if d[2] >= 2.5]

        # if no decks match, show message
        if not deck_containers:
            no_decks = ctk.CTkFrame(self.decks_frame, fg_color="transparent")
            no_decks.pack(fill="both", expand=True)
            ctk.CTkLabel(
                no_decks,
                text="No decks found",
                font=("Inter", 16, "bold"),
                text_color="#4B5563"
            ).pack(expand=True, pady=50)
            return

        # sort decks using BST based on ef values (lowest ef = higher priority)
        from graph import DeckNode, insert_node, in_order
        root = None
        for d in deck_containers:
            node = DeckNode(deck_id=d[0], deck_name=d[1], avg_ef=d[2], card_count=d[3])
            root = insert_node(root, node)
        sorted_nodes = in_order(root)

        # displays each deck in a 3-column grid
        row, col = 0, 0
        for node in sorted_nodes:
            deck_container = DeckContainer(
                self.decks_frame,
                deck_id=node.deck_id,
                deck_name=node.deck_name,
                card_count=node.card_count,
                avg_ef=node.avg_ef,
                edit_callback=None,
                delete_callback=None
            )
            deck_container.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            self.deck_containers[node.deck_id] = deck_container

            col += 1
            if col == 3:
                col = 0
                row += 1

        self.start_button.configure(state="normal" if self.selected_deck is not None else "disabled")

    # toggles which deck is selected (only one deck can be selected at a time)
    def toggle_deck(self, deck_id, selected):
        if selected:
            if self.selected_deck is not None and self.selected_deck != deck_id:
                prev_container = self.deck_containers.get(self.selected_deck)
                if prev_container:
                    prev_container.selected = False
                    prev_container.checkbox.deselect()
                    prev_container.configure(fg_color="white")
            self.selected_deck = deck_id
        else:
            if self.selected_deck == deck_id:
                self.selected_deck = None

        self.start_button.configure(state="normal" if self.selected_deck is not None else "disabled")

    # starts the quiz with the selected deck
    def start_quiz(self):
        if self.selected_deck is None:
            messagebox.showwarning("Warning", "Please select a deck")
            return
        for widget in self.master.winfo_children():
            widget.destroy()

        QuizSession(self.master, self.user_id, self.selected_deck, self.switch_page)
class QuizSession(ctk.CTkFrame):
    def __init__(self, master, user_id, deck_id, switch_page):
        super().__init__(master, corner_radius=0, fg_color="white")
        self.pack(fill="both", expand=True)
        self.user_id = user_id
        self.deck_id = deck_id
        self.switch_page = switch_page
        self.master.db = Database()

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

        # answer area (hidden until "Show answer")
        self.answer_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.answer_label = ctk.CTkLabel(self.answer_frame, text="", font=("Inter", 16), text_color="black", wraplength=600)
        self.answer_label.pack(pady=20)

        self.show_answer_btn = ctk.CTkButton(
            self.content, text="Show answer", width=120, height=32, corner_radius=16,
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
            if quality in (0, 1):
                # Very Hard or Hard → Red styling
                button_fg = "#FEE2E2"
                button_text = "#DC2626"
                button_hover = "#FECaCa"
            else:
                # Medium, Easy, Very Easy → Neutral styling
                button_fg = "#F3F4F6"
                button_text = "black"
                button_hover = "#E5E7EB"

            btn = ctk.CTkButton(
                self.rating_frame,
                text=text,
                width=120,
                height=32,
                corner_radius=16,
                fg_color=button_fg,
                text_color=button_text,
                hover_color=button_hover,
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

        # Hide answer and rating; show "Show answer" button.
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
            ("Correct answers", f"{self.correct_count}"),
            ("Wrong answers", f"{wrong}"),
            ("accuracy", f"{accuracy:.1f}%"),
            ("Total Time", f"{self.total_time:.1f}s"),
            ("avg Time/Card", f"{(self.total_time / total_cards):.1f}s" if total_cards else "0s")
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

class AnalyticsPage(BasePage):
    def __init__(self, master, user_id, switch_page):
        super().__init__(master, user_id, switch_page)
        self.user_id = user_id

        self.stats = self.db.get_quiz_stats(self.user_id)
        self.deck_expanded = {}
        self.master.db = Database()

        # Header
        header = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 0))
        ctk.CTkLabel(
            header,
            text="analytics",
            font=("Inter", 24, "bold"),
            text_color="black"
        ).pack(side="left")

        separator = ctk.CTkFrame(self.main_content, height=1, fg_color="#E5E7EB")
        separator.pack(fill="x", padx=30, pady=(10, 0))

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

    #############################################
    # 1) Overall Stats (3x2 layout)
    #############################################
    def create_overall_stats_section(self):
        container = ctk.CTkFrame(
            self.content_scroll,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color="#E5E7EB"
        )
        container.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            container,
            text="Overall Statistics",
            font=("Inter", 18, "bold"),
            text_color="#111827"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        parent_frame = ctk.CTkFrame(container, fg_color="white")
        parent_frame.pack(fill="x", padx=20, pady=(0, 15))

        total_sessions = self.stats.get("total_sessions", 0)
        total_reviewed = self.stats.get("total_reviewed", 0)
        total_correct = self.stats.get("total_correct", 0)
        overall_accuracy = self.stats.get("overall_accuracy", 0.0)
        total_time = self.stats.get("total_time", 0.0)
        avg_time_card = self.stats.get("overall_avg_time_per_card", 0.0)

        layout = [
            ("Total Sessions", str(total_sessions), "📊"),
            ("Total Cards Reviewed", str(total_reviewed), "📄"),
            ("Total Correct answers", str(total_correct), "✅"),
            ("Overall accuracy", f"{overall_accuracy:.1f}%", "🎯"),
            ("Total Quiz Time", f"{total_time:.1f}s", "⏱️"),
            ("avg Time/Card", f"{avg_time_card:.1f}s", "⚡"),
        ]

        row_count = 3
        col_count = 2
        idx = 0
        for r in range(row_count):
            rowf = ctk.CTkFrame(parent_frame, fg_color="white")
            rowf.pack(fill="x", pady=5)
            rowf.grid_columnconfigure(0, weight=1, uniform="stats_col")
            rowf.grid_columnconfigure(1, weight=1, uniform="stats_col")
            for c in range(col_count):
                if idx < len(layout):
                    label_text, val, icon = layout[idx]
                    self.create_stat_card(rowf, label_text, val, icon, c)
                    idx += 1

    def create_stat_card(self, parent, label_text, value_text, icon, col_index):
        card = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color="#E5E7EB"
        )
        card.grid(row=0, column=col_index, padx=5, sticky="nsew")
        inner = ctk.CTkFrame(card, fg_color="white")
        inner.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(inner, text=icon, font=("Inter", 18), text_color="#4B5563").pack(anchor="w")
        ctk.CTkLabel(inner, text=label_text, font=("Inter", 12), text_color="#4B5563").pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(inner, text=value_text, font=("Inter", 20, "bold"), text_color="#111827").pack(anchor="w", pady=(5, 0))

    #############################################
    # 2) Deck Performance (Sorted Descending)
    #############################################
    def create_deck_performance_section(self):
        container = ctk.CTkFrame(
            self.content_scroll,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color="#E5E7EB"
        )
        container.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            container,
            text="Deck Performance",
            font=("Inter", 18, "bold"),
            text_color="#111827"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        # Get decks, compute performance, sort descending
        decks = self.db.get_decks(self.user_id)
        deck_containers = []
        for deck_id, deck_name in decks:
            perf = self.db.get_deck_performance_score(self.user_id, deck_id)
            deck_containers.append((deck_id, deck_name, perf))

        # Sort by perf descending
        deck_containers.sort(key=lambda x: x[2], reverse=True)

        for deck_id, deck_name, perf in deck_containers:
            d_stats = self.db.get_deck_stats(self.user_id, deck_id)

            deck_card = ctk.CTkFrame(
                container,
                fg_color="white",
                corner_radius=8,
                border_width=1,
                border_color="#E5E7EB"
            )
            deck_card.pack(fill="x", padx=20, pady=5)

            row = ctk.CTkFrame(deck_card, fg_color="white")
            row.pack(fill="x", padx=15, pady=10)

            ctk.CTkLabel(
                row,
                text=deck_name,
                font=("Inter", 14, "bold"),
                text_color="#111827"
            ).pack(side="left")

            score_color = "#10B981"
            if perf < 50:
                score_color = "#DC2626"
            elif perf < 75:
                score_color = "#F59E0B"

            ctk.CTkLabel(
                row,
                text=f"{perf:.1f}/100",
                font=("Inter", 14, "bold"),
                text_color=score_color
            ).pack(side="right", padx=(10, 0))

            view_btn = ctk.CTkButton(
                row,
                text="View Details",
                width=100,
                height=32,
                corner_radius=16,
                fg_color="#F3F4F6",
                text_color="black",
                hover_color="#E5E7EB",
                command=lambda d_id=deck_id: self.toggle_deck_details(d_id)
            )
            view_btn.pack(side="right", padx=(10, 0))

            details_frame = ctk.CTkFrame(
                deck_card,
                fg_color="white",
                corner_radius=8,
                border_width=1,
                border_color="#E5E7EB"
            )
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
                ("Correct answers", f"{d_stats.get('total_correct', 0)}", "✅"),
                ("accuracy", f"{d_stats.get('accuracy', 0):.1f}%", "🎯"),
                ("Total Time (This Deck)", f"{d_stats.get('total_time', 0):.1f}s", "⏱️"),
                ("avg Time/Card", f"{d_stats.get('avg_time_per_card', 0):.1f}s", "⚡"),
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

    #############################################
    # 3) Graph Controls (Date Range + Previous X)
    #############################################
    def create_graph_controls(self):
        graph_box = ctk.CTkFrame(
            self.content_scroll,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color="#E5E7EB"
        )
        graph_box.pack(fill="both", expand=True, pady=(0, 20))

        ctk.CTkLabel(
            graph_box,
            text="Performance Graphs",
            font=("Inter", 18, "bold"),
            text_color="#111827"
        ).pack(anchor="w", padx=20, pady=(15, 5))

        controls = ctk.CTkFrame(graph_box, fg_color="white")
        controls.pack(fill="x", padx=20, pady=(0, 5))

        # Deck selection
        decks = self.db.get_decks(self.user_id)
        self.deck_options = {}
        deck_names = []
        for d_id, d_name in decks:
            self.deck_options[d_name] = d_id
            deck_names.append(d_name)
        self.selected_deck_name = ctk.StringVar(value=deck_names[0] if deck_names else "")
        self.deck_menu = ctk.CTkOptionMenu(
            controls,
            values=deck_names,
            variable=self.selected_deck_name,
            width=140,
            corner_radius=8,
            fg_color="white",
            button_color="#F3F4F6",
            button_hover_color="#E5E7EB",
            text_color="#111827"
        )
        self.deck_menu.pack(side="left", padx=(0, 20))

        # Metric selection
        self.selected_graph = ctk.StringVar(value="accuracy Over Time")
        self.graph_menu = ctk.CTkOptionMenu(
            controls,
            values=["accuracy Over Time", "avg Time Per Card", "Cumulative Retention"],
            variable=self.selected_graph,
            width=160,
            corner_radius=8,
            fg_color="white",
            button_color="#F3F4F6",
            button_hover_color="#E5E7EB",
            text_color="#111827"
        )
        self.graph_menu.pack(side="left", padx=(0, 20))

        # Start Date Entry (DD-MM-YYYY)
        self.start_date_label = ctk.CTkLabel(
            controls,
            text="Start (DD-MM-YYYY):",
            font=("Inter", 12),
            text_color="black"
        )
        self.start_date_label.pack(side="left", padx=(0, 5))

        default_start = (datetime.today() - timedelta(days=30)).strftime("%d-%m-%Y")
        self.start_date_entry = ctk.CTkEntry(
            controls,
            width=110,
            placeholder_text="DD-MM-YYYY",
            fg_color="#F3F4F6",
            text_color="black",
            border_width=0,
            corner_radius=0
        )
        self.start_date_entry.pack(side="left", padx=(0, 20))

        # End Date Entry (DD-MM-YYYY)
        self.end_date_label = ctk.CTkLabel(
            controls,
            text="End (DD-MM-YYYY):",
            font=("Inter", 12),
            text_color="black"
        )
        self.end_date_label.pack(side="left", padx=(0, 5))

        default_end = datetime.today().strftime("%d-%m-%Y")
        self.end_date_entry = ctk.CTkEntry(
            controls,
            width=110,
            placeholder_text="DD-MM-YYYY",
            fg_color="#F3F4F6",
            text_color="black",
            border_width=0,
            corner_radius=0
        )
        self.end_date_entry.pack(side="left", padx=(0, 20))


        # Show Graph button
        show_btn = ctk.CTkButton(
            controls,
            text="Show Graph",
            width=100,
            height=32,
            corner_radius=30,
            font=("Inter", 14),
            fg_color="#F3F4F6",
            text_color="black",
            hover_color="#E5E7EB",
            command=self.show_graph
        )
        show_btn.pack(side="left")

        # Graph display frame
        self.graph_display_frame = ctk.CTkFrame(graph_box, fg_color="white", corner_radius=8)
        self.graph_display_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
    def parse_date_fields(self):
        """
        Reads the start_date_entry and end_date_entry (DD-MM-YYYY).
        Returns (start_date, end_date) as date objects.
        Defaults if blank or invalid:
         - start_date -> 30 days ago
         - end_date -> today
        """
        start_str = self.start_date_entry.get().strip()
        end_str = self.end_date_entry.get().strip()

        # Default fallback
        default_start_date = datetime.today().date() - timedelta(days=30)
        default_end_date = datetime.today().date()

        # Parse start
        try:
            if not start_str:
                start_date = default_start_date
            else:
                start_date = datetime.strptime(start_str, "%d-%m-%Y").date()
        except:
            start_date = default_start_date

        # Parse end
        try:
            if not end_str:
                end_date = default_end_date
            else:
                end_date = datetime.strptime(end_str, "%d-%m-%Y").date()
        except:
            end_date = default_end_date

        if end_date < start_date:
            # swap if user typed them reversed
            start_date, end_date = end_date, start_date

        return (start_date, end_date)

    #############################################
    # 4) show_graph (Missing days => None)
    #############################################
    def show_graph(self):
        for w in self.graph_display_frame.winfo_children():
            w.destroy()

        deck_name = self.selected_deck_name.get()
        if deck_name not in self.deck_options:
            self.show_no_data_message()
            return

        deck_id = self.deck_options[deck_name]
        graph_type = self.selected_graph.get()

        # always day grouping, step=1
        group_by = "day"
        group_step = 1

        # Fetch data from DB (labels in "YYYY-MM-DD")
        if graph_type == "accuracy Over Time":
            labels, values = self.db.get_deck_accuracy_over_time(
                self.user_id, deck_id, group_by=group_by, group_step=group_step
            )
            ylabel = "accuracy (%)"
        elif graph_type == "avg Time Per Card":
            labels, values = self.db.get_deck_avg_time_over_time(
                self.user_id, deck_id, group_by=group_by, group_step=group_step
            )
            ylabel = "avg Time (s)"
        else:
            labels, values = self.db.get_deck_cumulative_retention(
                self.user_id, deck_id, group_by=group_by, group_step=group_step
            )
            ylabel = "Cumulative Retention (%)"

        if not labels:
            self.show_no_data_message()
            return

        # Parse user date fields
        start_date, end_date = self.parse_date_fields()

        # create a dict day_value_map from the DB data
        # Key: date object, Value: float
        day_value_map = {}
        for lb, val in zip(labels, values):
            try:
                d = datetime.strptime(lb, "%Y-%m-%d").date()
                day_value_map[d] = val
            except:
                continue

        # create a list of all dates in the user range
        all_dates = []
        delta = (end_date - start_date).days
        if delta < 0:
            # If for some reason the end_date is earlier, no data
            self.show_no_data_message()
            return

        for i in range(delta + 1):
            day = start_date + timedelta(days=i)
            all_dates.append(day)

        # For each date in all_dates, check if day_value_map has data
        # If not, store None
        all_values = []
        for d in all_dates:
            if d in day_value_map:
                all_values.append(day_value_map[d])
            else:
                all_values.append(None)

        # Format labels for X-axis as DD-MM-YYYY
        all_labels = [d.strftime("%d-%m-%Y") for d in all_dates]

        # Filter out the case where no valid days remain
        if not all_dates:
            self.show_no_data_message()
            return

        # Plot
        x_vals = list(range(len(all_dates)))
        width = 8 + max(0, (len(all_dates) - 10) * 0.3)
        height = 5

        plt.close("all")
        matplotlib.use("agg")
        plt.style.use("seaborn-v0_8-whitegrid")
        fig, ax = plt.subplots(figsize=(width, height))
        line_color = "#636ae8"

        # Plot line + scatter (None values => break in line)
        ax.plot(x_vals, all_values, color=line_color, linewidth=2, zorder=2)
        points = ax.scatter(x_vals, all_values, color=line_color, s=40, zorder=3, picker=True)

        title = f"{deck_name} - {graph_type}"
        ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
        ax.set_xlabel("Date", fontsize=12, labelpad=10)
        ax.set_ylabel(ylabel, fontsize=12, labelpad=10)
        ax.grid(True, linestyle="--", alpha=0.7)
        ax.set_xticks(x_vals)
        ax.set_xticklabels(all_labels, rotation=45, ha="right")

        if graph_type in ["accuracy Over Time", "Cumulative Retention"]:
            ax.set_ylim([0, 100])
        else:
            # auto-scale if we have any non-None values
            valid_vals = [v for v in all_values if v is not None]
            if valid_vals:
                mn = min(valid_vals)
                mx = max(valid_vals)
                if mn == mx:
                    mn = 0
                ax.set_ylim([mn * 0.8, mx * 1.2])

        fig.patch.set_facecolor("#F9FaFB")
        ax.set_facecolor("#FFFFFF")
        fig.tight_layout(pad=3.0)

        canvas = FigureCanvasTkagg(fig, master=self.graph_display_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Hover tooltips (skip None points)
        cursor = mplcursors.cursor(points, hover=True)

        @cursor.connect("add")
        def on_add(sel):
            x_val, y_val = sel.target
            idx = int(round(x_val))
            if 0 <= idx < len(all_dates):
                label_text = all_labels[idx]
                val = all_values[idx]
            else:
                label_text = str(idx)
                val = None

            if val is None:
                sel.annotation.set_text(f"{label_text}\nNo data")
            else:
                val_suffix = "%"
                if graph_type not in ["accuracy Over Time", "Cumulative Retention"]:
                    val_suffix = "s"
                sel.annotation.set_text(f"{label_text}\n{val:.1f}{val_suffix}")

            sel.annotation.set_bbox(
                dict(facecolor="#f3f4f6", edgecolor="none", alpha=0.9, boxstyle="round,pad=0.3")
            )

        self.add_graph_explanation(graph_type)

    def add_graph_explanation(self, graph_type):
        frame = ctk.CTkFrame(self.graph_display_frame, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=(5, 10))
        if graph_type == "accuracy Over Time":
            explanation = (
                "accuracy Over Time: The ratio of correct answers to total reviewed cards for each day, shown as a percentage."
            )
        elif graph_type == "avg Time Per Card":
            explanation = (
                "avg Time Per Card: The average number of seconds spent reviewing each card on that day."
            )
        else:
            explanation = (
                "Cumulative Retention: a running percentage calculated as cumulative correct answers divided by cumulative cards reviewed."
            )
        ctk.CTkLabel(
            frame,
            text=explanation,
            font=("Inter", 12),
            wraplength=600,
            justify="left",
            text_color="#4B5563"
        ).pack(anchor="w")

    def show_no_data_message(self):
        msg_frame = ctk.CTkFrame(self.graph_display_frame, fg_color="transparent")
        msg_frame.pack(fill="both", expand=True)
        ctk.CTkLabel(
            msg_frame,
            text="No data available for this selection",
            font=("Inter", 16, "bold"),
            text_color="#4B5563"
        ).pack(expand=True, pady=20)
        ctk.CTkLabel(
            msg_frame,
            text="Complete some quizzes with this deck to see performance data",
            font=("Inter", 14),
            text_color="#6B7280"
        ).pack(expand=True)

    #############################################
    # 5) Return to Dashboard
    #############################################
    def create_return_button(self):
        container = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        container.pack(side="bottom", fill="x", pady=(10, 0))
        ctk.CTkButton(
            container,
            text="Return to Dashboard",
            width=200,
            height=40,
            corner_radius=16,
            font=("Inter", 14),
            fg_color="#F3F4F6",
            text_color="black",
            hover_color="#E5E7EB",
            command=lambda: self.switch_page(
                __import__('app').DecksPage,
                user_id=self.user_id,
                switch_page=self.switch_page
            )
        ).pack(anchor="center", pady=20)

class SettingsPage(BasePage):
    def __init__(self, master, user_id, switch_page):
        super().__init__(master, user_id, switch_page)
        self.user_id = user_id
        self.switch_page = switch_page
        self.master.db = Database()

        
        try:
            user_info = db.get_user(self.user_id)
            current_email = user_info.get("email", "")
            current_username = user_info.get("username", "")
        except Exception as e:
            print(f"Error fetching user info: {e}")
            current_email = ""
            current_username = ""

        header = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))
        ctk.CTkLabel(
            header,
            text="account Settings",
            font=("Inter", 24, "bold"),
            text_color="black"
        ).pack(side="left")

        main_area = ctk.CTkFrame(self.main_content, fg_color="white")
        main_area.pack(fill="both", expand=True, padx=30, pady=20)

        center_container = ctk.CTkFrame(main_area, fg_color="transparent")
        center_container.place(relx=0.5, rely=0.3, anchor="center")

        self.settings_container = ctk.CTkFrame(
            center_container,
            fg_color="white",
            corner_radius=12,
            width=400,
            height=600
        )
        self.settings_container.pack(expand=True)
        self.settings_container.grid_propagate(False)

        ctk.CTkLabel(
            self.settings_container,
            text="Update Your account Details",
            font=("Inter", 20, "bold"),
            text_color="#000000"
        ).pack(pady=(30, 20))

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

        ctk.CTkButton(
            self.settings_container,
            text="Delete account",
            width=300,
            height=45,
            corner_radius=16,
            fg_color="#FEE2E2",
            text_color="#DC2626",
            hover_color="#FECaCa",
            command=self.delete_account
        ).pack(pady=10)

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

        if not new_email and not new_username and not new_password:
            self.status_label.configure(text="Please enter at least one field to update.")
            return

        
        try:
            updated = db.update_user(self.user_id, new_email, new_username, new_password)
            if updated:
                self.status_label.configure(text="Settings updated successfully.", text_color="#16a34a")
            else:
                self.status_label.configure(text="Failed to update settings.", text_color="#DC2626")
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="#DC2626")
        finally:
            db.close()
  

    def delete_account(self):
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            "are you sure you want to delete your account? This action cannot be undone."
        )
        if not confirm:
            return

        
        try:
            deleted = db.delete_user(self.user_id)
            if deleted:
                messagebox.showinfo("account Deleted", "Your account has been deleted.")
                from login import LoginPage
                self.switch_page(LoginPage)
            else:
                messagebox.showerror("Deletion Failed", "Failed to delete your account. Please try again later.")
        except Exception as e:
            messagebox.showerror("Error", f"an error occurred: {str(e)}")


