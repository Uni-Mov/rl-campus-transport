import { useState, useEffect, useRef } from "react";

type Coordinate = [number, number];

interface UseTripProps {
  routeCoordinates: Coordinate[];
  onTripUpdate?: (position: Coordinate, index: number) => void;
}

export const useTrip = ({ routeCoordinates, onTripUpdate }: UseTripProps) => {
  const [carPosition, setCarPosition] = useState<Coordinate>(routeCoordinates[0]);
  const [isTripStarted, setIsTripStarted] = useState(false);
  const [isTripCompleted, setIsTripCompleted] = useState(false);
  const [currentRouteIndex, setCurrentRouteIndex] = useState(0);
  const routeIndexRef = useRef(0);

  useEffect(() => {
    // se encarga de actualizar la posición del auto cada 3 segundos
    const interval = setInterval(() => {
      if (isTripStarted && routeIndexRef.current < routeCoordinates.length - 1) {
        routeIndexRef.current++;
        setCurrentRouteIndex(routeIndexRef.current);
        setCarPosition(routeCoordinates[routeIndexRef.current]);
        
        // Callback para notificar cambios
        onTripUpdate?.(routeCoordinates[routeIndexRef.current], routeIndexRef.current);
        
        // Verificar si llegó al destino
        if (routeIndexRef.current === routeCoordinates.length - 1) {
          setIsTripCompleted(true);
        }
      }
    }, 300); 
    
    return () => clearInterval(interval);
  }, [isTripStarted, routeCoordinates, onTripUpdate]);

  const startTrip = () => {
    setIsTripStarted(true);
    setIsTripCompleted(false);
    setCurrentRouteIndex(0);
    setCarPosition(routeCoordinates[0]);
    routeIndexRef.current = 0;
  };

  const resetTrip = () => {
    setIsTripStarted(false);
    setIsTripCompleted(false);
    setCurrentRouteIndex(0);
    setCarPosition(routeCoordinates[0]);
    routeIndexRef.current = 0;
  };

  return {
    carPosition,
    isTripStarted,
    isTripCompleted,
    currentRouteIndex,
    startTrip,
    resetTrip,
  };
};
