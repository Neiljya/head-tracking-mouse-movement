import customtkinter
from frame import Frame

FRAME_COLOR = "#1F1F1F"
class ConfigDialogue(customtkinter.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Initial Configuration - VisualLink")
        self.geometry("450x500")  # Slightly larger for better spacing
        self.transient(parent)  # Connects this class to the parent
        self.grab_set()  # Makes this window modal
        self.resizable(False, False)  # Prevent resizing for consistent layout

        # Variables
        self.sensitivity = customtkinter.DoubleVar(value=1.0)
        self.blink = customtkinter.IntVar(value=1)
        self.countdown = customtkinter.IntVar(value=3)

        # Main Frame for Content
        self.main_frame = customtkinter.CTkFrame(self, corner_radius=15, fg_color=FRAME_COLOR)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Title
        title_label = customtkinter.CTkLabel(
            self.main_frame, 
            text="Configure VisualLink", 
            font=("Arial", 24, "bold"), 
            text_color="white"
        )
        title_label.pack(pady=(20, 10))

        # Settings Frame
        self.settings_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        self.settings_frame.pack(pady=10, padx=20, fill="both", expand=True)
        self.settings_frame.grid_columnconfigure(0, weight=1)

        # Sensitivity Slider
        sens_label = customtkinter.CTkLabel(
            self.settings_frame, 
            text="Sensitivity (0-10):", 
            font=("Arial", 14),
            text_color="white"
        )
        sens_label.grid(row=0, column=0, pady=(10, 5), sticky="w")
        sens_slider = customtkinter.CTkSlider(
            self.settings_frame, 
            from_=0, 
            to=10, 
            variable=self.sensitivity, 
            width=250, 
            corner_radius=8
        )
        sens_slider.grid(row=1, column=0, pady=5, sticky="ew")

        # Blink Interval
        blink_label = customtkinter.CTkLabel(
            self.settings_frame, 
            text="Blink Interval (s):", 
            font=("Arial", 14),
            text_color="white"
        )
        blink_label.grid(row=2, column=0, pady=(20, 5), sticky="w")
        blink_entry = customtkinter.CTkEntry(
            self.settings_frame, 
            textvariable=self.blink, 
            width=120, 
            font=("Arial", 12), 
            corner_radius=8
        )
        blink_entry.grid(row=3, column=0, pady=5, sticky="w")


        # Countdown Timer
        countdown_label = customtkinter.CTkLabel(
            self.settings_frame, 
            text="Countdown (seconds):", 
            font=("Arial", 14),
            text_color="white"
        )
        countdown_label.grid(row=6, column=0, pady=(20, 5), sticky="w")
        countdown_entry = customtkinter.CTkEntry(
            self.settings_frame, 
            textvariable=self.countdown, 
            width=120, 
            font=("Arial", 12), 
            corner_radius=8
        )
        countdown_entry.grid(row=7, column=0, pady=5, sticky="w")

        # Submit Button
        submit_button = customtkinter.CTkButton(
            self.main_frame, 
            text="Start", 
            command=self.submit, 
            font=("Arial", 14), 
            corner_radius=10, 
            height=40, 
            fg_color="#1f538d",  # Matches dark-blue theme
            hover_color="#2a6db5"
        )
        submit_button.pack(pady=20)

        # Stores Results
        self.result = None

    def submit(self):
        try:
            settings = {
                "sensitivity": self.sensitivity.get(),
                "blinkInterval": self.blink.get(),
                "countdown": self.countdown.get()
            }
            if all(v >= 0 for v in settings.values()):
                self.result = settings
                self.grab_release()
                self.destroy()
            else:
                error_label = customtkinter.CTkLabel(
                    self.main_frame, 
                    text="Error: All values must be non-negative!", 
                    text_color="red", 
                    font=("Arial", 12)
                )
                error_label.pack(pady=5)
                self.after(3000, error_label.destroy)  # Auto-remove after 3 seconds
        except ValueError:
            error_label = customtkinter.CTkLabel(
                self.main_frame, 
                text="Error: Invalid input! Please enter numbers.", 
                text_color="red", 
                font=("Arial", 12)
            )
            error_label.pack(pady=5)
            self.after(3000, error_label.destroy)  # Auto-remove after 3 seconds
