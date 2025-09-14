import pygame
from players.player import Player

def enter_name(win):
    name = ""
    font = pygame.font.Font(None, 32)
    active = True
    while active:
        win.fill((255, 255, 255))
        text = font.render("Enter Name: " + name, True, (0, 0, 0))
        win.blit(text, (200, 330))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += event.unicode
    return Player(name)
