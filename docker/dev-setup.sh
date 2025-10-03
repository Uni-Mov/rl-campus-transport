#!/bin/bash
# Detener contenedores existentes
docker-compose down

# Limpiar volúmenes y caché
read -p "desea limpiar volúmenes existentes y cache (de tu sistema)? (y/n): " res
if [ "$res" = "y" ]; then
    docker system prune -f
fi

# Preguntar si reconstruir
read -p "desea reconstruir el contenedor? (y/n): " rebuild

if [ "$rebuild" = "y" ]; then
    echo "construyendo contenedores"
    docker compose up --build frontend
else
    echo "ejecutando contenedores existentes"
    docker compose up frontend
fi
