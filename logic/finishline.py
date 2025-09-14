class FinishLineDetector:
    def __init__(self, rect):
        self.rect = rect
        self.entered_cars = set()  # keeps cars currently inside

    def check(self, player,car_rect):
        

        if self.rect.colliderect(car_rect):
            if player not in self.entered_cars:
                self.entered_cars.add(player)
                return True  # First-time entry (lap counted)
            else:
                return False  # Already inside; ignore
        else:
            if player in self.entered_cars:
                self.entered_cars.remove(player)  # Car left zone, reset state
            return False
