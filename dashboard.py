import customtkinter as ctk
from typing import Callable
from tkinter import messagebox, filedialog
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import random
import os
from datetime import datetime, timedelta
import io
from PIL import ImageGrab  # Windows and macOS
from PIL import ImageTk

# My Imports
from database import Database
from helpers import Session
from components import CustomInputDialog
# from animations.animation_handler import AnimationHandler

session = Session()

#############################################################
# Base Components
#############################################################

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, switch_page: Callable, username: str, user_id: int, session: Session):
        super().__init__(
            master, 
            fg_color="white", 
            width=250, 
            corner_radius=0,
            border_width=0,  # Remove default border
            border_color="#E5E7EB"
        )
        self.pack_propagate(False)
        self.grid_propagate(False)
        
        # Create right border frame
        self.right_border = ctk.CTkFrame(
            self,
            width=1,
            fg_color="#E5E7EB",
            corner_radius=0
        )
        self.right_border.pack(side="right", fill="y")
        
        # Main content container
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(side="left", fill="both", expand=True)
        
        self.switch_page = switch_page
        self.user_id = user_id
        self.session = session

        # Check if we're on DecksPage or CardsPage
        show_decks = isinstance(master, (DecksPage, CardsPage))

        # Logo and navigation container
        nav_container = ctk.CTkFrame(self.content, fg_color="transparent")
        nav_container.pack(fill="x", expand=False)

        # Logo frame
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

        # Navigation buttons
        self.create_nav_buttons(nav_container, show_decks)

        # User info at bottom
        self.create_user_section(username)

    def create_nav_buttons(self, parent, show_decks):
        # My Decks button
        decks_button = self.create_decks_button(parent)
        decks_button.pack(fill="x", padx=20, pady=(0, 5))
        
        # Create deck list container that updates dynamically
        self.deck_container = ctk.CTkFrame(parent, fg_color="transparent", height=0)
        self.deck_container.pack(fill="x", expand=False)
        
        if show_decks:
            self.update_deck_list()

        # Navigation buttons
        nav_items = [
            ("Quiz yourself", "images/quiz_icon.png", 
             lambda: self.switch_page(QuizPage, user_id=self.user_id, session=self.session, switch_page=self.switch_page)),
            ("Analytics", "images/analytics_icon.png", 
             lambda: self.switch_page(AnalyticsPage, user_id=self.user_id, session=self.session, switch_page=self.switch_page))
        ]

        for text, icon_path, command in nav_items:
            button = self.create_nav_button(parent, text, icon_path, command)
            button.pack(fill="x", padx=20, pady=5)

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
        
        # Create sidebar
        self.sidebar = Sidebar(self, switch_page, self.username, self.user_id, self.session)
        self.sidebar.pack(side="left", fill="y")
        
        # Main content area
        self.main_content = ctk.CTkFrame(self, fg_color="white")
        self.main_content.pack(side="left", fill="both", expand=True)
        
        # Header frame
        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 0))
        
        # Title
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
        
        # Delete Selected button
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
        
        # Add separator line after header
        separator = ctk.CTkFrame(self.main_content, height=1, fg_color="#E5E7EB")
        separator.pack(fill="x", padx=30, pady=(20, 0))
        
        # Decks grid container
        self.decks_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.decks_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Configure grid columns with padding
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
            
        # Update delete button state
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
        
        # Make the entire container clickable
        self.bind("<Button-1>", self.toggle_selection)
        
        # Content frame
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        content_frame.bind("<Button-1>", self.toggle_selection)
        
        # Title and count
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
        
        # Checkbox
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

#############################################################DECKS PAGE#############################################################

