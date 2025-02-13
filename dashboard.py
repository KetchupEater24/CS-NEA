#External Imports
import customtkinter as ctk
from typing import Callable
from tkinter import messagebox
from PIL import Image
from datetime import datetime

# My Imports
from database import Database
from helpers import Session
from components import CustomInputDialog

session = Session()

#####################################################SIDEBAR########################################################################
class Sidebar(ctk.CTkFrame):
    def __init__(self, master, switch_page: Callable, username: str, user_id: int, session: Session):
        super().__init__(
            master, 
            fg_color="white", 
            width=250,
            corner_radius=0,
            border_width=0,  
            border_color="#E5E7EB"
        )
        self.pack_propagate(False)
        self.grid_propagate(False)
        
        #creates right border for navbar
        self.right_border = ctk.CTkFrame(
            self,
            width=1,
            fg_color="#E5E7EB",
            corner_radius=0
        )
        self.right_border.pack(side="right", fill="y")
        
        # main page content container (right side)
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(side="left", fill="both", expand=True)
        
        self.switch_page = switch_page
        self.user_id = user_id
        self.session = session

        # checks which page is currently open
        show_decks = isinstance(master, (DecksPage, CardsPage))

        # logo and navigation container
        nav_container = ctk.CTkFrame(self.content, fg_color="transparent")
        nav_container.pack(fill="x", expand=False)

        # logo frame
        logo_frame = ctk.CTkFrame(nav_container, fg_color="transparent")
        logo_frame.pack(fill="x", pady=(20, 20), padx=20)
        
        logo_image = ctk.CTkImage(light_image=Image.open("images/logo.png"), size=(32, 32))
        ctk.CTkLabel(logo_frame, image=logo_image, text="").pack(side="left")
        ctk.CTkLabel(
            logo_frame, 
            text="Flow Space",
            font=("Inter", 20, "bold"),
            text_color="black"
        ).pack(side="left", padx=10)

        # navigation buttons
        self.create_nav_buttons(nav_container, show_decks)

        # user info at bottom
        self.create_user_section(username)

    def create_nav_buttons(self, parent, show_decks):
        # My Decks button
        decks_button = self.create_decks_button(parent)
        decks_button.pack(fill="x", padx=20, pady=(0, 5))
        
        # Deck list container
        self.deck_container = ctk.CTkFrame(parent, fg_color="transparent", height=0)
        self.deck_container.pack(fill="x", expand=False)
        
        if show_decks:
            self.update_deck_list()

        # navigation buttons
        nav_items = [
            ("Quiz yourself", "images/quiz_icon.png", 
             lambda: self.switch_page(QuizPage, user_id=self.user_id, session=self.session, switch_page=self.switch_page)),
            ("Analytics", "images/analytics_icon.png", 
             lambda: self.switch_page(AnalyticsPage, user_id=self.user_id, session=self.session, switch_page=self.switch_page))
        ]

        #creates unique nav buttons with slightly different features (using tuple of items)
        for text, icon_path, command in nav_items:
            button = self.create_nav_button(parent, text, icon_path, command)
            button.pack(fill="x", padx=20, pady=5)

    #creates default My Decks button
    def create_decks_button(self, parent):
        decks_button = ctk.CTkButton(
            parent,
            text="My decks",
            image=ctk.CTkImage(light_image=Image.open("images/decks_icon.png"), size=(20, 20)),
            anchor="w",
            fg_color="transparent",
            text_color="black",
            hover_color="#F3F4F6",
            compound="left",
            font=("Inter", 14, "bold"),
            command=lambda: self.switch_page(DecksPage, user_id=self.user_id, session=self.session, switch_page=self.switch_page)
        )
        return decks_button

    #creates select multiple decks button
    def toggle_selection_mode(self):
        self.selection_mode = not getattr(self, 'selection_mode', False)
        self.select_button.configure(
            text="Cancel" if self.selection_mode else "Select",
            fg_color="#FEE2E2" if self.selection_mode else "transparent",
            text_color="#DC2626" if self.selection_mode else "#4F46E5",
            hover_color="#FECACA" if self.selection_mode else "#EEF2FF"
        )
        self.load_decks()  # Refresh decks to show/hide checkboxes

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.session.clear_session()
            from login import LoginPage
            self.switch_page(LoginPage)

    def load_decks(self):
        # Clear existing decks
        for widget in self.deck_container.winfo_children():
            widget.destroy()
            
        db = Database()
        decks = db.get_decks(self.user_id)
        
        if decks:
            # Create scrollable frame
            scroll_frame = ctk.CTkScrollableFrame(
                self.deck_container,
                fg_color="transparent",
                height=min(len(decks) * 36, 108),  # Dynamic height, max 3 items
                width=210,
                scrollbar_button_color="#E5E7EB",
                scrollbar_button_hover_color="#D1D5DB"
            )
            scroll_frame.pack(fill="x", padx=20, pady=(0, 10))
            
            # Add deck buttons with borders
            for deck_id, deck_name in decks:
                deck_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent", height=36)
                deck_frame.pack(fill="x", expand=False)
                deck_frame.pack_propagate(False)
                
                btn = ctk.CTkButton(
                    deck_frame,
                    text=deck_name,
                    fg_color="transparent",
                    text_color="#6B7280",
                    hover_color="#F3F4F6",
                    anchor="w",
                    height=35,  # Slightly less than frame height to show border
                    command=lambda d_id=deck_id: self.switch_page(
                        CardsPage,
                        user_id=self.user_id,
                        deck_id=d_id,
                        session=self.session,
                        switch_page=self.switch_page
                    )
                )
                btn.pack(fill="x", pady=(0, 1))  # 1px bottom padding for border
                
                # Add bottom border
                border = ctk.CTkFrame(deck_frame, height=1, fg_color="#E5E7EB")
                border.pack(fill="x", side="bottom")

    def create_deck_button(self, parent, deck_id, deck_name):
        btn = ctk.CTkButton(
            parent,
            text=deck_name,
            fg_color="transparent",
            text_color="#6B7280",
            hover_color="#F3F4F6",
            anchor="w",
            height=32,
            command=lambda: self.switch_page(
                CardsPage,
                user_id=self.user_id,
                deck_id=deck_id,
                session=self.session,
                switch_page=self.switch_page
            )
        )
        return btn

    def create_nav_button(self, parent, text, icon_path, command):
        button = ctk.CTkButton(
            parent,
            text=text,
            image=ctk.CTkImage(light_image=Image.open(icon_path), size=(20, 20)),
            anchor="w",
            fg_color="transparent",
            text_color="black",
            hover_color="#F3F4F6",
            compound="left",
            font=("Inter", 14, "bold"),
            command=command
        )
        return button


    #user info such as logo and name at bottom of navbar
    def create_user_section(self, username):
        # User info at bottom
        user_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        user_frame.pack(side="bottom", fill="x", pady=20, padx=20)
        
        # User avatar and name
        avatar_frame = ctk.CTkFrame(user_frame, fg_color="transparent")
        avatar_frame.pack(side="left", fill="y")
        
        first_letter = username[0].upper()
        avatar = ctk.CTkLabel(
            avatar_frame, 
            text=first_letter,
            width=40,  
            height=40,  
            fg_color="#4F46E5",
            text_color="white",
            font=("Inter", 16, "bold"),
            corner_radius=20
        )
        avatar.pack(side="left", pady=4)  # Added vertical padding to center
        
        ctk.CTkLabel(
            avatar_frame, 
            text=username,
            font=("Inter", 16),
            text_color="black"
        ).pack(side="left", padx=12, pady=4)  # Added vertical padding to center
        
        # Logout button with image
        logout_image = ctk.CTkImage(
            light_image=Image.open("images/logout.png"),
            dark_image=Image.open("images/logout.png"),
            size=(16, 16)  # Reduced image size
        )
        
        ctk.CTkButton(
            user_frame,
            text="",
            image=logout_image,
            width=36,
            height=36,
            corner_radius=18,  # Half of width/height
            fg_color="#F3F4F6",
            hover_color="#FEE2E2",
            command=self.logout
        ).pack(side="right", pady=4)  # Added vertical padding to center

    #if new decks added or deleted the navbar will have to reflect the update
    def update_deck_list(self):
        # Clear existing deck list
        for widget in self.deck_container.winfo_children():
            widget.destroy()

        db = Database()
        decks = db.get_decks(self.user_id)
        
        if decks:
            # Create scrollable frame
            scroll_frame = ctk.CTkScrollableFrame(
                self.deck_container,
                fg_color="transparent",
                height=min(len(decks) * 36, 108),  # Dynamic height, max 3 items
                width=210,
                scrollbar_button_color="#E5E7EB",
                scrollbar_button_hover_color="#D1D5DB"
            )
            scroll_frame.pack(fill="x", padx=20, pady=(0, 10))
            
            # Add deck buttons with borders
            for deck_id, deck_name in decks:
                deck_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent", height=36)
                deck_frame.pack(fill="x", expand=False)
                deck_frame.pack_propagate(False)
                
                btn = ctk.CTkButton(
                    deck_frame,
                    text=deck_name,
                    fg_color="transparent",
                    text_color="#6B7280",
                    hover_color="#F3F4F6",
                    anchor="w",
                    height=35,  # Slightly less than frame height to show border
                    command=lambda d_id=deck_id: self.switch_page(
                        CardsPage,
                        user_id=self.user_id,
                        deck_id=d_id,
                        session=self.session,
                        switch_page=self.switch_page
                    )
                )
                btn.pack(fill="x", pady=(0, 1))  # 1px bottom padding for border
                
                # Add bottom border
                border = ctk.CTkFrame(deck_frame, height=1, fg_color="#E5E7EB")
                border.pack(fill="x", side="bottom")

