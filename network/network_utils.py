# test_client.py
import socket

HOST = "127.0.0.1"
PORT = 65432

print("--- Minimal Terminal Client ---")

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"Connecting to {HOST}:{PORT}...")
        s.connect((HOST, PORT))
        print("Connected!")
        
        message = input("Enter a message to send: ")
        
        print(f"Sending: '{message}'")
        s.sendall(message.encode('utf-8'))
        
        data = s.recv(1024)
        
        print(f"Received back from server: '{data.decode('utf-8')}'")

except ConnectionRefusedError:
    print("CONNECTION FAILED. Is the server running?")
except Exception as e:
    print(f"An error occurred: {e}")