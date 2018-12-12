import json as js
from collections import defaultdict
import networkx as nx
from heapq import heappush, heappop
from client import *
from copy import deepcopy

COLOR_OTHER = '#C0C0C0'
COLOR_PLAYER = '#FFFACD'

class GameState(Enum):
    INIT = 1
    RUN = 2
    FINISHED = 3


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


class GOODS(Enum):
    PRODUCT = 1
    ARMOR = 2


class Layer0:
    def __init__(self, json):
        self.points = list()
        self.lines = list()
        self.list_adjacency = defaultdict(list)
        self.pos_points = dict()
        self.parse_layer(json)

    def parse_layer(self, data):
        tmp = [line['idx'] for line in data['lines']]
        self.lines = [None]*(max(tmp)+1)
        for line in data['lines']:
            self.lines[line['idx']] = Line(line)
        for line in self.lines:
            if line is not None:
                self.list_adjacency[line.point1].append(line.idx)
                self.list_adjacency[line.point2].append(line.idx)

        self.pos_points = self.set_pos(data)
        tmp = [idx for idx, pos in self.pos_points.items()]
        self.points = [None]*(max(tmp)+1)
        for idx, pos in self.pos_points.items():
            self.points[idx] = Point(idx, pos)

    def set_pos(self, data):
        graph = nx.Graph()
        graph.add_nodes_from([v['idx'] for v in data['points']])
        graph.add_weighted_edges_from((line['points'][0], line['points'][1], line['length']) for line in data['lines'])
        return nx.kamada_kawai_layout(graph, scale=300, weight=1)

    def get_point2(self, line, point):
        point2 = None
        if self.lines[line].point2 == point:
            point2 = self.lines[line].point1
        elif self.lines[line].point1 == point:
            point2 = self.lines[line].point2
        return point2

    def get_route(self, point, line):
        route = 0
        if line is not None:
            if self.lines[line].point2 == point:
                route = -1
            elif self.lines[line].point1 == point:
                route = 1
        return route

    def get_pos(self):
        return self.pos_points


class Layer1:
    def __init__(self, json, player_idx):
        self.trains = dict()
        self.posts = dict()
        self.train_goods = list()
        self.parse_layer(json, player_idx)

    def parse_layer(self, data, player_idx):
        for train in data['trains']:
            self.trains[train['idx']] = Train(train)
            if train['player_idx'] == player_idx:
                self.trains[train['idx']].color = COLOR_PLAYER
        self.train_goods = [0]*(len(self.trains))
        for post in data['posts']:
            self.posts[post['point_idx']] = CreatorPost.CreatePost(post)
            if post['type'] == PostType.TOWN.value:
                if post['player_idx'] == player_idx:
                    self.posts[post['point_idx']].color = COLOR_PLAYER

    def update(self, data):
        for train in data['trains']:
            self.trains[train['idx']].update(train)
        for post in data['posts']:
            self.posts[post['point_idx']].update(post)


class Player:
    def __init__(self, player):
        self.home = player['home']['idx']
        self.name = player['name']
        self.idx = player['idx']
        self.rating = player['rating']
        self.trains_idx = []
        for train in player['trains']:
            self.trains_idx.append(train['idx'])

    def update(self, rating):
        self.rating = rating


class Train:
    def __init__(self, train):
        self.idx = train['idx']
        self.line = train['line_idx']
        self.next_line = 0
        self.position = train['position']
        self.speed = train['speed']
        self.goods = train['goods']
        self.goods_capacity = train['goods_capacity']
        self.goods_type = train['goods_type']
        self.player_idx = train['player_idx']
        self.cooldown = train['cooldown']
        self.color = COLOR_OTHER

    def tostring(self):
        return 'speed: %d \ngoods: %d\ncapacity: %d' % (self.speed, self.goods, self.goods_capacity)

    def update(self, train):
        self.line = train['line_idx']
        self.position = train['position']
        self.speed = train['speed']
        self.goods = train['goods']
        self.cooldown = train['cooldown']
        self.goods_type = train['goods_type']
        self.next_line = 0


class Point:
    def __init__(self, idx, pos):
        self.idx = idx
        self.pos_x = pos[0]
        self.pos_y = pos[1]
        self.train_idx = 0


class Line:
    def __init__(self, line):
        self.idx = line['idx']
        self.point1 = line['points'][0]
        self.point2 = line['points'][1]
        self.length = line['length']
        self.train_idx = 0


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

    def get_goods(self, time1, time2):
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
        self.color = COLOR_OTHER

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
        product = self.replenishment * time
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
        armor = self.replenishment * time
        if time1 == 0:
            armor += self.armor
        return min(armor, self.armor_capacity)


class Path:
    def __init__(self, dist, goods, point):
        self.dist = dist
        self.goods = goods
        self.point = point
        self.start_line = None
        self.posts = dict()

    def update(self, post, capacity):
        if self.posts.get(post.idx) is None:
            self.posts[post.idx] = self.dist
            self.goods = min(capacity, self.goods + post.get_goods(0, self.dist))
        else:
            self.goods = min(capacity, self.goods + post.get_goods(self.posts[post.idx], self.dist))
            self.posts[post.idx] = self.dist

    def __lt__(self, other):
        return (self.dist < other.dist) or (self.dist == other.dist and self.goods < other.goods)

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result