#############################################################DECKS PAGE#############################################################

class DecksPage(ctk.CTkFrame):
    def __init__(self, master, user_id, session, switch_page):
        super().__init__(master, corner_radius=0, fg_color="white")
        self.user_id = user_id
        self.session = session
        self.switch_page = switch_page
        self.selected_decks = set()
        
        # Get username from database
        db = Database()
        self.username = db.get_username(self.user_id)
        
        # create sidebar instance
        self.sidebar = Sidebar(self, switch_page, self.username, self.user_id, self.session)
        self.sidebar.pack(side="left", fill="y")
        
        # main content area
        self.main_content = ctk.CTkFrame(self, fg_color="white")
        self.main_content.pack(side="left", fill="both", expand=True)
        
        # header frame
        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 0))
        
        # title
        ctk.CTkLabel(
            header_frame,
            text="My Decks",
            font=("Inter", 24, "bold"),
            text_color=("black")
        ).pack(side="left")
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        buttons_frame.pack(side="right")
        
        # Add button
        ctk.CTkButton(
            buttons_frame,
            text="+ Add",
            width=70,
            height=32,
            corner_radius=16,
            fg_color="#F3F4F6",
            text_color="black",
            hover_color="#E5E7EB",
            command=self.add_deck
        ).pack(side="left", padx=5)
        
        # delete selected button
        self.delete_button = ctk.CTkButton(
            buttons_frame,
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
        
        # add separator line after header
        separator = ctk.CTkFrame(self.main_content, height=1, fg_color="#E5E7EB")
        separator.pack(fill="x", padx=30, pady=(20, 0))
        
        # decks grid container
        self.decks_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.decks_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # configure grid columns with padding
        self.decks_frame.grid_columnconfigure((0, 1), weight=1, pad=20)
        
        self.display_decks()

    def display_decks(self):
        for widget in self.decks_frame.winfo_children():
            widget.destroy()
            
        db = Database()
        decks = db.get_decks(self.user_id)
        
        row = 0
        col = 0
        for deck_id, deck_name in decks:
            card_count = db.get_card_count(deck_id)
            deck_container = DeckContainer(
                self.decks_frame,
                deck_id,
                deck_name,
                card_count,
                self.toggle_deck_selection
            )
            deck_container.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            
            col += 1
            if col > 1:
                col = 0
                row += 1

    def add_deck(self):
        dialog = CustomInputDialog(title="New Deck Form", text="Enter deck name:")
        deck_name = dialog.get_input()
        if deck_name:
            db = Database()
            deck_id = db.create_deck(self.user_id, deck_name)
            if deck_id:
                self.display_decks()
                if hasattr(self, 'sidebar'):
                    self.sidebar.load_decks()

    def edit_deck(self, deck_id, current_name):
        dialog = CustomInputDialog(
            title="Edit Deck",
            text="Enter new deck name:",
            initial_value=current_name
        )
        new_name = dialog.get_input()
        
        if new_name:
            db = Database()
            db.update_deck_name(deck_id, new_name)
            self.display_decks()
            if hasattr(self, 'sidebar'):
                self.sidebar.load_decks()

    def delete_deck(self, deck_id):
        if messagebox.askyesno("Delete Deck", "Are you sure you want to delete this deck?"):
            db = Database()
            db.delete_deck(deck_id)
            self.display_decks()
            if hasattr(self, 'sidebar'):
                self.sidebar.load_decks()
            
    def toggle_deck_selection(self, deck_id, is_selected):
        if is_selected:
            self.selected_decks.add(deck_id)
        else:
            self.selected_decks.remove(deck_id)
            
        # update delete button state
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
                self.sidebar.load_decks()
            self.delete_button.configure(state="disabled")

class DeckContainer(ctk.CTkFrame):
    def __init__(self, master, deck_id, deck_name, card_count, selection_callback):
        super().__init__(master, fg_color="white", corner_radius=8)
        self.configure(border_width=1, border_color="#E5E7EB")
        self.deck_id = deck_id
        self.selection_callback = selection_callback
        self.selected = False
        
        # make the entire container clickable
        self.bind("<Button-1>", self.toggle_selection)
        
        # content frame
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        content_frame.bind("<Button-1>", self.toggle_selection)
        
        # title and count
        title_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="both", expand=True)
        
        ctk.CTkLabel(
            title_frame,
            text=deck_name,
            font=("Inter", 16, "bold"),
            text_color="black"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text=f"{card_count} cards",
            font=("Inter", 14),
            text_color="#6B7280"
        ).pack(anchor="w", pady=(5, 0))
        
        # csheckbox
        self.checkbox = ctk.CTkCheckBox(
            content_frame,
            text="",
            width=24,
            height=24,
            corner_radius=6,
            fg_color="#4F46E5",
            hover_color="#4338CA",
            command=self.on_checkbox_click
        )
        self.checkbox.pack(side="right")

    def toggle_selection(self, event=None):
        self.selected = not self.selected
        self.checkbox.select() if self.selected else self.checkbox.deselect()
        self.selection_callback(self.deck_id, self.selected)
        self.configure(fg_color="#F5F3FF" if self.selected else "white")

    def on_checkbox_click(self):
        self.toggle_selection()


