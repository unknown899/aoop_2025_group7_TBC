import pygame
import math
import sys, os
import random

def load_csmoke_images():
    frames1 = []
    frames2 = []
    scale1 = random.uniform(0.4, 0.6)
    scale2 = random.uniform(0.4, 0.6)
    alpha = 255  # 隨機透明度
    for i in range(1, 11, 2):  # 假設有 shockwave0.png ~ shockwave4.png
            img1 = pygame.image.load(f"images/effects/smoke/collapsed_{i}.png").convert_alpha()
            img2 = pygame.image.load(f"images/effects/smoke/collapsed_v2_{i}.png").convert_alpha()
            new_size1 = (int(img1.get_width() * scale1), int(img1.get_height() * scale1))
            new_size2 = (int(img2.get_width() * scale2), int(img2.get_height() * scale2))
            img1 = pygame.transform.scale(img1, new_size1)
            img2 = pygame.transform.scale(img2, new_size2)

            image_copy1 = img1.copy()
            image_copy1.set_alpha(alpha)
            frames1.append(image_copy1)
            image_copy2 = img2.copy()
            image_copy2.set_alpha(alpha)
            frames2.append(image_copy2)
    return frames1, frames2

def load_electric_images():
    frames = []
    alpha = 255
    scale = random.uniform(0.1, 0.2)  # 隨機煙霧大小
    for i in range(1, 11, 2):  # 假設有 shockwave0.png ~ shockwave4.png
            img = pygame.image.load(f"images/effects/electric/electric_{i}.png").convert_alpha()
            if scale != 1.0:
                new_size = (int(img.get_width() * scale), int(img.get_height() * scale))
                img = pygame.transform.scale(img, new_size)
            image_copy = img.copy()
            image_copy.set_alpha(alpha)
            frames.append(image_copy)
    return frames

def load_gas_images():
    frames = []
    alpha = 255
    scale = random.uniform(0.2, 0.3)  # 隨機煙霧大小
    color = (150, 150, 150)  # 灰色煙霧

    for i in range(1, 11, 2):  # 假設有 shockwave0.png ~ shockwave4.png
        img = pygame.image.load(f"images/effects/gas/Explosion_{i}.png").convert_alpha()
        if scale != 1.0:
            new_size = (int(img.get_width() * scale), int(img.get_height() * scale))
            img = pygame.transform.scale(img, new_size)
        image_copy = img.copy()
        image_copy.set_alpha(alpha)
        frames.append(image_copy)

    return frames

def load_physic_images():
    frames = []
    alpha = 255
    scale = random.uniform(0.1, 0.2)  # 隨機煙霧大小
    color = (150, 150, 150)  # 灰色煙霧
    for i in range(1, 11, 2):  # 假設有 shockwave0.png ~ shockwave4.png
            img = pygame.image.load(f"images/effects/physic/physic_{i}.png").convert_alpha()
            if scale != 1.0:
                new_size = (int(img.get_width() * scale), int(img.get_height() * scale))
                img = pygame.transform.scale(img, new_size)
            image_copy = img.copy()
            image_copy.set_alpha(alpha)
            frames.append(image_copy)

    return frames

def load_smoke_images():
    alpha = 100
    scale = random.uniform(0.1, 0.2)  # 隨機煙霧大小
    color = (150, 150, 150)  # 灰色煙霧

    frames = []
    for i in range(1, 25, 5):  # 假設有 shockwave0.png ~ shockwave4.png
        img = pygame.image.load(f"images/effects/smoke/smoke_frames/processed_frame_{i}.png").convert_alpha()
        if scale != 1.0:
            new_size = (int(img.get_width() * scale), int(img.get_height() * scale))
            img = pygame.transform.scale(img, new_size)
        image_copy = img.copy()
        image_copy.set_alpha(alpha)
        frames.append(image_copy)

    return frames

import pygame
import os

