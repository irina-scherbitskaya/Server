import sys
import warnings
from forserver import *
from gui import *
from gamedetails import *
import atexit
warnings.filterwarnings('ignore')


#details of games
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
    def move_train(self, indx, speed):
        train = self.layers[1].trains[indx]
        length = self.layers[0].lines[train.line].length
        if(train.position != 0 and train.position != length):
            Socket.send(Action.MOVE, '{"line_idx":%s,"speed":%s,"train_idx":%s}' % (train.line, speed, indx))
            rec = Socket.receive()
    def choose_train_line(self, indx, line):
        train = self.layers[1].trains[indx]
        length = self.layers[0].lines[train.line].length
        if(train.position == 0 or train.position == length):
            Socket.send(Action.MOVE, '{"line_idx":%s,"speed":%s,"train_idx":%s}' % (line, 1, indx))
            rec = Socket.receive()
    def update_layer(self, layer):
        Socket.send(Action.MAP, '{"layer":%s}' % layer)
        rec = Socket.receive()
        if layer == 0:
            self.layers[layer] = Layer0(rec.data)
        elif layer ==1:
            self.layers[layer] = Layer1(rec.data)
        self.app.update_layer(layer, self.layers[layer])

    def tick(self):
        Socket.send(Action.TURN,'')
        rec = Socket.receive()
        self.update_layer(1)

    def game_update(self):
        sys.exit(self.app.exec_())

    def end(self):
        Socket.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = Game()
    game.login()
    game.start_game()
    game.choose_train_line(1,1)
    game.tick()
    for x in range(9):
        game.move_train(1,1)
        game.tick()
    game.choose_train_line(1,7)
    game.tick()
    for x in range(9):
        game.move_train(1,1)
        game.tick()
    game.choose_train_line(1,8)
    game.tick()
    for x in range(9):
        game.move_train(1,1)
        game.tick()
    game.choose_train_line(1,9)
    game.tick()
    for x in range(9):
        game.move_train(1,1)
        game.tick()
    game.choose_train_line(1,10)
    game.tick()
    for x in range(5):
        game.move_train(1,1)
        game.tick()
    atexit.register(game.logout)
    sys.exit(app.exec_())