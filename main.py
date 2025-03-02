import customtkinter
from frame import Frame
from welcomeWindow import *
from configDialogue import *
import cv2
from PIL import Image, ImageTk
import time
import threading
import speech_recognition as sr
import pyautogui

from backend.headPoseEstimator import HeadPoseEstimator as Tracker

customtkinter.set_default_color_theme("dark-blue")


class Frontend(customtkinter.CTk):

    # VARIABLES
    HEADER_TEXT = "VisualLink"
    SENSITIVTY_LABEL = "Sensitivity"
    BLINK_INTERVAL_LEFT_CLICK_LABEL = "Blink Interval Left Click"
    BLINK_INTERVAL_RIGHT_CLICK_LABEL = "Blink Interval Right Click"
    COUNTDOWN_LABEL = "Countdown"
    
    VOICE_COMMANDS = [
        "start webcam - Starts the webcam feed",
        "increase sensitivity - Increases sensitivity by 1",
        "decrease sensitivity - Decreases sensitivity by 1",
        "exit/quit - Closes the application",
        "right click - (Right mouse click)",
        "left click - (Left mouse click)",
        "start typing - Begins typing mode (speak to type)",
        "stop typing - Ends typing mode"
    ]

    def __init__(self, blinkIntervalLeftClick, blinkIntervalRightClick, sensitivity=1, countdown=3):
        super().__init__()
        self.sensitivity = sensitivity
        self.blinkIntervalLeftClick = blinkIntervalLeftClick
        self.blinkIntervalRightClick = blinkIntervalRightClick
        self.countdown = countdown
        self.typing_mode = False

        import tkinter as tk

        if tk._default_root is None:
            tk._default_root = self

        # tkinter setup
        # Window SETUP
        self.geometry("1000x500")
        self.iconbitmap("./vislink_icon.ico")
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
        

        ###########################################################################
        ############### INITIALIZING THE UI ELEMENTS ##############################
        ###########################################################################

        # goes on the right-hand side
        self.initSliders()

        self.cap = cv2.VideoCapture(0)


        # Voice recognition setup
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.listening = False
        self.start_listening()

    def countDown(self, countdown=3):
        if countdown is None:
            countdown = self.countdown
        if countdown >= 0:
            self.webcam_area.configure(text=str(countdown))
            self.after(1000, lambda: self.countDown(countdown-1))
        else:
            self.updateVideoFeed()

    def start_model_and_camera(self):
        self.tracker = Tracker(self.sensitivity)
        self.updateVideoFeed()

    def cleanup(self) -> None:
        try:
            self.cap.release()
            self.quit()
            exit()
        except Exception as e:
            print(e)


    """
    This is where all the camera stuff is
    """
    def updateVideoFeed(self):
        ret, frame = self.cap.read()
        
        self.webcam_area.configure(text="+") # mark the center of the screen

        # turns cv footage into image so we can display it in
        # tkinter
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            frame = self.tracker.process_img(frame) # add more params here

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

        #print(self.sensitivity)

    def updateBlinkIntervalLeftClick(self, newIntervalLeft):
        self.blinkIntervalLeftClick = newIntervalLeft
        self.blinkIntervalLeftLabel.configure(text=f"{self.BLINK_INTERVAL_LEFT_CLICK_LABEL} ({self.blinkIntervalLeftClick:.1f})")
    
    def updateBlinkIntervalRightClick(self, newIntervalRight):
        self.blinkIntervalRightClick = newIntervalRight
        self.blinkIntervalRightLabel.configure(text=f"{self.BLINK_INTERVAL_RIGHT_CLICK_LABEL} ({self.blinkIntervalRightClick:.1f})")
    
    # METHODS FOR INITIALIZING THE UI
    
    def initSliders(self, width=200, row_count=7, col_count=5, row_weight=0, col_weight=0):

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
        
        self.blinkIntervalLeftSlider = customtkinter.CTkSlider(self.testFrame, 
                                                        from_=0, 
                                                        to=5,
                                                        width=width,
                                                        command=lambda value: self.updateBlinkIntervalLeftClick(value))

        self.blinkIntervalLeftSlider.grid(row=1, 
                                   column=1, 
                                   columnspan=col_count-1, 
                                   padx=10, 
                                   pady=0, 
                                   sticky="ew")
        
        self.blinkIntervalLeftLabel = customtkinter.CTkLabel(self.testFrame, 
                                                      text= f"{self.BLINK_INTERVAL_LEFT_CLICK_LABEL} ({self.blinkIntervalLeftClick})", 
                                                      fg_color="transparent")
        
        self.blinkIntervalLeftLabel.grid(row=1, 
                                  column=0, 
                                  padx=20, 
                                  pady=10, 
                                  sticky="ew")

        # blink interval right
        self.blinkIntervalRightSlider = customtkinter.CTkSlider(self.testFrame, 
                                                        from_=0, 
                                                        to=5,
                                                        width=width,
                                                        command=lambda value: self.updateBlinkIntervalRightClick(value))

        self.blinkIntervalRightSlider.grid(row=2, 
                                   column=1, 
                                   columnspan=col_count-1, 
                                   padx=10, 
                                   pady=0, 
                                   sticky="ew")
        
        self.blinkIntervalRightLabel = customtkinter.CTkLabel(self.testFrame, 
                                                      text= f"{self.BLINK_INTERVAL_RIGHT_CLICK_LABEL} ({self.blinkIntervalRightClick})", 
                                                      fg_color="transparent")
        
        self.blinkIntervalRightLabel.grid(row=2, 
                                  column=0, 
                                  padx=20, 
                                  pady=10, 
                                  sticky="ew")

        
        self.startWebcamBtn = customtkinter.CTkButton(self.testFrame,
                                                      text="Start Webcam",
                                                      command=lambda: self.countDown(self.countdown),
                                                      height=40, corner_radius = 10)

        self.startWebcamBtn.grid(row=4,
                                 column=0,
                                 columnspan=col_count,
                                 padx=20,
                                 pady=10,
                                 sticky='ew')

        # countdown
        self.countDownSlider = customtkinter.CTkSlider(self.testFrame,
                                                       from_=0,
                                                       to=30,
                                                       width=width)
        
        self.countDownSlider.grid(row=3,
                                  column=1,
                                  columnspan=col_count-1,
                                  padx=10,
                                  pady=0,
                                  sticky="ew")

        self.countDownLabel = customtkinter.CTkLabel(self.testFrame,
                                                     text=self.COUNTDOWN_LABEL)
        
        self.countDownLabel.grid(row=3,
                                 column=0,
                                 padx=10,
                                 pady=0,
                                 sticky="ew")
        
        # Voice commands section with better formatting
        self.voiceCommandsTextbox = customtkinter.CTkTextbox(self.testFrame, height=200, width=250, 
                                                             font=("Arial", 12), wrap="word")
        self.voiceCommandsTextbox.grid(row=5, column=0, columnspan=col_count, padx=20, pady=10, sticky="nsew")
        
        # Format the voice commands with bullets
        formatted_commands = "Voice Commands:\n\n" + "\n".join([f"• {cmd}" for cmd in self.VOICE_COMMANDS])
        self.voiceCommandsTextbox.insert("0.0", formatted_commands)
        self.voiceCommandsTextbox.configure(state="disabled")
        
        self.sensitivitySlider.set(self.sensitivity)
        self.blinkIntervalLeftSlider.set(self.blinkIntervalLeftClick)
        self.blinkIntervalRightSlider.set(self.blinkIntervalRightClick)


    def start_listening(self):
        # Starts voice recognition on new thread
        self.listening = True
        self.voice_thread = threading.Thread(target = self.listen_for_commands, daemon = True)
        self.voice_thread.start()

    def listen_for_commands(self):
        # Listens for commands during recording
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration = 1)
            print("Voice recognition started. Say 'start webcam', 'increase sensitivity', etc.")
            while self.listening:
                try:
                    audio = self.recognizer.listen(source, timeout = None)
                    command = self.recognizer.recognize_google(audio).lower()
                    print(f"Recognized command: {command}")
                    self.process_command(command)
                except sr.UnknownValueError:
                    print("Could not understand audio.")
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")
                except Exception as e:
                    print(f"Error in voice recognition: {e}")

    def type_text(self, text):
        """Simulate typing the given text using pyautogui."""
        try:
            pyautogui.typewrite(text)
            pyautogui.press("enter")  # Optional: press Enter after each phrase
        except Exception as e:
            print(f"Error typing text: {e}")

    def process_command(self, command):
            # Process commands
        if "start webcam" in command:
            self.after(0, lambda: self.countDown(self.countdown))  # Run countdown on main thread
        elif "increase sensitivity" in command:
            current_sensitivity = self.sensitivitySlider.get()
            new_sensitivity = min(current_sensitivity + 1, 10)  
            self.after(0, lambda: self.sensitivitySlider.set(new_sensitivity))  
            self.after(0, lambda: self.updateSensitivity(new_sensitivity))  
        elif "decrease sensitivity" in command:
            current_sensitivity = self.sensitivitySlider.get()
            new_sensitivity = max(current_sensitivity - 1, 0) 
            self.after(0, lambda: self.sensitivitySlider.set(new_sensitivity))
            self.after(0, lambda: self.updateSensitivity(new_sensitivity))
        elif "exit" in command or "quit" in command:
            self.after(0, self.cleanup) 
        elif "right click" in command:
            pass
        elif "left click" in command:
            pass
        elif "start typing" in command:
            if not self.typing_mode:
                self.typing_mode = True
                print("Typing mode started. Speak text to type, or say 'stop typing' to end.")
                self.after(0, lambda: self.webcam_area.configure(text="Typing Mode: ON"))
        elif "stop typing" in command:
            if self.typing_mode:
                self.typing_mode = False
                print("Typing mode stopped.")
                self.after(0, lambda: self.webcam_area.configure(text="Typing Mode: OFF"))
        elif self.typing_mode:
            # If in typing mode, treat the command as text to type
            print(f"Typing: {command}")
            self.after(0, lambda: self.type_text(command))


    



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
    