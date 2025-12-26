import pygame

from ..entities import cat_types, cat_costs, cat_cooldowns

# game/ui.py（draw_game_ui 函數）

import pygame

def draw_game_ui(screen, current_level, current_budget, enemy_tower, current_time, level_start_time,
                 selected_cats, last_spawn_time, button_rects, font, cat_key_map, budget_font, camera_offset_x,
                 wallet_level=None, wallet_upgrade_table = None, player_resources = None):
    """
    繪製遊戲 UI，包括：
    - 背景
    - 預算
    - 暫停按鈕
    - 出貓按鈕（含成本、冷卻條、快捷鍵）
    - 錢包升級系統（等級、上限、生錢速度、升級按鈕）
    """
    SCREEN_WIDTH = screen.get_width()
    SCREEN_HEIGHT = screen.get_height()

    # 背景（只顯示可見部分）
    bg_width = current_level.background.get_width()
    camera_offset_x = max(0, min(camera_offset_x, bg_width - SCREEN_WIDTH))
    screen.blit(current_level.background, (0, 0), (camera_offset_x, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    # === 錢包升級系統 UI（左上角）===
    if wallet_upgrade_table and wallet_level <= len(wallet_upgrade_table):
        current_stats = wallet_upgrade_table[wallet_level - 1]
    else:
        current_stats = {"max_budget": 16500, "budget_rate": 55}
    if wallet_level == None:
        wallet_level = 8
    if wallet_upgrade_table == None:
        wallet_upgrade_table = [
            {"level": 1, "max_budget": 6000, "budget_rate": 20, "upgrade_cost": 280},
            {"level": 2, "max_budget": 7500, "budget_rate": 25, "upgrade_cost": 560},
            {"level": 3, "max_budget": 9000, "budget_rate": 30, "upgrade_cost": 840},
            {"level": 4, "max_budget": 10500, "budget_rate": 35, "upgrade_cost": 1120},
            {"level": 5, "max_budget": 12000, "budget_rate": 40, "upgrade_cost": 1400},
            {"level": 6, "max_budget": 13500, "budget_rate": 45, "upgrade_cost": 1680},
            {"level": 7, "max_budget": 15000, "budget_rate": 50, "upgrade_cost": 1960},
            {"level": 8, "max_budget": 16500, "budget_rate": 55, "upgrade_cost": 0}
        ]
    wallet_title = budget_font.render(f"wallet Lv.{wallet_level}", True, (255, 215, 0))
    # limit_text = budget_font.render(f"Max {current_stats['max_budget']}", True, (200, 200, 255))
    # rate_text = budget_font.render(f"生錢: +{current_stats['budget_rate']}/0.333s", True, (100, 255, 100))
    screen.blit(wallet_title, (50, 50))
    # screen.blit(limit_text, (50, 90))
    # screen.blit(rate_text, (50, 130))

    upgrade_rect = None
    if wallet_level < len(wallet_upgrade_table):
        next_stats = wallet_upgrade_table[wallet_level]
        upgrade_cost = next_stats["upgrade_cost"]
        upgrade_rect = pygame.Rect(50, 180, 240, 70)

        can_upgrade = current_budget >= upgrade_cost
        btn_color = (0, 180, 0) if can_upgrade else (80, 80, 80)
        border_color = (0, 255, 0) if can_upgrade else (120, 120, 120)

        pygame.draw.rect(screen, btn_color, upgrade_rect, border_radius=15)
        pygame.draw.rect(screen, border_color, upgrade_rect, 4, border_radius=15)

        cost_text = budget_font.render(f"upgrade {upgrade_cost} costs", True, (255, 255, 255))
        next_text = budget_font.render(f"Lv.{wallet_level + 1}", True, (0, 255, 255))
        screen.blit(cost_text, (upgrade_rect.x + 10, upgrade_rect.y + 10))
        screen.blit(next_text, (upgrade_rect.x + 10, upgrade_rect.y + 40))
    else:
        max_text = budget_font.render("Max", True, (255, 100, 100))
        screen.blit(max_text, (50, 180))

    # === 預算顯示（右上角）===
    budget_text = budget_font.render(f"Budget: {current_budget}/{current_stats['max_budget']}", True, (255, 215, 0))
    screen.blit(budget_text, (SCREEN_WIDTH - budget_text.get_width() - 50, 10))

    # === 暫停按鈕（右上角）===
    pause_rect = pygame.Rect(SCREEN_WIDTH - 200, 50, 150, 50)
    pygame.draw.rect(screen, (100, 100, 255), pause_rect, border_radius=15)
    pause_text = font.render("Pause", True, (255, 255, 255))
    screen.blit(pause_text, (pause_rect.x + 40, pause_rect.y + 15))

    # === 出貓按鈕（中間偏左）===
    button_x_start = 300
    button_y_start = 50
    button_spacing_x = 120
    button_spacing_y = 70
    max_buttons_per_row = 5
    calculated_button_rects = {}

    for idx, cat_type in enumerate(selected_cats):
        row = idx // max_buttons_per_row
        col = idx % max_buttons_per_row
        rect_x = button_x_start + col * button_spacing_x
        rect_y = button_y_start + row * button_spacing_y
        rect = pygame.Rect(rect_x, rect_y, 100, 60)
        calculated_button_rects[cat_type] = rect

    for cat_type, rect in calculated_button_rects.items():
        cost = cat_costs.get(cat_type, 0)
        cooldown = cat_cooldowns.get(cat_type, 0)
        time_since_last_spawn = current_time - last_spawn_time.get(cat_type, 0)

        # 判斷按鈕顏色
        color = (0, 255, 0) if current_budget >= cost else (200, 200,  200, 200)
        if cooldown > 0 and time_since_last_spawn < cooldown:
            color = (150, 150, 150)

        pygame.draw.rect(screen, color, rect, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2, border_radius=10)

        # 貓名
        name_text = font.render(cat_type.replace('_', ' ').title(), True, (0, 0, 0))
        screen.blit(name_text, (rect.x + 5, rect.y + 5))

        # 成本
        cost_text = font.render(f"${cost}", True, (255, 215, 0))
        screen.blit(cost_text, (rect.x + 5, rect.y + 25))

        # 快捷鍵
        key = next((k for k, v in cat_key_map.items() if v == cat_type), None)
        key_str = pygame.key.name(key).upper() if key else "N/A"
        key_text = font.render(f"[{key_str}]", True, (255, 255, 255))
        screen.blit(key_text, (rect.x + 60, rect.y + 25))

        # 冷卻條
        if cooldown > 0 and time_since_last_spawn < cooldown:
            cooldown_remaining = max(0, cooldown - time_since_last_spawn)
            cooldown_percentage = cooldown_remaining / cooldown
            bar_height = 8
            bar_width = rect.width - 10
            bar_x = rect.x + 5
            bar_y = rect.y + rect.height - bar_height - 5

            pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
            fill_width = int(bar_width * cooldown_percentage)
            pygame.draw.rect(screen, (255, 100, 100), (bar_x, bar_y, fill_width, bar_height))
            pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 1)

    # 更新外部 button_rects
    button_rects.clear()
    button_rects.update(calculated_button_rects)

    # 返回值
    return pause_rect, calculated_button_rects, camera_offset_x, upgrade_rect  # 多返回一個 upgrade_rect 供點擊判斷