import { useMemo } from "react";
import { GeoJsonLayer, ColumnLayer } from "@deck.gl/layers";
import type { FeatureCollection, LineString } from "geojson";

type Coordinate = [number, number];

interface UseRouteProps {
  routeCoordinates: Coordinate[];
  carPosition: Coordinate;
  currentRouteIndex: number;
  waypoints?: Coordinate[]; // Puntos de origen y destino
}

export const useRoute = ({ routeCoordinates, carPosition, currentRouteIndex, waypoints }: UseRouteProps) => {
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

  // Crear GeoJSON para los waypoints (puntos de origen y destino)
  const waypointsGeoJson: FeatureCollection = useMemo(() => ({
    type: "FeatureCollection",
    features: waypoints?.map((point, index) => ({
      type: "Feature",
      geometry: {
        type: "Point",
        coordinates: point,
      },
      properties: {
        index: index + 1,
        isStart: index === 0,
        isEnd: index === waypoints.length - 1,
      },
    })) || [],
  }), [waypoints]);

  const layers = useMemo(() => [
    // Waypoints (puntos de origen y destino)
    ...(waypoints && waypoints.length > 0 ? [
      new GeoJsonLayer({
        id: "waypoints",
        data: waypointsGeoJson,
        pointRadiusMinPixels: 10,
        pointRadiusMaxPixels: 15,
        getFillColor: (d) => {
          const props = d.properties;
          if (props.isStart) return [0, 255, 0]; // Verde para inicio
          if (props.isEnd) return [255, 0, 0]; // Rojo para destino
          return [255, 255, 0]; // Amarillo para puntos intermedios
        },
        getLineColor: [255, 255, 255], // Borde blanco
        lineWidthMinPixels: 2,
        pickable: true,
      })
    ] : []),
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
  ], [waypoints, waypointsGeoJson, fullRouteGeoJson, dynamicRouteGeoJson, carPosition]);

  return {
    layers,
    dynamicRouteGeoJson,
    fullRouteGeoJson,
  };
};