class QuizPage(ctk.CTkFrame):
    def __init__(self, master, user_id, session, switch_page):
        super().__init__(master, corner_radius=0, fg_color="white")
        self.pack(fill="both", expand=True)
        
        self.user_id = user_id
        self.session = session
        self.switch_page = switch_page
        self.selected_decks = set()
        
        # get username from database
        db = Database()
        self.username = db.get_username(self.user_id)
        
        # create sidebar
        self.sidebar = Sidebar(self, switch_page, self.username, self.user_id, self.session)
        self.sidebar.pack(side="left", fill="y")
        
        # main content area
        self.main_content = ctk.CTkFrame(self, fg_color="white")
        self.main_content.pack(side="left", fill="both", expand=True)
        
        # header frame with "Start Quiz" button
        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 0))
        
        ctk.CTkLabel(
            header_frame,
            text="Quiz",
            font=("Inter", 24, "bold"),
            text_color="black"
        ).pack(side="left")
        
        self.start_button = ctk.CTkButton(
            header_frame,
            text="Start Quiz",
            width=120,
            height=32,
            corner_radius=16,
            fg_color="#4F46E5",
            hover_color="#4338CA",
            state="disabled",
            command=self.start_quiz
        )
        self.start_button.pack(side="right", padx=5)
        
        # add separator line
        separator = ctk.CTkFrame(self.main_content, height=1, fg_color="#E5E7EB")
        separator.pack(fill="x", padx=30, pady=(20, 0))
        
        # deck selection area
        self.create_deck_selection()

    def toggle_deck_selection(self, deck_id, selected):
        if selected:
            self.selected_decks.add(deck_id)
        else:
            self.selected_decks.discard(deck_id)
            
        # update start button state
        self.start_button.configure(
            state="normal" if self.selected_decks else "disabled"
        )

    def start_quiz(self):
        if not self.selected_decks:
            messagebox.showwarning("Warning", "Please select at least one deck")
            return
        
        # destroy all children of master first
        for widget in self.master.winfo_children():
            widget.destroy()
            
        QuizSession(
            self.master,
            self.user_id,
            list(self.selected_decks)[0],
            list(self.selected_decks),
            self.session,
            self.switch_page
        )

    def create_deck_selection(self):
        # container for deck selection
        selection_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        selection_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # instructions
        ctk.CTkLabel(
            selection_frame,
            text="Select decks to quiz yourself on:",
            font=("Inter", 16, "bold"),
            text_color="black"
        ).pack(anchor="w", pady=(0, 20))
        
        # Deck grid container
        self.decks_frame = ctk.CTkFrame(selection_frame, fg_color="transparent")
        self.decks_frame.pack(fill="both", expand=True)
        self.decks_frame.grid_columnconfigure((0, 1, 2), weight=1, pad=20)
        
        # load decks
        self.load_decks()

    def load_decks(self):
        # clear existing decks
        for widget in self.decks_frame.winfo_children():
            widget.destroy()
            
        # get decks from database
        db = Database()
        decks = db.get_decks(self.user_id)
        
        row = 0
        col = 0
        for deck_id, deck_name in decks:
            card_count = db.get_card_count(deck_id)
            quiz_deck = QuizDeckContainer(
                self.decks_frame,
                deck_id,
                deck_name,
                card_count,
                self.toggle_deck_selection
            )
            quiz_deck.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            
            col += 1
            if col > 1:
                col = 0
                row += 1
                
        # Update start button state
        self.start_button.configure(
            state="normal" if self.selected_decks else "disabled"
        )


