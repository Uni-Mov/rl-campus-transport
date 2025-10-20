interface TripControlsProps {
  isTripStarted: boolean;
  isTripCompleted: boolean;
  onStartTrip: () => void;
  onResetTrip: () => void;
}

export const TripControls = ({ 
  isTripStarted, 
  isTripCompleted, 
  onStartTrip, 
  onResetTrip 
}: TripControlsProps) => {
  return (
    <div className="absolute top-4 left-4 z-20 flex gap-3">
      {!isTripStarted ? (
        <button
          onClick={onStartTrip}
          className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-semibold shadow-lg transition-colors duration-200 flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Iniciar Viaje
        </button>
      ) : isTripCompleted ? (
        <button
          onClick={onResetTrip}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold shadow-lg transition-colors duration-200 flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Nuevo Viaje
        </button>
      ) : (
        <button
          onClick={onResetTrip}
          className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg font-semibold shadow-lg transition-colors duration-200 flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Reiniciar
        </button>
      )}
    </div>
  );
};
