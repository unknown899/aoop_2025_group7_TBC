# game/ui/map_menu.py
import pygame
from game.ui.map_level import draw_map_level_selection
from game.ui.gacha_ui import gacha_ui

def draw_battle_gacha(screen, clock):
    """
    畫 Battle 與 Gacha 按鈕，並回傳兩個按鈕的 Rect。
    """
    font = pygame.font.Font(None, 48)

    screen.fill((180, 200, 255))

    battle_text = font.render("⚔️ Battle", True, (0, 0, 0))
    battle_button_rect = battle_text.get_rect(topleft=(500, 200))

    gacha_text = font.render("🎁 Gacha", True, (0, 0, 0))
    gacha_button_rect = gacha_text.get_rect(topleft=(500, 300))

    screen.blit(battle_text, battle_button_rect.topleft)
    screen.blit(gacha_text, gacha_button_rect.topleft)

    pygame.display.flip()

    return battle_button_rect, gacha_button_rect


def battle_gacha_loop(screen, clock):
    """
    Battle/Gacha 選單的事件迴圈。
    點擊 Battle 會進入關卡選單，點擊 Gacha 會進入抽卡畫面。
    """
    running = True
    while running:
        battle_rect, gacha_rect = draw_battle_gacha(screen, clock)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if battle_rect.collidepoint(event.pos):
                    # 點擊 Battle -> 進入地圖選單
                    return "map_level"
                elif gacha_rect.collidepoint(event.pos):
                    # 點擊 Gacha -> 進入抽卡 UI
                    return "gacha"

        clock.tick(60)
