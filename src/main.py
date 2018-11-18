import sys
import warnings
from src.forserver import *
from src.gui import *
warnings.filterwarnings('ignore')


#details of games
class Game:

    def __init__(self, pers='Rondondon'):
        Socket.connect()
        self.pers_name = pers
        self.pers_data = None
        self.app = Application()

    def login(self):
        Socket.send(Action.LOGIN, '{"name":"%s"}' % self.pers_name)
        self.pers_data = Socket.receive()

    def get_maps(self):
        Socket.send(Action.MAP, '{"layer":0}')
        rec = Socket.receive()
        self.app.push_layer(0, rec.data)
        #Socket.send(Action.MAP, '{"layer":1}')
        #rec = Socket.receive()
        #self.app.maps.push_layer(1, rec.data)
        #self.app.show()

    def game_update(self):
        sys.exit(self.app.exec_())

    def end(self):
        Socket.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = Game()
    game.login()
    game.get_maps()

    sys.exit(app.exec_())
