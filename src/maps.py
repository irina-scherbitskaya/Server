import networkx as nx
import json as js
from src.gamedetails import *


class Map:
    def __init__(self):
        self.layers = []

    def push_layer(self, layer):
        self.layers.append(layer)

    def get_last(self):
        return self.layers[len(self.layers) - 1]


class Layer:
    def parse_layer(self, json_str):
        pass

    def show_layer(self, plot, canvas):
        pass

    def get_pos(self):
        pass


class Layer0(Layer):
    def __init__(self, json):
        self.points = dict()
        self.lines = dict()
        self.graph = nx.Graph()
        self.pos_points = dict()
        self.parse_layer(json)

    def parse_layer(self, json_str):
        data = js.loads(json_str)
        for line in data['lines']:
            self.lines[line['idx']] = Line(line['points'])
        self.create_graph(data)
        for key, value in self.pos_points.items():
            self.points[key] = Point(value)

    def create_graph(self, data):
        self.graph.add_nodes_from([v['idx'] for v in data['points']])
        self.graph.add_weighted_edges_from([(e['points'][0], e['points'][1], e['length']) for e in data['lines']])
        tmp_pos = nx.spring_layout(self.graph, iterations=100, scale=300)
        self.pos_points = nx.kamada_kawai_layout(self.graph, pos=tmp_pos, scale=250)

    def show_layer(self, plot, canvas):
        if len(self.points) != 0:
            plot.drawing_layer0(canvas, self.graph, self.pos_points)

    def get_pos(self):
        return self.pos_points


class Layer1(Layer):
    def __init__(self, json):
        self.trains = dict()
        self.parse_layer(json)

    def parse_layer(self, json_str):
        data = js.loads(json_str)
        for train in data['trains']:
            self.trains = Train(train)

    def show_layer(self, plot, canvas):
        if len(self.trains) != 0:
            plot.drawing_layer0(canvas, self.trains[0])

