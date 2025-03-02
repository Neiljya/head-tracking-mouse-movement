import customtkinter
from frame import Frame




class ConfigDialogue(customtkinter.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Initial Configuration - VisualLink")
        self.geometry("400x500")
        self.transient(parent) # Connects this class to the parent
        self.grab_set()

        # User Variables
        self.sensitivity = customtkinter.DoubleVar(value = 1.0)
        self.blink_left = customtkinter.IntVar(value = 1)
        self.blink_right = customtkinter.IntVar(value = 2)
        self.countdown = customtkinter.IntVar(value = 3)
 
        # Title
        title_label = customtkinter.CTkLabel(self, text = "Configure VisualLink", font = ("Arial", 20))
        title_label.pack(pady = 20)

        # Setting Frame
        self.settings_frame = Frame(master = self, row_count = 4, col_count = 1, row_weight = 1, col_weight = 1)
        self.settings_frame.pack(pady = 10, padx = 20, fill = "both", expand = True)

        # Sensitivity Slider
        sens_label = customtkinter.CTkLabel(self.settings_frame, text= "Sensitivity (0-10):")
        sens_label.grid(row = 0, column = 0, pady = 5, sticky = "w")
        sens_slider = customtkinter.CTkSlider(self.settings_frame, from_ = 0, to = 10, variable = self.sensitivity, width = 200)
        sens_slider.grid(row = 1, column = 0, pady = 5)

        # Blink Interval Left
        blink_left_label = customtkinter.CTkLabel(self.settings_frame, text = "Left Click Blink Interval:")
        blink_left_label.grid(row = 2, column = 0, pady = 5, sticky = "w")
        blink_left_entry = customtkinter.CTkEntry(self.settings_frame, textvariable = self.blink_left, width = 100)
        blink_left_entry.grid(row = 3, column = 0, pady = 5)

        # Blink Interval Right
        blink_right_label = customtkinter.CTkLabel(self.settings_frame, text = "Right Click Blink Interval:")
        blink_right_label.grid(row = 4, column = 0, pady = 5, sticky = "w")
        blink_right_entry = customtkinter.CTkEntry(self.settings_frame, textvariable = self.blink_right, width = 100)
        blink_right_entry.grid(row = 5, column = 0, pady = 5)

        # Countdown Timer
        countdown_label = customtkinter.CTkLabel(self.settings_frame, text = "Countdown(second):")
        countdown_label.grid(row = 6, column = 0, pady = 5, sticky = "w")
        countdown_entry = customtkinter.CTkEntry(self.settings_frame, textvariable = self.countdown, width = 100)
        countdown_entry.grid(row = 7, column = 0, pady = 5)

        # Submit Button
        submit_button = customtkinter.CTkButton(self, text = "Start", command = self.submit, corner_radius = 10)
        submit_button.pack(pady = 20)

        # Stores Results
        self.result = None



    def submit(self):
        try:
            settings = {
                "sensitivity": self.sensitivity.get(),
                "blinkIntervalLeftClick": self.blink_left.get(),
                "blinkIntervalRightClick": self.blink_right.get(),
                "countdown": self.countdown.get()
            }
            if all(v >= 0 for v in settings.values()):
                self.result = settings
                self.grab_release()
                self.destroy()
            else:
                print("All values must be non-negative!")
        except ValueError:
            print("Invalid input! Please enter numbers.")

