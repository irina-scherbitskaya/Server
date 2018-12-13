import networkx as nx
import json as js
from client import *


class PostType(Enum):
    TOWN = 1
    MARKET = 2
    STORAGE = 3


class EventType(Enum):
    TRAIN_COLLISION = 1
    HIJACKERS_ASSAULT = 2
    PARASITES_ASSAULT = 3
    REFUGEES_ARRIVAL = 4
    RESOURCE_OVERFLOW = 5
    RESOURCE_LACK = 6
    GAME_OVER = 100


class Layer0:
    def __init__(self, json):
        self.points = dict()
        self.lines = dict()
        self.dict_lines = dict()
        self.graph = nx.Graph()
        self.pos_points = dict()
        self.parse_layer(json)

    def parse_layer(self, json_str):
        data = js.loads(json_str)
        self.lines = {line['idx']: Line(line) for line in data['lines']}
        self.dict_lines = {(line.point1, line.point2): idx for idx, line in self.lines.items()}

        self.create_graph(data)
        self.points = {idx: Point(pos) for idx, pos in self.pos_points.items()}

    def create_graph(self, data):
        self.graph.add_nodes_from([v['idx'] for v in data['points']])
        self.graph.add_weighted_edges_from((line.point1, line.point2, line.length) for idx, line in self.lines.items())
        tmp_pos = nx.kamada_kawai_layout(self.graph, scale=290)
        self.pos_points = nx.spring_layout(self.graph, pos=tmp_pos, iterations=10000, scale=290)

    def get_line_idx(self, point1, point2):
        line_idx = None
        if self.dict_lines.get((point1, point2)) is not None:
            line_idx = self.dict_lines[(point1, point2)]
        elif self.dict_lines.get((point2, point1)) is not None:
            line_idx = self.dict_lines[(point2, point1)]
        return line_idx

    def get_line_length(self, point1, point2):
        length = 0
        line_idx = self.get_line_idx(point1, point2)
        if line_idx is not None:
            length = self.lines[line_idx].length
        return length

    def get_route(self, point1, point2):
        route = 0
        if self.dict_lines.get((point1, point2)) is not None:
            route = 1
        elif self.dict_lines.get((point2, point1)) is not None:
            route = -1
        return route

    def get_pos(self):
        return self.pos_points


class Layer1:
    def __init__(self, json):
        self.trains = dict()
        self.posts = dict()
        self.parse_layer(json)

    def parse_layer(self, json_str):
        if json_str != '':
            data = js.loads(json_str)
            for train in data['trains']:
                self.trains[train['idx']] = Train(train)
            for post in data['posts']:
                self.posts[post['idx']] = CreatorPost.CreatePost(post)

    def update(self, json_str):
        if json_str != '':
            data = js.loads(json_str)
            for train in data['trains']:
                self.trains[train['idx']].update(train)
            for post in data['posts']:
                self.posts[post['idx']].update(post)



class Player:
    def __init__(self, player):
        self.home_idx = player['home']['post_idx']
        self.name = player['name']
        self.rating = player['rating']
        self.trains_idx = []
        for train in player['trains']:
            self.trains_idx.append(train['idx'])


class Train:
    def __init__(self, train):
        self.line = train['line_idx']
        self.path = []
        self.pos_path = 0
        #speed for each line on path
        self.speed_on_path = []
        self.position = train['position']
        self.speed = train['speed']
        self.goods = train['goods']
        self.goods_capacity = train['goods_capacity']
        self.goods_type = train['goods_type']
        self.player_idx = train['player_idx']
        self.color = '#FFFF00'

    def tostring(self):
        return 'speed: %d \ngoods: %d\ncapacity: %d' % (self.speed, self.goods, self.goods_capacity)

    def update(self, train):
        self.line = train['line_idx']
        self.position = train['position']
        self.speed = train['speed']
        self.goods = train['goods']
        self.goods_type = train['goods_type']


class Point:
    def __init__(self, pos):
        self.pos_x = pos[0]
        self.pos_y = pos[1]


class Line:
    def __init__(self, line):
        self.point1 = line['points'][0]
        self.point2 = line['points'][1]
        self.length = line['length']


# create post according to the type
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
        self.type = post['type']

    def tostring(self):
        return '%s\n' % self.name

    def update(self, post):
        pass


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
        return super().tostring() + 'armor: %d \npopulation: %d \n' \
                                    'product: %d' % (self.armor, self.population, self.product)

    def update(self, town):
        self.armor = town['armor']
        self.population = town['population']
        self.product = town['product']


class Market(Post):
    def __init__(self, market):
        super().__init__(market)
        self.replenishment = market['replenishment']
        self.product = market['product']
        self.product_capacity = market['product_capacity']
        self.color = '#87CEEB'

    def tostring(self):
        return super().tostring() + 'product: %d \nreplenishment: %d' % (self.product, self.replenishment)

    def update(self, market):
        self.product = market['product']


