import pygame
from cars import player
import Game
import sys
import ctypes
pygame.init()

win=pygame.display.set_mode((700,700))






game=Game.game()
game.input_name(win)
game.create_lobby(win)
