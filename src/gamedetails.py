import json as js
from collections import  defaultdict
import networkx as nx
from heapq import heappush, heappop
from client import *
from copy import deepcopy


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
        self.list_adjacency = defaultdict(list)
        self.pos_points = dict()
        self.parse_layer(json)

    def parse_layer(self, data):
        self.lines = {line['idx']: Line(line) for line in data['lines']}
        for idx, line in self.lines.items():
            self.list_adjacency[line.point1].append(line)
            self.list_adjacency[line.point2].append(line)
        self.points = {idx: Point(pos) for idx, pos in self.pos_points.items()}
        self.pos_points = self.set_pos(data)

    def set_pos(self, data):
        graph = nx.Graph()
        graph.add_nodes_from([v['idx'] for v in data['points']])
        graph.add_weighted_edges_from((line.point1, line.point2, line.length) for idx, line in self.lines.items())
        tmp_pos = nx.kamada_kawai_layout(graph, scale=290)
        return nx.spring_layout(graph, pos=tmp_pos, iterations=10000, scale=290)

    def get_point2(self, line, point):
        point2 = None
        if line.point2 == point:
            point2 = line.point1
        elif line.point1 == point:
            point2 = line.point2
        return self.points[point2]

    def get_route(self, point, line):
        route = 0
        if line.point1 == point:
            route = 1
        elif line.point2 == point:
            route = -1
        return route

    def get_pos(self):
        return self.pos_points


class Layer1:
    def __init__(self, json):
        self.trains = dict()
        self.posts = dict()
        self.parse_layer(json)

    def parse_layer(self, data):
        for train in data['trains']:
            self.trains[train['idx']] = Train(train)
        for post in data['posts']:
            self.posts[post['point_idx']] = CreatorPost.CreatePost(post)

    def update(self, data):
        for train in data['trains']:
            self.trains[train['idx']].update(train)
        for post in data['posts']:
            self.posts[post['point_idx']].update(post)


class Player:
    def __init__(self, player):
        self.home_idx = player['home']['post_idx']
        self.name = player['name']
        self.rating = player['rating']
        self.trains_idx = []
        for train in player['trains']:
            self.trains_idx.append(train['idx'])

    def update(self, rating):
        self.rating = rating


class Train:
    def __init__(self, train):
        self.line = train['line_idx']
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
        self.idx = line['idx']
        self.point1 = line['points'][0]
        self.point2 = line['points'][1]
        self.length = line['length']
        self.free = True


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

    def get_goods(self, time, capacity):
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
        self.trains = dict()

    def tostring(self):
        return super().tostring() + 'product: %d \nreplenishment: %d' % (self.product, self.replenishment)

    def update(self, market):
        self.product = market['product']

    def get_goods(self, time1, time2):
        time = time2 - time1
        product = self.replenishment*time
        if time1 == 0:
            product += self.product_capacity
        return min(product, self.product_capacity)


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

    def get_goods(self, time1, time2):
        time = time2 - time1
        armor = self.replenishment*time
        if time1 == 0:
            armor += self.armor
        return min(armor, self.armor_capacity)

 class Path:
    def __init__(self, goods, point):
        self.goods = goods
        self.point = point
        self.start_line = -1
        self.posts = defaultdict()

    def update(self, post, time, capacity):
        if self.posts[post.idx] is None:
            self.posts[post.idx] = time
            self.goods = min(capacity, self.goods + post.get_goods(0, time))
        else:
            self.goods = min(capacity, self.goods + post.get_goods(self.posts[post.idx], time))
            self.posts[post.idx] = time

    def __copy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result


class Game:
    def __init__(self):
        Socket.connect()
        self.players = dict()
        self.layers = [None] * 2
        self.tic = 0

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
                if train.position == line.length:
                    self.get_next_line(train, line.point2)
                elif train.position == 0:
                    self.get_next_line(train, line.point1)
                self.move_train(train_idx, train)

    def get_next_line(self):
        pass

    # dijkstra
    def get_paths(self, point, town, post_type, train):
        heap = []
        # distance, point, goods, start_line
        heappush(heap, (0, Path(train.goods, point)))
        out = list()
        list_adj = self.layers[0].list_adjacency
        max_point_goods = dict()

        while len(heap) > 0:
            dist, path = heappop(heap)
            for line in list_adj[path.point]:
                if not line.free:
                    continue

                point2 = self.layers[0].get_point2(line, path.point)
                dist += line.length

                path = copy(path)
                post = self.layers[1].posts[point2]
                if post is not None:
                    if post.type == post_type:
                        path.update(post, dist, train.goods_capacity)
                    elif point2 == town:
                        out.append((path.start_line, path.goods))


                if max_point_goods[point2] is None:
                    max_point_goods[point2] = path.goods
                elif max_point_goods[point2] >= path.goods:
                    continue

                if path.start_line == -1:
                    path.start_line
                    heappush(heap, (dist, point2, goods, line.idx))
                else:
                    heappush(heap, (dist, point2, goods, start_line))

        return out

    def move_train(self, train_idx, train):
        line = train.line
        speed = train.speed
        Socket.send(Action.MOVE, '{"line_idx":%s,"speed":%s,"train_idx":%s}' % (line, speed, train_idx))
        rec = Socket.receive()

    def update_layer(self, layer):
        Socket.send(Action.MAP, '{"layer":%s}' % layer)
        rec = Socket.receive()
        if rec.result == Result.OKEY.value:
            data = js.loads(rec.data)
            if layer == 0:
                if self.layers[layer] is None:
                    self.layers[layer] = Layer0(data)
                else:
                    self.layers[layer].update(data)
            elif layer == 1:
                if self.layers[layer] is None:
                    self.layers[layer] = Layer1(data)
                else:
                    self.layers[layer].update(data)
                self.tic += 1
                self.update_ratings(data['ratings'])

    def update_ratings(self, ratings):
        for idx, player in self.players.items():
            player.update(ratings[idx]['rating'])

    def tick(self):
        Socket.send(Action.TURN, '')
        rec = Socket.receive()
        self.update_layer(1)
        self.next_move()
