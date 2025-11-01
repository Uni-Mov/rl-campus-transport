import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import random

# ------------------------------------------------------------
# 1. Embeddings (rico y pobre con distancia al goal)
# ------------------------------------------------------------
def build_rich_embeddings(G, goal):
    nodes = list(G.nodes(data=True))
    n = len(nodes)
    deg = dict(G.degree())
    max_deg = max(deg.values())
    total_edges = G.number_of_edges()
    density = total_edges / float(max(1, n*(n-1)))

    goal_x, goal_y = G.nodes[goal]["x"], G.nodes[goal]["y"]
    embeddings = {}
    for node, data in nodes:
        x, y = data["x"], data["y"]
        neighbors = list(G.neighbors(node))
        neighbor_count = len(neighbors)
        degree_centrality = deg[node] / (n-1)
        avg_neighbor_deg = np.mean([deg[nn] for nn in neighbors]) if neighbors else 0
        distance_to_goal = np.linalg.norm(np.array([x, y]) - np.array([goal_x, goal_y]))
        vec = np.array([
            x, y, deg[node]/max_deg, neighbor_count, degree_centrality,
            avg_neighbor_deg, density, distance_to_goal
        ], dtype=np.float32)
        embeddings[str(node)] = vec
    return embeddings


def build_poor_embeddings(G, goal):
    deg = dict(G.degree())
    max_deg = max(deg.values())
    goal_x, goal_y = G.nodes[goal]["x"], G.nodes[goal]["y"]

    embeddings = {}
    for node, data in G.nodes(data=True):
        x, y = data["x"], data["y"]
        distance_to_goal = np.linalg.norm(np.array([x, y]) - np.array([goal_x, goal_y]))
        vec = np.array([x, y, deg[node]/max_deg, distance_to_goal], dtype=np.float32)
        embeddings[str(node)] = vec
    return embeddings


# ------------------------------------------------------------
# 2. Construcción del grafo (garantizando camino al 30)
# ------------------------------------------------------------
random.seed(7)
G = nx.DiGraph()

# Centro urbano
for i in range(1, 16):
    G.add_node(i, x=random.uniform(0, 5), y=random.uniform(0, 5))
for a in range(1, 16):
    for b in range(a+1, 16):
        if random.random() < 0.4:
            G.add_edge(a, b)
            if random.random() < 0.5:
                G.add_edge(b, a)

# Transición
for i in range(16, 26):
    G.add_node(i, x=random.uniform(5, 9), y=random.uniform(2, 6))
    # conectar al azar con el centro
    G.add_edge(i, random.randint(1, 15))
    G.add_edge(random.randint(1, 15), i)
    if i > 16:
        G.add_edge(i, i-1)
        G.add_edge(i-1, i)

# Periferia (donde está el destino)
for i in range(26, 41):
    G.add_node(i, x=random.uniform(9, 13), y=random.uniform(0, 10))
    if i > 26:
        G.add_edge(i, i-1)
        G.add_edge(i-1, i)
    if i < 30:
        G.add_edge(i, i+1)
    if i == 26:
        G.add_edge(20, 26)   # conexión segura desde el centro hacia periferia
    if i == 30:
        G.add_edge(29, 30)   # asegurar camino al destino
        G.add_edge(28, 30)
        G.add_edge(25, 27)
        G.add_edge(27, 28)

# Ahora siempre hay camino desde 1 → ... → 30
pos = {n: (G.nodes[n]["x"], -G.nodes[n]["y"]) for n in G.nodes}

# ------------------------------------------------------------
# 3. Asignar pesos
# ------------------------------------------------------------
def assign_weights(G, embeddings):
    for u, v in G.edges:
        w_u = np.mean(embeddings[str(u)])
        w_v = np.mean(embeddings[str(v)])
        G[u][v]["weight"] = round((abs(w_u) + abs(w_v)) / 2, 3)


# ------------------------------------------------------------
# 4. Simulación paso a paso
# ------------------------------------------------------------
def simulate(G, start, goal, embeddings, title):
    current, visited, route = start, {start}, [start]
    plt.ion()
    fig, ax = plt.subplots(figsize=(8, 6))
    plt.title(title)
    plt.show(block=False)
    step = 0
    total_cost = 0

    while current != goal:
        step += 1
        neighbors = [n for n in G.neighbors(current) if n not in visited]
        if not neighbors:
            print(f"🚧 Sin salida desde {current}. Fin.")
            break

        neighbor_weights = {n: G[current][n]["weight"] for n in neighbors}
        next_node = min(neighbor_weights, key=neighbor_weights.get)
        cost = neighbor_weights[next_node]
        total_cost += cost
        route.append(next_node)
        visited.add(next_node)

        print(f"Paso {step}: {current} -> {next_node} (peso {cost:.3f})")

        ax.clear()
        nx.draw(G, pos, with_labels=True, node_size=400,
                node_color=["red" if n == next_node else "green" if n in route else "lightgray" for n in G.nodes],
                ax=ax)
        edge_labels = {(u, v): f"{d['weight']:.2f}" for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7, ax=ax)
        plt.title(f"{title} | Paso {step}: {current}->{next_node}")
        plt.pause(0.8)
        current = next_node

    plt.ioff()
    plt.show()
    print(f"Ruta final: {route} | Costo total: {total_cost:.3f}\n")
    return route, total_cost


# ------------------------------------------------------------
# 5. Comparar embeddings con mismo inicio y destino
# ------------------------------------------------------------
start, goal = 5, 30
print(f"\nInicio: {start} | Destino: {goal}\n")

# --- Embedding rico ---
rich_embeddings = build_rich_embeddings(G, goal)
assign_weights(G, rich_embeddings)
print("=== Simulación con EMBEDDING RICO ===")
route_rich, cost_rich = simulate(G.copy(), start, goal, rich_embeddings, "Embedding rico (con distancia)")

# --- Embedding pobre ---
poor_embeddings = build_poor_embeddings(G, goal)
assign_weights(G, poor_embeddings)
print("\n=== Simulación con EMBEDDING POBRE ===")
route_poor, cost_poor = simulate(G.copy(), start, goal, poor_embeddings, "Embedding pobre (con distancia)")

print("\n=== Comparación final ===")
print(f"Ruta con embedding rico:  {route_rich} | Costo total: {cost_rich:.3f}")
print(f"Ruta con embedding pobre: {route_poor} | Costo total: {cost_poor:.3f}")
