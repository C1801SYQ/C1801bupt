# enemies/enemy.py
import pygame
import math


class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.alive = True
        self.speed = 2
        self.detection_radius = 200
        self.state = "idle"

    def update(self, player_rect, player_obj, walls):  # ⭐ 新增 walls 参数
        if not self.alive:
            return

        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)

        if distance < self.detection_radius:
            self.state = "chase"
        else:
            self.state = "idle"

        if self.state == "chase" and distance > 0:
            # 计算归一化方向向量
            vx = (dx / distance) * self.speed
            vy = (dy / distance) * self.speed

            # --- 分轴移动与碰撞检测 ---

            # 1. 水平移动
            self.rect.x += vx
            for wall in walls:
                if self.rect.colliderect(wall):
                    if vx > 0:
                        self.rect.right = wall.left
                    elif vx < 0:
                        self.rect.left = wall.right

            # 2. 垂直移动
            self.rect.y += vy
            for wall in walls:
                if self.rect.colliderect(wall):
                    if vy > 0:
                        self.rect.bottom = wall.top
                    elif vy < 0:
                        self.rect.top = wall.bottom

            # 攻击判定
            if self.rect.colliderect(player_rect):
                player_obj.take_damage(0.2)

        elif self.state == "idle":
            pass

    def take_damage(self, amount):
        self.alive = False

    def draw(self, screen, camera):
        if self.alive:
            color = (255, 0, 0) if self.state == "chase" else (150, 0, 0)
            screen.blit(pygame.Surface((32, 32)), camera.apply(self))  # 占位
            pygame.draw.rect(screen, color, camera.apply(self))