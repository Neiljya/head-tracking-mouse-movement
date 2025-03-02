
import customtkinter
from PIL import Image

class WelcomeWindow(customtkinter.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.attributes("-alpha", 0.0)
        self.geometry("400x400")
        self.title("Welcome to VisLink")
        self.transient(parent)
        self.grab_set()
        
        # Center of window
        self.update_idletasks()
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        x = (width - 400) // 2
        y = (height - 300) // 2
        self.geometry(f"400+300+{x}+{y}")

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
            font = ("Arial", 24, "bold")
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
    
    def show_subtitle(self):
        self.subtitle_label.pack(pady=20)

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
