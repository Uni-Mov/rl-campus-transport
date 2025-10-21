import { AddressInput } from "../components/AddressInput";
import { SelectedPointsList } from "../components/SelectedPointsList";
import { RouteActions } from "../components/RouteActions";
import type { Coordinate } from "@/types/coordinate";

interface PointSelectionControlsProps {
  selectedPoints: Coordinate[];
  canGenerateRoute: boolean;
  isGeneratingRoute: boolean;
  maxPoints: number;
  onGenerateRoute: () => void;
  onClearPoints: () => void;
  onRemovePoint: (index: number) => void;
  onAddPointFromAddress: (address: string) => void;
  isGeocoding: boolean;
  geocodingError: string | null;
}

/**
 * componente de controles para la selección de puntos de ruta.
 * coordina los diferentes componentes de entrada y acciones.
 */
export const PointSelectionControls = ({
  selectedPoints,
  canGenerateRoute,
  isGeneratingRoute,
  maxPoints,
  onGenerateRoute,
  onClearPoints,
  onRemovePoint,
  onAddPointFromAddress,
  isGeocoding,
  geocodingError,
}: PointSelectionControlsProps) => {
  return (
    <div className="absolute top-4 left-4 z-10 bg-white rounded-lg shadow-lg p-4 min-w-[300px]">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">
          Seleccionar Puntos de Ruta
        </h3>
        <p className="text-sm text-gray-600 mb-3">
          Haz clic en el mapa para seleccionar hasta {maxPoints} puntos para tu ruta.
        </p>
        
        {/* campo para ingresar direcciones */}
        <AddressInput
          onAddPoint={onAddPointFromAddress}
          isGeocoding={isGeocoding}
          error={geocodingError}
        />
        
          {/* lista de puntos seleccionados */}
        <SelectedPointsList
          selectedPoints={selectedPoints}
          onRemovePoint={onRemovePoint}
        />
      </div>
      
      {/* controles de acción */}
      <RouteActions
        canGenerateRoute={canGenerateRoute}
        isGeneratingRoute={isGeneratingRoute}
        selectedPointsCount={selectedPoints.length}
        maxPoints={maxPoints}
        onGenerateRoute={onGenerateRoute}
        onClearPoints={onClearPoints}
      />
    </div>
  );
};

