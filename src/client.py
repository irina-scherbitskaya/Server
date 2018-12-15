import socket
from enum import Enum

LITTLE = 'little'
SIZE_MSG = 4


# enumeration of actions for a request to server
class Action(Enum):
    LOGIN = 1
    LOGOUT = 2
    MOVE = 3
    UPGRADE = 4
    TURN = 5
    PLAYER = 6
    GAMES = 7
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


# class processes the message to send to server
class ActionMessage:

    def __init__(self, action, data_length, data):
        self.action = action
        self.data_length = data_length
        self.data = data
        self.msg_in_bytes = self.get_msg_in_bytes()

    def get_msg_in_bytes(self):
        bytes_action = self.action.value.to_bytes(SIZE_MSG, LITTLE)
        bytes_length = len(self.data).to_bytes(SIZE_MSG, LITTLE)
        return bytes_action + bytes_length + bytes(self.data, encoding='utf-8')


# class processes a response message from server
class ResponseMessage:

    def __init__(self, bytes_msg):
        self.result = Result.OKEY
        self.data_length = 0
        self.data = ''
        self.get_data(bytes_msg)

    def get_data(self, bytes_msg):
        self.result = int.from_bytes(bytes_msg[:SIZE_MSG], LITTLE)
        if len(bytes_msg) > SIZE_MSG:
            self.data_length = int.from_bytes(bytes_msg[SIZE_MSG:SIZE_MSG * 2], LITTLE)
            self.data = bytes_msg[SIZE_MSG * 2:].decode('utf-8')


class Socket:
    sock = socket.socket()
    HOST = 'wgforge-srv.wargaming.net'
    PORT = 443
    @staticmethod
    def connect():
        Socket.sock.connect((Socket.HOST, Socket.PORT))

    @staticmethod
    def send(action, data):
        msg = ActionMessage(action, len(data), data).get_msg_in_bytes()
        try:
            Socket.sock.send(msg)
        except:
            Socket.sock.connect((Socket.HOST, Socket.PORT))
            Socket.sock.send(msg)

    @staticmethod
    def receive():
        result = Socket.sock.recv(SIZE_MSG)
        msg = b''
        len_msg = Socket.sock.recv(SIZE_MSG)
        count = int.from_bytes(len_msg, LITTLE)
        while count > 0:
            msg += Socket.sock.recv(min(SIZE_MSG, count))
            count -= SIZE_MSG
        msg = ResponseMessage(result+len_msg+msg)
        print(msg.result)
        if msg.result != 0:
            print( msg.data)
        return msg

    @staticmethod
    def close():
        Socket.sock.close()