def load_cannonskill_images(
    origin_scale=0.1,
    beam_scale=1.2,
    sweep_fx_scale=0.3,
    after_fx_scale1=0.3,
    after_fx_scale2=0.3,
    alpha=255
):
    def load_sequence(folder, prefix, frame_range, step=1, scale=1.0):
        frames = []
        for i in range(frame_range[0], frame_range[1], step):
            path = os.path.join(folder, f"{prefix}{i}.png")
            if not os.path.exists(path):
                continue

            img = pygame.image.load(path).convert_alpha()

            if scale != 1.0:
                new_size = (
                    int(img.get_width() * scale),
                    int(img.get_height() * scale)
                )
                img = pygame.transform.scale(img, new_size)

            img_copy = img.copy()
            img_copy.set_alpha(alpha)
            frames.append(img_copy)

        return frames

    # ===============================
    # 1️⃣ 砲口 Origin 動畫
    # ===============================
    origin_frames = load_sequence(
        folder="images/cannon/origin",
        prefix="origin",
        frame_range=(1, 2),
        step=1,
        scale=origin_scale
    )

    # ===============================
    # 2️⃣ 雷射光束（水平）
    # ===============================
    beam_frames = load_sequence(
        folder="images/cannon/beam",
        prefix="beam",
        frame_range=(1, 2),
        step=1,
        scale=beam_scale
    )

    # ===============================
    # 3️⃣ 掃射中地面 Splash
    # ===============================
    sweep_fx_frames = load_sequence(
        folder="images/cannon/sweep_fx",
        prefix="splash",
        frame_range=(1, 3),
        step=1,
        scale=sweep_fx_scale
    )

    # ===============================
    # 4️⃣ 掃射後沿地面移動特效
    # ===============================
    after_fx_frames_1 = load_sequence(
        folder="images/cannon/after_fx/1",
        prefix="Explosion_",
        frame_range=(3, 6),
        step=1,
        scale=after_fx_scale1
    )

    # ✅ 第二組：請依你的實際路徑/檔名前綴修改
    # 例如：images/skills/cannon/after_fx_v2/after_0.png ...
    after_fx_frames_2 = load_sequence(
        folder="images/cannon/after_fx/2",
        prefix="Explosion_2_",
        frame_range=(1, 7),
        step=1,
        scale=after_fx_scale2
    )

    # ✅ 變成二維（兩個列表）
    after_fx_frames = [after_fx_frames_1, after_fx_frames_2]

    return {
        "origin": origin_frames,
        "beam": beam_frames,
        "sweep_fx": sweep_fx_frames,
        "after_fx": after_fx_frames
    }

def load_cannonicon_image(scale=1.0):
    ready = []
    for i in range(1, 3, 1): 
        img = pygame.image.load(f"images/cannonicon/ready/ready{i}.png").convert_alpha()
        if scale != 1.0:
            new_size = (int(img.get_width() * scale), int(img.get_height() * scale))
            img = pygame.transform.scale(img, new_size)
        image_copy = img.copy()
        ready.append(image_copy)

    full = pygame.image.load(f"images/cannonicon/full.png").convert_alpha()
    if scale != 1.0:
        new_size = (int(full.get_width() * scale), int(full.get_height() * scale))
        full = pygame.transform.scale(full, new_size)
    
    gray = pygame.image.load(f"images/cannonicon/gray.png").convert_alpha()
    if scale != 1.0:
        new_size = (int(gray.get_width() * scale), int(gray.get_height() * scale))
        gray = pygame.transform.scale(gray, new_size)
    
    return ready, full, gray

def load_single_image(path, size=None, convert_alpha=True):
    """
    載入單張圖片並進行縮放。
    
    參數:
        path (str): 圖片路徑
        size (tuple): 目標大小 (width, height)，若為 None 則保持原圖大小
        convert_alpha (bool): 是否保留透明通道 (推薦 UI/去背圖使用 True)
    
    返回:
        pygame.Surface: 處理後的圖片物件
    """
    if not os.path.exists(path):
        print(f"Warning: File {path} not found!")
        # 如果找不到檔案，回傳一個紅色方塊避免程式崩潰
        fallback = pygame.Surface(size if size else (100, 100))
        fallback.fill((255, 0, 0))
        return fallback

    # 1. 載入圖片
    image = pygame.image.load(path)
    
    # 2. 根據需求決定是否轉換格式以優化效能
    if convert_alpha:
        image = image.convert_alpha()
    else:
        image = image.convert()

    # 3. 縮放處理
    if size:
        # 使用 smoothscale 讓背景縮放後更細緻
        image = pygame.transform.smoothscale(image, size)
        
    return image