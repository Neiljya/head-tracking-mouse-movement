import customtkinter

class Frame(customtkinter.CTkFrame):
    def __init__(self, master, row_count=1, col_count=1, row_weight=0, col_weight=1, **kwargs):
        super().__init__(master, **kwargs)

        for row in range(row_count):
            self.grid_rowconfigure(row, weight=row_weight,minsize=0)
        
        for col in range(col_count):
            self.grid_columnconfigure(col, weight=col_weight,minsize=0)

