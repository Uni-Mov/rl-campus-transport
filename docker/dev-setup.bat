@echo off
echo configurando entorno de desarrollo...

REM Detener contenedores existentes
docker-compose down

REM Limpiar volúmenes y caché
set /p res= desea limpiar volúmenes existentes y cache (de tu sistema)? (y/n): 

IF "%res%"=="y" (
    docker system prune -f
)

REM Preguntar si reconstruir
set /p rebuild= desea reconstruir el contenedor? (y/n): 

IF "%rebuild%"=="y" (
    echo reconstruyendo contenedores
    docker-compose up --build frontend
) ELSE (
    echo ejecutando contenedores existentes
    docker-compose up frontend
)

pause
