import { useMemo } from "react";
import { GeoJsonLayer, ColumnLayer } from "@deck.gl/layers";
import type { FeatureCollection, LineString } from "geojson";

type Coordinate = [number, number];

interface UseRouteProps {
  routeCoordinates: Coordinate[];
  carPosition: Coordinate;
  currentRouteIndex: number;
}

export const useRoute = ({ routeCoordinates, carPosition, currentRouteIndex }: UseRouteProps) => {
  // Crear ruta dinámica que muestra el progreso
  const dynamicRouteGeoJson: FeatureCollection<LineString> = useMemo(() => ({
    type: "FeatureCollection",
    features: [
      {
        type: "Feature",
        geometry: { 
          type: "LineString", 
          coordinates: routeCoordinates.slice(0, currentRouteIndex + 1) 
        },
        properties: {},
      },
    ],
  }), [routeCoordinates, currentRouteIndex]);

  // Ruta completa (gris) para mostrar el camino total
  const fullRouteGeoJson: FeatureCollection<LineString> = useMemo(() => ({
    type: "FeatureCollection",
    features: [
      {
        type: "Feature",
        geometry: { 
          type: "LineString", 
          coordinates: routeCoordinates 
        },
        properties: {},
      },
    ],
  }), [routeCoordinates]);

  const layers = useMemo(() => [
    // Ruta completa en gris
    new GeoJsonLayer({
      id: "full-route",
      data: fullRouteGeoJson,
      stroked: true,
      filled: false,
      lineWidthMinPixels: 3,
      getLineColor: [128, 128, 128], // Gris
      opacity: 0.5,
    }),
    // Ruta recorrida en verde
    new GeoJsonLayer({
      id: "completed-route",
      data: dynamicRouteGeoJson,
      stroked: true,
      filled: false,
      lineWidthMinPixels: 4,
      getLineColor: [29, 185, 84], // Verde
    }),
    // Vehículo 3D - Cuerpo del auto
    new ColumnLayer({
      id: "vehicle-body",
      data: [{ coordinates: carPosition }],
      getPosition: (d) => d.coordinates,
      getElevation: 0,
      getFillColor: [52, 138, 67], // Verde azulado
      radius: 12,
      height: 4,
      pickable: true,
      updateTriggers: {
        getPosition: carPosition,
      },
    }),
    // Vehículo 3D - Ruedas
    new ColumnLayer({
      id: "vehicle-wheels",
      data: [
        { coordinates: [carPosition[0] - 0.0001, carPosition[1] - 0.0001] },
        { coordinates: [carPosition[0] + 0.0001, carPosition[1] - 0.0001] },
        { coordinates: [carPosition[0] - 0.0001, carPosition[1] + 0.0001] },
        { coordinates: [carPosition[0] + 0.0001, carPosition[1] + 0.0001] },
      ],
      getPosition: (d) => d.coordinates,
      getElevation: 0,
      getFillColor: [20, 20, 20], // Negro para las ruedas
      radius: 3,
      height: 2,
      pickable: false,
      updateTriggers: {
        getPosition: carPosition,
      },
    }),
  ], [fullRouteGeoJson, dynamicRouteGeoJson, carPosition]);

  return {
    layers,
    dynamicRouteGeoJson,
    fullRouteGeoJson,
  };
};