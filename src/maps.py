import networkx as nx
import json as js
from src.gamedetails import *


class Map:
    def __init__(self):
        self.layers = []

    def push_layer(self, layer):
        self.layers.append(layer)

    def get(self, idx):
        return self.layers[idx]


class Layer:
    def parse_layer(self, json_str):
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
        tmp_pos = nx.kamada_kawai_layout(self.graph, scale=250)
        self.pos_points = nx.spring_layout(self.graph, pos=tmp_pos, fixed=tmp_pos, iterations=100, scale=250)

    def get_pos(self):
        return self.pos_points


class Layer1(Layer):
    def __init__(self, json):
        self.trains = dict()
        self.posts = dict()
        self.parse_layer(json)

    def parse_layer(self, json_str):
        data = js.loads(json_str)
        for train in data['trains']:
            self.trains[train['idx']] = Train(train)
        for post in data['posts']:
            self.posts[post['idx']] = Post(post)


