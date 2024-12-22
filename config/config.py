from pathlib import Path

class Config:
    main_uri = "https://api.offs.es"
    api_token = None  
    username  = None
    harbor_domain = "harbor.offs.es"
    harbor = "https://harbor.offs.es"
    endpoint_flag = f"{main_uri}/submit_challenge"
    endpoint_challenges = f"{main_uri}/get_challenges"
    endpoint_writeup = f"{main_uri}/writeup"
    endpoint_courses = f"{main_uri}/get_courses"
    endpoint_get_files = f"{main_uri}/get_files"
    endpoint_get_writeup = f"{main_uri}/get_writeup"
    endpoint_get_modules = f"{main_uri}/get_modules"
    endpoint_get_module_challenge = f"{main_uri}/get_challenges_modules"
    endpoint_get_stats = f"{main_uri}/get_stats"
    path = str(Path.home())

    # Colores
    verde_primario = "#0e7f22"
    verde_secundario = "#3a8b48"
    verde_botones = "#0aab26"



    gris_letras = "#c2c2c2"
    gris_fondo = "#333333"
    gris_fondo_oscuro = "#2b2b2b"

    verde_oscuro = "#1e5f10"
    verde_muy_oscuro = "#0d3404"
    
    rojo_oscuro = "#c43131"
    rojo_claro = "#e35757"


    rojo = "#d60000"
    rojo_claro = "#ff603d"

    font_letter = "Courier"

    

    