class QuizPage(ctk.CTkFrame):
    def __init__(self, master, user_id, session, switch_page):
        super().__init__(master, corner_radius=0, fg_color="white")
        self.pack(fill="both", expand=True)
        
        self.user_id = user_id
        self.session = session
        self.switch_page = switch_page
        self.selected_decks = set()
        
        # Get username from database
        db = Database()
        self.username = db.get_username(self.user_id)
        
        # Create sidebar
        self.sidebar = Sidebar(self, switch_page, self.username, self.user_id, self.session)
        self.sidebar.pack(side="left", fill="y")
        
        # Main content area
        self.main_content = ctk.CTkFrame(self, fg_color="white")
        self.main_content.pack(side="left", fill="both", expand=True)
        
        # Header frame with Start Quiz button
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
        
        # Add separator line
        separator = ctk.CTkFrame(self.main_content, height=1, fg_color="#E5E7EB")
        separator.pack(fill="x", padx=30, pady=(20, 0))
        
        # Deck selection area
        self.create_deck_selection()

    def toggle_deck_selection(self, deck_id, selected):
        if selected:
            self.selected_decks.add(deck_id)
        else:
            self.selected_decks.discard(deck_id)
            
        # Update start button state
        self.start_button.configure(
            state="normal" if self.selected_decks else "disabled"
        )

    def start_quiz(self):
        if not self.selected_decks:
            messagebox.showwarning("Warning", "Please select at least one deck")
            return
        
        # Destroy all children of master first
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
        # Container for deck selection
        selection_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        selection_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Instructions
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
        
        # Load decks
        self.load_decks()

    def load_decks(self):
        # Clear existing decks
        for widget in self.decks_frame.winfo_children():
            widget.destroy()
            
        # Get decks from database
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

