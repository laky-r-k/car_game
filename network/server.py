# game_server.py
import socket
import threading
import json
import time
import uuid
from logic.gamelogic import GameLogic
from cars.car import Car

class GameThread(threading.Thread):
    """A dedicated thread to run a game session for two players."""
    def __init__(self, player1_conn, player1_addr, player2_conn, player2_addr):
        super().__init__()
        self.players = {
            1: {'conn': player1_conn, 'addr': player1_addr,"car":Car(90,[50,50])},#set initial car position
            2: {'conn': player2_conn, 'addr': player2_addr,"car":Car(90,[50,50])}
        }
        self.game_id = str(uuid.uuid4())
        self.running = True
        self.game=GameLogic(2,1)
        

    def broadcast(self, message_dict):
        """Sends a message to both players in the game."""
        message_json = json.dumps(message_dict).encode('utf-8')
        for player_id, player_data in self.players.items():
            try:
                player_data['conn'].sendall(message_json)
            except socket.error:
                print(f"[Game {self.game_id}] Player {player_id} disconnected.")
                self.running = False

    def handle_player_input(self, player_id):
        """Listens for input from a single player."""
        player_conn = self.players[player_id]['conn']
        self.game.register_player(player_id)
        
        while self.running:
            try:
                data = player_conn.recv(1024)
                if not data:
                    break
                
                message = json.loads(data.decode('utf-8'))
                print(f"[Game {self.game_id}] Received from Player {player_id}: {message}")
                self.players[player_id]['car'].position=message['pos']#message is dict containing angle pos and laps
                self.players[player_id]['car'].theta=message['angle']
                self.game.player_laps[player_id]=message['laps']
               
                    
                # For a real game, you'd update game state here.
                # For this example, we'll just forward the message.
                other_player_id = 2 if player_id == 1 else 1
                self.players[other_player_id]['conn'].sendall(data)
                if self.game.player_laps[player_id]==self.game.total_laps and self.game.player_laps[other_player_id]==self.game.total_laps:
                    self.game.state="game_over"
                    self.running=False

                
            except (socket.error, json.JSONDecodeError):
                print("error_occured>>disconnected")#can be from both player
                self.running = False
                return
        
        
        print(f"[Game {self.game_id}] Player {player_id} input handler stopped.")
    # In game_server.py -> GameThread class

    def run(self):
        """The main game loop."""
        print(f"[NEW GAME] Starting game {self.game_id} for {self.players[1]['addr']} and {self.players[2]['addr']}")
        
        # --- MODIFIED SECTION ---
        # Send a custom start message to each player
        for player_id, player_data in self.players.items():
            other_player_id = 2 if player_id == 1 else 1
            start_message = {
                "type": "start",
                "player_id": player_id, # Tell the client who they are
                "opponent_state": self.players[other_player_id]['car'].get_state(),
                "game_id": self.game_id,
                "message": f"Match found! You are Player {player_id}.",
                "laps": self.game.total_laps,
            }
            player_data['conn'].sendall(json.dumps(start_message).encode('utf-8'))
        # --- END MODIFIED SECTION ---

        self.game.start()
        self.broadcast({"type":"gamestate_update","gamestate":self.game.state})
        
        p1_input_thread = threading.Thread(target=self.handle_player_input, args=(1,))
        p2_input_thread = threading.Thread(target=self.handle_player_input, args=(2,))
        p1_input_thread.start()
        p2_input_thread.start()
        
        p1_input_thread.join()
        p2_input_thread.join()
        
        end_message = {"type":"end","gamestate":self.game.state, "message": "A player disconnected."}
        self.broadcast(end_message)

        for player_data in self.players.values():
            player_data['conn'].close()
            
        print(f"[GAME OVER] Game {self.game_id} has ended.")
    

class GameServer:
    def __init__(self, host="127.0.0.1", port=65432):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.lobby = [] # A list to hold a single waiting player
        self.lobby_lock = threading.Lock() # A lock to make lobby access thread-safe

    def _matchmaking(self, conn, addr):
        """Handles the matchmaking logic for a new client."""
        print(f"[LOBBY] {addr} has connected and is looking for a game.")
        conn.sendall(json.dumps({"type": "status", "message": "Connected to server, waiting for a match..."}).encode('utf-8'))
        
        player_to_match = None
        
        with self.lobby_lock:
            if self.lobby:
                # If there's a player waiting, match them
                player_to_match = self.lobby.pop(0)
            else:
                # If lobby is empty, this player must wait
                self.lobby.append((conn, addr))

        if player_to_match:
            # If a match was found, start a game thread
            p1_conn, p1_addr = player_to_match
            p2_conn, p2_addr = conn, addr
            game = GameThread(p1_conn, p1_addr, p2_conn, p2_addr)
            game.start()

    def start(self):
        """Binds the server and starts accepting connections."""
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"🏎️  Game server started on {self.host}:{self.port}")
        
        try:
            while True:
                conn, addr = self.server_socket.accept()
                # Each new connection is handled in its own thread for matchmaking
                thread = threading.Thread(target=self._matchmaking, args=(conn, addr))
                thread.start()
        except KeyboardInterrupt:
            print("\nServer is shutting down.")
        finally:
            self.server_socket.close()

if __name__ == "__main__":
    server = GameServer()
    server.start()