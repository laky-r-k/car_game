from cars.car import Car

class Player:
    def __init__(self, name):
        self.name = name
        self.car = None
        self.car_image_path = None  
        self.car_list = ["assets/red-car.png"]
        self.coins = 100

    def choose_car(self, image_path):
        self.car = Car(0, [30, 140])
        self.car_image_path = image_path  

    def __eq__(self, other):
        return isinstance(other, Player) and self.name == other.name

    def __hash__(self):
        return hash(self.name)
