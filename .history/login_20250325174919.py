import customtkinter as ctk
from database import Database
from app import DecksPage
from PIL import Image
from tkinter import messagebox
from components import BaseComponents  # import our components helper

class LoginPage(ctk.CTkFrame):
    # initialises the login page as a subclass of ctk.CTkFrame
    def __init__(self, master):
        super().__init__(master, fg_color="#FFFFFF")
        
        # create login container and center it
        self.login_container = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=12,
            width=400,
            height=500
        )
        self.login_container.place(relx=0.5, rely=0.45, anchor="center")
        self.login_container.grid_propagate(False)
        
        # create logo image
        self.logo_image = ctk.CTkImage(
            light_image=Image.open("images/logo.png"),
            size=(80, 80)
        )
        # display logo image
        ctk.CTkLabel(
            self.login_container,
            image=self.logo_image,
            text=""
        ).pack(pady=(50, 10))
        
        # display title label "Flow Space"
        BaseComponents.create_label(
            self.login_container,
            text="Flow Space",
            font=("Inter", 28, "bold"),
            text_color="black"
        )
        
        # create username entry field using base components
        self.username_entry = BaseComponents.create_entry(
            self.login_container,
            placeholder_text="Username"
        )
        
        # create password entry field using base components
        self.password_entry = BaseComponents.create_entry(
            self.login_container,
            placeholder_text="Password"
        )
        # set password field to hide characters
        self.password_entry.configure(show="•")
        
        # create purple button for login action
        BaseComponents.create_purple_button(
            self.login_container,
            text="Login",
            command=self.login
        )
        
        # create error label for login errors
        self.error = BaseComponents.create_label(
            self.login_container,
            text="",
            text_color="#DC2626"
        )
        
        # create container for signup link section
        signup_link_section = ctk.CTkFrame(self.login_container, fg_color="transparent")
        signup_link_section.pack(pady=5)
        
        # display prompt label for signup link
        BaseComponents.create_label(
            signup_link_section,
            text="Don't have an account? ",
            fg_color="transparent",
            text_color="black"
        ).pack(side="left")
        
        # create signup link label with hand cursor styling
        signup_link = ctk.CTkLabel(
            signup_link_section,
            text="Signup",
            width=60,
            cursor="hand2",
            text_color="#636ae8"
        )
        signup_link.pack(side="left")
        
        # bind signup link click event to switch page to SignupPage
        from signup import SignupPage
        signup_link.bind("<Button-1>", lambda e: self.master.switch_page(SignupPage))
    
    # main login functionality
    def login(self):
        # retrieve username and password from entry fields
        username = self.username_entry.get()
        password = self.password_entry.get()
        # display error if fields are empty
        if not username or not password:
            self.error.configure(text="Please fill in all fields")
            return
        try:
            db = Database()
            user_id = db.verify_login(username, password)
            # switch to decks page if login is successful
            if user_id:
                self.master.switch_page(DecksPage, user_id=user_id, switch_page=self.master.switch_page)
            else:
                messagebox.showerror("Login Failed", "Invalid username or password. Please try again.")
        except Exception as e:
            messagebox.showerror("Login Error", str(e))
