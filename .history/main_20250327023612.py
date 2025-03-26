import customtkinter as ctk

from database import Database
from login import LoginPage

# application is a subclass that inherits from ctk.CTk (CustomTkinter main window class)
class Application(ctk.CTk):
    # initialises the application window dimensions, theme and title
    def __init__(self):
        super().__init__()
        self.geometry("1440x810")
        self.title("Flow Space")
        self._set_appearance_mode("light")
        # no page has been displayed yet, so current_page is None
        self.current_page = None
        # create database instance to be used throughout the program
        self.db = Database()

        # switches page to login page when application is run
        self.switch_page(LoginPage)

    def switch_page(self, page_class, **kwargs):
        # destroy all widgets in the current window
        for widget in self.winfo_children():
            widget.destroy()
        # create new page and set as current_page
        self.current_page = page_class(self, **kwargs)
        # pack the new page to fill it into the window
        self.current_page.pack(fill="both", expand=True)


# initialise the application class and run the application
if __name__ == "__main__":
    app = Application()
    app.mainloop()
