import matplotlib.pyplot as plt
import networkx as nx

# draws using pyplot
class Drawing:
    def __init__(self):
        self.fig = plt.gcf()
        self.fig.set_size_inches(10, 6)

    def drawing_layer0(self, canvas, graph, pos):
        self.fig.clear()
        labels = nx.get_edge_attributes(graph, 'weight')
        nx.draw_networkx_edge_labels(graph, pos, font_size=6, edge_labels=labels)
        nx.draw_networkx(graph, pos=pos, node_color='#DDA0DD', with_labels=True, font_size=6, node_size=100)
        canvas.draw_idle()