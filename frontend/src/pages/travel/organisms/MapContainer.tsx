import DeckGL from "@deck.gl/react";
import { StaticMap } from "react-map-gl";

interface MapContainerProps {
  initialViewState: any;
  viewState: any;
  onViewStateChange: (params: { viewState: any }) => void;
  layers: any[];
}

export const MapContainer = ({ 
  initialViewState, 
  viewState, 
  onViewStateChange, 
  layers 
}: MapContainerProps) => {
  return (
    <div className="w-full h-full">
      <DeckGL
        initialViewState={initialViewState}
        viewState={viewState}
        onViewStateChange={onViewStateChange}
        controller={true}
        layers={layers}
      >
        <StaticMap
          mapStyle="https://api.maptiler.com/maps/streets-v2/style.json?key=hD8j8L51dExCNzbWSoTr"
        />
      </DeckGL>
    </div>
  );
};
