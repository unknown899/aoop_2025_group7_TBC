cat_config = {
    "id":102,
    "hp": 1000,
    "atk": 20,
    "speed": 5,
    "color": (0, 255, 255),
    "attack_range": 210,
    "is_aoe": True,
    "kb_limit": 1,
    "cooldown": 5000,
    "cost": 900,
    "width":200,
    "height": 200,
    "windup_duration": 50,
    "attack_duration": 200,
    "recovery_duration": 50,
    "attack_interval": 10,
    "idle_frames": [f"cat_folder/oiia/walking/frame_000.png"],#900
    "move_frames": [f"cat_folder/oiia/walking/frame_00{i}.png" for i in range(1, 10)]\
         + [f"cat_folder/oiia/walking/frame_0{i}.png" for i in range(10, 41)],
    
    "windup_frames": [f"cat_folder/oiia/attacking/frame_0{i}.png" for i in range(41, 51)] \
        ,
    "attack_frames": [f"cat_folder/oiia/attacking/frame_0{i}.png" for i in range(51, 71)], \
        # + [f"cat_folder/oiia/attacking/frame_0{i}.png" for i in range(10, 26)], 
        # +[f"cat_folder/oiia/attacking/frame_000{i}.png" for i in range(100, 103)],
    "recovery_frames": [f"cat_folder/oiia/attacking/frame_0{i}.png" for i in range(71, 94)],
    
    "kb_frames": [f"cat_folder/oiia/walking/frame_000.png"],
    "delta_y": -42, # 微調 y 座標
    "ibtn_idle": "cat_folder/oiia/ibtn_idle.png",
    "ibtn_hover": "cat_folder/oiia/ibtn_hover.png",
    "ibtn_pressed": "cat_folder/oiia/ibtn_pressed.png",
    "attack_type": "physic",  # 攻擊類型
    "attack_type": "physic",  # 攻擊類型
    "cat_image": "cat_folder/oiia/cat_image.png",  # 放在levelselection的貓咪圖片
}