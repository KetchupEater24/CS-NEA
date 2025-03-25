import customtkinter as ctk
from database import Database
from helpers import Session
from app import DecksPage
from PIL import Image
from tkinter import messagebox


class LoginPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#FFFFFF")
        self.session = Session()

        # login container
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

        # Flow Space text
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
            fg_color="#636ae8",
            hover_color="#636ae8",
            command=self.login_action
        ).pack(pady=20)

        # sign up link (moved closer to the login button)
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

        # error label (placed after the sign up section)
        self.error_label = ctk.CTkLabel(
            self.login_container,
            text="",
            text_color="#DC2626"
        )
        self.error_label.pack()

    def switch_to_signup(self):
        from auth import SignupPage
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
                self.master.switch_page(DecksPage, user_id=user_id, session=session,
                                        switch_page=self.master.switch_page)
            else:
                messagebox.showerror("Login Failed", "Invalid username or password. Please try again.")
        except Exception as e:
            messagebox.showerror("Login Error", str(e))



class SignupPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#FFFFFF")
        self.session = Session()

        # signup container
        self.signup_container = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=12,
            width=400,
            height=500
        )
        self.signup_container.place(relx=0.5, rely=0.45, anchor="center")
        self.signup_container.grid_propagate(False)

        # logo
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

        # email entry
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

        # username entry
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

        # password entry
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

        # sign Up button
        ctk.CTkButton(
            self.signup_container,
            text="Sign Up",
            width=300,
            height=45,
            corner_radius=16,
            fg_color="#636ae8",
            hover_color="#636ae8",
            command=self.signup_action
        ).pack(pady=20)

        # error label (moved to appear below the sign Up button and above the login section)
        self.error_label = ctk.CTkLabel(
            self.signup_container,
            text="",
            text_color="#DC2626"
        )
        self.error_label.pack(pady=(0, 10))

        # login section
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
            self.error_label.configure(text="Please fill in all fields")
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
