import json as js
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import networkx as nx
import tkinter as tk
import warnings

warnings.filterwarnings('ignore')

list_graph = ['big_graph', 'small_graph', 'first', 'second']


class Maps:
    def __init__(self, list_map):
        self.plot = Drawing()
        self.idx = 0
        self.list_maps = []
        self.list_pos_maps = []
        for graph in list_map:
            self.push_map(graph)

    def push_map(self, json_str):
        graph = self.parse_map(json_str)
        tmp_pos = nx.fruchterman_reingold_layout(graph, iterations=100, weight=1)
        pos = nx.kamada_kawai_layout(graph, weight=None, pos=tmp_pos)
        self.list_maps.append(graph)
        self.list_pos_maps.append(pos)

    def parse_map(self, json_str):
        data = js.load(open('test_graphs/%s.json' % json_str))
        graph = nx.Graph()
        graph.add_nodes_from([v['idx'] for v in data['points']])
        graph.add_weighted_edges_from([(e['points'][0], e['points'][1], e['length']) for e in data['lines']])
        return graph

    def next_map(self, canvas):
        if len(self.list_maps) - 1 > self.idx > -1:
            self.idx += 1
            self.show_map(canvas)

    def last_map(self, canvas):
        if len(self.list_maps) - 1 >= self.idx > 0:
            self.idx -= 1
            self.show_map(canvas)

    def show_map(self, canvas):
        graph = self.list_maps[self.idx]
        pos = self.list_pos_maps[self.idx]
        self.plot.drawing_map(canvas, graph, pos)


# draws using pyplot
class Drawing:
    def __init__(self):
        self.fig = plt.gcf()
        self.fig.set_size_inches(10, 6)

    def drawing_map(self, canvas, graph, pos):
        self.fig.clear()
        labels = nx.get_edge_attributes(graph, 'weight')
        nx.draw_networkx_edge_labels(graph, pos, font_size=6, edge_labels=labels)
        nx.draw_networkx(graph, pos=pos, node_color='#DDA0DD', with_labels=True, font_size=6, node_size=100)
        canvas.draw_idle()


# creates gui
class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.configure(bg='white')
        self.title('Drawing graph')
        self.maps = Maps(list_graph)
        self.create_widgets()
        self.destroy_flag = True
        self.protocol('WM_DELETE_WINDOW', self.destroy_window)

    def destroy_window(self):
        self.destroy_flag = False
        self.destroy()

    def last_graph(self):
        self.maps.last_map(self.canvas)

    def next_graph(self):
        self.maps.next_map(self.canvas)

    def create_widgets(self):
        self.canvas = FigureCanvasTkAgg(self.maps.plot.fig, master=self)
        self.create_buttons()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.maps.show_map(self.canvas)
        self.canvas.draw()

    def create_buttons(self):
        self.frame = tk.Frame(self)
        button_next = tk.Button(master=self.frame, text="Next graph", command=self.next_graph, font='arial 15',
                                bg='white')
        button_next.pack(side=tk.RIGHT, anchor=tk.W)
        button_last = tk.Button(master=self.frame, text="Last graph", command=self.last_graph, font='arial 15',
                                bg='white')
        button_last.pack(side=tk.LEFT, anchor=tk.W)
        self.frame.pack(side=tk.BOTTOM)


if __name__ == "__main__":
    app = Application()
    while app.destroy_flag:
       app.update()
