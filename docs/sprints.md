# Sprint 0: Product Discovery

Este documento resume la planificación y objetivos del Sprint 0, cuyo foco es diseñar un MVP basado en un algoritmo de Reinforcement Learning para decidir qué pasajeros conviene recoger.

## Objetivo
Diseñar y planificar un MVP cuyo foco sea un algoritmo de **Reinforcement Learning (RL)** capaz de decidir qué pasajeros conviene recoger, dado un conductor y un conjunto de posibles pasajeros.

## 1. Alcance y restricciones
- El sistema será gratuito; no se consideran pagos ni reparto de costos.
- No se medirán tasas de aceptación, tiempo de espera, cobertura geográfica ni desvíos promedio.
- La privacidad y verificación de identidad no son prioritarias en esta fase; login simple.
- Sprint cada 2 semanas, con retrospectiva del profesor.

## 2. Usuarios
- Cualquier persona de la universidad puede registrarse como conductor o pasajero.
- El rol se puede cambiar en cualquier momento.

## 3. Funcionalidades del MVP
1. Login simple.
2. Perfil de usuario (rol conductor/pasajero, editable).
3. Crear solicitud de viaje.
4. Publicar viaje como conductor (origen, capacidad de asientos).
5. Algoritmo de RL para decidir qué pasajeros recoger.
6. Interfaz de mapa para visualizar conductor y pasajeros.
7. Métricas internas solo para evaluar el modelo (tiempos de viaje).

## 4. Tecnologías y repositorio
- Repositorio único en GitHub, con ramas: `frontend`, `backend`, `ia-ml`.
- **Frontend:** React + Tailwind + Vite + TypeScript.
- **Backend:** Python + Flask + Pytest.
- **IA/ML:** numpy, pandas, scikit-learn, tensorflow, keras.
- **Grafo de calles:** OpenStreetMap + osmnx.

## 5. División de tareas
- En cada sprint: 2 personas para frontend, 2 para backend, 2 para IA/ML.
- Roles rotativos.

## 6. Rol de Dijkstra/A*
- Dijkstra/A* calcula rutas base (sin pasajeros) o tramos entre puntos.
- El RL no reemplaza este cálculo; lo usa para estimar cuánto aumenta el tiempo al insertar pasajeros.

## 7. Premios y castigos
- El agente de RL recibe recompensas basadas en Dijkstra/A*.
- Objetivo: aproximar las rutas del RL a las rutas óptimas calculadas por Dijkstra/A*.

---

# Sprint 1: Análisis y dataset del grafo de Río Cuarto con OSMnx

## 1. Analizar la estructura de nodos y aristas

**Objetivo:**
Comprender cómo OSMnx representa los elementos del grafo y qué información se puede extraer.

**Tareas concretas:**
- Listar todos los nodos y sus atributos (`x`, `y`, `street_count`, `highway`, `elevation`, etc.).
- Listar todas las aristas y sus atributos (`osmid`, `highway`, `length`, `lanes`, `maxspeed`, `oneway`, `reversed`).
- Generar un resumen estadístico de nodos y aristas (promedio de calles por nodo, distribución de longitud de aristas, cantidad de aristas unidireccionales vs bidireccionales).

**Resultado esperado:**
Una tabla o CSV que resuma la estructura del grafo, donde cada fila representa un nodo o una arista, y las columnas correspondan a los atributos clave. Esto permitirá visualizar de manera clara cómo se conecta la ciudad y cuáles son las características de sus calles y cruces.

---

## 2. Diseñar el dataset

**Objetivo:**
Crear un dataset que represente el grafo de Río Cuarto de forma consistente con OSMnx.

**Tareas concretas:**
- Definir el formato de los nodos y aristas para CSV o JSON.
- Asegurarse de que el dataset pueda **reproducir un MultiDiGraph** al ser cargado.
- Crear un ejemplo de dataset con unas pocas calles y nodos para pruebas y testeo.

**Resultado esperado:**
Un dataset estructurado que pueda ser utilizado para recrear el grafo en OSMnx o NetworkX, conservando todos los atributos clave y relaciones entre nodos y aristas.

---

## 3. Probar funcionalidades de OSMnx

**Objetivo:**
Explorar OSMnx y documentar qué funcionalidades pueden ser útiles para el análisis de Río Cuarto.

**Tareas concretas:**
- Encontrar el nodo más cercano a coordenadas específicas (`ox.distance.nearest_nodes`).
- Ver qué atributos se pueden usar para filtrar calles (`highway`, `maxspeed`, `lanes`).
- Probar la visualización de grafos y rutas (`ox.plot_graph`, `ox.plot_graph_route`).
- Probar rutas con waypoints intermedios y subgrafos locales alrededor de un nodo.

**Resultado esperado:**
Un informe o ejemplos de código mostrando cómo estas funcionalidades pueden ayudar a analizar la ciudad, planificar rutas o explorar características de la red vial.

---

## 4. Comparar dataset con grafo de OSMnx

**Objetivo:**
Verificar que el dataset diseñado represente correctamente el grafo de Río Cuarto.

**Tareas concretas:**
- Cargar el dataset y generar un grafo con OSMnx.
- Comparar el número de nodos y aristas con el grafo descargado desde OSMnx.
- Verificar que se preserven los atributos clave (`length`, `oneway`, etc.).

**Resultado esperado:**
Confirmación de que el dataset es fiel al grafo original y puede ser utilizado para análisis y visualización sin pérdida de información.

---

## 5. Documentar y presentar hallazgos

**Objetivo:**
Que el equipo entienda cómo OSMnx representa la ciudad y cómo se traduce al dataset.

**Tareas concretas:**
- Generar gráficos que muestren la distribución de nodos y aristas.
- Documentar ejemplos de rutas, subgrafos y características relevantes.
- Preparar un mini manual de cómo se estructura el dataset y cómo usarlo para análisis y visualización.

**Resultado esperado:**
Documentación clara y ejemplos prácticos que permitan al equipo y futuros colaboradores comprender y utilizar el dataset y el grafo de Río Cuarto de manera efectiva.
