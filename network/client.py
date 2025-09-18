# game_client.py
import socket
import threading
import json
import struct

# NOTE: Make sure these import paths match your project structure
from cars.car import Car
from players.player import Player
from logic.gamelogic import GameLogic

# ==============================================================================
# SECTION 1: NETWORKING HELPER FUNCTIONS
# ==============================================================================

def send_message(conn, data_dict):
    """
    Serializes a dictionary to JSON, prefixes it with its length, and sends it.
    """
    message = json.dumps(data_dict).encode('utf-8')
    # Prepend the message with a 4-byte length (big-endian unsigned int)
    len_prefix = struct.pack('>I', len(message))
    conn.sendall(len_prefix + message)

def receive_message(conn):
    """
    Receives a length-prefixed JSON message.
    """
    # Read the 4-byte length prefix
    len_prefix = conn.recv(4)
    if not len_prefix:
        return None
    msg_len = struct.unpack('>I', len_prefix)[0]
    
    # Read the full message in a loop to ensure all data is received
    data = b''
    while len(data) < msg_len:
        packet = conn.recv(msg_len - len(data))
        if not packet:
            return None
        data += packet
    return json.loads(data.decode('utf-8'))

# ==============================================================================
# SECTION 2: THE GAME CLIENT CLASS
# ==============================================================================

class GameClient:
    def __init__(self, host="127.0.0.1", port=65432):
        """Initializes the networking component of the client."""
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True
        
        self.me = None
        self.opponent = None
        self.game_logic = GameLogic()

    def _listen_for_messages(self):
        """
        Runs on a background thread. Its only job is to receive data from
        the server and update the local game state.
        """
        while self.running:
            try:
                # CORRECTED: Use the helper function to reliably receive one full message.
                # This fixes the UnicodeDecodeError and JSONDecodeError.
                message = receive_message(self.client_socket)
                
                if message is None: # Server disconnected gracefully
                    self.running = False
                    break
                
                msg_type = message.get("type")

                if msg_type == "start":
                    self.me = Player(name=message['your_name'])
                    self.me.choose_car(message['your_car_image'])
                    self.opponent = Player(name=message['opponent_name'])
                    self.opponent.choose_car(message['opponent_car_image'])
                    initial_states = message['initial_state']
                    self.me.car.set_state(initial_states[self.me.name])
                    self.opponent.car.set_state(initial_states[self.opponent.name])
                    self.game_logic.register_player(self.me)
                    self.game_logic.register_player(self.opponent)
                    print(f"[SERVER] {message.get('message', 'Game starting!')}")

                elif msg_type == "game_update":
                    states = message['states']
                    laps = message['laps']
                    if self.me and self.me.name in states:
                        self.me.car.set_state(states[self.me.name])
                        self.game_logic.player_laps[self.me] = laps.get(self.me.name, 0)
                    if self.opponent and self.opponent.name in states:
                        self.opponent.car.set_state(states[self.opponent.name])
                        self.game_logic.player_laps[self.opponent] = laps.get(self.opponent.name, 0)
                
                elif msg_type == "end":
                    print(f"\n[SERVER] {message.get('message', 'Game over.')}")
                    self.running = False
            
            except (socket.error, struct.error):
                if self.running:
                    print("\n[ERROR] Connection lost.")
                self.running = False
                break

    def send_inputs(self, keys_pressed_dict):
        """
        Sends the player's keyboard inputs to the server using the framing protocol.
        """
        if self.running:
            try:
                payload = { "keys": keys_pressed_dict }
                # CORRECTED: Use the helper function to reliably send one full message.
                send_message(self.client_socket, payload)
            except socket.error:
                self.running = False

    def start_networking(self):
        """Connects to the server and starts the listening thread."""
        try:
            self.client_socket.connect((self.host, self.port))
            listener = threading.Thread(target=self._listen_for_messages, daemon=True)
            listener.start()
            print("✅ Client connected to server.")
            return True
        except ConnectionRefusedError:
            print("❌ Could not connect to the server.")
            self.running = False
            return False

    def disconnect(self):
        """Shuts down the client."""
        self.running = False
        if self.client_socket:
            self.client_socket.close()
        print("Connection closed.")