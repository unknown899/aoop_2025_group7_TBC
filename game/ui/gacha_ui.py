# ui/gacha_developing.py

import pygame
import json
import time

def draw_gacha_developing_screen(
    screen,
    select_font,
    font,
    key_action_sfx=None
):
    """
    繪製「轉蛋系統開發中」的畫面並處理返回邏輯
    
    返回值：
        new_game_state (str | None): 
            - 如果玩家點擊「back」或按 ESC，返回 "main_menu"
            - 否則返回 None
    """
    SCREEN_WIDTH = screen.get_width()
    SCREEN_HEIGHT = screen.get_height()

    # 背景顏色（深紫色）
    screen.fill((50, 0, 100))

    # 標題
    title = select_font.render("Gacha System Developing Now!", True, (255, 255, 200))
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))

    # 小提示
    tip = font.render("Have fun!", True, (255, 255, 0))
    screen.blit(tip, (SCREEN_WIDTH // 2 - tip.get_width() // 2, 300))

    # 返回按鈕
    back_rect = pygame.Rect(50, SCREEN_HEIGHT - 100, 200, 60)
    pygame.draw.rect(screen, (200, 0, 0), back_rect, border_radius=20)
    
    back_text = font.render("Back", True, (255, 255, 255))
    screen.blit(back_text, back_text.get_rect(center=back_rect.center))

    # 更新畫面
    pygame.display.flip()

    # 事件處理
    new_game_state = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # 讓主程式處理退出
            pygame.event.post(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if back_rect.collidepoint(event.pos):
                new_game_state = "main_menu"
                if key_action_sfx and key_action_sfx.get('other_button'):
                    key_action_sfx['other_button'].play()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                new_game_state = "main_menu"
                if key_action_sfx and key_action_sfx.get('other_button'):
                    key_action_sfx['other_button'].play()

    return new_game_state


def draw_gacha_screen(
    screen,
    select_font,
    font,
    gacha_bg,
    gacha_anim_player,
    gacha_is_anim_playing,
    gacha_result,
    key_action_sfx=None
):
    from ..gacha_manager import perform_gacha
    from ..constants import GACHA_COST_GOLD, GACHA_COST_SOULS, RESOURCE_FILE

    SCREEN_WIDTH = screen.get_width()
    SCREEN_HEIGHT = screen.get_height()

    # -------------------------
    # 讀取資源
    # -------------------------
    try:
        with open(RESOURCE_FILE, "r", encoding="utf-8") as f:
            player_data = json.load(f)
    except:
        player_data = {"gold": 0, "souls": 0}

    # -------------------------
    # 畫面繪製
    # -------------------------
    screen.blit(gacha_bg, (0, 0))

    gold_text = font.render(f"Gold: {player_data['gold']}", True, (255, 215, 0))
    soul_text = font.render(f"Souls: {player_data['souls']}", True, (200, 100, 255))
    screen.blit(gold_text, (SCREEN_WIDTH - 250, 40))
    screen.blit(soul_text, (SCREEN_WIDTH - 250, 80))

    # 轉蛋按鈕
    btn_rect = pygame.Rect(
        SCREEN_WIDTH // 2 - 125,
        SCREEN_HEIGHT // 2 - 50,
        250,
        100
    )
    pygame.draw.rect(screen, (70, 40, 120), btn_rect, border_radius=15)
    pygame.draw.rect(screen, (255, 255, 255), btn_rect, 3, border_radius=15)

    label = font.render("Roll Single", True, (255, 255, 255))
    screen.blit(label, label.get_rect(center=btn_rect.center))

    # 返回
    back_rect = pygame.Rect(50, SCREEN_HEIGHT - 100, 150, 60)
    pygame.draw.rect(screen, (150, 50, 50), back_rect, border_radius=15)
    back_text = font.render("Back", True, (255, 255, 255))
    screen.blit(back_text, back_text.get_rect(center=back_rect.center))

    # -------------------------
    # 播放動畫
    # -------------------------
    current_time = pygame.time.get_ticks()
    if gacha_is_anim_playing:
        still_playing = gacha_anim_player.draw(screen, current_time)
        if not still_playing:
            gacha_is_anim_playing = False

    # -------------------------
    # 顯示結果
    # -------------------------
    if not gacha_is_anim_playing and gacha_result:
        msg = gacha_result["msg"]
        text = select_font.render(msg, True, (255, 255, 0))
        screen.blit(
            text,
            text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 140))
        )

    pygame.display.flip()

    # -------------------------
    # 事件處理
    # -------------------------
    new_game_state = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            new_game_state = "quit"

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if back_rect.collidepoint(event.pos):
                new_game_state = "main_menu"

            elif btn_rect.collidepoint(event.pos):
                if gacha_is_anim_playing:
                    continue

                success, result = perform_gacha()
                if success:
                    gacha_result = result
                    gacha_is_anim_playing = True
                    gacha_anim_player.start(pygame.time.get_ticks())

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                new_game_state = "main_menu"

    # 🔴 重點：把狀態「傳回去」
    return new_game_state, gacha_is_anim_playing, gacha_result