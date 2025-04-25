# external imports
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime


# my imports
from components import BasePage, BaseContainer, BaseDialog

class DecksPage(BasePage):
    # initialises decks page as a subclass of basepage (inheritance)
    def __init__(self, master, user_id, switch_page, db):
        super().__init__(master, user_id, switch_page, db=db)
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

        deck_list = []
        decks = self.db.get_decks(self.user_id)

        # build deck_list as tuples with following, (deck_id, deck_name, avg_ef, card_count)
        for deck_id, deck_name in decks:
            # gets all cards for a certain deck from database
            cards = self.db.get_cards(deck_id)
            if cards:
                # calculates avg_ef of deck by doing total_ef/number of cards
                total_ef = sum(self.db.get_card_easiness(self.user_id, c[0]) for c in cards)
                avg_ef = total_ef / len(cards)
            else:
                # if cards dont exist defaults to ef of 2.5
                avg_ef = 2.5
            # retrieves number of cards in a deck
            card_count = self.db.get_card_count(deck_id)
            
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
                user_id=self.user_id,
                deck_name=node.deck_name, 
                card_count=node.card_count,
                selection_callback=self.toggle_deck_selection,
                avg_ef=node.avg_ef, 
                edit_callback=self.edit_deck,
                delete_callback=self.delete_deck,
                db=self.db
            )
            deck_container.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            col += 1
            if col == 3:
                col = 0
                row += 1

    # calls add deck dialog which adds deck to database and updates deck list
    def add_deck(self):
        AddDeckDialog(self, db=self.db)
        self.update_deck_list()
        self.sidebar.update_deck_list()

    # calls edit deck dialog which allows to edit an existing deck and udpates deck list
    def edit_deck(self, deck_id):
        EditDeckDialog(self, deck_id, db=self.db)
        self.update_deck_list()
        self.sidebar.update_deck_list()
        
    # allows to delete a deck from database and update deck list
    def delete_deck(self, deck_id):
        if messagebox.askyesno("Delete Deck", "Are you sure you want to delete this deck?"):
            self.db.delete_deck(deck_id)
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
            for deck_id in self.selected_decks:
                self.db.delete_deck(deck_id)
            self.selected_decks.clear()
            self.update_deck_list()
            self.sidebar.update_deck_list()
            self.delete_selected_button.configure(state="disabled")

class DeckContainer(BaseContainer):
    # initialises deck cotnainer as subclass of base container (inheritance)
    def __init__(self, master, deck_id, user_id, deck_name, card_count, selection_callback, avg_ef, edit_callback, delete_callback, db):
        super().__init__(master, db=db)
        self.deck_id = deck_id
        self.user_id = user_id
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
        available_for_review = self.db.get_available_for_review_count(self.user_id, deck_id)
        if available_for_review is None:
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
    
    
    def on_checkbox_toggle(self):
        # if checkbox pressed, get its value (true if selected, otherwise false)
        self.selected = self.checkbox.get()
        # call selection_callback with the deck id and current selection state (true or false)
        if self.selection_callback:
            self.selection_callback(self.deck_id, self.selected)
        # if the checkbox is selected, change background and checkbox color
        if self.selected:
            self.configure(fg_color="#F5F3FF")
            self.checkbox.configure(fg_color="#636ae8", checkmark_color="white", hover_color="#636ae8")
        # if deselected or not selected, reset background and checkbox colors to default
        else:
            self.configure(fg_color="white")
            self.checkbox.configure(fg_color="white", checkmark_color="black", hover_color="white")


class CardsPage(BasePage):
    def __init__(self, master, user_id, deck_id, switch_page, db):
        super().__init__(master, user_id, switch_page, db=db)
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

        card_list = []
        cards = self.db.get_cards(self.deck_id)
        
        # builds card_list as tuples with following, (card_id, question, answer, ef)
        # _ is deck_id which is ignored
        for card in cards:
            card_id, _, question, answer = card
            ef = self.db.get_card_easiness(self.user_id, card_id)
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
                db=self.db,
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
        AddCardDialog(self, deck_id=self.deck_id, db=self.db)
        self.update_card_list()
    # call edit card dialog to edit card (it's question and answer)
    def edit_card(self, card_id):
        EditCardDialog(self, card_id, db=self.db)
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

class CardContainer(BaseContainer):
    # initialises card container as subclass of base container (inheritance)
    def __init__(self, master, db, card_id, question, answer, edit_callback, delete_callback, ef, selection_callback=None):
        super().__init__(master, db=db)
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
    
    def on_checkbox_toggle(self):
        # if checkbox pressed, get its value (true if selected, otherwise false)
        self.selected = self.checkbox.get()
        # call selection_callback with the card id and current selection state (true or false)
        if self.selection_callback:
            self.selection_callback(self.card_id, self.selected)
        # if the checkbox is selected, change background and checkbox color
        if self.selected:
            self.configure(fg_color="#F5F3FF")
            self.checkbox.configure(fg_color="#636ae8", checkmark_color="white", hover_color="#636ae8")
        # if deselected or not selected, reset background and checkbox colors to default        
        else:
            self.configure(fg_color="white")
            self.checkbox.configure(fg_color="white", checkmark_color="black", hover_color="white")

class EditCardDialog(BaseDialog):
    # initialise edit card dialog as subclass of basedialog (inheritance)
    def __init__(self, parent, card_id, db):
        # set dialog size for editing a card
        super().__init__(db=db, title="Edit Card", width=500, height=500)
        self.parent = parent
        self.card_id = card_id

        # fetch current card info from the database
        card_info = self.db.get_card(card_id)
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
        # for CTkTextbox, you must specify a range when retrieving text.
        # in ("1.0", "end-1c"), the 1 means start at the first line and the 0 means start at the first character of this line
        # then "end-1c" means retrieve all text from the first character to the last character, and also remove the trailing newline
        new_question = self.question_entry.get("1.0", "end-1c").strip()
        new_answer = self.answer_entry.get("1.0", "end-1c").strip()
        if not new_question or not new_answer:
            messagebox.showwarning("Warning", "Please fill in both question and answer")
            return
        try:
            self.db.update_card(self.card_id, new_question, new_answer)
            # simply close the dialog; the calling page should update the cards list
            self.cancel_dialog_event()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update card: {str(e)}")

