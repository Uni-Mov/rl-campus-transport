# User Model and Schema Documentation

## 1. Modelo `User` (SQLAlchemy)

El modelo **User** representa la tabla `users` en la base de datos. Cada instancia de este modelo corresponde a un usuario del sistema.

### Campos del modelo

- **id**: Identificador único del usuario, clave primaria de la tabla.
- **first_name**: Nombre del usuario, obligatorio.
- **last_name**: Apellido del usuario, obligatorio.
- **dni**: Documento Nacional de Identidad del usuario, único y obligatorio.
- **email**: Correo electrónico del usuario, único y obligatorio, utilizado también para login.
- **password_hash**: Hash de la contraseña del usuario; se almacena cifrado y nunca se debe exponer.
- **role**: Enum que define el rol del usuario dentro del sistema; puede ser **DRIVER** (conductor) o **PASSENGER** (pasajero).

### Enum `UserRole`

Define los posibles roles que puede tener un usuario:

- **DRIVER**: Usuario que actúa como conductor.
- **PASSENGER**: Usuario que actúa como pasajero.

### Método `__repr__`

Devuelve una representación legible del objeto User para depuración y logs, mostrando id, nombre completo, email y rol.

---

## 2. Schema `UserSchema` (Pydantic)

El schema **UserSchema** sirve para serializar y validar los datos de los usuarios que se envían o reciben a través de la API.

### Campos del schema

- **id**: Identificador único del usuario.
- **first_name**: Nombre del usuario.
- **last_name**: Apellido del usuario.
- **dni**: Documento Nacional de Identidad.
- **email**: Correo electrónico, validado automáticamente.
- **role**: Rol del usuario, puede ser **driver** o **passenger**.

### Configuración importante

- **orm_mode = True**: Permite que el schema acepte directamente objetos SQLAlchemy y los transforme en JSON listo para la API.
- No incluye `password_hash` para evitar exponer información sensible.

---

## 3. Uso en `api/users.py` (to do hernan)

Para exponer los usuarios a través de la API:

1. Crear un endpoint que consulte la tabla `users` mediante SQLAlchemy.
2. Cada objeto `User` obtenido se convierte a `UserSchema` usando `from_orm`.
3. Convertir cada schema a diccionario y devolver como JSON.
4. La API expone únicamente los campos seguros y validados definidos en el schema.

---

## 4. Qué debe tener `core/database.py` (to do hernan)

- **Motor de conexión**: Conecta la aplicación a la base de datos.
- **SessionLocal**: Fábrica de sesiones para interactuar con la base de datos (consultas, inserciones, actualizaciones).
- **Base**: Clase base de SQLAlchemy de la que heredarán todos los modelos, incluyendo `User`.

Esta configuración central permite que los modelos, schemas y endpoints trabajen de manera consistente y segura con la base de datos.
