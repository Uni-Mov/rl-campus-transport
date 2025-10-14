# Backend - Estructura del Proyecto

Este backend está desarrollado con **Python y Flask**, siguiendo una **arquitectura modular** que separa responsabilidades en distintas capas: **API**, **servicios**, **repositorios**, **modelos** y **configuración del núcleo**.  
Este enfoque facilita la **escalabilidad**, la **mantenibilidad** y la **realización de tests unitarios**.

---

## 🧱 Estructura de Carpetas

```text
backend/
├── app/
│   ├── api/
│   │   
│   ├── core/
│   │   
│   ├── models/
│   │   
│   ├── repositories/
│   │   
│   ├── schemas/
│   │   
│   ├── services/
│   │   
│   └── main.py
├── requirements.txt
└── tests/
```

---

## 📂 Descripción de Carpetas y Archivos Principales

### `app/`
Contiene **toda la lógica del backend** y se organiza por capas.

---

### `api/` — Endpoints de la API

Archivo principal: `users.py`

Define las rutas HTTP disponibles para interactuar con los usuarios.  
Usa **Blueprints** para modularizar la API y separar responsabilidades por entidad.

```python
bp = Blueprint("users", __name__)
```

Ejemplo de endpoint:
```python
@bp.route("/", methods=["GET"])
def list_users():
    with SessionLocal() as session:
        user_repository = UserRepository(session)
        user_service = UserService(user_repository)
        users = user_service.list_users()
    return jsonify(users)
```

👉 Este endpoint obtiene todos los usuarios desde la base de datos.  
Flask gestiona la solicitud, el servicio ejecuta la lógica y el repositorio accede a la base de datos.

Otro ejemplo: obtener un usuario por ID
```python
@bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id: int):
    with SessionLocal() as session:
        user_repository = UserRepository(session)
        user_service = UserService(user_repository)
        user = user_service.get_user(user_id)
        if not user:
            abort(404, description="User not found")
    return jsonify(user)
```

---

### `core/` — Configuración Global y Base de Datos

Archivo: `database.py`

Este módulo **centraliza la conexión a la base de datos** mediante **SQLAlchemy**.

Funciones y componentes clave:

- `engine`: gestiona la conexión a la base de datos PostgreSQL.
- `SessionLocal`: clase de sesión para realizar operaciones con la base de datos.
- `Base`: clase base del ORM, a partir de la cual se definen los modelos.
- `create_tables()`: crea las tablas automáticamente a partir de los modelos.

---

### `models/` — Modelos ORM

Archivo: `user.py`

Define el modelo `User`, que representa una tabla SQL llamada `users`.

```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    dni = Column(String(10), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
```

El modelo incluye métodos útiles:
```python
def full_name(self):
    return f"{self.first_name} {self.last_name}"
```

Y una representación legible para depuración:
```python
def __repr__(self):
    return f"<User(id={self.id}, name='{self.full_name()}', email='{self.email}', role='{self.role.name}')>"
```

---

### `repositories/` — Acceso a Datos

Archivo: `user_repository.py`

El repositorio **encapsula la lógica de acceso a la base de datos**, evitando que el resto del sistema dependa directamente de SQLAlchemy.

```python
class UserRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_all(self):
        return self.db_session.query(User).all()

    def get_by_id(self, user_id: int):
        return self.db_session.query(User).filter(User.id == user_id).first()
```

De esta forma, el repositorio actúa como intermediario entre la base de datos y la capa de servicio.

---

### `services/` — Lógica de Negocio

Archivo: `user_service.py`

Define la **lógica de negocio** asociada a los usuarios.  
Aquí se definen las operaciones que combinan reglas de negocio, validaciones y acceso a datos.

```python
class UserService:
    def list_users(self):
        users = self.user_repository.get_all()
        return [self._serialize(user) for user in users]

    def get_user(self, user_id: int):
        user = self.user_repository.get_by_id(user_id)
        return self._serialize(user) if user else None
```

El método `_serialize()` convierte objetos del modelo en diccionarios JSON listos para enviar al frontend.

---

### `schemas/` — Validación y Serialización

Archivo: `user_schema.py`

Define **esquemas Pydantic** para validar y serializar datos.

```python
class UserSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    dni: str
    email: EmailStr
    role: UserRole

    class Config:
        orm_mode = True
```

Gracias a `orm_mode`, los modelos ORM de SQLAlchemy se pueden transformar fácilmente a esquemas Pydantic.

---

### `main.py` — Punto de Entrada del Backend

Crea e inicializa la aplicación Flask, registra los endpoints y crea las tablas en la base de datos.

```python
def create_app():
    app = Flask(__name__)
    CORS(app, origins="*")
    app.register_blueprint(users_bp, url_prefix="/users")
    create_tables()
    return app
```

Al ejecutarlo directamente, levanta el servidor en modo debug:
```python
if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=5000, debug=True)
```

---

## 🔄 Flujo General de la Aplicación

