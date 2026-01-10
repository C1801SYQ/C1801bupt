import pygame
from items.gold import Gold

class Chest:
    def __init__(self, x, y, gold_amount=20):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.gold_amount = gold_amount
        self.opened = False

    def try_open(self, player_rect):
        if self.opened:
            return None

        if self.rect.colliderect(player_rect):
            self.opened = True
            return Gold(self.rect.x, self.rect.y, self.gold_amount)

        return None

    def draw(self, screen):
        color = (150, 75, 0) if not self.opened else (80, 80, 80)
        pygame.draw.rect(screen, color, self.rect)
