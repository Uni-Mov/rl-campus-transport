# OSMnx Guide for Río Cuarto Graphs

This document explains how we use **OSMnx** to represent and analyze the road network of Río Cuarto, Córdoba, Argentina. It covers nodes, edges, and basic operations, with code examples.

## Nodes

In OSMnx, **nodes** are represented as tuples:

```
(node_id, attrs)
```

- **node\_id**: a unique identifier from OpenStreetMap (OSM).
- **attrs**: a dictionary containing information about the node, typically including:
  - `x`: longitude of the point
  - `y`: latitude of the point
  - `street_count`: number of streets connected to this node

Sometimes `attrs` may also include additional attributes such as `highway`, `elevation`, etc.

**Interpretation:** nodes represent either an **intersection** or the **end of a street segment**.

---

## Edges

**Edges** in OSMnx are represented as tuples of the form:

```
(u, v, info_segment)
```

- **u**: node ID of the origin
- **v**: node ID of the destination
- **info\_segment**: a dictionary containing information about the road segment, commonly including:
  - `osmid`: the unique OSM ID for this way
  - `highway`: type of road (e.g., residential, primary)
  - `lanes`: number of lanes
  - `maxspeed`: maximum speed
  - `oneway`: `True` if the street is one-way
  - `reversed`: `True` if OSMnx reversed the edge to match the real-world direction
  - `length`: length of the segment in meters

**Interpretation:** edges represent **street segments connecting two nodes**.

---

## Graph Type

When you create a graph with:

```python
G = ox.graph_from_place("Río Cuarto, Córdoba, Argentina", network_type="drive")
```

OSMnx generates a **MultiDiGraph**:

- **Multi**: multiple edges can exist between the same pair of nodes. This allows modeling:
  - streets with separate lanes in each direction
  - multiple parallel streets
- **DiGraph**: the graph is **directed**:
  - one-way streets will have a single edge in the allowed direction
  - two-way streets will have two edges, one for each direction

This structure accurately represents the real-world road network, including complex intersections, one-way streets, and multi-lane roads.

---

## Example: Visualizing and Inspecting the Graph

The following Python code demonstrates how to download, visualize, and inspect the Río Cuarto road network:

```python
import osmnx as ox 
import matplotlib.pyplot as plt 

# Download the road network for Río Cuarto
G = ox.graph_from_place("Río Cuarto, Córdoba, Argentina", network_type="drive")

# Plot and save the graph
fig, ax = ox.plot_graph(G, show=False, close=False)
fig.savefig("grafo_rio_cuarto.png", dpi=300)
plt.close(fig)
print("Graph saved as grafo_rio_cuarto.png")

# Number of nodes and edges
print("Nodes:", G.number_of_nodes())
print("Edges:", G.number_of_edges())

# View the first 5 nodes with attributes
print("First 5 nodes:", list(G.nodes(data=True))[:5])

# View the first 5 edges (streets) with attributes
print("First 5 edges:", list(G.edges(data=True))[:5])
```

**Explanation:**

- `graph_from_place`: downloads the road network for the specified place.
- `plot_graph`: creates a visual representation of the network.
- `number_of_nodes()` and `number_of_edges()`: return the total number of nodes (intersections/endpoints) and edges (street segments) in the graph.
- `list(G.nodes(data=True))[:5]`: displays the first 5 nodes along with their attributes.
- `list(G.edges(data=True))[:5]`: displays the first 5 edges (street segments) with their attributes.

This allows you to both **visualize** the road network and **explore the structure** of nodes and edges programmatically.

---

## Example: Highlighting the Nearest Node to Specific Coordinates

You can find the node in the graph that is closest to a given set of coordinates (e.g., the location of UNRC at latitude -33.1089, longitude -64.3019) and visualize it:

```python
import osmnx as ox
import matplotlib.pyplot as plt

# Download the road network for Río Cuarto
G = ox.graph_from_place("Río Cuarto, Córdoba, Argentina", network_type="drive")

# Coordinates of UNRC
latitude = -33.1089
longitude = -64.3019

# Find the nearest node
nearest_node = ox.distance.nearest_nodes(G, X=longitude, Y=latitude)
print("Nearest node ID:", nearest_node)

# Plot the graph and highlight the nearest node
fig, ax = ox.plot_graph(
    G, 
    node_color='lightblue', 
    node_size=10, 
    edge_color='gray', 
    edge_linewidth=0.5, 
    show=False, 
    close=False
)
# Highlight the nearest node
ax.scatter(
    G.nodes[nearest_node]['x'], 
    G.nodes[nearest_node]['y'], 
    c='red', s=50, label='UNRC Node'
)
plt.legend()
plt.savefig("grafo_rio_cuarto_unrc.png", dpi=300)
plt.close(fig)
print("Graph saved as grafo_rio_cuarto_unrc.png")
```

**Explanation:**

- `ox.distance.nearest_nodes(G, X, Y)`: finds the node in the graph closest to the given coordinates. Note that `X` is longitude and `Y` is latitude.  
- `ax.scatter(...)`: plots a red dot to highlight the nearest node.  
- `plt.savefig(...)`: saves the figure to a PNG file.  

This method allows you to **identify a specific location in the road network**, highlight it, and save a visual representation of the graph with the highlighted node.
