import type { Coordinate } from "@/types/coordinate";

export const defineRoute = async (points: Coordinate[], useCustomRouter: boolean = false): Promise<Coordinate[]> => {
  try {
    const coordinatesString = points.map(([lng, lat]) => `${lng},${lat}`).join(";");
    
    if (useCustomRouter) {
      // using our own RL engine (POST JSON)
      // points[0] = inicio, points[-1] = fin, points[1:-1] = waypoints
      const body = {
        start_node: points[0],
        end_node: points[points.length - 1],
        waypoints: points.length > 2 ? points.slice(1, -1) : []
      };

      const res = await fetch(`/api/paths/calculate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        throw new Error(`Backend error: ${res.statusText}`);
      }

      const data = await res.json();
      const coordinates = data.route && data.route[0] && data.route[0].coordinates ? data.route[0].coordinates : [];
      return coordinates;
    } else {
      
      // using OSRM
      const res = await fetch(`https://router.project-osrm.org/route/v1/driving/${coordinatesString}?overview=full&geometries=geojson`);
      const data = await res.json();
      const coordinates = data.routes[0].geometry.coordinates;
      return coordinates;
    }
  } catch (err) {
    console.error("Error fetching route:", err);
    return [];
  }
};
  