from PyQt5.QtCore import QLineF, QPointF, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QPainter, QRadialGradient, QPen, QFont
from PyQt5.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem,
                             QGridLayout, QVBoxLayout, QHBoxLayout, QWidget,
                             QLabel, QLineEdit, QPushButton, QStyle, QMainWindow)
from gamedetails import *
import atexit


# new poses for drawing
def ret_new_poses(pos_points):
    new_poses = dict()
    for idx, pos in pos_points.items():
        new_poses[idx] = QPointF(pos[0], pos[1])
    return new_poses


#set size for details
class Sizes:
    def __init__(self):
        self.x = QApplication.desktop().availableGeometry().width()*4/5
        self.y = QApplication.desktop().availableGeometry().height()*4/5
        self.center = (self.x*5/8, self.y*5/8)
        self.indent = self.y/30
        self.point = self.y/25
        self.train = self.y/30


#drawing graphs
class DrawGraph(QGraphicsItem):
    def __init__(self, layer):
        super(DrawGraph, self).__init__()
        self.new_poses = ret_new_poses(layer.pos_points)
        self.layer = layer
        self.sizes = Sizes()
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    def boundingRect(self):
        return QRectF(-self.sizes.x/2, -self.sizes.y/2, self.sizes.x, self.sizes.y)

    def paint(self, painter, option, widget):
        painter.setPen(QColor(0, 0, 0))
        painter.setBrush(QColor(221, 160, 221))
        for idx, line in self.layer.lines.items():
            point1 = self.new_poses[line.point1]
            point2 = self.new_poses[line.point2]
            painter.drawLine(point1, point2)
        for idx, point in self.new_poses.items():
            painter.drawRect(point.x() - self.sizes.point, point.y() - self.sizes.point,
                             2*self.sizes.point, 2*self.sizes.point)

    def update_layer0(self, layer):
        self.layer = layer


#drawing posts and trains
class DrawDetails(QGraphicsItem):
    def __init__(self, layer0, layer1):
        super(DrawDetails, self).__init__()
        self.new_poses = ret_new_poses(layer0.pos_points)
        self.layer1 = layer1
        self.layer0 = layer0
        self.sizes = Sizes()
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    def boundingRect(self):
        return QRectF(-self.sizes.x/2, -self.sizes.y/2, self.sizes.x, self.sizes.y)

    def paint(self, painter, option, widget):
        painter.setPen(QColor(0, 0, 0))
        painter.setFont(QFont('Times', 6))
        self.draw_post(painter, option, widget)
        self.draw_train(painter, option, widget)

    def draw_post(self, painter, option, widget):
        for idx, post in self.layer1.posts.items():
            point = self.new_poses[post.point]
            painter.setBrush(QColor(post.color))
            #set rect for text
            painter.drawRect(point.x() - self.sizes.point, point.y() - self.sizes.point,
                             2*self.sizes.point, 2*self.sizes.point)
            #output of the info of the post
            painter.drawText(QRectF(point.x() - self.sizes.point + 2, point.y() - self.sizes.point + 2,
                                    self.sizes.point*2, self.sizes.point*2),  post.tostring())

    def draw_train(self, painter, option, widget):
        for idx, train in self.layer1.trains.items():
            line = self.layer0.lines[train.line]
            x1, x2 = self.new_poses[line.point1].x(), self.new_poses[line.point2].x()
            x = x1 - train.position * (x1 - x2) / line.length
            y1, y2 = self.new_poses[line.point1].y(), self.new_poses[line.point2].y()
            y = y1 - train.position*(y1-y2)/line.length
            painter.drawEllipse(QPointF(x, y), self.sizes.train, self.sizes.train)

    def update_layer1(self, layer):
        self.layer1 = layer
        self.update()


class Scenes(QGraphicsView):
    def __init__(self):
        super(Scenes, self).__init__()
        self.center = None
        self.flag_start_game = False
        self.sizes = Sizes()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.game = Game()
        self.sceneItems = [None]*2
        self.setSceneRect(self.sizes.center[0] - self.sizes.x/2,
                          self.sizes.center[1] - self.sizes.y/2,
                          self.sizes.x, self.sizes.y)

    #add and draw layer
    def update_layer(self, layer):

        if layer == 0:
            if (self.sceneItems[0]):
                self.sceneItems[0].update_layer0(self.game.layers[0])
            else:
                graph = DrawGraph(self.game.layers[0])
                self.sceneItems[0] = graph
                self.scene.addItem(graph)
                graph.setPos(self.sizes.center[0], self.sizes.center[1])

        elif layer == 1:
            if (self.sceneItems[1]):
                self.sceneItems[1].update_layer1(self.game.layers[1])
            else:
                details = DrawDetails(self.game.layers[0], self.game.layers[1])
                self.sceneItems[1] = details
                self.scene.addItem(details)
                details.setPos(self.sizes.center[0], self.sizes.center[1])

        self.update()

    def move_train(self):
        if self.flag_start_game:
            self.game.random_move(1)
            self.update_layer(1)

    def start_game(self):
        if not self.flag_start_game:
            self.game.login()
            self.game.start_game()
            self.update_layer(0)
            self.update_layer(1)
        self.flag_start_game = True


class Application(QMainWindow):
    def __init__(self):
        super().__init__()
        #create main var and set main attr
        self.win = QWidget()
        self.scenes = Scenes()
        self.sizes = Sizes()
        self.setWindowTitle('Game')
        self.setGeometry(self.sizes.center[0] - self.sizes.x/ 2 - self.sizes.indent*2,
                         self.sizes.center[1] - self.sizes.y/ 2 - self.sizes.indent*2,
                         self.sizes.x + self.sizes.indent * 4, self.sizes.y + self.sizes.indent * 4)
        # layout
        self.setCentralWidget(self.win)
        self.main_vbox = QVBoxLayout()
        self.main_vbox.addWidget(self.scenes)
        #create buttons
        self.set_button()
        self.win.setLayout(self.main_vbox)

        self.show()

    def set_button(self):
        hbox = QHBoxLayout()
        hbox.addStretch(1)

        tick_button = QPushButton('Tick')
        tick_button.clicked.connect(self.scenes.move_train)
        start_button = QPushButton('Start game')
        start_button.clicked.connect(self.scenes.start_game)

        hbox.addWidget(tick_button)
        hbox.addWidget(start_button)
        self.main_vbox.addLayout(hbox)

    def closeEvent(self, QCloseEvent):
        atexit.register(self.scenes.game.logout)
        self.close()

