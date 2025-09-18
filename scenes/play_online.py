# In your main game file (e.g., main.py)
import pygame
import sys
import time

# NOTE: Make sure these import paths match your project structure
from network.client import GameClient
from rendering.car_renderer import CarRenderer # Assuming you have this renderer class

def play_online(win):
    # 1. INITIALIZATION
    clock = pygame.time.Clock()
    client = GameClient()
    if not client.start_networking():
        return # Exit if connection fails

    # --- ASSET LOADING ---
    # ADDED: Complete asset loading
    track = pygame.transform.scale(pygame.image.load("assets/track.png"), (700, 700))
    track_border_img = pygame.transform.scale(pygame.image.load("assets/track-border.png"), (700, 700))
    track_mask = pygame.mask.from_surface(track_border_img)
    finish_line_img = pygame.transform.scale(pygame.image.load("assets/finish.png"),(65,20)).convert_alpha()
    finish_line_pos = (21,180)
    # --- END ADDED SECTION ---

    my_car_renderer = None
    opponent_car_renderer = None

    # 2. WAITING LOBBY LOOP
    while client.running and not client.me:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                client.running = False

        win.fill((200, 200, 200))
        font = pygame.font.SysFont(None, 55)
        text = font.render('Waiting for opponent...', True, (0,0,0))
        win.blit(text, (win.get_width()/2 - text.get_width()/2, 300))
        pygame.display.update()
        time.sleep(0.1)

    # 3. MAIN GAME LOOP
    while client.running:
        clock.tick(60)

        if client.me and not my_car_renderer:
            my_car_renderer = CarRenderer(client.me.car_image_path)
        if client.opponent and not opponent_car_renderer:
            opponent_car_renderer = CarRenderer(client.opponent.car_image_path)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                client.running = False
        
        # This logic assumes a background thread in the client is updating state
        if client.me:
            keys = pygame.key.get_pressed()
            inputs_to_send = {
                'UP': keys[pygame.K_UP],
                'DOWN': keys[pygame.K_DOWN],
                'LEFT': keys[pygame.K_LEFT],
                'RIGHT': keys[pygame.K_RIGHT]
            }
            client.send_inputs(inputs_to_send)

        # --- RENDER EVERYTHING ---
        win.fill((255, 255, 255))
        win.blit(track, (0, 0))
        
        # ADDED: Draw the finish line
        win.blit(finish_line_img, finish_line_pos)
        
        if opponent_car_renderer and client.opponent:
            opponent_car_renderer.draw(win, client.opponent.car.position, client.opponent.car.theta)
        if my_car_renderer and client.me:
            my_car_renderer.draw(win, client.me.car.position, client.me.car.theta)
        
        # ADDED: Draw the track border on top so it overlaps the cars
        win.blit(track_border_img, (0, 0))
        
        pygame.display.update()

    # 4. CLEANUP
    client.disconnect()
    print("Game Over or Disconnected.")