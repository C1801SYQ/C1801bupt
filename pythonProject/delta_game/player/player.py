# player/player.py
import pygame
from player.inventory import Inventory
import math


class Player:
    def __init__(self, x, y):
        # --- 1. 基础属性 ---
        self.speed = 4
        self.inventory = Inventory()
        self.attack_cooldown = 0
        self.max_hp = 100
        self.hp = 100

        # --- 2. 动画状态机属性 (参考专业做法) ---
        self.status = 'down_idle'
        self.frame_index = 0
        self.animation_speed = 0.15

        # --- 3. 自动切割贴图 ---
        self.animations = {
            'down': [], 'up': [], 'left': [], 'right': [],
            'down_idle': [], 'up_idle': [], 'left_idle': [], 'right_idle': []
        }
        self.import_assets()

        # 初始图片
        self.image = self.animations[self.status][self.frame_index]

        self.rect = pygame.Rect(x, y, 24, 20)

    def import_assets(self):
        """从 1024x1024 的大图自动切分 16 格"""
        img_path = r"C:\Users\lenovo\OneDrive\Desktop\作业\大二上\python\pythonProject\delta_game\asserts\images\player.png"
        try:
            full_sheet = pygame.image.load(img_path).convert_alpha()
            # 1024 / 4 = 256 像素每格
            grid_size = 256

            def get_frame(col, row):
                # 创建透明画布
                frame = pygame.Surface((grid_size, grid_size), pygame.SRCALPHA)
                frame.blit(full_sheet, (0, 0), (col * grid_size, row * grid_size, grid_size, grid_size))
                # 缩放到游戏内显示大小
                return pygame.transform.scale(frame, (48, 48))

            # 映射图片布局 (假设：0行下，1行上，2行右，3行左)
            self.animations['down_idle'] = [get_frame(0, 0)]
            self.animations['down'] = [get_frame(1, 0), get_frame(2, 0), get_frame(3, 0)]
            self.animations['up_idle'] = [get_frame(0, 1)]
            self.animations['up'] = [get_frame(1, 1), get_frame(2, 1), get_frame(3, 1)]
            self.animations['right_idle'] = [get_frame(0, 2)]
            self.animations['right'] = [get_frame(1, 2), get_frame(2, 2), get_frame(3, 2)]
            self.animations['left_idle'] = [get_frame(0, 3)]
            self.animations['left'] = [get_frame(1, 3), get_frame(2, 3), get_frame(3, 3)]

        except Exception as e:
            print(f"贴图加载失败: {e}")
            fallback = pygame.Surface((48, 48))
            fallback.fill((255, 200, 0))
            for key in self.animations: self.animations[key] = [fallback]

    def get_status(self, dx, dy):
        """确定当前动作状态"""
        if dx > 0:
            self.status = 'right'
        elif dx < 0:
            self.status = 'left'
        elif dy > 0:
            self.status = 'down'
        elif dy < 0:
            self.status = 'up'

        if dx == 0 and dy == 0:
            if not '_idle' in self.status:
                self.status += '_idle'

    def animate(self):
        """播放动画帧"""
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
        self.image = animation[int(self.frame_index)]

    # ⭐ 补回缺失的攻击方法
    def attack(self, enemies):
        if self.attack_cooldown > 0:
            return
        # 判定范围比自身大一圈
        attack_rect = self.rect.inflate(30, 30)
        for enemy in enemies:
            if enemy.alive and attack_rect.colliderect(enemy.rect):
                enemy.take_damage(1)
        self.attack_cooldown = 20

    # ⭐ 补回缺失的受伤方法
    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)

    def update(self, input_handler, walls, world_w, world_h):
        # 1. 移动逻辑
        current_speed = self.speed * self.inventory.get_speed_multiplier()
        dx = dy = 0
        if input_handler.is_pressed(pygame.K_w): dy -= current_speed
        if input_handler.is_pressed(pygame.K_s): dy += current_speed
        if input_handler.is_pressed(pygame.K_a): dx -= current_speed
        if input_handler.is_pressed(pygame.K_d): dx += current_speed

        # 2. 状态更新与动画播放
        self.get_status(dx, dy)
        self.animate()

        # 3. 碰撞处理
        self.rect.x += dx
        for wall in walls:
            if self.rect.colliderect(wall):
                if dx > 0:
                    self.rect.right = wall.left
                elif dx < 0:
                    self.rect.left = wall.right

        self.rect.y += dy
        for wall in walls:
            if self.rect.colliderect(wall):
                if dy > 0:
                    self.rect.bottom = wall.top
                elif dy < 0:
                    self.rect.top = wall.bottom

        # 4. 限制在世界边界内
        self.rect.clamp_ip(pygame.Rect(0, 0, world_w, world_h))

        # 5. 攻击冷却计时
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def draw(self, screen, camera):
        """⭐ 修改绘制方法：让图片的中心对准碰撞箱的中心"""
        bobbing = math.sin(pygame.time.get_ticks() * 0.01) * 2

        # 获取碰撞箱在屏幕上的显示位置
        pos_on_screen = camera.apply(self)

        # 3. 计算图片的绘制矩形
        # 让 48x48 的大图片中心和 24x20 的碰撞箱中心重合
        # 这样人物看起来是踩在碰撞箱上的，上半身可以遮挡一部分墙体
        img_rect = self.image.get_rect(center=pos_on_screen.center)

        # 应用呼吸效果
        img_rect.y += bobbing

        screen.blit(self.image, img_rect)