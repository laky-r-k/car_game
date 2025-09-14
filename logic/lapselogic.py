class LapValidator:
    def __init__(self, expected_direction=(0, -1)):
        self.reverse_entry = set()
        self.expected_direction = expected_direction  # e.g. up

    def check(self, player):
        if player not in self.reverse_entry:
            if self.is_correct_direction(player):
                return True  # ✅ valid lap
            else:
                self.reverse_entry.add(player)
                return False  # ❌ reverse entry
        else:
            if self.is_correct_direction(player):
                self.reverse_entry.remove(player)
            return False  # 🚫 previously reversed; wait until fixed

    def is_correct_direction(self, player):
        dir_x, dir_y = player.car.get_direction()
        print(dir_x," ",dir_y)
        allowed_x, allowed_y = self.expected_direction
        dot = dir_x * allowed_x + dir_y * allowed_y
        return dot > 0.7  # angle less than ~45 degrees
