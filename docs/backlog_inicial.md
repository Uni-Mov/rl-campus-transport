# Backlog inicial

## 🗂️ Organización del repositorio y entorno
- Crear la **estructura de carpetas** para:
  - `backend/`
  - `frontend/`
  - `ia_ml/`
- Configurar `.gitignore` para Python, Node y datos intermedios.
- Preparar **Docker** para:
  - Backend (Flask + dependencias).
  - Frontend (React + Vite).
  - [Opcional] Contenedor para IA/ML (útil si TensorFlow/Keras necesita su propio entorno).
- Documentar cómo levantar los servicios con `docker-compose`.

---

## 🗺️ Análisis de grafo y dataset
- Descargar el grafo de Río Cuarto con OSMnx.
- Explorar y **analizar nodos y aristas**:
  - Listar atributos disponibles.
  - Obtener métricas básicas (cantidad de nodos, longitudes de aristas, tipos de calles, etc.).
- Diseñar un **dataset** que refleje fielmente el grafo:
  - Definir formato de nodos y aristas (CSV o JSON).
  - Asegurar compatibilidad para reconstruir un `MultiDiGraph`.
- Crear un dataset de ejemplo (pocas calles y nodos) para testear.
- Comparar el dataset con el grafo original:
  - Nodos, aristas, atributos clave (`length`, `oneway`, `highway`, etc.).

---

## 🧭 Integración con algoritmos de rutas
- Investigar cómo usar **Dijkstra/A*** con los datos de OSMnx.
- Probar cálculo de rutas simples (sin pasajeros).
- Documentar cómo el RL podría usar esos tiempos como recompensas.

---

## 🎨 Documentación y comunicación
- Documentar:
  - Representación de la ciudad con OSMnx (nodos/aristas).
  - Estructura del dataset.
  - Organización del repo y estructura de carpetas.
  - Decisiones sobre Docker y dependencias.
- Preparar una breve guía de cómo levantar el entorno y correr ejemplos.

