import customtkinter as ctk
import requests
from gui.styles import apply_dark_theme
from classes.CTkListbox import CTkListbox
import subprocess
from classes.Challenge import Challenge
from config.config import Config
from classes.CustomDialog import CustomDialog
from tkinter import Tk, IntVar
from pathlib import Path
import os
import threading  # Importado para manejar hilos

class ChallengesFrame(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid_columnconfigure(0, weight=4, minsize=300)
        self.grid_columnconfigure(1, weight=8, minsize=800)
        self.grid_rowconfigure(1, weight=1)

        self.current_challenge = None
        self.check_status_job = None
        self.status_label = None
        self.jobs_list = []
        self.statusIP = ""
        self.nombreReto = {}
        self.actual_format = "pdf"
        
        self.setup_ui()
        apply_dark_theme()
        self.bind("<Configure>", self.on_resize)

        # Inicializar variables para la animación de carga
        self.loading_dots = 0
        self.loading_running = False

    # CREA LA ESTRUCTURA PRINCIPAL DE LA PÁGINA QUE PARTE DE SELF, DIVIDIDO EN:
    # - filter_frame: Apartado superior con todos los filtros
    # - challenges_list: Parte de la izquierda con el listado de retos
    # - details_frame: Parte principal con el contenido de un reto

    def setup_ui(self):
        filter_frame = ctk.CTkFrame(self)
        filter_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        filter_frame.grid_columnconfigure(0, weight=1)
        filter_frame.grid_columnconfigure(1, weight=1)
        filter_frame.grid_columnconfigure(2, weight=1)
        filter_frame.grid_columnconfigure(3, weight=1) 

        self.setup_filters(filter_frame)

        # Lista de retos y detalles colocados en una fila inferior
        self.challenges_list = CTkListbox(
            self, 
            command=self.on_challenge_select, 
            hover_color=Config.verde_primario,
            highlight_color=Config.verde_secundario,
            font=(Config.font_letter, 18)
        )
        self.challenges_list.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)

        self.details_frame = ctk.CTkFrame(self)
        self.details_frame.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)

        # Label para mostrar el estado (incluyendo "Loading...")
        self.status_label = ctk.CTkLabel(
            self.details_frame, 
            text="", 
            font=(Config.font_letter, 16), 
            text_color=Config.verde_primario
        )
        self.status_label.pack(pady=(0, 10))

        self.load_challenges()

    # REDIMENSIONAMIENTO DE LA APP. Cuando se hace click se calcular el with y el height
    # entonces se vuelve se reajusto el contenido de cada sección y se carga el reto 
    # llamando a "display_challenge_details". Además se elimina y se carga de nuevo el job
    # que comprueba si el reto actual esta activo.

    def on_resize(self, event):
        new_width = self.winfo_width()
        new_height = self.winfo_height()
        self.grid_columnconfigure(0, weight=4, minsize=new_width*0.3)
        self.grid_columnconfigure(1, weight=8, minsize=new_width*0.7)
        
        if self.current_challenge is not None: 
            self.statusIP = ""
            self.cancel_all_jobs()
            self.display_challenge_details(self.current_challenge)
            if self.current_challenge.is_docker == 1:
                self.check_status()

    # CARGA EL CONTENIDO DE LA PARTE SUPERIOR (FILTRADO DE RETOS).

    def setup_filters(self, frame):
        from gui.main_frame import MainFrame

        levels = ["Facil", "Medio", "Dificil", "Insano"]
        topics = ['criptografia', 'forense', 'esteganografia', 'miscelanea', 'web', 'escalada de privilegios', 'reversing']
        mode = ['todos', 'completados', 'pendientes']

        self.level_var = ctk.StringVar(value="Facil")
        self.topic_var = ctk.StringVar(value="Web")
        self.mode_var = ctk.StringVar(value="Todos")

        level_menu = ctk.CTkOptionMenu(
            frame, 
            variable=self.level_var, 
            values=levels,
            font=(Config.font_letter,15),
            dropdown_font=(Config.font_letter,15),
            fg_color=Config.verde_primario, 
            dropdown_fg_color=Config.verde_primario, 
            button_color=Config.verde_oscuro, 
            button_hover_color=Config.verde_muy_oscuro
        )
        level_menu.grid(row=0, column=0, padx=5, pady=10, sticky="w")

        topic_menu = ctk.CTkOptionMenu(
            frame, 
            variable=self.topic_var, 
            values=topics,
            font=(Config.font_letter,15),
            dropdown_font=(Config.font_letter,15),
            fg_color=Config.verde_primario, 
            dropdown_fg_color=Config.verde_primario, 
            button_color=Config.verde_oscuro, 
            button_hover_color=Config.verde_muy_oscuro
        )
        topic_menu.grid(row=0, column=1, padx=5, pady=10, sticky="w")

        mode_menu = ctk.CTkOptionMenu(
            frame, 
            variable=self.mode_var, 
            values=mode,
            font=(Config.font_letter,15),
            dropdown_font=(Config.font_letter,15),
            fg_color=Config.verde_primario, 
            dropdown_fg_color=Config.verde_primario, 
            button_color=Config.verde_oscuro, 
            button_hover_color=Config.verde_muy_oscuro
        )
        mode_menu.grid(row=0, column=2, padx=5, pady=10, sticky="w")

        search_button = ctk.CTkButton(
            frame, 
            text="Buscar",
            font=(Config.font_letter,18), 
            command=self.load_challenges, 
            fg_color=Config.verde_primario, 
            hover_color=Config.verde_secundario
        )
        search_button.grid(row=0, column=3, padx=5, pady=10, sticky="w")

        back_button = ctk.CTkButton(
            frame,
            text="Atras",
            command=lambda: self.controller.show_frame(MainFrame),
            fg_color=Config.rojo_oscuro,
            hover_color=Config.rojo_claro,
            text_color="white",
            corner_radius=10,
            font=(Config.font_letter,18)
        )
        back_button.grid(row=0, column=4, padx=10, pady=10, sticky="w")

    # REALIZA LA PETICIÓN PARA CARGAR EL LISTADO DE RETOS. Cuando se hace click en en el boton de filtrar retos
    # se realiza una consulta para obtener de nuevo el listado de retos que se almacena en "self.challenges"

    def load_challenges(self):
        params = {
            'token': Config.api_token, 
            'level': self.level_var.get(), 
            'topic': self.topic_var.get(), 
            'type': self.mode_var.get()
        }
        try:
            response = requests.post(Config.endpoint_challenges, params=params)
            response.raise_for_status()  # Verifica que la solicitud fue exitosa
        except requests.exceptions.RequestException as e:
            CustomDialog(self, title="Error", message=f"Error en la solicitud: {e}")
            return

        try:
            challenges_data = response.json()
        except ValueError as e:
            # Si ocurre un error al parsear JSON, lanza una excepción con el contenido de la respuesta
            CustomDialog(self, title="Error", message=f"Error al parsear JSON. Contenido de la respuesta: {response.text}")
            return
        
        # Verifica si la respuesta es una lista y no un diccionario
        if isinstance(challenges_data, list):
            try:
                # Convertir los datos del servidor en una lista de objetos Challenge
                self.challenges = [
                    Challenge(
                        v['name'], 
                        v['description'], 
                        v['is_docker'], 
                        v['version'], 
                        v['id'], 
                        v['has_file'], 
                        v['completed']
                    ) for v in challenges_data
                ]
                self.update_challenge_list_all()
            except KeyError as e:
                CustomDialog(self, title="Error", message=f"Faltan campos esperados en los datos del desafío: {e}")
        else:
            CustomDialog(self, title="Error", message=f"La respuesta no es una lista. Contenido de la respuesta: {challenges_data}")

    # CARGA TODOS LOS RETOS.

    def update_challenge_list_all(self):
        self.nombreReto.clear()
        self.challenges_list.delete(0, "end")
        for challenge in self.challenges:
            if challenge.completed == 1:
                name = f"{challenge.tittle} - Completado"
                self.nombreReto[name] = challenge.tittle
                self.challenges_list.insert("END", name)
            else:
                self.nombreReto[challenge.tittle] = challenge.tittle
                self.challenges_list.insert("end", challenge.tittle)

    # CÓDIGO CUANDO SE HACE CLICK EN UN NUEVO RETO. 
    # Se eliminan los anteriores jobs, y se carga de nuevo la página llamando a
    # load_new_challenge, en el caso que el challenge tenga docker "is_docker=1"
    # Se llama a check_status que dará comienzo al primer job.

    def on_challenge_select(self, selected_option):
        self.statusIP = ""
        self.cancel_all_jobs()
        self.load_new_challenge(self.nombreReto[selected_option])
        if self.current_challenge.is_docker == 1:
            self.check_status()

    # FUNCION AUXILIAR PARA CANCELAR LOS JOBS

    def cancel_all_jobs(self):
        for job in self.jobs_list:
            self.after_cancel(job)
        self.jobs_list = [] 

    # ACTUALIZA EL NOMBRE DEL RETO ACTUAL Y LLAMA A "display_challenge_details".
    # para que cargue en la parte derecho el contenido del reto.

    def load_new_challenge(self, selected_option):
        try:
            for challenge in self.challenges:
                if selected_option == challenge.tittle:
                    self.current_challenge = challenge
                    self.display_challenge_details(self.current_challenge)
        except KeyError:
            CustomDialog(self, title="Error", message=f"La clave '{selected_option}' no existe en el diccionario de desafíos.")

    # CREA UN JOB QUE SE LLAMA CADA 3 SEGUNDOS, en el caso de que el valor haya cambiado
    # se actualiza el contenido con "Inactivo" o con la IP.

    def check_status(self):
        if self.current_challenge is not None:
            script_path = "./gui/scripts/check_docker.sh"
            try:
                result = subprocess.run(
                    [script_path, self.current_challenge.tittle, self.current_challenge.version],
                    capture_output=True, 
                    text=True
                )
                status = result.stdout.strip()
            except Exception as e:
                status = f"Error: {e}"

            if status != self.statusIP:
                self.statusIP = status 
                if self.status_label:
                    self.status_label.destroy()

                if status == "Inactive":
                    self.status_label = ctk.CTkLabel(
                        self.details_frame, 
                        text="Inactivo", 
                        font=(Config.font_letter, 22, "bold"), 
                        text_color=Config.rojo_oscuro
                    )
                else:
                    self.status_label = ctk.CTkLabel(
                        self.details_frame, 
                        text=f"Activo (IP: {status})", 
                        font=(Config.font_letter, 22, "bold"), 
                        text_color=Config.verde_secundario
                    )
                
                self.status_label.pack(pady=(5, 20))

            # Programar la siguiente comprobación
            new_job = self.after(3000, self.check_status)
            self.jobs_list.append(new_job)

    # FUNCION PARA INICIAR, PARAR Y REINICIAR CONTENEDORES

    def run_script(self, mode, action):
        """
        Ejecuta el script para iniciar, parar o reiniciar el contenedor.
        
        :param mode: 0 para iniciar/reiniciar, 1 para parar
        :param action: 'start', 'stop', 'restart'
        """
        # Evitar múltiples animaciones de carga
        if self.loading_running:
            return

        # Iniciar la animación de carga
        self.animate_loading()

        # Ejecutar el script en un hilo separado
        thread = threading.Thread(target=self.run_script_thread, args=(mode, action), daemon=True)
        thread.start()

    def run_script_thread(self, mode, action):
        domain = Config.harbor_domain
        title = self.current_challenge.tittle
        version = self.current_challenge.version

        script_path = "./gui/scripts/script.sh"

        try:
            result = subprocess.run(
                [script_path, f"{domain}/challenges/", title, version, str(mode)],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                # Acción exitosa
                if action == 'start':
                    message = "Contenedor iniciado con exito."
                elif action == 'stop':
                    message = "Contenedor detenido con exito."
                elif action == 'restart':
                    message = "Contenedor reiniciado con exito."
                else:
                    message = "Acción completada con éxito."
            else:
                # Error en la acción
                if action == 'start':
                    message = "Hubo un error al iniciar el contendor."
                elif action == 'stop':
                    message = "Hubo un error al detener el contenedor."
                elif action == 'restart':
                    message = "Hubo un error al reiniciar el contenedor."
                else:
                    message = "Hubo un error al realizar la acción."
        except Exception as e:
            message = f"Error al ejecutar el script: {str(e)}"

        # Actualizar la interfaz desde el hilo principal
        self.after(0, self.on_script_complete, message)

    def on_script_complete(self, message):
        # Detener la animación de carga
        self.stop_loading()

        # Mostrar el mensaje en un CustomDialog
        CustomDialog(self, title="Acción del contenedor", message=message)

    # MÉTODOS PARA ANIMACIÓN DE CARGA

    def animate_loading(self):
        self.loading_dots = 0
        self.loading_running = True
        self.update_loading()

    def update_loading(self):
        if self.loading_running:
            self.loading_dots = (self.loading_dots % 3) + 1
            dots = '.' * self.loading_dots
            self.status_label.configure(text=f"Loading{dots}")
            job = self.after(500, self.update_loading)
            self.jobs_list.append(job)

    def stop_loading(self):
        self.loading_running = False
        # Cancelar todos los trabajos de actualización de carga
        for job in self.jobs_list:
            self.after_cancel(job)
        self.jobs_list = []
        # Restaurar el estado del contenedor si es necesario
        if self.current_challenge and self.current_challenge.is_docker == 1:
            # Forzar una actualización del estado
            self.statusIP = ""
            self.check_status()

    # CODIGO PRINCIPAL QUE MUESTRA TODO EL CONTENIDO DE UN RETO

    def display_challenge_details(self, challenge):
        # TITULO

        for widget in self.details_frame.winfo_children():
            widget.destroy()

        if self.current_challenge.completed == 1:
            tittle = challenge.tittle + " - Completado"
            color = Config.verde_secundario
        else:
            tittle = challenge.tittle
            color = Config.gris_letras 

        tittle_label = ctk.CTkLabel(
            self.details_frame,
            text=tittle,
            font=(Config.font_letter, 35, "bold"),
            text_color=color,
            wraplength=500
        )
        tittle_label.pack(pady=(20, 40))


        # CONTEXTO

        context_label = ctk.CTkLabel(
            self.details_frame,
            text=challenge.description,
            font=(Config.font_letter, 17),
            wraplength=self.winfo_width()*0.61,
            anchor="w",
            justify="left"
        )
        context_label.pack(fill='x', padx=20, pady=(0, 40))

        # ENVIAR LA FLAG

        entry_button_frame = ctk.CTkFrame(self.details_frame, fg_color=Config.gris_fondo)
        entry_button_frame.pack(fill='x', pady=(10, 20), padx=20)

        flag_entry = ctk.CTkEntry(
            entry_button_frame, 
            placeholder_text="Introducir flag", 
            font=(Config.font_letter,18)
        )
        flag_entry.grid(row=0, column=0, sticky="ew", padx=(30, 30))

        submit_button = ctk.CTkButton(
            entry_button_frame,
            text="Enviar Flag",
            fg_color=Config.verde_primario, 
            hover_color=Config.verde_secundario,
            font=(Config.font_letter,18),
            command=lambda: self.send_flag(flag_entry.get()) 
        )
        submit_button.grid(row=0, column=1, sticky="ew")

        entry_button_frame.grid_columnconfigure(0, weight=3) 
        entry_button_frame.grid_columnconfigure(1, weight=1) 

        # CHECKBOX CON EL FORMATO PFD O MD

        checkbox_frame = ctk.CTkFrame(self.details_frame, fg_color=Config.gris_fondo)
        checkbox_frame.pack(fill='x', pady=(10, 10), padx=20)

        self.pdf_var = IntVar()
        self.md_var = IntVar()

        self.pdf_var.set(1)
        self.actual_format = "pdf"

        def update_checkbox(format):
            self.actual_format = format

            if format == "pdf":
                self.pdf_var.set(1)
                self.md_var.set(0)
            elif format == "md":
                self.pdf_var.set(0)
                self.md_var.set(1)

        self.checkbox_pdf = ctk.CTkCheckBox(
            checkbox_frame, 
            text="PDF",
            onvalue=1, 
            offvalue=0, 
            variable=self.pdf_var,
            command=lambda: update_checkbox("pdf"), 
            fg_color=Config.gris_fondo, 
            hover_color=Config.verde_secundario
        )
        self.checkbox_pdf.grid(row=0, column=0, padx=20, pady=10)

        self.checkbox_md = ctk.CTkCheckBox(
            checkbox_frame, 
            text="MD", 
            onvalue=1, 
            offvalue=0, 
            variable=self.md_var,
            command=lambda: update_checkbox("md"), 
            fg_color=Config.gris_fondo, 
            hover_color=Config.verde_secundario
        )
        self.checkbox_md.grid(row=1, column=0, padx=20)

        get_writeup_frame = ctk.CTkFrame(self.details_frame, fg_color=Config.gris_fondo)
        get_writeup_frame.pack(fill='x', pady=(10, 20), padx=20)

        submit_button_writeup = ctk.CTkButton(
            get_writeup_frame,
            text="Descargar writeup",
            fg_color=Config.verde_primario, 
            hover_color=Config.verde_secundario,
            font=(Config.font_letter,18),
            command=lambda: self.download_writeup() 
        )
        submit_button_writeup.grid(row=0, column=1, sticky="ew")

        if challenge.has_file == 1:
            get_files_frame = ctk.CTkFrame(self.details_frame, fg_color=Config.gris_fondo)
            get_files_frame.pack(fill='x', pady=(10, 20), padx=20)

            submit_button_has_file = ctk.CTkButton(
                get_files_frame,
                text="Descargar ficheros del reto",
                fg_color=Config.verde_primario, 
                hover_color=Config.verde_secundario,
                font=(Config.font_letter,18),
                command=lambda: self.obtainFiles() 
            )
            submit_button_has_file.grid(row=0, column=1, sticky="ew")

        # BOTONES DE RUN, STOP y RESTART
        if challenge.is_docker == 1:

            button_frame = ctk.CTkFrame(self.details_frame, fg_color=Config.gris_fondo)
            button_frame.pack(side="bottom", expand=False, padx=10, pady=10)

            self.check_status()

            run_button = ctk.CTkButton(
                button_frame, 
                text="Iniciar",
                font=(Config.font_letter,18), 
                command=lambda: self.run_script(0, 'start'),  # Modificado para incluir acción
                fg_color=Config.verde_oscuro, 
                corner_radius=30, 
                hover_color=Config.verde_secundario
            )
            run_button.pack(side="left", expand=True, fill="x", padx=(30, 0))

            stop_button = ctk.CTkButton(
                button_frame, 
                text="Parar",
                font=(Config.font_letter,18), 
                command=lambda: self.run_script(1, 'stop'),  # Modificado para incluir acción
                fg_color=Config.verde_oscuro, 
                corner_radius=30, 
                hover_color=Config.verde_secundario
            )
            stop_button.pack(side="left", expand=True, fill="x", padx=(30, 30))

            restart_button = ctk.CTkButton(
                button_frame, 
                text="Reiniciar",
                font=(Config.font_letter,18), 
                command=lambda: self.run_script(0, 'restart'),  # Modificado para incluir acción
                fg_color=Config.verde_oscuro, 
                corner_radius=30, 
                hover_color=Config.verde_secundario
            )
            restart_button.pack(side="left", expand=True, fill="x", padx=(0, 30))

    # FUNCION PARA ENVIAR LA FLAG

    def send_flag(self, flag_value):
        if not flag_value: 
            CustomDialog(self, title="Flag", message="Por favor, introduce una flag.")
            return

        if self.current_challenge is None:
            CustomDialog(self, title="Flag", message="No hay ningún reto seleccionado.")
            return

        url = Config.endpoint_flag
        data = {
            "flag": flag_value,
            "challengeID": self.current_challenge.id,
            "token": Config.api_token
        }

        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                CustomDialog(self, title="Flag", message="La flag introducida es correcta.")
                self.load_challenges()
            else:
                CustomDialog(self, title="Flag", message="La flag introducida no es correcta.")
            
        except requests.exceptions.RequestException as e:
            CustomDialog(self, title="Error", message=f"Error de conexión: {e}")

    # FUNCION PARA DESCARGAR FICHEROS RELACIONADOS

    def obtainFiles(self):
        url = Config.endpoint_get_files
        data = {
            "challengeID": self.current_challenge.id,
            "token": Config.api_token
        }

        try:
            response = requests.post(url, json=data)

            if response.status_code == 200:
                home_path = Config.path
                folder_path = os.path.join(home_path, "Offensive_skills")

                # Crear la carpeta si no existe
                os.makedirs(folder_path, exist_ok=True)

                name = self.current_challenge.tittle.lower()
                challenge_path = os.path.join(home_path, "Offensive_skills", name)

                os.makedirs(challenge_path, exist_ok=True)

                content_path = os.path.join(challenge_path, "content")

                os.makedirs(content_path, exist_ok=True)

                file_path = os.path.join(content_path, f"{name}.zip")

                # Guardar el archivo en la nueva carpeta
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                msj = f"Los archivos se han descargado correctamente: {os.path.join(Config.path, 'Offensive_skills', name, 'content', f'{name}.zip')}"
                CustomDialog(self, title="Files", message=msj)
            else:
                CustomDialog(self, title="Files", message="Hubo un error al descargar el archivo.")
        
        except requests.exceptions.RequestException as e:
            CustomDialog(self, title="Error", message=f"Error de conexión: {e}")

    # FUNCION PARA DESCARGAR EL WRITEUP

    def download_writeup(self):
        url = Config.endpoint_get_writeup
        data = {
            "challengeID": self.current_challenge.id,
            "token": Config.api_token,
            "format": self.actual_format
        }

        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                home_path = Config.path
                folder_path = os.path.join(home_path, "Offensive_skills")

                # Crear la carpeta si no existe
                os.makedirs(folder_path, exist_ok=True)

                name = self.current_challenge.tittle.lower()
                challenge_path = os.path.join(home_path, "Offensive_skills", name)

                os.makedirs(challenge_path, exist_ok=True)

                writeup_path = os.path.join(challenge_path, "writeup")

                os.makedirs(writeup_path, exist_ok=True)

                file_path = os.path.join(writeup_path, f"{name}.{self.actual_format}")

                # Guardar el archivo en la nueva carpeta
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                msj = f"Los archivos se han descargado correctamente: {os.path.join(Config.path, 'Offensive_skills', name, 'writeup', f'writeup.{self.actual_format}')}"
                CustomDialog(self, title="Files", message=msj)
            else:
                CustomDialog(self, title="Files", message="Hubo un error al descargar el archivo.")
        
        except requests.exceptions.RequestException as e:
            CustomDialog(self, title="Error", message=f"Error de conexión: {e}")

    # MÉTODO PARA ANIMAR EL TEXTO DE CARGA

    def animate_loading(self):
        self.loading_dots = 0
        self.loading_running = True
        self.update_loading()

    def update_loading(self):
        if self.loading_running:
            self.loading_dots = (self.loading_dots % 3) + 1
            dots = '.' * self.loading_dots
            self.status_label.configure(text=f"Loading{dots}", text_color=Config.gris_letras)
            job = self.after(500, self.update_loading)
            self.jobs_list.append(job)

    def stop_loading(self):
        self.loading_running = False
        for job in self.jobs_list:
            self.after_cancel(job)
        self.jobs_list = []
        self.status_label.configure(text="")
        if self.current_challenge and self.current_challenge.is_docker == 1:
            self.statusIP = ""
            self.check_status()

    # MÉTODO PARA MANEJAR LA CONCLUSIÓN DEL SCRIPT

    def on_script_complete(self, message):
        self.stop_loading()
        CustomDialog(self, title="Acción del contenedor", message=message)
