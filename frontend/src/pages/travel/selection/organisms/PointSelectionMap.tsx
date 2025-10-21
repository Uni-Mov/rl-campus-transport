import DeckGL from "@deck.gl/react";
import { StaticMap } from "react-map-gl";
import { GeoJsonLayer } from "@deck.gl/layers";
import { useMemo } from "react";
import type { Coordinate } from "@/types/coordinate";

interface PointSelectionMapProps {
  initialViewState: any;
  viewState: any;
  onViewStateChange: (params: { viewState: any }) => void;
  selectedPoints: Coordinate[];
  onPointClick: (coordinate: Coordinate) => void;
}

export const PointSelectionMap = ({ 
  initialViewState, 
  viewState, 
  onViewStateChange,
  selectedPoints,
  onPointClick
}: PointSelectionMapProps) => {
  
  // crear capas para mostrar los puntos seleccionados
  const layers = useMemo(() => {
    const pointLayers = [] as any[];
    
    // capa para mostrar los puntos seleccionados
    if (selectedPoints.length > 0) {
      const pointsGeoJson = {
        type: "FeatureCollection" as const,
        features: selectedPoints.map((point, index) => ({
          type: "Feature" as const,
          geometry: {
            type: "Point" as const,
            coordinates: point,
          },
          properties: {
            index: index + 1,
          },
        })),
      };

      pointLayers.push(
        new GeoJsonLayer({
          id: "selected-points",
          data: pointsGeoJson,
          pointRadiusMinPixels: 8,
          pointRadiusMaxPixels: 12,
          getFillColor: [255, 0, 0], // rojo para los puntos seleccionados
          getLineColor: [255, 255, 255], // borde blanco
          lineWidthMinPixels: 2,
          pickable: true,
          onClick: (info: any) => {
            if (info.object) {
              // permitir eliminar puntos haciendo click en ellos
              console.log("Punto clickeado:", info.object.properties.index);
            }
          },
        })
      );
    }

    return pointLayers;
  }, [selectedPoints]);

  // manejar clicks en el mapa
  const handleClick = (info: any) => {
    if (info.coordinate) {
      onPointClick([info.coordinate[0], info.coordinate[1]]);
    }
  };

  return (
    <div className="w-full h-full">
      <DeckGL
        initialViewState={initialViewState}
        viewState={viewState}
        onViewStateChange={onViewStateChange}
        controller={true}
        layers={layers}
        onClick={handleClick}
      >
        <StaticMap
          mapStyle="https://api.maptiler.com/maps/streets-v2/style.json?key=hD8j8L51dExCNzbWSoTr"
        />
      </DeckGL>
    </div>
  );
};

