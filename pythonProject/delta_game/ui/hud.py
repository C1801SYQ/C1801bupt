import pygame


class HUD:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 24)

    def draw(self, screen, player):
        # ===== 金币 =====
        gold_text = self.font.render(
            f"Gold: {player.inventory.gold}",
            True,
            (255, 215, 0)
        )
        screen.blit(gold_text, (10, 10))

        # ===== 血量 =====
        hp_text = self.font.render(
            f"HP: {player.hp}/{player.max_hp}",
            True,
            (200, 50, 50)
        )
        screen.blit(hp_text, (10, 40))

        # ===== 血瓶数量 =====
        potion_count = player.inventory.items.get("Potion", [None, 0])[1]
        potion_text = self.font.render(
            f"Potion: {potion_count}",
            True,
            (180, 180, 255)
        )
        screen.blit(potion_text, (10, 70))
