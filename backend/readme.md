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

  - **`core/`**: Configuraciones y utilidades globales. 
    Aquí se define `database.py`, que gestiona la entre Python conexión y la base de datos relacional. 
    Aquí se define la clase Base = declarative_base(), que es la clase a partir de la cual se crean todos los modelos de la aplicación.
    Esto es lo que une Python con las tablas SQL, ya que cualquier clase que herede de Base se convierte automáticamente en una tabla dentro de la base de datos.

  - **`main.py`**: Punto de entrada de la aplicación. 
    Inicializa Flask.
    Habilita CORS para permitir solicitudes desde el frontend.
    Registra los blueprints (módulos de endpoints).
    Finalmente, arranca el servidor para que la API quede disponible.

  - **`models/`**:Contiene las definiciones de los modelos de datos que representan las tablas en la base de datos. 
    Cada modelo (ejemplo: User) hereda de Base (definida en core/database.py).
    Se importa lo necesario para armar el modelo ORM: Column, Integer, String, Enum, etc.
    Se definen enumeraciones (enum.Enum) para valores fijos como roles de usuario.
    Los modelos incluyen métodos útiles como full_name() o __repr__() para representación y depuración.

  - **`repositories/`**: Encapsula la lógica de acceso a los datos usando los modelos definidos en `models/`. 

  - **`schemas/`**: Contiene los esquemas de validación de datos usando Pydantic.
    Estos esquemas se usan para validar la información que llega en los requests (por ejemplo, cuando alguien manda un JSON al crear un usuario).
    También sirven para serializar los datos que devolvemos en las respuestas de la API, asegurando que tengan el formato esperado (ejemplo: que el email sea válido).

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

1. `main.py` inicia la aplicación Flask, configura la base de datos y registra los endpoints definidos en `api/`.
2. Los **endpoints** reciben las solicitudes HTTP, validan los datos con los **schemas**, y llaman a los **servicios** correspondientes.
3. Los **servicios** interactúan con los **repositorios**, que a su vez acceden a la **base de datos** a través de los **modelos**.
4. Todo el acceso a la base de datos se gestiona desde `core/database.py`, asegurando conexiones seguras y consistentes.
5. Los tests en `tests/` permiten verificar que los distintos módulos funcionen correctamente y que la API devuelva los resultados esperados.

---

### Tests 

Para ejecutar los tests del backend, asegurate de estar en la carpeta `docker/` y ejecutar los siguientes comandos:

```bash
sudo docker compose up -d db
sudo docker compose run --rm backend pytest -v
```

Detalles del comando:

- Levanta un contenedor temporal del servicio `backend`.
- Ejecuta todos los tests que se encuentran en `backend/tests/`.
- Muestra los resultados en modo detallado (`-v` = verbose).
- El contenedor temporal se elimina automáticamente al finalizar (`--rm`).

---

### Configuración de Pylint con pre-commit

Para asegurarnos de que todo el código cumpla con las reglas de estilo y buenas prácticas, configuramos **Pylint** con **pre-commit**.  
De esta manera, cada vez que hagas un commit, el código se validará automáticamente.

##  Instrucciones para instalarlo en tu máquina

1. Entrar a la carpeta `backend`:
   ```bash
   cd backend
   ```

2. Activar el Entorno Virtual:
   ```bash
   source venv/bin/activate
   ```

3. Instalar las Dependencias del Proyecto:
   ```bash
   pip install -r requirements.txt
   ```

4. Instalar los Hook de pre-commit:
   ```bash
   pre-commit install
   ```

A partir de ahora, cada vez que hagas:
   ```bash
   git commit -m "mensaje"
   ```

Automáticamente se ejecutará **Pylint** sobre el código de `backend/app`.
