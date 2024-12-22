#!/bin/bash

if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <container_name>"
    exit 1
fi

# Guarda el nombre del contenedor en una variable
TITTLE=$1
VERSION=$2
name="${TITTLE}${VERSION}"

# Utiliza docker ps para buscar el contenedor
if docker ps --format '{{.Names}}' | grep -w "^$name$" > /dev/null; then
    # Contenedor activo, obtener la IP
    container_ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $name)
    echo "$container_ip"  # Devuelve la IP del contenedor
else
    echo "Inactive"  # No se encontró el contenedor activo
fi
