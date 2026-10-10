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
# SECTION 1: NETWORKING HELPER FUNCTIONS AND CLASSES
# ==============================================================================

def send_message(conn, data):
    try:
        message = json.dumps(data).encode('utf-8')
        len_prefix = struct.pack('>I', len(message))
        conn.sendall(len_prefix + message)
    except (socket.error, OSError): pass

def receive_message(conn):
    try:
        len_prefix = conn.recv(4)
        if not len_prefix: return None
        msg_len = struct.unpack('>I', len_prefix)[0]
        data = b''
        while len(data) < msg_len:
            packet = conn.recv(msg_len - len(data));
            if not packet: return None
            data += packet
        return json.loads(data.decode('utf-8'))
    except (socket.error, struct.error, json.JSONDecodeError): return None

class ServerCarRepresentation:
    def __init__(self, image_path):
        self.original_image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.original_image, (self.original_image.get_width() // 2, self.original_image.get_height() // 2))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.top_left = (0, 0)
    
    def update(self, car_obj):
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
        self.game_state_lock = threading.Lock(); self.running = True
        self.game_id = str(uuid.uuid4()); self.input_queue = Queue()
        
        player1 = Player(name="Player 1"); player1.choose_car("assets/red-car.png")
        player1.car.position = [60, 140]; player1.car.theta = 90
        player2 = Player(name="Player 2"); player2.choose_car("assets/purple-car.png")
        player2.car.position = [60, 180]; player2.car.theta = 90
        
        self.players = { player1: {'conn': player1_conn}, player2: {'conn': player2_conn} }
        self.conn_to_player = { v['conn']: k for k, v in self.players.items() }

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

        # COMPLETED: Send the initial 'start' message
        for player, data in self.players.items():
            opponent = [p for p in self.players if p != player][0]
            start_message = {
                "type": "start", "your_name": player.name, "your_car_image": player.car_image_path,
                "opponent_name": opponent.name, "opponent_car_image": opponent.car_image_path,
                "initial_state": {p.name: p.car.get_state() for p in self.players},
                "total_laps": self.game_logic.total_laps,
                "message": "Game starting!"
            }
            send_message(data['conn'], start_message)

        self.game_logic.start()

        TICK_RATE = 30
        while self.running:
            start_time = time.time()
            
            # COMPLETED: Process inputs from the queue
            while not self.input_queue.empty():
                player, input_data = self.input_queue.get()
                keys = input_data.get('keys', {})
                if keys.get('UP'): player.car.move_forward()
                if keys.get('DOWN'): player.car.move_backward()
                if keys.get('LEFT'): player.car.rotate(left=True)
                if keys.get('RIGHT'): player.car.rotate(right=True)
            
            with self.game_state_lock:
                for player in self.players:
                    player.car.update_position()
                    car_rep = self.server_cars[player]
                    car_rep.update(player.car)
                    if self.track_mask.overlap(car_rep.mask, car_rep.top_left):
                        player.car.bounce()
                    if self.finish_line.check(player, car_rep.rect):
                        if self.lap_validator.check(player):
                            self.game_logic.lap_completed(player)
                            print(f"[GAME LOGIC] {player.name} completed a lap!")
                    if self.game_logic.player_laps.get(player, 0) >= self.game_logic.total_laps:
                        print(f"[GAME OVER] {player.name} wins!")
                        self.running = False
            
            # COMPLETED: Broadcast the game state
            game_state_packet = {
                "type": "game_update",
                "states": {p.name: p.car.get_state() for p in self.players},
                "laps": {p.name: laps for p, laps in self.game_logic.player_laps.items()}
            }
            self.broadcast(game_state_packet)
            
            time_to_sleep = (1 / TICK_RATE) - (time.time() - start_time)
            if time_to_sleep > 0: time.sleep(time_to_sleep)

        print(f"[GAME OVER] Game {self.game_id} has ended.")
        self.broadcast({"type": "end", "message": "Game over."})
        for data in self.players.values(): data['conn'].close()

# ==============================================================================
# SECTION 3: THE GAMESERVER (Matchmaking)
# ==============================================================================
class GameServer:
    def __init__(self, host="127.0.0.1", port=65432):
        self.host = host; self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.lobby = []; self.lobby_lock = threading.Lock()

    def _matchmaking(self, conn, addr):
        print(f"[LOBBY] {addr} has connected...")
        send_message(conn, {"type": "status", "message": "Connected, waiting for match..."})

        game_to_start = None
        with self.lobby_lock:
            self.lobby.append((conn, addr))
            if len(self.lobby) >= 2:
                p1_conn, p1_addr = self.lobby.pop(0)
                p2_conn, p2_addr = self.lobby.pop(0)
                game_to_start = GameThread(p1_conn, p1_addr, p2_conn, p2_addr)

        # Start the game thread outside the lock so new clients can still connect
        if game_to_start:
            game_to_start.start()

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

# ==============================================================================
# SECTION 4: MAIN EXECUTION
# ==============================================================================
if __name__ == "__main__":
    # CORRECTED: Initialize Pygame ONCE at the start of the server process
    pygame.init()
    server = GameServer()
    server.start()