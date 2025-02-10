 def __init__(self, master, user_id, deck_id, deck_name, session, switch_page: Callable):
        super().__init__(master, fg_color="white")
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.current_index = 0
        self.start_time = None
        self.card_start_time = None
        self.correct_count = 0
        self.total_time = 0
        self.ratings = []

        self.switch_page = switch_page
        self.user_id = user_id
        self.session = session
        
        # Destroy all children of master first
        for widget in self.winfo_children():
            widget.destroy()

        # Get cards for review
        db = Database()
        self.cards = db.get_cards_for_review(deck_id)
        if not self.cards:
            self.show_no_cards_message()
            return
            
        self.setup_ui()
        self.start_quiz()
        
    def setup_ui(self):
        # Header with deck name
        self.header = ctk.CTkFrame(self, fg_color="#F3F4F6", height=60)
        self.header.pack(fill="x", pady=(0, 20))
        self.header.pack_propagate(False)
        
        ctk.CTkLabel(
            self.header,
            text=f"Quiz Session - {self.deck_name}",
            font=("Inter", 18, "bold"),
            text_color="black"
        ).pack(expand=True)
        
        # Card display area
        self.card_frame = ctk.CTkFrame(
            self,
            fg_color="#F3F4F6",
            corner_radius=12
        )
        self.card_frame.pack(expand=True, fill="both", padx=30, pady=10)
        
        # Question label
        self.question_label = ctk.CTkLabel(
            self.card_frame,
            text="",
            font=("Inter", 16),
            text_color="black",
            wraplength=500
        )
        self.question_label.pack(expand=True, pady=20)
        
        # Answer frame (initially hidden)
        self.answer_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        
        self.answer_label = ctk.CTkLabel(
            self.answer_frame,
            text="",
            font=("Inter", 16),
            text_color="black",
            wraplength=500
        )
        self.answer_label.pack(pady=20)
        
        # Rating buttons frame
        self.rating_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        
        ctk.CTkLabel(
            self.rating_frame,
            text="Rate your answer:",
            font=("Inter", 14),
            text_color="#4B5563"
        ).pack(pady=(0, 10))
        
        # Rating buttons
        ratings_container = ctk.CTkFrame(self.rating_frame, fg_color="transparent")
        ratings_container.pack()
        
        ratings = [
            ("Again", 0, "#DC2626"),
            ("Hard", 3, "#F59E0B"),
            ("Good", 4, "#10B981"),
            ("Easy", 5, "#3B82F6")
        ]
        
        for text, value, color in ratings:
            btn = ctk.CTkButton(
                ratings_container,
                text=text,
                width=80,
                height=32,
                fg_color=color,
                hover_color=color,
                command=lambda v=value: self.rate_card(v)
            )
            btn.pack(side="left", padx=5)
        
        # Show Answer button
        self.show_answer_btn = ctk.CTkButton(
            self.card_frame,
            text="Show Answer",
            width=120,
            height=32,
            command=self.show_answer
        )
        self.show_answer_btn.pack(pady=20)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(fill="x", padx=30, pady=(20, 0))
        self.progress_bar.set(0)
        
    def start_quiz(self):
        self.start_time = datetime.now()
        self.display_card()
        
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
        
        # Start timing this card
        self.card_start_time = datetime.now()
        
        # Update progress
        progress = (self.current_index + 1) / len(self.cards)
        self.progress_bar.set(progress)
        
    def show_answer(self):
        self.show_answer_btn.pack_forget()
        self.answer_frame.pack(expand=True, fill="both")
        self.rating_frame.pack(pady=20)
        
    def rate_card(self, rating):
        # Calculate time taken for this card
        time_taken = (datetime.now() - self.card_start_time).total_seconds()
        
        # Get current card ID
        card_id = self.cards[self.current_index][0]  # card_id
        
        # Update spaced repetition data
        db = Database()
        db.update_card_sm2(card_id, rating, time_taken)
        
        # Track correct answers (rating >= 3 is considered correct)
        if rating >= 3:
            self.correct_count += 1
        
        self.ratings.append(rating)
        self.total_time += time_taken
        
        # Move to next card or end quiz
        self.current_index += 1
        if self.current_index < len(self.cards):
            self.display_card()
        else:
            self.end_quiz()
            
    def end_quiz(self):
        # Calculate statistics
        total_cards = len(self.cards)
        accuracy = (self.correct_count / total_cards) * 100
        avg_time = self.total_time / total_cards
        
        # Save session stats
        db = Database()
        db.save_session_stats(
            1,  # TODO: Get actual user_id
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
        # Clear main content
        for widget in self.winfo_children():
            widget.destroy()
            
        # Create summary frame
        summary_frame = ctk.CTkFrame(
            self,
            fg_color="#F3F4F6",
            corner_radius=12
        )
        summary_frame.pack(expand=True, fill="both", padx=30, pady=20)
        
        # Title
        ctk.CTkLabel(
            summary_frame,
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
            stat_frame = ctk.CTkFrame(summary_frame, fg_color="transparent")
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
        
        # Return to deck button
        ctk.CTkButton(
            summary_frame,
            text="Return to Deck",
            width=200,
            height=40,
            command=lambda: self.master.switch_page(DecksPage)
        ).pack(pady=40)
        
    def show_no_cards_message(self):
        # Clear and show message
        for widget in self.winfo_children():
            widget.destroy()
            
        message_frame = ctk.CTkFrame(self, fg_color="white")
        message_frame.pack(expand=True, fill="both", padx=30, pady=20)
        
        ctk.CTkLabel(
            message_frame,
            text="No cards due for review!",
            font=("Inter", 18, "bold"),
            text_color="black"
        ).pack(expand=True)
        
        ctk.CTkButton(
            message_frame,
            text="Return to Deck",
            width=200,
            height=40,
            command=lambda: self.master.switch_page(DecksPage)
        ).pack(pady=20)