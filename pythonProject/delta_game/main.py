# main.py
import pygame
from core.game import Game
from ui.menu import MainMenu
from ui.result_screen import ResultScreen

# main.py

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    state = "menu"  # 初始状态是大厅

    while state != "quit":
        if state == "menu":
            menu = MainMenu(screen)
            state = menu.run()  # 当 menu.run 返回 "play" 时进入游戏


        elif state == "play":
            game = Game(screen)
            game.run()
            # ⭐ 新增：弹出结算页面
            # 假设你在 game 结束时保存了本次收益 current_session_gold
            result = ResultScreen(screen, game.status, game.session_gold)
            result.display()

            state = "menu"

    pygame.quit()
if __name__ == "__main__":
    main()