class QuizSession(ctk.CTkFrame):
    def __init__(self, master, user_id, deck_id, deck_ids, session, switch_page):
        super().__init__(master, corner_radius=0, fg_color="white")
        self.pack(fill="both", expand=True)
        
        # Store instance variables
        self.user_id = user_id
        self.deck_id = deck_id
        self.deck_ids = deck_ids
        self.session = session
        self.switch_page = switch_page
        
        # Quiz state
        self.current_index = 0
        self.start_time = datetime.now()
        self.card_start_time = None
        self.correct_count = 0
        self.total_time = 0
        
        # Get cards for review
        db = Database()
        self.cards = db.get_cards_for_review(deck_id)
        
        if not self.cards:
            self.show_no_cards_message()
            return
            
        self.setup_ui()
        self.display_card()
        
    def setup_ui(self):
        # Header with deck name and progress
        self.header = ctk.CTkFrame(self, fg_color="#F3F4F6", height=60)
        self.header.pack(fill="x", pady=(0, 20))
        self.header.pack_propagate(False)
        
        # Title
        ctk.CTkLabel(
            self.header,
            text=f"Quiz Session - {self.deck_id}",
            font=("Inter", 18, "bold"),
            text_color="black"
        ).pack(side="left", padx=30)
        
        # Progress label
        self.progress_label = ctk.CTkLabel(
            self.header,
            text=f"Card 1/{len(self.cards)}",
            font=("Inter", 14),
            text_color="#4B5563"
        )
        self.progress_label.pack(side="right", padx=30)
        
        # Main content area
        self.content = ctk.CTkFrame(self, fg_color="white")
        self.content.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Question area
        self.question_label = ctk.CTkLabel(
            self.content,
            text="",
            font=("Inter", 16),
            text_color="black",
            wraplength=600
        )
        self.question_label.pack(pady=20)
        
        # Answer area (initially hidden)
        self.answer_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.answer_label = ctk.CTkLabel(
            self.answer_frame,
            text="",
            font=("Inter", 16),
            text_color="black",
            wraplength=600
        )
        self.answer_label.pack(pady=20)
        
        # Show Answer button
        self.show_answer_btn = ctk.CTkButton(
            self.content,
            text="Show Answer",
            width=120,
            height=32,
            command=self.show_answer
        )
        self.show_answer_btn.pack(pady=20)
        
        # Rating buttons frame (initially hidden)
        self.rating_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        
        # Rating buttons
        ratings = [
            ("Incorrect", False, "#DC2626"),
            ("Correct", True, "#10B981")
        ]
        
        for text, value, color in ratings:
            btn = ctk.CTkButton(
                self.rating_frame,
                text=text,
                width=100,
                height=32,
                fg_color=color,
                hover_color=color,
                command=lambda v=value: self.rate_card(v)
            )
            btn.pack(side="left", padx=10)
            
    def display_card(self):
        # Reset UI state
        self.answer_frame.pack_forget()
        self.rating_frame.pack_forget()
        self.show_answer_btn.pack(pady=20)
        
        # Get current card
        card = self.cards[self.current_index]
        
        # Update question and answer
        self.question_label.configure(text=card[1])  # question
        self.answer_label.configure(text=card[2])    # answer
        
        # Update progress
        self.progress_label.configure(
            text=f"Card {self.current_index + 1}/{len(self.cards)}"
        )
        
        # Start timing this card
        self.card_start_time = datetime.now()
        
    def show_answer(self):
        self.show_answer_btn.pack_forget()
        self.answer_frame.pack()
        self.rating_frame.pack(pady=20)
        
    def rate_card(self, is_correct):
        # Calculate time taken
        time_taken = (datetime.now() - self.card_start_time).total_seconds()
        
        # Get current card ID
        card_id = self.cards[self.current_index][0]
        
        # Save result
        db = Database()
        db.save_quiz_result(
            self.user_id,
            self.deck_id,
            card_id,
            is_correct,
            time_taken
        )
        
        # Update stats
        if is_correct:
            self.correct_count += 1
        self.total_time += time_taken
        
        # Move to next card or end quiz
        self.current_index += 1
        if self.current_index < len(self.cards):
            self.display_card()
        else:
            self.end_quiz()
            
    def end_quiz(self):
        # Calculate final stats
        total_cards = len(self.cards)
        accuracy = (self.correct_count / total_cards) * 100
        avg_time = self.total_time / total_cards
        
        # Save session stats
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
        
        # Show summary
        self.show_summary(accuracy, avg_time)
        
    def show_summary(self, accuracy, avg_time):
        # Clear content
        for widget in self.winfo_children():
            widget.destroy()
            
        # Create summary frame
        summary = ctk.CTkFrame(self, fg_color="#F3F4F6")
        summary.pack(expand=True, fill="both", padx=30, pady=20)
        
        # Title
        ctk.CTkLabel(
            summary,
            text="Quiz Complete!",
            font=("Inter", 24, "bold"),
            text_color="black"
        ).pack(pady=(40, 20))
        
        # Stats
        stats = [
            ("Cards Reviewed", f"{len(self.cards)}"),
            ("Correct Answers", f"{self.correct_count}"),
            ("Accuracy", f"{accuracy:.1f}%"),
            ("Average Time", f"{avg_time:.1f}s")
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
        
        # Return button
        ctk.CTkButton(
            summary,
            text="Return to Deck",
            width=200,
            height=40,
            command=lambda: self.switch_page(DecksPage)
        ).pack(pady=40)
        
    def show_no_cards_message(self):
        # Clear and show message
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
            text="Return to Deck",
            width=200,
            height=40,
            command=lambda: self.switch_page(DecksPage)
        ).pack(pady=20)

