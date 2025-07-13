import pygame
from core.game_manager import GameManager

pygame.init()
win = pygame.display.set_mode((700, 700))
pygame.display.set_caption("Multiplayer Car Game")

if __name__ == "__main__":
    game = GameManager(win)
    game.run()
