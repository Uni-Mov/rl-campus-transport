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
    <div className="absolute top-2 right-2 sm:top-4 sm:right-4 z-10 bg-white rounded-lg shadow-lg p-2 sm:p-4">
      <div className="flex flex-wrap gap-2">
        {!isTripStarted && (
          <button
            onClick={onStartTrip}
            className="px-3 sm:px-4 py-1.5 sm:py-2 bg-green-600 hover:bg-green-700 text-white rounded-md text-xs sm:text-sm font-medium whitespace-nowrap"
          >
            Iniciar viaje
          </button>
        )}
        <button
          onClick={onResetTrip}
          className="px-3 sm:px-4 py-1.5 sm:py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-md text-xs sm:text-sm font-medium whitespace-nowrap"
        >
          Reiniciar
        </button>
        {onBackToSelection && (
          <button
            onClick={onBackToSelection}
            className="px-3 sm:px-4 py-1.5 sm:py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-xs sm:text-sm font-medium whitespace-nowrap"
          >
            <span className="hidden sm:inline">Volver a selección</span>
            <span className="sm:hidden">Volver</span>
          </button>
        )}
      </div>
      {isTripCompleted && (
        <p className="mt-2 text-xs text-gray-500">Viaje completado</p>
      )}
    </div>
  );
};