class AnalyticsPage(ctk.CTkFrame):
    def __init__(self, master, user_id, session, switch_page):
        super().__init__(master, corner_radius=0, fg_color="white")
        self.pack(fill="both", expand=True)
        
        self.user_id = user_id
        self.session = session
        self.switch_page = switch_page
        
        # Get username from database
        db = Database()
        self.username = db.get_username(self.user_id)
        self.stats = db.get_user_stats(self.user_id)
        
        # Create sidebar
        self.sidebar = Sidebar(self, switch_page, self.username, self.user_id, self.session)
        self.sidebar.pack(side="left", fill="y")
        
        # Main content area
        self.main_content = ctk.CTkFrame(self, fg_color="white")
        self.main_content.pack(side="left", fill="both", expand=True)
        
        # Header
        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkLabel(
            header_frame,
            text="Analytics",
            font=("Inter", 24, "bold"),
            text_color="black"
        ).pack(side="left")
        
        # Create stats grid
        self.create_stats_grid()
        
        # Create graphs
        self.create_graphs()

    def create_stats_grid(self):
        stats_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        stats_frame.pack(fill="x", padx=30, pady=20)
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)  # Changed to 3 columns
        
        # Get quiz stats for success rate
        db = Database()
        quiz_stats = db.get_quiz_stats(self.user_id)
        
        # Row 1: Card Statistics
        self.create_stat_card(
            stats_frame,
            "Total Cards",
            str(self.stats['total_cards']),
            0, 0
        )
        
        reviewed_percentage = round(self.stats['reviewed_cards']/self.stats['total_cards']*100 if self.stats['total_cards'] > 0 else 0)
        self.create_stat_card(
            stats_frame,
            "Cards Reviewed",
            f"{self.stats['reviewed_cards']} ({reviewed_percentage}%)",
            0, 1
        )
        
        self.create_stat_card(
            stats_frame,
            "Success Rate",
            f"{round(quiz_stats['success_rate'], 1)}%",
            0, 2
        )
        
        # Row 2: Learning Statistics
        self.create_stat_card(
            stats_frame,
            "Current Easiness",
            f"{self.stats['avg_easiness']} / {self.stats['max_easiness']}",
            1, 0
        )
        
        self.create_stat_card(
            stats_frame,
            "Review Interval",
            f"{self.stats['avg_interval']} days",
            1, 1
        )
        
        streak = db.calculate_study_streak(self.user_id)
        self.create_stat_card(
            stats_frame,
            "Study Streak",
            f"{streak} days",
            1, 2
        )

    def create_stat_card(self, parent, title, value, row, col):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=12)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        card.configure(border_width=1, border_color="#E5E7EB")
        
        ctk.CTkLabel(
            card,
            text=title,
            font=("Inter", 14),
            text_color="#6B7280"
        ).pack(pady=(20, 5))
        
        ctk.CTkLabel(
            card,
            text=value,
            font=("Inter", 24, "bold"),
            text_color="black"
        ).pack(pady=(0, 20))

    def create_graphs(self):
        graphs_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        graphs_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Create figure with two subplots
        fig = plt.figure(figsize=(12, 6))
        fig.patch.set_facecolor('#ffffff')
        
        # Performance over time
        ax1 = fig.add_subplot(121)
        self.plot_performance_trend(ax1)
        
        # Retention curve
        ax2 = fig.add_subplot(122)
        self.plot_retention_curve(ax2)
        
        plt.tight_layout(pad=3.0)
        canvas = FigureCanvasTkAgg(fig, graphs_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def plot_performance_trend(self, ax):
        db = Database()
        history = db.get_performance_over_time(self.user_id)
        
        dates = [h[0] for h in history]
        accuracies = [h[1] for h in history]
        
        # Calculate trend line
        x = np.arange(len(dates))
        z = np.polyfit(x, accuracies, 1)
        p = np.poly1d(z)
        
        ax.plot(dates, accuracies, 'o-', color='#4F46E5', alpha=0.6)
        ax.plot(dates, p(x), '--', color='#DC2626')
        ax.set_title('Performance Trend', pad=20)
        ax.set_xlabel('Date')
        ax.set_ylabel('Accuracy (%)')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)

    def plot_retention_curve(self, ax):
        db = Database()
        intervals = db.get_retention_intervals(self.user_id)
        
        if intervals:
            days = [i[0] for i in intervals]
            retention = [i[1] for i in intervals]
            
            # Fit exponential decay curve
            x = np.array(days)
            y = np.array(retention)
            a, b = np.polyfit(x, np.log(y), 1)
            
            x_fit = np.linspace(min(days), max(days), 100)
            y_fit = np.exp(b) * np.exp(a * x_fit)
            
            ax.scatter(days, retention, color='#4F46E5', alpha=0.6)
            ax.plot(x_fit, y_fit, '--', color='#DC2626')
            ax.set_title('Memory Retention Curve', pad=20)
            ax.set_xlabel('Days since last review')
            ax.set_ylabel('Retention rate (%)')
            ax.grid(True, alpha=0.3)

