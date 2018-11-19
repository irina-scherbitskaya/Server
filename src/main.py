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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = Game()
    game.login()
    game.start_game()
    atexit.register(game.logout)
    sys.exit(app.exec_())