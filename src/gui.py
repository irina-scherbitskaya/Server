from PyQt5.QtCore import QLineF, QPointF, QRectF, Qt, QTimer
from PyQt5.QtGui import QBrush, QColor, QPainter, QRadialGradient, QPen, QFont
from PyQt5.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem,
                             QGridLayout, QVBoxLayout, QHBoxLayout, QWidget,
                             QLabel, QLineEdit, QPushButton, QStyle, QMainWindow)
from gamedetails import *

SLEEP_TIME = 10000


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
        self.indent = self.y/15
        self.point = self.y/50
        self.train = self.y/60
        self.rad = self.y/100


#drawing graphs
class DrawGraph(QGraphicsItem):
    def __init__(self, layer):
        super(DrawGraph, self).__init__()
        self.new_poses = ret_new_poses(layer.pos_points)
        self.layer = layer
        self.sizes = Sizes()

    def boundingRect(self):
        return QRectF(-self.sizes.x/2, -self.sizes.y/2, self.sizes.x, self.sizes.y)

    def paint(self, painter, option, widget):
        painter.setPen(QColor(0, 0, 0))
        painter.setFont(QFont('Times', 5))
        painter.setBrush(QColor(255, 255, 255))
        for line in self.layer.lines:
            if line is not None:
                point1 = self.new_poses[line.point1]
                point2 = self.new_poses[line.point2]
                painter.drawLine(point1, point2)
                x1, x2 = self.new_poses[line.point1].x(), self.new_poses[line.point2].x()
                x = x1 - (x1 - x2) / 2
                y1, y2 = self.new_poses[line.point1].y(), self.new_poses[line.point2].y()
                y = y1 - (y1 - y2) / 2
                painter.drawEllipse(QPointF(x, y), self.sizes.rad, self.sizes.rad)
                painter.drawText(x - self.sizes.rad/4, y + self.sizes.rad/4, '%d' % line.length)
                painter.drawText(x - self.sizes.rad * 3, y - self.sizes.rad * 3, '%d' % line.idx)
        painter.setBrush(QColor(221, 160, 221))
        for idx, point in self.new_poses.items():
            painter.drawRect(point.x() - self.sizes.point, point.y() - self.sizes.point,
                                 2*self.sizes.point, 2*self.sizes.point)
            painter.drawText(point.x() - self.sizes.rad*3, point.y() - self.sizes.rad *3, '%d' % idx)


#drawing posts and trains
class DrawDetails(QGraphicsItem):
    def __init__(self, layer0, layer1):
        super(DrawDetails, self).__init__()
        self.new_poses = ret_new_poses(layer0.pos_points)
        self.layer1 = layer1
        self.layer0 = layer0
        self.sizes = Sizes()

    def boundingRect(self):
        return QRectF(-self.sizes.x/2, -self.sizes.y/2, self.sizes.x, self.sizes.y)

    def paint(self, painter, option, widget):
        painter.setPen(QColor(0, 0, 0))
        painter.setFont(QFont('Times', 4))
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
            painter.setBrush(QColor(train.color))
            line = self.layer0.lines[train.line]
            x1, x2 = self.new_poses[line.point1].x(), self.new_poses[line.point2].x()
            x = x1 - train.position * (x1 - x2) / line.length
            y1, y2 = self.new_poses[line.point1].y(), self.new_poses[line.point2].y()
            y = y1 - train.position*(y1-y2)/line.length
            painter.drawRect(x - self.sizes.train, y - self.sizes.train, self.sizes.train*2, self.sizes.train*2)
            painter.drawText(QRectF(x - self.sizes.train + 2, y - self.sizes.train + 2, self.sizes.train*2,
                                    self.sizes.train*2), train.tostring())


class DrawInfo(QGraphicsItem):
    def __init__(self, ratings, num_tick):
        super(DrawInfo, self).__init__()
        self.sizes = Sizes()
        self.rect = QRectF(- self.sizes.x/2 , - self.sizes.y/2,
                            self.sizes.x , self.sizes.y )
        self.ratings = ratings
        self.tick = num_tick

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget):
        painter.setPen(QColor(50, 40, 160))
        painter.setFont(QFont('Times', 10))
        self.tick += 1
        label = 'Tick:%d\nRating:\n' % self.tick
        for idx, rating in self.ratings.items():
            label = label + '%s:%d\n' % (rating[0], rating[1])

        painter.drawText(self.rect, label)


class Scenes(QGraphicsView):
    def __init__(self):
        super(Scenes, self).__init__()
        self.center = None
        self.flag_start_game = False
        self.sizes = Sizes()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.game = Game()
        self.sceneItems = [None]*3
        self.setSceneRect(self.sizes.center[0] - self.sizes.x/2,
                          self.sizes.center[1] - self.sizes.y/2,
                          self.sizes.x, self.sizes.y)
        self.timer = QTimer()
        self.timer.timeout.connect(self.time_update)
        self.timer.setInterval(SLEEP_TIME)

    def add_item(self, idx, item, pos):
        self.sceneItems[idx] = item
        self.scene.addItem(item)
        item.setPos(pos[0], pos[1])

    #add and draw layer
    def update_layer(self, layer):
        if layer == 0:
            if self.sceneItems[0] is None:
                self.add_item(0, DrawGraph(self.game.layers[0]), self.sizes.center)
        elif layer == 1:
            if self.sceneItems[1] is None:
                self.add_item(1, DrawDetails(self.game.layers[0], self.game.layers[1]), self.sizes.center)
                self.add_item(2, DrawInfo(self.game.ratings, self.game.num_tick), self.sizes.center)
            self.sceneItems[2].update()

        self.sceneItems[layer].update()
        self.update()

    def tick(self):
        if self.flag_start_game:
            self.timer.stop()
            self.game.tick()
            self.timer.start()
            self.update_layer(1)

    def start_game(self):
        if not self.flag_start_game:
            self.game.login()
            self.game.start_game()
            self.timer.start()
            self.update_layer(0)
            self.update_layer(1)
        self.flag_start_game = True

    def time_update(self):
        self.game.update_layer(1)
        self.game.next_move()
        self.update_layer(1)
        self.timer.start()


class Application(QMainWindow):
    def __init__(self):
        super().__init__()
        #create main var and set main attr
        self.win = QWidget()
        self.scenes = Scenes()
        self.sizes = Sizes()
        self.setWindowTitle('Game')
        self.setGeometry(self.sizes.center[0] - self.sizes.x/2 - self.sizes.indent,
                         self.sizes.center[1] - self.sizes.y/2 - self.sizes.indent,
                         self.sizes.x + self.sizes.indent * 2, self.sizes.y + self.sizes.indent * 2)
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
        tick_button.clicked.connect(self.scenes.tick)
        start_button = QPushButton('Start game')
        start_button.clicked.connect(self.scenes.start_game)

        hbox.addWidget(tick_button)
        hbox.addWidget(start_button)
        self.main_vbox.addLayout(hbox)

    def closeEvent(self, QCloseEvent):
        self.scenes.game.logout()
        self.close()


