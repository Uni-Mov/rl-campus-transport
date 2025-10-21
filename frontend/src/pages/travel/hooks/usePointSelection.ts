import { useState, useCallback } from "react";
import type { Coordinate } from "@/types/coordinate";
import { useGeocoding } from "./useGeocoding";

interface UsePointSelectionProps {
  maxPoints?: number;
}

export const usePointSelection = ({ maxPoints = 5 }: UsePointSelectionProps = {}) => {
  const [selectedPoints, setSelectedPoints] = useState<Coordinate[]>([]);
  const { geocodeAddress, isGeocoding, error: geocodingError, clearError } = useGeocoding();

  const addPoint = useCallback((coordinate: Coordinate) => {
    setSelectedPoints(prev => {
      if (prev.length >= maxPoints) {
        const newPoints = [...prev];
        newPoints[newPoints.length - 1] = coordinate;
        return newPoints;
      }
      return [...prev, coordinate];
    });
  }, [maxPoints]);

  const removePoint = useCallback((index: number) => {
    setSelectedPoints(prev => prev.filter((_, i) => i !== index));
  }, []);

  const clearPoints = useCallback(() => {
    setSelectedPoints([]);
  }, []);

  const addPointFromAddress = useCallback(async (address: string) => {
    try {
      clearError();
      const result = await geocodeAddress(address);
      addPoint(result.coordinates);
    } catch (error) {
      console.error("Error al geocodificar la dirección:", error);
      throw error;
    }
  }, [geocodeAddress, addPoint, clearError]);

  const canGenerateRoute = selectedPoints.length >= 1;
  const canAddMorePoints = selectedPoints.length < maxPoints;

  return {
    selectedPoints,
    addPoint,
    removePoint,
    clearPoints,
    addPointFromAddress,
    isGeocoding,
    geocodingError,
    canGenerateRoute,
    canAddMorePoints,
    maxPoints,
  };
};
