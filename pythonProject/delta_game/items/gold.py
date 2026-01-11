# items/gold.py
import pygame

class Gold:
    # ⭐ 必须确保这里有 (self, x, y, amount, item_data=None) 这些参数
    def __init__(self, x, y, amount, item_data=None):
        self.rect = pygame.Rect(x, y, 16, 16)
        self.amount = amount
        self.collected = False

        if item_data:
            # ⭐ 确保使用的是 item_data 而不是之前报错的 item_info
            self.name = item_data.get("name", "未知物品")
            self.color = item_data.get("color", (200, 200, 200))
            # 增加重量属性：价值越高越重
            self.weight = amount / 500.0
        else:
            self.name = "现金"
            self.color = (255, 215, 0)
            self.weight = amount / 1000.0

    def update(self, player_rect):
        """检测拾取，返回对象本身以便获取重量"""
        if not self.collected and self.rect.colliderect(player_rect):
            self.collected = True
            return self # ⭐ 返回 self 而不是 self.amount
        return None

    def draw(self, screen, camera):
        if not self.collected:
            pygame.draw.ellipse(screen, self.color, camera.apply(self))
            pygame.draw.ellipse(screen, (255, 255, 255), camera.apply(self), 1)