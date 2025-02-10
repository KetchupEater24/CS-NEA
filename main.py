# External Imports
import customtkinter as ctk
from tkinter import *
from PIL import ImageTk
# My Imports
from database import Database
from login import LoginPage
from dashboard import DecksPage
from helpers import Session

db = Database()
session = Session()

class Application(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1440x810")
        self.title("Flow Space")
        self._set_appearance_mode("light")
        self.current_page = None
        self.session = session
        self.switch_page(LoginPage)

    def switch_page(self, page_class, **kwargs):
        # Destroy all existing widgets first
        for widget in self.winfo_children():
            widget.destroy()
        self.current_page = page_class(self, **kwargs)
        self.current_page.pack(fill="both", expand=True)

    def check_login(self):
        if not self.session.is_logged_in():
            self.switch_page(LoginPage)
        else:
            self.switch_page(DecksPage, user_id=self.session.get_user_id())

if __name__ == "__main__":
    db.create_tables()
    app = Application()
    app.mainloop()
