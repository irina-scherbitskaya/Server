import matplotlib.image as mpimg
from enum import Enum
import networkx as nx
import json as js
train_img = 'resource/train.png'


class PostType(Enum):
    TOWN = 1
    MARKET = 2
    STORAGE = 3

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
            self.lines[line['idx']] = Line(line)
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

class Train:
    def __init__(self, train):
        self.line = train['line_idx']
        self.position = train['position']
        self.speed = train['speed']


class Point:
    def __init__(self, pos):
        self.pos_x = pos[0]
        self.pos_y = pos[1]


class Line:
    def __init__(self, line):
        self.point1 = line['points'][0]
        self.point2 = line['points'][1]
        self.length = line['length']


class Post:
    def __init__(self, post):
        self.type = PostType(post['type'])
        self.name = post['name']
        self.point = post['point_idx']
        