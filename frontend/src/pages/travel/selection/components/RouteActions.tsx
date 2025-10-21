interface RouteActionsProps {
  canGenerateRoute: boolean;
  isGeneratingRoute: boolean;
  selectedPointsCount: number;
  maxPoints: number;
  onGenerateRoute: () => void;
  onClearPoints: () => void;
}

export const RouteActions = ({
  canGenerateRoute,
  isGeneratingRoute,
  selectedPointsCount,
  maxPoints,
  onGenerateRoute,
  onClearPoints,
}: RouteActionsProps) => {
  return (
    <>
      {/* Controles */}
      <div className="flex space-x-2">
        <button
          onClick={onGenerateRoute}
          disabled={!canGenerateRoute || isGeneratingRoute}
          className={`
            flex-1 px-4 py-2 rounded-md font-medium text-sm transition-colors
            ${canGenerateRoute && !isGeneratingRoute
              ? 'bg-blue-600 hover:bg-blue-700 text-white'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }
          `}
        >
          {isGeneratingRoute ? 'Generando...' : 'Generar Ruta'}
        </button>
        
        <button
          onClick={onClearPoints}
          disabled={selectedPointsCount === 0}
          className={`
            px-4 py-2 rounded-md font-medium text-sm transition-colors
            ${selectedPointsCount > 0
              ? 'bg-red-600 hover:bg-red-700 text-white'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }
          `}
        >
          Limpiar
        </button>
      </div>
      
      {/* Información adicional */}
      <div className="mt-3 text-xs text-gray-500">
        {selectedPointsCount < 1 && (
          <p>Selecciona al menos 1 punto para generar una ruta</p>
        )}
        {selectedPointsCount >= 1 && selectedPointsCount < maxPoints && (
          <p>La Universidad de Río Cuarto se agregará automáticamente como destino final</p>
        )}
        {selectedPointsCount === maxPoints && (
          <p>Máximo de puntos alcanzado. Haz clic en un punto existente para reemplazarlo.</p>
        )}
      </div>
    </>
  );
};