##############################################################CARDS PAGE#############################################################
class CardsPage(ctk.CTkFrame):
    def __init__(self, master, user_id, deck_id, session, switch_page: Callable):
        super().__init__(master, corner_radius=0, fg_color="white")
        self.user_id = user_id
        self.deck_id = deck_id
        self.session = session
        self.switch_page = switch_page

        # get username from database User-Defined OOP - example of association
        db = Database()
        self.username = db.get_username(self.user_id)
        self.deck_info = db.get_deck_info(self.deck_id)

        # greate sidebar - example of instantiation
        self.sidebar = Sidebar(self, switch_page, self.username, self.user_id, self.session)
        self.sidebar.pack(side="left", fill="y")

        # main content area
        self.main_content = ctk.CTkFrame(self, fg_color="white")
        self.main_content.pack(side="left", fill="both", expand=True)

        # header frame
        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=20)
        
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

        # add card button
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

        # cards container
        self.cards_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.cards_frame.pack(fill="both", expand=True, padx=30)
        
        self.display_cards()

    def add_card(self):
        dialog = CardCreationDialog(self, deck_id=self.deck_id)
        dialog.grab_set()

    def edit_card(self, card_id):
        try:
            db = Database()
            card = db.get_card(card_id)  # expecting a dictionary now
            edit_dialog = EditCardDialog(
                self,
                card_id,
                card['question'],  # use dictionary keys
                card['answer']
            )
            edit_dialog.focus()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit card: {str(e)}")



    def delete_card(self, card_id):
        if messagebox.askyesno("Delete Card", "Are you sure you want to delete this card?"):
            db = Database()
            db.delete_card(card_id)
            self.display_cards()

    def display_cards(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        
        db = Database()
        cards = db.get_cards(self.deck_id)
        print(cards)
        if not cards:
            self.show_empty_state()
            return
        
        for card in cards:
            card_container = CardContainer(
                self.cards_frame,
                card_id=card[0],
                question=card[2],
                answer=card[3],
                edit_callback=self.edit_card,
                delete_callback=self.delete_card
            )
            card_container.pack(fill="x", pady=10)

    def show_empty_state(self):
        empty_frame = ctk.CTkFrame(self.cards_frame, fg_color="white")
        empty_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            empty_frame,
            text="No cards yet",
            font=("Inter", 16, "bold"),
            text_color="#6B7280"
        ).pack(pady=(20, 5))
        
        ctk.CTkLabel(
            empty_frame,
            text="Create your first card to get started",
            font=("Inter", 14),
            text_color="#6B7280"
        ).pack()

