# sidebar.py
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from database import Database
# Removed: from app import CardsPage, DecksPage, QuizPage, AnalyticsPage

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, switch_page, username: str, user_id: int):
        super().__init__(master,
                         fg_color="white",
                         width=250,
                         corner_radius=0,
                         border_width=0,
                         border_color="#E5E7EB")
        self.pack_propagate(False)
        self.grid_propagate(False)

        # Create right border
        self.right_border = ctk.CTkFrame(self, width=1, fg_color="#E5E7EB", corner_radius=0)
        self.right_border.pack(side="right", fill="y")

        # Main content container
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(side="left", fill="both", expand=True)

        self.switch_page = switch_page
        self.user_id = user_id

        # For simplicity, assume show_decks is True
        show_decks = True

        # Logo and navigation container
        nav_container = ctk.CTkFrame(self.content, fg_color="transparent")
        nav_container.pack(fill="x", expand=False)

        # Logo frame
        logo_frame = ctk.CTkFrame(nav_container, fg_color="transparent")
        logo_frame.pack(fill="x", pady=(20, 20), padx=20)
        logo_image = ctk.CTkImage(light_image=Image.open("images/logo.png"), size=(32, 32))
        ctk.CTkLabel(logo_frame, image=logo_image, text="").pack(side="left")
        ctk.CTkLabel(logo_frame,
                     text="Flow Space",
                     font=("Inter", 20, "bold"),
                     text_color="black").pack(side="left", padx=10)

        # Navigation buttons
        self.create_nav_buttons(nav_container, show_decks)
        # User info at bottom
        self.create_user_section(username)

    def create_nav_buttons(self, parent, show_decks):
        decks_button = self.create_decks_button(parent)
        decks_button.pack(fill="x", padx=20, pady=(0, 5))

        self.deck_container = ctk.CTkFrame(parent, fg_color="transparent", height=0)
        self.deck_container.pack(fill="x", expand=False)
        if show_decks:
            self.update_deck_list()

        nav_items = [
            # Lazy import inside lambda for QuizPage
            ("Quiz yourself", "images/quiz_icon.png",
             lambda: self.switch_page(__import__('app').QuizPage,
                                        user_id=self.user_id,
                                        switch_page=self.switch_page)),
            # Lazy import inside lambda for AnalyticsPage
            ("Analytics", "images/analytics_icon.png",
             lambda: self.switch_page(__import__('app').AnalyticsPage,
                                        user_id=self.user_id,
                                        switch_page=self.switch_page)),
            ("Settings", "images/settings_icon.png",
             lambda: self.switch_page(__import__('app').SettingsPage,
                                      user_id=self.user_id,
                                      switch_page=self.switch_page))
        ]
        for text, icon_path, command in nav_items:
            button = self.create_nav_button(parent, text, icon_path, command)
            button.pack(fill="x", padx=20, pady=5)

    def create_decks_button(self, parent):
        return ctk.CTkButton(
            parent,
            text="My decks",
            image=ctk.CTkImage(light_image=Image.open("images/decks_icon.png"), size=(20, 20)),
            anchor="w",
            fg_color="transparent",
            text_color="black",
            hover_color="#F3F4F6",
            compound="left",
            font=("Inter", 14, "bold"),
            # Lazy import for DecksPage button callback
            command=lambda: self.switch_page(__import__('app').DecksPage,
                                             user_id=self.user_id,
                                             switch_page=self.switch_page)
        )

    def create_nav_button(self, parent, text, icon_path, command):
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

    def create_user_section(self, username):
        user_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        user_frame.pack(side="bottom", fill="x", pady=20, padx=20)
        avatar_frame = ctk.CTkFrame(user_frame, fg_color="transparent")
        avatar_frame.pack(side="left", fill="y")
        first_letter = username[0].upper()
        avatar = ctk.CTkLabel(avatar_frame,
                              text=first_letter,
                              width=40,
                              height=40,
                              fg_color="#4F46E5",
                              text_color="white",
                              font=("Inter", 16, "bold"),
                              corner_radius=20)
        avatar.pack(side="left", pady=4)
        ctk.CTkLabel(avatar_frame,
                     text=username,
                     font=("Inter", 16),
                     text_color="black").pack(side="left", padx=12, pady=4)
        logout_image = ctk.CTkImage(light_image=Image.open("images/logout.png"),
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
            from app import CardsPage
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
                        switch_page=self.switch_page
                    )
                )
                btn.pack(fill="x", pady=(0, 1))  # 1px bottom padding for border

                # Add bottom border
                border = ctk.CTkFrame(deck_frame, height=1, fg_color="#E5E7EB")
                border.pack(fill="x", side="bottom")

    def display_decks(self):
        self.update_deck_list()

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            from login import LoginPage
            self.switch_page(LoginPage)

