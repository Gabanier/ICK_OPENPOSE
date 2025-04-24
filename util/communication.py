import socket
from util import config


def create_message(direction: str)-> str:
    
    map = {"None" : "0000",
           "Gora" : "1000",
           "Dol" : "0100",
           "Lewo" : "0010",
           "Prawo" : "0001",
           "Gora-Prawo" : "1001",
           "Gora-Lewo" : "1010",
           "Dol-Lewo" : "0110",
           "Dol-Prawo" : "0101"}
    
    if direction not in map.keys():
        print(f"Unsupported direction named {direction}!")
        return None

    string = "1" + map[direction]
    return string


class UDPClient:
    def __init__(self)-> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def sendto(self, address: str, port: str, message: str)-> None:
        if config.DEBUG:
            print(f"Send data: {message}")
        self.socket.sendto(message.encode("utf-8"), (address, port))

