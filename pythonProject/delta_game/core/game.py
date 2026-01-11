import pygame
import random
from settings import FPS, SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE
from core.input import Input
from player.player import Player
from map.tilemap import TileMap
from items.gold import Gold
from ui.hud import HUD
from enemies.enemy import Enemy
from items.chest import Chest
from items.potion import Potion
from core.camera import Camera
from core.save_manager import save_game, load_game
from items.loot_config import LOOT_TABLE # 引入你的配置


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True

        self.input = Input()
        self.tilemap = TileMap(rows=80, cols=60)

        spawn_x, spawn_y = self.tilemap.player_spawn
        self.player = Player(spawn_x, spawn_y)
        # 加载历史累计金币
        saved_gold = load_game()
        self.player.inventory.gold = saved_gold

        # core/game.py 的 __init__ 中
        # 替换掉原本生成 golds 和 enemies 的固定列表

        self.chests = []
        self.enemies = []
        self.golds = []

        # 遍历所有房间
        for i, (rx, ry, rw, rh) in enumerate(self.tilemap.rooms):
            # 转换为带 padding 的世界坐标
            wx = (rx + self.tilemap.padding) * TILE_SIZE
            wy = (ry + self.tilemap.padding) * TILE_SIZE

            if i == 0:
                # 第一个房间是出生点，不放怪
                self.player.rect.topleft = (wx + 32, wy + 32)
            else:
                # 其他房间：放置 1 个宝箱和 2 个守卫怪
                self.chests.append(Chest(wx + (rw // 2) * 32, wy + (rh // 2) * 32))
                for _ in range(2):
                    ex = wx + random.randint(1, rw - 2) * 32
                    ey = wy + random.randint(1, rh - 2) * 32
                    self.enemies.append(Enemy(ex, ey))

        # 走廊和房间随机撒不同等级的战利品
        for _ in range(15):
            pos = self.tilemap.get_random_empty_pos()
            # 随机权重：80%普通, 15%稀有, 5%史诗
            roll = random.random()
            if roll < 0.05:
                category = "epic"
            elif roll < 0.20:
                category = "rare"
            else:
                category = "common"

            item_info = random.choice(LOOT_TABLE[category])
            val = random.randint(item_info["min_val"], item_info["max_val"])

            # 创建带有配置信息的物品
            self.golds.append(Gold(pos[0], pos[1], val, item_info))


        self.hud = HUD()

        self.player.inventory.add_item(Potion(0, 0))

        self.camera = Camera(self.tilemap.width, self.tilemap.height)

        self.exit_timer = 0  # 撤离计时器
        self.exit_need_time = 180  # 假设需要 180 帧 (3秒)

        self.status = "playing"  # 状态：playing, win, dead

        data = load_game()
        self.player.inventory.gold = data["total_gold"]

        # 根据存档数量添加药水
        for _ in range(data["potions"]):
            self.player.inventory.add_item(Potion(0, 0))

        self.damage_flash_timer = 0

        data = load_game()
        self.start_gold = data.get("total_gold", 0)  # 记录进场时的钱
        self.player.inventory.gold = self.start_gold

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
                # ⭐ 按 B 键打开/关闭背包
                if event.key == pygame.K_b:
                    self.player.inventory.toggle()

                # 只有背包关闭时才允许其他操作
                if not self.player.inventory.is_open:


                # 攻击逻辑
                    if event.key == pygame.K_j:
                        self.player.attack(self.enemies)

                # 修改后的开箱逻辑：增加判定范围
                    if event.key == pygame.K_k:
                        interact_rect = self.player.rect.inflate(20, 20) # 扩大交互判定
                        for chest in self.chests:
                            gold = chest.try_open(interact_rect)
                            if gold:
                                self.golds.append(gold)
                                print("宝箱已打开！")

                # 使用药水
                    if event.key == pygame.K_h:
                        # 我们之前在 Inventory 里写好的 use_item 方法
                        used = self.player.inventory.use_item("Potion", self.player)
                        if used:
                            print("生命值已恢复！")

    def update(self):
        # ⭐ 如果背包打开，跳过逻辑更新（实现暂停效果）
        if self.player.inventory.is_open:
            return


        # 1. 应用重量减速：使用 Inventory 的计算公式
        speed_mult = self.player.inventory.get_speed_multiplier()
        self.player.speed = 5 * speed_mult

        # 2. 玩家更新
        self.player.update(self.input, self.tilemap.walls, self.tilemap.width, self.tilemap.height)

        # 3. 撤离检测 (保持原样)
        if self.tilemap.exit_rect and self.player.rect.colliderect(self.tilemap.exit_rect):
            self.exit_timer += 1
            if self.exit_timer >= self.exit_need_time:
                self.handle_extraction()
        else:
            self.exit_timer = 0

        # 4. 物品拾取逻辑
        for gold in self.golds[:]:
            item_obj = gold.update(self.player.rect)
            if item_obj:
                # ⭐ 修正：将 add_loot 改为 add_item
                self.player.inventory.add_item(item_obj)
                self.golds.remove(gold)

        # 5. 敌人更新 (⭐ 注意：确保这个循环不在 gold 循环内部)
        for enemy in self.enemies[:]:
            # 注意：如果你的 Enemy.update 需要 walls 参数，请确保传入
            enemy.update(self.player.rect, self.player, self.tilemap.walls)

            if not enemy.alive:
                # --- 模拟宝箱的随机掉落逻辑 ---
                roll = random.random()
                if roll < 0.05:  # 5% 概率掉落史诗 (比宝箱略高，鼓励战斗)
                    category = "epic"
                elif roll < 0.25:  # 20% 概率掉落稀有
                    category = "rare"
                else:  # 普通掉落
                    category = "common"

                # 从配置表抽取数据
                item_data = random.choice(LOOT_TABLE[category])
                # 随机生成价值（注意使用 loot_config.py 中的键名 min_val）
                amount = random.randint(item_data["min_val"], item_data["max_val"])

                # 在敌人尸体位置创建具有实体的战利品
                # 传入 item_data 确保它有颜色、名称和重量
                drop_item = Gold(enemy.rect.x, enemy.rect.y, amount, item_data)
                self.golds.append(drop_item)

                # 移除敌人
                self.enemies.remove(enemy)
                print(f"击败敌人！掉落了: {item_data['name']} (${amount})")

        # 6. 死亡判定
        if self.player.hp <= 0:
            data = load_game()
            # 惩罚：如果你死在里面，本次捡到的钱带不走，且带进去的药水全部丢失
            save_game(data["total_gold"], 0)
            self.status = "dead"
            self.running = False

    # core/game.py

    def handle_extraction(self):
        # ⭐ 关键修复：先改变状态，再结束运行
        self.status = "win"

        from core.save_manager import save_game
        save_game(self.player.inventory.gold, self.get_potion_count())
        print(f"存档成功，金币：{self.player.inventory.gold}，状态：{self.status}")

        self.running = False

    def get_potion_count(self):
        # 辅助函数：统计玩家背包里还剩多少药水
        count = 0
        for item in self.player.inventory.items:
            # 假设你的 Potion 类有 name 属性，或者直接判断类型
            if hasattr(item, 'name') and item.name == "Potion":
                count += 1
        return count

    # core/game.py 内部

    @property
    def session_gold(self):
        # 本次收益 = 当前总资产 - 进场时的总资产
        # 这样 main.py 里的 ResultScreen 就能拿到数据了
        return self.player.inventory.gold - self.start_gold

    def _draw_extraction_bar(self):
        """修复 AttributeError: 'Game' object has no attribute '_draw_extraction_bar'"""
        bar_width = 200
        bar_height = 15
        x = (SCREEN_WIDTH - bar_width) // 2
        y = SCREEN_HEIGHT // 2 + 60
        progress = self.exit_timer / self.exit_need_time

        # 绘制进度条背景和填充
        pygame.draw.rect(self.screen, (50, 50, 50), (x, y, bar_width, bar_height))
        pygame.draw.rect(self.screen, (0, 191, 255), (x, y, int(bar_width * progress), bar_height))
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, bar_width, bar_height), 1)


    def draw(self):
        # 1. 清屏 (现在由 tilemap 画背景，这里可以保留作为底色)
        self.screen.fill((30, 30, 30))

        # 2. 更新相机位置（确保相机紧跟玩家）
        self.camera.update(self.player)

        # ⭐ 关键修改：直接调用 tilemap 的 draw 方法
        # 这会自动画出：深色地面、带随机颜色的加厚墙体
        self.tilemap.draw(self.screen, self.camera)

        # 3. 绘制撤离点 (保持原样，但在地图之上)
        if self.tilemap.exit_rect:
            pygame.draw.rect(self.screen, (0, 191, 255), self.camera.apply_rect(self.tilemap.exit_rect))
            pygame.draw.rect(self.screen, (255, 255, 255), self.camera.apply_rect(self.tilemap.exit_rect), 2)

        # 4. 绘制宝箱
        for chest in self.chests:
            color = (80, 80, 80) if chest.opened else (139, 69, 19)
            pygame.draw.rect(self.screen, color, self.camera.apply(chest))

        # 5. 绘制金币/战利品
        for gold in self.golds:
            # 此时 gold.draw 已经在类里定义好了，或者手动画：
            pygame.draw.ellipse(self.screen, gold.color, self.camera.apply(gold))
            pygame.draw.ellipse(self.screen, (255, 255, 255), self.camera.apply(gold), 1)

        # 6. 绘制敌人
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera)

        # 7. 绘制玩家
        self.player.draw(self.screen, self.camera)

        # 8. 绘制受击闪红和 HUD (固定在屏幕上)
        if self.damage_flash_timer > 0:
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            s.set_alpha(100)
            s.fill((255, 0, 0))
            self.screen.blit(s, (0, 0))
            self.damage_flash_timer -= 1

        self.hud.draw(self.screen, self.player, self.exit_timer, self.exit_need_time)
        # 9. 绘制操作指南
        self.hud.draw_controls_guide(self.screen)

        # 10. 绘制开局提示
        self.hud.draw_start_tip(self.screen)

        # 绘制小地图
        self.hud.draw_minimap(self.screen, self.player, self.tilemap)

        # 最后画背包面板，确保它遮挡一切
        self.hud.draw_inventory_panel(self.screen, self.player)

        pygame.display.flip()


