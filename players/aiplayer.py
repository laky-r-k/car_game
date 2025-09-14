from players.player import Player
from cars.AICAR import AICar
 
class AIplayer(Player):
    def __init__(self, name):
        super().__init__(name)
    def choose_car(self,angle,pos,image_path,waypoints):
        self.car=AICar(angle,pos,waypoints)
        self.car_image_path="assets/purple-car.png"
        
    
        