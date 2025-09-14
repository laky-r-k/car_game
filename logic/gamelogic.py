class GameLogic:
    def __init__(self, total_laps=3, max_winners=3):
        self.total_laps = total_laps
        self.max_winners = max_winners

        self.player_laps = {}  # {player: current_lap}
        self.finished_players = []  # [player1, player2, ...]

        self.state = "waiting"  # "waiting", "playing", "game_over"

    def register_player(self, player):
        self.player_laps[player] = 0

    def lap_completed(self, player):
        if self.state != "playing":
            return

        if player in self.finished_players:
            return  # Already finished

        self.player_laps[player] += 1

        if self.player_laps[player] >= self.total_laps:
            self.finished_players.append(player)
            print(f"{player.name} finished in position #{len(self.finished_players)}")

            if len(self.finished_players) >= self.max_winners:
                self.state = "game_over"

    def get_leaderboard(self):
        return [(p.name, i + 1) for i, p in enumerate(self.finished_players)]

    def reset(self):
        for p in self.player_laps:
            self.player_laps[p] = 0
        self.finished_players.clear()
        self.state = "waiting"
    def start(self):
        self.state= "playing"
