from ia_ml.utils.see_nodes import plot_nodes
from ia_ml.utils.see_streets import plot_streets

graph_file = "src/data/Río_Cuarto_Cordoba_Argentina.graphml"

plot_nodes(graph_file)
plot_streets(graph_file)
print("Visualización generada.")
