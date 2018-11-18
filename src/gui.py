from PyQt5.QtCore import QLineF, QPointF, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QPainter, QRadialGradient, QPen
from PyQt5.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem,
                             QGridLayout, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QStyle)
from src.maps import *

size_x = 800
size_y = 650
indent = 10


#drawing graphs
class Graph(QGraphicsItem):
    def __init__(self, layer):
        super(Graph, self).__init__()
        self.new_poses = dict()
        self.layer = layer
        #new poses for drawing
        for idx, pos in layer.pos_points.items():
            self.new_poses[idx]= QPointF(pos[0]+size_x/2,pos[1]+size_y/2)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    def boundingRect(self):
        return QRectF(0, 0, size_x, size_y)

    def paint(self, painter, option, widget):
        print(len(self.new_poses))
        painter.setPen(QColor(0, 0, 0))
        painter.setBrush(QColor(221, 160, 221))
        for idx, line in self.layer.lines.items():
            point1 = self.new_poses[line.point1]
            point2 = self.new_poses[line.point2]
            painter.drawLine(point1, point2)
        for idx, point in self.new_poses.items():
            painter.drawEllipse(point, 30, 30)


class Application(QGraphicsView):

    def __init__(self):
        super(Application, self).__init__()
        self.maps = Map()
        self.center = None
        self.set_position()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setWindowTitle("Game")
        self.show()

    #set widgets on center of window with size = (800x600)
    def set_position(self):
        screen_geometry = QApplication.desktop().availableGeometry()
        screen_size = (screen_geometry.width(), screen_geometry.height())
        x = screen_size[0] / 2
        y = screen_size[1] / 2
        self.center = (x - size_x/2, y - size_y/2)
        self.setGeometry(x - size_x/2, y - size_y/2, size_x, size_y)
        self.setSceneRect(x - size_x/2 + indent, y - size_y/2 + indent, size_x - indent, size_y - indent)

    #add and draw layer
    def push_layer(self, layer, data):
        if layer == 0:
            self.maps.push_layer(Layer0(data))
            graph = Graph(self.maps.get_last())
            self.scene.addItem(graph)
            graph.setPos(self.center[0], self.center[1])
            self.update()

        elif layer == 1:
            self.maps.push_layer(Layer1(data))


