import json as js
import matplotlib.pyplot as plt
import networkx as nx
import warnings
warnings.filterwarnings('ignore')

fig = plt.gcf()
fig.set_size_inches(20.5, 20)
    
def drawing_graph(file):
    fig.clear()
    data = js.load(open('%s.json' % file))
    G = nx.Graph()
    G.add_nodes_from([v['idx'] for v in data['points']])
    G.add_weighted_edges_from([(e['points'][0], e['points'][1], e['length']) for e in data['lines']])

    labels = nx.get_edge_attributes(G,'weight')
    pos = nx.spectral_layout(G)
    nx.draw_networkx_edge_labels(G, pos, font_size = 8, edge_labels = labels)
    nx.draw_networkx_labels(G, pos, font_size = 8)
    nx.draw(G,pos, node_color = '#DDA0DD')

    fig.savefig('%s.png' % file)

drawing_graph('small_graph')
drawing_graph('big_graph')