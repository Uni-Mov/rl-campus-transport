import { useTrip } from "../hooks/useTrip";
import { useMap } from "../../hooks/useMap";
import { useRoute } from "../hooks/useRoute";
import { TripControls } from "../organisms/TripControls";
import { TripInfo } from "../organisms/TripInfo";
import { MapContainer } from "../organisms/MapContainer";
import type { Coordinate } from "@/types/coordinate";

interface TravelWithRouteProps {
  routeCoordinates: Coordinate[];
  waypoints: Coordinate[];
  onBackToSelection?: () => void;
}

export const TravelWithRoute = ({ 
  routeCoordinates, 
  waypoints,
  onBackToSelection 
}: TravelWithRouteProps) => {
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
    waypoints,
  });

  const handleStartTrip = () => {
    startTrip();
  };

  const handleResetTrip = () => {
    resetTrip();
    resetView();
  };

  return (
    <div className="w-full h-[80vh] max-w-7xl mx-auto relative rounded-lg overflow-hidden shadow">
      <TripControls
        isTripStarted={isTripStarted}
        isTripCompleted={isTripCompleted}
        onStartTrip={handleStartTrip}
        onResetTrip={handleResetTrip}
        onBackToSelection={onBackToSelection}
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
};
