import matplotlib.image as mpimg
from enum import Enum
train_img = 'resource/train.png'


class PostType(Enum):
    TOWN = 1
    MARKET = 2
    STORAGE = 3


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


class Post:
    def __init__(self, post):
        self.type = PostType(post['type'])
        self.name = post['name']
        self.point = post['point_idx']