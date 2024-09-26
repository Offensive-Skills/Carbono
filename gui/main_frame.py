import customtkinter as ctk
import subprocess
from gui.styles import apply_dark_theme
from .challenges import ChallengesFrame
from .courses import CoursesFrame 
import tkinter.messagebox as mb
from .styles import DEFAULT_FONT
from classes.CustomDialog import CustomDialog
from PIL import Image, ImageTk
from config.config import Config
from .stats import StatsFrame 
import os
import sys
from classes.CustomDialog import CustomDialog

class MainFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller  # Almacena la referencia al controlador
        self.configure(corner_radius=10)  # Establece el radio de las esquinas del frame
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        apply_dark_theme()  # Aplica el tema oscuro a este frame
        dark_image = Image.open(self.resource_path("pictures/Offs.png"))

        # Convertir las imágenes PIL a CTkImage
        self.ctk_dark_image = ctk.CTkImage(dark_image=dark_image, size=(1200,700))
        self.background_label = ctk.CTkLabel(self, image=self.ctk_dark_image, text="")
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Crear un frame para contener los botones
        #self.buttons_frame = ctk.CTkFrame(self,fg_color=Config.verde_secundario)
        #self.buttons_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER, relwidth=0.2, relheight=0.5)

        self.bind("<Configure>", self.on_resize)
        self.setup_ui()

    def on_resize(self, event):
        new_width = self.winfo_width()
        new_height = self.winfo_height()

        if (new_width*0.7 <  new_height):
            height = new_height
            width = int(new_height * 1.4)
        else:
            width = new_width
            height = int(new_width * 0.7)
        dark_image = Image.open(self.resource_path("pictures/Offs.png"))

        self.ctk_dark_image = ctk.CTkImage(dark_image=dark_image, size=(width,height))
        self.background_label.configure(self, image=self.ctk_dark_image)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)




    def setup_ui(self):
        # Configuración común para todos los botones
        button_style = {
            "width": 300,
            "height": 50,
            "corner_radius": 0,  # Aumento del radio de las esquinas
            "fg_color": "#b8f0ab",  # Color de fondo del botón
            "hover_color": Config.verde_secundario,  # Color de fondo al pasar el ratón
            "text_color": "black",  # Color del texto
            "font":(Config.font_letter,28, "bold")
        }

        button_style_red = {
            "width": 300,
            "height": 50,
            "corner_radius": 0,  # Aumento del radio de las esquinas
            "fg_color": Config.rojo_claro,  # Color de fondo del botón
            "hover_color": Config.rojo,  # Color de fondo al pasar el ratón
            "text_color": "black",  # Color del texto
            "font":(Config.font_letter,28, "bold")
        }

        # Botón "Retos" para comprobar la conexión a internet
        self.button_retos = ctk.CTkButton(
            self, 
            text="Retos", 
            command=lambda: self.switch_frame(ChallengesFrame),
            **button_style
        )
        self.button_retos.place(relx=0.5, rely=0.15, anchor=ctk.CENTER)

        # Botón "Cursos" para navegar a la sección de cursos
        self.button_cursos = ctk.CTkButton(
            self, 
            text="Cursos", 
            command=lambda: self.switch_frame(CoursesFrame),
            **button_style
        )
        self.button_cursos.place(relx=0.5, rely=0.3, anchor=ctk.CENTER)


        # Botón "API token" para ejecutar el script de configuración inicial
        self.button_setup = ctk.CTkButton(
            self, 
            text="Estadísticas", 
            command=lambda: self.controller.show_frame_stats(StatsFrame),
            **button_style
        )
        self.button_setup.place(relx=0.5, rely=0.45, anchor=ctk.CENTER) 

        # Botón "Salir" para cerrar la aplicación
        self.button_exit = ctk.CTkButton(
            self, 
            text="Salir", 
            command=self.master.quit,
            **button_style
        )
        self.button_exit.place(relx=0.5, rely=0.6, anchor=ctk.CENTER)

                # Botón "resetear" 
        self.button_setup = ctk.CTkButton(
            self, 
            text="Resetear datos", 
            command= self.reset_data,
            **button_style_red
        )
        self.button_setup.place(relx=0.5, rely=0.75, anchor=ctk.CENTER) 



    def switch_frame(self, frame_class):
        self.controller.show_frame(frame_class)

    def run_setup(self):
        try:
            result = subprocess.run(["bash", "./utilities/dependencies.sh"], check=True, text=True, capture_output=True)
            CustomDialog(self, title="Configuración", message="La configuración se ha instalado correctamente.")
        except subprocess.CalledProcessError as e:
            CustomDialog(self, title="Error de Configuración", message=f"Se produjo un error: {e.stderr}")



    def reset_data(self):
        # Mostrar mensaje de que las imágenes de Docker se están eliminando
        msj = "Se están eliminando las imágenes de Docker..."
        CustomDialog(self, title="Eliminando imágenes", message=msj)

        subprocess.Popen(["bash", "./gui/scripts/restart_data.sh"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)



    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller crea una carpeta temporal y almacena la ruta en _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

