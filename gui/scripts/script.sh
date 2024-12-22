#!/bin/bash

# Función para mostrar cómo usar el script
usage() {
    echo "Usage: $0 <domain> <title> <version> <mode>"
    exit 1
}

# Función para verificar si el contenedor está en ejecución
is_container_running() {
    docker inspect --format="{{.State.Running}}" "$1" 2>/dev/null
}

# Función para detener y eliminar un contenedor
stop_and_remove_container() {
    docker stop "$1" > /dev/null 2>&1 &
    wait $!  # Espera a que el comando `docker stop` termine
    docker rm "$1" > /dev/null 2>&1 &
    wait $!  # Espera a que el comando `docker rm` termine
}

# Función para crear y ejecutar un contenedor
create_and_run_container() {
    docker pull "$1" > /dev/null 2>&1 &
    wait $!  # Espera a que el comando `docker pull` termine
    docker run -d --name "$2" "$1" > /dev/null 2>&1 &
    wait $!  # Espera a que el comando `docker run` termine
}

# Verifica si se proporcionaron los argumentos necesarios
if [ "$#" -lt 4 ]; then
    usage
fi

DOMAIN=$1
TITLE=$2
VERSION=$3
MODE=$4
FULL_URI="${DOMAIN}${TITLE}:${VERSION}"
CONTAINER_NAME="${TITLE}${VERSION}"

# Manejar diferentes modos
case $MODE in
    0) # Modo para iniciar el contenedor
        if [[ "$(is_container_running "$CONTAINER_NAME")" == "true" ]]; then
            # Contenedor en ejecución, parar y reiniciar
            stop_and_remove_container "$CONTAINER_NAME"
            create_and_run_container "$FULL_URI" "$CONTAINER_NAME"
        elif docker ps -a --format '{{.Names}}' | grep -wq "$CONTAINER_NAME"; then
            # Contenedor existe pero está parado, eliminar y reiniciar
            stop_and_remove_container "$CONTAINER_NAME"
            create_and_run_container "$FULL_URI" "$CONTAINER_NAME"
        else
            # Contenedor no existe, crear y ejecutar
            create_and_run_container "$FULL_URI" "$CONTAINER_NAME"
        fi
        ;;
    1) # Modo para parar el contenedor
        if [[ "$(is_container_running "$CONTAINER_NAME")" == "true" ]]; then
            # Contenedor en ejecución, pararlo
            docker stop "$CONTAINER_NAME" > /dev/null 2>&1 &
            wait $!  # Espera a que el comando termine
        else
            echo "El contenedor no está en ejecución o no existe."
        fi
        ;;
    *)
        echo "Modo no reconocido. Los modos válidos son 0 o 1."
        usage
        ;;
esac
