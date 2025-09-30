# Backend - Estructura del proyecto

Este backend está desarrollado con **Python y Flask**, siguiendo un patrón modular que permite separar responsabilidades y mantener el código escalable y mantenible.

## Estructura de carpetas y archivos

```text
backend/
├── app/
│ ├── api/
│ ├── core/
│ ├── main.py
│ ├── models/
│ ├── repositories/
│ ├── schemas/
│ └── services/
├── requirements.txt
└── tests/
```

### Descripción de las carpetas y archivos principales

- **`app/`**: Contiene toda la lógica de la aplicación.
  
  - **`api/`**: Define los endpoints de la API. Por ejemplo, `users.py` maneja las rutas relacionadas con los usuarios.
  
  - **`core/`**: Configuraciones y utilidades globales. `database.py` gestiona la conexión a la base de datos y la creación de sesiones.
  
  - **`main.py`**: Punto de entrada de la aplicación. Inicializa Flask, registra los endpoints y arranca el servidor.
  
  - **`models/`**: Contiene las definiciones de los modelos de datos que representan las tablas en la base de datos.
  
  - **`repositories/`**: Encapsula la lógica de acceso a los datos usando los modelos definidos en `models/`.
  
  - **`schemas/`**: Contiene los esquemas de validación de datos (ej. usando Pydantic), asegurando que la información que llega a la API sea correcta.
  
  - **`services/`**: Contiene la lógica de negocio de la aplicación, interactuando con los repositorios y realizando las operaciones necesarias.

- **`requirements.txt`**: Lista las dependencias necesarias para ejecutar el proyecto:
  - `Flask`: Framework web principal.
  - `Pydantic`: Validación de datos y esquemas.
  - `SQLAlchemy`: ORM para manejar la base de datos.
  - `pytest`: Framework para pruebas.
  - `pylint`: Herramienta de análisis de código.

- **`tests/`**: Contiene pruebas unitarias y de integración para asegurar que los distintos componentes de la aplicación funcionen correctamente.

---

### Flujo general de la aplicación

1. `main.py` inicia la aplicación Flask y registra los endpoints definidos en `api/`.
2. Los **endpoints** reciben las solicitudes HTTP, validan los datos con los **schemas**, y llaman a los **servicios** correspondientes.
3. Los **servicios** interactúan con los **repositorios**, que a su vez acceden a la **base de datos** a través de los **modelos**.
4. Todo el acceso a la base de datos se gestiona desde `core/database.py`, asegurando conexiones seguras y consistentes.
5. Los tests en `tests/` permiten verificar que los distintos módulos funcionen correctamente y que la API devuelva los resultados esperados.

---

### Tests 

Para ejecutar los tests del backend, asegurate de estar en la carpeta `docker/` y ejecutar el siguiente comando:

```bash
sudo docker compose run --rm backend pytest -v
```

Detalles del comando:

- Levanta un contenedor temporal del servicio `backend`.
- Ejecuta todos los tests que se encuentran en `backend/tests/`.
- Muestra los resultados en modo detallado (`-v` = verbose).
- El contenedor temporal se elimina automáticamente al finalizar (`--rm`).
```

---

### Configuración de Pylint con pre-commit

Para asegurarnos de que todo el código cumpla con las reglas de estilo y buenas prácticas, configuramos **Pylint** con **pre-commit**.  
De esta manera, cada vez que hagas un commit, el código se validará automáticamente.

## 🚀 Instrucciones para instalarlo en tu máquina

1. Entrar a la carpeta `backend`:
   ```bash
   cd backend

2. Activar el Entorno Virtual:
   ```bash
   cd source venv/bin/activate

3. Instalar las Dependencias del Proyecto:
   ```bash
   pip install -r requirements.txt

4. Instalar los Hook de pre-commit:
   ```bash
   pre-commit install

Apartir de ahora, cada vez que hagas:
   ```bash
   git commit -m "mensaje"

Automaticamente se Ejecutara Pylint sobre el codigo de backend/app/


---
