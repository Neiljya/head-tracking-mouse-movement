#import tkinter as tk
import customtkinter
from frame import Frame
from welcomeWindow import *
import cv2
from PIL import Image, ImageTk
import time
import threading



customtkinter.set_default_color_theme("dark-blue")






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







class Frontend(customtkinter.CTk):

    # VARIABLES
    HEADER_TEXT = "VisualLink"
    SENSITIVTY_LABEL = "Sensitivity"
    BLINK_INTERVAL_LABEL = "Blink Interval"

    def __init__(self, blinkIntervalLeftClick, blinkIntervalRightClick, sensitivity=1, countdown=3):
        super().__init__()
        self.sensitivity = sensitivity
        self.blinkIntervalLeftClick = blinkIntervalLeftClick
        self.blinkIntervalRightClick = blinkIntervalRightClick
        self.countdown = countdown

        import tkinter as tk

        if tk._default_root is None:
            tk._default_root = self

        # tkinter setup
        # Window SETUP
        self.geometry("1000x500")
        self.title(self.HEADER_TEXT)

        """
        Custom Grid System:
        
        - Each col/row has to be configured individually:
        SYNTAX: self.grid_rowconfigure(int, weight, minsize)
        or self.grid_colconfigure(int, weight, minsize)

        - int corresponds to # of the row/col
        - weight corresponds to space between, higher weight = more space
        - min size is the min size of the row/col
        
        """
        
        for i in range(3):
            self.grid_rowconfigure(i, weight=1)

        for i in range(5):
            self.grid_columnconfigure(i, weight=1)


        # Creating webcame area on left-hand side
        self.webcam_area = customtkinter.CTkLabel(
            self, 
            text = "Webcam Feed Here", 
            font = ("Arial", 20), 
            #width = 900, 
            #height = 550, 
            bg_color="gray30", 
            corner_radius=20
            )

        self.webcam_area.grid(
            row = 0,
            column = 0,
            rowspan = 3, # Maximizes height
            columnspan = 4, # Leaves room for sliders
            padx = 20,
            pady = 20,
            sticky = "nsew"
        )
        

        #self.header = customtkinter.CTkLabel(self, text=self.HEADER_TEXT, fg_color="transparent")
        #self.header.grid(row=0,column=0,padx=20,pady=10,sticky="nsew")

        ###########################################################################
        ############### INITIALIZING THE UI ELEMENTS ##############################
        ###########################################################################

        # goes on the right-hand side
        self.initSliders()

        self.cap = cv2.VideoCapture(0)

    def countDown(self, countdown=3):
        if countdown is None:
            countdown = self.countdown
        if countdown >= 0:
            self.webcam_area.configure(text=str(countdown))
            self.after(1000, lambda: self.countDown(countdown-1))
        else:
            self.updateVideoFeed()

    def cleanup(self) -> None:
        try:
            self.cap.release()
            self.quit()
            exit()
        except Exception as e:
            print(e)

    def updateVideoFeed(self):
        ret, frame = self.cap.read()
        
        self.webcam_area.configure(text="+") # mark the center of the screen

        # turns cv footage into image so we can display it in
        # tkinter
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            imgtk = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=imgtk)
            
            self.webcam_area.imgtk = imgtk
            self.webcam_area.configure(image=imgtk)

            self.webcam_area.after(5, self.updateVideoFeed)

    def updateWebCamImage(self, pilImg):
        try:
            #imgtk = ImageTk.PhotoImage(image=pilImg, master=self)

            width, height = pilImg.size

            ctk_img = customtkinter.CTkImage(dark_image=pilImg, size=(width, height))

            self.webcam_area.configure(image=ctk_img, text="")
            self.webcam_area.image = ctk_img
        except Exception as e:
            print("Could not update webcam image: ",e)

    def updateSensitivity(self, newSensitivity):
        self.sensitivity = newSensitivity
        self.sensitivityLabel.configure(text=f"{self.SENSITIVTY_LABEL} ({self.sensitivity:.1f})")

        print(self.sensitivity)

        
    
    # METHODS FOR INITIALIZING THE UI
    
    def initSliders(self, width=200, row_count=3, col_count=5, row_weight=0, col_weight=0):

        self.testFrame = Frame(master=self, 
                               row_count=row_count, 
                               col_count=col_count, 
                               row_weight=row_weight, 
                               col_weight=col_weight)

        self.testFrame.grid(row=0,
                            column=col_count-1, 
                            rowspan=row_count, 
                            columnspan=1,
                            padx=20,
                            pady=20,
                            sticky="nse")

        # sensitivty sliders

        self.sensitivitySlider = customtkinter.CTkSlider(self.testFrame, 
                                                        from_=0, 
                                                        to=10,
                                                        width=width,
                                                        command=lambda value: self.updateSensitivity(value))

        self.sensitivitySlider.grid(row=0, 
                                   column=1, 
                                   columnspan=col_count-1, 
                                   padx=10, 
                                   pady=0, 
                                   sticky="ew")

        self.sensitivityLabel = customtkinter.CTkLabel(self.testFrame, 
                                                      text=f"{self.SENSITIVTY_LABEL} ({self.sensitivity})", 
                                                      fg_color="transparent")
        
        self.sensitivityLabel.grid(row=0, 
                                  column=0, 
                                  padx=20, 
                                  pady=10, 
                                  sticky="ew")
        
        # blink intervals
        
        self.blinkIntervalSlider = customtkinter.CTkSlider(self.testFrame, 
                                                        from_=0, 
                                                        to=5,
                                                        width=width)

        self.blinkIntervalSlider.grid(row=1, 
                                   column=1, 
                                   columnspan=col_count-1, 
                                   padx=10, 
                                   pady=0, 
                                   sticky="ew")
        
        self.blinkIntervalLabel = customtkinter.CTkLabel(self.testFrame, 
                                                      text= f"{self.BLINK_INTERVAL_LABEL} ({self.blinkIntervalLeftClick})", 
                                                      fg_color="transparent")
        
        self.blinkIntervalLabel.grid(row=1, 
                                  column=0, 
                                  padx=20, 
                                  pady=10, 
                                  sticky="ew")
        
        self.startWebcamBtn = customtkinter.CTkButton(self.testFrame,
                                                      text="Start Webcam",
                                                      command=lambda: self.countDown(self.countdown))
        self.startWebcamBtn.grid(row=5,
                                 column=0,
                                 padx=20,
                                 pady=10,
                                 sticky='s')
        
        self.sensitivitySlider.set(self.sensitivity)
        self.blinkIntervalSlider.set(self.blinkIntervalLeftClick)

        




    # TODO: define methods here

    # Initializes the tracking software

    # Shows image displayed from webcam
    def webcam(self):
        pass

    # Allows sensitivity to be customized
    def customizeSensitivity(self):
        pass


def mainTest():
    app = Frontend(
        blinkIntervalLeftClick=1,
        blinkIntervalRightClick=2,
        sensitivity=1,
        countdown=3
    )

    app.withdraw()

    welcome = WelcomeWindow(app)
    app.wait_window(welcome)

    config_dialogue = ConfigDialogue(app)
    app.wait_window(config_dialogue)

    print(config_dialogue.result)
    if config_dialogue.result:
        settings = config_dialogue.result
        app.blinkIntervalLeftClick = settings["blinkIntervalLeftClick"]
        app.blinkIntervalRightClick = settings["blinkIntervalRightClick"]
        app.sensitivity = settings["sensitivity"]
        app.countdown = settings["countdown"]
    else:
        app.destroy()
        return

    app.after(100, app.deiconify)
    app.mainloop()



if __name__ == '__main__':
    mainTest()
    