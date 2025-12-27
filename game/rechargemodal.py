import pygame
import json
import time

class RechargeModal:
    def __init__(self, panel_rect, resource_file, font):
        self.rect = panel_rect
        self.resource_file = resource_file
        self.font = font

        # 儲值方案
        self.packs = [
            {"gold": 300, "price": "NT$30"},
            {"gold": 1800, "price": "NT$150"},
            {"gold": 4000, "price": "NT$300"},
        ]

        # 信用卡輸入
        self.card_digits = ""
        self.cursor_visible = True
        self.last_cursor_toggle = time.time()

        # 狀態
        self.selected_pack = None
        self.success = False

        # 成功動畫
        self.fade_alpha = 0
        self.fading = False

    # ---------- 更新 ----------
    def update(self):
        # 游標閃爍
        if time.time() - self.last_cursor_toggle > 0.5:
            self.cursor_visible = not self.cursor_visible
            self.last_cursor_toggle = time.time()

        # 成功動畫 fade out
        if self.fading:
            self.fade_alpha -= 8
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.fading = False

    # ---------- 繪製 ----------
    def draw(self, screen):
        # 半透明 panel
        panel = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))
        screen.blit(panel, self.rect.topleft)

        # 標題
        title = self.font.render("Recharge", True, (255, 255, 255))
        screen.blit(title, (self.rect.x + 20, self.rect.y + 20))

        # 儲值方案
        for i, pack in enumerate(self.packs):
            btn = pygame.Rect(
                self.rect.x + 50,
                self.rect.y + 80 + i * 60,
                200,
                45
            )
            pygame.draw.rect(screen, (80, 80, 160), btn, border_radius=8)
            txt = self.font.render(
                f"{pack['gold']} Gold ({pack['price']})",
                True,
                (255, 255, 255)
            )
            screen.blit(txt, txt.get_rect(center=btn.center))
            pack["rect"] = btn

        # 信用卡輸入框
        input_rect = pygame.Rect(self.rect.x + 300, self.rect.y + 100, 260, 50)
        pygame.draw.rect(screen, (255, 255, 255), input_rect, 2, border_radius=6)

        card_text = self.format_card_number()
        render = self.font.render(card_text, True, (255, 255, 255))
        screen.blit(render, (input_rect.x + 10, input_rect.y + 10))

        # 游標
        if self.cursor_visible and len(self.card_digits) < 16:
            cursor_x = input_rect.x + 10 + render.get_width() + 2
            pygame.draw.line(
                screen,
                (255, 255, 255),
                (cursor_x, input_rect.y + 10),
                (cursor_x, input_rect.y + 40),
                2
            )

        # 成功動畫（白 → 淡出）
        if self.fade_alpha > 0:
            fade = pygame.Surface(screen.get_size())
            fade.fill((255, 255, 255))
            fade.set_alpha(self.fade_alpha)
            screen.blit(fade, (0, 0))

            msg = self.font.render("Recharge Success!", True, (0, 0, 0))
            screen.blit(
                msg,
                msg.get_rect(center=screen.get_rect().center)
            )

    # ---------- 事件 ----------
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for pack in self.packs:
                if pack["rect"].collidepoint(event.pos):
                    self.selected_pack = pack

        elif event.type == pygame.KEYDOWN:
            if self.success:
                if event.key == pygame.K_RETURN:
                    return "close"

            elif event.key == pygame.K_BACKSPACE:
                self.card_digits = self.card_digits[:-1]

            elif event.key == pygame.K_RETURN:
                if self.selected_pack and len(self.card_digits) == 16:
                    self.perform_recharge()

            elif event.unicode.isdigit() and len(self.card_digits) < 16:
                self.card_digits += event.unicode

        return None

    # ---------- 工具 ----------
    def format_card_number(self):
        s = self.card_digits
        groups = [s[i:i+4] for i in range(0, len(s), 4)]
        return " ".join(groups)

    def perform_recharge(self):
        with open(self.resource_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["gold"] += self.selected_pack["gold"]

        with open(self.resource_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        self.fade_alpha = 255
        self.fading = True
        self.success = True
