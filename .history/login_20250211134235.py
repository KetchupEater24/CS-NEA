import customtkinter as ctk
from database import Database
from helpers import Session
from dashboard import DecksPage
from PIL import Image

from tkinter import messagebox

class LoginPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#FFFFFF")  
        self.session = Session()

        #login container
        self.login_container = ctk.CTkFrame(
            self, 
            fg_color="white",
            corner_radius=12,
            width=400,
            height=500
        )
        self.login_container.place(relx=0.5, rely=0.45, anchor="center")
        self.login_container.grid_propagate(False)

        # logo
        self.logo_image = ctk.CTkImage(
            light_image=Image.open("images/logo.png"),
            size=(80, 80)
        )
        ctk.CTkLabel(
            self.login_container,
            image=self.logo_image,
            text=""
        ).pack(pady=(50, 10))
        
        #flkw space text
        ctk.CTkLabel(
            self.login_container,
            text="Flow Space",
            font=("Inter", 28, "bold"),
            text_color=("#000000"),
        ).pack(pady=(0, 30))

        # username entry
        self.username_entry = ctk.CTkEntry(
            self.login_container,
            placeholder_text="Username",
            width=300,
            height=45,
            corner_radius=16,
            border_color="#E5E7EB",
            fg_color="transparent",
            text_color="black",
            placeholder_text_color="#6B7280"
        )
        self.username_entry.pack(pady=10)

        # password entry
        self.password_entry = ctk.CTkEntry(
            self.login_container,
            placeholder_text="Password",
            width=300,
            height=45,
            corner_radius=16,
            border_color="#E5E7EB",
            fg_color="transparent",
            text_color="black",
            placeholder_text_color="#6B7280",
            show="•"
        )
        self.password_entry.pack(pady=10)

        # login button
        ctk.CTkButton(
            self.login_container,
            text="Login",
            width=300,
            height=45,
            corner_radius=16,
            fg_color="#4F46E5",
            hover_color="#4338CA",
            command=self.login_action
        ).pack(pady=20)

        # error label
        self.error_label = ctk.CTkLabel(
            self.login_container,
            text="",
            text_color="#DC2626"
        )
        self.error_label.pack()

        # sign up link
        signup_frame = ctk.CTkFrame(self.login_container, fg_color="transparent")
        signup_frame.pack(pady=10)
        
        ctk.CTkLabel(
            signup_frame,
            text="Don't have an account?",
            text_color="#6B7280"
        ).pack(side="left", padx=5)
        
        signup_link = ctk.CTkButton(
            signup_frame,
            text="Sign up",
            fg_color="#ffffff",
            hover_color="",
            text_color="#4F46E5",
            cursor="hand2",
            width=60
            )
        signup_link.pack(side="left")
        signup_link.bind("<Button-1>", lambda e: self.switch_to_signup())

    def switch_to_signup(self):
        from signup import SignupPage
        self.master.switch_page(SignupPage)

    def login_action(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            self.error_label.configure(text="Please fill in all fields")
            return
        
        db = Database()
        try:
            user_id = db.verify_login(username, password)
            session = db.create_session(user_id)
            if user_id:
                self.master.switch_page(DecksPage, user_id=user_id, session=session, switch_page=self.master.switch_page)
            else:
                messagebox.showerror("Login Failed", "Invalid username or password. Please try again.")
        except Exception as e:
            messagebox.showerror("Login Error", str(e))
            

