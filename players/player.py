from cars.car import Car

class Player:
    def __init__(self, name):
        self.name = name
        self.car = None
        self.car_image_path = None  
        self.car_list = ["assets/red-car.png"]
        self.coins = 100

    def choose_car(self, image_path):
        self.car = Car(0, [50, 80])
        self.car_image_path = image_path  
