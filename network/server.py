# game_server.py
import pygame
import socket
import threading
import json
import time
import uuid
import struct
from queue import Queue

# NOTE: Make sure these import paths match your project structure
from logic.gamelogic import GameLogic
from logic.lapselogic import LapValidator
from logic.finishline import FinishLineDetector
from cars.car import Car
from players.player import Player

# ==============================================================================
# SECTION 1: SERVER-SIDE HELPER FUNCTIONS AND CLASSES
# ==============================================================================

def send_message(conn, data):
    """Encodes, prefixes, and sends a message."""
    try:
        message = json.dumps(data).encode('utf-8')
        len_prefix = struct.pack('>I', len(message))
        conn.sendall(len_prefix + message)
    except (socket.error, OSError): pass

def receive_message(conn):
    """Receives a complete length-prefixed message."""
    try:
        len_prefix = conn.recv(4);
        if not len_prefix: return None
        msg_len = struct.unpack('>I', len_prefix)[0]
        data = b'';
        while len(data) < msg_len:
            packet = conn.recv(msg_len - len(data));
            if not packet: return None
            data += packet
        return json.loads(data.decode('utf-8'))
    except (socket.error, struct.error, json.JSONDecodeError): return None

class ServerCarRepresentation:
    """A server-side helper to calculate a car's collision rect and mask."""
    def __init__(self, image_path):
        # Load the image to get its properties, but we won't blit it
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (self.original_image.get_width() // 2, self.original_image.get_height() // 2))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.top_left = (0, 0)
    
    def update(self, car_obj):
        """Rotates the image (in memory) to get the new mask and rect for collision."""
        rotated_image = pygame.transform.rotate(self.image, car_obj.theta)
        self.rect = rotated_image.get_rect(center=car_obj.position)
        self.mask = pygame.mask.from_surface(rotated_image)
        self.top_left = self.rect.topleft

# ==============================================================================
# SECTION 2: THE AUTHORITATIVE GAME THREAD
# ==============================================================================

class GameThread(threading.Thread):
    def __init__(self, player1_conn, player1_addr, player2_conn, player2_addr):
        super().__init__()
        # --- Standard setup ---
        self.game_state_lock = threading.Lock(); self.running = True
        self.game_id = str(uuid.uuid4()); self.input_queue = Queue()
        
        # --- Player and Car setup ---
        player1 = Player(name="Player 1"); player1.choose_car("assets/red-car.png")
        player1.car.position = [60, 140]; player1.car.theta = 90
        player2 = Player(name="Player 2"); player2.choose_car("assets/purple-car.png")
        player2.car.position = [60, 180]; player2.car.theta = 90
        self.players = { player1: {'conn': player1_conn}, player2: {'conn': player2_conn} }
        self.conn_to_player = { v['conn']: k for k, v in self.players.items() }

        # --- NEW: Initialize Game Logic and Assets on Server ---
        pygame.init() # Pygame needs to be initialized to use its modules
        self.game_logic = GameLogic(total_laps=3)
        track_border_img = pygame.image.load("assets/track-border.png")
        self.track_mask = pygame.mask.from_surface(track_border_img)
        finish_line_rect = pygame.Rect(21, 180, 65, 20)
        self.finish_line = FinishLineDetector(finish_line_rect)
        self.lap_validator = LapValidator((0, -1))
        self.server_cars = {
            player1: ServerCarRepresentation(player1.car_image_path),
            player2: ServerCarRepresentation(player2.car_image_path)
        }

    def broadcast(self, message_dict):
        for data in self.players.values(): send_message(data['conn'], message_dict)

    def handle_player_input(self, player_conn):
        player = self.conn_to_player[player_conn]
        while self.running:
            message = receive_message(player_conn)
            if message is None: break
            self.input_queue.put((player, message))
        self.running = False

    def run(self):
        print(f"[NEW GAME] Starting game {self.game_id}...")
        for player in self.players: self.game_logic.register_player(player)
        for data in self.players.values():
            threading.Thread(target=self.handle_player_input, args=(data['conn'],), daemon=True).start()

        # ... (Send initial 'start' message as before) ...
        self.game_logic.start()

        TICK_RATE = 30
        while self.running:
            start_time = time.time()
            # ... (Process inputs from queue as before) ...
            
            with self.game_state_lock:
                for player in self.players:
                    # 1. Update car physics
                    player.car.update_position()
                    
                    # 2. Update server-side representation for collision
                    car_rep = self.server_cars[player]
                    car_rep.update(player.car)

                    # 3. Check for wall collisions
                    if self.track_mask.overlap(car_rep.mask, car_rep.top_left):
                        player.car.bounce()

                    # 4. Check for lap completion
                    if self.finish_line.check(player, car_rep.rect):
                        if self.lap_validator.check(player):
                            self.game_logic.lap_completed(player)
                            print(f"[GAME LOGIC] {player.name} completed a lap!")
                    
                    # 5. Check for a winner
                    if self.game_logic.player_laps.get(player, 0) >= self.game_logic.total_laps:
                        print(f"[GAME OVER] {player.name} wins!")
                        self.running = False
            
            # ... (Broadcast game_state_packet as before) ...
            
            time_to_sleep = (1 / TICK_RATE) - (time.time() - start_time)
            if time_to_sleep > 0: time.sleep(time_to_sleep)

        # ... (Game over and cleanup as before) ...


class GameServer:
    def __init__(self, host="127.0.0.1", port=65432):
        self.host = host; self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.lobby = []; self.lobby_lock = threading.Lock()

    def _matchmaking(self, conn, addr):
        send_message(conn, {"type": "status", "message": "Connected, waiting for match..."})
        with self.lobby_lock:
            self.lobby.append((conn, addr))
            if len(self.lobby) >= 2:
                p1_conn, p1_addr = self.lobby.pop(0)
                p2_conn, p2_addr = self.lobby.pop(0)
                game = GameThread(p1_conn, p1_addr, p2_conn, p2_addr)
                game.start()

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"🏎️  Game server started on {self.host}:{self.port}")
        try:
            while True:
                conn, addr = self.server_socket.accept()
                threading.Thread(target=self._matchmaking, args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt: print("\nServer shutting down.")
        finally: self.server_socket.close()

if __name__ == "__main__":
    server = GameServer()
    server.start()