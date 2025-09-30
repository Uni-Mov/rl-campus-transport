import type { Coordinate } from "@/types/coordinate";

export const defineRoute = async (): Promise<Coordinate[]> => {
try {
  const res = await fetch("https://router.project-osrm.org/route/v1/driving/-64.3051,-33.1208;-64.3499,-33.1226?overview=full&geometries=geojson");
  
  const data = await res.json();
  const coordinates = data.routes[0].geometry.coordinates;
  return coordinates;
} catch (err) {
  console.error("Error fetching route:", err);
  return [];
}
};
  