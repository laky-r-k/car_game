# In your main game file (e.g., main.py)
import pygame
import sys
from rendering.car_renderer import CarRenderer
from logic.lapselogic import LapValidator
from logic.finishline import FinishLineDetector
from network.client import GameClient # Import the client we defined above

def play_online(win):
    # 1. INITIALIZATION
    clock = pygame.time.Clock()
    
    # Create the network client. This will manage all game state.
    client = GameClient()
    if not client.start_networking():
        # If connection fails, we can't play.
        # You could show a menu screen here.
        return 

    # Load assets (same as offline mode)
    track = pygame.transform.scale(pygame.image.load("assets/track.png"), (700, 700))
    track_border_img = pygame.transform.scale(pygame.image.load("assets/track-border.png"), (700, 700))
    track_mask = pygame.mask.from_surface(track_border_img)
    finish_line_img = pygame.transform.scale(pygame.image.load("assets/finish.png"),(65,20)).convert_alpha()
    finish_line_pos = (21,180)
    finish_line_rect = finish_line_img.get_rect(topleft=finish_line_pos)
    finish_line = FinishLineDetector(finish_line_rect)
    
    # Logic for client-side lap detection
    lapse_validator = LapValidator((0, -1))

    # Create renderers for our car and the opponent's car
    # NOTE: Assuming car images are pre-determined. This could also come from the server.
    my_car_renderer = CarRenderer("assets/red-car.png")
    opponent_car_renderer = CarRenderer("assets/purple-car.png")
    
    # Wait for the game to start
    while client.running and client.game_logic.state != "playing":
        win.fill((255,255,255))
        # You can draw a "Waiting for opponent..." message here
        font = pygame.font.SysFont(None, 55)
        text = font.render('Waiting for opponent...', True, (0,0,0))
        win.blit(text, (150, 300))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                client.disconnect()
                pygame.quit()
                sys.exit()

    # 2. MAIN GAME LOOP
    while client.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                client.running = False
        
        # Handle local player input
        keys = pygame.key.get_pressed()
        moved = False
        if keys[pygame.K_LEFT]: client.my_car.rotate(left=True); moved = True
        if keys[pygame.K_RIGHT]: client.my_car.rotate(right=True); moved = True
        if keys[pygame.K_UP]: client.my_car.move_forward(); moved = True
        if keys[pygame.K_DOWN]: client.my_car.move_backward(); moved = True

        # Update local car physics
        client.my_car.update_position()

        # Check for local collisions for immediate feedback
        if track_mask.overlap(my_car_renderer.mask, my_car_renderer.top_left):
            client.my_car.bounce(-2)

        # Check for local lap completion
        if finish_line.check(client.player_id, my_car_renderer.get_rect()):
            if lapse_validator.check(client.player_id):
                client.game_logic.lap_completed(client.player_id)
                print(f"You completed a lap! Laps: {client.game_logic.player_laps[client.player_id]}")

        # Send our updated state to the server
        client.send_state()
        
        # 3. DRAW EVERYTHING
        win.fill((255, 255, 255))
        win.blit(track, (0, 0))
        win.blit(finish_line_img, finish_line_pos)
        
        # Draw the opponent's car based on the latest state received
        opponent_car_renderer.draw(win, client.opponent_car.position, client.opponent_car.theta)
        
        # Draw our car based on its current local state
        my_car_renderer.draw(win, client.my_car.position, client.my_car.theta)
        
        pygame.display.update()
        clock.tick(60)

    # 4. CLEANUP
    client.disconnect()
    # You can return to a main menu here
    print("Game Over or Disconnected.")