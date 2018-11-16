import json as js
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import warnings
from src.forserver import *
from src.gui import *

warnings.filterwarnings('ignore')


class Map:
    def __init__(self):
        self.plot = Drawing()
        self.layers = []

    def push_layer(self, layer, data):
        if layer == 0:
            self.layers.append(Layer0(data))

    def draw_layers(self, canvas):
        for layer in self.layers:
            layer.show_layer(self.plot, canvas)


class Layer:
    def parse_layer(self, json_str):
        pass

    def show_layer(self, plot, canvas):
        pass


class Layer0(Layer):
    def __init__(self, json):
        self.points = []
        self.lines = []
        self.pos_points = []
        self.graph = nx.Graph()
        self.parse_layer(json)

    def parse_layer(self, json_str):
        data = js.loads(json_str)
        self.points = data['points']
        self.lines = data['lines']
        self.graph.add_nodes_from([v['idx'] for v in data['points']])
        self.graph.add_weighted_edges_from([(e['points'][0], e['points'][1], e['length']) for e in data['lines']])
        tmp_pos = nx.spring_layout(self.graph, iterations=100, weight=1)
        self.pos_points = nx.kamada_kawai_layout(self.graph, weight=None, pos=tmp_pos)

    def show_layer(self, plot, canvas):
        if len(self.points) != 0:
            plot.drawing_layer0(canvas, self.graph, self.pos_points)

# creates gui
class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.configure(bg='white')
        self.title('Drawing graph')
        self.map = Map()
        self.create_widgets()
        self.destroy_flag = True
        self.protocol('WM_DELETE_WINDOW', self.destroy_window)

    def destroy_window(self):
        self.destroy_flag = False
        self.destroy()

    def create_widgets(self):
        self.canvas = FigureCanvasTkAgg(self.map.plot.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.map.draw_layers(self.canvas)
        self.canvas.draw()

    def show(self):
        self.map.draw_layers(self.canvas)


#details of games
class Game:

    def __init__(self, pers='Rondondon'):
        Socket.connect()
        self.pers_name = pers
        self.pers_data = None
        self.maps = []
        self.app = Application()

    def login(self):
        Socket.send(Action.LOGIN, '{"name":"%s"}' % self.pers_name)
        self.pers_data = Socket.receive()

    def get_maps(self):
        Socket.send(Action.MAP, '{"layer":0}')
        rec = Socket.receive()
        self.maps.append(rec)
        self.app.map.push_layer(0, rec.data)
        self.app.show()


if __name__ == "__main__":
    game = Game()
    game.login()
    game.get_maps()

    while game.app.destroy_flag:
       game.app.update()

    Socket.close()
