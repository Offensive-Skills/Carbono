import customtkinter as ctk

class CustomDialog(ctk.CTkToplevel):
    def __init__(self, parent, title="Mensaje", message=""):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x200")  # Ajusta según necesites

        # Configura la ventana para que no pueda cambiar de tamaño
        self.resizable(False, False)

        # Añade un texto
        self.label = ctk.CTkLabel(self, text=message, wraplength=280)
        self.label.pack(pady=20, padx=20)

        # Añade un botón de cerrar
        self.close_button = ctk.CTkButton(self, text="Cerrar", command=self.destroy)
        self.close_button.pack(pady=20)

        # Hace que la ventana bloquea la interacción con la ventana principal hasta que se cierre
        self.transient(parent)
        
        # Asegura que la ventana esté visible antes de establecer el grab
        self.update()
        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window(self)