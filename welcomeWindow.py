
import customtkinter
from font_configs import font_path_regular
from PIL import Image

class WelcomeWindow(customtkinter.CTkToplevel):

    BACKGROUND_COLOR = "#2b2b2b"
    TEXT_COLOR_WHITE = "#ffffff"

    def __init__(self, parent):
        super().__init__(parent)
        self.attributes("-alpha", 0.0)
        self.geometry("400x400")
        self.title("Welcome to VisLink")
        self.transient(parent)
        self.grab_set()
        
        # Center of window
        self.update_idletasks()
        
        # This is a scale factor dependent on the size of the screen
        # aka it varies from machine to machine probably but adjust
        # as you can until its centered ( or not )
        scale_factor = 1.5

        scaling = self.tk.call('tk', 'scaling')
        height = 400
        width = 400
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = int(((screen_width/2) - (width/2)) * scale_factor)
        y = int(((screen_height/2) - (height/1.5)) * scale_factor)

        #x = int((screen_width - (width * scaling)) / 2)
        #y = int((screen_height - (height * scaling)) / 2)


        self.geometry(f"{width}x{height}+{x}+{y}")

        # Logo image
        logo_pil = Image.open("./vislink_logo.png")
        logo = customtkinter.CTkImage(dark_image=logo_pil, size=(200,200))

        logo_label = customtkinter.CTkLabel(
            self,
            image=logo,
            text=""
        )

        logo_label.pack(pady=10)


        # Welcome content
        self.welcome_label = customtkinter.CTkLabel(
            self, 
            text = "Welcome to VisualLink",
            font = (font_path_regular, 24, "bold")
        )
        
        
        self.subtitle_label = customtkinter.CTkLabel(
            self, 
            text = "Eye-tracking setup loading...",
            font = ("Arial", 14)
        )
        

        # === PROGRESS BAR =====
        self.progressbar = customtkinter.CTkProgressBar(self, width=300)
        self.progressbar.set(0)


        # Fade in animation
        self.after(100, self.fade_in)

        # ===== FADE IN WELCOME, LOADING, AND PROGRESS
        self.after(1500, self.show_welcome)

        self.after(2500, self.show_subtitle)

        self.after(3500, self.show_progressBar)


        # Auto-close after 12 seconds
        self.after(1000*12, self.close_welcome)

    """
    Fade in label - helper method to help fade in text (by transitioning the color)
    """
    def fade_in_label(self, label, start_hex, end_hex, steps=20, delay=50, current=0):

        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip("#")
            return tuple(int(hex_color[i:i+2], 16) for i in (0,2,4))
        
        def rgb_to_hex(rgb):
            return "#{:02x}{:02x}{:02x}".format(*rgb)
        
        start_rgb = hex_to_rgb(start_hex)
        end_rgb = hex_to_rgb(end_hex)

        if current > steps:
            return
        
        r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * (current / steps))
        g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * (current / steps))
        b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * (current / steps))
        new_color = rgb_to_hex((r, g, b))
        label.configure(text_color=new_color)
        self.after(delay, lambda: self.fade_in_label(label, start_hex, end_hex, steps, delay, current + 1))
    
    def animate_progress(self):
        current = self.progressbar.get()
        if current < 1.0:
            self.progressbar.set(current + 0.01)
            self.after(50, self.animate_progress)
        
    def show_progressBar(self):
        self.progressbar.pack(pady=10)
        self.animate_progress()

    def show_welcome(self):
        self.welcome_label.pack(pady=10)
        self.fade_in_label(self.welcome_label, self.BACKGROUND_COLOR, self.TEXT_COLOR_WHITE)
    
    def show_subtitle(self):
        self.subtitle_label.pack(pady=20)
        self.fade_in_label(self.subtitle_label, self.BACKGROUND_COLOR, self.TEXT_COLOR_WHITE)

    def fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1.0:
            alpha += 0.05
            self.attributes("-alpha", alpha)
            self.after(30, self.fade_in)

    def close_welcome(self):
        self.fade_out()

    def fade_out(self):
        alpha = self.attributes("-alpha")
        if alpha > 0:
            alpha -= 0.05
            self.attributes("-alpha", alpha)
            self.after(30, self.fade_out)
        else:
            self.grab_release()
            self.destroy()
