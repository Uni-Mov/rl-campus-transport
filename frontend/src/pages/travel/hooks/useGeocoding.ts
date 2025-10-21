import { useState, useCallback } from "react";
import type { Coordinate } from "@/types/coordinate";

interface GeocodingResult {
  address: string;
  coordinates: Coordinate;
  formattedAddress: string;
}

interface UseGeocodingProps {
  apiKey?: string;
}

export const useGeocoding = ({} : UseGeocodingProps = {}) => {
  const [isGeocoding, setIsGeocoding] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const geocodeAddress = useCallback(async (address: string): Promise<GeocodingResult> => {
    if (!address.trim()) {
      throw new Error("La dirección no puede estar vacía");
    }

    setIsGeocoding(true);
    setError(null);

    try {
      const encodedAddress = encodeURIComponent(address);
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodedAddress}&limit=1&addressdetails=1`
      );

      if (!response.ok) {
        throw new Error(`Error en la respuesta del servidor: ${response.status}`);
      }

      const data = await response.json();

      if (!data || data.length === 0) {
        throw new Error("No se encontró la dirección especificada");
      }

      const result = data[0];
      const coordinates: Coordinate = [parseFloat(result.lon), parseFloat(result.lat)];
      
      return {
        address: address,
        coordinates,
        formattedAddress: result.display_name,
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Error desconocido al buscar la dirección";
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsGeocoding(false);
    }
  }, []);

  // funcion para geocoding inverso (coordenadas a dirección)
  const reverseGeocode = useCallback(async (coordinates: Coordinate): Promise<string> => {
    setIsGeocoding(true);
    setError(null);

    try {
      const [lon, lat] = coordinates;
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&addressdetails=1`
      );

      if (!response.ok) {
        throw new Error(`Error en la respuesta del servidor: ${response.status}`);
      }

      const data = await response.json();

      if (!data || !data.display_name) {
        throw new Error("No se pudo obtener la dirección para estas coordenadas");
      }

      return data.display_name;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Error desconocido al obtener la dirección";
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsGeocoding(false);
    }
  }, []);

  return {
    geocodeAddress,
    reverseGeocode,
    isGeocoding,
    error,
    clearError: () => setError(null),
  };
};
