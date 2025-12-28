# game/ui/battle_menu.py

import pygame
from game.entities import levels
from game.rewards import LEVEL_REWARDS

def draw_battle_map_selection(
    screen,
    level_map_bg,
    snail_image,
    LEVEL_NODES,
    completed_levels,
    player_pos,
    player_speed=6,
    select_font=None,
    claimed_first_clear=None
):
    """
    Draws the battle map selection UI.
    Returns: (selected_level_idx, new_game_state)
    - selected_level_idx: Level confirmed by player (Nearby + ENTER)
    - new_game_state: "main_menu" or None
    """
    if claimed_first_clear is None:
        claimed_first_clear = {"0": [[], []], "1": [[], []], "2": [[], []], "3": [[], []], "4": [[], []]}

    if select_font is None:
        select_font = pygame.font.SysFont(None, 60)

    SCREEN_WIDTH = screen.get_width()
    SCREEN_HEIGHT = screen.get_height()

    # Background
    screen.blit(level_map_bg, (0, 0))

    # Player movement
    keys = pygame.key.get_pressed()
    dx = dy = 0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        dx -= player_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        dx += player_speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        dy -= player_speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        dy += player_speed

    player_pos[0] += dx
    player_pos[1] += dy

    # Border limits (Snail radius ~35)
    player_pos[0] = max(35, min(SCREEN_WIDTH - 35, player_pos[0]))
    player_pos[1] = max(35, min(SCREEN_HEIGHT - 35, player_pos[1]))

    # Draw player (Snail)
    screen.blit(snail_image, (player_pos[0] - 35, player_pos[1] - 35))

    # Font settings
    font_title   = pygame.font.SysFont(None, 30)  # Level Title
    font_header  = pygame.font.SysFont(None, 26)  # Section Headers
    font_content = pygame.font.SysFont(None, 22)  # Reward Content
    font_status  = pygame.font.SysFont(None, 20)  # Status Label
    font_hint    = pygame.font.SysFont(None, 24)  # Control Hints

    # Detect hover and nearest node
    hovered_idx = None
    nearest_idx = None
    nearest_dist = float('inf')
    mouse_pos = pygame.mouse.get_pos()

    for idx, (nx, ny) in enumerate(LEVEL_NODES):
        dist_to_player = ((player_pos[0] - nx)**2 + (player_pos[1] - ny)**2)**0.5
        dist_to_mouse = ((mouse_pos[0] - nx)**2 + (mouse_pos[1] - ny)**2)**0.5

        # Unlock status
        unlocked = idx == 0 or (idx - 1) in completed_levels
        color = (100, 255, 100) if idx in completed_levels else ((0, 255, 0) if unlocked else (100, 100, 100))

        # Main node circle
        pygame.draw.circle(screen, color, (nx, ny), 50)
        pygame.draw.circle(screen, (255, 255, 255), (nx, ny), 50, 6)

        # Level number
        num_text = select_font.render(str(idx + 1), True, (0, 0, 0))
        screen.blit(num_text, num_text.get_rect(center=(nx, ny)))

        # Highlight logic
        highlight = False
        if dist_to_player < 100:
            highlight = True
            if dist_to_player < nearest_dist:
                nearest_dist = dist_to_player
                nearest_idx = idx
        if dist_to_mouse < 60:
            highlight = True
            hovered_idx = idx

        if highlight:
            pygame.draw.circle(screen, (255, 255, 0), (nx, ny), 65, 8)

    # Control hints
    hint_str = "WASD/Arrows: Move | ENTER: Select Level | ESC: Main Menu"
    hint_text = font_hint.render(hint_str, True, (255, 255, 200))
    screen.blit(hint_text, (20, 20))

    # === Reward Preview Panel ===
    preview_idx = hovered_idx if hovered_idx is not None else nearest_idx

    if preview_idx is not None:
        level = levels[preview_idx]
        reward_data = LEVEL_REWARDS.get(preview_idx, {})

        # Panel settings
        preview_x, preview_y = SCREEN_WIDTH - 460, SCREEN_HEIGHT - 580
        preview_w, preview_h = 440, 560

        # Semi-transparent background
        s = pygame.Surface((preview_w, preview_h))
        s.set_alpha(230)
        s.fill((10, 10, 40))
        screen.blit(s, (preview_x, preview_y))
        pygame.draw.rect(screen, (0, 200, 255), (preview_x, preview_y, preview_w, preview_h), 5)

        # Title
        title = font_title.render(f"Level {preview_idx + 1}: {level.name}", True, (255, 255, 100))
        screen.blit(title, (preview_x + 20, preview_y + 20))

        y_off = preview_y + 65

        # Repeatable Rewards
        repeatable = reward_data.get("repeatable", [])
        if repeatable:
            header = font_header.render("Completion Rewards:", True, (100, 255, 100))
            screen.blit(header, (preview_x + 20, y_off))
            y_off += 30
            # print(repeatable)
            for item in repeatable:
                chance = item.get("weight", 0)
                item = item.get("reward", {})
                g, s_points = item.get("gold", 0), item.get("souls", 0)
                text = f"{chance} % chance: +{g} Gold, +{s_points} Souls"
                surf = font_content.render(text, True, (200, 255, 200))
                screen.blit(surf, (preview_x + 40, y_off))
                y_off += 25

        # First Clear Rewards
        first_clear = reward_data.get("first_clear", [])
        if first_clear:
            y_off += 10
            header = font_header.render("First Clear Rewards:", True, (255, 200, 100))
            screen.blit(header, (preview_x + 20, y_off))
            y_off += 30
            claimed_list = claimed_first_clear.get(str(preview_idx), [[], []])[0]
            for idx, item in enumerate(first_clear):
                chance = item.get("weight", 0)
                reward = item.get("reward", {})
                g, s_points, unlock = reward.get("gold", 0), reward.get("souls", 0), reward.get("unlock_cat", "")

                text = f"{chance}% Chance: +{g}G, +{s_points}S"
                if unlock:
                    text += f", Unlock {unlock.capitalize()} Cat"

                # Status Label
                obtained = idx in claimed_list
                status_text = "CLAIMED" if obtained else "AVAILABLE"
                status_color = (150, 255, 150) if obtained else (255, 150, 150)
                bg_color = (0, 60, 0) if obtained else (80, 0, 0)

                status_surf = font_status.render(status_text, True, status_color)
                bg_rect = pygame.Rect(preview_x + preview_w - 110, y_off - 3, 100, 24)
                pygame.draw.rect(screen, bg_color, bg_rect, border_radius=8)
                screen.blit(status_surf, (bg_rect.x + 10, bg_rect.y + 4))

                reward_surf = font_content.render(text, True, (255, 255, 200))
                screen.blit(reward_surf, (preview_x + 40, y_off))
                y_off += 30

        # Speed Bonus
        speed_bonus = reward_data.get("speed_bonus", [])
        if speed_bonus:
            y_off += 10
            header = font_header.render("Speed Bonus:", True, (100, 200, 255))
            screen.blit(header, (preview_x + 20, y_off))
            y_off += 30
            claimed_speed = claimed_first_clear.get(str(preview_idx), [[], []])[1]
            for idx, item in enumerate(speed_bonus):

                time_limit = item.get("threshold", 0)
                # reward = item.get("reward", {})
                g, s_points, unlock = item.get("gold", 0), item.get("souls", 0), item.get("unlock_cat", "")

                text = f"Clear in \u2264 {time_limit}s: +{g}G, +{s_points}S"
                if unlock:
                    text += f", Unlock {unlock.capitalize()} Cat"

                obtained = idx in claimed_speed
                status_text = "CLAIMED" if obtained else "AVAILABLE"
                status_color = (150, 255, 150) if obtained else (255, 150, 150)
                bg_color = (0, 60, 0) if obtained else (80, 0, 0)

                status_surf = font_status.render(status_text, True, status_color)
                bg_rect = pygame.Rect(preview_x + preview_w - 110, y_off - 3, 100, 24)
                pygame.draw.rect(screen, bg_color, bg_rect, border_radius=8)
                screen.blit(status_surf, (bg_rect.x + 10, bg_rect.y + 4))

                reward_surf = font_content.render(text, True, (200, 255, 255))
                screen.blit(reward_surf, (preview_x + 40, y_off))
                y_off += 30

    pygame.display.flip()

    # Event handling
    selected_level_idx = None
    new_game_state = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # 這是點擊視窗右上角的 X 按鈕
            end_game_state = "quit"
            return selected_level_idx, end_game_state
        elif event.type == pygame.KEYDOWN:
            # 新增：按 X 或 ESC 鍵回到主選單
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_x:
                new_game_state = "main_menu"
            
            # 按 ENTER 或 SPACE 選擇關卡
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                if nearest_idx is not None:
                    # 檢查是否已解鎖 (Level 1 預設解鎖，或前一關已完成)
                    if nearest_idx == 0 or (nearest_idx - 1) in completed_levels:
                        selected_level_idx = nearest_idx
    return selected_level_idx, new_game_state