cat_config = {
    "id":101,
    "hp": 100000,
    "atk": 200,
    "speed": 4,
    "color": (0, 255, 255),
    "attack_range": 210,
    "is_aoe": True,
    "kb_limit": 1,
    "cooldown": 500000,
    "cost": 270,
    "width":200,
    "height": 200,
    "windup_duration": 400,
    "attack_duration": 50,
    "recovery_duration": 400,
    "attack_interval": 10000,
    "idle_frames": ["cat_folder/kp/walking/urudcd8G.png"],#900
    "move_frames": [f"cat_folder/kp/walking/urudcd8G.png"],
    
    "windup_frames": [f"cat_folder/kp/attacking/frame_0000{i}.png" for i in range(85, 95)] \
        ,
    "attack_frames": [f"cat_folder/kp/attacking/frame_0000{i}.png" for i in range(95, 100)]\
        +[f"cat_folder/kp/attacking/frame_000{i}.png" for i in range(100, 103)],
    "recovery_frames": [f"cat_folder/kp/attacking/frame_000{i}.png" for i in range(103, 170)],
    
    "kb_frames": [],
    "delta_y": -42, # 微調 y 座標
    "ibtn_idle": "cat_folder/kp/ibtn_idle.png",
    "ibtn_hover": "cat_folder/kp/ibtn_hover.png",
    "ibtn_pressed": "cat_folder/kp/ibtn_pressed.png",
    "attack_type": "physic",  # 攻擊類型
    "attack_type": "physic",  # 攻擊類型
    "cat_image": "cat_folder/kp/cat_image.png",  # 放在levelselection的貓咪圖片
}