# Graph utilities — brief technical reference

This document describes the purpose, behavior, inputs, outputs, and usage of the small set of utilities in ia_ml/src that operate on the OSMnx graph for Río Cuarto.

## Summary table

- ia_ml/src/data/download_graph.py — download, save, load, relabel graph and instantiate the navigation env.
- ia_ml/src/utils/see_nodes.py — human-friendly console inspection of nodes and incident edges.
- ia_ml/src/utils/see_streets.py — extract street names per node and optional reverse-geocoding for address/house number.

---

## ia_ml/src/data/download_graph.py

Purpose
- Download the road network for a place using OSMnx (network_type="drive").
- Save the graph to GraphML for reuse.
- Load an existing GraphML if present.
- Relabel nodes from OSM IDs to dense indices 0..N-1 to match the expectations of the RL environment.
- Create a `WaypointNavigationEnv` instance for quick sanity checks.

Location
- ia_ml/src/data/download_graph.py

Key functions
- _configure_osmnx(): compatibility wrapper to set OSMnx config/settings across versions.
- download_and_save_graph(place_name: str, out_path: str): downloads and saves GraphML.
- load_graph_from_graphml(path: str) -> nx.MultiDiGraph: loads GraphML via OSMnx.
- relabel_nodes_to_indices(G) -> (G_relabeled, node_to_idx, idx_to_node): produces 0..N-1 relabeled graph and mappings.
- example_create_env(...): demonstration flow that downloads/loads the graph, relabels it, creates waypoints and destination, and instantiates the environment.

Inputs
- place (default "Río Cuarto, Córdoba, Argentina")
- destination file path (hardcoded default: `ia_ml/src/data/grafo_rio_cuarto.graphml`)

Outputs / Side effects
- Writes GraphML at `ia_ml/src/data/grafo_rio_cuarto.graphml` (if not present).
- Returns an env instance when run as script (prints initial observation).

Notes and integration
- Run from repo root using module execution to keep imports working:
  - python3 -m ia_ml.src.data.download_graph
- If you want a relabeled GraphML persisted, add an extra save step (not currently saved).
- The script expects `WaypointNavigationEnv` to accept a networkx graph with integer node IDs.

---

## ia_ml/src/utils/see_nodes.py

Purpose
- Provide a readable console listing of a small sample of nodes and edges for quick inspection.
- Shows node ID, coordinates, street_count, degree and a small sample of neighbors.
- Prints a compact summary of incident edges (length, highway type, lanes, speed, one-way flag, geometry existence).

Location
- ia_ml/src/utils/see_nodes.py

Behavior / Output
- Loads GraphML from `ia_ml/src/data/grafo_rio_cuarto.graphml`.
- Prints total node and edge counts.
- For the first N nodes (default N=5) prints:
  - node id, latitude, longitude, street_count and degree
  - sample neighbor list with coordinates
- Prints the first N edges with concise attributes and whether they include geometry.

Notes
- Uses OSMnx `ox.load_graphml`.
- Designed for human consumption in the terminal; not intended for programmatic parsing.

Suggested improvements
- Accept CLI args (path, sample size).
- Option to output CSV or JSON for downstream processing.

---

## ia_ml/src/utils/see_streets.py

Purpose
- For a sample of nodes, aggregate street names from incident edges and attempt reverse-geocoding to obtain a human-readable road name and house number (when available).
- Useful to correlate graph nodes with street identifiers and addresses.

Location
- ia_ml/src/utils/see_streets.py

Behavior / Output
- Loads the GraphML from `ia_ml/src/data/grafo_rio_cuarto.graphml`.
- For a sample of nodes (default 20) prints:
  - node id and coordinates
  - list of street names inferred from `edge['name']` on incident edges
  - result of reverse geocoding via Nominatim: road and house_number (if available)
- Rate-limited to respect Nominatim usage (RateLimiter with min_delay_seconds=1.0).

Important considerations
- Street names originate from OSM edge attributes (`name`) attached to edges that connect the node.
- House numbers are not part of the road graph and will only be returned by reverse geocoding if OSM has address data at that coordinate.
- Nominatim usage policy:
  - Provide a clear `user_agent`.
  - Avoid bulk queries against the public endpoint; use local instance or paid service for large volumes.
  - Respect rate limits and caching.