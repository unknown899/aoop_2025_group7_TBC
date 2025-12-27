import pygame

from ..entities import cat_types, cat_costs, cat_cooldowns

# game/ui.py（draw_game_ui 函數）
def draw_game_ui(screen, current_level, current_budget, enemy_tower, current_time, level_start_time,
                 selected_cats, last_spawn_time, button_rects, font, cat_key_map, budget_font, camera_offset_x,
                 wallet_level=None, wallet_upgrade_table=None, player_resources=None, cat_images=None):
    """
    繪製遊戲 UI - 出擊格子大小與 level_selection.py 完全一致（180x70），文字加黑描邊
    """
    if cat_images is None:
        cat_images = {}

    SCREEN_WIDTH = screen.get_width()
    SCREEN_HEIGHT = screen.get_height()

    # 背景（隨相機）
    bg_width = current_level.background.get_width()
    camera_offset_x = max(0, min(camera_offset_x, bg_width - SCREEN_WIDTH))
    screen.blit(current_level.background, (0, 0), (camera_offset_x, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    # === 預算顯示（右上角）===
    current_max = wallet_upgrade_table[wallet_level - 1]["max_budget"] if wallet_upgrade_table and wallet_level <= len(wallet_upgrade_table) else 16500
    budget_text = budget_font.render(f"budget: {current_budget}/{current_max}", True, (255, 215, 0))
    screen.blit(budget_text, (SCREEN_WIDTH - budget_text.get_width() - 50, 20))

    # === 最下方整條：出擊陣容（格子大小與選貓畫面一致）===
    bottom_bar_y = SCREEN_HEIGHT - 160
    bottom_bar_height = 180
    bottom_bar_width = SCREEN_WIDTH - 500

    # 背景與外框（與 level_selection 一致）
    # lineup_bg = pygame.Surface((bottom_bar_width, bottom_bar_height))
    # lineup_bg.set_alpha(200)
    # lineup_bg.fill((20, 20, 50))
    # screen.blit(lineup_bg, (200, bottom_bar_y))
    # pygame.draw.rect(screen, (0, 200, 255), (200, bottom_bar_y, bottom_bar_width, bottom_bar_height), 5)

    # 標題
    # title_text = font.render("出擊陣容 (快捷鍵 1-0)", True, (255, 255, 100))
    # screen.blit(title_text, (210, bottom_bar_y + 10))

    # 格子參數（與 level_selection 完全一致）
    slot_width = 120
    slot_height = 60
    slot_spacing = 5
    slots_per_row = 5
    total_slots_width = slots_per_row * slot_width + (slots_per_row - 1) * slot_spacing
    start_x = 200 + (bottom_bar_width - total_slots_width) // 2

    upper_y = bottom_bar_y + 40
    lower_y = upper_y + slot_height + 2

    calculated_button_rects = {}

# 繪製 10 個格子（上下兩排）
    for i in range(10):
        row = 0 if i < 5 else 1
        col = i % 5
        slot_x = start_x + col * (slot_width + slot_spacing)
        slot_y = upper_y if row == 0 else lower_y
        slot_rect = pygame.Rect(slot_x, slot_y, slot_width, slot_height)

        # 儲存為出貓按鈕（只有已選貓咪才有）
        if i < len(selected_cats):
            cat_type = selected_cats[i]
            calculated_button_rects[cat_type] = slot_rect

        if i < len(selected_cats):
            cat_type = selected_cats[i]
            cost = cat_costs.get(cat_type, 0)
            cooldown = cat_cooldowns.get(cat_type, 0)
            time_since = current_time - last_spawn_time.get(cat_type, 0)

            # 判斷格子狀態
            on_cooldown = cooldown > 0 and time_since < cooldown
            cannot_afford = current_budget < cost

            if on_cooldown or cannot_afford:
                # 冷卻中 或 錢不夠 → 灰色
                bg_color = (80, 80, 80)
                border_color = (150, 150, 150)
            else:
                # 可出擊 → 綠色
                bg_color = (50, 100, 50)
                border_color = (0, 255, 0)

            # 畫格子背景與邊框
            pygame.draw.rect(screen, bg_color, slot_rect, border_radius=15)
            pygame.draw.rect(screen, border_color, slot_rect, 3, border_radius=15)

            # 小圖片（稍微變暗如果不可用）
            if cat_type in cat_images:
                small_img = pygame.transform.scale(cat_images[cat_type], (50, 50))
                if on_cooldown or cannot_afford:
                    # 加灰色遮罩表示不可用
                    overlay = pygame.Surface((50, 50), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 100))  # 半透明黑
                    small_img.blit(overlay, (0, 0))
                screen.blit(small_img, (slot_x + 10, slot_y + 10))

            # 快捷鍵數字
            key_num = str(i + 1) if i < 9 else "0"
            key_color = (200, 200, 200) if on_cooldown or cannot_afford else (255, 255, 0)
            key_text = font.render(key_num, True, key_color)
            screen.blit(key_text, (slot_x + 70, slot_y + 10))

            # 名稱（不可用時變灰）
            name_str = cat_type.replace('_', ' ').title()
            name_color = (180, 180, 180) if on_cooldown or cannot_afford else (255, 255, 255)
            name_surf = font.render(name_str, True, name_color)
            # 黑描邊（讓文字更清楚）
            outline_offsets = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
            for dx, dy in outline_offsets:
                outline = font.render(name_str, True, (0, 0, 0))
                screen.blit(outline, (slot_x + 10 + dx, slot_y + 35 + dy))
            screen.blit(name_surf, (slot_x + 10, slot_y + 35))

            # 成本（不可用時變紅/灰）
            cost_color = (150, 150, 150) if cannot_afford else (255, 215, 0)
            cost_str = f"$ {cost}"
            cost_surf = font.render(cost_str, True, cost_color)
            cost_x = slot_x + slot_width - cost_surf.get_width() - 10
            cost_y = slot_y + 35
            for dx, dy in outline_offsets:
                outline = font.render(cost_str, True, (0, 0, 0))
                screen.blit(outline, (cost_x + dx, cost_y + dy))
            screen.blit(cost_surf, (cost_x, cost_y))

            # 冷卻條（只有冷卻中才顯示）
            if on_cooldown:
                progress = time_since / cooldown
                bar_w = slot_width - 20
                bar_y = slot_y + slot_height - 15
                pygame.draw.rect(screen, (100, 0, 0), (slot_x + 10, bar_y, bar_w, 10))
                pygame.draw.rect(screen, (0, 255, 0), (slot_x + 10, bar_y, int(bar_w * progress), 10))
                pygame.draw.rect(screen, (255, 255, 255), (slot_x + 10, bar_y, bar_w, 10), 2)

        else:
            # 未選位置：灰色虛框
            pygame.draw.rect(screen, (70, 70, 70), slot_rect, border_radius=15, width=3)
            empty_text = font.render("?", True, (150, 150, 150))
            screen.blit(empty_text, empty_text.get_rect(center=slot_rect.center))

    # 更新出貓按鈕矩形
    button_rects.clear()
    button_rects.update(calculated_button_rects)

    # === 錢包升級按鈕（左下角，三種狀態兩張圖）===
    wallet_x = -10
    wallet_y = bottom_bar_y + 50
    wallet_rect = pygame.Rect(wallet_x, wallet_y, 120, 120)
    upgrade_rect = wallet_rect

    available_icon = None
    unavailable_icon = None

    try:
        available_icon = pygame.image.load("images/ui/wallet_upgrade_available.png").convert_alpha()
    except:
        pass

    try:
        unavailable_icon = pygame.image.load("images/ui/wallet_upgrade_unavailable.png").convert_alpha()
    except:
        pass

    if wallet_level < len(wallet_upgrade_table):
        next_cost = wallet_upgrade_table[wallet_level]["upgrade_cost"]
        can_upgrade = current_budget >= next_cost

        if can_upgrade:
            icon_to_use = available_icon
            bg_color = (0, 150, 0)
            border_color = (0, 255, 0)
        else:
            icon_to_use = unavailable_icon
            bg_color = (60, 60, 60)
            border_color = (150, 150, 150)

        pygame.draw.rect(screen, bg_color, wallet_rect, border_radius=25)
        pygame.draw.rect(screen, border_color, wallet_rect, 8, border_radius=25)

        if icon_to_use:
            icon_scaled = pygame.transform.scale(icon_to_use, (90, 90))
            screen.blit(icon_scaled, icon_scaled.get_rect(center=wallet_rect.center))
        else:
            # fallback 文字
            title_surf = budget_font.render(f"Lv.{wallet_level}", True, (255, 215, 0))
            cost_surf = font.render(f"升級 {next_cost} 金幣", True, (255, 255, 255) if can_upgrade else (255, 100, 100))
            next_surf = font.render(f"→ Lv.{wallet_level + 1}", True, (0, 255, 255))
            screen.blit(title_surf, title_surf.get_rect(centerx=wallet_rect.centerx, y=wallet_y + 20))
            screen.blit(cost_surf, cost_surf.get_rect(centerx=wallet_rect.centerx, y=wallet_y + 60))
            screen.blit(next_surf, next_surf.get_rect(centerx=wallet_rect.centerx, y=wallet_y + 90))

        if can_upgrade:
            pygame.draw.rect(screen, (0, 255, 0), wallet_rect, 4, border_radius=25)
    else:
        # 滿級
        pygame.draw.rect(screen, (100, 50, 50), wallet_rect, border_radius=25)
        pygame.draw.rect(screen, (255, 100, 100), wallet_rect, 8, border_radius=25)
        if available_icon:
            icon_scaled = pygame.transform.scale(available_icon, (90, 90))
            screen.blit(icon_scaled, icon_scaled.get_rect(center=wallet_rect.center))
        else:
            max_surf = budget_font.render("MAX", True, (255, 255, 255))
            screen.blit(max_surf, max_surf.get_rect(center=wallet_rect.center))

    # === 暫停按鈕（右上角）===
    pause_rect = pygame.Rect(SCREEN_WIDTH - 100, 40, 80, 80)

    try:
        pause_icon = pygame.image.load("images/ui/pause_icon.png").convert_alpha()
        icon_scaled = pygame.transform.scale(pause_icon, (60, 60))
        pygame.draw.rect(screen, (100, 100, 255), pause_rect, border_radius=20)
        pygame.draw.rect(screen, (200, 200, 255), pause_rect, 6, border_radius=20)
        screen.blit(icon_scaled, icon_scaled.get_rect(center=pause_rect.center))
    except:
        pygame.draw.rect(screen, (100, 100, 255), pause_rect, border_radius=20)
        pygame.draw.rect(screen, (200, 200, 255), pause_rect, 6, border_radius=20)
        pause_surf = budget_font.render("pulse", True, (255, 255, 255))
        screen.blit(pause_surf, pause_surf.get_rect(center=pause_rect.center))

    return pause_rect, calculated_button_rects, camera_offset_x, upgrade_rect