class CardContainer(ctk.CTkFrame):
    def __init__(self, master, card_id, question, answer, edit_callback, delete_callback):
        super().__init__(
            master, 
            fg_color="white", 
            corner_radius=12,
            border_width=1,
            border_color="#E5E7EB"
        )
        
        # content frame
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=15)
        
        # left side: Text content
        text_frame = ctk.CTkFrame(content, fg_color="transparent")
        text_frame.pack(side="left", fill="x", expand=True)
        
        # question and answer with black text
        ctk.CTkLabel(
            text_frame, 
            text=question, 
            font=("Inter", 16, "bold"),
            text_color="black"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            text_frame, 
            text=answer, 
            font=("Inter", 14),
            text_color="black"
        ).pack(anchor="w", pady=(5,0))
        
        # buttons frame
        buttons_frame = ctk.CTkFrame(text_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10,0))
        
        # edit button - matches Add Card style
        ctk.CTkButton(
            buttons_frame,
            text="Edit",
            width=70,
            height=32,
            corner_radius=16,
            fg_color=("#F3F4F6"),
            text_color=("black"),
            hover_color=("#E5E7EB"),
            command=lambda: edit_callback(card_id)
        ).pack(side="left", padx=5)
        
        # delete button - matches deck delete style
        ctk.CTkButton(
            buttons_frame,
            text="Delete",
            width=70,
            height=32,
            corner_radius=16,
            fg_color=("#FEE2E2"),
            text_color=("#DC2626"),
            hover_color=("#FECACA"),
            command=lambda: delete_callback(card_id)
        ).pack(side="left", padx=5)
        

class CardCreationDialog(ctk.CTkToplevel):
    def __init__(self, parent, deck_id):
        super().__init__(parent)
        self.title("Create New Card")
        self.geometry("500x800")
        self.attributes('-topmost', True) 
        self.parent = parent
        self.deck_id = deck_id
        
        # main scrollable container
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="white",
            width=480,
            height=780
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # question section
        self.create_question_section()
        
        # answer section
        self.create_answer_section()
        
        # save button
        self.save_button = ctk.CTkButton(
            self.scroll_frame,
            text="Save Card",
            command=self.save,
            fg_color="green",
            text_color="white"
        )
        self.save_button.pack(fill="x", padx=20, pady=(20, 10))
        
    def save(self):
        question = self.question_entry.get("1.0", "end-1c").strip()
        answer = self.answer_entry.get("1.0", "end-1c").strip()
        
        if not question or not answer:
            messagebox.showwarning("Warning", "Please fill in both question and answer")
            return
        
        try:
            db = Database()
            db.create_card(self.deck_id, question, answer)
            self.parent.display_cards()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save card: {str(e)}")
    
    def create_question_section(self):
        # Question label
        ctk.CTkLabel(
            self.scroll_frame,
            text="Question:",
            font=("Inter", 14, "bold"),
            text_color="black"
        ).pack(fill="x", padx=20, pady=(20,5))
        
        # Question text entry
        self.question_entry = ctk.CTkTextbox(
            self.scroll_frame,
            height=100,
            border_width=1,
            border_color="#E5E7EB"
        )
        self.question_entry.pack(fill="x", padx=20, pady=(0,10))
    
    def create_answer_section(self):
        # similar structure for answer section
        ctk.CTkLabel(
            self.scroll_frame,
            text="Answer:",
            font=("Inter", 14, "bold"),
            text_color="black"
        ).pack(fill="x", padx=20, pady=(20,5))
        
        self.answer_entry = ctk.CTkTextbox(
            self.scroll_frame,
            height=100,
            border_width=1,
            border_color="#E5E7EB"
        )
        self.answer_entry.pack(fill="x", padx=20, pady=(0,10))
        


class EditCardDialog(ctk.CTkToplevel):
    def __init__(self, parent, card_id, current_question, current_answer):
        super().__init__(parent)
        self.title("Edit Card")
        self.geometry("500x800")
        self.attributes('-topmost', True)
        self.parent = parent
        self.card_id = card_id
        
        # main scrollable container
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="white",
            width=480,
            height=780
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # create UI sections for question and answer
        self.create_question_section()
        self.create_answer_section()
        
        # save button to commit changes
        self.save_button = ctk.CTkButton(
            self.scroll_frame,
            text="Save Changes",
            command=self.save_card,
            fg_color="green",
            text_color="white"
        )
        self.save_button.pack(fill="x", padx=20, pady=(20, 10))
        
        # pre-populate the textboxes with the current question and answer
        self.question_entry.insert("1.0", current_question)
        self.answer_entry.insert("1.0", current_answer)
    
    def create_question_section(self):
        ctk.CTkLabel(
            self.scroll_frame,
            text="Question:",
            font=("Inter", 14, "bold"),
            text_color="black"
        ).pack(fill="x", padx=20, pady=(20, 5))
        
        self.question_entry = ctk.CTkTextbox(
            self.scroll_frame,
            height=100,
            border_width=1,
            border_color="#E5E7EB"
        )
        self.question_entry.pack(fill="x", padx=20, pady=(0, 10))
    
    def create_answer_section(self):
        ctk.CTkLabel(
            self.scroll_frame,
            text="Answer:",
            font=("Inter", 14, "bold"),
            text_color="black"
        ).pack(fill="x", padx=20, pady=(20, 5))
        
        self.answer_entry = ctk.CTkTextbox(
            self.scroll_frame,
            height=100,
            border_width=1,
            border_color="#E5E7EB"
        )
        self.answer_entry.pack(fill="x", padx=20, pady=(0, 10))
    
    def save_card(self):
        new_question = self.question_entry.get("1.0", "end-1c").strip()
        new_answer = self.answer_entry.get("1.0", "end-1c").strip()
        
        if not new_question or not new_answer:
            messagebox.showwarning("Warning", "Please fill in both question and answer")
            return
        
        try:
            db = Database()
            db.update_card(self.card_id, new_question, new_answer)
            # Refresh the card list if the parent supports it
            if hasattr(self.parent, 'display_cards'):
                self.parent.display_cards()
            self.destroy()  # Close the dialog
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update card: {str(e)}")


