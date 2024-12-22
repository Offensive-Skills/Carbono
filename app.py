# app.py
import customtkinter as ctk
from gui.main_frame import MainFrame
from gui.challenges import ChallengesFrame
from gui.courses import CoursesFrame
from gui.course_challenge import CourseChallengeFrame
from gui.modules import ModulesFrame
import argparse
from config.config import Config
import subprocess
from gui.stats import StatsFrame 
import os


class AppController(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Offensive Skills")
        self.geometry("1200x960")
        self.minsize(800, 800)
        self.frames = {}
        self.create_frames()

    def create_frames(self):
        self.grid_columnconfigure(0, weight=1)  # Añade peso a la columna
        self.grid_rowconfigure(0, weight=1)     # Añade peso a la fila
        for F in (MainFrame, ChallengesFrame, CourseChallengeFrame, CoursesFrame, ModulesFrame, StatsFrame): 
            frame = F(parent=self, controller=self)  # Pasar la referencia del controlador
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            frame.grid_remove()  # Oculta inicialmente los frames

        self.show_frame(MainFrame)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.grid()  # Asegura que el frame sea visible
        frame.tkraise()  # Trae al frente el frame deseado

    def show_frame_modules(self, cont,course):
        frame = self.frames[cont]
        frame.grid() 
        frame.tkraise()  
        frame.receive_data(course)

    
    def show_frame_module_challenge(self, cont,course, module):
        frame = self.frames[cont]
        frame.grid() 
        frame.tkraise()  
        frame.receive_data(course,module)

    def show_frame_stats(self, cont):
        frame = self.frames[cont]
        frame.grid() 
        frame.tkraise()  
        frame.reload()

    def run(self):
        self.mainloop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Aplicación de escritorio para realizar pruebas de auditoría en entornos simulados.')
    parser.add_argument('--api-token', type=str, help='API token para acceso a recursos externos', required=True)
    parser.add_argument('--username', type=str, help='Nombre de usuario registrado en offs.es', required=True)
    args = parser.parse_args()

    Config.api_token = args.api_token
    Config.username = args.username

    variable_value = os.getenv("OFFS_PATH")

    if variable_value is not None:

        variable_value_expanded = os.path.expanduser(variable_value)
        if os.path.isdir(variable_value_expanded):
            Config.path = variable_value_expanded

    try:
        login_command = ['docker', 'login', Config.harbor, '-u', Config.username, '--password-stdin']
        process = subprocess.Popen(login_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, error = process.communicate(input=Config.api_token)
        if process.returncode == 0:
            app = AppController()
            app.run()
        else:
            print("Usuario o API token no validos")
        
    except subprocess.SubprocessError as e:
        print(f"Error ejecutando el comando docker: {e}")





