# External Imports
import customtkinter as ctk
from database import Database
from sidebar import Sidebar

# dialog is a small window that pops up on top of the main window
class BaseDialog(ctk.CTkToplevel):
    # initializes the base dialog as a subclass of CTkToplevel
    # does not control width/height; that is handled by the subclass
    # only handles central positioning, title, and common container setup
    def __init__(self, title=""):
        super().__init__()
        self.title(title)
        # do not set geometry here; let subclasses manage width and height
        self.resizable(False, False)  # prevent user from resizing the dialog
        self.configure(fg_color="white")
        
        # setup container for dialog contents with padding and rounded corners
        self.container = ctk.CTkFrame(self, fg_color="transparent", corner_radius=12)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # center the dialog on screen once it's idle (subclass should have set geometry)
        self.after_idle(self.center_dialog)
        
        # handle window close event
        self.protocol("WM_DELETE_WINDOW", self.cancel_event)
        # lock focus onto the dialog, preventing clicking outside
        self.grab_set()

    # centers the dialog on screen based on its current geometry
    def center_dialog(self):
        self.update_idletasks()  # ensure geometry info is up-to-date
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"+{x}+{y}")

    # creates a title label for the dialog using common styling
    def create_title(self, text):
        label = ctk.CTkLabel(self.container, text=text, font=("Helvetica", 20, "bold"), text_color="black")
        label.pack(pady=(20, 10))
        return label

    # creates a single-line input field using common styling; returns the entry widget
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

    # creates a button with common styling for dialog actions; returns the button widget
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

    # called when the dialog is closed (via the X button or programmatically)
    def cancel_event(self):
        self.grab_release()  # release focus from the dialog
        self.destroy()       # destroy the dialog window


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
