import pygame
import math

class CannonSkill:
    def __init__(
        self,
        origin_pos,
        sweep_start_x,
        range,
        ground_y,
        sweep_speed=0.6667,#sweep_duration=1200,
        cooldown=5000,
        damage=300,
        origin_frames=None,
        beam_frames=None,
        sweep_fx_frames=None,
        after_fx_frames=None,  # ✅ 改成 2D： [frames_group1, frames_group2]
        frame_duration1=100,
        frame_duration2=100,
        after_duration=1000
    ):
        # --- 基本設定 ---
        self.origin_x, self.origin_y = origin_pos
        self.sweep_start_x = sweep_start_x
        self.sweep_end_x = self.sweep_start_x-range#sweep_end_x
        self.ground_y = ground_y
        self.sweep_duration = range/sweep_speed
        self.cooldown = cooldown
        self.damage = damage

        # --- 圖片 ---
        self.origin_frames = origin_frames or []
        self.beam_frames = beam_frames or []
        self.sweep_fx_frames = sweep_fx_frames or []

        # ✅ 讓 after_fx_frames 永遠是「二維」
        # 允許你傳：
        # 1) None
        # 2) [group1_frames, group2_frames]
        # 3) 單一 group（舊寫法） -> 會自動包成 [group]
        if after_fx_frames is None:
            self.after_fx_frames = []
        else:
            # 如果傳進來是「一維 frames(裡面是 Surface)」，就包成二維
            if len(after_fx_frames) > 0 and isinstance(after_fx_frames[0], pygame.Surface):
                self.after_fx_frames = [after_fx_frames]
            else:
                self.after_fx_frames = after_fx_frames

        # --- 狀態 ---
        self.state = "ready"
        self.start_time = 0
        self.cooldown_start = 0
        self.after_duration = range/sweep_speed
        self.after_start_time = 0  # 紀錄進入 after 狀態的時間

        # --- 動畫 ---
        #self.anim_index = 0
        self.after_x = sweep_start_x
        self.frame_duration1 = frame_duration1 # for sweep_fx例如 100ms 代表 1秒 10 張圖
        self.frame_duration2 = frame_duration2 # for sweep_fx
        self.current_time_ms = 0
    # ======================================================
    # 觸發技能
    # ======================================================
    def activate(self, current_time):
        if self.state == "ready":
            self.state = "sweeping"
            self.start_time = current_time
            self.anim_index = 0

    # ======================================================
    # 更新
    # ======================================================
    def update(self, current_time, enemies, enemy_tower):
        #self.anim_index += 1
        self.current_time_ms = current_time

        # ---------- 掃射中 ----------
        if self.state == "sweeping":
            progress = (current_time - self.start_time) / self.sweep_duration

            if progress >= 1.0:
                # 掃射結束 → 進入後效
                self.state = "after"
                self.after_x = self.sweep_start_x
                self.after_start_time = current_time # <--- 新增這一行
                # 結算傷害（只在這裡一次）
                self._apply_damage(enemies, enemy_tower)

        # ---------- 掃射後地面殘影 ----------
        elif self.state == "after":
            # 計算進入 after 狀態後的進度 (0.0 ~ 1.0)
            after_progress = (current_time - self.after_start_time) / self.after_duration
            
            if after_progress >= 1.0:
                # 進度結束，進入冷卻
                self.state = "cooldown"
                self.cooldown_start = current_time
            else:
                # 根據進度更新位置：從 start_x 走到 end_x
                self.after_x = self.sweep_start_x + (self.sweep_end_x - self.sweep_start_x) * after_progress

        # ---------- 冷卻 ----------
        elif self.state == "cooldown":
            if current_time - self.cooldown_start >= self.cooldown:
                self.state = "ready"

    def _get_frame(self, frames, frame_duration=None):
        """根據時間計算目前該顯示哪一張圖"""
        if not frames: return None
        if frame_duration is None:
            frame_duration = self.frame_duration1
        # 總時間除以每幀時長，再對總幀數取餘數
        idx = (self.current_time_ms // frame_duration) % len(frames)
        return frames[idx]
    
    # ======================================================
    # 繪製
    # ======================================================
    def draw(self, screen, camera_offset_x):
        # ---------- 掃射中 ----------
        if self.state == "sweeping":
            self._draw_origin(screen, camera_offset_x)
            self._draw_beam(screen, camera_offset_x)
            self._draw_sweep_fx(screen, camera_offset_x)

        # ---------- 掃射後 ----------
        elif self.state == "after":
            self._draw_after_fx(screen, camera_offset_x)

    # ======================================================
    # 子功能
    # ======================================================
    def _draw_origin(self, screen, camera_offset_x):
        if not self.origin_frames:
            return
        img = self._get_frame(self.origin_frames)
        rect = img.get_rect(center=(self.origin_x-camera_offset_x, self.origin_y))
        screen.blit(img, rect)

    def _draw_beam(self, screen, camera_offset_x):
        if not self.beam_frames:
            return

        # 1. 計算當前目標點 T 的位置
        progress = (pygame.time.get_ticks() - self.start_time) / self.sweep_duration
        progress = max(0, min(1, progress))

        tx = self.sweep_start_x + (self.sweep_end_x - self.sweep_start_x) * progress
        ty = self.ground_y
        #print(f"tx: {tx}")

        # 2. 計算向量與距離 (O 到 T)
        dx = tx - self.origin_x
        dy = ty - self.origin_y
        distance = math.sqrt(dx**2 + dy**2)
        
        # 計算角度 (math.atan2 是 y, x)
        # 這裡的 angle 計算方式取決於你原始圖片的朝向。
        # 假設原始圖片是水平長條狀，我們要轉向 T
        angle = -math.degrees(math.atan2(dy, dx))

        # 3. 獲取原始影格並進行「長度縮放」
        # 寬度變為 distance，高度維持原本 beam 的高度
        beam_original = self._get_frame(self.beam_frames)
        scaled_beam = pygame.transform.scale(beam_original, (int(distance), beam_original.get_height()))

        # 4. 旋轉圖片
        # 注意：旋轉會導致 Surface 變大（為了容納旋轉後的斜邊）
        rotated_beam = pygame.transform.rotate(scaled_beam, angle)

        # 5. 定位：將旋轉後圖片的「右上角」對準「發射源」
        # 我們將 origin 減去相機偏移量得到螢幕上的固定點
        screen_origin = (self.origin_x - camera_offset_x, self.origin_y)
        
        # 建立 Rect 並指定 topright 位置
        # 這樣無論長度如何變化或如何旋轉，右上角永遠鎖死在 origin
        rect = rotated_beam.get_rect(topright=screen_origin)

        # 6. 繪製
        screen.blit(rotated_beam, rect)

    def _draw_sweep_fx(self, screen, camera_offset_x):
        if not self.sweep_fx_frames:
            return

        progress = (pygame.time.get_ticks() - self.start_time) / self.sweep_duration
        tx = self.sweep_start_x + (self.sweep_end_x - self.sweep_start_x) * progress
        ty = self.ground_y

        fx = self._get_frame(self.sweep_fx_frames)#self.sweep_fx_frames[self.anim_index % len(self.sweep_fx_frames)]
        rect = fx.get_rect(center=(tx-camera_offset_x, ty))#高度微調
        screen.blit(fx, rect)

    def _draw_after_fx(self, screen, camera_offset_x):
        if not self.after_fx_frames:
            return

        # 再次計算進度供繪製使用
        after_progress = (pygame.time.get_ticks() - self.after_start_time) / self.after_duration
        after_progress = max(0, min(1, after_progress))

        ty = self.ground_y
        offsetx = 0
        offsety = 0
        for group in self.after_fx_frames:
            if not group:
                continue

            # 使用你原本封裝的基於時間獲取影格的函數
            fx = self._get_frame(group, self.frame_duration2)

            # 進階：讓殘影隨進度變透明 (可選)
            # alpha = int(255 * (1.0 - after_progress))
            # fx.set_alpha(alpha) 

            # 這裡的 offset 邏輯：
            # 第一個 (0) 是目前掃過的進度點
            # 第二個 (sweep_end_x - after_x) 會讓另一個特效固定在終點等待，這取決於你的設計需求
            rect = fx.get_rect(bottomright=(self.after_x - camera_offset_x + offsetx, ty+25+ offsety))# 高度微調
            screen.blit(fx, rect)
            offsetx -= 140
            offsety -= 20
    # ======================================================
    # 傷害計算（只在掃射結束）
    # ======================================================
    def _apply_damage(self, enemies, enemy_tower):
        print(f"Applying damage to enemies between x={self.sweep_start_x} and x={self.sweep_end_x}")
        for e in enemies:
            print(f"Checking enemy at x={e.x} with width={e.width}")
            # 獲取敵人的左右邊界
            enemy_left = e.x
            enemy_right = e.x + e.width
            # 檢查敵人是否在掃射範圍內(may not correct for other direction)
            if self.sweep_start_x >= enemy_left and enemy_right >= self.sweep_end_x:
                e.take_damage(self.damage, "physic")
                print(f" - Enemy at x={e.x} took {self.damage} damage!")
        # 檢查敵方塔樓
        print(f"Checking enemy_tower at x={enemy_tower.x} with width={enemy_tower.width}")
        # 獲取敵方塔的左右邊界
        enemy_left = enemy_tower.x
        enemy_right = enemy_tower.x + enemy_tower.width
        # 檢查敵方塔是否在掃射範圍內(may not correct for other direction)
        if self.sweep_start_x >= enemy_left and enemy_right >= self.sweep_end_x:
            enemy_tower.take_damage(self.damage, "physic")
            print(f" - Enemy_tower at x={enemy_tower.x} took {self.damage} damage!")
                        
            
                