class CardsPage(ctk.CTkFrame):
    def __init__(self, master, user_id, deck_id, session, switch_page: Callable):
        super().__init__(master, corner_radius=0, fg_color="white")
        self.user_id = user_id
        self.deck_id = deck_id
        self.session = session
        self.switch_page = switch_page

        # Get username from database
        db = Database()
        self.username = db.get_username(self.user_id)
        self.deck_info = db.get_deck_info(self.deck_id)

        # Create sidebar
        self.sidebar = Sidebar(self, switch_page, self.username, self.user_id, self.session)
        self.sidebar.pack(side="left", fill="y")

        # Main content area
        self.main_content = ctk.CTkFrame(self, fg_color="white")
        self.main_content.pack(side="left", fill="both", expand=True)

        # Header frame
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

        # Add card button
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

        # Cards container
        self.cards_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.cards_frame.pack(fill="both", expand=True, padx=30)
        
        self.display_cards()

    def add_card(self):
        dialog = CardCreationDialog(self, deck_id=self.deck_id)
        dialog.grab_set()

    def edit_card(self, card_id):
        try:
            db = Database()
            card = db.get_card(card_id)
            if card:
                edit_dialog = EditCardDialog(
                    self,
                    card_id,
                    card[2],  # question
                    card[3]   # answer
                )
                edit_dialog.grab_set()  # Make dialog modal
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
        
        # Content frame
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=15)
        
        # Left side: Text content
        text_frame = ctk.CTkFrame(content, fg_color="transparent")
        text_frame.pack(side="left", fill="x", expand=True)
        
        # Question and answer with black text
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
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(text_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10,0))
        
        # Edit button - matches Add Card style
        ctk.CTkButton(
            buttons_frame,
            text="Edit",
            width=70,
            height=32,
            corner_radius=16,
            fg_color="#F3F4F6",
            text_color="black",
            hover_color="#E5E7EB",
            command=lambda: edit_callback(card_id)
        ).pack(side="left", padx=5)
        
        # Delete button - matches deck delete style
        ctk.CTkButton(
            buttons_frame,
            text="Delete",
            width=70,
            height=32,
            corner_radius=16,
            fg_color="#FEE2E2",
            text_color="#DC2626",
            hover_color="#FECACA",
            command=lambda: delete_callback(card_id)
        ).pack(side="left", padx=5)
        

class QuizDeckContainer(ctk.CTkFrame):
    def __init__(self, master, deck_id, deck_name, card_count, toggle_callback):
        super().__init__(master, fg_color="white", corner_radius=8)
        self.configure(border_width=1, border_color="#E5E7EB")
        
        self.deck_id = deck_id
        self.toggle_callback = toggle_callback
        self.selected = False
        
        # Content frame
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title and count
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
        
        # Checkbox
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
        
        # Make the entire container clickable
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

class CardCreationDialog(ctk.CTkToplevel):
    def __init__(self, parent, deck_id):
        super().__init__(parent)
        self.title("Create New Card")
        self.geometry("500x800")
        self.attributes('-topmost', True)  # Always on top
        self.parent = parent
        self.deck_id = deck_id
        
        # Main scrollable container
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="white",
            width=480,
            height=780
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Question section
        self.create_question_section()
        
        # Answer section
        self.create_answer_section()
        
        # Save button
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
        # Similar structure for answer section
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
        

