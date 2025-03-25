import customtkinter as ctk
from database import Database
from app import DecksPage
from PIL import Image
from tkinter import messagebox

class SignupPage(ctk.CTkFrame):
    # initialises the signup page as a subclass of CTkFrame (inheritance)
    def __init__(self, master):
        super().__init__(master, fg_color="#FFFFFF")

        self.signup_container = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=12,
            width=400,
            height=500
        )
        self.signup_container.place(relx=0.5, rely=0.45, anchor="center")
        self.signup_container.grid_propagate(False)

        self.logo_image = ctk.CTkImage(
            light_image=Image.open("images/logo.png"),
            size=(80, 80)
        )
        ctk.CTkLabel(
            self.signup_container,
            image=self.logo_image,
            text=""
        ).pack(pady=(50, 10))

        ctk.CTkLabel(
            self.signup_container,
            text="Flow Space",
            font=("Inter", 28, "bold"),
            text_color="black",
        ).pack(pady=(0, 30))

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

        ctk.CTkButton(
            self.signup_container,
            text="Sign Up",
            width=300,
            height=45,
            corner_radius=16,
            fg_color="#636ae8",
            hover_color="#636ae8",
            command=self.signup
        ).pack(pady=20)

        self.error = ctk.CTkLabel(
            self.signup_container,
            text="",
            text_color="#DC2626"
        )
        self.error.pack(pady=(0, 10))

        login_link_section = ctk.CTkFrame(self.signup_container, fg_color="transparent")
        login_link_section.pack(pady=5)

        ctk.CTkLabel(
            login_link_section,
            text="Already have an account? ",
            fg_color="transparent",
            text_color="black"

        ).pack(side="left")

        login_link = ctk.CTkLabel(
            login_link_section,
            text="Log in",
            width=60,
            cursor="hand2",
            text_color="#636ae8"
        )
        login_link.pack(side="left")

        # if login link is clicked, switch_page is called to switch the page to LoginPage
        # e is an event object which holds info about mouse position, which widget has been clicked, etc)
        # e is passed into the lambda function so the tkinter knows which button was pressed
        # then the lamda function runs the code on the right side of the colon
        from login import LoginPage
        login_link.bind("<Button-1>", lambda e: self.master.switch_page(LoginPage))

        # above is all the styling code, such as logo image, title, entry fields, buttons and links

    # main signup functionality
    def signup(self):
        # retrieves the username, password and email from the entry fields
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        email = self.email_entry.get().strip()
        # displays error message if username, password or email not entered
        if not username or not password or not email:
            self.error.configure(text="Please fill in all fields")
            return


        try:
            db = Database()
            # create_user stores the users details into the database.
            user_id = db.create_user(username, email, password)
            # if user_id is returned, page is switched to DecksPage
            # if user_id isn't returned (user does not exist in database), then an error message is shown
            if user_id:
                self.master.switch_page(DecksPage, user_id=user_id, switch_page=self.master.switch_page)
            else:
                messagebox.showerror("Error", "Username already exists or failed to create account")
        # if there is any other error during signup, the Exception statement catches it and shows the error
        except Exception as e:
            messagebox.showerror("Signup Error", str(e))
