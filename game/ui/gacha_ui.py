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
    key_action_sfx=None
):
    # 這裡必須與主程式路徑一致，假設 constants 在同一級或上一級
    from ..gacha_manager import perform_gacha
    from ..constants import GACHA_COST_GOLD, GACHA_COST_SOULS, RESOURCE_FILE

    # 1. 讀取最新資源數據
    try:
        with open(RESOURCE_FILE, "r", encoding="utf-8") as f:
            player_data = json.load(f)
    except Exception as e:
        print(f"Error loading resource: {e}")
        player_data = {"gold": 0, "souls": 0}

    SCREEN_WIDTH = screen.get_width()
    SCREEN_HEIGHT = screen.get_height()

    # 2. 繪製畫面
    # 繪製背景 (gacha_bg)
    screen.blit(gacha_bg, (0, 0))

    # 顯示資源 (右上角)
    gold_text = font.render(f"Gold: {player_data.get('gold', 0)}", True, (255, 215, 0))
    soul_text = font.render(f"Souls: {player_data.get('souls', 0)}", True, (200, 100, 255))
    screen.blit(gold_text, (SCREEN_WIDTH - 250, 40))
    screen.blit(soul_text, (SCREEN_WIDTH - 250, 80))

    # 繪製轉蛋按鈕 (置中)
    btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 125, SCREEN_HEIGHT // 2 - 50, 250, 100)
    pygame.draw.rect(screen, (70, 40, 120), btn_rect, border_radius=15)
    pygame.draw.rect(screen, (255, 255, 255), btn_rect, width=3, border_radius=15)
    
    label = font.render("Roll Single", True, (255, 255, 255))
    cost = font.render(f"{GACHA_COST_GOLD}G / {GACHA_COST_SOULS}S", True, (200, 200, 200))
    screen.blit(label, label.get_rect(center=(btn_rect.centerx, btn_rect.centery - 20)))
    screen.blit(cost, cost.get_rect(center=(btn_rect.centerx, btn_rect.centery + 20)))

    # 繪製返回按鈕 (左下角)
    back_rect = pygame.Rect(50, SCREEN_HEIGHT - 100, 150, 60)
    pygame.draw.rect(screen, (150, 50, 50), back_rect, border_radius=15)
    back_text = font.render("Back", True, (255, 255, 255))
    screen.blit(back_text, back_text.get_rect(center=back_rect.center))

    # --- 重要：更新畫面 ---
    # 如果不呼叫這行，畫面會一直停留在上一個 State (選單)
    pygame.display.flip()

    # 3. 事件處理
    new_game_state = None
    # 注意：這裡會消耗掉這一幀的所有事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.event.post(event)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 點擊返回
            if back_rect.collidepoint(event.pos):
                new_game_state = "main_menu"
                if key_action_sfx and key_action_sfx.get('other_button'):
                    key_action_sfx['other_button'].play()
            
            # 點擊轉蛋
            elif btn_rect.collidepoint(event.pos):
                success, msg, _ = perform_gacha()
                if success:
                    # 簡易視覺回饋：閃爍白色
                    screen.fill((255, 255, 255))
                    pygame.display.flip()
                    if key_action_sfx and key_action_sfx.get('laser'):
                        key_action_sfx['laser'].play()
                    time.sleep(0.1) # 短暫停頓營造儀式感
                else:
                    if key_action_sfx and key_action_sfx.get('cannot_deploy'):
                        key_action_sfx['cannot_deploy'].play()
                print(f"[Gacha] {msg}")

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                new_game_state = "main_menu"

    return new_game_state