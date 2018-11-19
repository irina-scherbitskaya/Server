from PyQt5.QtCore import QLineF, QPointF, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QPainter, QRadialGradient, QPen, QFont
from PyQt5.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem,
                             QGridLayout, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QStyle)

size_x = 800
size_y = 650
indent = 20
size_point = 30


# new poses for drawing
def ret_new_poses(pos_points):
    new_poses = dict()
    for idx, pos in pos_points.items():
        new_poses[idx] = QPointF(pos[0] + size_x / 2, pos[1] + size_y / 2)
    return new_poses


#drawing graphs
class DrawGraph(QGraphicsItem):
    def __init__(self, layer):
        super(DrawGraph, self).__init__()
        self.new_poses = ret_new_poses(layer.pos_points)
        self.layer = layer
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    def boundingRect(self):
        return QRectF(0, 0, size_x, size_y)

    def paint(self, painter, option, widget):
        painter.setPen(QColor(0, 0, 0))
        painter.setBrush(QColor(221, 160, 221))
        for idx, line in self.layer.lines.items():
            point1 = self.new_poses[line.point1]
            point2 = self.new_poses[line.point2]
            painter.drawLine(point1, point2)
        for idx, point in self.new_poses.items():
            painter.drawRect(point.x() - size_point, point.y() - size_point,
                             2*size_point,2*size_point)


#drawing posts and trains
class DrawDetails(QGraphicsItem):
    def __init__(self, layer0, layer1):
        super(DrawDetails, self).__init__()
        self.new_poses = ret_new_poses(layer0.pos_points)
        self.layer1 = layer1
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    def boundingRect(self):
        return QRectF(0, 0, size_x, size_y)

    def paint(self, painter, option, widget):

        painter.setPen(QColor(0, 0, 0))
        painter.setFont(QFont('Times', 10))
        for idx, post in self.layer1.posts.items():
            point = self.new_poses[post.point]
            painter.setBrush(QColor(post.color))
            #set rect for text
            painter.drawRect(point.x() - size_point, point.y() - size_point,
                             2*size_point, 2*size_point)
            #output of the info of the post
            painter.drawText(QRectF(point.x() - size_point + 2, point.y() - size_point + 2,
                             point.x() + size_point,point.y() + size_point),  post.tostring())


class Application(QGraphicsView):

    def __init__(self):
        super(Application, self).__init__()
        self.center = None
        self.set_position()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setWindowTitle("Game")
        self.layers = [None]*2

    #set widgets on center of window with size = (800x600)
    def set_position(self):
        screen_geometry = QApplication.desktop().availableGeometry()
        screen_size = (screen_geometry.width(), screen_geometry.height())
        x = screen_size[0] / 2
        y = screen_size[1] / 2
        self.center = (x - size_x/2, y - size_y/2)
        self.setGeometry(x - size_x/2, y - size_y/2, size_x, size_y)
        self.setSceneRect(x - size_x/2 + indent, y - size_y/2 + indent, size_x - indent, size_y - indent)


    def add_item(self, item):
        pass

    #add and draw layer
    def update_layer(self, layer, data):
        self.layers[layer] = data
        if layer == 0:
            graph = DrawGraph(data)
            self.scene.addItem(graph)
            graph.setPos(self.center[0], self.center[1])

        elif layer == 1:
            details = DrawDetails(self.layers[0], self.layers[1])
            self.scene.addItem(details)
            details.setPos(self.center[0], self.center[1])

        self.update()


