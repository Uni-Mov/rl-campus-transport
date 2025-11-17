import { defineRoute } from "@/pages/travel/hooks/defineRoute";
import type { Coordinate } from "@/types/coordinate";
import { describe, it, expect, vi, afterEach } from "vitest";

// Mock global fetch
global.fetch = vi.fn();

describe("defineRoute", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  describe("with useCustomRouter = true (POST to backend)", () => {
    it("should send POST request with correct JSON body", async () => {
      const mockResponse = {
        route: [
          {
            coordinates: [
              [-64.349, -33.123],
              [-64.350, -33.124],
              [-64.351, -33.125],
            ],
          },
        ],
        waypoints: [[-64.349, -33.123]],
      };

      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const points: Coordinate[] = [
        [-64.349, -33.123],
        [-64.349, -33.123],
        [-64.351, -33.125],
      ];

      const result = await defineRoute(points, true);

      // Verify fetch was called with correct method and headers
      expect(fetch).toHaveBeenCalledWith(
        "/api/paths/calculate",
        expect.objectContaining({
          method: "POST",
          headers: { "Content-Type": "application/json" },
        })
      );

      // Verify body payload
      const callArgs = vi.mocked(fetch).mock.calls[0];
      const bodyArg = callArgs[1]?.body;
      const sentBody = JSON.parse(bodyArg as string);

      expect(sentBody).toEqual({
        start_node: [-64.349, -33.123],
        end_node: [-64.351, -33.125],
        waypoints: [[-64.349, -33.123]],
      });

      // Verify returned coordinates
      expect(result).toEqual(mockResponse.route[0].coordinates);
    });

    it("should handle empty waypoints when only start and end are provided", async () => {
      const mockResponse = {
        route: [{ coordinates: [[-64.349, -33.123], [-64.351, -33.125]] }],
        waypoints: [],
      };

      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const points: Coordinate[] = [
        [-64.349, -33.123],
        [-64.351, -33.125],
      ];

      await defineRoute(points, true);

      const callArgs = vi.mocked(fetch).mock.calls[0];
      const bodyArg = callArgs[1]?.body;
      const sentBody = JSON.parse(bodyArg as string);

      expect(sentBody.waypoints).toEqual([]);
    });

    it("should handle backend errors gracefully", async () => {
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: false,
        statusText: "Internal Server Error",
        text: async () => "Error message",
      } as Response);

      const points: Coordinate[] = [
        [-64.349, -33.123],
        [-64.351, -33.125],
      ];

      const result = await defineRoute(points, true);

      // Should return empty array on error
      expect(result).toEqual([]);
    });

    it("should handle malformed response gracefully", async () => {
      const mockResponse = { route: [] }; // Missing coordinates

      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const points: Coordinate[] = [
        [-64.349, -33.123],
        [-64.351, -33.125],
      ];

      const result = await defineRoute(points, true);

      expect(result).toEqual([]);
    });
  });

  describe("with useCustomRouter = false (fallback to OSRM)", () => {
    it("should fetch from OSRM with correct URL", async () => {
      const mockResponse = {
        routes: [
          {
            geometry: {
              coordinates: [
                [-64.349, -33.123],
                [-64.350, -33.124],
              ],
            },
          },
        ],
      };

      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const points: Coordinate[] = [
        [-64.349, -33.123],
        [-64.351, -33.125],
      ];

      await defineRoute(points, false);

      // Verify OSRM URL is constructed correctly
      const url = vi.mocked(fetch).mock.calls[0][0] as string;
      expect(url).toContain("https://router.project-osrm.org/route/v1/driving/");
      expect(url).toContain("-64.349,-33.123");
      expect(url).toContain("-64.351,-33.125");
    });

    it("should return OSRM coordinates from geometry.coordinates", async () => {
      const osrmCoordinates = [
        [-64.349, -33.123],
        [-64.350, -33.124],
        [-64.351, -33.125],
      ];

      const mockResponse = {
        routes: [
          {
            geometry: {
              coordinates: osrmCoordinates,
            },
          },
        ],
      };

      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const points: Coordinate[] = [
        [-64.349, -33.123],
        [-64.351, -33.125],
      ];

      const result = await defineRoute(points, false);

      expect(result).toEqual(osrmCoordinates);
    });

    it("should handle OSRM errors gracefully", async () => {
      vi.mocked(fetch).mockRejectedValueOnce(new Error("Network error"));

      const points: Coordinate[] = [
        [-64.349, -33.123],
        [-64.351, -33.125],
      ];

      const result = await defineRoute(points, false);

      expect(result).toEqual([]);
    });
  });

  describe("edge cases", () => {
    it("should handle fetch network errors", async () => {
      vi.mocked(fetch).mockRejectedValueOnce(new Error("Fetch failed"));

      const points: Coordinate[] = [
        [-64.349, -33.123],
        [-64.351, -33.125],
      ];

      const result = await defineRoute(points, true);

      expect(result).toEqual([]);
    });
  });
});
