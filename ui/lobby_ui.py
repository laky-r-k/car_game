import pygame
from ui.buttons import Button

class LobbyUI:
    def __init__(self, win, manager,gamemanager):
        self.win = win
        self.manager = manager

        self.font = pygame.font.Font(None, 32)
        self.buttons = {
            "offline": Button("play offline", [0,0,0], [100,100,0], 75, 100, (450,600),manager=gamemanager),
            "online": Button("play online", [0,0,0], [100,100,0], 75, 100, (575,600),manager=gamemanager),
            "left": Button("<", [0,0,0], [100,100,0], 100, 100, (50,250),manager=gamemanager),
            "right": Button(">", [0,0,0], [100,100,0], 100, 100, (550,250),manager=gamemanager),
            "choose": Button("choose", [0,0,0], [100,100,0], 75, 100, (200,425),manager=gamemanager),
            "buy": Button("buy", [0,0,0], [100,100,0], 75, 100, (400,425),manager=gamemanager),
        }

    def draw(self):
        p = self.manager.player
        car_index = self.manager.car_index

        name = self.font.render(p.name, True, (0,0,0))
        coin = self.font.render(f"Coins: {p.coins}", True, (0,0,0))
        cost = self.font.render(f"Cost: {self.manager.car_prices[car_index]}", True, (0,0,0))

        car_image = pygame.transform.scale(pygame.image.load(self.manager.car_list[car_index]), (125,200))
        pygame.draw.rect(self.win, [250,250,0], pygame.Rect(200,200,300,200))

        self.win.blit(name, (10,10))
        self.win.blit(coin, (600,10))
        self.win.blit(cost, (300,450))
        self.win.blit(car_image, (200,200))

        # draw buttons
        for key, button in self.buttons.items():
            if key == "buy" and not self.manager.can_buy():
                continue
            button.draw(self.win)

    def handle_mouse(self, pos):
        if self.buttons["left"].is_pressed(pos):
            self.manager.prev_car()
        elif self.buttons["right"].is_pressed(pos):
            self.manager.next_car()
        elif self.buttons["choose"].is_pressed(pos):
            self.manager.choose()
        elif self.buttons["buy"].is_pressed(pos):
            self.manager.buy()
        elif self.buttons["offline"].is_pressed(pos):
            return "offline"
        elif self.buttons["online"].is_pressed(pos):
            return "online"
        return None
