# ui/gacha_developing.py

import pygame

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