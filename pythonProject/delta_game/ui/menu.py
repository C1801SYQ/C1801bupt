# ui/menu.py
import pygame
from core.save_manager import load_game, save_game


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("SimHei", 32)

    def draw(self):
        self.screen.fill((20, 20, 20))
        # 获取存档字典
        save_data = load_game()
        # ⭐ 提取具体的数值，而不是打印整个字典
        gold = save_data.get("total_gold", 0)
        potion_count = save_data.get("potions", 0)

        # 修改后的文字渲染
        text = self.font.render(f"仓库总资产: ${gold}", True, (255, 215, 0))
        self.screen.blit(text, (100, 100))

        # 建议顺便把药水数量也显示出来，方便玩家确认购买成功
        potion_text = self.font.render(f"持有药水: {potion_count} 瓶", True, (255, 255, 255))
        self.screen.blit(potion_text, (100, 150))

        # 商店逻辑雏形
        shop_text = self.font.render("按 B 购买药水 ($50)", True, (255, 255, 255))
        self.screen.blit(shop_text, (100, 200))

        start_text = self.font.render("按 SPACE 开始下注/进入关卡", True, (0, 255, 0))
        self.screen.blit(start_text, (100, 400))

        pygame.display.flip()

    def run(self):
        waiting = True
        while waiting:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return "play"
                    if event.key == pygame.K_b:
                        data = load_game()
                        # 确保金币和药水都有默认值，防止 KeyError
                        current_gold = data.get("total_gold", 0)
                        current_potions = data.get("potions", 0)

                        if current_gold >= 50:
                            current_gold -= 50
                            current_potions += 1
                            # 保存更新后的数据
                            save_game(current_gold, current_potions)
                            print(f"购买成功！当前金币: {current_gold}, 药水: {current_potions}")
                        else:
                            print("金币不足！")
        return "quit"