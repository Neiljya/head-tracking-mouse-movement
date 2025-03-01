import customtkinter
from frame import Frame

customtkinter.set_default_color_theme("dark-blue")
class Frontend(customtkinter.CTk):

    # VARIABLES
    HEADER_TEXT = "VisualLink"
    SENSITIVTY_LABEL = "Sensitivity"

    def __init__(self, blinkIntervalLeftClick, blinkIntervalRightClick, sensitivity=1, countdown=3):
        super().__init__()
        self.sensitivty = sensitivity
        self.blinkIntervalLeftClick = blinkIntervalLeftClick
        self.blinkIntervalRightClick = blinkIntervalRightClick
        self.countdown = countdown

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
        

        #self.header = customtkinter.CTkLabel(self, text=self.HEADER_TEXT, fg_color="transparent")
        #self.header.grid(row=0,column=0,padx=20,pady=10,sticky="nsew")

        self.initSliders()




    
    # METHODS FOR INITIALIZING THE UI
    def initSliders(self, width=200):
        self.testFrame = Frame(master=self, row_count=3, col_count=5, row_weight=0, col_weight=0)
        self.testFrame.grid(row=0,column=4, rowspan=3, columnspan=1,padx=20,pady=20,sticky="nse")

        self.sensitivtyLabel = customtkinter.CTkLabel(self.testFrame, text=self.SENSITIVTY_LABEL, fg_color="transparent")
        self.sensitivtyLabel.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        self.sensitivtySlider = customtkinter.CTkSlider(self.testFrame, from_=0, to=100,width=width)
        self.sensitivtySlider.grid(row=0, column=1, columnspan=4, padx=10, pady=0, sticky="ew")

    # TODO: define methods here

    # Initializes the tracking software

    # Shows image displayed from webcam
    def webcam(self):
        pass

    # Allows sensitivity to be customized
    def customizeSensitivity(self):
        pass
    


    


if __name__ == '__main__':
    app = Frontend(blinkIntervalLeftClick = 1, blinkIntervalRightClick = 2)
    app.mainloop()