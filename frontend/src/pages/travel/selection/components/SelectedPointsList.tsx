import type { Coordinate } from "@/types/coordinate";

interface SelectedPointsListProps {
  selectedPoints: Coordinate[];
  onRemovePoint: (index: number) => void;
}

export const SelectedPointsList = ({ selectedPoints, onRemovePoint }: SelectedPointsListProps) => {
  return (
    <div className="space-y-2 mb-3">
      {selectedPoints.length === 0 ? (
        <p className="text-sm text-gray-500">Aún no hay puntos seleccionados</p>
      ) : (
        selectedPoints.map((point, index) => (
          <div key={index} className="flex items-center justify-between bg-gray-50 p-2 rounded">
            <span className="text-sm text-gray-700">
              Punto {index + 1}: {point[1].toFixed(5)}, {point[0].toFixed(5)}
            </span>
            <button
              onClick={() => onRemovePoint(index)}
              className="text-red-600 hover:text-red-700 text-sm"
            >
              Quitar
            </button>
          </div>
        ))
      )}
    </div>
  );
};

