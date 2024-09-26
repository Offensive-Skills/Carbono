import math
import requests
from tkinter import Canvas
import customtkinter as ctk
from config.config import Config


class StatsFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        from gui.main_frame import MainFrame
        self.header_frame = ctk.CTkFrame(self, fg_color=Config.gris_fondo_oscuro)
        self.header_frame.pack(pady=20, fill='x')
        self.stats_label = ctk.CTkLabel(self.header_frame, text="Estadísticas de Avance por Categoría", font=(Config.font_letter, 32, 'bold'))
        self.stats_label.pack(side="left", padx=40, pady=30)

        self.back_button = ctk.CTkButton(
            self.header_frame,
            text="Atrás",
            command=lambda: self.controller.show_frame(MainFrame),
            fg_color=Config.rojo_oscuro, hover_color=Config.rojo_claro,
            text_color="white",
            corner_radius=10,
            font=(Config.font_letter, 18)
        )
        self.back_button.pack(side="right", padx=(10, 20))

        # Ajustes para el Canvas
        self.min_canvas_size = 925
        self.canvas_size = self.min_canvas_size
        self.stats_canvas = Canvas(self, width=self.canvas_size, height=self.canvas_size, bg=Config.gris_fondo_oscuro, highlightcolor=Config.gris_fondo_oscuro, bd=0, highlightbackground=Config.gris_fondo_oscuro)
        self.stats_canvas.pack(pady=20, expand=True)
        self.bind("<Configure>", self.on_resize)
        self.load_stats()

    def reload(self):
        self.load_stats()

    def on_resize(self, event):
        # Mantener el Canvas cuadrado y proporcional al tamaño más pequeño
        new_size = max(self.min_canvas_size, min(event.width, event.height))
        self.stats_canvas.config(width=new_size, height=new_size)
        self.canvas_size = new_size
        self.draw_polygon(self.stats)

    def load_stats(self):
        token = Config.api_token
        response = requests.post(Config.endpoint_get_stats, params={'token': token})
        if response.status_code == 200:
            stats = response.json()
            self.stats = {k: max(30, v) for k, v in stats.items()}
            self.draw_polygon(stats)
        else:
            print("Error al cargar las estadísticas:", response.text)

    def draw_polygon(self, stats):
        points = self.calculate_polygon_points(stats)
        self.stats_canvas.delete("all")
        self.stats_canvas.create_polygon(points, outline=Config.gris_letras, fill=Config.verde_secundario, width=2)
        self.draw_center_circle()
        self.draw_lines_to_vertices(points)
        self.display_stats_text(points, stats)

    def draw_center_circle(self):
        center_x, center_y = self.canvas_size / 2, (self.canvas_size / 2  - 100)
        radius = 3  # Radio del círculo ajustable
        self.stats_canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius, fill=Config.gris_letras)

    def draw_lines_to_vertices(self, points):
        center_x, center_y = self.canvas_size / 2, (self.canvas_size / 2  - 100)
        for i in range(0, len(points), 2):
            x, y = points[i], points[i + 1]
            self.stats_canvas.create_line(center_x, center_y, x, y, fill=Config.gris_letras, width=2)

    def calculate_polygon_points(self, stats):
        center_x, center_y = self.canvas_size / 2, (self.canvas_size / 2  - 100)
        angle = 360 / len(stats)
        radius = self.canvas_size * 0.22  
        points = []
        for i, (category, percent) in enumerate(stats.items()):
            theta = math.radians(angle * i)
            x = center_x + radius * math.cos(theta) * (percent / 130)
            y = center_y + radius * math.sin(theta) * (percent / 130)
            points.extend([x, y])
        return points

    def display_stats_text(self, points, stats):
        center_x, center_y = self.canvas_size / 2, (self.canvas_size / 2  - 100)
        angle = 360 / len(stats)
        radius = self.canvas_size * 0.36  # Posición del texto respecto al tamaño del canvas
        for i, (category, percent) in enumerate(stats.items()):
            theta = math.radians(angle * i)
            x = center_x + radius * math.cos(theta)
            y = center_y + radius * math.sin(theta)
            display_percent = percent - 30
            self.stats_canvas.create_text(x, y, text=f"{category}: {display_percent:.1f}%", fill='white', font=(Config.font_letter, 14, 'bold'))
