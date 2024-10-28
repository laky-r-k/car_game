import socket
from _thread import start_new_thread

server="192.168.149.72"
port=5555
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
try:
    s.bind((server,port))
except socket.error as e:
    str(e)

s.listen(2)


print("waiting for connection")

def threaded_client(conn):
    reply=" "
    while True:
        try:
            data=conn.recv(2048)
            reply=data.decode("utf-8")
            if not data:
                print("disconnectd")
                break
            else:
                print("recieved:",reply)
                print("sending")
            conn.send(str.encode("hi how are you"))
        except:
            break
    print("connection lost")
    conn.close()
num=input("number of players")
i=0
run=True
conn_list=[]
while run:
    conn, addr = s.accept() 
    i+=1
    print("connected to : ",addr)
    #start_new_thread(threaded_client,(conn,))
    if i==num:
        run=False
for x in conn_list:
    start_new_thread(threaded_client,(x,))
    