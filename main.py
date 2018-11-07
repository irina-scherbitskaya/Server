import json as js
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import networkx as nx
import tkinter as tk
import warnings
warnings.filterwarnings('ignore')


class Drawing:
    def __init__(self):
        self.idx = 1
        self.fig = plt.gcf()
        self.fig.set_size_inches(10, 6)
        self.list_graphs = ['small_graph', 'big_graph', 'first', 'second', 'third']
        self.dict_layout = {i: nx.kamada_kawai_layout for i in self.list_graphs}
        self.dict_layout['small_graph'] = nx.fruchterman_reingold_layout

    def drawing_graph(self, canvas):
        self.fig.clear()
        G = self.parse_graph()
        labels = nx.get_edge_attributes(G, 'weight')
        pos = self.dict_layout[self.list_graphs[self.idx]](G, weight=None)
        nx.draw_networkx_edge_labels(G, pos, font_size=8, edge_labels=labels)
        nx.draw_networkx(G, pos=pos, node_color='#DDA0DD', with_labels=True, font_size=8, node_size=200)
        canvas.draw_idle()

    def parse_graph(self):
        with open('Graphs/%s.json' % self.list_graphs[self.idx]) as f:
           data = js.load(f)
        G = nx.Graph()
        G.add_nodes_from([v['idx'] for v in data['points']])
        G.add_weighted_edges_from([(e['points'][0], e['points'][1], e['length']) for e in data['lines']])
        return G

    def drawing_next_graph(self, canvas):
        if self.idx < len(self.list_graphs) - 1:
            self.idx += 1
            self.drawing_graph(canvas)

    def drawing_last_graph(self, canvas):
        if self.idx > 0:
            self.idx -= 1
            self.drawing_graph(canvas)


class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.configure(bg='white')
        self.title('Drawing graph')
        self.plot = Drawing()
        self.create_widgets()

    def last_graph(self):
        self.plot.drawing_last_graph(self.canvas)

    def next_graph(self):
        self.plot.drawing_next_graph(self.canvas)

    def create_widgets(self):
        self.canvas = FigureCanvasTkAgg(self.plot.fig, master=self)
        self.create_buttons()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.plot.drawing_graph(self.canvas)
        self.canvas.draw()

    def create_buttons(self):
        self.frame = tk.Frame(self)
        button_next = tk.Button(master=self.frame, text="Next graph", command=self.next_graph, font='arial 15', bg='white')
        button_next.pack(side=tk.RIGHT, anchor=tk.W)
        button_last = tk.Button(master=self.frame, text="Last graph", command=self.last_graph, font='arial 15', bg='white')
        button_last.pack(side=tk.LEFT, anchor=tk.W)
        self.frame.pack(side=tk.BOTTOM)


app = Application()

app.mainloop()
