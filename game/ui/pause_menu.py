import pygame

def draw_pause_menu(screen, font, current_level):
    # 1. 繪製背景與遮罩 (這裡維持原樣)
    screen.blit(current_level.background, (0, 0))
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((50, 50, 50, 100))
    screen.blit(overlay, (0, 0))

    # 2. 設定暫停面板
    panel_width, panel_height = 400, 200
    panel_x, panel_y = 440, 200
    background_color = (100, 100, 100, 240)
    pause_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    pause_surface.fill(background_color)
    screen.blit(pause_surface, (panel_x, panel_y))

    # 計算面板的中心點座標
    center_x = panel_x + panel_width // 2  # 剛好是 640 (螢幕中線)
    center_y = panel_y + panel_height // 2 # 剛好是 300

    # 3. 建立按鈕 Rect 並對齊中心
    # 使用 Rect 的 center 屬性直接定位
    end_rect = pygame.Rect(0, 0, 200, 50)
    end_rect.center = (center_x, center_y - 40)  # 中心點往上移一點，留空間給下一個按鈕

    continue_rect = pygame.Rect(0, 0, 200, 50)
    continue_rect.center = (center_x, center_y + 40) # 中心點往下移一點

    # 4. 繪製按鈕
    pygame.draw.rect(screen, (255, 100, 100), end_rect)
    pygame.draw.rect(screen, (100, 255, 100), continue_rect)

    # 5. 繪製文字 (同樣使用文字的 center 對齊按鈕的 center)
    end_text = font.render("End Battle", True, (0, 0, 0))
    continue_text = font.render("Continue", True, (0, 0, 0))

    # 讓文字中心等於按鈕中心
    end_text_rect = end_text.get_rect(center=end_rect.center)
    continue_text_rect = continue_text.get_rect(center=continue_rect.center)

    screen.blit(end_text, end_text_rect)
    screen.blit(continue_text, continue_text_rect)

    return end_rect, continue_rect