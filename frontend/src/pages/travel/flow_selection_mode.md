# Modo Selección — Flujo detallado de selección de puntos

Este documento explica a fondo cómo funciona el modo de selección de puntos antes del cálculo de la ruta, qué responsabilidades tiene cada pieza y cómo integrarlo con el contenedor `Travel`.

## Objetivo
- Entregar los puntos seleccionados al contenedor para que allí se calcule la ruta y se pase al modo de visualización.

## Estructura del modo

```
selection/
├─ PointSelectionMode.tsx          # Vista principal del modo
├─ hooks/
│  ├─ usePointSelection.ts         # Re-export del hook real de selección
│  └─ useGeocoding.ts              # Re-export del hook de geocodificación
├─ components/
│  ├─ AddressInput.tsx             # Input + botón para buscar por dirección
│  ├─ SelectedPointsList.tsx       # Lista de puntos con acción “Quitar”
│  └─ RouteActions.tsx             # Botones Generar Ruta / Limpiar + mensajes
└─ organisms/
   ├─ PointSelectionControls.tsx   # Orquesta los componentes de UI
   └─ PointSelectionMap.tsx        # Selección vía clic y render de puntos
```

## Contrato del modo

- Prop única: `onPointsSelected(selectedPoints: Coordinate[]) => void | Promise<void>`
- Al pulsar “Generar Ruta”, `PointSelectionMode` invoca el callback con los puntos actuales

## Ciclo de interacción

1) Clic en mapa → `onPointClick` → `addPoint(coordinate)`
2) Dirección ingresada → `addPointFromAddress(address)` → geocoding → `addPoint(coordinates)`
3) El usuario puede “Quitar” puntos individuales o “Limpiar” todos
4) Si `selectedPoints.length >= 1`, se habilita “Generar Ruta”
5) Click en “Generar Ruta” → `PointSelectionMode` setea `isGeneratingRoute=true`, llama `await onPointsSelected(selectedPoints)` y luego `isGeneratingRoute=false`

## Hooks y estados clave

- `usePointSelection`
  - Estado: `selectedPoints: Coordinate[]`
  - Acciones: `addPoint`, `removePoint`, `clearPoints`, `addPointFromAddress`

- `useGeocoding`
  - Estado: `isGeocoding`, `error`
  - API: `geocodeAddress(address) => { coordinates, label }`

- `useMap` (compartido)
  - Maneja `initialViewState`, `viewState` y `onViewStateChange`

## UI y comportamiento

- `AddressInput`: deshabilita mientras `isGeocoding` y muestra `error` si ocurre.
- `SelectedPointsList`: muestra lat/lng y permite quitar puntos.
- `RouteActions`:
  - “Generar Ruta” se deshabilita si `!canGenerateRoute` o `isGeneratingRoute`
  - “Limpiar” se deshabilita si no hay puntos
  - Mensajes contextuales (máximo de puntos, agregado de destino final por el contenedor)
- `PointSelectionControls`: contiene los tres componentes anteriores y recibe `isGeneratingRoute` del modo para feedback del botón.
- `PointSelectionMap`: renderiza puntos como `GeoJsonLayer` y emite `onPointClick`.

## Integración con `Travel`

En `travel.tsx`:

```tsx
const handlePointsSelected = async (selectedPoints: Coordinate[]) => {
  const waypoints = [...selectedPoints, UNIVERSITY_COORDINATES];
  const route = await defineRoute(waypoints);
  setRouteCoordinates(route);
  setWaypoints(waypoints);
  setMode('route');
};

return <PointSelectionMode onPointsSelected={handlePointsSelected} />;
```

## Reglas y casos límite

- Máximo de puntos: 5. Si se excede, se reemplaza el último punto.
- `canGenerateRoute = selectedPoints.length >= 1`.
- Geocoding con feedback de carga y error.
- `isGeneratingRoute` es local al modo para bloquear doble envío y mostrar “Generando…”.