class Storage(Post):
    def __init__(self, storage):
        super().__init__(storage)
        self.armor = storage['armor']
        self.armor_capacity = storage['armor_capacity']
        self.replenishment = storage['replenishment']
        self.color = '#808080'

    def tostring(self):
        return super().tostring() + 'armor: %d\n' % self.armor

    def update(self, storage):
        self.armor = storage['armor']


class Game:
    def __init__(self):
        Socket.connect()
        self.players = dict()
        self.layers = [None] * 2

    def login(self, name='Petya'):
        Socket.send(Action.LOGIN, '{"name":"%s"}' % name)
        rec = Socket.receive()
        player_data = js.loads(rec.data)
        self.players[player_data['idx']] = Player(player_data)

    def logout(self):
        Socket.send(Action.LOGOUT, '')
        Socket.close()

    def start_game(self):
        self.update_layer(0)
        self.update_layer(1)
        self.next_move()

    # calculation of the next move
    def next_move(self):
        for idx, player in self.players.items():
            for train_idx in player.trains_idx:
                train = self.layers[1].trains[train_idx]
                line = self.layers[0].lines[train.line]
                if (len(train.path) == 0 or len(train.path) == train.pos_path) and train.position == line.length:
                    self.get_next_path(train, line.point2)
                elif (len(train.path) == 0 or len(train.path) == train.pos_path) and train.position == 0:
                    self.get_next_path(train, line.point1)
                self.move_train(train_idx, train)

    def get_path_len_speed(self, from_point, to_point):
        path = nx.dijkstra_path(self.layers[0].graph, from_point, to_point)
        line_path = []
        len_path = 0
        speed = []
        for i in range(0, len(path) - 1):
            line_path.append(self.layers[0].get_line_idx(path[i], path[i + 1]))
            len_path += self.layers[0].get_line_length(path[i], path[i + 1])
            speed.append(self.layers[0].get_route(path[i], path[i+1]))
        return (line_path, len_path, speed)

    # return train to home
    def path_to_home(self, train, point):
        town = self.layers[1].posts[self.players[train.player_idx].home_idx].point
        path = nx.dijkstra_path(self.layers[0].graph, point, town)
        train.path = [self.layers[0].get_line_idx(path[i], path[i + 1])
                      for i in range(0, len(path) - 1)]
        train.speed_on_path = [self.layers[0].get_route(path[i], path[i + 1])
                               for i in range(0, len(path) - 1)]

    # get new product for home
    def get_next_path(self, train, point):
        max_capacity = train.goods_capacity - train.goods
        max_goods = 0
        time = 0
        town = self.layers[1].posts[self.players[train.player_idx].home_idx]
        train.path = []
        train.pos_path = 0
        if town.population != 0:
            if max_capacity != 0:
                for idx, post in self.layers[1].posts.items():

                    if post.type != 2:
                        continue
                    # get path to market and home from point
                    path_to_market = self.get_path_len_speed(point, post.point)
                    path_to_home = self.get_path_len_speed(post.point, town.point)
                    len_path = path_to_market[1]
                    # get list of lines for train path and get length of path

                    can_get_product = min(len_path * post.replenishment + post.product,
                                          post.product_capacity, train.goods_capacity)

                    len_path += path_to_home[1]

                    if len_path > town.product / town.population or can_get_product > max_capacity:
                        continue

                    # if need to stop
                    if len(path_to_market) == 0 and (post.replenishment > max_goods
                                                     or (post.replenishment == max_goods and time > 1)):
                        time = 1
                        max_goods = post.replenishment
                    # if need to move
                    elif can_get_product > max_goods or (can_get_product == max_goods and time > len_path):
                        time = len_path
                        max_goods = can_get_product
                        train.path = path_to_market[0]
                        train.speed_on_path = path_to_market[2]

            if max_goods == 0:
                self.path_to_home(train, point)

    def move_train(self, train_idx, train):
        line = train.line
        line_length = self.layers[0].lines[line].length
        speed = train.speed
        if len(train.path) != 0 and (train.position == line_length or train.position == 0):
            line = train.path[train.pos_path]
            speed = train.speed_on_path[train.pos_path]
            train.pos_path += 1
        Socket.send(Action.MOVE, '{"line_idx":%s,"speed":%s,"train_idx":%s}' % (line, speed, train_idx))
        rec = Socket.receive()

    def update_layer(self, layer):
        Socket.send(Action.MAP, '{"layer":%s}' % layer)
        rec = Socket.receive()
        if layer == 0:
            if self.layers[layer] is None:
                self.layers[layer] = Layer0(rec.data)
            else:
                self.layers[layer].update(rec.data)
        elif layer == 1:
            if self.layers[layer] is None:
                self.layers[layer] = Layer1(rec.data)
            else:
                self.layers[layer].update(rec.data)

    def tick(self):
        Socket.send(Action.TURN, '')
        rec = Socket.receive()
        self.update_layer(1)
        self.next_move()
