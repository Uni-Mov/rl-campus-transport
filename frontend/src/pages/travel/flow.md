# Travel Component - Flujo Completo

## Arquitectura

El componente Travel está organizado en una estructura modular que separa responsabilidades:

```
travel/
├── travel.tsx      
├── hooks/
│   ├── useTrip.ts         # Lógica del viaje
│   ├── useMap.ts          # Lógica del mapa
│   ├── useRoute.ts        # Lógica de rutas y capas
│   └── defineRoute.ts     # Coordenadas de la ruta
└── organisms/
    ├── TripControls.tsx   # Controles del viaje
    ├── TripInfo.tsx       # Información del viaje
    └── MapContainer.tsx   # Contenedor del mapa
```

## Flujo de Datos

### 1. **Inicialización**
```typescript
// travel.tsx
const routeCoordinates = defineRoute();  // Obtiene coordenadas de la ruta

// useMap - Estado inicial del mapa
const { viewState, setViewState, initialViewState, centerOnPosition, resetView } = useMap({
  initialLongitude: routeCoordinates[0][0],
  initialLatitude: routeCoordinates[0][1],
  initialZoom: 12,
});

// useTrip - Estado inicial del viaje
const { carPosition, isTripStarted, isTripCompleted, currentRouteIndex, startTrip, resetTrip } = useTrip({
  routeCoordinates,
  onTripUpdate: centerOnPosition,  // Callback para centrar mapa
});

// useRoute - Capas del mapa
const { layers } = useRoute({
  routeCoordinates,
  carPosition,
  currentRouteIndex,
});
```

### 2. **Inicio del Viaje**
```typescript
const handleStartTrip = () => {
  startTrip();  // useTrip.startTrip()
  // El callback onTripUpdate se ejecuta automáticamente
};
```

**Flujo interno de `startTrip()`:**
1. `setIsTripStarted(true)` - Activa el viaje
2. `setIsTripCompleted(false)` - Resetea estado completado
3. `setCurrentRouteIndex(0)` - Vuelve al inicio
4. `setCarPosition(routeCoordinates[0])` - Posiciona vehículo
5. `routeIndexRef.current = 0` - Resetea índice interno

### 3. **Movimiento del Vehículo (Cada 3 segundos)**

**En `useTrip.ts`:**
```typescript
useEffect(() => {
  const interval = setInterval(() => {
    if (isTripStarted && routeIndexRef.current < routeCoordinates.length - 1) {
      // 1. Avanzar al siguiente punto
      routeIndexRef.current++;
      
      // 2. Actualizar estados
      setCurrentRouteIndex(routeIndexRef.current);
      setCarPosition(routeCoordinates[routeIndexRef.current]);
      
      // 3. Notificar al mapa (callback)
      onTripUpdate?.(routeCoordinates[routeIndexRef.current], routeIndexRef.current);
      
      // 4. Verificar si llegó al destino
      if (routeIndexRef.current === routeCoordinates.length - 1) {
        setIsTripCompleted(true);
      }
    }
  }, 3000);
  
  return () => clearInterval(interval);
}, [isTripStarted, routeCoordinates, onTripUpdate]);
```

### 4. **Actualización del Mapa**

**Cuando se ejecuta `onTripUpdate` (que es `centerOnPosition`):**

**En `useMap.ts`:**
```typescript
const centerOnPosition = (coordinates: Coordinate) => {
  setViewState(prev => ({
    ...prev,
    longitude: coordinates[0],  // Nueva longitud
    latitude: coordinates[1],   // Nueva latitud
  }));
};
```

### 5. **Actualización de Capas**

**En `useRoute.ts`:**
```typescript
// useMemo se ejecuta porque carPosition cambió
const layers = useMemo(() => [
  // Ruta completa (gris)
  new GeoJsonLayer({ data: fullRouteGeoJson, ... }),
  
  // Ruta recorrida (verde) - SE ACTUALIZA
  new GeoJsonLayer({ 
    data: dynamicRouteGeoJson,  // Nuevas coordenadas
    getLineColor: [29, 185, 84] 
  }),
  
  // Vehículo 3D - SE ACTUALIZA
  new ColumnLayer({
    data: [{ coordinates: carPosition }],  // Nueva posición
    getFillColor: [52, 138, 67]
  }),
], [fullRouteGeoJson, dynamicRouteGeoJson, carPosition]);
```

### 6. **Re-renderizado del Mapa**

**En `MapContainer.tsx`:**
```typescript
<DeckGL
  viewState={viewState}        // ← Vista actualizada
  layers={layers}             // ← Capas actualizadas
  onViewStateChange={...}
>
  <StaticMap />
</DeckGL>
```

## Flujo Completo Resumido

1. **Timer** (cada 3s) → **useTrip** mueve vehículo
2. **useTrip** → **useMap** (centra vista via callback)
3. **useTrip** → **useRoute** (actualiza capas via props)
4. **useMap** + **useRoute** → **MapContainer**
5. **MapContainer** → **DeckGL** → **Mapa actualizado**

## Componentes UI

### **TripControls**
- Botones: "Iniciar Viaje", "Reiniciar", "Nuevo Viaje"
- Estados condicionales según `isTripStarted` e `isTripCompleted`

### **TripInfo**
- Panel de progreso del viaje
- Barra de progreso visual
- Mensaje de destino alcanzado
- Solo visible cuando `isTripStarted = true`

### **MapContainer**
- Encapsula DeckGL y StaticMap
- Maneja configuración del mapa

## Optimizaciones

### **useMemo en useRoute**
```typescript
const layers = useMemo(() => [...], [fullRouteGeoJson, dynamicRouteGeoJson, carPosition]);
```
- Evita recálculos innecesarios de capas
- Solo se actualiza cuando cambian las dependencias
- Directamente se bugea todo si no esta

### **useCallback en useTrip**
```typescript
const onTripUpdate = useCallback((position, index) => {
  centerOnPosition(position);
}, [centerOnPosition]);
```
- Evita re-renders innecesarios
- Mantiene referencias estables
