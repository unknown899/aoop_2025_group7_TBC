import asyncio
import pygame
import sys
# 從 game 包中導入 game_loop_old 模組
from game.game_loop import main_game_loop

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

# import asyncio
# import pygame
# import sys
# # 從 game 包中導入 game_loop_old 模組
# from game.game_loop import main_game_loop

# async def main():
#     pygame.init()
#     pygame.display.set_caption("The Snail Adventure")
    
#     # 這裡的視窗大小需與您遊戲邏輯中的螢幕座標匹配
#     screen = pygame.display.set_mode((1280, 600)) 
#     clock = pygame.time.Clock()

#     # 執行導入的非同步主迴圈
#     # 注意：傳入 screen 和 clock 參數
#     await main_game_loop(screen, clock)

# if __name__ == "__main__":
#     if sys.platform == "emscripten":  # 瀏覽器環境 (pygbag)
#         asyncio.ensure_future(main())
#     else:  # 本地 PC 環境
#         try:
#             asyncio.run(main())
#         except KeyboardInterrupt:
#             pass

