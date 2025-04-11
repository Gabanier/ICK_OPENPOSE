import socket

def create_message(direction: str)-> str:
    if direction == "None":
        return None
    
    map = {"Gora" : "w",
           "Dol" : "s",
           "Lewo" : "a",
           "Prawo" : "d",
           "Gora-Prawo" : "wd",
           "Gora-Lewo" : "wa",
           "Dol-Lewo" : "sa",
           "Dol-Prawo" : "sd"}
    
    if direction not in map.keys():
        print(f"Unsupported direction named {direction}!")
        return None

    string = "1" + map[direction]
    return string


class UDPClient:
    def __init__(self)-> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def send(self, address: str, port: str, message: str)-> None:
        print(f"Send data: {message}")
        self.socket.sendto(message.encode("utf-8"), (address, port))

