import pygame
import math


class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 28, 28)
        self.speed = 2

        self.hp = 3
        self.alive = True

        self.damage = 10
        self.attack_cooldown = 1000  # 毫秒
        self.last_attack_time = 0

    def move_towards(self, target_rect):
        dx = target_rect.centerx - self.rect.centerx
        dy = target_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        if dist == 0:
            return

        dx /= dist
        dy /= dist

        self.rect.x += int(dx * self.speed)
        self.rect.y += int(dy * self.speed)

    def update(self, player_rect, player=None):
        if not self.alive:
            return

        # 追踪玩家
        self.move_towards(player_rect)

        # 攻击玩家
        if player and self.rect.colliderect(player_rect):
            now = pygame.time.get_ticks()
            if now - self.last_attack_time >= self.attack_cooldown:
                player.take_damage(self.damage)
                self.last_attack_time = now

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            print("敌人死亡")

    def draw(self, screen):
        if self.alive:
            pygame.draw.rect(screen, (200, 50, 50), self.rect)
