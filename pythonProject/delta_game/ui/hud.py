# ui/hud.py
import pygame


class HUD:
    def __init__(self):
        # 建议在 settings.py 定义字体大小，这里先硬编码
        self.font = pygame.font.SysFont("SimHei", 24)  # 支持中文
        self.big_font = pygame.font.SysFont("SimHei", 48)
        self.message_timer = 100

    def draw_start_tip(self, screen):
        """在屏幕中央显示开局任务目标"""
        if self.message_timer > 0:
            # 简单的淡出效果
            alpha = 255
            if self.message_timer < 60:
                alpha = int((self.message_timer / 60) * 255)

            # 创建文字表面并设置透明度
            text = "任务：收集物资，寻找蓝色区域撤离！"
            text_surf = self.big_font.render(text, True, (255, 255, 255))
            text_surf.set_alpha(alpha)

            # 居中显示
            rect = text_surf.get_rect(center=(screen.get_width() // 2, 200))

            # 绘制文字背景阴影，增加可读性
            shadow = self.big_font.render(text, True, (0, 0, 0))
            shadow.set_alpha(alpha)
            screen.blit(shadow, (rect.x + 2, rect.y + 2))
            screen.blit(text_surf, rect)

            self.message_timer -= 1


    def draw(self, screen, player, exit_timer, exit_need_time):
        #  绘制血条 (左上角)
        pygame.draw.rect(screen, (50, 50, 50), (20, 20, 200, 15))  # 背景
        hp_width = int((player.hp / player.max_hp) * 200)
        hp_color = (0, 255, 0) if player.hp > 30 else (255, 0, 0)
        pygame.draw.rect(screen, hp_color, (20, 20, hp_width, 15))
        potion_count = sum(1 for item in player.inventory.items if getattr(item, 'name', '') == "Potion")

        font = pygame.font.SysFont("SimHei", 20)

        # 2. 绘制当前物资价值 (下移至 y=50)
        gold_text = font.render(f"当前物资价值: ${player.inventory.gold}", True, (255, 215, 0))
        screen.blit(gold_text, (20, 50))

        # 3. 绘制药水信息 (下移至 y=80)
        # 统计药水数量
        potion_count = sum(1 for item in player.inventory.items if getattr(item, 'name', '') == "Potion")

        # 药水图标背景
        pygame.draw.rect(screen, (50, 200, 50), (20, 80, 15, 20))
        potion_text = font.render(f" x {potion_count}  (按 [H] 使用)", True, (255, 255, 255))
        screen.blit(potion_text, (45, 80))

        # 4. 绘制负重信息 (下移至 y=110)
        # 这里的 total_weight 来自 player.inventory
        weight_color = (255, 255, 255) if player.inventory.total_weight <= 10 else (255, 100, 100)
        weight_text = font.render(f"负重: {player.inventory.total_weight:.2f} kg", True, weight_color)
        screen.blit(weight_text, (20, 110))

        #  核心：绘制撤离进度条 (屏幕正中央)
        if exit_timer > 0:
            # 背景黑框
            bar_width = 300
            bar_height = 30
            bar_x = (screen.get_width() - bar_width) // 2
            bar_y = screen.get_height() // 2 + 100

            pygame.draw.rect(screen, (30, 30, 30), (bar_x, bar_y, bar_width, bar_height))
            # 进度填充
            progress = exit_timer / exit_need_time
            pygame.draw.rect(screen, (0, 191, 255), (bar_x, bar_y, int(bar_width * progress), bar_height))

            # 文字提示
            tip_text = self.font.render("正在撤离，请勿离开区域...", True, (255, 255, 255))
            screen.blit(tip_text, (bar_x + 30, bar_y - 30))

    def draw_inventory_panel(self, screen, player):
        if not player.inventory.is_open:
            return

        # 1. 绘制半透明黑色背景遮罩（让游戏背景变暗）
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # 2. 绘制背包主窗口（居中）
        pw, ph = 400, 500
        px = (screen.get_width() - pw) // 2
        py = (screen.get_height() - ph) // 2
        pygame.draw.rect(screen, (30, 30, 30), (px, py, pw, ph))
        pygame.draw.rect(screen, (150, 150, 150), (px, py, pw, ph), 2)  # 边框

        # 3. 绘制标题
        title_font = pygame.font.SysFont("SimHei", 32)
        title_surf = title_font.render("物资背包 (按 B 关闭)", True, (255, 255, 255))
        screen.blit(title_surf, (px + 20, py + 20))

        # 4. 绘制物品清单
        item_data = player.inventory.get_item_counts()
        y_offset = 80
        item_font = pygame.font.SysFont("SimHei", 20)

        for name, info in item_data.items():
            # 品质颜色小方块
            pygame.draw.rect(screen, info["color"], (px + 30, py + y_offset + 5, 12, 12))
            # 名字 x 数量
            txt = item_font.render(f"{name} x {info['count']}", True, (220, 220, 220))
            screen.blit(txt, (px + 55, py + y_offset))
            y_offset += 35

        # 5. 底部统计
        status_txt = item_font.render(f"总价值: ${player.inventory.gold} | 总重: {player.inventory.total_weight:.2f}kg",
                                      True, (255, 215, 0))
        screen.blit(status_txt, (px + 20, py + ph - 40))


    def draw_minimap(self, screen, player, tilemap):
        size = 150
        margin = 20
        map_rect = pygame.Rect(800 - size - margin, margin, size, size)

        #  绘制小地图背景
        s = pygame.Surface((size, size))
        s.set_alpha(150);
        s.fill((0, 0, 0))
        screen.blit(s, (map_rect.x, map_rect.y))

        scale_x = size / tilemap.width
        scale_y = size / tilemap.height

        for cx, cy, cw, ch in tilemap.corridors:
            cor_x = map_rect.x + (cx + tilemap.padding) * tilemap.tile_size * scale_x
            cor_y = map_rect.y + (cy + tilemap.padding) * tilemap.tile_size * scale_y
            cor_w = max(2, cw * tilemap.tile_size * scale_x)  # 确保至少可见
            cor_h = max(2, ch * tilemap.tile_size * scale_y)
            pygame.draw.rect(screen, (100, 100, 100), (cor_x, cor_y, cor_w, cor_h))

        # 绘制房间 (用明显的灰色)
        for rx, ry, rw, rh in tilemap.rooms:
            room_x = map_rect.x + (rx + tilemap.padding) * tilemap.tile_size * scale_x
            room_y = map_rect.y + (ry + tilemap.padding) * tilemap.tile_size * scale_y
            pygame.draw.rect(screen, (60, 60, 60), (room_x, room_y,
                                                    rw * tilemap.tile_size * scale_x, rh * tilemap.tile_size * scale_y))

        # 绘制撤离点 (蓝色)
        if tilemap.exit_rect:
            ex = map_rect.x + tilemap.exit_rect.x * scale_x
            ey = map_rect.y + tilemap.exit_rect.y * scale_y
            pygame.draw.rect(screen, (0, 191, 255), (ex, ey, 6, 6))

        # 4. 绘制玩家 (绿色)
        px = map_rect.x + player.rect.x * scale_x
        py = map_rect.y + player.rect.y * scale_y
        pygame.draw.circle(screen, (0, 255, 0), (int(px), int(py)), 3)

    # ui/hud.py 中新增方法

    def draw_inventory_list(self, screen, inventory):
        # 绘制背景
        rect = pygame.Rect(20, 100, 200, 300)
        pygame.draw.rect(screen, (40, 40, 40, 150), rect)

        font = pygame.font.SysFont("SimHei", 18)
        # 显示总负重
        weight_text = font.render(f"总负重: {inventory.total_weight:.2f}kg", True, (255, 255, 255))
        screen.blit(weight_text, (30, 110))

        # 显示最近捡到的 8 个物品
        for i, item in enumerate(inventory.items[-8:]):
            color = item.color
            item_text = font.render(f"{item.name} (${item.amount})", True, color)
            screen.blit(item_text, (30, 140 + i * 25))

    def draw_controls_guide(self, screen):
        """在右下角显示按键指南"""
        controls = [
            "WASD: 移动",
            "J   : 攻击",
            "K   : 开箱/交互",
            "H   : 使用药水",
            "B   : 开启/关闭背包",
        ]

        # 设定起始位置
        margin = 20
        line_height = 25
        # 计算面板高度
        panel_h = len(controls) * line_height + 20
        panel_w = 180

        # 1. 绘制半透明背景
        guide_rect = pygame.Rect(screen.get_width() - panel_w - margin,
                                 screen.get_height() - panel_h - margin,
                                 panel_w, panel_h)
        s = pygame.Surface((panel_w, panel_h))
        s.set_alpha(120)
        s.fill((0, 0, 0))
        screen.blit(s, guide_rect.topleft)

        # 2. 绘制文字
        for i, text in enumerate(controls):
            txt_surf = self.font.render(text, True, (200, 200, 200))
            screen.blit(txt_surf, (guide_rect.x + 10, guide_rect.y + 10 + i * line_height))