################################################ANALYTICS PAGE#########################################################################

class AnalyticsPage(ctk.CTkFrame):
    def __init__(self, master, user_id, session, switch_page):
        super().__init__(master, corner_radius=0, fg_color="#ffffff")
        self.pack(fill="both", expand=True)
        
        self.user_id = user_id
        self.session = session
        self.switch_page = switch_page
        
        db = Database()
        # use the aggregated stats method instead of get_user_stats.
        self.stats = db.get_aggregated_quiz_stats(self.user_id)
        
        # create sidebar
        self.sidebar = Sidebar(self, switch_page, db.get_username(self.user_id), self.user_id, self.session)
        self.sidebar.pack(side="left", fill="y")
        
        # main content area (we remove the graphs and only display stats)
        self.main_content = ctk.CTkFrame(self, fg_color="white")
        self.main_content.pack(side="left", fill="both", expand=True)
        
        # header
        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkLabel(
            header_frame,
            text="Analytics",
            font=("Inter", 24, "bold"),
            text_color="black"
        ).pack(side="left")
        
        # create a simple stats display
        stats_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        stats_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # define a list of stat tuples to display
        stat_items = [
            ("Total Sessions", f"{self.stats['session_count']}"),
            ("Total Cards Reviewed", f"{self.stats['total_cards']}"),
            ("Total Correct Answers", f"{self.stats['total_correct']}"),
            ("Overall Accuracy", f"{self.stats['avg_accuracy']:.1f}%"),
            ("Total Time (s)", f"{self.stats['total_time']:.1f}s"),
            ("Avg Time per Card (s)", f"{self.stats['overall_avg_time_per_card']:.1f}s")
        ]
        
        for label, value in stat_items:
            stat_frame_inner = ctk.CTkFrame(stats_frame, fg_color="transparent")
            stat_frame_inner.pack(pady=10)
            ctk.CTkLabel(
                stat_frame_inner,
                text=label,
                font=("Inter", 14),
                text_color="#4B5563"
            ).pack(side="left", padx=5)
            ctk.CTkLabel(
                stat_frame_inner,
                text=value,
                font=("Inter", 14, "bold"),
                text_color="black"
            ).pack(side="left", padx=5)
        
        # return button to go back to the dashboard (which is decks page by default)
        ctk.CTkButton(
            self.main_content,
            text="Return to Dashboard",
            width=200,
            height=40,
            corner_radius=16,
            fg_color="#F3F4F6",
            text_color="black",
            hover_color="#E5E7EB",
            command=lambda: self.switch_page(DecksPage, user_id=self.user_id, session=self.session, switch_page=self.switch_page)
        ).pack(pady=40)



#######################################################################QUIZ PAGE#######################################################

class QuizPage(ctk.CTkFrame):
    def __init__(self, master, user_id, session, switch_page):
        super().__init__(master, corner_radius=0, fg_color="white")
        self.pack(fill="both", expand=True)
        
        self.user_id = user_id
        self.session = session
        self.switch_page = switch_page
        self.selected_decks = set()
        
        # get username from database
        db = Database()
        self.username = db.get_username(self.user_id)
        
        # create sidebar
        self.sidebar = Sidebar(self, switch_page, self.username, self.user_id, self.session)
        self.sidebar.pack(side="left", fill="y")
        
        # main content area
        self.main_content = ctk.CTkFrame(self, fg_color="white")
        self.main_content.pack(side="left", fill="both", expand=True)
        
        # header frame with Start Quiz button
        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 0))
        
        ctk.CTkLabel(
            header_frame,
            text="Quiz",
            font=("Inter", 24, "bold"),
            text_color="black"
        ).pack(side="left")
        
        self.start_button = ctk.CTkButton(
            header_frame,
            text="Start Quiz",
            width=120,
            height=32,
            corner_radius=16,
            fg_color="#4F46E5",
            hover_color="#4338CA",
            state="disabled",
            command=self.start_quiz
        )
        self.start_button.pack(side="right", padx=5)
        
        # add separator line
        separator = ctk.CTkFrame(self.main_content, height=1, fg_color="#E5E7EB")
        separator.pack(fill="x", padx=30, pady=(20, 0))
        
        # deck selection area
        self.create_deck_selection()

    def toggle_deck_selection(self, deck_id, selected):
        if selected:
            self.selected_decks.add(deck_id)
        else:
            self.selected_decks.discard(deck_id)
            
        # update start button state
        self.start_button.configure(
            state="normal" if self.selected_decks else "disabled"
        )

    def start_quiz(self):
        if not self.selected_decks:
            messagebox.showwarning("Warning", "Please select at least one deck")
            return
        
        # destroy all children of master first
        for widget in self.master.winfo_children():
            widget.destroy()
            
        QuizSession(
            self.master,
            self.user_id,
            list(self.selected_decks)[0],
            list(self.selected_decks),
            self.session,
            self.switch_page
        )

    def create_deck_selection(self):
        # container for deck selection
        selection_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        selection_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # instructions
        ctk.CTkLabel(
            selection_frame,
            text="Select decks to quiz yourself on:",
            font=("Inter", 16, "bold"),
            text_color="black"
        ).pack(anchor="w", pady=(0, 20))
        
        # deck grid container
        self.decks_frame = ctk.CTkFrame(selection_frame, fg_color="transparent")
        self.decks_frame.pack(fill="both", expand=True)
        self.decks_frame.grid_columnconfigure((0, 1, 2), weight=1, pad=20)
        
        # load decks
        self.load_decks()

    def load_decks(self):
        # clear existing decks
        for widget in self.decks_frame.winfo_children():
            widget.destroy()
            
        # get decks from database
        db = Database()
        decks = db.get_decks(self.user_id)
        
        row = 0
        col = 0
        for deck_id, deck_name in decks:
            card_count = db.get_card_count(deck_id)
            quiz_deck = QuizDeckContainer(
                self.decks_frame,
                deck_id,
                deck_name,
                card_count,
                self.toggle_deck_selection
            )
            quiz_deck.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            
            col += 1
            if col > 1:
                col = 0
                row += 1
                
        # update start button state if decks 
        self.start_button.configure(
            state="normal" if self.selected_decks else "disabled"
        )


