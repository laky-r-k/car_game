import pygame
import sys
from rendering.car_renderer import CarRenderer
from cars.car import Car

def play_offline(win, player):
    clock = pygame.time.Clock()

    # Load and scale track image and border
    track = pygame.transform.scale(pygame.image.load("assets/track.png"), (700, 700))
    track_border_img = pygame.transform.scale(pygame.image.load("assets/track-border.png"), (700, 700))
    track_mask = pygame.mask.from_surface(track_border_img)

    # Create car physics + renderer
    car = player.car
    car_renderer = CarRenderer(player.car_image_path)  # car_image_path must be stored in player
    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

        # Handle input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: car.rotate(left=True)
        if keys[pygame.K_RIGHT]: car.rotate(right=True)
        if keys[pygame.K_UP]: car.move_forward()
        if keys[pygame.K_DOWN]: car.move_backward()

        # Update car position
        car.update_position()

        # Draw everything
        win.fill((255, 255, 255))
        win.blit(track, (0, 0))
        car_renderer.draw(win, car.position, car.theta)

        # Collision check
        if track_mask.overlap(car_renderer.mask, car_renderer.top_left):
            car.bounce()

        pygame.display.update()
        clock.tick(60)
