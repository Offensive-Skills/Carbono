#!/bin/bash

# setup.sh - Script de instalación para la aplicación Offensive Skills
# Este script instala Python3, pip, Docker, Docker Compose y las librerías de pip necesarias dentro de un entorno virtual en el directorio del script.

# Función para mostrar mensajes informativos
function echo_info() {
    echo -e "\e[34m[INFO]\e[0m $1"
}

# Función para mostrar mensajes de éxito
function echo_success() {
    echo -e "\e[32m[SUCCESS]\e[0m $1"
}

# Función para mostrar mensajes de error
function echo_error() {
    echo -e "\e[31m[ERROR]\e[0m $1"
}

# Verificar si se está ejecutando como root
if [ "$EUID" -ne 0 ]; then
    echo_error "Por favor, ejecuta este script como root o usando sudo."
    exit 1
fi

# Identificar el usuario no root que invocó sudo
if [ -n "$SUDO_USER" ] && [ "$SUDO_USER" != "root" ]; then
    USER_NAME="$SUDO_USER"
    USER_HOME=$(getent passwd "$USER_NAME" | cut -d: -f6)
else
    echo_error "No se pudo identificar un usuario no root. Asegúrate de ejecutar el script con sudo desde una cuenta de usuario no root."
    exit 1
fi

echo_info "Usuario identificado: $USER_NAME con directorio home en $USER_HOME"

# Detectar el directorio del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo_info "Directorio del script detectado: $SCRIPT_DIR"

# Actualizar la lista de paquetes
echo_info "Actualizando la lista de paquetes..."
apt-get update -y

# Actualizar los paquetes existentes
echo_info "Actualizando los paquetes instalados..."
apt-get upgrade -y

# Función para verificar si un comando existe
function command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Instalar Python3
if command_exists python3; then
    echo_success "Python3 ya está instalado."
else
    echo_info "Instalando Python3..."
    apt-get install -y python3 python3-pip python3-venv
    if command_exists python3; then
        echo_success "Python3 instalado correctamente."
    else
        echo_error "Fallo al instalar Python3."
        exit 1
    fi
fi

# 2. Instalar pip3
if command_exists pip3; then
    echo_success "pip3 ya está instalado."
else
    echo_info "Instalando pip3..."
    apt-get install -y python3-pip
    if command_exists pip3; then
        echo_success "pip3 instalado correctamente."
    else
        echo_error "Fallo al instalar pip3."
        exit 1
    fi
fi

echo_info "Verificando si python3-tk está instalado..."

if dpkg -l | grep -qw python3-tk; then
    echo_success "python3-tk ya está instalado."
else
    echo_info "Instalando python3-tk..."
    apt-get install -y python3-tk
    if dpkg -l | grep -qw python3-tk; then
        echo_success "python3-tk instalado correctamente."
    else
        echo_error "Fallo al instalar python3-tk."
        exit 1
    fi
fi


# 3. Instalar Docker
if command_exists docker; then
    echo_success "Docker ya está instalado."
else
    echo_info "Instalando Docker..."

    # Actualizar el índice de paquetes e instalar paquetes necesarios para usar el repositorio HTTPS
    apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

    # Añadir la clave GPG oficial de Docker
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

    # Añadir el repositorio de Docker a APT
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Actualizar el índice de paquetes
    apt-get update -y

    # Instalar Docker Engine
    apt-get install -y docker-ce docker-cli containerd.io

    # Verificar la instalación de Docker
    if command_exists docker; then
        echo_success "Docker instalado correctamente."
    else
        echo_error "Fallo al instalar Docker."
        exit 1
    fi
fi

# 4. Añadir el usuario al grupo docker
if id -nG "$USER_NAME" | grep -qw "docker"; then
    echo_success "El usuario '$USER_NAME' ya está en el grupo 'docker'."
