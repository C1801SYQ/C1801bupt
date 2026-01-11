# ui/result_screen.py
import pygame


class ResultScreen:
    def __init__(self, screen, status, gold_earned):
        self.screen = screen
        self.status = status  # "win" 或 "dead"
        self.gold = gold_earned

        # ⭐ 修复：定义 display 中需要用到的所有字体
        self.font = pygame.font.SysFont("SimHei", 32)
        self.big_font = pygame.font.SysFont("SimHei", 64)  # 之前漏掉了这个

    def display(self):
        waiting = True
        while waiting:
            self.screen.fill((10, 10, 10))

            # 颜色逻辑
            title_color = (0, 255, 0) if self.status == "win" else (255, 0, 0)
            title_text = "顺利撤离！" if self.status == "win" else "不幸牺牲..."

            # 渲染文字 - 现在 self.big_font 已经存在了
            t_surf = self.big_font.render(title_text, True, title_color)
            g_surf = self.font.render(f"本次带回资产: ${self.gold}", True, (255, 215, 0))
            hint_surf = self.font.render("按 任意键 回到大厅", True, (200, 200, 200))

            # 居中逻辑
            sw, sh = self.screen.get_size()
            self.screen.blit(t_surf, (sw // 2 - t_surf.get_width() // 2, sh // 2 - 100))
            self.screen.blit(g_surf, (sw // 2 - g_surf.get_width() // 2, sh // 2))
            self.screen.blit(hint_surf, (sw // 2 - hint_surf.get_width() // 2, sh // 2 + 100))

            pygame.display.flip()

            # 事件监听：按键后退出 display 循环，回到 main.py 的逻辑
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False