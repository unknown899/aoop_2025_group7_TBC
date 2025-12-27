import pygame
import json
import time

class RechargeModal:
    def __init__(self, panel_rect, resource_file, font1, font2, font3, success_rect, visa_img):
        
        self.rect = panel_rect
        self.success_rect = success_rect
        self.resource_file = resource_file
        self.font1 = font1#bigger
        self.font2 = font2
        self.font3 = font3#middle
        self.visa_img = visa_img

        # ----------------- 儲值方案 -----------------
        self.packs = [
            {"gold": 300, "souls": 100, "price": "NT$30"},
            {"gold": 1800, "souls": 700, "price": "NT$150"},
            {"gold": 4000, "souls": 1600, "price": "NT$300"},
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
        self.success = False #在儲值成功通知界面
        self.fade_alpha = 0
        #self.fading = False


    # ---------- 更新 ----------
    def update(self):
        # 游標閃爍
        if time.time() - self.last_cursor_toggle > 0.5:
            self.cursor_visible = not self.cursor_visible
            self.last_cursor_toggle = time.time()
        '''
        # 成功動畫 fade out
        if self.fading:
            self.fade_alpha -= 2
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.fading = False
        '''
    # ---------- 繪製 ----------
    def draw(self, screen):

        SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
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
        screen.blit(pack_title, (self.rect.x + 20, self.rect.y + 140))

        #card_title
        card_title = self.font3.render("Card Number:", True, (255, 255, 255))
        screen.blit(card_title, (self.rect.x + 500, self.rect.y + 140))

        # 繪製儲值方案
        for i, pack in enumerate(self.packs):
            # 計算按鈕位置
            btn_x = self.rect.x + 20
            btn_y = self.rect.y + 200 + i * 60
            btn_w = 430
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
            txt = self.font2.render(f"{pack['gold']} Gold {pack['souls']} Souls ({pack['price']})", True, (255, 255, 255))
            screen.blit(txt, txt.get_rect(center=pack["rect"].center))
        # 信用卡輸入框
        input_rect = pygame.Rect(self.rect.x + 600, self.rect.y + 220, 300, 50)
        pygame.draw.rect(screen, (255, 255, 255), input_rect, 2, border_radius=6)
        card_text = self.format_card_number()
        render = self.font2.render(card_text, True, (255, 255, 255))
        screen.blit(render, (input_rect.x + 10, input_rect.y + 10))
        
        # draw visa icon (與 input_rect 同高度、在左側一點)
        visa_rect = self.visa_img.get_rect()
        padding = 10
        visa_pos = (
            input_rect.left - visa_rect.width - padding,
            input_rect.centery - visa_rect.height // 2
        )
        screen.blit(self.visa_img, visa_pos)

        # 游標閃爍
        if self.cursor_visible and len(self.card_digits) < 16:
            cursor_x = input_rect.x + 10 + render.get_width() + 2
            pygame.draw.line(screen, (255, 255, 255), (cursor_x, input_rect.y + 10), (cursor_x, input_rect.y + 40), 2)

        # 確認按鈕（灰/亮）
        self.confirm_rect = pygame.Rect(self.rect.x + 500, self.rect.y + 300, 120, 40)
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

        # -------------------------
        # 讀取資源
        # -------------------------
        try:
            with open(self.resource_file, "r", encoding="utf-8") as f:
                player_data = json.load(f)
        except:
            player_data = {"gold": 0, "souls": 0}

        # 資源顯示

        gold_text = self.font1.render(f"Gold: {player_data['gold']}", True, (255, 215, 0))
        soul_text = self.font1.render(f"Souls: {player_data['souls']}", True, (200, 100, 255))
        screen.blit(gold_text, (SCREEN_WIDTH - 610, 553))
        screen.blit(soul_text, (SCREEN_WIDTH - 300, 553))

        if self.success:
            # 1. 繪製半透明黑色背景遮罩 (讓後方遊戲畫面變暗，突出視窗)
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            # 2. 繪製主視窗底色 (深灰色帶圓角)
            # 稍微擴展一下 rect 讓它看起來大方一點
            panel_rect = self.success_rect.inflate(20, 20)
            pygame.draw.rect(screen, (40, 44, 52), panel_rect, border_radius=15) # 主背景
            pygame.draw.rect(screen, (255, 215, 0), panel_rect, 3, border_radius=15) # 金色外框

            # 3. 繪製頂部標題裝飾 (可選)
            title_area = pygame.Rect(panel_rect.x, panel_rect.y, panel_rect.width, 40)
            pygame.draw.rect(screen, (60, 70, 90), title_area, border_top_left_radius=15, border_top_right_radius=15)

            # 4. 渲染文字 - 標題
            title_msg = self.font1.render("CONGRATULATIONS", True, (255, 215, 0))
            screen.blit(title_msg, title_msg.get_rect(center=(panel_rect.centerx, panel_rect.y + 20)))

            # 5. 渲染文字 - 獲得內容 (亮白色)
            msg_text = f"Recharge Success! +{self.selected_pack['gold']} Gold"
            msg = self.font1.render(msg_text, True, (255, 255, 255))
            screen.blit(msg, msg.get_rect(center=(panel_rect.centerx, panel_rect.centery + 10)))

            # 6. 渲染提示文字 (灰色，並加上一個小背景像按鈕一樣)
            enter_msg = self.font3.render("Press Enter to close", True, (180, 180, 180))
            enter_rect = enter_msg.get_rect(center=(panel_rect.centerx, panel_rect.bottom - 35))
            
            # 在提示字下面畫一個淡淡的底色
            #pygame.draw.rect(screen, (60, 60, 60), enter_rect.inflate(20, 10), border_radius=5)
            screen.blit(enter_msg, enter_rect)
            

    # ---------- 事件 ----------
    def handle_event(self, event):

        # 視窗關閉
        if event.type == pygame.QUIT:
            return "quit"

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.success:
                return None  # 成功視窗時不處理點擊事件
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
                    self.success = False

            # 輸入中
            else:
                if event.key == pygame.K_BACKSPACE:
                    self.card_digits = self.card_digits[:-1]
                elif event.unicode.isdigit() and len(self.card_digits) < 16:
                    self.card_digits += event.unicode

        return None


    def reset(self):
        self.card_digits = ""
        self.selected_pack = None
        self.success = False
        self.fade_alpha = 0
        #self.fading = False
    # ---------- 工具 ----------
    def format_card_number(self):
        s = self.card_digits
        groups = [s[i:i+4] for i in range(0, len(s), 4)]
        return " ".join(groups)

    def perform_recharge(self):
        with open(self.resource_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["gold"] += self.selected_pack["gold"]
        data["souls"] += self.selected_pack["souls"]

        with open(self.resource_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        self.fade_alpha = 255
        #self.fading = True
        self.success = True
