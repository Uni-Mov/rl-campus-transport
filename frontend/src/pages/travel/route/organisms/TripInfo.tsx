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

  const percent = Math.min(100, Math.max(0, ((currentRouteIndex + 1) / totalRoutePoints) * 100));

  return (
    <div className="absolute top-2 left-2 sm:top-4 sm:left-4 z-10 pointer-events-none">
      <div className="bg-white/80 backdrop-blur-sm border border-gray-200/60 rounded-md px-2 sm:px-3 py-1.5 sm:py-2 shadow-sm text-[10px] sm:text-xs text-gray-700">
        <div className="flex items-center gap-2">
          <span className="font-medium">Progreso</span>
          <span className="text-gray-500">{currentRouteIndex + 1}/{totalRoutePoints}</span>
        </div>
        <div className="w-24 sm:w-28 bg-gray-200 rounded-full h-1 sm:h-1.5 mt-1 sm:mt-1.5">
          <div 
            className={`h-1 sm:h-1.5 rounded-full transition-all duration-300 ${
              isTripCompleted ? 'bg-blue-600' : 'bg-green-600'
            }`}
            style={{ width: `${percent}%` }}
          />
        </div>
        {isTripCompleted && (
          <div className="mt-1 text-[10px] sm:text-[11px] text-green-600 font-medium flex items-center gap-1">
            <svg className="w-3 sm:w-3.5 h-3 sm:h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            Destino alcanzado
          </div>
        )}
      </div>
    </div>
  );
};
