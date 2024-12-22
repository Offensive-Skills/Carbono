import customtkinter 

BG_COLOR = "#2D2D30"
BUTTON_COLOR = "#3E3E42"
BUTTON_HOVER_COLOR = "#007ACC"
TEXT_COLOR = "#D4D4D4"
# Definiciones de fuentes
FONT_FAMILY = "Helvetica"
FONT_SIZE = 12
FONT_STYLE = "normal"

# Puedes definir otros estilos aquí, como colores, tamaños de botones, etc.
DEFAULT_FONT = (FONT_FAMILY, FONT_SIZE, FONT_STYLE)

def apply_dark_theme():
    customtkinter.set_appearance_mode("Dark")