interface TripControlsProps {
  isTripStarted: boolean;
  isTripCompleted: boolean;
  onStartTrip: () => void;
  onResetTrip: () => void;
  onBackToSelection?: () => void;
}

export const TripControls = ({
  isTripStarted,
  isTripCompleted,
  onStartTrip,
  onResetTrip,
  onBackToSelection,
}: TripControlsProps) => {
  return (
    <div className="absolute top-4 right-4 z-10 bg-white rounded-lg shadow-lg p-4">
      <div className="flex space-x-2">
        {!isTripStarted && (
          <button
            onClick={onStartTrip}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md text-sm font-medium"
          >
            Iniciar viaje
          </button>
        )}
        <button
          onClick={onResetTrip}
          className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-md text-sm font-medium"
        >
          Reiniciar
        </button>
        {onBackToSelection && (
          <button
            onClick={onBackToSelection}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium"
          >
            Volver a selección
          </button>
        )}
      </div>
      {isTripCompleted && (
        <p className="mt-2 text-xs text-gray-500">Viaje completado</p>
      )}
    </div>
  );
};

