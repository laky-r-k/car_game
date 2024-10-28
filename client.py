import socket
import json

class server_client:
    def __init__(self) -> None:
        self.server="192.168.149.72"
        self.port=5555
        self.addr=("192.168.149.72",self.port)
        self.client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.client.connect(self.addr)
        print("Connected")
    def send(self,data):
        try:
            data=json.dump(data)
            self.client.sendall(str.encode(data))
        except:
            print("failed to send")
    
    def recive(self):
        data=self.client.recv(2048)
        data=data.decode()
        data=json.load(data)
        print(data)
        return data
"""while True:
    send("hello client here")
    recive()"""