# external imports
import customtkinter as ctk
from database import Database
from sidebar import Sidebar

# basic dialog class; no widget creation inside—only window styling and layout
class BaseDialog(ctk.CTkToplevel):
    # initialises dialog with title, dimensions, and centers it on screen
    def __init__(self, title="", width=400, height=300):
        super().__init__()
        # set window title
        self.title(title)
        # set dialog dimensions
        self.geometry(f"{width}x{height}")
        # disable window resizing
        self.resizable(False, False)
        # set background color
        self.configure(fg_color="white")
        # center the dialog on screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        # create a container for dialog content
        self.container = ctk.CTkFrame(self, fg_color="transparent", corner_radius=12)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        # placeholder for result if needed
        self.result = None
        # set protocol for closing (X button) and lock focus to dialog
        self.protocol("WM_DELETE_WINDOW", self.cancel_event)
        self.grab_set()

    # releases focus and destroys the dialog
    def cancel_event(self):
        self.grab_release()
        self.destroy()


# basic basepage class; it sets up a common layout with sidebar and main content.
# It does not include any widget-creation logic.
class BasePage(ctk.CTkFrame):
    # initialises basepage with master (parent widget), user id and switch_page callback
    def __init__(self, master, user_id, switch_page):
        super().__init__(master, corner_radius=0, fg_color="white")
        self.pack(fill="both", expand=True)
        self.user_id = user_id
        self.switch_page = switch_page
        # initialize database and fetch user info
        self.db = Database()
        self.user = self.db.get_user(user_id)
        if self.user:
            self.username = self.user["username"]
        # create and pack the sidebar (imported from sidebar.py)
        self.sidebar = Sidebar(self, switch_page, self.username, self.user_id)
        self.sidebar.pack(side="left", fill="y")
        # create main content area for page-specific widgets
        self.main_content = ctk.CTkFrame(self, fg_color="white")
        self.main_content.pack(side="left", fill="both", expand=True)


# base container class with default styling
class BaseContainer(ctk.CTkFrame):
    # initialises a container with default corner_radius, border_width, border_color, and fg_color.
    def __init__(self, master, corner_radius=12, border_width=1, border_color="#E5E7EB", fg_color="white"):
        super().__init__(master, corner_radius=corner_radius, border_width=border_width, border_color=border_color, fg_color=fg_color)
        # disable geometry propagation to keep set dimensions
        self.pack_propagate(False)


# components class groups common widget factories with consistent styling.
class BaseComponents:
    # creates a regular entry field (used in login, signup dialogs, etc.)
    @staticmethod
    def create_entry(master, placeholder_text="", width=300, height=45, corner_radius=16,
                     fg_color="transparent", border_color="#E5E7EB", text_color="black", 
                     placeholder_text_color="#6B7280"):
        entry = ctk.CTkEntry(
            master,
            placeholder_text=placeholder_text,
            width=width,
            height=height,
            corner_radius=corner_radius,
            fg_color=fg_color,
            border_color=border_color,
            text_color=text_color,
            placeholder_text_color=placeholder_text_color)
        entry.pack(pady=10)
        return entry

    # creates a search entry field; same as entry but can be adjusted later if needed
    @staticmethod
    def create_search_entry(master, placeholder_text="Search...", width=300, height=45, corner_radius=16,
                            fg_color="white", border_color="#e5e7eb", text_color="#000000",
                            placeholder_text_color="#D1D1D1"):
        entry = ctk.CTkEntry(
            master,
            placeholder_text=placeholder_text,
            width=width,
            height=height,
            corner_radius=corner_radius,
            fg_color=fg_color,
            border_color=border_color,
            text_color=text_color,
            placeholder_text_color=placeholder_text_color)
        entry.pack(pady=10)
        return entry

    # creates a date entry field with placeholder "DD-MM-YYYY"
    @staticmethod
    def create_date_entry(master, placeholder_text="DD-MM-YYYY", width=110, height=45, corner_radius=8,
                          fg_color="#F3F4F6", text_color="black"):
        entry = ctk.CTkEntry(
            master,
            placeholder_text=placeholder_text,
            width=width,
            height=height,
            corner_radius=corner_radius,
            fg_color=fg_color,
            text_color=text_color,
            border_width=0)
        entry.pack(pady=10)
        return entry

    # creates a purple (primary) button (for login, signup, start quiz actions)
    @staticmethod
    def create_purple_button(master, text, command, width=300, height=45, corner_radius=16,
                             fg_color="#636ae8", hover_color="#636ae8", text_color="white"):
        button = ctk.CTkButton(
            master,
            text=text,
            command=command,
            width=width,
            height=height,
            corner_radius=corner_radius,
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color)
        button.pack(pady=20)
        return button

    # creates a danger (red) button (for delete actions)
    @staticmethod
    def create_danger_button(master, text, command, width=300, height=45, corner_radius=16,
                             fg_color="#FEE2E2", hover_color="#FECACA", text_color="#DC2626"):
        button = ctk.CTkButton(
            master,
            text=text,
            command=command,
            width=width,
            height=height,
            corner_radius=corner_radius,
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color)
        button.pack(pady=20)
        return button

    # creates a gray button (for edit, add, view details, show graph, etc.)
    @staticmethod
    def create_gray_button(master, text, command, width=300, height=45, corner_radius=16,
                           fg_color="#F3F4F6", hover_color="#E5E7EB", text_color="black"):
        button = ctk.CTkButton(
            master,
            text=text,
            command=command,
            width=width,
            height=height,
            corner_radius=corner_radius,
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color)
        button.pack(pady=20)
        return button

    # creates an option menu for dropdown selections (e.g., priority, graph options)
    @staticmethod
    def create_option_menu(master, values, variable, width=120, corner_radius=8,
                           fg_color="white", button_color="#F3F4F6",
                           button_hover_color="#E5E7EB", text_color="#111827"):
        option_menu = ctk.CTkOptionMenu(
            master,
            values=values,
            variable=variable,
            width=width,
            corner_radius=corner_radius,
            fg_color=fg_color,
            button_color=button_color,
            button_hover_color=button_hover_color,
            text_color=text_color)
        option_menu.pack(pady=10)
        return option_menu

    # creates a regular label with consistent styling
    @staticmethod
    def create_label(master, text, font=("Inter", 14), text_color="black", **kwargs):
        label = ctk.CTkLabel(master, text=text, font=font, text_color=text_color, **kwargs)
        label.pack(pady=10)
        return label
