import pygame
import json
import time

class RechargeModal:
    def __init__(self, panel_rect, resource_file, font1, font2, font3):
        self.rect = panel_rect
        self.resource_file = resource_file
        self.font1 = font1#bigger
        self.font2 = font2
        self.font3 = font3#middle

        # ----------------- 儲值方案 -----------------
        self.packs = [
            {"gold": 300, "price": "NT$30"},
            {"gold": 1800, "price": "NT$150"},
            {"gold": 4000, "price": "NT$300"},
        ]
        for pack in self.packs:
            pack["rect"] = pygame.Rect(0,0,0,0)  # 先初始化，不然 draw 前 collidepoint 會爆

        self.selected_pack = None  # 選中的方案

        # ----------------- 信用卡輸入 -----------------
        self.card_digits = ""
        self.cursor_visible = True
        self.last_cursor_toggle = time.time()

        # ----------------- 按鈕 -----------------
        self.confirm_rect = pygame.Rect(0,0,0,0)  # 確認按鈕（draw 會更新位置）
        self.cancel_rect = pygame.Rect(0,0,0,0)   # 取消按鈕（draw 會更新位置）

        # ----------------- 儲值成功動畫 -----------------
        self.success = False
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
        # 畫半透明 panel
        panel = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))
        screen.blit(panel, self.rect.topleft)
        '''
        # 標題
        title = self.font1.render("Recharge", True, (255, 255, 255))
        screen.blit(title, (self.rect.x + 20, self.rect.y + 20))
        '''
        #儲值提示
        hint = self.font1.render("Select a pack and enter card number:", True, (255, 255, 255))
        screen.blit(hint, (self.rect.x + 20, self.rect.y + 60))

        #pack_title
        pack_title = self.font3.render("Recharge Packs:", True, (255, 255, 255))
        screen.blit(pack_title, (self.rect.x + 20, self.rect.y + 120))

        #card_title
        card_title = self.font3.render("Card Number:", True, (255, 255, 255))
        screen.blit(card_title, (self.rect.x + 450, self.rect.y + 120))

        # 繪製儲值方案
        for i, pack in enumerate(self.packs):
            # 計算按鈕位置
            btn_x = self.rect.x + 50
            btn_y = self.rect.y + 180 + i * 60
            btn_w = 300
            btn_h = 45
            pack["rect"] = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

            # 按鈕顏色
            btn_color = (80, 80, 160)
            border_color = (255, 255, 255)
            if self.selected_pack == pack:
                border_color = (255, 215, 0)  # 高亮

            pygame.draw.rect(screen, btn_color, pack["rect"], border_radius=8)
            pygame.draw.rect(screen, border_color, pack["rect"], 3, border_radius=8)

            # 文字
            txt = self.font2.render(f"{pack['gold']} Gold ({pack['price']})", True, (255, 255, 255))
            screen.blit(txt, txt.get_rect(center=pack["rect"].center))
        # 信用卡輸入框
        input_rect = pygame.Rect(self.rect.x + 450, self.rect.y + 200, 260, 50)
        pygame.draw.rect(screen, (255, 255, 255), input_rect, 2, border_radius=6)
        card_text = self.format_card_number()
        render = self.font2.render(card_text, True, (255, 255, 255))
        screen.blit(render, (input_rect.x + 10, input_rect.y + 10))

        # 游標閃爍
        if self.cursor_visible and len(self.card_digits) < 16:
            cursor_x = input_rect.x + 10 + render.get_width() + 2
            pygame.draw.line(screen, (255, 255, 255), (cursor_x, input_rect.y + 10), (cursor_x, input_rect.y + 40), 2)

        # 確認按鈕（灰/亮）
        self.confirm_rect = pygame.Rect(self.rect.x + 450, self.rect.y + 280, 120, 40)
        if self.selected_pack and len(self.card_digits) == 16:
            confirm_color = (50, 200, 50)  # 可點亮
        else:
            confirm_color = (100, 100, 100)  # 灰色

        pygame.draw.rect(screen, confirm_color, self.confirm_rect, border_radius=6)
        confirm_txt = self.font2.render("Confirm", True, (255, 255, 255))
        screen.blit(confirm_txt, confirm_txt.get_rect(center=self.confirm_rect.center))

        # 取消按鈕
        self.cancel_rect = pygame.Rect(self.rect.right - 120, self.rect.y + 20, 110, 35)
        pygame.draw.rect(screen, (150, 60, 60), self.cancel_rect, border_radius=6)
        cancel_text = self.font2.render("Cancel", True, (255, 255, 255))
        screen.blit(cancel_text, cancel_text.get_rect(center=self.cancel_rect.center))

        # 成功儲值畫面
        if self.fade_alpha > 0:
            fade = pygame.Surface(screen.get_size())
            fade.fill((255, 255, 255))
            fade.set_alpha(self.fade_alpha)
            screen.blit(fade, (0, 0))
            msg = self.font1.render(f"Recharge Success! +{self.selected_pack['gold']} Gold", True, (0, 0, 0))
            screen.blit(msg, msg.get_rect(center=screen.get_rect().center))
            enter_msg = self.font1.render("Press Enter to close", True, (0, 0, 0))
            screen.blit(enter_msg, enter_msg.get_rect(center=(screen.get_rect().centerx, screen.get_rect().centery+50)))


    # ---------- 事件 ----------
    def handle_event(self, event):

        # 視窗關閉
        if event.type == pygame.QUIT:
            return "quit"

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 點擊取消/離開
            if self.cancel_rect.collidepoint(event.pos):
                return "close"

            # 點擊儲值方案（一次只選一個）
            for pack in self.packs:
                if pack["rect"].collidepoint(event.pos):
                    # 選中 → 如果已選同一個則取消
                    if self.selected_pack == pack:
                        self.selected_pack = None
                    else:
                        self.selected_pack = pack

            # 點擊確認按鈕
            if self.confirm_rect.collidepoint(event.pos):
                if self.selected_pack and len(self.card_digits) == 16:
                    self.perform_recharge()

        elif event.type == pygame.KEYDOWN:
            # 儲值成功後 Enter 離開
            if self.success:
                if event.key == pygame.K_RETURN:
                    return "close"

            # 輸入中
            else:
                if event.key == pygame.K_ESCAPE:
                    return "close"
                elif event.key == pygame.K_BACKSPACE:
                    self.card_digits = self.card_digits[:-1]
                elif event.unicode.isdigit() and len(self.card_digits) < 16:
                    self.card_digits += event.unicode

        return None


    def reset(self):
        self.card_digits = ""
        self.selected_pack = None
        self.success = False
        self.fade_alpha = 0
        self.fading = False
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