class QuizDeckContainer(ctk.CTkFrame):
    def __init__(self, master, deck_id, deck_name, card_count, toggle_callback):
        super().__init__(master, fg_color="white", corner_radius=8)
        self.configure(border_width=1, border_color="#E5E7EB")
        
        self.deck_id = deck_id
        self.toggle_callback = toggle_callback
        self.selected = False
        
        # content frame
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # title and count
        title_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="both", expand=True)
        
        ctk.CTkLabel(
            title_frame,
            text=deck_name,
            font=("Inter", 16, "bold"),
            text_color="black"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text=f"{card_count} cards",
            font=("Inter", 14),
            text_color="#6B7280"
        ).pack(anchor="w", pady=(5, 0))
        
        # checkbox
        self.checkbox = ctk.CTkCheckBox(
            content_frame,
            text="",
            width=24,
            height=24,
            corner_radius=6,
            fg_color="#4F46E5",
            hover_color="#4338CA",
            command=self.on_checkbox_click
        )
        self.checkbox.pack(side="right")
        
        # make the entire container clickable
        self.bind("<Button-1>", self.toggle_selection)
        content_frame.bind("<Button-1>", self.toggle_selection)
        title_frame.bind("<Button-1>", self.toggle_selection)

    def toggle_selection(self, event=None):
        self.selected = not self.selected
        self.checkbox.select() if self.selected else self.checkbox.deselect()
        self.toggle_callback(self.deck_id, self.selected)
        self.configure(fg_color="#F5F3FF" if self.selected else "white")

    def on_checkbox_click(self):
        self.toggle_selection()


