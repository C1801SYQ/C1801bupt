import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from core.game import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Delta Gold Hunter")

    game = Game(screen)
    game.run()

    pygame.quit()

if __name__ == "__main__":
    main()
