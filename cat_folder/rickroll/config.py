cat_config = {
    "id":103,
    "hp": 2000,
    "atk": 20,
    "speed": 5,
    "color": (0, 255, 255),
    "attack_range": 210,
    "is_aoe": True,
    "kb_limit": 1,
    "cooldown": 5000,
    "cost": 750,
    "width":200,
    "height": 200,
    "windup_duration": 50,
    "attack_duration": 200,
    "recovery_duration": 50,
    "attack_interval": 10,
    "idle_frames": [f"cat_folder/rickroll/walking/frame_000.png"],#900
    "move_frames": [f"cat_folder/rickroll/walking/frame_00{i}.png" for i in range(1, 10)]\
         + [f"cat_folder/rickroll/walking/frame_0{i}.png" for i in range(10, 28)],
    
    "windup_frames": [f"cat_folder/rickroll/attacking/frame_00{i}.png" for i in range(0, 1)] \
        ,
    "attack_frames": [f"cat_folder/rickroll/attacking/frame_00{i}.png" for i in range(1, 10)]\
        + [f"cat_folder/rickroll/attacking/frame_0{i}.png" for i in range(10, 26)], 
        # +[f"cat_folder/rickroll/attacking/frame_000{i}.png" for i in range(100, 103)],
    "recovery_frames": [f"cat_folder/rickroll/attacking/frame_0{i}.png" for i in range(26, 28)],
    
    "kb_frames": [f"cat_folder/rickroll/walking/frame_000.png"],
    "delta_y": -30, # 微調 y 座標
    "ibtn_idle": "cat_folder/rickroll/ibtn_idle.png",
    "ibtn_hover": "cat_folder/rickroll/ibtn_hover.png",
    "ibtn_pressed": "cat_folder/rickroll/ibtn_pressed.png",
    "attack_type": "physic",  # 攻擊類型
    "attack_type": "physic",  # 攻擊類型
    "cat_image": "cat_folder/rickroll/cat_image.png",  # 放在levelselection的貓咪圖片
}