class AddCardDialog(BaseDialog):
    # initialise add card dialog as subclass of base dialog (inheritance)
    def __init__(self, parent, deck_id, db):
        # set dialog size for creating a new card
        super().__init__(db=db, title="New Card", width=500, height=500)
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
        # for CTkTextbox, you must specify a range when retrieving text.
        # in ("1.0", "end-1c"), the 1 means start at the first line and the 0 means start at the first character of this line
        # then "end-1c" means retrieve all text from the first character to the last character, and also remove the trailing newline
        question = self.question_entry.get("1.0", "end-1c").strip()
        answer = self.answer_entry.get("1.0", "end-1c").strip()
        if not question or not answer:
            messagebox.showwarning("Warning", "Please fill in both question and answer")
            return
        try:
            self.db.create_card(self.deck_id, question, answer)
            # simply close the dialog; the calling page should update the cards list
            self.cancel_dialog_event()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create card: {str(e)}")

class EditDeckDialog(BaseDialog):
    # intiialise edit deck dialog as subclass of basedialog (inheritance)
    def __init__(self, parent, deck_id, db):
        # set dialog size
        super().__init__(db=db, title="Edit Deck", width=400, height=300)
        self.parent = parent
        self.deck_id = deck_id

        # fetch current deck name from the database
        deck_info = self.db.get_deck_info(deck_id)
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
            self.db.update_deck_name(self.deck_id, new_deck_name)
            self.cancel_dialog_event()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update deck: {str(e)}")

class AddDeckDialog(BaseDialog):
    # initialise add deck dialog as subclass of basedialog (inheritance)
    def __init__(self, parent, db):
        # set dialog size
        super().__init__(db=db, title="New Deck", width=400, height=300)
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
            self.db.create_deck(self.parent.user_id, new_deck_name)
            self.cancel_dialog_event()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create deck: {str(e)}")

class QuizPage(BasePage):
    # initialise quiz page as subclass of base page (inheritance)
    def __init__(self, master, user_id, switch_page, db):
        super().__init__(master, user_id, switch_page, db=db)

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

        # create filter frame for deck search and priority filter (same as decks page)
        self.filter_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.filter_frame.pack(side="right", padx=10)
        
        # deck search entry
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
        
        # update deck list when search or filter changes
        self.deck_search_input.trace_add("write", lambda *args: self.update_deck_list())
        self.deck_priority_filter_selection.trace_add("write", lambda *args: self.update_deck_list())

        # start quiz button (initially disabled)
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

        # separator to divide header from main content
        self.separator = ctk.CTkFrame(self.main_header_content, height=1, fg_color="#E5E7EB")
        self.separator.pack(fill="x", padx=30, pady=(20, 0))

        # selection frame holds a label prompting the user to select a deck
        self.selection_frame = ctk.CTkFrame(self.main_header_content, fg_color="transparent")
        self.selection_frame.pack(fill="both", expand=True, padx=30, pady=20)
        ctk.CTkLabel(
            self.selection_frame,
            text="Select a deck to quiz yourself on",
            font=("Inter", 16, "bold"),
            text_color="black"
        ).pack(anchor="w", pady=(0, 10))

        # scrollable frame for displaying deck containers
        self.decks_frame = ctk.CTkScrollableFrame(
            self.selection_frame,
            fg_color="transparent",
            scrollbar_button_color="#E5E7EB",
            scrollbar_button_hover_color="#D1D5DB"
        )
        self.decks_frame.pack(fill="both", expand=True)
        self.decks_frame.grid_columnconfigure((0, 1, 2), weight=1, pad=10)

        # update deck list when quiz page is shown
        self.update_deck_list()

    # update deck list (same as in decks page)
    def update_deck_list(self):
        for widget in self.decks_frame.winfo_children():
            widget.destroy()

        deck_list = []
        decks = self.db.get_decks(self.user_id)
        for deck in decks:
            deck_id = deck[0]
            deck_name = deck[1]
            cards = self.db.get_cards(deck_id)
            if cards:
                total_ef = 0
                for c in cards:
                    total_ef += self.db.get_card_easiness(self.user_id, c[0])
                avg_ef = total_ef / len(cards)
            else:
                avg_ef = 2.5
            card_count = self.db.get_card_count(deck_id)
            deck_list.append((deck_id, deck_name, avg_ef, card_count))

        # filter deck list based on search query
        search_query = self.deck_search_input.get().lower().strip()
        if search_query:
            deck_list = [deck for deck in deck_list if search_query in deck[1].lower()]

        # filter deck list based on priority selection
        priority_filter = self.deck_priority_filter_selection.get().lower()
        if priority_filter != "all":
            if priority_filter == "high":
                deck_list = [deck for deck in deck_list if deck[2] < 2.0]
            elif priority_filter == "medium":
                deck_list = [deck for deck in deck_list if 2.0 <= deck[2] < 2.5]
            elif priority_filter == "low":
                deck_list = [deck for deck in deck_list if deck[2] >= 2.5]

        # if no decks found, display a message
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

        # sort decks using bst (based on avg_ef)
        from graph import DeckNode, insert_node, in_order
        root = None
        for deck in deck_list:
            node = DeckNode(deck_id=deck[0], deck_name=deck[1], avg_ef=deck[2], card_count=deck[3])
            root = insert_node(root, node)
        sorted_nodes = in_order(root)

        # create a deck container for each deck
        row, col = 0, 0
        for node in sorted_nodes:
            deck_container = DeckContainer(
                self.decks_frame,
                deck_id=node.deck_id,
                user_id=self.user_id,
                deck_name=node.deck_name,
                card_count=node.card_count,
                selection_callback=self.toggle_deck_selection,
                avg_ef=node.avg_ef,
                edit_callback=None,
                delete_callback=None,
                db=self.db
            )
            deck_container.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            col += 1
            if col == 3:
                col = 0
                row += 1

    def toggle_deck_selection(self, deck_id, selected):
        # iterate through each deck container widget in the decks frame
        for widget in self.decks_frame.winfo_children():
            # if this widget's deck id matches the toggled deck's id
            if widget.deck_id == deck_id:
                # set its selected state to the same as the toggled deck
                widget.selected = selected
                # if selected, change background and mark checkbox; if not, reset appearance
                if selected:
                    widget.configure(fg_color="#F5F3FF")
                    widget.checkbox.select()
                else:
                    widget.configure(fg_color="white")
                    widget.checkbox.deselect()
            else:
                # ensure all other deck containers are deselected
                widget.selected = False
                widget.configure(fg_color="white")
                widget.checkbox.deselect()
        
        # manually check if any deck is selected
        selected_found = False
        for widget in self.decks_frame.winfo_children():
            if widget.selected:
                selected_found = True
                break

        # enable the start button if any deck is selected, otherwise disable it
        self.start_button.configure(state="normal" if selected_found else "disabled")

    def start_quiz(self):
        # initialize variable to store the selected deck's id
        selected_deck_id = None
        # iterate through all deck container widgets in the decks frame
        for widget in self.decks_frame.winfo_children():
            if widget.selected:
                # if found, store its deck id and exit loop
                selected_deck_id = widget.deck_id
                break
        # if no deck is selected, show a warning message
        if selected_deck_id is None:
            messagebox.showwarning("Warning", "Please select a deck")
            return
        # clear all widgets on the window to start the quiz session
        for widget in self.master.winfo_children():
            widget.destroy()
        # start a quiz session with the selected deck, passing along the db connection
        QuizSession(self.master, self.user_id, selected_deck_id, self.switch_page, db=self.db)

