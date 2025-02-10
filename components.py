# External Imports
import customtkinter as ctk

class CustomInputDialog(ctk.CTkToplevel):
    def __init__(self, title="", text="", button_text="OK", initial_value=""):
        super().__init__()
        self.title(title)
        self.geometry("400x300")
        self.resizable(False, False)
        
        # Center the dialog
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 300) // 2
        self.geometry(f"400x300+{x}+{y}")

        # Update the fg_color of the main window
        self.configure(fg_color="white")
        
        # Container frame - remove fg_color since parent is already white
        container = ctk.CTkFrame(self, fg_color="transparent", corner_radius=12)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(
            container,
            text=title,
            font=("Helvetica", 20, "bold"),
            text_color="black"
        ).pack(pady=(20, 10))

        # Description
        ctk.CTkLabel(
            container,
            text=text,
            font=("Helvetica", 14),
            text_color="#6B7280"
        ).pack(pady=(0, 20))

        # Entry
        self.entry = ctk.CTkEntry(
            container,
            width=300,
            height=45,
            corner_radius=16,
            border_color="#E5E7EB",
            fg_color="transparent",
            text_color="black",
            placeholder_text_color="#6B7280"
        )
        if initial_value:
            self.entry.insert(0, initial_value)
        self.entry.pack(pady=10)

        # Button
        ctk.CTkButton(
            container,
            text=button_text,
            width=300,
            height=45,
            corner_radius=16,
            fg_color="#4F46E5",
            hover_color="#4338CA",
            command=self.ok_event
        ).pack(pady=20)

        self.result = None
        self.protocol("WM_DELETE_WINDOW", self.cancel_event)
        self.bind("<Return>", lambda e: self.ok_event())
        self.bind("<Escape>", lambda e: self.cancel_event())
        
        self.entry.focus_force()
        self.grab_set()
        self.wait_window()

    def ok_event(self):
        self.result = self.entry.get()
        self.grab_release()
        self.destroy()

    def cancel_event(self):
        self.result = None
        self.grab_release()
        self.destroy()

    def get_input(self):
        return self.result 