1. `main.py` inicia Flask y registra los endpoints.
2. Las rutas de `api/users.py` reciben solicitudes HTTP.
3. Los datos se validan con `schemas`.
4. Los `services` aplican la lógica de negocio.
5. Los `repositories` acceden a los `models` y la base de datos.
6. Se devuelve una respuesta JSON al cliente.

---

## 🧪 Ejecución de Tests

Para correr los tests dentro de Docker:

```bash
sudo docker compose up -d db
sudo docker compose run --rm backend pytest -v
```

Explicación:
- Levanta un contenedor con la base de datos.
- Ejecuta las pruebas del backend.
- Muestra los resultados en modo detallado.
- El contenedor temporal se elimina al finalizar.

---

## 🧹 Configuración de Pylint con pre-commit

Para mantener el código limpio y coherente, usamos **pre-commit** para ejecutar Pylint antes de cada commit.

### Instalación

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
pre-commit install
```

Cada vez que ejecutes:

```bash
git commit -m "mensaje"
```

Se correrá automáticamente Pylint sobre el código antes de confirmar los cambios.

---

# 🚀 Ejecución y Pruebas Locales

Para levantar el entorno de desarrollo completo y probar la API, sigue estos pasos desde tu terminal.

---

## 1. 🐳 Iniciar el Entorno con Docker

Estos comandos aseguran que inicies desde un estado limpio y consistente.

### 🔹 Limpiar entorno previo (opcional pero recomendado)

```bash
# Navega a la carpeta que contiene tu docker-compose.yml
cd docker/
sudo docker-compose down -v
```

> Este comando detiene y elimina cualquier contenedor, red o volumen previo.  
> La bandera `-v` es crucial porque borra la base de datos, asegurando que partimos de un estado **100% limpio**.

### 🔹 Reconstruir las imágenes

```bash
sudo docker-compose build --no-cache
```

> Reconstruye las imágenes de Docker desde cero, ignorando la caché.  
> Es útil para evitar problemas con capas corruptas si se modifico el `Dockerfile` o el código fuente.

### 🔹 Levantar los servicios

```bash
sudo docker-compose up
```

> Levanta todos los servicios (**backend, base de datos**, etc.) y muestra sus logs en tiempo real en la terminal.

---

## 2. 🧪 Probar la API

Una vez que los contenedores estén corriendo, puedes probar los endpoints.

### 🧩 Probando Endpoints GET (con el Navegador)

**Listar todos los usuarios (`GET /users/`):**

Abre tu navegador y ve a:
```
http://localhost:5000/users/
```

Resultado esperado: Verás una lista JSON `[]` con todos los usuarios de la base de datos.

**Obtener un usuario específico (`GET /users/<id>`):**

En el navegador, ve a:
```
http://localhost:5000/users/1
```

Resultado esperado: Verás un objeto JSON con los datos del usuario con ID `1`.  
Si no existe, recibirás un error **404**.

---

### ✉️ Probando Endpoints POST (con Postman)

1. Crea una cuenta en **Postman** si aún no la tienes.  
2. Crea una nueva petición y selecciona el método **POST**.  
3. Introduce la URL:
   ```
   http://localhost:5000/users/
   ```
4. Ve a la pestaña **Body**, selecciona la opción **raw** y asegúrate de que el formato sea **JSON**.  
5. Pega el siguiente objeto en el área de texto:

```json
{
    "first_name": "Ana",
    "last_name": "García",
    "dni": "98765432",
    "email": "ana.garcia@example.com",
    "password": "unpasswordmuyseguro123",
    "role": "driver"
}
```

6. Haz clic en **Send**.

> ⚠️ **Importante:** La primera vez, Postman te pedirá que descargues e instales el **Desktop Agent**.  
> Esto es necesario porque tu API se está ejecutando localmente (`localhost`) y el agente de escritorio permite que Postman pueda acceder a ella desde tu propia máquina.

---

## 3. 💾 Persistencia de Datos y Ciclo de Vida

- **Para detener los servicios:**  
  Ve a la terminal donde se está ejecutando `docker-compose up` y presiona **Ctrl + C**.

- **Los datos persisten:**  
  Si después de detenerlo vuelves a ejecutar `sudo docker-compose up`, notarás que los usuarios que creaste con POST siguen ahí.  
  Esto ocurre porque Docker **no elimina el volumen de la base de datos** a menos que se lo indiques.

- **Para borrar todos los datos:**  
  Si quieres empezar de cero, usa:

  ```bash
  sudo docker-compose down -v
  ```

  La próxima vez que inicies, la base de datos estará completamente vacía.

---

## ⚙️ Tecnologías Utilizadas

- **Flask** → Framework web principal.
- **SQLAlchemy** → ORM para interactuar con PostgreSQL.
- **Pydantic** → Validación de datos.
- **pytest** → Testing automatizado.
- **pylint** → Análisis estático del código.
- **Docker Compose** → Orquestación de contenedores para entorno de desarrollo.

---

> 💡 Este diseño modular y desacoplado permite ampliar el backend fácilmente: 
> se pueden agregar nuevas entidades repitiendo la misma estructura (`api`, `models`, `services`, `repositories`, `schemas`).
