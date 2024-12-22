# gui/login_frame.py
import customtkinter as ctk
from config.config import Config
from classes.CustomDialog import CustomDialog

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Establecer el color de fondo
        self.configure(fg_color=Config.gris_fondo)

        # Crear y colocar los widgets utilizando los colores especificados

        # Marco para centrar el formulario de inicio de sesión
        self.login_frame = ctk.CTkFrame(self, fg_color=Config.gris_fondo_oscuro)
        self.login_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        # Etiqueta de título
        self.title_label = ctk.CTkLabel(
            self.login_frame, 
            text="Iniciar Sesión", 
            text_color=Config.gris_letras, 
            font=(Config.font_letter, 24, "bold")
        )
        self.title_label.pack(pady=(20, 10))

        # Etiqueta y campo de entrada para el nombre de usuario
        self.username_label = ctk.CTkLabel(
            self.login_frame, 
            text="Usuario:", 
            text_color=Config.gris_letras
        )
        self.username_label.pack(pady=(10, 5))
        self.username_entry = ctk.CTkEntry(
            self.login_frame, 
            width=300, 
            fg_color=Config.gris_fondo_oscuro, 
            text_color=Config.gris_letras
        )
        self.username_entry.pack(pady=(0, 10))

        # Etiqueta y campo de entrada para el API token
        self.token_label = ctk.CTkLabel(
            self.login_frame, 
            text="API Token:", 
            text_color=Config.gris_letras
        )
        self.token_label.pack(pady=(10, 5))
        self.token_entry = ctk.CTkEntry(
            self.login_frame, 
            width=300, 
            show="*", 
            fg_color=Config.gris_fondo_oscuro, 
            text_color=Config.gris_letras
        )
        self.token_entry.pack(pady=(0, 20))

        # Botón de inicio de sesión
        self.login_button = ctk.CTkButton(
            self.login_frame, 
            text="Iniciar Sesión", 
            command=self.login, 
            fg_color=Config.verde_botones, 
            hover_color=Config.verde_secundario,
            text_color="black",
            font=(Config.font_letter, 16, "bold")
        )
        self.login_button.pack(pady=(0, 20))

    def login(self):
        username = self.username_entry.get()
        api_token = self.token_entry.get()

        if not username or not api_token:
            CustomDialog(self, title="Error", message="Por favor, ingresa el usuario y el API token")
            return

        # Llamar al método perform_login en el controlador
        self.controller.perform_login(username, api_token)
