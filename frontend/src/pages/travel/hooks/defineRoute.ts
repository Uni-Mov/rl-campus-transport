import type { Coordinate } from "@/types/coordinate";

export const defineRoute = async (points: Coordinate[]): Promise<Coordinate[]> => {
try {
   const coordinatesString = points.map(([lng, lat]) => `${lng},${lat}`).join(";");
  const res = await fetch(`https://router.project-osrm.org/route/v1/driving/${coordinatesString}?overview=full&geometries=geojson`);
  const data = await res.json();
  const coordinates = data.routes[0].geometry.coordinates;
  return coordinates;
} catch (err) {
  console.error("Error fetching route:", err);
  return [];
}
};
  