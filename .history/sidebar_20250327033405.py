import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from database import Database

class Sidebar(ctk.CTkFrame):
    # initialises the sidebar as a subclass of CTkFrame (inheritance)
    # CTkFrame is allows sidebar to be a widget on the screen
    def __init__(self, master, switch_page, user_id, db):
        super().__init__(master, fg_color="white", width=250, corner_radius=0, border_width=0, border_color="#E5E7EB")

        self.switch_page = switch_page
        self.user_id = user_id
        self.db = db
        show_decks = True # show decks is true by default so the sidebar always shows all the decks the user has

        self.right_border = ctk.CTkFrame(self, width=1, fg_color="#E5E7EB", corner_radius=0)
        self.right_border.pack(side="right", fill="y")

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(side="left", fill="both", expand=True)
        
        nav_container = ctk.CTkFrame(self.content, fg_color="transparent")
        nav_container.pack(fill="x", expand=False)

        logo = ctk.CTkFrame(nav_container, fg_color="transparent")
        logo.pack(fill="x", pady=(20, 20), padx=20)
        logo_image = ctk.CTkImage(light_image=Image.open("images/logo.png"), size=(32, 32))
        ctk.CTkLabel(logo, image=logo_image, text="").pack(side="left")
        ctk.CTkLabel(logo, text="Flow Space", font=("Inter", 20, "bold"), text_color="black").pack(side="left", padx=10)

        self.create_buttons(nav_container, show_decks)

        user_info = db.get_user(self.user_id)
        if user_info:
            username = user_info["username"]
        else:
            username = "User"
        # Removed db.close() so that the shared connection remains open
        self.create_bottom_section(username)

    def create_buttons(self, parent, show_decks):
        # circular import happens because all pages inherit from BasePage (in components.py),
        # which imports sidebar, and sidebar tries to import the pages again
        # To solve this __import__ is used, which is a lazy import technique used here so that the pages are
        # only imported when the buttons to go to them are clicked
        nav_items = [
            # decks page nav button
            ("My decks", "images/decks_icon.png",
             lambda: self.switch_page(__import__('app').DecksPage, user_id=self.user_id, switch_page=self.switch_page, db=self.db)),
            # quiz page nav button
            ("Quiz yourself", "images/quiz_icon.png",
             lambda: self.switch_page(__import__('app').QuizPage, user_id=self.user_id, switch_page=self.switch_page, db=self.db)),
            # analytics page nav button
            ("Analytics", "images/analytics_icon.png",
             lambda: self.switch_page(__import__('app').AnalyticsPage, user_id=self.user_id, switch_page=self.switch_page, db=self.db)),
            # settings page nav button
            ("Settings", "images/settings_icon.png",
             lambda: self.switch_page(__import__('app').SettingsPage, user_id=self.user_id, switch_page=self.switch_page, db=self.db))
        ]
        # loop through nav items and create buttons
        print(list(enumerate(nav_items)))
        for x, (text, icon_path, command) in enumerate(nav_items):
            # creates each individual button with its styling defined in create_button()
            button = self.create_button(parent, text, icon_path, command)
            # give my decks different top padding to separate it from the title text ("Flow Space")
            if x == 0:
                button.pack(fill="x", padx=20, pady=(0, 5))
                self.deck_container = ctk.CTkFrame(parent, fg_color="transparent", height=0)
                self.deck_container.pack(fill="x", expand=False)
                # if show_decks is True, update the deck list to display directly under my decks button
                if show_decks:
                    self.update_deck_list()
            else:
                button.pack(fill="x", padx=20, pady=5)  # all other buttons are added to the sidebar

    # defines styling for each individual button
    def create_button(self, parent, text, icon_path, command): 
        return ctk.CTkButton(
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
    
    # creates the bottom section of the sidebar with the purple profile icon, the initial inside of it, the username next to it and the logout button
    def create_bottom_section(self, username):
        user_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        user_frame.pack(side="bottom", fill="x", pady=20, padx=20)
        profile_icon_frame = ctk.CTkFrame(user_frame, fg_color="transparent")
        profile_icon_frame.pack(side="left", fill="y")
        first_letter = username[0].upper()
        profile_icon = ctk.CTkLabel(profile_icon_frame,
            text=first_letter,
            width=40,
            height=40,
            fg_color="#4F46E5",
            text_color="white",
            font=("Inter", 16, "bold"),
            corner_radius=20)
        profile_icon.pack(side="left", pady=4)
        ctk.CTkLabel(profile_icon_frame,
            text=username,
            font=("Inter", 16),
            text_color="black").pack(side="left", padx=12, pady=4)
        logout_image = ctk.CTkImage( 
            light_image=Image.open("images/logout.png"), 
            dark_image=Image.open("images/logout.png"), 
            size=(16, 16))
        ctk.CTkButton(user_frame,
            text="",
            image=logout_image,
            width=36,
            height=36,
            corner_radius=18,
            fg_color="#F3F4F6",
            hover_color="#e5e7eb",
            command=self.logout).pack(side="right", pady=4)

    
    def update_deck_list(self):
        # destroys all current decks in deck_container
        for widget in self.deck_container.winfo_children():
            widget.destroy()

        # Use the shared database instance instead of creating a new one
        decks = self.db.get_decks(self.user_id)

        if decks:
            deck_list = []
            for deck_id, deck_name in decks:
                # retrieves cards for each deck
                cards = self.db.get_cards(deck_id)
                if cards:
                    total_ef = 0
                    # calculates average ef by getting each card's easiness from database,
                    # adding them together (total_ef) and dividing by number of cards (len(cards))
                    for card in cards:
                        total_ef += self.db.get_card_easiness(self.user_id, card[0])
                    avg_ef = total_ef / len(cards)
                else:
                    # if card doesn't have ef, uses 2.5 as default value
                    avg_ef = 2.5

                # appends deck id, deck name and average ef to deck list
                deck_list.append((deck_id, deck_name, avg_ef))
            
            # sorts deck list by ascending ef
            # works by looping through deck_list, passing each tuple in it to get_ef, which returns a list of ef like [0, 2, 1.2]
            # once all ef are gathered into the list, sort() function sorts deck_list in ascending order of these efs
            def get_ef(deck):
                return deck[2]
            deck_list.sort(key=get_ef)

            # create a scrollable frame for decks to be displayed in
            decks_frame = ctk.CTkScrollableFrame(
                self.deck_container,
                fg_color="transparent",
                height=min(len(deck_list) * 36, 108), # calculates the pixel height if each deck gets a height of 36px, making sure to not exceed a height of 108px
                width=210,
                scrollbar_button_color="#E5E7EB",
                scrollbar_button_hover_color="#D1D5DB"
            )
            decks_frame.pack(fill="x", padx=20, pady=(0, 10))

            # imports cards page here to avoid circular imports at the top
            from app import CardsPage
            
            # iterate through deck id and deck name in deck list and make a button for each deck
            for deck_id, deck_name, _ in deck_list:
                deck = ctk.CTkFrame(decks_frame, fg_color="transparent", height=36)
                deck.pack(fill="x", expand=False)
                deck.pack_propagate(False)

                deck_btn = ctk.CTkButton(
                    deck,
                    text=deck_name,
                    fg_color="transparent",
                    text_color="#6B7280",
                    hover_color="#F3F4F6",
                    anchor="w",
                    height=35,
                    command=lambda d_id=deck_id: self.switch_page(CardsPage, user_id=self.user_id, deck_id=d_id, switch_page=self.switch_page)
                )
                deck_btn.pack(fill="x", pady=(0, 1))


    # asks the user if they want to logout (yes or no)
    # if yes, switches page to login page
    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.current_user = None  # Clear the stored user info
            from login import LoginPage
            self.switch_page(LoginPage)
