class LobbyManager:
    def __init__(self, player, car_list, car_prices):
        self.player = player
        self.car_list = car_list
        self.car_prices = car_prices
        self.car_index = 0

    def next_car(self):
        if self.car_index < len(self.car_list) - 1:
            self.car_index += 1

    def prev_car(self):
        if self.car_index > 0:
            self.car_index -= 1

    def can_buy(self):
        car = self.car_list[self.car_index]
        return car not in self.player.car_list and self.player.coins >= self.car_prices[self.car_index]

    def buy(self):
        if self.can_buy():
            car = self.car_list[self.car_index]
            self.player.coins -= self.car_prices[self.car_index]
            self.player.car_list.append(car)

    def choose(self):
        car = self.car_list[self.car_index]
        if car in self.player.car_list:
            self.player.choose_car(car)
