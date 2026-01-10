import pygame
from player.inventory import Inventory

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 28, 28)
        self.speed = 4
        # self.gold = 0
        self.inventory = Inventory()
        self.attack_cooldown = 0
        self.max_hp = 100
        self.hp = 100

    def update(self, input, walls, world_w, world_h):
        dx = dy = 0

        if input.is_pressed(pygame.K_w):
            dy -= self.speed
        if input.is_pressed(pygame.K_s):
            dy += self.speed
        if input.is_pressed(pygame.K_a):
            dx -= self.speed
        if input.is_pressed(pygame.K_d):
            dx += self.speed

        # X 碰撞
        self.rect.x += dx
        for wall in walls:
            if self.rect.colliderect(wall):
                if dx > 0:
                    self.rect.right = wall.left
                elif dx < 0:
                    self.rect.left = wall.right

        # Y 碰撞
        self.rect.y += dy
        for wall in walls:
            if self.rect.colliderect(wall):
                if dy > 0:
                    self.rect.bottom = wall.top
                elif dy < 0:
                    self.rect.top = wall.bottom

        # 世界边界
        self.rect.left = max(0, self.rect.left)
        self.rect.top = max(0, self.rect.top)
        self.rect.right = min(world_w, self.rect.right)
        self.rect.bottom = min(world_h, self.rect.bottom)

        #attack
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def attack(self, enemies):
        if self.attack_cooldown > 0:
            return

        attack_rect = self.rect.inflate(20, 20)

        for enemy in enemies:
            if enemy.alive and attack_rect.colliderect(enemy.rect):
                enemy.take_damage(1)

        self.attack_cooldown = 20

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0
        print(f"玩家受伤 -{amount}，当前HP: {self.hp}")

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 200, 0), self.rect)
