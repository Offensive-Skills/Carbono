#!/bin/bash

# setup.sh - Script de instalación para la aplicación Offensive Skills
# Este script instala Python3, pip, Docker, Docker Compose y las librerías de pip necesarias.

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
    apt-get install -y python3 python3-pip
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
    apt-get install -y docker-cli 

    # Verificar la instalación de Docker
    if command_exists docker; then
        echo_success "Docker instalado correctamente."
    else
        echo_error "Fallo al instalar Docker."
        exit 1
    fi
fi

# 4. Añadir el usuario actual al grupo docker
CURRENT_USER=$(logname)
if id -nG "$CURRENT_USER" | grep -qw "docker"; then
    echo_success "El usuario '$CURRENT_USER' ya está en el grupo 'docker'."
else
    echo_info "Añadiendo al usuario '$CURRENT_USER' al grupo 'docker'..."
    usermod -aG docker "$CURRENT_USER"
    if id -nG "$CURRENT_USER" | grep -qw "docker"; then
        echo_success "Usuario '$CURRENT_USER' añadido al grupo 'docker' correctamente."
    else
        echo_error "Fallo al añadir el usuario '$CURRENT_USER' al grupo 'docker'."
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

# 6. Instalar librerías de pip necesarias
echo_info "Instalando las librerías de pip necesarias..."


# Actualizar pip
pip install --upgrade pip

# Instalar las librerías
pip install customtkinter==5.2.2 pillow==10.4.0 requests==2.32.3 --break-system-packages

# Verificar la instalación de las librerías
REQUIRED_LIBS=("customtkinter==5.2.2" "pillow==10.4.0" "requests==2.32.3")
for lib in "${REQUIRED_LIBS[@]}"; do
    pip show "${lib%%==*}" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo_success "La librería '$lib' está instalada."
    else
        echo_error "La librería '$lib' no se pudo instalar."
        deactivate
        exit 1
    fi
done

# Desactivar el entorno virtual
deactivate

echo_success "Todas las librerías de pip han sido instaladas correctamente."

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

