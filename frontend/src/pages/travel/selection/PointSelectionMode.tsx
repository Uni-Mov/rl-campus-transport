import { useState } from "react";
import { useMap } from "../hooks/useMap";
import { usePointSelection } from "./hooks/usePointSelection";
import { PointSelectionMap } from "./organisms/PointSelectionMap";
import { PointSelectionControls } from "./organisms/PointSelectionControls";
import type { Coordinate } from "@/types/coordinate";

interface PointSelectionModeProps {
  // Finaliza la selección y devuelve los puntos elegidos
  onPointsSelected: (selectedPoints: Coordinate[]) => void | Promise<void>;
}

export const PointSelectionMode = ({ onPointsSelected }: PointSelectionModeProps) => {
  const [isGeneratingRoute, setIsGeneratingRoute] = useState(false);
  const { viewState, setViewState, initialViewState } = useMap({
    initialLongitude: -64.3051,
    initialLatitude: -33.1208,
    initialZoom: 12,
  });

  const {
    selectedPoints,
    addPoint,
    removePoint,
    clearPoints,
    addPointFromAddress,
    isGeocoding,
    geocodingError,
    canGenerateRoute,
    maxPoints,
  } = usePointSelection({ maxPoints: 5 });

  const handleFinishSelection = async () => {
    try {
      setIsGeneratingRoute(true);
      await onPointsSelected(selectedPoints);
    } finally {
      setIsGeneratingRoute(false);
    }
  };

  const handleAddPointFromAddress = async (address: string) => {
    try {
      await addPointFromAddress(address);
    } catch (error) {
      console.error("Error al agregar punto desde dirección:", error);
    }
  };

  return (
    <div className="w-full h-[80vh] max-w-7xl mx-auto relative rounded-lg overflow-hidden shadow">
      <PointSelectionControls
        selectedPoints={selectedPoints}
        canGenerateRoute={canGenerateRoute}
        isGeneratingRoute={isGeneratingRoute}
        maxPoints={maxPoints}
        onGenerateRoute={handleFinishSelection}
        onClearPoints={clearPoints}
        onRemovePoint={removePoint}
        onAddPointFromAddress={handleAddPointFromAddress}
        isGeocoding={isGeocoding}
        geocodingError={geocodingError}
      />

      <PointSelectionMap
        initialViewState={initialViewState}
        viewState={viewState}
        onViewStateChange={({ viewState: newViewState }) => setViewState(newViewState as any)}
        selectedPoints={selectedPoints}
        onPointClick={addPoint}
      />
    </div>
  );
};
