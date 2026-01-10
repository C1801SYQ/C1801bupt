import pygame
from settings import FPS
from core.input import Input
from player.player import Player
from map.tilemap import TileMap
from items.gold import Gold
from ui.hud import HUD
from enemies.enemy import Enemy
from items.chest import Chest
from items.potion import Potion


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True

        self.input = Input()
        self.tilemap = TileMap()

        spawn_x, spawn_y = self.tilemap.player_spawn
        self.player = Player(spawn_x, spawn_y)

        self.golds = [
            Gold(200, 100, 5),
            Gold(300, 140, 3),
            Gold(400, 100, 10),
        ]

        self.enemies = [
            Enemy(350, 120),
            Enemy(450, 160),
        ]

        self.hud = HUD()

        self.chests = []
        for x, y in self.tilemap.chest_spawns:
            self.chests.append(Chest(x, y))

        self.player.inventory.add_item(Potion(30))

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            self.input.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_j:
                    self.player.attack(self.enemies)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_k:
                    for chest in self.chests:
                        gold = chest.try_open(self.player.rect)
                        if gold:
                            self.golds.append(gold)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    used = self.player.inventory.use_item("Potion", self.player)
                    if used:
                        print("使用血瓶，HP:", self.player.hp)

    def update(self):
        # 玩家更新
        self.player.update(
            self.input,
            self.tilemap.walls,
            self.tilemap.width,
            self.tilemap.height
        )

        # 金币拾取
        for gold in self.golds[:]:
            gained = gold.update(self.player.rect)
            if gold.collected:
                self.player.inventory.add_gold(gained)
                self.golds.remove(gold)
                print(f"捡到金币 +{gained}，当前金币：{self.player.inventory.gold}")

        # 敌人更新
        for enemy in self.enemies:
            enemy.update(self.player.rect, self.player)

        # 敌人死亡掉落
        for enemy in self.enemies[:]:
            if not enemy.alive:
                self.golds.append(
                    Gold(enemy.rect.x, enemy.rect.y, 5)
                )
                self.enemies.remove(enemy)

        if self.player.hp <= 0:
            print("玩家死亡")
            self.running = False

    def draw(self):
        self.screen.fill((30, 30, 30))
        self.tilemap.draw(self.screen)

        for chest in self.chests:
            chest.draw(self.screen)

        for gold in self.golds:
            gold.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        self.player.draw(self.screen)
        self.hud.draw(self.screen, self.player)

        pygame.display.flip()

