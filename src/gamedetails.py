import matplotlib.image as mpimg

train_img = 'resource/train.png'


class Train:
    def __init__(self, train):
        self.line = train['line_idx']
        self.position = train['position']
        self.speed = train['speed']
        self.img = mpimg.imread(train_img, 'png')


class Point:
    def __init__(self, pos):
        self.pos_x = pos[0]
        self.pos_y = pos[1]


class Line:
    def __init__(self, point):
        self.point1 = point[0]
        self.point2 = point[1]