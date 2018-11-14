import json as js
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import networkx as nx
import tkinter as tk
import warnings
import socket
from enum import Enum

warnings.filterwarnings('ignore')


# enumeration of actions for a request to server
class Action(Enum):
    LOGIN = 1
    LOGOUT = 2
    MOVE = 3
    UPGRADE = 4
    TURN = 5
    PLAYER = 6
    MAP = 10


# enumeration of results of server
class Result(Enum):
    OKEY = 0
    BAD_COMMAND = 1
    RESOURCE_NOT_FOUND = 2
    ACCESS_DENIED = 3
    NOT_READY = 4
    TIMEOUT = 5
    INTERNAL_SERVER_ERROR = 500


# draws a graph using pyplot
class Drawing:
    def __init__(self, maps):
        self.idx = 0
        self.fig = plt.gcf()
        self.fig.set_size_inches(10, 6)
        self.list_map = []
        for map in maps:
            self.push_map(map)

    def push_map(self, json_str):
        self.list_map.append(self.parse_map(json_str))

    def drawing_map(self, canvas):
        self.fig.clear()
        G = self.list_map[self.idx]
        labels = nx.get_edge_attributes(G, 'weight')
        pos = nx.kamada_kawai_layout(G, weight=None)
        nx.draw_networkx_edge_labels(G, pos, font_size=8, edge_labels=labels)
        nx.draw_networkx(G, pos=pos, node_color='#DDA0DD', with_labels=True, font_size=8, node_size=200)
        canvas.draw_idle()

    def parse_map(self, json_str):
        data = js.loads(json_str)
        G = nx.Graph()
        G.add_nodes_from([v['idx'] for v in data['points']])
        G.add_weighted_edges_from([(e['points'][0], e['points'][1], e['length']) for e in data['lines']])
        return G

    def drawing_next_map(self, canvas):
        if len(self.list_map) - 1 > self.idx > -1:
            self.idx += 1
            self.drawing_map(canvas)

    def drawing_last_map(self, canvas):
        if len(self.list_map) - 1 > self.idx > 0:
            self.idx -= 1
            self.drawing_map(canvas)


# creates gui
class Application(tk.Tk):
    def __init__(self, maps):
        tk.Tk.__init__(self)
        self.configure(bg='white')
        self.title('Drawing graph')
        self.map = Drawing(maps)
        self.create_widgets()
        self.destroy_flag = True
        self.protocol('WM_DELETE_WINDOW', self.destroy_window)

    def destroy_window(self):
        self.destroy_flag = False
        self.destroy()

    def last_graph(self):
        self.map.drawing_last_map(self.canvas)

    def next_graph(self):
        self.map.drawing_next_map(self.canvas)

    def create_widgets(self):
        self.canvas = FigureCanvasTkAgg(self.map.fig, master=self)
        self.create_buttons()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.map.drawing_map(self.canvas)
        self.canvas.draw()

    def create_buttons(self):
        self.frame = tk.Frame(self)
        button_next = tk.Button(master=self.frame, text="Next graph", command=self.next_graph, font='arial 15',
                                bg='white')
        button_next.pack(side=tk.RIGHT, anchor=tk.W)
        button_last = tk.Button(master=self.frame, text="Last graph", command=self.last_graph, font='arial 15',
                                bg='white')
        button_last.pack(side=tk.LEFT, anchor=tk.W)
        self.frame.pack(side=tk.BOTTOM)


# class processes the message to send to server
class ActionMessage:

    def __init__(self, action, data_length, data):
        self.action = action
        self.data_length = data_length;
        self.data = data

    def get_msg_of_bytes(self):
        bytes_action = self.action.value.to_bytes(4, 'little')
        bytes_length = len(self.data).to_bytes(4, 'little')
        return bytes_action + bytes_length + bytes(self.data, encoding='utf-8')


# class processes a response message from server
class ResponseMessage:

    def __init__(self, bytes_msg):
        self.result = Result.OKEY
        self.data_length = 0
        self.data = ''
        self.get_data(bytes_msg)

    def get_data(self, bytes_msg):
        size = 4
        self.result = int.from_bytes(bytes_msg[:size], 'little')
        if len(bytes_msg) > 4:
            self.data_length = int.from_bytes(bytes_msg[size:size * 2], 'little')
            self.data = bytes_msg[size * 2:].decode('utf-8')


# working with server
class Socket:
    sock = socket.socket()
    host = 'wgforge-srv.wargaming.net'
    port = 443

    @staticmethod
    def connect():
        Socket.sock.connect((Socket.host, Socket.port))

    @staticmethod
    def send(action, data):
        msg = ActionMessage(action, len(data), data).get_msg_of_bytes()
        try:
            Socket.sock.send(msg)
        except:
            Socket.sock.connect((Socket.host, Socket.port))
            Socket.sock.send(msg)

    @staticmethod
    def receive():
        result = Socket.sock.recv(4)
        len_msg = b''
        msg = b''
        if int.from_bytes(result, 'little') == 0:
            len_msg = Socket.sock.recv(4)
            count = int.from_bytes(len_msg, 'little')
            while count > 0:
                msg += Socket.sock.recv(min(4, count))
                count -= 4
        return ResponseMessage(result+len_msg+msg)

    @staticmethod
    def close():
        Socket.sock.close()


if __name__ == "__main__":
    Socket.connect()
    Socket.send(Action.LOGIN, '{"name":"Begemotik"}')
    pers = Socket.receive()
    Socket.send(Action.MAP, '{"layer":0}')
    map = Socket.receive()
    app = Application([map.data])

    while app.destroy_flag:
       app.update()

    Socket.close()
