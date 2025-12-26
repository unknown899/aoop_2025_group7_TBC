cat_config = {
    "id":101,
    "hp": 600,
    "atk": 400,
    "speed": 4,
    "color": (0, 255, 255),
    "attack_range": 710,
    "is_aoe": True,
    "kb_limit": 1,
    "cooldown": 50,
    "cost": 80,
    "width":400,
    "height": 400,
    "windup_duration": 200,
    "attack_duration": 100,
    "recovery_duration": 200,
    "attack_interval": 3000,
    "idle_frames": ["cat_folder/kp/walking/Screenshot from 2025-12-26 17-03-40.png"],#900
    "move_frames": [f"cat_folder/kp/walking/Screenshot from 2025-12-26 17-03-40.png"],
    
    "windup_frames": [f"cat_folder/kp/attacking/frame_0000{i}.png" for i in range(85, 95)] \
        ,
    "attack_frames": [f"cat_folder/kp/attacking/frame_0000{i}.png" for i in range(95, 100)]\
        +[f"cat_folder/kp/attacking/frame_000{i}.png" for i in range(100, 103)],
    "recovery_frames": [f"cat_folder/kp/attacking/frame_000{i}.png" for i in range(103, 121)],
    
    "kb_frames": [],
    "delta_y": -42, # 微調 y 座標
    "ibtn_idle": "cat_folder/eraser/ibtn_idle.png",
    "ibtn_hover": "ccat_folder/eraser/ibtn_hover.png",
    "ibtn_pressed": "cat_folder/eraser/ibtn_pressed.png",
    "attack_type": "physic",  # 攻擊類型
    "attack_type": "physic",  # 攻擊類型
    "cat_image": "cat_folder/eraser/cat_image.png",  # 放在levelselection的貓咪圖片
}