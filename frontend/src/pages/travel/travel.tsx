import { useState } from "react";
import { PointSelectionMode } from "./selection/PointSelectionMode";
import { TravelWithRoute } from "./route/components/TravelWithRoute";
import { defineRoute } from "./route/services/defineRoute";
import { UNIVERSITY_COORDINATES } from "./constants";
import type { Coordinate } from "@/types/coordinate";


// Estados posibles de la aplicación
type TravelMode = 'selection' | 'route';

/**
 * componente principal que maneja el estado global de la aplicación de viajes.
 * Su única responsabilidad es coordinar entre los dos modos principales:
 * - modo selección: Para seleccionar puntos y generar rutas
 * - modo ruta: Para visualizar y simular el viaje
 */
export default function Travel() {
  const [routeCoordinates, setRouteCoordinates] = useState<Coordinate[]>([]);
  const [waypoints, setWaypoints] = useState<Coordinate[]>([]);
  const [isLoading] = useState(false);
  const [mode, setMode] = useState<TravelMode>('selection');

  // manejadores de eventos para la coordinación entre los modos
  const handlePointsSelected = async (selectedPoints: Coordinate[]) => {
    // completa los waypoints agregando la universidad como destino
    const waypointsWithUniversity = [...selectedPoints, UNIVERSITY_COORDINATES];
    // calcula la ruta usando el util compartido
    const route = await defineRoute(waypointsWithUniversity);
    setRouteCoordinates(route);
    setWaypoints(waypointsWithUniversity);
    setMode('route');
  };

  const handleBackToSelection = () => {
    setMode('selection');
    setRouteCoordinates([]);
    setWaypoints([]);
  };

  // renderizado condicional basado en el modo actual
  if (isLoading) {
    return (
      <div className="w-full h-screen flex items-center justify-center">
        <div className="text-lg">Cargando ruta...</div>
      </div>
    );
  }

  if (mode === 'route' && routeCoordinates.length > 0) {
    return (
      <TravelWithRoute 
        routeCoordinates={routeCoordinates} 
        waypoints={waypoints} 
        onBackToSelection={handleBackToSelection} 
      />
    );
  }

  return <PointSelectionMode onPointsSelected={handlePointsSelected} />;
}
