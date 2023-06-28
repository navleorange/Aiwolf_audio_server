import socket
import configparser
from . import util

class TCP:
    def __init__(self, inifile:configparser.ConfigParser) -> None:
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.host = inifile.get("connection","host")
        self.port = inifile.getint("connection","port")
        self.buffer = inifile.getint("connection","buffer")
        self.socket.bind((self.host,self.port))
        self.socket.listen(inifile.getint("game","player_num"))

    def accept(self) -> None:
        return self.socket.accept()
    
    def receive(self, socket, address) -> str:
        responses = b""

        while not util.is_json_complate(responces=responses):
            response = socket.recv(self.buffer)
            
            if response == b"":
                raise RuntimeError("socket connection broken")
            
            responses += response
        return responses.decode("utf-8")
    
    def receive_time_out(self, socket, address) -> str:
        responses = b""

        while not util.is_json_complate(responces=responses):
            try:
                response = socket.recv(self.buffer)
            except:
                return None
            
            if response == b"":
                raise RuntimeError("socket connection broken")
            
            responses += response

        return responses.decode("utf-8")
    
    def set_time_out(self, socket, address, time) -> None:
        socket.settimeout(time)
    
    def restore_time_out(self, socket, address) -> None:
        socket.setblocking(True)
    
    def send(self, socket, address, message:str) -> None:
        message += "\n"

        socket.send(message.encode("utf-8"))
    
    def conversation(self, socket, address, message) -> str:
        self.send(socket=socket, address=address, message=message)
        return self.receive(socket=socket, address=address)

    def close(self) -> None:
        #self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()