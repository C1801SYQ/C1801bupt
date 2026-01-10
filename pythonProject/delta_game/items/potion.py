import pygame
from items.item import Item

class Potion(Item):
    def __init__(self, heal_amount=20):
        super().__init__("Potion")
        self.heal_amount = heal_amount

    def use(self, player):
        player.hp = min(player.max_hp, player.hp + self.heal_amount)
