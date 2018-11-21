import sys
import random
import warnings
import time
from forserver import *
from gui import *
from gamedetails import *
import atexit
warnings.filterwarnings('ignore')

def move_train():
    game.random_move(1)

class Application(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scenes = Scenes()
        self.sizes = Sizes()
        tick_button = QPushButton(self.scenes)
        tick_button.setText('Tick')
        tick_button.clicked.connect(move_train)
        self.setWindowTitle('Game')
        self.setCentralWidget(self.scenes)
        self.setGeometry(self.sizes.center[0] - self.sizes.x/2 - self.sizes.indent,
                         self.sizes.center[1] - self.sizes.y/2 - self.sizes.indent,
                         self.sizes.x + self.sizes.indent * 2, self.sizes.y + self.sizes.indent * 2)

    def update_layer(self, layer, data):
        self.scenes.update_layer(layer, data)

class Game:

    def __init__(self, pers='Rondondon'):
        Socket.connect()
        self.pers_name = pers
        self.pers_data = None
        self.app = Application()
        self.layers = [None]*2

    def login(self):
        Socket.send(Action.LOGIN, '{"name":"%s"}' % self.pers_name)
        self.pers_data = Socket.receive()

    def logout(self):
        Socket.send(Action.LOGOUT, '')
        Socket.close()

    def start_game(self):
        self.update_layer(0)
        self.update_layer(1)
        self.app.show()

    def random_move(self, idx):
        train = self.layers[1].trains[idx]
        length = self.layers[0].lines[train.line].length
        if train.position != 0 and train.position != length :
            self.move_train_forward(idx)
        else:
            if train.position == 0:
                point = self.layers[0].lines[train.line].point1
            else:
                point = self.layers[0].lines[train.line].point2
            lines = []
            for i, line in self.layers[0].lines.items():
                if line.point1 == point or line.point2 == point:
                    lines.append(i)
            line = lines[random.randint(0,len(lines)-1)]
            self.choose_train_line(idx, line)
    
    def move_train_forward(self, idx):
        train = self.layers[1].trains[idx]
        length = self.layers[0].lines[train.line].length
        if train.position != 0 and train.position != length :
            Socket.send(Action.MOVE, '{"line_idx":%s,"speed":%s,"train_idx":%s}' % (train.line, train.speed, idx))
            rec = Socket.receive()
            self.tick()

    def move_train_back(self, idx):
        train = self.layers[1].trains[idx]
        length = self.layers[0].lines[train.line].length
        if train.position != 0 and train.position != length :
            Socket.send(Action.MOVE, '{"line_idx":%s,"speed":%s,"train_idx":%s}' % (train.line, -train.speed, idx))
            rec = Socket.receive()
            self.tick()

    def stop_train(self, idx):
        train = self.layers[1].trains[idx]
        Socket.send(Action.MOVE, '{"line_idx":%s,"speed":%s,"train_idx":%s}' % (train.line, 0, idx))
        rec = Socket.receive()
        self.tick()

    def choose_train_line(self, idx, line_idx):
        train = self.layers[1].trains[idx]
        length = self.layers[0].lines[train.line].length
        line = self.layers[0].lines[line_idx]
        if train.position == 0 or train.position == length:
            if train.position == 0:
                    point = self.layers[0].lines[train.line].point1
            else :
                    point = self.layers[0].lines[train.line].point2
            if line.point1 == point:
                Socket.send(Action.MOVE, '{"line_idx":%s,"speed":%s,"train_idx":%s}' % (line_idx, 1, idx))
                rec = Socket.receive()
                self.tick()
            elif  line.point2 == point:
                Socket.send(Action.MOVE, '{"line_idx":%s,"speed":%s,"train_idx":%s}' % (line_idx, -1, idx))
                rec = Socket.receive()
                self.tick()

    def update_layer(self, layer):
        Socket.send(Action.MAP, '{"layer":%s}' % layer)
        rec = Socket.receive()
        if layer == 0:
            self.layers[layer] = Layer0(rec.data)
        elif layer == 1:
            self.layers[layer] = Layer1(rec.data)
        self.app.update_layer(layer, self.layers[layer])

    def tick(self):
        Socket.send(Action.TURN, '')
        rec = Socket.receive()
        self.update_layer(1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = Game()
    game.login()
    game.start_game()
    atexit.register(game.logout)
    sys.exit(app.exec_())