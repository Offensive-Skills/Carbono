import customtkinter as ctk
from config.config import Config
from gui.styles import apply_dark_theme
import requests
import json
from classes.Module import Module
from gui.course_challenge import CourseChallengeFrame

class ModulesFrame(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.default_size = 400
        self.controller = controller
        self.setup_ui()
        self.bind("<Configure>", self.on_resize)
        self.module_frames = []
        self.title_label = None
        

    def setup_ui(self):
        # Configurar el menú de filtros
        self.course = None
        self.filter_frame = ctk.CTkFrame(self, fg_color=Config.gris_fondo_oscuro)
        self.filter_frame.grid(row=0, column=0, sticky="ew")
        self.setup_filters(self.filter_frame)
        self.module_frames= None
        # Configurar el bloque principal
        self.canvas = ctk.CTkCanvas(self, background=Config.gris_fondo_oscuro, highlightcolor= Config.gris_fondo_oscuro, bd=0, highlightbackground= Config.gris_fondo_oscuro) 
        self.canvas_frame = ctk.CTkFrame(self.canvas, fg_color=Config.gris_fondo)
        self.scrollbar = ctk.CTkScrollbar(self, command=self.canvas.yview, orientation='vertical')
        self.canvas_frame = ctk.CTkFrame(self.canvas)
        
        self.canvas.create_window((0, 0), window=self.canvas_frame, anchor='nw')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=1, column=0, sticky="nsew")
        self.scrollbar.grid(row=1, column=1, sticky='ns')
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        

        self.canvas_frame.bind("<Configure>", self.on_canvas_configure)


    def on_resize(self, event):
        cols = max(1, self.winfo_width() // self.default_size)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.redistribute_frames(cols)

    def on_canvas_configure(self, event):
        # Ajustar el tamaño del canvas al tamaño del frame interno
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def redistribute_frames(self, cols):
        # Borrar el contenido actual de canvas_frame
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        # Crear los frames de nuevo con el nuevo número de columnas
        for i, module in enumerate(self.modules):
            frame = self.create_module_frame(module, cols)
            frame.grid(row=i // cols, column=i % cols, padx=10, pady=10, sticky="nsew")
            self.canvas_frame.grid_columnconfigure(i % cols, weight=1)

    def receive_data(self, course):
        self.course = course
        for frame in self.module_frames:
            frame.destroy()
        self.module_frames.clear()

        self.restart_tittle(self.filter_frame)
        
        data = { "token": Config.api_token, "courseID": course.id }
        try:
            response = requests.post(Config.endpoint_get_modules, json=data)
            if response.status_code == 200:
                
                module_data = response.json()
                if isinstance(module_data, list):
                    
                    self.modules = [Module(id=v['id'] ,tittle=v['name'], description=v['description']) for v in module_data]
                    self.module_frames = []
                    self.redistribute_frames(max(1, self.winfo_width() // self.default_size))
            else:
                module_frame = ctk.CTkFrame(self.canvas_frame, width=400, height=200, corner_radius=10)
                module_frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")

        except requests.exceptions.RequestException as e:
            print(f"Error de conexión: {e}")

    def create_module_frame(self, module, cols):
        # Crear el frame para un curso específico
        frame_width = self.winfo_width() // cols - 20  # Ajustar el ancho del frame al ancho disponible
        module_frame = ctk.CTkFrame(self.canvas_frame, width=frame_width, corner_radius=10, fg_color=Config.gris_fondo)
        
        # Título del curso
        tittle_label = ctk.CTkLabel(module_frame, text=module.tittle, font=(Config.font_letter, 19, "bold"), corner_radius=10, text_color=Config.verde_primario)
        tittle_label.pack(fill="x", padx=5, pady=(10, 2))

        # Detalles del curso
        details_label = ctk.CTkLabel(module_frame, width = frame_width - 20 ,text=f"{module.description}", font=(Config.font_letter, 16), corner_radius=10)
        details_label.pack(fill="x", padx=5, pady=10)
        details_label.configure(wraplength=frame_width - 20)

        access_button = ctk.CTkButton(
            module_frame,
            text="Acceder",
            fg_color=Config.verde_primario, hover_color=Config.verde_secundario,
            font=(Config.font_letter, 18),
            command=lambda: self.accessChallenge(module)
        )
        access_button.pack(side="top", padx=10, pady=10) 

        return module_frame


    def restart_tittle(self, frame):

        if not self.title_label:
            # Crea el título sólo si no existe
            self.title_label = ctk.CTkLabel(
                frame,
                font=(Config.font_letter, 32, "bold"),
                text_color=Config.gris_letras
            )
            self.title_label.grid(row=0, column=1, padx=10, pady=30, sticky="n")

        # Actualizar texto del título si el curso no es None
        if self.course:
            self.title_label.configure(text=f"{self.course.tittle}")


    def setup_filters(self, frame):
        from gui.courses import CoursesFrame

        # Crear el botón de atrás y alinearlo a la derecha
        back_button = ctk.CTkButton(
            frame,
            text="Atras",
            command=lambda: self.controller.show_frame(CoursesFrame),
            fg_color=Config.rojo_oscuro, hover_color=Config.rojo_claro,
            text_color="white",
            corner_radius=10,
            font=(Config.font_letter, 18)
        )
        back_button.grid(row=0, column=2, padx=10, pady=10, sticky="e")

        if (self.course != None):
            self.title_label = ctk.CTkLabel(
                frame,
                text=f"{self.course.tittle}",
                font=(Config.font_letter, 32, "bold"),
                text_color=Config.gris_letras
            )
            self.title_label.grid(row=0, column=1, padx=10, pady=30, sticky="n")

        # Configurar el grid
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)

    def accessChallenge(self, module):
        self.controller.show_frame_module_challenge(CourseChallengeFrame,self.course, module)
