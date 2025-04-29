class QuizSession(ctk.CTkFrame):
    def __init__(self, master, user_id, deck_id, switch_page, db):
        super().__init__(master, corner_radius=0, fg_color="white")
        self.difficulty_rated = False # makes a ed this line of code to fix testing issue

        # creates a  scrollbar 
        self.canvas = ctk.CTkCanvas(master, highlightthickness=0, bg="white")
        self.scrollbar = ctk.CTkScrollbar(master, orientation="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # creates a  frame inside the canvas for all content
        self.scrollable_frame = ctk.CTkFrame(self.canvas, corner_radius=0, fg_color="white")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=master.winfo_width())
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas.find_all()[0], width=e.width))
        
        # rest of your initialization code will now use scrollable_frame as parent
        self.user_id = user_id
        self.deck_id = deck_id
        self.switch_page = switch_page
        self.db = db

        # retrieve cards available for review for this deck
        self.cards = self.db.get_available_for_review(self.user_id, self.deck_id)
        if not self.cards:
            self.show_no_cards_message()
            return

        # get deck name
        deck_name = self.db.get_deck_name(self.deck_id)
        self.total_cards = len(self.cards)
        self.correct_count = 0
        self.session_start_time = datetime.now()
        self.current_card = 0

        # header with title, progress, and timer
        self.header = ctk.CTkFrame(self.scrollable_frame, fg_color="#f3f4f6", height=60)
        self.header.pack(fill="x", pady=(0, 20))
        
        self.header_center = ctk.CTkFrame(self.header, fg_color="transparent")
        self.header_center.pack(expand=True, fill="x")
        
        self.title_label = ctk.CTkLabel(
            self.header_center, text=f"Quiz Session - {deck_name}", font=("Inter", 18, "bold"), text_color="black"
        )
        self.title_label.pack(side="left", padx=30)
        self.progress_label = ctk.CTkLabel(
            self.header_center, text=f"Card 1/{self.total_cards}", font=("Inter", 14), text_color="#4b5563"
        )
        self.progress_label.pack(side="right", padx=30)
        self.timer_label = ctk.CTkLabel(
            self.header_center, text="Time Elapsed: 00:00:00", font=("Inter", 14), text_color="#4b5563"
        )
        self.timer_label.pack(side="right", padx=30)

        # makes an instruction label to tell the user how to answer a card
        self.instruction_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="After you view each question, click \"Show Answer\" and then review  difficulty and correctness (whether you got it right or wrong) of the card.",
            font=("Inter", 14),
            text_color="#1f2937",
            wraplength=800,
            justify="center"
        )

        self.instruction_label.pack(fill="x", padx=30, pady=(0,10))

        self.content = ctk.CTkFrame(self.scrollable_frame, fg_color="white")
        self.content.pack(fill="both", expand=True, padx=30, pady=10)
        
        # question section with clear header  and bordered
        self.question_section = ctk.CTkFrame(
            self.content, 
            fg_color="white", 
            border_width=1,
            border_color="#e5e7eb",
            corner_radius=8
        )
        self.question_section.pack(fill="x", pady=(0, 5))  # reduced spacing between q and a
        
        self.question_header = ctk.CTkLabel(
            self.question_section, text="QUESTION", font=("Inter", 16, "bold"), text_color="#4b5563"
        )
        self.question_header.pack(anchor="center", pady=(10, 0))
        
        # separator line
        self.question_separator = ctk.CTkFrame(self.question_section, height=1, fg_color="#e5e7eb")
        self.question_separator.pack(fill="x", pady=5, padx=15)
        
        self.question_label = ctk.CTkLabel(
            self.question_section, text="", font=("Inter", 16), text_color="black", wraplength=600, justify="center"
        )
        self.question_label.pack(anchor="center", pady=(5, 15))

        # answer section with clear header (initially hidden)  and bordered
        self.answer_frame = ctk.CTkFrame(
            self.content, 
            fg_color="white",
            border_width=1,
            border_color="#e5e7eb",
            corner_radius=8
        )
        
        self.answer_header = ctk.CTkLabel(
            self.answer_frame, text="ANSWER", font=("Inter", 16, "bold"), text_color="#4b5563"
        )
        self.answer_header.pack(anchor="center", pady=(10, 0))
        
        # separator line
        self.answer_separator = ctk.CTkFrame(self.answer_frame, height=1, fg_color="#e5e7eb")
        self.answer_separator.pack(fill="x", pady=5, padx=15)
        
        self.answer_label = ctk.CTkLabel(
            self.answer_frame, text="", font=("Inter", 16), text_color="black", wraplength=600, justify="center"
        )
        self.answer_label.pack(anchor="center", pady=(5, 15))

        # show answer button in its own frame 
        self.button_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.button_frame.pack(fill="x", pady=15)  # reduced spacing
        
        self.show_answer_button = ctk.CTkButton(
            self.button_frame, text="Show Answer", width=120, height=32, corner_radius=16,
            fg_color="#f3f4f6", text_color="black", hover_color="#e5e7eb", command=self.show_answer
        )
        self.show_answer_button.pack(anchor="center")
        
        # rating section with "difficulty" header - renamed from "recall quality"
        self.rating_section = ctk.CTkFrame(
            self.content, 
            fg_color="white",
            border_width=1,
            border_color="#e5e7eb",
            corner_radius=8
        )
        
        self.rating_header = ctk.CTkLabel(
            self.rating_section, text="DIFFICULTY", font=("Inter", 16, "bold"), text_color="#4b5563"
        )
        self.rating_header.pack(anchor="center", pady=(10, 0))
        
        # separator line
        self.rating_separator = ctk.CTkFrame(self.rating_section, height=1, fg_color="#e5e7eb")
        self.rating_separator.pack(fill="x", pady=5, padx=15)

        # difficulty rating options 
        self.rating_frame = ctk.CTkFrame(self.rating_section, fg_color="transparent")
        self.rating_frame.pack(pady=10)
        
        # center container for rating buttons
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
                button_fg = "#fee2e2"
                button_text = "#dc2626"
                button_hover = "#fecaca"
            else:
                # for medium, easy, or very easy, use gray styling
                button_fg = "#f3f4f6"
                button_text = "black"
                button_hover = "#e5e7eb"
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
        
        # makes a  interval explanation label (hidden until answer revealed) 
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
            text_color="#4b5563",
            wraplength=600,
            justify="center"
        )
        self.interval_help.pack(pady=(0, 15))
        
        # hide the entire rating section initially
        self.rating_section.pack_forget()

        # makes a  "correctness" section with border
        self.correctness_section = ctk.CTkFrame(
            self.content, 
            fg_color="white",
            border_width=1,
            border_color="#e5e7eb",
            corner_radius=8
        )
        
        self.correctness_header = ctk.CTkLabel(
            self.correctness_section, text="CORRECTNESS", font=("Inter", 16, "bold"), text_color="#4b5563"
        )
        self.correctness_header.pack(anchor="center", pady=(10, 0))
        
        # separator line
        self.correctness_separator = ctk.CTkFrame(self.correctness_section, height=1, fg_color="#e5e7eb")
        self.correctness_separator.pack(fill="x", pady=5, padx=15)
        
        # correct/incorrect buttons to record recall accuracy 
        self.correct_frame = ctk.CTkFrame(self.correctness_section, fg_color="transparent")
        self.correct_frame.pack(pady=10)
        
        # center container for correct/incorrect buttons
        self.correct_center = ctk.CTkFrame(self.correct_frame, fg_color="transparent")
        self.correct_center.pack(expand=True, anchor="center")
        
        # explain correctness meaning 
        self.correct_help = ctk.CTkLabel(
            self.correct_frame,
            text=(
                "Judge whether or not you feel you got the card right. \"Correct\" marks it right, \"Incorrect\" marks it wrong.    "
                "Remember to be honest with yourself—making mistakes is a natural part of learning and helps you improve!"
            ),
            font=("Inter", 12),
            text_color="#4b5563",
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
            fg_color="#d1fae5",
            text_color="#065f46",
            hover_color="#a7f3d0",
            command=lambda: self.record_correctness(True)
        )
        self.correct_button.pack(side="left", padx=5)
        
        self.incorrect_button = ctk.CTkButton(
            self.correct_center,
            text="Incorrect",
            width=120,
            height=32,
            corner_radius=16,
            fg_color="#fee2e2",
            text_color="#b91c1c",
            hover_color="#fecaca",
            command=lambda: self.record_correctness(False)
        )
        self.incorrect_button.pack(side="left", padx=5)
        
        ctk.CTkFrame(self.correctness_section, fg_color="transparent", height=5).pack()
        
        # hide correctness section initially
        self.correctness_section.pack_forget()

        # start timer and display the first card
        self.update_timer()
        self.display_card()
        
    def update_timer(self):
        # updates the  the timer label every second
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
        self.difficulty_rated = False # makes a ed this line of code to fix testing issue
        # if no more cards remain, end the quiz
        if self.current_card >= self.total_cards:
            self.end_quiz()
            return

        # hide answer, correctness, interval and rating ui
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
        self.answer_frame.pack(fill="x", pady=(5, 10))  # reduced spacing
        
        # show rating section with explanation
        self.rating_section.pack(fill="x", pady=(5, 5))  # reduced spacing
        self.correctness_section.pack(fill="x", pady=(5, 0))  # reduced spacing

    def record_correctness(self, was_correct):
        # check if difficulty has been rated first
        if not self.difficulty_rated: # makes a ed this line of code to fix testing issue
            self.show_temporary_confirmation("Please rate difficulty first before marking correctness", duration=2000) # makes a ed this line of code to fix testing issue
            return # makes a ed this line of code to fix testing issue
        # sets the correctness
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
        # creates a  small popup frame on top of the current content
        popup = ctk.CTkFrame(
            self.content, 
            fg_color="#f3f4f6",  
            corner_radius=8,
            border_width=1,
            border_color="#e5e7eb" 
        )
        
        # position the popup at the center top of the content area
        popup.place(relx=0.5, rely=0.3, anchor="center")
        
        # makes a  the confirmation message
        confirm_label = ctk.CTkLabel(
            popup,
            text=message,
            font=("Inter", 14),
            text_color="#000000",  
            padx=20,
            pady=10
        )
        confirm_label.pack(padx=20, pady=10)
        
        # schedule the popup to disappear after the specified duration
        self.after(duration, lambda: popup.destroy())

            
    def rate_card_difficulty(self, quality):
        self.difficulty_rated = True # makes a ed this line of code to fix testing issue

        # updates the  scheduling of card using spaced repitition algorithm
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
        # clear the canvas and scrollbar
        self.canvas.destroy()
        self.scrollbar.destroy()
        
        # creates a  new frame for the summary
        summary_frame = ctk.CTkFrame(self.master, fg_color="white", corner_radius=0)
        summary_frame.pack(fill="both", expand=True)
        
        # header section with title
        header_frame = ctk.CTkFrame(summary_frame, fg_color="#f3f4f6", height=60)
        header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            header_frame,
            text="Quiz Complete!",
            font=("Inter", 24, "bold"),
            text_color="black"
        ).pack(pady=20)
        
        # stats container matching analytics page style
        stats_container = ctk.CTkFrame(
            summary_frame,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color="#e5e7eb"
        )
        stats_container.pack(fill="x", padx=30, pady=(0, 20))
        
        ctk.CTkLabel(
            stats_container,
            text="Session Results (Go to Analytics Page to see what these mean - Information located on Analytics Page --> then scroll down on Analytics Page)",
            font=("Inter", 18, "bold"),
            text_color="#111827"
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        # container for stat cards
        stat_cards_container = ctk.CTkFrame(stats_container, fg_color="white")
        stat_cards_container.pack(fill="x", padx=20, pady=(0, 15))
        
        # calculate stats
        total_cards = self.total_cards
        wrong = total_cards - self.correct_count
        accuracy = (self.correct_count / total_cards) * 100 if total_cards > 0 else 0
        
        # layout for stats - each tuple is (label, value, icon)
        stats_layout = [
            ("Total Cards Reviewed", f"{total_cards}", "📄"),
            ("Correct Answers", f"{self.correct_count}", "✅"),
            ("Wrong Answers", f"{wrong}", "❌"),
            ("Accuracy", f"{accuracy:.1f}%", "🎯"),
            ("Total Time Spent", f"{self.total_time:.1f}s", "⏱️"),
            ("Avg Time Per Card", f"{(self.total_time / total_cards):.1f}s" if total_cards else "0s", "⚡")
        ]
        
        # use same grid layout as analytics page: 3 rows, 2 columns
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
                    
        # makes a ed the below button to fix testing issue
        ctk.CTkButton(
            summary_frame,  
            text="Return to Quiz Homepage",
            width=200,
            height=40,
            corner_radius=16,
            font=("Inter", 14),
            fg_color="#f3f4f6",
            text_color="black",
            hover_color="#e5e7eb",
            command=lambda: self.switch_page(__import__('app').QuizPage, user_id=self.user_id, switch_page=self.switch_page)
    ).pack(anchor="center", pady=20)
        
    def create_stat_card(self, parent, label_text, value_text, icon_text, col_index):
        # container for an individual stat card
        stat_card_container = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color="#e5e7eb"
        )
        stat_card_container.grid(row=0, column=col_index, padx=5, sticky="nsew")
        
        # inner frame holding the stat info
        stat_info = ctk.CTkFrame(stat_card_container, fg_color="white")
        stat_info.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(stat_info, text=icon_text, font=("Inter", 18), text_color="#4b5563").pack(anchor="w")
        ctk.CTkLabel(stat_info, text=label_text, font=("Inter", 12), text_color="#4b5563").pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(stat_info, text=value_text, font=("Inter", 20, "bold"), text_color="#111827").pack(anchor="w", pady=(5, 0))
            
    def show_no_cards_message(self):
        # clear the canvas and scrollbar if they exist
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
        
        button_frame = ctk.CTkFrame(msg_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="Return to Quiz Homepage",
            width=200,
            height=40,
            corner_radius=16,
            font=("Inter", 14),
            fg_color="#f3f4f6",
            text_color="black",
            hover_color="#e5e7eb",
            command=lambda: self.switch_page(__import__('app').QuizPage, user_id=self.user_id, switch_page=self.switch_page)
        ).pack(pady=20, anchor="center")

