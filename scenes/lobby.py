import pygame
from ui.lobby_ui import LobbyUI
from logic.lobby_manager import LobbyManager

def show_lobby(win, player,gamemanager):
    car_list = ["assets/red-car.png", "assets/green-car.png", "assets/grey-car.png", "assets/white-car.png", "assets/purple-car.png"]
    car_prices = [0, 100,200,300,400]
    
    manager = LobbyManager(player, car_list, car_prices)
    ui = LobbyUI(win, manager,gamemanager)

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                action = ui.handle_mouse(pygame.mouse.get_pos())
                if action == "offline" and player.car:
                    from scenes.play_offline import play_offline
                    play_offline(win, player)
                    return
                elif action == "online":
                    from scenes.play_online import play_online
                    play_online(win, player)
                    return

        win.fill((255, 255, 255))
        ui.draw()
        pygame.display.update()
        clock.tick(60)
