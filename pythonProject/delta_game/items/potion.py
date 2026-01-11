import pygame
from items.item import Item

# items/potion.py

class Potion:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 16, 16)
        self.name = "Potion"  # ⭐ 必须有这个
        self.collected = False

    def use(self, player):
        player.hp = min(player.max_hp, player.hp + 30) # 回复30点血