class EditCardDialog(CardCreationDialog): 
    def __init__(self, parent, card_id, question, answer):
        super().__init__(parent, parent.deck_id)
        self.title("Edit Card")
        self.card_id = card_id
        
        # Set the current question and answer
        self.question_entry.insert('1.0', question)
        self.answer_entry.insert('1.0', answer)
        
        # Change the save button text
        self.save_button.configure(text="Save Changes")
        
    def save(self):
        question = self.question_entry.get('1.0', 'end-1c').strip()
        answer = self.answer_entry.get('1.0', 'end-1c').strip()
        
        if not question or not answer:
            messagebox.showerror("Error", "Both question and answer are required")
            return
            
        db = Database()
        db.update_card(self.card_id, question, answer)
        self.parent.display_cards()  # Refresh the cards display
        self.destroy()


class DeckManager:
    def __init__(self, parent, user_id, session, switch_page):
        self.parent = parent
        self.user_id = user_id
        self.session = session
        self.switch_page = switch_page
        self.db = Database()
        
        self.create_ui()
        self.load_decks()
        
    def create_ui(self):
        # Clear parent
        for widget in self.parent.winfo_children():
            widget.destroy()
            
        # Create main content
        self.main_content = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.main_content.pack(fill="both", expand=True)
        
        # Header
        header = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 0))
        
        ctk.CTkLabel(
            header,
            text="Your Decks",
            font=("Inter", 24, "bold"),
            text_color="black"
        ).pack(side="left")
        
        # Add deck button
        add_deck_btn = ctk.CTkButton(
            header,
            text="+ New Deck",
            command=self.show_add_deck_dialog,
            width=120,
            height=32,
            corner_radius=16
        )
        add_deck_btn.pack(side="right")
        
        # Decks container
        self.decks_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.decks_container.pack(fill="both", expand=True, padx=30, pady=20)
        
    def load_decks(self):
        # Clear existing decks
        for widget in self.decks_container.winfo_children():
            widget.destroy()
            
        # Get decks from database
        decks = self.db.get_decks(self.user_id)
        
        # Create deck cards
        for deck in decks:
            self.create_deck_card(deck)
            
    def create_deck_card(self, deck):
        deck_frame = ctk.CTkFrame(self.decks_container, fg_color="white", corner_radius=12)
        deck_frame.pack(fill="x", pady=10)
        
        # Deck info
        info_frame = ctk.CTkFrame(deck_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            info_frame,
            text=deck[1],  # deck name
            font=("Inter", 16, "bold"),
            text_color="black"
        ).pack(side="left")
        
        # Action buttons
        actions_frame = ctk.CTkFrame(deck_frame, fg_color="transparent")
        actions_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        stats = self.db.get_deck_stats(deck[0])
        
        ctk.CTkLabel(
            actions_frame,
            text=f"{stats['card_count']} cards",
            font=("Inter", 14),
            text_color="#6B7280"
        ).pack(side="left")
        
        # Study button
        study_btn = ctk.CTkButton(
            actions_frame,
            text="Study",
            command=lambda: self.start_quiz(deck[0]),
            width=100,
            height=32,
            corner_radius=16
        )
        study_btn.pack(side="right", padx=5)
        
        # Edit button
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="Edit",
            command=lambda: self.edit_deck(deck[0]),
            width=100,
            height=32,
            corner_radius=16,
            fg_color="#F3F4F6",
            text_color="black",
            hover_color="#E5E7EB"
        )
        edit_btn.pack(side="right", padx=5)
        
    def show_add_deck_dialog(self):
        dialog = ctk.CTkInputDialog(
            text="Enter deck name:",
            title="New Deck"
        )
        deck_name = dialog.get_input()
        if deck_name:
            deck_id = self.db.create_deck(self.user_id, deck_name)
            self.load_decks()
            
    def start_quiz(self, deck_id):
        QuizSession(
            self.master,
            self.user_id,
            self.deck_id,
            self.deck_name,
            list(self.selected_decks),
            self.session,
            self.switch_page
        )
        
    def edit_deck(self, deck_id):
        # TODO: Implement deck editing functionality
        pass
