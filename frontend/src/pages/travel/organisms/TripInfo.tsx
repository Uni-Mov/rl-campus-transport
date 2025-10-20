interface TripInfoProps {
  isTripStarted: boolean;
  isTripCompleted: boolean;
  currentRouteIndex: number;
  totalRoutePoints: number;
}

export const TripInfo = ({ 
  isTripStarted, 
  isTripCompleted, 
  currentRouteIndex, 
  totalRoutePoints 
}: TripInfoProps) => {
  if (!isTripStarted) return null;

  return (
    <div className="absolute top-4 right-4 z-20 bg-white/90 backdrop-blur-sm rounded-lg p-4 shadow-lg">
      <div className="text-sm text-gray-600">
        <div className="font-semibold text-gray-800 mb-2">
          {isTripCompleted ? "¡Viaje Completado!" : "Estado del Viaje"}
        </div>
        <div>Progreso: {currentRouteIndex + 1} / {totalRoutePoints}</div>
        <div className="w-32 bg-gray-200 rounded-full h-2 mt-2">
          <div 
            className={`h-2 rounded-full transition-all duration-300 ${
              isTripCompleted ? 'bg-blue-600' : 'bg-green-600'
            }`}
            style={{ width: `${((currentRouteIndex + 1) / totalRoutePoints) * 100}%` }}
          ></div>
        </div>
        {isTripCompleted && (
          <div className="mt-2 text-green-600 font-semibold flex items-center gap-1">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            ¡Destino alcanzado!
          </div>
        )}
      </div>
    </div>
  );
};
