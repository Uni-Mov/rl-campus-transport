import { useTrip } from "./hooks/useTrip";
import { useMap } from "./hooks/useMap";
import { useRoute } from "./hooks/useRoute";
import { defineRoute } from "./hooks/defineRoute";
import { TripControls } from "./organisms/TripControls";
import { TripInfo } from "./organisms/TripInfo";
import { MapContainer } from "./organisms/MapContainer";


export default function Travel() {
  const routeCoordinates = defineRoute();
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