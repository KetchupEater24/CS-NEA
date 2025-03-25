# External Imports
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image

# My Imports
from database import Database
from misc import Session
from app import DecksPage

class SignupPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#FFFFFF")  # White background
        self.session = Session()

        # Center container
        self.signup_container = ctk.CTkFrame(
            self, 
            fg_color="white",
            corner_radius=12,
            width=400,
            height=500
        )
        self.signup_container.place(relx=0.5, rely=0.45, anchor="center")
        self.signup_container.grid_propagate(False)

        # Logo
        self.logo_image = ctk.CTkImage(
            light_image=Image.open("images/logo.png"),
            size=(80, 80)
        )
        ctk.CTkLabel(
            self.signup_container,
            image=self.logo_image,
            text=""
        ).pack(pady=(50, 10))
        
        # Flow Space text
        ctk.CTkLabel(
            self.signup_container,
            text="Flow Space",
            font=("Inter", 28, "bold"),
            text_color=("#000000"),
        ).pack(pady=(0, 30))

        # Email entry
        self.email_entry = ctk.CTkEntry(
            self.signup_container,
            placeholder_text="Email",
            width=300,
            height=45,
            corner_radius=16,
            border_color="#E5E7EB",
            fg_color="transparent",
            text_color="black",
            placeholder_text_color="#6B7280"
        )
        self.email_entry.pack(pady=10)

        # Username entry
        self.username_entry = ctk.CTkEntry(
            self.signup_container,
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

        # Password entry
        self.password_entry = ctk.CTkEntry(
            self.signup_container,
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

        # Sign Up button
        ctk.CTkButton(
            self.signup_container,
            text="Sign Up",
            width=300,
            height=45,
            corner_radius=16,
            fg_color="#4F46E5",
            hover_color="#4338CA",
            command=self.signup_action
        ).pack(pady=20)

        # Login text and link
        login_frame = ctk.CTkFrame(self.signup_container, fg_color="transparent")
        login_frame.pack(pady=5)
        
        ctk.CTkLabel(
            login_frame,
            text="Already have an account? ",
            text_color="#6B7280"
        ).pack(side="left")
        
        login_link = ctk.CTkLabel(
            login_frame,
            text="Log in",
            fg_color="transparent",
            text_color="#4F46E5",
            width=60,            
            cursor="hand2"
            )
        login_link.pack(side="left")
        login_link.bind("<Button-1>", lambda e: self.switch_to_login())

    def switch_to_login(self):
        from login import LoginPage
        self.master.switch_page(LoginPage)

    def signup_action(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        email = self.email_entry.get().strip()
        
        if not username or not password or not email:
            messagebox.showwarning("Warning", "Please fill in all fields")
            return
        
        db = None
        try:
            db = Database()
            user_id = db.create_user(username, email, password)
            
            if user_id:
                self.master.session.login(user_id)
                self.master.switch_page(DecksPage, 
                                    user_id=user_id,
                                    session=self.master.session,
                                    switch_page=self.master.switch_page)
            else:
                messagebox.showerror("Error", "Username already exists or failed to create account")
        except Exception as e:
            print(f"Signup error: {e}")
            messagebox.showerror("Error", "An error occurred during signup. Please try again.")
        finally:
            if db:
                db.close()
