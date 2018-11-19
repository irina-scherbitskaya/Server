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
            self.posts[post['idx']] = CreatorPost.CreatePost(post)


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
    def __init__(self, point):
        self.point1 = point[0]
        self.point2 = point[1]


#created post according to the type
class CreatorPost:
    @staticmethod
    def CreatePost(post):
        ret_post = Post(post)
        if post['type'] == 1:
            ret_post = Town(post)
        elif post['type'] == 2:
            ret_post = Market(post)
        elif post['type'] == 3:
            ret_post = Storage(post)
        return ret_post


class Post:
    def __init__(self, post):
        self.name = post['name']
        self.point = post['point_idx']
        self.idx = post['idx']

    def tostring(self):
        return '%s\n' % self.name


class Town(Post):
    def __init__(self, town):
        super().__init__(town)
        self.armor = town['armor']
        self.armor_capacity = town['armor_capacity']
        self.player = town['player_idx']
        self.population = town['population']
        self.population_capacity = town['population_capacity']
        self.product = town['product']
        self.product_capacity = town['product_capacity']
        self.color = '#FFFF00'

    def tostring(self):
        return super().tostring()+'armor: %d \npopulation: %d \n' \
                                  'product: %d' % (self.armor, self.population, self.product)


class Market(Post):
    def __init__(self, market):
        super().__init__(market)
        self.replenishment = market['replenishment']
        self.product = market['product']
        self.product_capacity = market['product_capacity']
        self.color = '#87CEEB'

    def tostring(self):
        return super().tostring() + 'product: %d' % self.product


class Storage(Post):
    def __init__(self, storage):
        super().__init__(storage)
        self.armor = storage['armor']
        self.armor_capacity = storage['armor_capacity']
        self.replenishment = storage['replenishment']
        self.color = '#808080'

    def tostring(self):
        return super().tostring() + 'armor: %d\n' % self.armor



