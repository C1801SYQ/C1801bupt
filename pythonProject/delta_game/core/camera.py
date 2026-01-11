import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width   # 地图总宽度
        self.height = height # 地图总高度

    def apply(self, entity):
        # 返回物体相对于相机的渲染位置
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        # 计算理想偏移量，使玩家处于屏幕中心
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target.rect.centery + int(SCREEN_HEIGHT / 2)

        # ⭐ 核心逻辑：锁定边界，不让相机露出地图外的黑色
        x = min(0, x)  # 限制左边界
        y = min(0, y)  # 限制上边界
        x = max(-(self.width - SCREEN_WIDTH), x)   # 限制右边界
        y = max(-(self.height - SCREEN_HEIGHT), y)  # 限制下边界

        self.camera.topleft = (x, y)