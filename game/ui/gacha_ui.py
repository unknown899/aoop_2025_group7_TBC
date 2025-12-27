# ui/gacha_developing.py

import pygame
import json
import time

from ..gacha_manager import perform_gacha
from ..constants import GACHA_COST_GOLD, GACHA_COST_SOULS, RESOURCE_FILE, gacha_bg, gacha_afterbg


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
    gacha_anim_player,
    gacha_is_anim_playing,
    gacha_result,
    gacha_is_fading,
    gacha_show_result,
    gacha_fade_alpha,
    key_action_sfx=None
):
    
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
    if gacha_show_result or gacha_is_fading:
        screen.blit(gacha_afterbg, (0, 0))  # 或另一張 result_bg
    elif not gacha_is_fading and not gacha_is_anim_playing:
        screen.blit(gacha_bg, (0, 0))

    gold_text = select_font.render(f"Gold: {player_data['gold']}", True, (255, 215, 0))
    soul_text = select_font.render(f"Souls: {player_data['souls']}", True, (200, 100, 255))
    screen.blit(gold_text, (SCREEN_WIDTH - 610, 553))
    screen.blit(soul_text, (SCREEN_WIDTH - 300, 553))
    

    # 轉蛋按鈕
    btn_rect = pygame.Rect(
        SCREEN_WIDTH - 270,
        SCREEN_HEIGHT - 170,
        250,
        100
    )
    if not gacha_is_anim_playing and not gacha_is_fading and not gacha_show_result:
        pygame.draw.rect(screen, (70, 40, 120), btn_rect, border_radius=15)
        pygame.draw.rect(screen, (255, 255, 255), btn_rect, 3, border_radius=15)

        # 1. 原有的 "Roll Single" 文字
        label = font.render("Roll Single", True, (255, 255, 255))
        # 將中心點往上移動一點 (例如 -10)，給下方的資訊留空間
        label_rect = label.get_rect(center=(btn_rect.centerx, btn_rect.centery - 10))
        screen.blit(label, label_rect)

        # 2. 新增的資源消耗文字 (使用較小的字體或直接渲染)
        cost_text = f"Gold: -{GACHA_COST_GOLD}, Soul: -{GACHA_COST_SOULS}"
        # 建議可以用稍微小一點的字體，這裡先假設使用同一個 font
        cost_label = font.render(cost_text, True, (255, 0, 0)) # 顏色稍微調淡一點
        # 將中心點往下移動 (例如 +15)
        cost_rect = cost_label.get_rect(center=(btn_rect.centerx, btn_rect.centery + 15))
        screen.blit(cost_label, cost_rect)

        # 返回
        back_rect = pygame.Rect(40, SCREEN_HEIGHT - 120, 150, 60)
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
            gacha_is_fading = True
            gacha_fade_alpha = 255

    if gacha_is_fading:
        white = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        white.fill((255, 255, 255))
        white.set_alpha(gacha_fade_alpha)
        screen.blit(white, (0, 0))

        gacha_fade_alpha -= 8   # 調整淡出速度
        if gacha_fade_alpha <= 0:
            gacha_is_fading = False
            gacha_show_result = True
    
    
    

    if gacha_show_result and gacha_result:

        msg = gacha_result["msg"]
        is_win = gacha_result["won_id"] is not None

        if is_win:
            # 顯示貓咪圖片
            cat_img = pygame.image.load(
                f"./cat_folder/{gacha_result['won_id']}/cat_gacha.png"
            ).convert_alpha()

            new_size = (400, int(cat_img.get_height() * 400/cat_img.get_width()))
            cat_img = pygame.transform.scale(cat_img, new_size)
            
            cat_rect = cat_img.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
            )
            screen.blit(cat_img, cat_rect)

            # 大字 msg
            text = select_font.render(msg, True, (255, 215, 0))
            screen.blit(
                text,
                text.get_rect(
                    center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 140)
                )
            )
        else:
            fail_img = pygame.image.load(
                f"./images/fail_img.jpg"
            ).convert_alpha()

            new_size = (300, int(fail_img.get_height() * 300/fail_img.get_width()))
            fail_img = pygame.transform.scale(fail_img, new_size)
            
            fail_rect = fail_img.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 -10)
            )
            screen.blit(fail_img, fail_rect)
            # 大字 msg
            text = select_font.render(msg, True, (255, 0, 0))#different color for no win
            screen.blit(
                text,
                text.get_rect(
                    center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150)
                )
            )
        hint = font.render("Press ENTER to continue", True, (216, 246, 144))
        if is_win:
            screen.blit(
                hint,
                hint.get_rect(
                    center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)
                )
            )
        else:
            screen.blit(
                hint,
                hint.get_rect(
                    center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 75)
                )
            )
    '''
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
    '''
    pygame.display.flip()

    # -------------------------
    # 事件處理
    # -------------------------
    new_game_state = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            new_game_state = "quit"

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if gacha_is_anim_playing or gacha_is_fading or gacha_show_result: 
                    continue
            if back_rect.collidepoint(event.pos):
                new_game_state = "main_menu"

            elif btn_rect.collidepoint(event.pos):

                success, result = perform_gacha()
                if success:
                    gacha_result = result
                    gacha_is_anim_playing = True
                    gacha_anim_player.start(pygame.time.get_ticks())
                elif not success and result["msg"] == "Insufficient Resources!":
                    new_game_state = "recharge"   # ← 交給主程式切 state

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                new_game_state = "main_menu"

            if event.key == pygame.K_RETURN and gacha_show_result:
                # reset 狀態
                gacha_show_result = False
                gacha_result = None

    return new_game_state, gacha_is_anim_playing, gacha_result, gacha_is_fading, gacha_show_result, gacha_fade_alpha