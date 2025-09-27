import { useState } from "react";

type Coordinate = [number, number];

interface UseMapProps {
  initialLongitude: number;
  initialLatitude: number;
  initialZoom: number;
}

export const useMap = ({ initialLongitude, initialLatitude, initialZoom }: UseMapProps) => {
  const [viewState, setViewState] = useState({
    longitude: initialLongitude,
    latitude: initialLatitude,
    zoom: initialZoom,
    pitch: 0,
    bearing: 0,
  });
    // set initial map state
  const initialViewState = {
    longitude: initialLongitude,
    latitude: initialLatitude,
    zoom: initialZoom,
    pitch: 0,
    bearing: 0,
  };
    // set map position to the passed coordinates, useful when moving the car
  const centerOnPosition = (coordinates: Coordinate) => {
    setViewState(prev => ({
      ...prev,
      longitude: coordinates[0],
      latitude: coordinates[1],
    }));
  };
    // reset map state to initial state
  const resetView = () => {
    setViewState({
      longitude: initialLongitude,
      latitude: initialLatitude,
      zoom: initialZoom,
      pitch: 0,
      bearing: 0,
    });
  };
    // return map state, function to center map on a position and function to reset map state 
  return {
    viewState,
    setViewState,
    initialViewState,
    centerOnPosition,
    resetView,
  };
};
