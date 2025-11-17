import { useState } from "react";
import { useAuth } from "@/context/auth-context";
import { useRouter } from "@/context/router-context";
import { PointSelectionMode } from "./selection/PointSelectionMode";
import { TravelWithRoute } from "./route/components/TravelWithRoute";
import { defineRoute } from "./route/services/defineRoute";
import { UNIVERSITY_COORDINATES } from "./constants";
import type { Coordinate } from "@/types/coordinate";
import Sidebar from "./organisms/sidebar";
import { useNavigate } from "react-router-dom";


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
  const navigate = useNavigate();
  const { useCustomRouter } = useRouter();

  // manejadores de eventos para la coordinación entre los modos
  const handlePointsSelected = async (selectedPoints: Coordinate[]) => {
    // completa los waypoints agregando la universidad como destino
    const waypointsWithUniversity = [...selectedPoints, UNIVERSITY_COORDINATES];
    // calcula la ruta usando el util compartido (con opción de usar el motor personalizado)
    const route = await defineRoute(waypointsWithUniversity, useCustomRouter);
    setRouteCoordinates(route);
    setWaypoints(waypointsWithUniversity);
    setMode('route');
  };

  const handleBackToSelection = () => {
    setMode('selection');
    setRouteCoordinates([]);
    setWaypoints([]);
  };

  if (useAuth().isLoggedIn) {
    return (
      <div className="flex h-screen overflow-hidden overscroll-none">
        <Sidebar />
        <main className="flex-1 overflow-hidden flex flex-col lg:ml-0 overscroll-none">
          {isLoading ? (
            <div className="flex-1 flex items-center justify-center p-4 sm:p-6">
              <div className="text-base sm:text-lg">Cargando ruta...</div>
            </div>
          ) : mode === 'route' && routeCoordinates.length > 0 ? (
            <div className="flex-1 min-h-0 relative">
              <TravelWithRoute 
                routeCoordinates={routeCoordinates} 
                waypoints={waypoints} 
                onBackToSelection={handleBackToSelection} 
              />
            </div>
          ) : (
            <div className="flex-1 min-h-0 relative">
              <PointSelectionMode onPointsSelected={handlePointsSelected} />
            </div>
          )}
        </main>
      </div>
    );
  } else {
    navigate("/login");
  }

}