class Game:
    def __init__(self):
        Socket.connect()
        self.player = None
        self.layers = [None] * 2
        self.ratings = dict()
        self.num_tick = 0

    def login(self, name='Cache me if you can'):
        Socket.send(Action.LOGIN, '{"name":"%s"}' % name)
        rec = Socket.receive()
        player_data = js.loads(rec.data)
        self.player = Player(player_data)

    def logout(self):
        Socket.send(Action.LOGOUT, '')
        Socket.close()

    def start_game(self):
        self.update_layer(0)
        self.update_layer(1)

    def next_move(self):
        for train_idx in self.player.trains_idx:
            train = self.layers[1].trains[train_idx]
            town = self.layers[1].posts[self.player.home]
            if train.cooldown == 0 and town.population > 0:
                line = self.layers[0].lines[train.line]
                time = town.product // town.population + 1
                mod = town.product % town.population
                if train.position == line.length:
                    self.get_next_line(train, line.point2, time, mod, PostType.MARKET.value, town)
                elif train.position == 0:
                    self.get_next_line(train, line.point1, time, mod, PostType.MARKET.value, town)


    def get_next_line(self, train, point, time, mod, post_type, town):
        paths = self.get_paths(point, town.point, post_type, train, time + min(1, mod))
        line = None
        if len(paths) > 0:
            paths_save = sorted([(goods, line) for dist, line, goods in paths if dist <= time],
                                          key=lambda x: -x[0])
            if len(paths_save) > 0:
                line = paths_save[0][1]
            else:
                paths_half_save = sorted([(goods, line) for dist, line, goods in paths if dist > time],
                                          key=lambda x: -x[0])
                line = paths_half_save[0][1]
        if line is not None:
            print(train.idx, line, self.layers[0].lines[train.line].train_idx)
            if self.layers[0].lines[train.line].train_idx == train.idx:
                self.layers[0].lines[train.line].train_idx = 0
            self.layers[0].lines[line].train_idx = train.idx
            self.layers[1].trains[train.idx].next_line = line
            self.move_train(line, self.layers[0].get_route(point, line), train.idx)
        else:
            self.move_train(train.line, 0, train.idx)

    def get_paths(self, point, town_idx, post_type, train, max_time):
        heap = []
        heappush(heap, Path(0, train.goods, point))
        out = list()
        list_adj = self.layers[0].list_adjacency
        max_point_goods = [-1]*len(self.layers[0].lines)

        while len(heap) > 0:
            path = heappop(heap)
            if path.dist > max_time:
                break

            post = self.layers[1].posts.get(path.point)
            if post is not None:
                if post.type == post_type:
                    new_path = deepcopy(path)
                    new_path.dist += 1
                    new_path.update(post, train.goods_capacity)
                    heappush(heap, new_path)

            for line in list_adj[path.point]:

                train_idx = self.layers[0].lines[line].train_idx
                if train_idx == 0 or train_idx == train.idx or path.point != point:
                    pass
                elif self.layers[1].trains[train_idx].next_line != line and self.layers[1].trains[train_idx].line != line:
                    self.layers[0].lines[line].train_idx = 0
                else:
                    continue

                point2 = self.layers[0].get_point2(line, path.point)
                new_path = deepcopy(path)
                new_path.dist += self.layers[0].lines[line].length
                new_path.point = point2

                post = self.layers[1].posts.get(point2)
                if post is not None:
                    if post.type == post_type:
                        new_path.update(post, train.goods_capacity)

                if max_point_goods[point2] < new_path.goods:
                    max_point_goods[point2] = new_path.goods
                else:
                    continue

                if new_path.start_line is None:
                    new_path.start_line = line

                if point2 == town_idx:
                    out.append((new_path.dist, new_path.start_line, new_path.goods))
                else:
                    heappush(heap, new_path)

        return out

    def move_train(self, line, speed, idx):
        print('{"line_idx":%s,"speed":%s,"train_idx":%s}' % (line, speed, idx))
        Socket.send(Action.MOVE, '{"line_idx":%s,"speed":%s,"train_idx":%s}' % (line, speed, idx))
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
                    self.layers[layer] = Layer1(data, self.player.idx)
                else:
                    self.layers[layer].update(data)
                    self.num_tick += 1
                self.update_ratings(data['ratings'])
                lines = ''
                for line in self.layers[0].lines:
                    if line is not None:
                        lines += '%d:%d; ' % (line.idx, line.train_idx)
                print(self.num_tick, lines)
                self.next_move()

    def update_ratings(self, ratings):
        for idx, rating in ratings.items():
            self.ratings[rating['idx']] = (rating['name'], rating['rating'])

    def tick(self):
        Socket.send(Action.TURN, '')
        rec = Socket.receive()
        self.update_layer(1)