else
    echo_info "Añadiendo al usuario '$USER_NAME' al grupo 'docker'..."
    usermod -aG docker "$USER_NAME"
    if id -nG "$USER_NAME" | grep -qw "docker"; then
        echo_success "Usuario '$USER_NAME' añadido al grupo 'docker' correctamente."
    else
        echo_error "Fallo al añadir el usuario '$USER_NAME' al grupo 'docker'."
        echo_info "Por favor, cierra la sesión y vuelve a iniciarla para que los cambios surtan efecto."
    fi
fi

# 5. Instalar Docker Compose
DOCKER_COMPOSE_VERSION="2.20.3"

if command_exists docker-compose; then
    echo_success "Docker Compose ya está instalado."
else
    echo_info "Instalando Docker Compose versión $DOCKER_COMPOSE_VERSION..."

    curl -L "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

    chmod +x /usr/local/bin/docker-compose

    # Verificar la instalación
    if command_exists docker-compose; then
        echo_success "Docker Compose instalado correctamente."
    else
        echo_error "Fallo al instalar Docker Compose."
        exit 1
    fi
fi

# 6. Configurar el entorno virtual y instalar las librerías de pip necesarias en el directorio del script
VENV_DIR="$SCRIPT_DIR/venv"

echo_info "Creando entorno virtual en $VENV_DIR..."
sudo -u "$USER_NAME" python3 -m venv "$VENV_DIR"

if [ -d "$VENV_DIR" ]; then
    echo_success "Entorno virtual creado correctamente."
else
    echo_error "Fallo al crear el entorno virtual."
    exit 1
fi

echo_info "Actualizando pip en el entorno virtual..."
sudo -u "$USER_NAME" "$VENV_DIR/bin/pip" install --upgrade pip

echo_info "Instalando las librerías de pip necesarias en el entorno virtual..."
sudo -u "$USER_NAME" "$VENV_DIR/bin/pip" install tk==0.1.0 customtkinter==5.2.2 pillow==10.4.0 requests==2.32.3

# Verificar la instalación de las librerías
REQUIRED_LIBS=("tk" "customtkinter" "pillow" "requests")
declare -A LIB_VERSIONS=( ["tk"]="0.1.0" ["customtkinter"]="5.2.2" ["pillow"]="10.4.0" ["requests"]="2.32.3" )

for lib in "${REQUIRED_LIBS[@]}"; do
    VERSION_EXPECTED=${LIB_VERSIONS[$lib]}
    VERSION_INSTALLED=$(sudo -u "$USER_NAME" "$VENV_DIR/bin/pip" show "$lib" | grep ^Version: | awk '{print $2}')
    if [ "$VERSION_INSTALLED" == "$VERSION_EXPECTED" ]; then
        echo_success "La librería '$lib==$VERSION_EXPECTED' está instalada correctamente."
    else
        echo_error "La librería '$lib==$VERSION_EXPECTED' no se pudo instalar correctamente. Versión instalada: $VERSION_INSTALLED"
        exit 1
    fi
done

echo_success "Todas las librerías de pip han sido instaladas correctamente en el entorno virtual."

# Opcional: Instalar build-essential para compilaciones de paquetes Python
if dpkg -l | grep -qw build-essential; then
    echo_success "build-essential ya está instalado."
else
    echo_info "Instalando build-essential..."
    apt-get install -y build-essential
    if dpkg -l | grep -qw build-essential; then
        echo_success "build-essential instalado correctamente."
    else
        echo_error "Fallo al instalar build-essential."
        exit 1
    fi
fi

# Limpieza
echo_info "Limpiando el caché de APT..."
apt-get clean

echo_success "Instalación y configuración completadas exitosamente."
echo_info "Por favor, reinicia tu sesión para que los cambios en el grupo 'docker' surtan efecto."
echo
echo


echo_info "¡Enhorabuena. Ya has instalado Carbono! "
echo_info "Para poder ejecutarlo, necesitas ejecutar lo siguiente:"
echo_info "    source venv/bin/activate"
echo
echo_info "Ahora podrás arrancar la aplicación ejecutando:"
echo_info "    python app.py --username <user> --api-token <token>"


