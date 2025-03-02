
import customtkinter


class WelcomeWindow(customtkinter.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.attributes("-alpha", 0.0)
        self.geometry("400x300")
        self.title("Welcome to VisualLink")
        self.transient(parent)
        self.grab_set()
        
        # Center of window
        self.update_idletasks()
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        x = (width - 400) // 2
        y = (height - 300) // 2
        self.geometry(f"400+300+{x}+{y}")

        # Welcome content
        welcome_label = customtkinter.CTkLabel(
            self, 
            text = "Welcome to VisualLink",
            font = ("Arial", 24, "bold")
        )
        welcome_label.pack(pady = 50)
        
        subtitle_label = customtkinter.CTkLabel(
            self, 
            text = "Eye-tracking setup loading...",
            font = ("Arial", 14)
        )
        subtitle_label.pack(pady = 20)


        # Fade in animation
        self.after(100, self.fade_in)

        # Auto-close after 2 seconds
        self.after(2000, self.close_welcome)

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
