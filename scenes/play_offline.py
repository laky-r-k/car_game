import pygame
import sys
from rendering.car_renderer import CarRenderer
from cars.car import Car
from logic.gamelogic import GameLogic
from logic.lapselogic import LapValidator
from logic.finishline import FinishLineDetector
from players.aiplayer import AIplayer
def drawpoints(win,points):
     for point in points:
          pygame.draw.circle(win,[250,0,0],point,2)
def play_offline(win, player):
    clock = pygame.time.Clock()

    # Load and scale track image and border
    track = pygame.transform.scale(pygame.image.load("assets/track.png"), (700, 700))
    track_border_img = pygame.transform.scale(pygame.image.load("assets/track-border.png"), (700, 700))
    track_mask = pygame.mask.from_surface(track_border_img)

    finish_line_img = pygame.transform.scale(pygame.image.load("assets/finish.png"),(65,20)).convert_alpha()
    finish_line_pos = (21,180)  # top-left corner

    finish_line_rect = finish_line_img.get_rect(topleft=finish_line_pos)
    finish_line=FinishLineDetector(finish_line_rect)
    

    #gamelogic
    game=GameLogic(2,1)
    lapse=LapValidator((0,-1))

    waypoints = [(60, 114)
, (118, 73)
, (170, 120)
, (170, 353)
, (232, 410)
, (283, 322)
, (291, 83)
, (695, 73)
, (438, 366)
, (690, 368)
, (748, 643)
, (598, 655)
, (512, 468)
, (403, 606)
, (327, 727)
, (76, 485)
, (57, 205)]

    #aiplayer
    aiplayer=AIplayer("bot")
    aiplayer.choose_car(0,[60,140],"assets/purple-car.png",waypoints)
    aicar=aiplayer.car
    ai_car_renderer=CarRenderer(aiplayer.car_image_path)
    
    # Create car physics + renderer
    car = player.car
    car_renderer = CarRenderer(player.car_image_path)  # car_image_path must be stored in player
    run=True
    game.start()
    game.register_player(player)
    game.register_player(aiplayer)

    while game.state!="game_over" and run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run=False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                waypoints.append(mouse_pos)
                print(f", {mouse_pos}")
            

        # Handle input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: car.rotate(left=True)
        if keys[pygame.K_RIGHT]: car.rotate(right=True)
        if keys[pygame.K_UP]: car.move_forward()
        if keys[pygame.K_DOWN]: car.move_backward()

        # Update car position
        car.update_position()
        aicar.update_position()
        aicar.aimove()

        # Draw everything
        win.fill((255, 255, 255))
        win.blit(track, (0, 0))
        win.blit(finish_line_img,finish_line_pos)
        drawpoints(win,waypoints)
        pygame.draw.rect(win,[250,250,250],finish_line_rect,3)
        car_renderer.draw(win, car.position, car.theta)
        ai_car_renderer.draw(win,aicar.position,aicar.theta)

        # Collision check
        if track_mask.overlap(car_renderer.mask, car_renderer.top_left):
            car.bounce(-2)
        if track_mask.overlap(ai_car_renderer.mask,ai_car_renderer.top_left):
             aicar.bounce(-2)
        if ai_car_renderer.get_rect().collidepoint(aicar.get_current_point()):
            aicar.update_path_point()
            

        if finish_line.check(player,car_renderer.get_rect()):
                if lapse.check(player):
                    game.lap_completed(player)
        if finish_line.check(aiplayer,ai_car_renderer.get_rect()):
                if lapse.check(aiplayer):
                    game.lap_completed(aiplayer)
        
        

        pygame.display.update()
        clock.tick(60)
    print(waypoints)