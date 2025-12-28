# game/ui/level_selection.py

import pygame
import os
from ..entities import cat_types, cat_costs, cat_cooldowns

_level_selection_background_image = None
_level_selection_background_image_path = "images/background/level_selection_bg.png"

def load_level_selection_background_image(screen_width, screen_height):
    global _level_selection_background_image
    if _level_selection_background_image is None:
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            image_path = os.path.join(base_dir, _level_selection_background_image_path)
            if os.path.exists(image_path):
                image = pygame.image.load(image_path).convert()
                _level_selection_background_image = pygame.transform.scale(image, (screen_width, screen_height))
            else:
                _level_selection_background_image = None
        except pygame.error as e:
            print(f"Error loading level selection background image: {e}")
            _level_selection_background_image = None
    return _level_selection_background_image

def draw_level_selection(
    screen, levels, selected_level, selected_cats,
    font, select_font, completed_levels, cat_images,
    square_surface, unlock_cats=set()
):
    background_image = load_level_selection_background_image(screen.get_width(), screen.get_height())
    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill((30, 30, 60))

    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

    # 標題背景方塊
    screen.blit(square_surface, (40, 90))
    title = select_font.render("Select Level and Cats", True, (255, 255, 255))
    screen.blit(title, (48, 45))

    cat_rects = {}
    hovered_cats = []
    mouse_pos = pygame.mouse.get_pos()

    # === 左側：關卡列表 ===
    for i, level in enumerate(levels):
        rect = pygame.Rect(50, 100 + i * 60, 200, 50)
        is_playable = i == 0 or (i - 1) in completed_levels
        color = (100, 200, 100) if i == selected_level and is_playable else \
                (70, 140, 70) if is_playable else \
                (80, 80, 80)
        pygame.draw.rect(screen, color, rect, border_radius=12)
        pygame.draw.rect(screen, (255, 255, 255), rect, 3, border_radius=12)

        level_text = font.render(level.name if is_playable else f"{level.name} (Locked)", True, (255, 255, 255))
        screen.blit(level_text, (rect.x + 10, rect.y + 15))

    
    # === 底部：出擊陣容（嚴格按照你的邊框設定）===
    lineup_y = SCREEN_HEIGHT - 200
    lineup_height = 90
    lineup_width = SCREEN_WIDTH - 500

    # 背景與外框
    lineup_bg = pygame.Surface((lineup_width, lineup_height * 2 + 20))
    lineup_bg.set_alpha(200)
    lineup_bg.fill((20, 20, 50))
    screen.blit(lineup_bg, (200, lineup_y))
    pygame.draw.rect(screen, (0, 200, 255), (200, lineup_y, lineup_width, lineup_height * 2 + 20), 5)

    # 標題
    title_text = font.render("battle stage(press 1-0)", True, (255, 255, 100))
    screen.blit(title_text, (210, lineup_y + 10))

    # 格子設定
    slots_per_row = 5
    slot_width = 100
    slot_height = 60
    total_slots_width = slots_per_row * slot_width + (slots_per_row - 1) * 10
    start_x = 200 + (lineup_width - total_slots_width) // 2

    upper_y = lineup_y + 40
    lower_y = upper_y + lineup_height + 10

    for i in range(10):
        row = i // 5
        col = i % 5
        slot_x = start_x + col * (slot_width + 10)
        slot_y = upper_y if row == 0 else lower_y
        slot_rect = pygame.Rect(slot_x, slot_y, slot_width, slot_height)

        if i < len(selected_cats):
            cat_type = selected_cats[i]
            pygame.draw.rect(screen, (50, 100, 50), slot_rect, border_radius=10)
            pygame.draw.rect(screen, (0, 255, 0), slot_rect, 3, border_radius=10)

            if cat_type in cat_images:
                small_img = pygame.transform.scale(cat_images[cat_type], (50, 50))
                screen.blit(small_img, (slot_x + 25, slot_y + 5))

            key_num = str(i + 1) if i < 9 else "0"
            key_text = font.render(key_num, True, (255, 255, 0))
            screen.blit(key_text, (slot_x + 5, slot_y + 5))

            small_font = pygame.font.SysFont(None, 20)
            name_text = small_font.render(cat_type.replace('_', ' ').title(), True, (255, 255, 255))
            screen.blit(name_text, name_text.get_rect(center=(slot_x + slot_width // 2, slot_y + 50)))
        else:
            pygame.draw.rect(screen, (70, 70, 70), slot_rect, border_radius=10, width=3)
            empty_text = font.render("?", True, (150, 150, 150))
            screen.blit(empty_text, empty_text.get_rect(center=slot_rect.center))

    # === 右側四大按鈕（新增 Back to Menu）===
    button_width = 280
    button_height = 50
    button_x = SCREEN_WIDTH - button_width - 50
    button_spacing = 0
    button_y = SCREEN_HEIGHT - button_height - 0

    # 從上到下：Back → Reset → Quit → Start
    back_rect  = pygame.Rect(button_x, button_y - (button_height + button_spacing) * 3, button_width, button_height)
    reset_rect = pygame.Rect(button_x, button_y - (button_height + button_spacing) * 2, button_width, button_height)
    quit_rect  = pygame.Rect(button_x, button_y - (button_height + button_spacing), button_width, button_height)
    start_rect = pygame.Rect(button_x, button_y, button_width, button_height)

    # Back to Menu 按鈕（藍色系）
    pygame.draw.rect(screen, (50, 100, 200), back_rect, border_radius=15)
    pygame.draw.rect(screen, (100, 150, 255), back_rect, 5, border_radius=15)
    back_text = font.render("Back to Menu", True, (255, 255, 255))
    screen.blit(back_text, back_text.get_rect(center=back_rect.center))

    # Reset
    pygame.draw.rect(screen, (200, 50, 50), reset_rect, border_radius=15)
    pygame.draw.rect(screen, (255, 100, 100), reset_rect, 5, border_radius=15)
    reset_text = font.render("Reset Progress", True, (255, 255, 255))
    screen.blit(reset_text, reset_text.get_rect(center=reset_rect.center))

    # Quit
    pygame.draw.rect(screen, (150, 50, 50), quit_rect, border_radius=15)
    pygame.draw.rect(screen, (255, 80, 80), quit_rect, 5, border_radius=15)
    quit_text = font.render("Quit Game", True, (255, 255, 255))
    screen.blit(quit_text, quit_text.get_rect(center=quit_rect.center))

    # Start
    pygame.draw.rect(screen, (0, 150, 0), start_rect, border_radius=15)
    pygame.draw.rect(screen, (0, 255, 0), start_rect, 5, border_radius=15)
    start_text = font.render("Start Battle", True, (255, 255, 255))
    screen.blit(start_text, start_text.get_rect(center=start_rect.center))

    # 操作提示
    hint = font.render("Click cat to select (max 10) | Hover to preview | 1-0: Quick deploy", True, (200, 200, 255))
    screen.blit(hint, (300, SCREEN_HEIGHT - 95))
    # === 中間：貓咪選擇網格 ===
    idy = 0
    for cat_type in cat_types.keys():
        if cat_type not in unlock_cats:
            continue

        col = idy % 5
        row = idy // 5
        rect = pygame.Rect(270 + col * 200, 100 + row * 80, 180, 70)
        cat_rects[cat_type] = rect

        is_selected = cat_type in selected_cats
        bg_color = (100, 200, 100) if is_selected else (70, 70, 90)
        pygame.draw.rect(screen, bg_color, rect, border_radius=15)
        pygame.draw.rect(screen, (255, 255, 255), rect, 3, border_radius=15)

        name_surf = font.render(cat_type.replace('_', ' ').title(), True, (255, 255, 255))
        screen.blit(name_surf, (rect.x + 10, rect.y + 10))
        cost = cat_costs.get(cat_type, 0)
        cost_surf = font.render(f"Cost: {cost}", True, (255, 215, 0))
        screen.blit(cost_surf, (rect.x + 10, rect.y + 35))

        if is_selected:
            pygame.draw.rect(screen, (0, 255, 0), rect, 5, border_radius=15)

        if rect.collidepoint(mouse_pos):
            hovered_cats.append((cat_type, rect))
            pygame.draw.rect(screen, (255, 255, 100), rect, 5, border_radius=15)

        idy += 1

    # === 統一繪製 hover 大圖（最上層）===
    for cat_type, rect in hovered_cats:
        if cat_type in cat_images:
            cat_img = cat_images[cat_type]
            img_x = rect.x + (rect.width - cat_img.get_width()) // 2
            img_y = rect.y + 60
            screen.blit(cat_img, (img_x, img_y))

    

    pygame.display.flip()

    # 返回四個矩形 + 新增 back_rect
    return cat_rects, reset_rect, quit_rect, start_rect, back_rect