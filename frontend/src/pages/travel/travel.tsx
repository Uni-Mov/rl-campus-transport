import { useTrip } from "./hooks/useTrip";
import { useMap } from "./hooks/useMap";
import { useRoute } from "./hooks/useRoute";
import { defineRoute } from "./hooks/defineRoute";
import { TripControls } from "./organisms/TripControls";
import { TripInfo } from "./organisms/TripInfo";
import { MapContainer } from "./organisms/MapContainer";
import { useEffect, useState } from "react";
import type { Coordinate } from "@/types/coordinate";


// Componente que maneja los hooks - solo se renderiza cuando hay coordenadas
function TravelWithRoute({ routeCoordinates }: { routeCoordinates: Coordinate[] }) {
  // seteo el estado inicial del mapa
  const { viewState, setViewState, initialViewState, centerOnPosition, resetView } = useMap({
    initialLongitude: routeCoordinates[0][0],
    initialLatitude: routeCoordinates[0][1],
    initialZoom: 12,
  });
  
  // seteo el estado inicial del viaje
  const { 
    carPosition, 
    isTripStarted, 
    isTripCompleted, 
    currentRouteIndex, 
    startTrip, 
    resetTrip 
  } = useTrip({
    routeCoordinates,
    onTripUpdate: centerOnPosition,
  });
  
  // seteo el estado inicial de la ruta/lineas de la ruta
  const { layers } = useRoute({
    routeCoordinates,
    carPosition,
    currentRouteIndex,
  });

  const handleStartTrip = () => {
    startTrip();
  };

  const handleResetTrip = () => {
    resetTrip();
    resetView();
  };

  return (
    <div className="w-full h-screen relative">
      <TripControls
        isTripStarted={isTripStarted}
        isTripCompleted={isTripCompleted}
        onStartTrip={handleStartTrip}
        onResetTrip={handleResetTrip}
      />

      <TripInfo
        isTripStarted={isTripStarted}
        isTripCompleted={isTripCompleted}
        currentRouteIndex={currentRouteIndex}
        totalRoutePoints={routeCoordinates.length}
      />

      <MapContainer
        initialViewState={initialViewState}
        viewState={viewState}
        onViewStateChange={({ viewState: newViewState }) => setViewState(newViewState as any)}
        layers={layers}
      />
    </div>
  );
}

// Componente principal que solo maneja la carga de datos
export default function Travel() {
  const [routeCoordinates, setRouteCoordinates] = useState<Coordinate[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    defineRoute().then(coords => {
      setRouteCoordinates(coords);
      setIsLoading(false);
    });
  }, []);

  // Mostrar loading mientras se cargan las coordenadas
  if (isLoading || routeCoordinates.length === 0) {
    return (
      <div className="w-full h-screen flex items-center justify-center">
        <div className="text-lg">Cargando ruta...</div>
      </div>
    );
  }

  // Solo renderizar el componente con hooks cuando las coordenadas estén listas
  return <TravelWithRoute routeCoordinates={routeCoordinates} />;
}