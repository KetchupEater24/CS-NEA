import customtkinter as ctk
from database import Database
from app import DecksPage
from PIL import Image

from tkinter import messagebox

class LoginPage(ctk.CTkFrame):
    # initialises the login page as a subclass of CTkFrame (inheritance)
    def __init__(self, master, db):
        super().__init__(master, fg_color="#FFFFFF")
        self.db = db
        self.login_container = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=12,
            width=400,
            height=500
        )
        self.login_container.place(relx=0.5, rely=0.45, anchor="center")
        self.login_container.grid_propagate(False)

        self.logo_image = ctk.CTkImage(
            light_image=Image.open("images/logo.png"),
            size=(80, 80)
        )
        ctk.CTkLabel(
            self.login_container,
            image=self.logo_image,
            text=""
        ).pack(pady=(50, 10))

        ctk.CTkLabel(
            self.login_container,
            text="Flow Space",
            font=("Inter", 28, "bold"),
            text_color=("#000000"),
        ).pack(pady=(0, 30))

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

        ctk.CTkButton(
            self.login_container,
            text="Login",
            width=300,
            height=45,
            corner_radius=16,
            fg_color="#636ae8",
            hover_color="#636ae8",
            command=self.login
        ).pack(pady=20)

        self.error = ctk.CTkLabel(
            self.login_container,
            text="",
            text_color="#DC2626"
        )
        self.error.pack()

        signup_link_section = ctk.CTkFrame(self.login_container, fg_color="transparent")
        signup_link_section.pack(pady=5)

        ctk.CTkLabel(
            signup_link_section,
            text="Don't have an account? ",
            fg_color="transparent",
            text_color="black"
        ).pack(side="left")

        signup_link = ctk.CTkLabel(
            signup_link_section,
            text="Signup",
            width=60,
            cursor="hand2",
            text_color="#636ae8"
        )
        signup_link.pack(side="left")

        # if signup link is clicked, switch_page is called to switch the page to SignupPage
        # e is an event object which holds info about mouse position, which widget has been clicked, etc)
        # e is passed into the lambda function so the tkinter knows which button was pressed
        # then the lambda function runs the code on the right side of the colon
        from signup import SignupPage
        signup_link.bind("<Button-1>", lambda e: self.master.switch_page(SignupPage))

        # above is all the styling code, such as logo image, title, entry fields, buttons and links


    # main login functionality
    def login(self):
        # retrieves the username and password from the entry fields
        username = self.username_entry.get()
        password = self.password_entry.get()
        # displays error message if username or password not entered
        if not username or not password:
            self.error.configure(text="Please fill in all fields")
            return
        
        try:
            # verify_login checks if the username and password exist in the database, in which case the user_id is returned
            user_id = self.db.verify_login(username, password)
            # if user_id is returned, page is switched to DecksPage
            # if user_id isn't returned (user does not exist in database), then an error message is shown

            if user_id:
                self.master.switch_page(DecksPage, user_id=user_id, switch_page=self.master.switch_page, db=self.db)
            else:
                messagebox.showerror("Login Failed", "Invalid username or password. Please try again.")
        # if there is any other error during login, the Exception statement catches it and shows the error
        except Exception as e:
            messagebox.showerror("Login Error", str(e))
