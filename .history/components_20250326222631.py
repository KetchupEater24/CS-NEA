# External Imports
import customtkinter as ctk
from database import Database
from sidebar import Sidebar

# dialog is a small window that pops up on top of the main window
class BaseDialog(ctk.CTkToplevel):
    # initialises the base dialog  as a subclass of CTkFrame (inheritance)
    # initialises base dialog with width and height    
    def __init__(self, title="", width=width, height=height):
        super().__init__()
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False) # makes sure the user cant resize the dialog window
        self.configure(fg_color="white")
        

        # centers the dialog on screen with the width and height and the x,y position for top left corner of dialog
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"+{x}+{y}")
        
        self.container = ctk.CTkFrame(self, fg_color="transparent", corner_radius=12)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        self.protocol("WM_DELETE_WINDOW", self.cancel_event) # cancel event called when X button on dialog window clicked
        self.grab_set() # locks focus onto the dialog, preventing the user clicking on anything outside the dialog

    # window title for dialog
    def create_title(self, text):
        label = ctk.CTkLabel(self.container, text=text, font=("Helvetica", 20, "bold"), text_color="black")
        label.pack(pady=(20, 10))
        return label

    # base styling for input fields
    def create_input_field(self, initial_value=""):
        entry = ctk.CTkEntry(
            self.container,
            width=300,
            height=45,
            corner_radius=16,
            border_color="#E5E7EB",
            fg_color="transparent",
            text_color="black",
            placeholder_text_color="#6B7280"
        )
        if initial_value:
            entry.insert(0, initial_value)
        entry.pack(pady=10)
        return entry

    # creates a button (to be used to execute dialog actions, e.g changing a deck name)
    def create_button(self, text, command):
        button = ctk.CTkButton(
            self.container,
            text=text,
            width=300,
            height=45,
            corner_radius=16,
            fg_color="#4F46E5",
            hover_color="#4338CA",
            text_color="white",
            command=command
        )
        button.pack(pady=20)
        return button

    def cancel_event(self):
        self.grab_release() # releases focus from the dialog, allowing the user to click on things outside the dialog
        self.destroy() # destroys the dialog


class BasePage(ctk.CTkFrame):
    # initialises basepage with master, user id and switch page, which is a subclass inheriting from CTkFrame
    def __init__(self, master, user_id, switch_page):
        super().__init__(master, corner_radius=0, fg_color="white")
        self.pack(fill="both", expand=True)

        self.user_id = user_id
        self.switch_page = switch_page

        self.db = Database()
        self.user = self.db.get_user(user_id)
        if self.user:
            self.username = self.user["username"]
            
        # create and pack the sidebar on the screen
        self.sidebar = Sidebar(self, switch_page, self.username, self.user_id)
        self.sidebar.pack(side="left", fill="y")

        self.main_header_content = ctk.CTkFrame(self, fg_color="white")
        self.main_header_content.pack(side="right", fill="both", expand=True)

class BaseContainer(ctk.CTkFrame):
    # initialises the base container as a subclass of CTkFrame (inheritance)
    # initialises base container with corner radius, border width, border colour, foreground colour
    def __init__(self, master,corner_radius=12,border_width=1,border_color="#E5E7EB",fg_color="white"):
        super().__init__(master,corner_radius=corner_radius,border_width=border_width,border_color=border_color,fg_color=fg_color)
