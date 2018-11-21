import sys
import warnings
import time
from client import *
from gui import *
from gamedetails import *
import atexit
warnings.filterwarnings('ignore')


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

    def move_train(self, idx, speed):
        train = self.layers[1].trains[idx]
        length = self.layers[0].lines[train.line].length
        if train.position != 0 and train.position != length :
            Socket.send(Action.MOVE, '{"line_idx":%s,"speed":%s,"train_idx":%s}' % (train.line, 2, idx))
            rec = Socket.receive()
        self.tick()

    def choose_train_line(self, idx, line):
        print(idx)
        train = self.layers[1].trains[idx]
        length = self.layers[0].lines[train.line].length
        if train.position == 0 or train.position == length:
            Socket.send(Action.MOVE, '{"line_idx":%s,"speed":%s,"train_idx":%s}' % (line, 1, idx))
            rec = Socket.receive()
        self.tick()

    def update_layer(self, layer):
        Socket.send(Action.MAP, '{"layer":%s}' % layer)
        rec = Socket.receive()
        if layer == 0:
            self.layers[layer] = Layer0(rec.data)
        elif layer == 1:
            self.layers[layer] = Layer1(rec.data)
            print(rec.data)
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
    QApplication.processEvents()
    game.move_train(1, 1)
    QApplication.processEvents()
    atexit.register(game.logout)
    sys.exit(app.exec_())