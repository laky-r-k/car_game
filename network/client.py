# game_client.py
import socket
import threading
import json
import time
from cars.car import Car
from logic.gamelogic import GameLogic

class GameClient:
    def __init__(self, host="127.0.0.1", port=65432):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True
        
        # All game state is managed here
        self.player_id = None
        self.opponent_id = None
        self.my_car = Car(90, [60, 140]) # Set a default start position
        self.opponent_car = Car(90, [60, 140])
        self.game_logic = GameLogic()

    def _listen_for_messages(self):
        """Runs on a background thread to handle all incoming server messages."""
        while self.running:
            try:
                # This part is the same as our previous version
                data = self.client_socket.recv(1024)
                if not data: self.running = False; break
                
                message = json.loads(data.decode('utf-8'))
                msg_type = message.get("type")

                if msg_type == "start":
                    self.player_id = message['player_id']
                    self.opponent_id = 2 if self.player_id == 1 else 1
                    # Important: Update both your car and opponent's car with server start state
                    if self.player_id == 1:
                        self.my_car.position = [60, 140]
                        self.opponent_car.position = [60, 180] # Stagger start pos
                    else:
                        self.my_car.position = [60, 180]
                        self.opponent_car.position = [60, 140]

                    self.game_logic.total_laps = message['laps']
                    self.game_logic.register_player(self.player_id)
                    self.game_logic.register_player(self.opponent_id)
                    print(f"[SERVER] {message.get('message')}")

                elif msg_type == "gamestate_update":
                    self.game_logic.state = message.get('gamestate')
                
                elif msg_type == "end":
                    self.running = False
                
                else: # Opponent state update
                    self.opponent_car.position = message.get('pos', self.opponent_car.position)
                    self.opponent_car.theta = message.get('angle', self.opponent_car.theta)
                    
                    self.game_logic.player_laps[self.opponent_id] = message.get('laps', 0)

            except (socket.error, json.JSONDecodeError):
                if self.running: self.running = False
                break

    def send_state(self):
        """Sends the current state of this client's car to the server."""
        if self.running:
            try:
                payload = {
            "pos": self.my_car.position,
            "angle": self.my_car.theta,
            "laps": self.game_logic.player_laps.get(self.player_id, 0)
        }
                self.client_socket.sendall(json.dumps(payload).encode('utf-8'))
            except socket.error:
                self.running = False

    def start_networking(self):
        """Connects to the server and starts the listening thread."""
        try:
            self.client_socket.connect((self.host, self.port))
            listener = threading.Thread(target=self._listen_for_messages, daemon=True)
            listener.start()
            return True
        except ConnectionRefusedError:
            print("❌ Could not connect to the server.")
            self.running = False
            return False

    def disconnect(self):
        self.running = False
        self.client_socket.close()
        print("Connection closed.")