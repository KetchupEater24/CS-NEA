# external imports
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcursors


# my imports
from database import Database
from components import BasePage, BaseContainer, BaseDialog


class DecksPage(BasePage):
    # initialises decks page as a subclass of basepage (inheritance)
    def __init__(self, master, user_id, switch_page):
        super().__init__(master, user_id, switch_page)
        self.selected_decks = set()

        # header frame, container for the page title, search option and filter by priority option
        self.header_frame = ctk.CTkFrame(self.main_header_content, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=30, pady=(20, 0))

        # page title
        self.header_title = ctk.CTkLabel(
            self.header_frame,
            text="My Decks",
            font=("Inter", 24, "bold"),
            text_color="black"
        )
        self.header_title.pack(side="left")

        # filter frame, container for search and priority filter
        self.filter_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.filter_frame.pack(side="right", padx=10)

        # deck search input
        self.deck_search_input = ctk.StringVar()
        self.deck_search_entry_field = ctk.CTkEntry(
            self.filter_frame,
            textvariable=self.deck_search_input,
            placeholder_text="Search deck",
            placeholder_text_color="#D1D1D1",
            text_color="#000000",
            fg_color="white",
            border_color="#e5e7eb",
            width=200
        )
        self.deck_search_entry_field.pack(side="left", padx=5)

        # deck priority filter dropdown
        self.deck_priority_filter_selection = ctk.StringVar(value="All")
        self.deck_priority_filter_menu = ctk.CTkOptionMenu(
            self.filter_frame,
            values=["All", "High", "Medium", "Low"],
            variable=self.deck_priority_filter_selection,
            width=120,
            fg_color="white",
            button_color="#F3F4F6",
            button_hover_color="#E5E7EB",
            text_color="#111827"
        )
        self.deck_priority_filter_menu.pack(side="left", padx=5)

        # trace_add listens for changes in search and filter and calls update_deck_list accordingly
        self.deck_search_input.trace_add("write", lambda *args: self.update_deck_list())
        self.deck_priority_filter_selection.trace_add("write", lambda *args: self.update_deck_list())

        # buttons frame, holds the add button and delete selected button on the right side of the header frame
        self.buttons_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.buttons_frame.pack(side="right")

        self.add_button = ctk.CTkButton(
            self.buttons_frame,
            text="+ Add",
            width=70,
            height=32,
            corner_radius=16,
            fg_color="#F3F4F6",
            text_color="black",
            hover_color="#E5E7EB",
            command=self.add_deck
        )
        self.add_button.pack(side="left", padx=5)

        self.delete_selected_button = ctk.CTkButton(
            self.buttons_frame,
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
        self.delete_selected_button.pack(side="left", padx=5)

        # separator, seperates header from the decks frame below
        self.separator = ctk.CTkFrame(self.main_header_content, height=1, fg_color="#E5E7EB")
        self.separator.pack(fill="x", padx=30, pady=(20, 0))

        # decks frame, scrollable area to display deck containers
        self.decks_frame = ctk.CTkScrollableFrame(
            self.main_header_content,
            fg_color="transparent",
            scrollbar_button_color="#E5E7EB",
            scrollbar_button_hover_color="#D1D5DB"
        )
        self.decks_frame.pack(fill="both", expand=True, padx=30, pady=20)
        self.decks_frame.grid_columnconfigure((0, 1, 2), weight=1, pad=10)

        # calls update_deck_list to show decks, when decks  page is shown
        # is used whenever a change happens to decks, such as deleting a deck
        self.update_deck_list()

    def update_deck_list(self):
        # clear current deck containers
        for widget in self.decks_frame.winfo_children():
            widget.destroy()

        db = Database()
        deck_list = []
        decks = db.get_decks(self.user_id)

        # build deck_list as tuples with following, (deck_id, deck_name, avg_ef, card_count)
        for deck_id, deck_name in decks:
            # gets all cards for a certain deck from database
            cards = db.get_cards(deck_id)
            if cards:
                # calculates avg_ef of deck by doing total_ef/number of cards
                total_ef = sum(db.get_card_easiness(self.user_id, c[0]) for c in cards)
                avg_ef = total_ef / len(cards)
            else:
                # if cards dont exist defaults to ef of 2.5
                avg_ef = 2.5
            # retrieves number of cards in a deck
            card_count = db.get_card_count(deck_id)
            
            deck_list.append((deck_id, deck_name, avg_ef, card_count))

        # gets the user input from the search field, makes it lowercase and strips whitespace
        search_query = self.deck_search_input.get().lower().strip()
        if search_query:
            filtered_deck_list = []
            # iterates through deck list
            for deck in deck_list:
                # makes deck name lower case
                deck_name = deck[1].lower()
                # if any characters in the search query are in deck_name, 
                # append that deck to filtered decks and make deck_list equal to filtered decks
                if search_query in deck_name:
                    filtered_deck_list.append(deck)
            # assigns deck list to the now filtered deck list
            deck_list = filtered_deck_list

        # filter by priority (using avg_ef)
        priority_filter = self.deck_priority_filter_selection.get().lower()
        # if a priority is selected (anything but "all")
        if priority_filter != "all":
            filtered_deck_list = []
            # if high, then only append decks with avg_ef less than 2
            if priority_filter == "high":
                for deck in deck_list:
                    if deck[2] < 2.0:
                        filtered_deck_list.append(deck)
            # if medium, then only append decks with avg_ef between 2 and 2.5, including 2
            elif priority_filter == "medium":
                for deck in deck_list:
                    if 2.0 <= deck[2] < 2.5:
                        filtered_deck_list.append(deck)
            # if low, then only show append with avg_ef more than or equal to 2.5
            elif priority_filter == "low":
                for deck in deck_list:
                    if deck[2] >= 2.5:
                        filtered_deck_list.append(deck)
            # assigns deck_list to the now filtered deck list
            deck_list = filtered_deck_list

        # if user has no decks, then display a message
        if not deck_list:
            no_decks_frame = ctk.CTkFrame(self.decks_frame, fg_color="transparent")
            no_decks_frame.pack(fill="both", expand=True)
            ctk.CTkLabel(no_decks_frame, text="No decks found", font=("Inter", 16, "bold"),
                         text_color="#4B5563").pack(expand=True, pady=50)
            return

        # sort decks using BST (binary search tree) (based on avg_ef)
        # how this works is explained in graph.py
        from graph import DeckNode, insert_node, in_order
        root = None
        for deck in deck_list:
            node = DeckNode(deck_id=deck[0], deck_name=deck[1], avg_ef=deck[2], card_count=deck[3])
            root = insert_node(root, node)
        sorted_nodes = in_order(root)

        # instantiate deck container for each deck to be displayed
        row, col = 0, 0
        for node in sorted_nodes:
            deck_container = DeckContainer(
            self.decks_frame, 
            deck_id=node.deck_id,
            deck_name=node.deck_name, 
            card_count=node.card_count,
            selection_callback=self.toggle_deck_selection,
            avg_ef=node.avg_ef, 
            edit_callback=self.edit_deck,
            delete_callback=self.delete_deck)
            deck_container.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            col += 1
            if col == 3:
                col = 0
                row += 1

    # calls add deck dialog which adds deck to database and updates deck list
    def add_deck(self):
        AddDeckDialog(self)
        self.update_deck_list()
        self.sidebar.update_deck_list()

    # calls edit deck dialog which allows to edit an existing deck and udpates deck list
    def edit_deck(self, deck_id):
        EditDeckDialog(self, deck_id)
        self.update_deck_list()
        self.sidebar.update_deck_list()
        
    # allows to delete a deck from database and update deck list
    def delete_deck(self, deck_id):
        if messagebox.askyesno("Delete Deck", "Are you sure you want to delete this deck?"):
            db = Database()
            db.delete_deck(deck_id)
            self.update_deck_list()
            self.sidebar.update_deck_list()

    # adds any deck that is selected to selected decks and updates the styling of delete selected button to normal 
    # if deck(s) have been selected
    def toggle_deck_selection(self, deck_id, is_selected):
        if is_selected:
            self.selected_decks.add(deck_id)
        else:
            self.selected_decks.discard(deck_id)
        self.delete_selected_button.configure(state="normal" if self.selected_decks else "disabled")
        
    # deletes all selected decks upon clicking delete selected button
    def delete_selected_decks(self):
        if not self.selected_decks:
            return
        if messagebox.askyesno("Delete Decks", f"Are you sure you want to delete {len(self.selected_decks)} deck(s)?"):
            db = Database()
            for deck_id in self.selected_decks:
                db.delete_deck(deck_id)
            self.selected_decks.clear()
            self.update_deck_list()
            if hasattr(self, 'sidebar'):
                self.sidebar.update_deck_list()
            self.delete_selected_button.configure(state="disabled")

class DeckContainer(BaseContainer):
    # initialises deck cotnainer as subclass of base container (inheritance)
    def __init__(self, master, deck_id, deck_name, card_count, selection_callback, avg_ef, edit_callback, delete_callback):
        super().__init__(master)
        self.deck_id = deck_id
        self.selection_callback = selection_callback 
        self.selected = False
        self.avg_ef = avg_ef
        self.edit_callback = edit_callback
        self.delete_callback = delete_callback

        # main container for the deck content
        self.deck_container = ctk.CTkFrame(self, fg_color="transparent")
        self.deck_container.pack(fill="both", expand=True, padx=20, pady=20)

        # frame to display deck information on the left side, like priority, card count, etc.
        self.info_frame = ctk.CTkFrame(self.deck_container, fg_color="transparent")
        self.info_frame.pack(side="left", fill="both", expand=True)

        # label to display the deck name in bold text
        ctk.CTkLabel(
            self.info_frame,
            text=deck_name,
            font=("Inter", 16, "bold"),
            text_color="black"
        ).pack(anchor="w")

        # label to show the number of cards in the deck
        ctk.CTkLabel(
            self.info_frame,
            text=f"{card_count} cards",
            font=("Inter", 14),
            text_color="#6B7280"
        ).pack(anchor="w", pady=(5, 0))

        # get available for review count from database
        db = Database()
        if hasattr(self.selection_callback, '__self__'):
            # self.selection_callback is a reference to toggle_deck_selection method in deckspage
            # toggle_deck_selection's __self__ attribute refers to the decks page, so it allows access to 
            # user_id without needing to explicitly state it in deck container
            available_for_review = db.get_available_for_review(self.selection_callback.__self__.user_id, deck_id)
        else:
            # if selection_callback does not have an attribute __self__ that refers to the decks page, default to 0
            available_for_review = 0
        
        # label to display how many cards are available for review
        ctk.CTkLabel(
            self.info_frame,
            text=f"{available_for_review} available for review",
            font=("Inter", 12),
            text_color="#DC2626"
        ).pack(anchor="w", pady=(5, 0))

        # determine deck priority based on average ef value
        if self.avg_ef < 2.0:
            priority_text = "High Priority"
            tag_color = "red"
        elif self.avg_ef < 2.5:
            priority_text = "Medium Priority"
            tag_color = "orange"
        else:
            priority_text = "Low Priority"
            tag_color = "green"
        # label to display the deck priority
        ctk.CTkLabel(
            self.info_frame,
            text=priority_text,
            font=("Inter", 12, "bold"),
            text_color=tag_color
        ).pack(anchor="w", pady=(5, 0))

        # if both edit and delete callbacks are provided, create a button container
        if self.edit_callback is not None and self.delete_callback is not None:
            buttons_container = ctk.CTkFrame(self.deck_container, fg_color="transparent")
            buttons_container.pack(side="bottom", fill="x", pady=(10, 0))
            # edit button to trigger the edit callback for the deck
            ctk.CTkButton(
                buttons_container,
                text="Edit",
                width=70,
                height=32,
                corner_radius=16,
                fg_color="#F3F4F6",
                text_color="black",
                hover_color="#E5E7EB",
                command=lambda: self.edit_callback(self.deck_id)
            ).pack(side="left", padx=(5, 2), pady=5)
            # delete button to trigger the delete callback for the deck
            ctk.CTkButton(
                buttons_container,
                text="Delete",
                width=70,
                height=32,
                corner_radius=16,
                fg_color="#FEE2E2",
                text_color="#DC2626",
                hover_color="#FECACA",
                command=lambda: self.delete_callback(self.deck_id)
            ).pack(side="left", padx=(2, 5), pady=5)

        # checkbox on top right of container
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

    # called when the checkbox is toggled, updates the colour of checkbox to purple
    # def on_checkbox_toggle(self):
    #     self.selected = self.checkbox.get()
    #     if self.selection_callback:
    #         self.selection_callback(self.deck_id, self.selected)
    #     if self.selected:
    #         self.configure(fg_color="#F5F3FF")
    #         self.checkbox.configure(
    #             fg_color="#636ae8",
    #             checkmark_color="white"
    #         )
    #     else:
    #         self.configure(fg_color="white")
    #         self.checkbox.configure(
    #             fg_color="white",
    #             checkmark_color="black"
    #         )
            
    def on_checkbox_toggle(self):
        self.selected = self.checkbox.get()
        if self.selection_callback:
            self.selection_callback(self.deck_id, self.selected)
        if self.selected:
            self.configure(fg_color="#F5F3FF")
            self.checkbox.configure(fg_color="#636ae8", checkmark_color="white", hover_color="#636ae8")
        else:
            self.configure(fg_color="white")
            self.checkbox.configure(fg_color="white", checkmark_color="black", hover_color="white")

class CardContainer(BaseContainer):
    # initialises card container as subclass of base container (inheritance)
    def __init__(self, master, card_id, question, answer, edit_callback, delete_callback, ef, selection_callback=None):
        super().__init__(master)
        self.card_id = card_id
        self.selection_callback = selection_callback  # callback for handling selection state
        self.selected = False

        # main container for card content
        self.card_container = ctk.CTkFrame(self, fg_color="transparent")
        self.card_container.pack(fill="x", padx=20, pady=15)

        # label to display the card question in bold text
        ctk.CTkLabel(
            self.card_container,
            text=question,
            font=("Inter", 16, "bold"),
            text_color="black"
        ).pack(anchor="w")

        # label to display the card answer
        ctk.CTkLabel(
            self.card_container,
            text=answer,
            font=("Inter", 14),
            text_color="black"
        ).pack(anchor="w", pady=(5, 0))

        # priority indicator, determines card priority based on easiness factor (ef)
        if ef < 2.0:
            priority_text = "High Priority"
            color = "red"
        elif ef < 2.5:
            priority_text = "Medium Priority"
            color = "orange"
        else:
            priority_text = "Low Priority"
            color = "green"
        # label to show card priority
        ctk.CTkLabel(
            self.card_container,
            text=priority_text,
            font=("Inter", 12, "bold"),
            text_color=color
        ).pack(anchor="w", pady=(5, 10))

        # aligns buttons_frame to be on bottom of card
        buttons_frame = ctk.CTkFrame(self.card_container, fg_color="transparent")
        buttons_frame.pack(side="bottom", fill="x")
        # aligns buttons_container to be on the right of card (so now the buttons are on the bottom-right)
        buttons_container = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        buttons_container.pack(side="right", padx=5, pady=5)

        # edit button calls the edit callback for this card
        ctk.CTkButton(
            buttons_container,
            text="Edit",
            width=70,
            height=32,
            corner_radius=16,
            fg_color="#F3F4F6",
            text_color="black",
            hover_color="#E5E7EB",
            command=lambda: edit_callback(self.card_id)
        ).pack(side="left", padx=(5, 2))
        
        # delete button, calls the delete callback for this card
        ctk.CTkButton(
            buttons_container,
            text="Delete",
            width=70,
            height=32,
            corner_radius=16,
            fg_color="#FEE2E2",
            text_color="#DC2626",
            hover_color="#FECACA",
            command=lambda: delete_callback(self.card_id)
        ).pack(side="left", padx=(2, 5))

        # checkbox at top right
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

    # changes checkbox colour to purple on toggle
    # def on_checkbox_toggle(self):
    #     self.selected = self.checkbox.get()
    #     if self.selection_callback:
    #         self.selection_callback(self.card_id, self.selected)
    #     if self.selected:
    #         # self.configure(fg_color="#F5F3FF")
    #         self.checkbox.configure(
    #             fg_color="#636ae8",
    #             checkmark_color="white"
    #         )
    #     else:
    #         self.configure(fg_color="white")
    #         self.checkbox.configure(
    #             fg_color="white",
    #             checkmark_color="black",
    #             hover_color="white"
    #         )
    
    def on_checkbox_toggle(self):
        self.selected = self.checkbox.get()
        if self.selection_callback:
            self.selection_callback(self.card_id, self.selected)
        if self.selected:
            self.configure(fg_color="#F5F3FF")
            self.checkbox.configure(fg_color="#636ae8", checkmark_color="white", hover_color="#636ae8")
        else:
            self.configure(fg_color="white")
            self.checkbox.configure(fg_color="white", checkmark_color="black", hover_color="white")

class CardsPage(BasePage):
    def __init__(self, master, user_id, deck_id, switch_page):
        super().__init__(master, user_id, switch_page)
        self.deck_id = deck_id
        self.selected_cards = set()
        self.deck_info = self.db.get_deck_info(self.deck_id)

        # header frame, a container for deck title, card count, search, and filter by priority option
        self.header_frame = ctk.CTkFrame(self.main_header_content, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=30, pady=20)

        # page title (the deck name)
        self.deck_title_label = ctk.CTkLabel(
            self.header_frame,
            text=self.deck_info["name"],
            font=("Inter", 24, "bold"),
            text_color="black"
        )
        self.deck_title_label.pack(side="left")

        # card count label shows number of cards in the deck
        self.card_count_label = ctk.CTkLabel(
            self.header_frame,
            text=f"{self.deck_info['card_count']} cards",
            font=("Inter", 14),
            text_color="#6B7280"
        )
        self.card_count_label.pack(side="left", padx=(10, 0))

        # filter frame holds the search entry and priority dropdown
        self.filter_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.filter_frame.pack(side="right", padx=10)

        # card_search_input stores the users search text
        # card_search_entry_field makes the search box
        self.card_search_input = ctk.StringVar()
        self.card_search_entry_field = ctk.CTkEntry(
            self.filter_frame,
            textvariable=self.card_search_input,
            placeholder_text="Search card",
            placeholder_text_color="#D1D1D1",
            text_color="#000000",
            fg_color="white",
            border_color="#e5e7eb",
            width=200
        )
        self.card_search_entry_field.pack(side="left", padx=5)

        # card priority filter and dropdown menu (default selected valu eis All)
        self.card_priority_filter_selection = ctk.StringVar(value="All")
        self.card_priority_filter_menu = ctk.CTkOptionMenu(
            self.filter_frame,
            values=["All", "High", "Medium", "Low"],
            variable=self.card_priority_filter_selection,
            width=120,
            fg_color="white",
            button_color="#F3F4F6",
            button_hover_color="#E5E7EB",
            text_color="#111827"
        )
        self.card_priority_filter_menu.pack(side="left", padx=5)

        # trace_add listens for changes in search and filter and calls update_card_list accordingly
        self.card_search_input.trace_add("write", lambda *args: self.update_card_list())
        self.card_priority_filter_selection.trace_add("write", lambda *args: self.update_card_list())

        # delete selected cards button, which is initially disabled (only enabled if checkbox(es) clicked)
        self.delete_selected_button = ctk.CTkButton(
            self.header_frame,
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
        self.delete_selected_button.pack(side="right", padx=5)

        # add card button, which allows user to add card by calling add card
        # add card then opens a dialog to enter card info
        self.add_card_button = ctk.CTkButton(
            self.header_frame,
            text="+ Add Card",
            width=70,
            height=32,
            corner_radius=16,
            fg_color="#F3F4F6",
            text_color="black",
            hover_color="#E5E7EB",
            command=self.add_card
        )
        self.add_card_button.pack(side="right", padx=5)

        # cards frame, scrollable container for displaying card containers
        self.cards_frame = ctk.CTkScrollableFrame(
            self.main_header_content,
            fg_color="transparent",
            scrollbar_button_color="#E5E7EB",
            scrollbar_button_hover_color="#D1D5DB"
        )
        self.cards_frame.pack(fill="both", expand=True, padx=30, pady=20)

        # display cards initially
        self.update_card_list()

    # displays the cards in the scrollable cards frame
    def update_card_list(self):
        # clear existing card widgets from the scrollable frame
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        db = Database()
        card_list = []
        cards = db.get_cards(self.deck_id)
        
        # builds card_list as tuples with following, (card_id, question, answer, ef)
        # _ is deck_id which is ignoredS
        for card in cards:
            card_id, _, question, answer = card
            ef = db.get_card_easiness(self.user_id, card_id)
            card_list.append((card_id, question, answer, ef))

        # gets the user input from the search field, makes it lowercase and strips whitespace
        search_query = self.card_search_input.get().lower().strip()
        if search_query:
            filtered_card_list = []
            for card in card_list:
                # if any characters in the search query are in card[1] (which is the question), 
                # append that card to filtered card list and make card_list equal to filtered card list
                if search_query in card[1].lower():
                    filtered_card_list.append(card)
            card_list = filtered_card_list

        # filter card_list by priority (using easiness factor)
        priority_filter = self.card_priority_filter_selection.get().lower()
        # if a priority is selected (anything but "all")
        if priority_filter != "all":
            filtered_card_list = []
            # if high, then append cards with ef less than 2
            if priority_filter == "high":
                for card in card_list:
                    if card[3] < 2.0:
                        filtered_card_list.append(card)
            # if high, then append cards with ef between 2 and 2.5, including 2
            elif priority_filter == "medium":
                for card in card_list:
                    if 2.0 <= card[3] < 2.5:
                        filtered_card_list.append(card)
            # if low, then append cards with ef less than or equal to 2.5
            elif priority_filter == "low":
                for card in card_list:
                    if card[3] >= 2.5:
                        filtered_card_list.append(card)
            card_list = filtered_card_list

        # if user has no cards, display a message
        if not card_list:
            no_cards_frame = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
            no_cards_frame.pack(fill="both", expand=True)
            ctk.CTkLabel(
                no_cards_frame,
                text="No cards found",
                font=("Inter", 16, "bold"),
                text_color="#4B5563"
            ).pack(expand=True, pady=50)
            return

        # sort card_list using merge sort based on easiness factor (lower ef means higher priority)
        # sorts from lowest to highest ef (so highest to lowest priority)
        from misc import MiscFunctions
        sorted_cards = MiscFunctions.split(card_list)

        # instantiate card container for each card to be displayed
        for card in sorted_cards:
            card_container = CardContainer(
                self.cards_frame,
                card_id=card[0],
                question=card[1],
                answer=card[2],
                edit_callback=self.edit_card,
                delete_callback=self.delete_card,
                ef=card[3],
                selection_callback=self.toggle_card_selection
            )
            card_container.pack(fill="x", pady=10)

    # call add card dialog to add a card (with question and answer)
    def add_card(self):
        AddCardDialog(self, deck_id=self.deck_id)
        self.update_card_list()
    # call edit card dialog to edit card (it's question and answer)
    def edit_card(self, card_id):
        EditCardDialog(self, card_id)
        self.update_card_list()

    # deletes a card
    def delete_card(self, card_id):
        if messagebox.askyesno("Delete Card", "Are you sure you want to delete this card?"):
            self.db.delete_card(card_id)
            self.update_card_list()

    # adds any card that is selected to selected cards and updates the styling of delete selected button to normal 
    # if card(s) have been selected
    def toggle_card_selection(self, card_id, selected):
        if selected:
            self.selected_cards.add(card_id)
        else:
            self.selected_cards.discard(card_id)
        self.delete_selected_button.configure(state="normal" if self.selected_cards else "disabled")

    # deletes all selected decks upon clicking delete selected button
    def delete_selected_cards(self):
        if not self.selected_cards:
            return
        if messagebox.askyesno("Delete Cards", f"Are you sure you want to delete {len(self.selected_cards)} card(s)?"):
            for card_id in self.selected_cards:
                self.db.delete_card(card_id)
            self.selected_cards.clear()
            self.update_card_list()
            self.delete_selected_button.configure(state="disabled")

class EditCardDialog(BaseDialog):
    # initialise edit card dialog as subclass of basedialog (inheritance)
    def __init__(self, parent, card_id):
        # set dialog size for editing a card
        super().__init__(title="Edit Card", width=500, height=500)
        self.parent = parent
        self.card_id = card_id

        # fetch current card info from the database
        db = Database()
        card_info = db.get_card(card_id)
        current_question = card_info['question']
        current_answer = card_info['answer']

        # create dialog title (defined in basedialog)
        self.create_dialog_title("Edit Card")

        # create question section label
        ctk.CTkLabel(
            self.container,
            text="Question",
            font=("Inter", 14, "bold"),
            text_color="black"
        ).pack(fill="x", pady=(10, 5))
        
        # create textbox for the question
        self.question_entry = ctk.CTkTextbox(
            self.container,
            height=100,
            border_width=1,
            border_color="#E5E7EB",
            text_color="black",
            fg_color="white"
        )
        self.question_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.question_entry.insert("1.0", current_question)

        # create answer section label
        ctk.CTkLabel(
            self.container,
            text="Answer",
            font=("Inter", 14, "bold"),
            text_color="black"
        ).pack(fill="x", pady=(10, 5))
        
        # create textbox for the answer
        self.answer_entry = ctk.CTkTextbox(
            self.container,
            height=100,
            border_width=1,
            border_color="#E5E7EB",
            text_color="black",
            fg_color="white"
        )
        self.answer_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.answer_entry.insert("1.0", current_answer)


        # create save button (defined in basedialog)
        self.create_dialog_button("Save Card", self.save_card)
        self.wait_window()

    # when save card button clicked, call save_card to update the database with new card info
    def save_card(self):
        new_question = self.question_entry.get().strip()
        new_answer = self.answer_entry.get().strip()
        if not new_question or not new_answer:
            messagebox.showwarning("Warning", "Please fill in both question and answer")
            return
        try:
            db = Database()
            db.update_card(self.card_id, new_question, new_answer)
            # simply close the dialog; the calling page should update the cards list
            self.cancel_dialog_event()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update card: {str(e)}")

class AddCardDialog(BaseDialog):
    # initialise add card dialog as subclass of base dialog (inheritance)
    def __init__(self, parent, deck_id):
        # set dialog size for creating a new card
        super().__init__(title="New Card", width=500, height=500)
        self.parent = parent
        self.deck_id = deck_id
        # create title (defined in base dialog)
        self.create_dialog_title("New Card")

        # create question section label
        ctk.CTkLabel(
            self.container,
            text="Question",
            font=("Inter", 14, "bold"),
            text_color="black"
        ).pack(pady=(10, 5))
        # create textbox for the question
        self.question_entry = ctk.CTkTextbox(
            self.container,
            height=100,
            border_width=1,
            border_color="#E5E7EB",
            text_color="black",
            fg_color="white"
        )
        self.question_entry.pack(fill="x", padx=10, pady=(0, 10))

        # create answer section label
        ctk.CTkLabel(
            self.container,
            text="Answer",
            font=("Inter", 14, "bold"),
            text_color="black"
        ).pack(pady=(10, 5))
        
        # createtextbox for the answer
        self.answer_entry = ctk.CTkTextbox(
            self.container,
            height=100,
            border_width=1,
            border_color="#E5E7EB",
            text_color="black",
            fg_color="white"
        )
        self.answer_entry.pack(fill="x", padx=10, pady=(0, 10))

        # create save button (defined in base dialog)
        self.create_dialog_button("Save Card", self.save_card)
        self.wait_window()

    # when save card button clicked, call save_card to add the card to the database
    def save_card(self):
        question = self.question_entry.get().strip()
        answer = self.answer_entry.get().strip()
        if not question or not answer:
            messagebox.showwarning("Warning", "Please fill in both question and answer")
            return
        try:
            db = Database()
            db.create_card(self.deck_id, question, answer)
            # simply close the dialog; the calling page should update the cards list
            self.cancel_dialog_event()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create card: {str(e)}")

class EditDeckDialog(BaseDialog):
    # intiialise edit deck dialog as subclass of basedialog (inheritance)
    def __init__(self, parent, deck_id):
        # set dialog size
        super().__init__(title="Edit Deck", width=400, height=300)
        self.parent = parent
        self.deck_id = deck_id

        # fetch current deck name from the database
        db = Database()
        deck_info = db.get_deck_info(deck_id)
        current_deck_name = deck_info["name"]

        # create title (defined in base dialog)
        self.create_dialog_title("Edit Deck")

        # create label for deck name
        ctk.CTkLabel(
            self.container,
            text="Deck Name",
            font=("Inter", 14, "bold"),
            text_color="black"
        ).pack(fill="x", pady=(10, 5))

        # create input field, with current deck name in it (defined in base dialog)
        self.deck_entry = self.create_dialog_input_field(initial_value=current_deck_name)

        # create save button (defined in base dialog)
        self.create_dialog_button("Save Deck", self.save_deck)
        self.wait_window()

    # when save deck button clicked, call save_deck to update datebase with new deck info
    def save_deck(self):
        new_deck_name = self.deck_entry.get().strip()
        if not new_deck_name:
            messagebox.showwarning("Warning", "Please enter a deck name")
            return
        try:
            db = Database()
            db.update_deck_name(self.deck_id, new_deck_name)
            self.cancel_dialog_event()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update deck: {str(e)}")

class AddDeckDialog(BaseDialog):
    # initialise add deck dialog as subclass of basedialog (inheritance)
    def __init__(self, parent):
        # set dialog size
        super().__init__(title="New Deck", width=400, height=300)
        self.parent = parent 
        self.create_dialog_title("New Deck")
        ctk.CTkLabel(
            self.container,
            text="Enter deck name",
            font=("Inter", 14, "bold"),
            text_color="black"
        ).pack(pady=(10, 5))
        
        # create input field (defined in basedialog)
        self.deck_entry = self.create_dialog_input_field()
        # create add button (defined in base dialog)
        self.create_dialog_button("Save Deck", self.save_deck)
        self.wait_window()

    # when save deck button pressed, call save_deck to add the deck to database
    def save_deck(self):
        new_deck_name = self.deck_entry.get().strip()
        if not new_deck_name:
            messagebox.showwarning("Warning", "Please enter a deck name")
            return
        try:
            db = Database()
            db.create_deck(self.parent.user_id, new_deck_name)
            self.cancel_dialog_event()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create deck: {str(e)}")


class QuizPage(BasePage):
    # initialise quiz page as subclass of base page  (inheritance)
    def __init__(self, master, user_id, switch_page):
        super().__init__(master, user_id, switch_page)

        # create header frame (for title, start quiz button, search bar, etc.)
        self.header_frame = ctk.CTkFrame(self.main_header_content, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=30, pady=(20, 0))

        # page title
        self.header_title = ctk.CTkLabel(
            self.header_frame,
            text="Quiz",
            font=("Inter", 24, "bold"),
            text_color="black"
        )
        self.header_title.pack(side="left")

        # filter frame to hold priority selection and search field (works same way as it does in decks page)
        # refer to decks page for comments that explain the below code
        self.filter_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.filter_frame.pack(side="right", padx=10)
        
        self.deck_search_input = ctk.StringVar()
        self.deck_search_entry_field = ctk.CTkEntry(
            self.filter_frame,
            textvariable=self.deck_search_input,
            placeholder_text="Search deck",
            placeholder_text_color="#D1D1D1",
            text_color="#000000",
            fg_color="white",
            border_color="#e5e7eb",
            width=200
        )
        self.deck_search_entry_field.pack(side="left", padx=5)

        self.deck_priority_filter_selection = ctk.StringVar(value="All")
        self.deck_priority_filter_menu = ctk.CTkOptionMenu(
            self.filter_frame,
            values=["All", "High", "Medium", "Low"],
            variable=self.deck_priority_filter_selection,
            width=120,
            fg_color="white",
            button_color="#F3F4F6",
            button_hover_color="#E5E7EB",
            text_color="#111827"
        )
        self.deck_priority_filter_menu.pack(side="left", padx=5)
        
        self.deck_search_input.trace_add("write", lambda *args: self.update_deck_list())
        self.deck_priority_filter_selection.trace_add("write", lambda *args: self.update_deck_list())

        # start quiz button
        self.start_button = ctk.CTkButton(
            self.header_frame,
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
        self.start_button.pack(side="right", padx=(0, 10))

        # seperator, to seperate header from the main content of the page below
        self.separator = ctk.CTkFrame(self.main_header_content, height=1, fg_color="#E5E7EB")
        self.separator.pack(fill="x", padx=30, pady=(20, 0))

        # selection frame holds a label to tell the user to select decks for a quiz
        self.selection_frame = ctk.CTkFrame(self.main_header_content, fg_color="transparent")
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
        self.decks_frame.grid_columnconfigure((0, 1, 2), weight=1, pad=10)

        # calls update_deck_list to show decks, when quiz page is shown
        self.update_deck_list()

    # refer to decks page for comments explaining the below function
    def update_deck_list(self):
        for widget in self.decks_frame.winfo_children():
            widget.destroy()

        db = self.db
        deck_list = []
        decks = db.get_decks(self.user_id)
        for deck in decks:
            deck_id = deck[0]
            deck_name = deck[1]
            cards = db.get_cards(deck_id)
            if cards:
                total_ef = 0
                for c in cards:
                    total_ef += db.get_card_easiness(self.user_id, c[0])
                avg_ef = total_ef / len(cards)
            else:
                avg_ef = 2.5
            card_count = db.get_card_count(deck_id)
            deck_list.append((deck_id, deck_name, avg_ef, card_count))

        search_query = self.deck_search_input.get().lower().strip()
        if search_query:
            filtered_deck_list = []
            for deck in deck_list:
                if search_query in deck[1].lower():
                    filtered_deck_list.append(deck)
            deck_list = filtered_deck_list

        priority_filter = self.deck_priority_filter_selection.get().lower()
        if priority_filter != "all":
            filtered_deck_list = []
            if priority_filter == "high":
                for deck in deck_list:
                    if deck[2] < 2.0:
                        filtered_deck_list.append(deck)
            elif priority_filter == "medium":
                for deck in deck_list:
                    if 2.0 <= deck[2] < 2.5:
                        filtered_deck_list.append(deck)
            elif priority_filter == "low":
                for deck in deck_list:
                    if deck[2] >= 2.5:
                        filtered_deck_list.append(deck)
            deck_list = filtered_deck_list

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

        from graph import DeckNode, insert_node, in_order
        root = None
        for deck in deck_list:
            node = DeckNode(deck_id=deck[0], deck_name=deck[1], avg_ef=deck[2], card_count=deck[3])
            root = insert_node(root, node)
        sorted_nodes = in_order(root)

        row, col = 0, 0
        for node in sorted_nodes:
            deck_container = DeckContainer(
                self.decks_frame,
                deck_id=node.deck_id,
                deck_name=node.deck_name,
                card_count=node.card_count,
                selection_callback=self.toggle_deck_selection,
                avg_ef=node.avg_ef,
                edit_callback=None,
                delete_callback=None
            )
            deck_container.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            col += 1
            if col == 3:
                col = 0
                row += 1

   
    def toggle_deck_selection(self, deck_id, selected):
        for widget in self.decks_frame.winfo_children():
            if widget.deck_id == deck_id:
                widget.selected = selected
                if selected:
                    widget.configure(fg_color="#F5F3FF")
                    widget.checkbox.select()
                else:
                    widget.configure(fg_color="white")
                    widget.checkbox.deselect()
            else:
                widget.selected = False
                widget.configure(fg_color="white")
                widget.checkbox.deselect()
        any_selected = False
        for widget in self.decks_frame.winfo_children():
            if widget.selected:
                any_selected = True
                break
        self.start_button.configure(state="normal" if any_selected else "disabled")

    def start_quiz(self):
        # Find the selected deck by iterating over deck containers
        selected_deck_id = None
        for widget in self.decks_frame.winfo_children():
            if hasattr(widget, "selected") and widget.selected:
                selected_deck_id = widget.deck_id
                break
        if selected_deck_id is None:
            messagebox.showwarning("Warning", "Please select a deck")
            return
        # Clear the master and start the quiz session with the selected deck.
        for widget in self.master.winfo_children():
            widget.destroy()
        QuizSession(self.master, self.user_id, selected_deck_id, self.switch_page)

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

        self.show_answer_button = ctk.CTkButton(
            self.content, text="Show Answer", width=120, height=32, corner_radius=16,
            fg_color="#F3F4F6", text_color="black", hover_color="#E5E7EB", command=self.show_answer
        )
        self.show_answer_button.pack(pady=20)

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
                button_hover = "#FECACA"
            else:
                # Medium, Easy, Very Easy → Neutral styling
                button_fg = "#F3F4F6"
                button_text = "black"
                button_hover = "#E5E7EB"

            button = ctk.CTkButton(
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
            button.pack(side="left", padx=5)

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
        self.show_answer_button.pack(pady=20)

        card = self.cards[self.current_index]
        # card structure: (card_id, question, answer, next_review_date)
        self.current_card_id = card[0]
        self.question_label.configure(text=card[1])
        self.answer_label.configure(text=card[2])
        self.progress_label.configure(text=f"Card {self.current_index + 1}/{self.total_cards}")
        self.card_start_time = datetime.now()

    def show_answer(self):
        self.show_answer_button.pack_forget()
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
        self.db.update_spaced_rep(
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


class AnalyticsPage(BasePage):
    def __init__(self, master, user_id, switch_page):
        super().__init__(master, user_id, switch_page)
        self.db = Database()
        self.user_id = user_id

        self.stats = self.db.get_quiz_stats(self.user_id)
        self.deck_expanded = {}

        # Header
        header_frame = ctk.CTkFrame(self.main_header_content, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 0))
        ctk.CTkLabel(
            header_frame,
            text="Analytics",
            font=("Inter", 24, "bold"),
            text_color="black"
        ).pack(side="left")

        separator = ctk.CTkFrame(self.main_header_content, height=1, fg_color="#E5E7EB")
        separator.pack(fill="x", padx=30, pady=(10, 0))

        self.content_scroll = ctk.CTkScrollableFrame(
            self.main_header_content,
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
            ("Total Correct Answers", str(total_correct), "✅"),
            ("Overall Accuracy", f"{overall_accuracy:.1f}%", "🎯"),
            ("Total Quiz Time", f"{total_time:.1f}s", "⏱️"),
            ("Avg Time/Card", f"{avg_time_card:.1f}s", "⚡"),
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
        deck_list = []
        for deck_id, deck_name in decks:
            perf = self.db.get_deck_performance_score(self.user_id, deck_id)
            deck_list.append((deck_id, deck_name, perf))

        # Sort by perf descending
        deck_list.sort(key=lambda x: x[2], reverse=True)

        for deck_id, deck_name, perf in deck_list:
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

            view_button = ctk.CTkButton(
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
            view_button.pack(side="right", padx=(10, 0))

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
        self.selected_graph = ctk.StringVar(value="Accuracy Over Time")
        self.graph_menu = ctk.CTkOptionMenu(
            controls,
            values=["Accuracy Over Time", "Avg Time Per Card", "Cumulative Retention"],
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
        show_button = ctk.CTkButton(
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
        show_button.pack(side="left")

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

        # Always day grouping, step=1
        group_by = "day"
        group_step = 1

        # Fetch data from DB (labels in "YYYY-MM-DD")
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

        if not labels:
            self.show_no_data_message()
            return

        # Parse user date fields
        start_date, end_date = self.parse_date_fields()

        # Build a dict day_value_map from the DB data
        # Key: date object, Value: float
        day_value_map = {}
        for lb, val in zip(labels, values):
            try:
                d = datetime.strptime(lb, "%Y-%m-%d").date()
                day_value_map[d] = val
            except:
                continue

        # Build a list of all dates in the user range
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
        matplotlib.use("Agg")
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

        if graph_type in ["Accuracy Over Time", "Cumulative Retention"]:
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

        fig.patch.set_facecolor("#F9FAFB")
        ax.set_facecolor("#FFFFFF")
        fig.tight_layout(pad=3.0)

        canvas = FigureCanvasTkAgg(fig, master=self.graph_display_frame)
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
                if graph_type not in ["Accuracy Over Time", "Cumulative Retention"]:
                    val_suffix = "s"
                sel.annotation.set_text(f"{label_text}\n{val:.1f}{val_suffix}")

            sel.annotation.set_bbox(
                dict(facecolor="#f3f4f6", edgecolor="none", alpha=0.9, boxstyle="round,pad=0.3")
            )

        self.add_graph_explanation(graph_type)

    def add_graph_explanation(self, graph_type):
        frame = ctk.CTkFrame(self.graph_display_frame, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=(5, 10))
        if graph_type == "Accuracy Over Time":
            explanation = (
                "Accuracy Over Time: The ratio of correct answers to total reviewed cards for each day, shown as a percentage."
            )
        elif graph_type == "Avg Time Per Card":
            explanation = (
                "Avg Time Per Card: The average number of seconds spent reviewing each card on that day."
            )
        else:
            explanation = (
                "Cumulative Retention: A running percentage calculated as cumulative correct answers divided by cumulative cards reviewed."
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
        # Initialize BasePage (sets up sidebar, main_header_content, etc.)
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
        header_frame = ctk.CTkFrame(self.main_header_content, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 10))
        ctk.CTkLabel(
            header_frame,
            text="Account Settings",
            font=("Inter", 24, "bold"),
            text_color="black"
        ).pack(side="left")

        # Main content area (non-scrollable).
        main_area = ctk.CTkFrame(self.main_header_content, fg_color="white")
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
