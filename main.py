import asyncio
import pygame
import sys
# 從 game 包中導入 game_loop_old 模組
from game.game_loop_old import main_game_loop

async def main():
    pygame.init()
    pygame.display.set_caption("The Snail Adventure")
    
    # 這裡的視窗大小需與您遊戲邏輯中的螢幕座標匹配
    screen = pygame.display.set_mode((1280, 600)) 
    clock = pygame.time.Clock()

    # 執行導入的非同步主迴圈
    # 注意：傳入 screen 和 clock 參數
    await main_game_loop(screen, clock)

if __name__ == "__main__":
    if sys.platform == "emscripten":  # 瀏覽器環境 (pygbag)
        asyncio.ensure_future(main())
    else:  # 本地 PC 環境
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            pass

# main.py

# import pygame
# import sys

# # 從 game 包中導入我們重寫好的同步主迴圈
# from game.game_loop import main_game_loop

# def main():
#     pygame.init()
#     pygame.display.set_caption("The Snail Adventure")

#     # 視窗大小要和遊戲內所有座標、背景圖設計一致
#     SCREEN_WIDTH = 1280
#     SCREEN_HEIGHT = 720  # 建議用 720p，比較常見（你原本遊戲邏輯大多假設高度 720）
#     screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

#     clock = pygame.time.Clock()
#     FPS = 60

#     # 直接呼叫同步的 main_game_loop
#     main_game_loop(screen, clock)

#     pygame.quit()
#     sys.exit()

# if __name__ == "__main__":
#     if sys.platform == "emscripten":  # 瀏覽器環境 (pygbag)
#         # pygbag 需要 asyncio 包裝
#         import asyncio
#         asyncio.ensure_future(main())
#     else:  # 本地執行（Windows/Mac/Linux）
#         main()