class QuizSession(ctk.CTkFrame):
    def __init__(self, master, user_id, deck_id, switch_page, db):
        super().__init__(master, corner_radius=0, fg_color="white")
        
        # Create a canvas with scrollbar for scrollability
        self.canvas = ctk.CTkCanvas(master, highlightthickness=0, bg="white")
        self.scrollbar = ctk.CTkScrollbar(master, orientation="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Create a frame inside the canvas for all content
        self.scrollable_frame = ctk.CTkFrame(self.canvas, corner_radius=0, fg_color="white")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=master.winfo_width())
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas.find_all()[0], width=e.width))
        
        # Rest of your initialization code will now use scrollable_frame as parent
        self.user_id = user_id
        self.deck_id = deck_id
        self.switch_page = switch_page
        self.db = db

        # retrieve cards available for review for this deck
        self.cards = self.db.get_available_for_review(self.user_id, self.deck_id)
        if not self.cards:
            self.show_no_cards_message()
            return

        # Get deck name
        deck_name = self.db.get_deck_name(self.deck_id)
        self.total_cards = len(self.cards)
        self.correct_count = 0
        self.session_start_time = datetime.now()
        self.current_card = 0

        # header with title, progress, and timer
        self.header = ctk.CTkFrame(self.scrollable_frame, fg_color="#F3F4F6", height=60)
        self.header.pack(fill="x", pady=(0, 20))
        
        # Center align the header items with a center frame
        self.header_center = ctk.CTkFrame(self.header, fg_color="transparent")
        self.header_center.pack(expand=True, fill="x")
        
        self.title_label = ctk.CTkLabel(
            self.header_center, text=f"Quiz Session - {deck_name}", font=("Inter", 18, "bold"), text_color="black"
        )
        self.title_label.pack(side="left", padx=30)
        self.progress_label = ctk.CTkLabel(
            self.header_center, text=f"Card 1/{self.total_cards}", font=("Inter", 14), text_color="#4B5563"
        )
        self.progress_label.pack(side="right", padx=30)
        self.timer_label = ctk.CTkLabel(
            self.header_center, text="Time Elapsed: 00:00:00", font=("Inter", 14), text_color="#4B5563"
        )
        self.timer_label.pack(side="right", padx=30)

        # makes an instruction label to tell the user how to answer a card
        self.instruction_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="After you view each question, click \"Show Answer\" and then review  difficulty and correctness (whether you got it right or wrong) of the card.",
            font=("Inter", 14),
            text_color="#1F2937",
            wraplength=800,
            justify="center"
        )

        self.instruction_label.pack(fill="x", padx=30, pady=(0,10))

        # main content for question and answer - center align all content
        self.content = ctk.CTkFrame(self.scrollable_frame, fg_color="white")
        self.content.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Question section with clear header - center aligned and bordered
        self.question_section = ctk.CTkFrame(
            self.content, 
            fg_color="white", 
            border_width=1,
            border_color="#E5E7EB",
            corner_radius=8
        )
        self.question_section.pack(fill="x", pady=(0, 5))  # Reduced spacing between Q and A
        
        self.question_header = ctk.CTkLabel(
            self.question_section, text="QUESTION", font=("Inter", 16, "bold"), text_color="#4B5563"
        )
        self.question_header.pack(anchor="center", pady=(10, 0))
        
        # Separator line
        self.question_separator = ctk.CTkFrame(self.question_section, height=1, fg_color="#E5E7EB")
        self.question_separator.pack(fill="x", pady=5, padx=15)
        
        self.question_label = ctk.CTkLabel(
            self.question_section, text="", font=("Inter", 16), text_color="black", wraplength=600, justify="center"
        )
        self.question_label.pack(anchor="center", pady=(5, 15))

        # Answer section with clear header (initially hidden) - center aligned and bordered
        self.answer_frame = ctk.CTkFrame(
            self.content, 
            fg_color="white",
            border_width=1,
            border_color="#E5E7EB",
            corner_radius=8
        )
        
        self.answer_header = ctk.CTkLabel(
            self.answer_frame, text="ANSWER", font=("Inter", 16, "bold"), text_color="#4B5563"
        )
        self.answer_header.pack(anchor="center", pady=(10, 0))
        
        # Separator line
        self.answer_separator = ctk.CTkFrame(self.answer_frame, height=1, fg_color="#E5E7EB")
        self.answer_separator.pack(fill="x", pady=5, padx=15)
        
        self.answer_label = ctk.CTkLabel(
            self.answer_frame, text="", font=("Inter", 16), text_color="black", wraplength=600, justify="center"
        )
        self.answer_label.pack(anchor="center", pady=(5, 15))

        # Show answer button in its own frame - center aligned
        self.button_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.button_frame.pack(fill="x", pady=15)  # Reduced spacing
        
        self.show_answer_button = ctk.CTkButton(
            self.button_frame, text="Show Answer", width=120, height=32, corner_radius=16,
            fg_color="#F3F4F6", text_color="black", hover_color="#E5E7EB", command=self.show_answer
        )
        self.show_answer_button.pack(anchor="center")
        
        # Rating section with "DIFFICULTY" header - renamed from "RECALL QUALITY"
        self.rating_section = ctk.CTkFrame(
            self.content, 
            fg_color="white",
            border_width=1,
            border_color="#E5E7EB",
            corner_radius=8
        )
        
        self.rating_header = ctk.CTkLabel(
            self.rating_section, text="DIFFICULTY", font=("Inter", 16, "bold"), text_color="#4B5563"
        )
        self.rating_header.pack(anchor="center", pady=(10, 0))
        
        # Separator line
        self.rating_separator = ctk.CTkFrame(self.rating_section, height=1, fg_color="#E5E7EB")
        self.rating_separator.pack(fill="x", pady=5, padx=15)

        # difficulty rating options - center aligned
        self.rating_frame = ctk.CTkFrame(self.rating_section, fg_color="transparent")
        self.rating_frame.pack(pady=10)
        
        # Center container for rating buttons
        self.rating_center = ctk.CTkFrame(self.rating_frame, fg_color="transparent")
        self.rating_center.pack(expand=True, anchor="center")
        
        rating_options = [
            ("Very Hard (2 mins)", 0),
            ("Hard (6 mins)", 1),
            ("Medium (10 mins)", 2),
            ("Easy (1 day)", 3),
            ("Very Easy (3 days)", 4)
        ]
        for text, quality in rating_options:
            if quality in (0, 1):
                # for very hard or hard, use red styling
                button_fg = "#FEE2E2"
                button_text = "#DC2626"
                button_hover = "#FECACA"
            else:
                # for medium, easy, or very easy, use gray styling
                button_fg = "#F3F4F6"
                button_text = "black"
                button_hover = "#E5E7EB"
            button = ctk.CTkButton(
                self.rating_center,
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
        
        # add interval explanation label (hidden until answer revealed) - center aligned
        self.interval_help = ctk.CTkLabel(
            self.rating_section,
            text=(

                "Choose how well you recalled the answer:\n"
                " • Very Hard → review in 2 minutes   (you barely remembered it; need to review the card again)\n"
                " • Hard → review in 6 minutes         (you struggled; repeat soon the card soon)\n"
                " • Medium → review in 10 minutes      (you remembered with effort; revisit the card shortly)\n"
                " • Easy → review tomorrow (1 day)     (you recalled it comfortably; check if you still remember the card tomorrow)\n"
                " • Very Easy → review in 3 days       (you remembered effortlessly; check if you still remember the card after 3 days)\n"
                "\n"
                "Cards “available for review” are those whose scheduled review time has arrived (or have never been reviewed) and are ready for practice.\n"
                "\n"
                "For example, pressing “Very Hard” will make the card available to practice in just 2 minutes.\n"
                "While the option “Very Easy“ will make the card available to practice in 3 days\n"
                "This ensures that Easier cards are reviewed after longer periods of time, while harder ones are reviewed more frequently, thus enforcing Spaced Repitition"


            ),
            font=("Inter", 12),
            text_color="#4B5563",
            wraplength=600,
            justify="center"
        )
        self.interval_help.pack(pady=(0, 15))
        
        # hide the entire rating section initially
        self.rating_section.pack_forget()

        # NEW: Add "CORRECTNESS" section with border
        self.correctness_section = ctk.CTkFrame(
            self.content, 
            fg_color="white",
            border_width=1,
            border_color="#E5E7EB",
            corner_radius=8
        )
        
        self.correctness_header = ctk.CTkLabel(
            self.correctness_section, text="CORRECTNESS", font=("Inter", 16, "bold"), text_color="#4B5563"
        )
        self.correctness_header.pack(anchor="center", pady=(10, 0))
        
        # Separator line
        self.correctness_separator = ctk.CTkFrame(self.correctness_section, height=1, fg_color="#E5E7EB")
        self.correctness_separator.pack(fill="x", pady=5, padx=15)
        
        # correct/incorrect buttons to record recall accuracy - center aligned
        self.correct_frame = ctk.CTkFrame(self.correctness_section, fg_color="transparent")
        self.correct_frame.pack(pady=10)
        
        # Center container for correct/incorrect buttons
        self.correct_center = ctk.CTkFrame(self.correct_frame, fg_color="transparent")
        self.correct_center.pack(expand=True, anchor="center")
        
        # explain correctness meaning - center aligned
        self.correct_help = ctk.CTkLabel(
            self.correct_frame,
            text=(
                "Judge whether or not you feel you got the card right. \"Correct\" marks it right, \"Incorrect\" marks it wrong.    "
                "Remember to be honest with yourself—making mistakes is a natural part of learning and helps you improve!"
            ),
            font=("Inter", 12),
            text_color="#4B5563",
            wraplength=600,
            justify="center"
        )
        self.correct_help.pack(pady=(0,10))
        
        self.correct_button = ctk.CTkButton(
            self.correct_center,
            text="Correct",
            width=120,
            height=32,
            corner_radius=16,
            fg_color="#D1FAE5",
            text_color="#065F46",
            hover_color="#A7F3D0",
            command=lambda: self.record_correctness(True)
        )
        self.correct_button.pack(side="left", padx=5)
        
        self.incorrect_button = ctk.CTkButton(
            self.correct_center,
            text="Incorrect",
            width=120,
            height=32,
            corner_radius=16,
            fg_color="#FEE2E2",
            text_color="#B91C1C",
            hover_color="#FECACA",
            command=lambda: self.record_correctness(False)
        )
        self.incorrect_button.pack(side="left", padx=5)
        
        # Extra padding at the bottom of correctness section
        ctk.CTkFrame(self.correctness_section, fg_color="transparent", height=5).pack()
        
        # Hide correctness section initially
        self.correctness_section.pack_forget()

        # start timer and display the first card
        self.update_timer()
        self.display_card()
        
    def update_timer(self):
        # update the timer label every second
        if not hasattr(self, 'timer_label') or not self.timer_label.winfo_exists():
            return
        elapsed = datetime.now() - self.session_start_time
        total_seconds = int(elapsed.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        self.timer_label.configure(text=f"Time Elapsed: {hours:02d}:{minutes:02d}:{seconds:02d}")
        self.after(1000, self.update_timer)

    def display_card(self):
        # if no more cards remain, end the quiz
        if self.current_card >= self.total_cards:
            self.end_quiz()
            return

        # hide answer, correctness, interval and rating UI
        self.answer_frame.pack_forget()
        self.rating_section.pack_forget()
        self.correctness_section.pack_forget()
        self.button_frame.pack(fill="x", pady=15)
        self.show_answer_button.pack(anchor="center")
        
        # get current card (in a tuple with card_id, question, answer, next_review_date)
        card = self.cards[self.current_card]
        self.current_card_id = card[0]
        self.question_label.configure(text=card[1])
        self.answer_label.configure(text=card[2])
        self.progress_label.configure(text=f"Card {self.current_card + 1}/{self.total_cards}")
        self.card_start_time = datetime.now()

    def show_answer(self):
        # hide the "show answer" button and reveal the answer and rating options
        self.button_frame.pack_forget()
        self.answer_frame.pack(fill="x", pady=(5, 10))  # Reduced spacing
        
        # show rating section with explanation
        self.rating_section.pack(fill="x", pady=(5, 5))  # Reduced spacing
        self.correctness_section.pack(fill="x", pady=(5, 0))  # Reduced spacing

    def record_correctness(self, was_correct):
        # set correctness
        if was_correct:
            self.correct_count += 1
        self.db.update_card_correctness(
            user_id=self.user_id,
            card_id=self.current_card_id,
            is_correct=was_correct
        )
        # move to next card
        self.current_card += 1
        self.display_card()
        
    # shows a confirmation message after rating option selected
    def show_temporary_confirmation(self, message, duration=1500):
        # Create a small popup frame on top of the current content
        popup = ctk.CTkFrame(
            self.content, 
            fg_color="#F3F4F6",  
            corner_radius=8,
            border_width=1,
            border_color="#E5E7EB" 
        )
        
        # Position the popup at the center top of the content area
        popup.place(relx=0.5, rely=0.3, anchor="center")
        
        # Add the confirmation message
        confirm_label = ctk.CTkLabel(
            popup,
            text=message,
            font=("Inter", 14),
            text_color="#000000",  
            padx=20,
            pady=10
        )
        confirm_label.pack(padx=20, pady=10)
        
        # Schedule the popup to disappear after the specified duration
        self.after(duration, lambda: popup.destroy())

            
    def rate_card_difficulty(self, quality):
        # update scheduling of card using spaced repitition algorithm
        card_time = (datetime.now() - self.card_start_time).total_seconds()
        self.db.update_spaced_rep(
            user_id=self.user_id,
            card_id=self.current_card_id,
            quality=quality,
            time_taken=card_time
        )
        
        difficulty_messages = {
            0: "Rating received: Very Hard - Card will be reviewed in 2 minutes",
            1: "Rating received: Hard - Card will be reviewed in 6 minutes",
            2: "Rating received: Medium - Card will be reviewed in 10 minutes",
            3: "Rating received: Easy - Card will be reviewed in 1 day",
            4: "Rating received: Very Easy - Card will be reviewed in 3 days"
        }
        
        message = difficulty_messages.get(quality, "Rating received")
        self.show_temporary_confirmation(message)
        
    def end_quiz(self):
        # calculate total quiz session time and average time per card
        deck_time = (datetime.now() - self.session_start_time).total_seconds()
        self.total_time = deck_time
        avg_time = deck_time / self.total_cards if self.total_cards > 0 else 0
        # save the quiz result in the database
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
        # Clear the canvas and scrollbar
        self.canvas.destroy()
        self.scrollbar.destroy()
        
        # Create a new frame for the summary
        summary_frame = ctk.CTkFrame(self.master, fg_color="white", corner_radius=0)
        summary_frame.pack(fill="both", expand=True)
        
        # Header section with title
        header_frame = ctk.CTkFrame(summary_frame, fg_color="#F3F4F6", height=60)
        header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            header_frame,
            text="Quiz Complete!",
            font=("Inter", 24, "bold"),
            text_color="black"
        ).pack(pady=20)
        
        # Stats container matching analytics page style
        stats_container = ctk.CTkFrame(
            summary_frame,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color="#E5E7EB"
        )
        stats_container.pack(fill="x", padx=30, pady=(0, 20))
        
        ctk.CTkLabel(
            stats_container,
            text="Session Results",
            font=("Inter", 18, "bold"),
            text_color="#111827"
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        # Container for stat cards
        stat_cards_container = ctk.CTkFrame(stats_container, fg_color="white")
        stat_cards_container.pack(fill="x", padx=20, pady=(0, 15))
        
        # Calculate stats
        total_cards = self.total_cards
        wrong = total_cards - self.correct_count
        accuracy = (self.correct_count / total_cards) * 100 if total_cards > 0 else 0
        
        # Layout for stats - each tuple is (label, value, icon)
        stats_layout = [
            ("Total Cards Reviewed", f"{total_cards}", "📄"),
            ("Correct Answers", f"{self.correct_count}", "✅"),
            ("Wrong Answers", f"{wrong}", "❌"),
            ("Accuracy", f"{accuracy:.1f}%", "🎯"),
            ("Total Time Spent", f"{self.total_time:.1f}s", "⏱️"),
            ("Avg Time Per Card", f"{(self.total_time / total_cards):.1f}s" if total_cards else "0s", "⚡")
        ]
        
        # Use same grid layout as analytics page: 3 rows, 2 columns
        row_count = 3
        col_count = 2
        index = 0
        
        for row in range(row_count):
            row_frame = ctk.CTkFrame(stat_cards_container, fg_color="white")
            row_frame.pack(fill="x", pady=5)
            row_frame.grid_columnconfigure(0, weight=1, uniform="stats_col")
            row_frame.grid_columnconfigure(1, weight=1, uniform="stats_col")
            for col in range(col_count):
                if index < len(stats_layout):
                    stat_label, stat_value, stat_icon = stats_layout[index]
                    self.create_stat_card(row_frame, stat_label, stat_value, stat_icon, col)
                    index += 1
        
        # Return button with improved visibility
        return_container = ctk.CTkFrame(summary_frame, fg_color="transparent")
        return_container.pack(fill="x", pady=(10, 20))
        
        ctk.CTkButton(
            return_container,
            text="Return to Quiz",
            width=200,
            height=40,
            corner_radius=16,
            font=("Inter", 14, "bold"),
            fg_color="#F3F4F6",  
            text_color="white",
            hover_color="#E5E7EB",
            command=lambda: self.switch_page(__import__('app').QuizPage, user_id=self.user_id, switch_page=self.switch_page)
        ).pack(anchor="center", pady=20)
        
    def create_stat_card(self, parent, label_text, value_text, icon_text, col_index):
        # Container for an individual stat card
        stat_card_container = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color="#E5E7EB"
        )
        stat_card_container.grid(row=0, column=col_index, padx=5, sticky="nsew")
        
        # Inner frame holding the stat info
        stat_info = ctk.CTkFrame(stat_card_container, fg_color="white")
        stat_info.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(stat_info, text=icon_text, font=("Inter", 18), text_color="#4B5563").pack(anchor="w")
        ctk.CTkLabel(stat_info, text=label_text, font=("Inter", 12), text_color="#4B5563").pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(stat_info, text=value_text, font=("Inter", 20, "bold"), text_color="#111827").pack(anchor="w", pady=(5, 0))
            
    def show_no_cards_message(self):
        # Clear the canvas and scrollbar if they exist
        if hasattr(self, 'canvas'):
            self.canvas.destroy()
        if hasattr(self, 'scrollbar'):
            self.scrollbar.destroy()
        
        msg_frame = ctk.CTkFrame(self.master, fg_color="white")
        msg_frame.pack(fill="both", expand=True, padx=30, pady=30)
        ctk.CTkLabel(
            msg_frame,
            text="No cards available for review!",
            font=("Inter", 18, "bold"),
            text_color="black"
        ).pack(expand=True)
        
        # Center align the button
        button_frame = ctk.CTkFrame(msg_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="Return to Quiz",
            width=200,
            height=40,
            corner_radius=16,
            command=lambda: self.switch_page(__import__('app').QuizPage, user_id=self.user_id, switch_page=self.switch_page)
        ).pack(pady=20, anchor="center")






class AnalyticsPage(BasePage):
    # initialises analytics page as a subclass of basepage (inheritance)
    def __init__(self, master, user_id, switch_page, db):
        super().__init__(master, user_id, switch_page, db=db)
        # get quiz stats for the user and initialise deck details mapping
        self.stats = self.db.get_quiz_stats(self.user_id)
        # deck_details stores a mapping from each deck id to its details container widget
        # each key is a deck id and the value is the frame that holds detailed statistics for that deck
        self.deck_details = {}

        # header frame page title ("Analytics")
        header_frame = ctk.CTkFrame(self.main_header_content, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 0))
        ctk.CTkLabel(
            header_frame,
            text="Analytics",
            font=("Inter", 24, "bold"),
            text_color="black"
        ).pack(side="left")

        # separator between header and main content
        separator = ctk.CTkFrame(self.main_header_content, height=1, fg_color="#E5E7EB")
        separator.pack(fill="x", padx=30, pady=(10, 0))

        # scrollable container for analytics content
        self.analytics_container = ctk.CTkScrollableFrame(
            self.main_header_content,
            fg_color="transparent",
            border_width=0,
            scrollbar_button_color="#E5E7EB",
            scrollbar_button_hover_color="#D1D5DB"
        )
        self.analytics_container.pack(fill="both", expand=True, padx=30, pady=20)

        # create overall stats section, deck performance section, graph controls and return button
        self.create_overall_stats_section()
        self.create_deck_performance_section()
        self.create_return_button()
    
    # creates a single stat card used in overall stats section and individual deck stats section
    def create_stat_card(self, parent, label_text, value_text, icon_text, col_index):
        # container for an individual stat card
        stat_card_container = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color="#E5E7EB"
        )
        stat_card_container.grid(row=0, column=col_index, padx=5, sticky="nsew")
        # inner frame holding the stat info
        stat_info = ctk.CTkFrame(stat_card_container, fg_color="white")
        stat_info.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(stat_info, text=icon_text, font=("Inter", 18), text_color="#4B5563").pack(anchor="w")
        ctk.CTkLabel(stat_info, text=label_text, font=("Inter", 12), text_color="#4B5563").pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(stat_info, text=value_text, font=("Inter", 20, "bold"), text_color="#111827").pack(anchor="w", pady=(5, 0))

    # creates the overall statistics section
    def create_overall_stats_section(self):
        # stat container for overall stats
        stats_container = ctk.CTkFrame(
            self.analytics_container,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color="#E5E7EB"
        )
        stats_container.pack(fill="x", pady=(0, 20))

        # title label for overall statistics
        ctk.CTkLabel(
            stats_container,
            text="Overall Statistics",
            font=("Inter", 18, "bold"),
            text_color="#111827"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        # stat_cards_container to hold the individual stat cards (like avg time per card, total sessions, etc.)
        stat_cards_container = ctk.CTkFrame(stats_container, fg_color="white")
        stat_cards_container.pack(fill="x", padx=20, pady=(0, 15))

        total_sessions = self.stats.get("total_sessions", 0)
        total_reviewed = self.stats.get("total_reviewed", 0)
        total_correct = self.stats.get("total_correct", 0)
        overall_accuracy = self.stats.get("overall_accuracy", 0.0)
        total_time = self.stats.get("total_time", 0.0)
        avg_time_card = self.stats.get("overall_avg_time_per_card", 0.0)

        # layout for each stat card: (label, value, icon)
        stats_layout = [
            ("Total Sessions", str(total_sessions), "📊"),
            ("Total Cards Reviewed", str(total_reviewed), "📄"),
            ("Total Correct Answers", str(total_correct), "✅"),
            ("Overall Accuracy", f"{overall_accuracy:.1f}%", "🎯"),
            ("Total Time Spent Quizzing", f"{total_time:.1f}s", "⏱️"),
            ("Avg Time Per Card", f"{avg_time_card:.1f}s", "⚡"),
        ]

        # create stat cards in a grid with 3 rows and 2 columns
        row_count = 3
        col_count = 2
        index = 0  # counter to iterate through stats_layout
        
        # iterates through stats_layout and displays each stat as a container in a 2x3 grid
        for row in range(row_count):
            row_frame = ctk.CTkFrame(stat_cards_container, fg_color="white")
            row_frame.pack(fill="x", pady=5)
            row_frame.grid_columnconfigure(0, weight=1, uniform="stats_col")
            row_frame.grid_columnconfigure(1, weight=1, uniform="stats_col")
            for col in range(col_count):
                if index < len(stats_layout):
                    stat_label, stat_value, stat_icon = stats_layout[index]
                    self.create_stat_card(row_frame, stat_label, stat_value, stat_icon, col)
                    index += 1
  

    # creates the deck performance section
    def create_deck_performance_section(self):
        # container for deck performance stats
        performance_container = ctk.CTkFrame(
            self.analytics_container,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color="#E5E7EB"
        )
        performance_container.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            performance_container,
            text="Deck Performance",
            font=("Inter", 18, "bold"),
            text_color="#111827"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        # build a list of decks with performance scores
        decks = self.db.get_decks(self.user_id)
        deck_list = []
        for deck_id, deck_name in decks:
            performance_score = self.db.get_deck_performance_score(self.user_id, deck_id)
            deck_list.append((deck_id, deck_name, performance_score))

        # reverse=True is needed because sort() will sort in ascending order by default, but this needs to be descending
        # get_performance_score returns the third element of each deck in deck_list
        # which is performance_score, and then sort() sorts the deck_list based on these performance scores in descending order
        def get_performance_score(x):
            return x[2]
        deck_list.sort(key=get_performance_score, reverse=True)

        # create a deck performance card for each deck
        for deck_id, deck_name, performance in deck_list:
            self.db.get_deck_stats(self.user_id, deck_id)
            # deck_stats = 
            # container for a single deck performance card
            deck_performance_card = ctk.CTkFrame(
                performance_container,
                fg_color="white",
                corner_radius=8,
                border_width=1,
                border_color="#E5E7EB"
            )
            deck_performance_card.pack(fill="x", padx=20, pady=5)

            row_frame = ctk.CTkFrame(deck_performance_card, fg_color="white")
            row_frame.pack(fill="x", padx=15, pady=10)

            ctk.CTkLabel(
                row_frame,
                text=deck_name,
                font=("Inter", 14, "bold"),
                text_color="#111827"
            ).pack(side="left")

            # set score color based on performance thresholds
            if performance < 50:
                # red for performance below 50
                score_color = "#DC2626"  
                # yellow for performance between 50 and 80
            elif performance < 80:
                score_color = "#F59E0B"  
            else:
                # green for performance 80 and above
                score_color = "#10B981"  
                
            # place performance on right side
            ctk.CTkLabel(
                row_frame,
                text=f"{performance:.1f}/100",
                font=("Inter", 14, "bold"),
                text_color=score_color
            ).pack(side="right", padx=(10, 0))

            # view details button to view the stat containers for a deck (deck details)
            view_details_button = ctk.CTkButton(
                row_frame,
                text="View Details",
                width=100,
                height=32,
                corner_radius=16,
                fg_color="#F3F4F6",
                text_color="black",
                hover_color="#E5E7EB",
                command=lambda d_id=deck_id: self.toggle_deck_details(d_id)
            )
            view_details_button.pack(side="right", padx=(10, 0))

            # hides the individual deck details container
            deck_detail_container = ctk.CTkFrame(
                deck_performance_card,
                fg_color="white",
                corner_radius=8,
                border_width=1,
                border_color="#E5E7EB"
            )
            deck_detail_container.pack_forget()
            self.deck_details[deck_id] = deck_detail_container

    # toggles the visibility of deck details when "view details" is clicked
    def toggle_deck_details(self, deck_id):
        # get the details frame for this deck from our deck_details mapping
        deck_details_frame = self.deck_details.get(deck_id)
        if not deck_details_frame:
            return

        # if the deck details frame is already shown, hide it and exit
        if deck_details_frame.winfo_ismapped():
            deck_details_frame.pack_forget()
        else:
            # clear any existing widgets in the details frame
            for widget in deck_details_frame.winfo_children():
                widget.destroy()

            # fetch deck statistics from the database for this deck
            deck_stats = self.db.get_deck_stats(self.user_id, deck_id)
            # define layout for deck details: each tuple is (stat label, stat value, icon)
            deck_details_layout = [
                ("sessions", f"{deck_stats.get('session_count', 0)}", "📊"),
                ("total cards reviewed", f"{deck_stats.get('total_reviewed', 0)}", "📄"),
                ("correct answers", f"{deck_stats.get('total_correct', 0)}", "✅"),
                ("overall accuracy", f"{deck_stats.get('accuracy', 0):.1f}%", "🎯"),
                ("total quiz time", f"{deck_stats.get('total_time', 0):.1f}s", "⏱️"),
                ("avg time/card", f"{deck_stats.get('avg_time_per_card', 0):.1f}s", "⚡"),
            ]

            # create a container frame for the deck detail stat cards
            details_container = ctk.CTkFrame(deck_details_frame, fg_color="white")
            details_container.pack(fill="x", expand=True, padx=15, pady=15)

            # set up grid: 3 rows and 2 columns for six stat cards
            row_count = 3
            col_count = 2
            index = 0  # counter to iterate through deck_details_layout
            
            
            for row in range(row_count):
                row_frame = ctk.CTkFrame(details_container, fg_color="white")
                row_frame.pack(fill="x", pady=5)
                row_frame.grid_columnconfigure(0, weight=1, uniform="stats_col")
                row_frame.grid_columnconfigure(1, weight=1, uniform="stats_col")
                for col in range(col_count):
                    if index < len(deck_details_layout):
                        stat_label, stat_value, stat_icon = deck_details_layout[index]
                        # create a stat card using the same function as overall stats
                        self.create_stat_card(row_frame, stat_label, stat_value, stat_icon, col)
                        index += 1

            # display the deck details frame so all stat cards are visible
            deck_details_frame.pack(fill="x", pady=(5, 10))

    # return to dashboard button
    def create_return_button(self):
        return_container = ctk.CTkFrame(self.analytics_container, fg_color="transparent")
        return_container.pack(side="bottom", fill="x", pady=(10, 0))
        ctk.CTkButton(
            return_container,
            text="Return to dashboard",
            width=200,
            height=40,
            corner_radius=16,
            font=("Inter", 14),
            fg_color="#F3F4F6",
            text_color="black",
            hover_color="#E5E7EB",
            command=lambda: self.switch_page(__import__('app').DecksPage, user_id=self.user_id, switch_page=self.switch_page)
        ).pack(anchor="center", pady=20)

class SettingsPage(BasePage):
    # initialise settings page as subclass of basepage
    def __init__(self, master, user_id, switch_page, db):
        # initialize basepage (sets up sidebar, main_header_content, etc.)
        super().__init__(master, user_id, switch_page, db=db)
        self.user_id = user_id
        self.switch_page = switch_page

        # fetch current user info from the database; expected keys: "email", "username"
        try:
            user_info = self.db.get_user(self.user_id)
            current_email = user_info.get("email", "")
            current_username = user_info.get("username", "")
        except Exception as e:
            print(f"error fetching user info: {e}")
            current_email = ""
            current_username = ""

        # create header frame in the main header content area
        header_frame = ctk.CTkFrame(self.main_header_content, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 10))
        ctk.CTkLabel(
            header_frame,
            text="Account Settings",
            font=("Inter", 24, "bold"),
            text_color="black"
        ).pack(side="left")

        # create main header content area (non-scrollable)
        main_area = ctk.CTkFrame(self.main_header_content, fg_color="white")
        main_area.pack(fill="both", expand=True, padx=30, pady=20)

        # create a central container to center the settings container within main_area
        center_container = ctk.CTkFrame(main_area, fg_color="transparent")
        center_container.place(relx=0.5, rely=0.3, anchor="center")

        # create settings container (holds the settings form) (to change username, email, password and delete account)
        self.settings_container = ctk.CTkFrame(
            center_container,
            fg_color="white",
            corner_radius=12,
            width=400,
            height=600
        )
        
        
        self.settings_container.pack(expand=True)

        # add title label inside settings container
        ctk.CTkLabel(
            self.settings_container,
            text="Update Your Account Details",
            font=("Inter", 20, "bold"),
            text_color="#000000"
        ).pack(pady=(30, 20))

        # add email label and entry (with current email)
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

        # add username label and entry (with current username)
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

        # add password label and entry (left blank so user can enter a new password if desired)
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
        # note: do not pre-populate the password field

        # add update settings button
        ctk.CTkButton(
            self.settings_container,
            text="Update",
            width=300,
            height=45,
            corner_radius=16,
            fg_color="#F3F4F6",
            text_color="black",
            hover_color="#E5E7EB",
            command=self.update
        ).pack(pady=20)

        # add delete account button
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

        # add status label for feedback messages
        self.status_label = ctk.CTkLabel(
            self.settings_container,
            text="",
            text_color="#DC2626"
        )
        self.status_label.pack(pady=10)

    def update(self):
        new_email = self.email_entry.get().strip()
        new_username = self.username_entry.get().strip()
        new_password = self.password_entry.get().strip()

        # if no fields are provided, show an error message
        if not new_email and not new_username and not new_password:
            self.status_label.configure(text="Please enter at least one field to update.")
            return

        try:
            # update the user information; if new_password is blank, the current password remains unchanged
            updated = self.db.update_user(self.user_id, new_email, new_username, new_password)
            if updated:
                self.status_label.configure(text="Settings updated successfully.", text_color="#16A34A")
            else:
                self.status_label.configure(text="Failed to update settings.", text_color="#DC2626")
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="#DC2626")

    def delete_account(self):
        # ask for confirmation before deleting the account
        confirm = messagebox.askyesno(
            "Confirm deletion",
            "Are you sure you want to delete your account? this action cannot be undone."
        )
        if not confirm:
            return
        
        try:
            deleted = self.db.delete_user(self.user_id)
            if deleted:
                messagebox.showinfo("Account deleted", "Your account has been deleted.")
                from login import LoginPage
                self.switch_page(LoginPage)
            else:
                messagebox.showerror("Deletion failed", "Failed to delete your account. Please try again later.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
