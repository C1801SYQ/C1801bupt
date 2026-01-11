import pygame
import random
from items.gold import Gold

# 定义战利品配置（参考三角洲，分为普通、蓝色、金色）
LOOT_TABLE = {
    "common": [
        {"name": "工业螺丝", "min": 50, "max": 150, "color": (200, 200, 200)},
        {"name": "打火机", "min": 20, "max": 80, "color": (200, 200, 200)}
    ],
    "rare": [
        {"name": "加密硬盘", "min": 800, "max": 1500, "color": (0, 191, 255)},
        {"name": "手术包", "min": 1200, "max": 2500, "color": (0, 191, 255)}
    ],
    "epic": [
        {"name": "曼德尔砖", "min": 10000, "max": 15000, "color": (255, 215, 0)},
        {"name": "黄金狮子", "min": 30000, "max": 50000, "color": (255, 215, 0)}
    ]
}


class Chest:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.opened = False

    def try_open(self, player_rect):
        if self.opened:
            return None

        if self.rect.colliderect(player_rect):
            self.opened = True

            # --- 随机抽取逻辑 ---
            roll = random.random()
            if roll < 0.03:  # 3% 概率出史诗
                category = "epic"
            elif roll < 0.20:  # 17% 概率出稀有
                category = "rare"
            else:  # 80% 概率出普通
                category = "common"

            # 1. 获取对应的物品数据
            item_data = random.choice(LOOT_TABLE[category])

            # 2. 随机生成价值（注意：这里对应 LOOT_TABLE 里的 min_val 和 max_val）
            amount = random.randint(item_data["min"], item_data["max"])

            # 3. 创建掉落物实体 (⭐ 传入第四个参数 item_data)
            # 这样 Gold 类内部会自动根据 amount 和 item_data 计算重量和颜色
            drop = Gold(self.rect.x, self.rect.y, amount, item_data)

            print(f"【{category.upper()}】 开出了 {drop.name}，估值: ${amount}，负重: {drop.weight:.2f}kg")
            return drop

        return None

    def draw(self, screen, camera):
        color = (139, 69, 19) if not self.opened else (80, 80, 80)
        pygame.draw.rect(screen, color, camera.apply(self))