class QuizSession(ctk.CTkFrame):
    def __init__(self, master, user_id, deck_id, deck_ids, session, switch_page):
        super().__init__(master, corner_radius=0, fg_color="white")
        self.pack(fill="both", expand=True)
        
         # store instance variables
        self.user_id = user_id
        self.deck_id = deck_id      
        self.deck_ids = deck_ids    
        self.session = session
        self.switch_page = switch_page
        
        # quiz state
        self.current_index = 0
        self.start_time = datetime.now()
        self.card_start_time = None
        self.correct_count = 0
        self.total_time = 0
        
        from helpers import HelperFunctions
        db = Database()
        self.cards = []
        for d in self.deck_ids:
            # assume get_cards_for_review returns tuples with difficulty as the fourth element
            self.cards.extend(db.get_cards_for_review(d))

        # print the unsorted difficulties for debugging
        print("before sort:")
        for card in self.cards:
            print("card id:", card[0], "difficulty:", card[3])

        # sort the cards from highest to lowest difficulty using the merge sort implementation
        self.cards = HelperFunctions.merge_sort_cards(self.cards)

        # print the sorted difficulties for debugging
        print("after sort:")
        for card in self.cards:
            print("card id:", card[0], "difficulty:", card[3])

        if not self.cards:
            self.show_no_cards_message()
            return

        deck_names = []
        for d in deck_ids:
            info = db.get_deck_info(d)
            if info:
                deck_names.append(info["name"])
        self.session_title = "Quiz Session - " + ", ".join(deck_names)

        if not self.cards:
            self.show_no_cards_message()
            return
                
        self.setup_ui()  # creates UI components 
        self.update_timer()
        self.display_card()
        
    def setup_ui(self):
        # create the header frame with a left and right section.
        self.header = ctk.CTkFrame(self, fg_color="#F3F4F6", height=60)
        self.header.pack(fill="x", pady=(0, 20))
        self.header.pack_propagate(False)
        
        # left side: display the session title
        self.title_label = ctk.CTkLabel(
            self.header,
            text=self.session_title,
            font=("Inter", 18, "bold"),
            text_color="black"
        )
        self.title_label.pack(side="left", padx=30)
        
        # right side: create a container for progress and timer.
        right_frame = ctk.CTkFrame(self.header, fg_color="#F3F4F6", width=200)
        right_frame.pack(side="right", padx=30)
        right_frame.pack_propagate(False)
        
        # progress label
        self.progress_label = ctk.CTkLabel(
            right_frame,
            text=f"Card 1/{len(self.cards)}",
            font=("Inter", 14),
            text_color="#4B5563"
        )
        self.progress_label.pack()
        
        # timer label (updated per second)
        self.timer_label = ctk.CTkLabel(
            right_frame,
            text="Time Elapsed: 00:00:00",
            font=("Inter", 14),
            text_color="#4B5563"
        )
        self.timer_label.pack()
        
        # main content area for the question/answer.
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
        
        # answer area (initially hidden)
        self.answer_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.answer_label = ctk.CTkLabel(
            self.answer_frame,
            text="",
            font=("Inter", 16),
            text_color="black",
            wraplength=600
        )
        self.answer_label.pack(pady=20)
        
        # show Answer button
        self.show_answer_btn = ctk.CTkButton(
            self.content,
            text="Show Answer",
            width=120,
            height=32,
            command=self.show_answer
        )
        self.show_answer_btn.pack(pady=20)
        
        # rating frame for four difficulty options
        self.rating_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        # define options: (button text, difficulty weight, button color)
        ratings = [
            ("Very Hard", 4, "#DC2626"),
            ("Hard", 3, "#FECACA"),
            ("Easy", 2, "#10B981"),
            ("Very Easy", 1, "#A3E635")
        ]
        for text, weight, color in ratings:
            btn = ctk.CTkButton(
                self.rating_frame,
                text=text,
                width=100,
                height=32,
                fg_color=color,
                hover_color=color,
                command=lambda w=weight: self.rate_card_difficulty(w)
            )
            btn.pack(side="left", padx=10)

    
    def display_card(self):
        #hide answer and rating, show answer button
        self.answer_frame.pack_forget()
        self.rating_frame.pack_forget()
        self.show_answer_btn.pack(pady=20)
        
        # get current card (in tuple form (card_id, question, answer))
        card = self.cards[self.current_index]
        
        self.question_label.configure(text=card[1])  # question
        self.answer_label.configure(text=card[2])    # answer
        
        self.progress_label.configure(
            text=f"Card {self.current_index + 1}/{len(self.cards)}"
        )
        
        # start timing this card
        self.card_start_time = datetime.now()
        
    def show_answer(self):
        self.show_answer_btn.pack_forget()
        self.answer_frame.pack()
        self.rating_frame.pack(pady=20)
        
    # def rate_card(self, is_correct):
    #     # calculate time taken for the card
    #     time_taken = (datetime.now() - self.card_start_time).total_seconds()
        
    #     # get current card ID (assuming card tuple: (card_id, question, answer))
    #     card_id = self.cards[self.current_index][0]
        
    #     # save quiz result
    #     db = Database()
    #     db.save_quiz_result(
    #         self.user_id,
    #         self.deck_id,
    #         card_id,
    #         is_correct,
    #         time_taken
    #     )
        
    #     # update stats
    #     if is_correct:
    #         self.correct_count += 1
    #     self.total_time += time_taken
        
    #     # move to next card or finish quiz
    #     self.current_index += 1
    #     if self.current_index < len(self.cards):
    #         self.display_card()
    #     else:
    #         self.end_quiz()


    # method to handle the difficulty rating of the current card
    def rate_card_difficulty(self, difficulty_weight):
        # calculate time taken for the current card
        time_taken = (datetime.now() - self.card_start_time).total_seconds()
        # get the current card (assumed tuple format: (card_id, question, answer, difficulty))
        current_card = self.cards[self.current_index]
        card_id = current_card[0]
        # update the card's difficulty in the database using the new method
        db = Database()
        db.update_card_difficulty(card_id, difficulty_weight)
        # optionally, record additional quiz result info if desired
        self.total_time += time_taken
        # move to the next card
        self.current_index += 1
        if self.current_index < len(self.cards):
            self.display_card()
        else:
            self.end_quiz()

            
    def end_quiz(self):
        total_cards = len(self.cards)
        accuracy = (self.correct_count / total_cards) * 100
        avg_time = self.total_time / total_cards
        
        # save session stats 
        db = Database()
        db.save_session_stats(
            self.user_id,
            self.deck_id,
            accuracy,
            avg_time,
            total_cards,
            self.correct_count,
            self.total_time
        )
        
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
            ctk.CTkLabel(
                stat_frame,
                text=label,
                font=("Inter", 14),
                text_color="#4B5563"
            ).pack(side="left", padx=5)
            ctk.CTkLabel(
                stat_frame,
                text=value,
                font=("Inter", 14, "bold"),
                text_color="black"
            ).pack(side="left", padx=5)
        
        # "return to quiz" page button
        ctk.CTkButton(
            summary,
            text="Return to Quiz",
            corner_radius=16,
            fg_color="#F3F4F6",
            text_color="black",
            hover_color="#E5E7EB",
            command=lambda: self.switch_page(
                QuizPage,
                user_id=self.user_id,
                session=self.session,
                switch_page=self.switch_page
            )
        ).pack(pady=40)
        
    def show_no_cards_message(self):
        for widget in self.winfo_children():
            widget.destroy()
            
        message_frame = ctk.CTkFrame(self, fg_color="white")
        message_frame.pack(expand=True, fill="both", padx=30, pady=20)
        
        ctk.CTkLabel(
            message_frame,
            text="No cards available for review!",
            font=("Inter", 18, "bold"),
            text_color="black"
        ).pack(expand=True)
        
        ctk.CTkButton(
            message_frame,
            text="Return to Quiz",
            width=200,
            height=40,
            command=lambda: self.switch_page(
                QuizPage,
                user_id=self.user_id,
                session=self.session,
                switch_page=self.switch_page
            )
        ).pack(pady=20)


    def update_timer(self):
        # if the timer label no longer exists, don't try to update it.
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
        except Exception as e:
            return
        self.after(1000, self.update_timer)