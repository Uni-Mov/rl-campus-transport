import type { Coordinate } from "@/types/coordinate";

export const defineRoute = (): Coordinate[] => {
        
const routeCoordinates: Coordinate[] = [
    [-74.006, 40.7128], // starting point
    [-73.99, 40.715],
    [-73.975, 40.725],
    [-73.955, 40.7310],
    [-73.950, 40.7320], // final point
  ];

  return routeCoordinates;
}
  