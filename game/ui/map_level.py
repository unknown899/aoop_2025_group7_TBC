# game/ui/map_level.py

import pygame
import os
from game.entities import levels  # 你的關卡列表
from game.rewards import LEVEL_REWARDS  # 獎勵表
from game.game_loop import claimed_first_clear  # first_clear 領取記錄（需從 game_loop 傳入或設為 global）

_level_selection_background_image = None
_level_selection_background_image_path = "images/background/level_selection_bg.png"

# 關卡圖標位置（自動計算）
level_icon_positions = {}

def load_map_level_selection_background_image(screen_width, screen_height):
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

def draw_map_level_selection(screen, selected_level=0, completed_levels=set(), claimed_first_clear=None):
    """
    繪製關卡選擇地圖
    返回：(selected_idx, new_state, hovered_idx)
    - selected_idx: 確認選擇的關卡（點擊或 Enter）
    - new_state: "main_menu" 或 None
    - hovered_idx: 當前懸停的關卡（用於預覽）
    """
    if claimed_first_clear is None:
        claimed_first_clear = {"0": [[], []], "1": [[], []], "2": [[], []], "3": [[], []], "4": [[], []]}

    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
    background_image = load_map_level_selection_background_image(SCREEN_WIDTH, SCREEN_HEIGHT)
    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill((30, 30, 60))

    # 圖標設定
    icon_radius = 35
    font_large = pygame.font.SysFont(None, 48)
    font_normal = pygame.font.SysFont(None, 32)
    font_small = pygame.font.SysFont(None, 26)

    # 自動計算位置（5xN 網格）
    global level_icon_positions
    if not level_icon_positions:
        cols = 5
        margin_x, margin_y = 150, 150
        spacing_x, spacing_y = 220, 180
        for i in range(len(levels)):
            row = i // cols
            col = i % cols
            x = margin_x + col * spacing_x
            y = margin_y + row * spacing_y
            level_icon_positions[i] = (x, y)

    # 滑鼠位置與懸停偵測
    mouse_pos = pygame.mouse.get_pos()
    hovered_idx = None
    level_rects = {}

    # 繪製所有關卡圖標
    for idx, (x, y) in level_icon_positions.items():
        rect = pygame.Rect(x - icon_radius, y - icon_radius, icon_radius * 2, icon_radius * 2)
        level_rects[idx] = rect

        # 顏色判斷
        if idx == selected_level:
            color = (255, 255, 0)  # 黃色：選中
            border_width = 8
        elif idx in completed_levels:
            color = (100, 255, 100)  # 綠色：已完成
            border_width = 5
        else:
            color = (200, 200, 200)  # 灰色：未完成
            border_width = 5

        # 懸停高亮
        if rect.collidepoint(mouse_pos):
            hovered_idx = idx
            pygame.draw.circle(screen, (255, 255, 255), (x, y), icon_radius + 10, 6)

        pygame.draw.circle(screen, color, (x, y), icon_radius)
        pygame.draw.circle(screen, (0, 0, 0), (x, y), icon_radius, border_width)

        # 關卡編號
        num_text = font_large.render(str(idx + 1), True, (0, 0, 0))
        screen.blit(num_text, num_text.get_rect(center=(x, y)))

    # === 懸停預覽框 ===
    if hovered_idx is not None:
        level = levels[hovered_idx]
        reward_data = LEVEL_REWARDS.get(hovered_idx, {})

        preview_x = SCREEN_WIDTH - 420
        preview_y = SCREEN_HEIGHT - 380
        preview_w, preview_h = 400, 360

        # 半透明背景
        s = pygame.Surface((preview_w, preview_h))
        s.set_alpha(230)
        s.fill((10, 10, 40))
        screen.blit(s, (preview_x, preview_y))
        pygame.draw.rect(screen, (0, 200, 255), (preview_x, preview_y, preview_w, preview_h), 4)

        # 標題
        title = font_normal.render(f"關卡 {hovered_idx + 1}: {level.name}", True, (255, 255, 100))
        screen.blit(title, (preview_x + 20, preview_y + 20))

        y_off = preview_y + 70

        # 每次通關獎勵
        repeatable = reward_data.get("repeatable", [])
        if repeatable:
            header = font_normal.render("每次通關：", True, (100, 255, 100))
            screen.blit(header, (preview_x + 20, y_off))
            y_off += 35
            for item in repeatable:
                g = item.get("gold", 0)
                s = item.get("souls", 0)
                text = f"+{g} Gold + {s} Souls"
                surf = font_small.render(text, True, (200, 255, 200))
                screen.blit(surf, (preview_x + 40, y_off))
                y_off += 28

        # 首次通關獎勵
        first_clear = reward_data.get("first_clear", [])
        if first_clear:
            header = font_normal.render("首次通關獎勵：", True, (255, 200, 100))
            screen.blit(header, (preview_x + 20, y_off))
            y_off += 35
            claimed_list = claimed_first_clear.get(str(hovered_idx), [[], []])[0]
            for idx, item in enumerate(first_clear):
                chance = item.get("weight", 0)
                reward = item.get("reward", {})
                g = reward.get("gold", 0)
                s = reward.get("souls", 0)
                unlock = reward.get("unlock_cat", "")

                text = f"{chance}%: +{g} Gold + {s} Souls"
                if unlock:
                    text += f" + 解鎖 {unlock.capitalize()}"

                # 狀態標注
                status_text = "已取得" if idx in claimed_list else "尚未取得"
                status_color = (100, 200, 100) if idx in claimed_list else (255, 100, 100)
                bg_color = (0, 60, 0) if idx in claimed_list else (80, 0, 0)

                # 背景標注
                status_surf = font_small.render(status_text, True, status_color)
                bg_rect = pygame.Rect(preview_x + preview_w - 120, y_off - 5, 110, 28)
                pygame.draw.rect(screen, bg_color, bg_rect, border_radius=8)
                screen.blit(status_surf, (bg_rect.x + 10, bg_rect.y + 5))

                # 獎勵文字
                reward_surf = font_small.render(text, True, (255, 255, 200))
                screen.blit(reward_surf, (preview_x + 40, y_off))
                y_off += 32

        # 時間獎勵
        speed_bonus = reward_data.get("speed_bonus", [])
        if speed_bonus:
            header = font_normal.render("時間獎勵：", True, (100, 200, 255))
            screen.blit(header, (preview_x + 20, y_off))
            y_off += 35
            claimed_speed = claimed_first_clear.get(str(hovered_idx), [[], []])[1]
            for idx, item in enumerate(speed_bonus):
                time_limit = item.get("threshold", 0)
                reward = item.get("reward", {})
                g = reward.get("gold", 0)
                s = reward.get("souls", 0)
                unlock = reward.get("unlock_cat", "")

                text = f"≤ {time_limit}s: +{g} Gold + {s} Souls"
                if unlock:
                    text += f" + 解鎖 {unlock.capitalize()}"

                status_text = "已取得" if idx in claimed_speed else "尚未取得"
                status_color = (100, 200, 100) if idx in claimed_speed else (255, 100, 100)
                bg_color = (0, 60, 0) if idx in claimed_speed else (80, 0, 0)

                status_surf = font_small.render(status_text, True, status_color)
                bg_rect = pygame.Rect(preview_x + preview_w - 120, y_off - 5, 110, 28)
                pygame.draw.rect(screen, bg_color, bg_rect, border_radius=8)
                screen.blit(status_surf, (bg_rect.x + 10, bg_rect.y + 5))

                reward_surf = font_small.render(text, True, (200, 255, 255))
                screen.blit(reward_surf, (preview_x + 40, y_off))
                y_off += 32

    pygame.display.flip()

    # 事件處理
    selected_idx = None
    new_state = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return None, "quit", None
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左鍵選擇
                for idx, rect in level_rects.items():
                    if rect.collidepoint(event.pos):
                        selected_idx = idx
                        return selected_idx, None, hovered_idx
            elif event.button == 3:  # 右鍵返回主選單
                new_state = "main_menu"
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if 0 <= selected_level < len(levels):
                    selected_idx = selected_level
            elif event.key == pygame.K_ESCAPE:
                new_state = "main_menu"
            else:
                # 方向鍵移動（你的原邏輯可保留或改進）
                new_selected = handle_level_selection_movement(selected_level, event.key)
                if new_selected != selected_level:
                    selected_level = new_selected

    return selected_idx, new_state, hovered_idx

def handle_level_selection_movement(selected_level, key):
    """鍵盤方向移動選擇（可選優化）"""
    if not level_icon_positions:
        return selected_level

    positions = list(level_icon_positions.items())
    if selected_level not in level_icon_positions:
        return selected_level

    current_pos = level_icon_positions[selected_level]
    x, y = current_pos

    closest_idx = selected_level
    min_dist = float('inf')

    for i, pos in positions:
        if i == selected_level:
            continue
        dx = pos[0] - x
        dy = pos[1] - y
        dist = dx**2 + dy**2

        if key == pygame.K_RIGHT and dx > 50 and abs(dy) < 100 and dist < min_dist:
            min_dist = dist
            closest_idx = i
        elif key == pygame.K_LEFT and dx < -50 and abs(dy) < 100 and dist < min_dist:
            min_dist = dist
            closest_idx = i
        elif key == pygame.K_DOWN and dy > 50 and abs(dx) < 100 and dist < min_dist:
            min_dist = dist
            closest_idx = i
        elif key == pygame.K_UP and dy < -50 and abs(dx) < 100 and dist < min_dist:
            min_dist = dist
            closest_idx = i

    return closest_idx