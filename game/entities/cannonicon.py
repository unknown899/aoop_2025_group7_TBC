import pygame

class CannonIcon:
    def __init__(self, ui_pos, icon_config, ui_frame_duration=500):
        """
        icon_config 需包含:
        - 'ready': [Surface] (準備好時的動畫幀)
        - 'full': Surface (全彩原圖，用於注水效果)
        - 'gray': Surface (灰階圖，作為冷卻底圖)
        - 'bounds': (top, bottom) (手動定義的非透明區域 Y 軸邊界)
        """
        self.pos = ui_pos
        self.ready_frames = icon_config['ready']
        self.full_img = icon_config['full']
        self.gray_img = icon_config['gray']
        self.top_bound, self.bottom_bound = icon_config['bounds']
        self.ui_frame_duration = ui_frame_duration # 預設 500ms 換一張圖
        
        # 用於點擊偵測的矩形與 Mask
        self.rect = self.full_img.get_rect(topleft=ui_pos)
        self.mask = pygame.mask.from_surface(self.full_img)
        self.total_fill_height = self.bottom_bound - self.top_bound

    def is_clicked(self, mouse_pos):
        """精確偵測是否點擊到圖片的非透明像素"""
        if self.rect.collidepoint(mouse_pos):
            rel_x = mouse_pos[0] - self.rect.x
            rel_y = mouse_pos[1] - self.rect.y
            return self.mask.get_at((rel_x, rel_y))
        return False

    def draw(self, screen, skill_state, progress, current_time):
        """
        skill_state: 來自 CannonSkill 的 state
        progress: 0.0 ~ 1.0 的冷卻百分比
        anim_index: 來自 CannonSkill 的動畫計數
        """
        if skill_state == "ready":
            # 使用傳入的 current_time 計算 UI 影格
            idx = (current_time // self.ui_frame_duration) % len(self.ready_frames)
            img = self.ready_frames[idx]
            screen.blit(img, self.rect)
        else:
            # 狀態為 Sweeping, After 或 Cooldown 時：顯示灰階底圖 + 彩色注水(但其實只有cooldown和ready才有）
            # 1. 先畫灰色底圖
            screen.blit(self.gray_img, self.rect)
            
            # 2. 根據進度裁切全彩圖
            # 當進度 1.0 (100%) 時，split_y = top_bound
            fill_height = progress * self.total_fill_height
            split_y = self.bottom_bound - fill_height
            
            w, h = self.full_img.get_size()
            # 裁切區域 (從 split_y 到底部)
            crop_area = (0, split_y, w, h - split_y)
            
            # 繪製全彩部分，目的地座標 Y 需根據 split_y 偏移
            screen.blit(self.full_img, (self.pos[0], self.pos[1] + split_y), crop_area)