cat_config = {
    "id":105,
    "hp": 12,
    "atk": 900,
    "speed": 1,
    "color": (0, 255, 255),
    "attack_range": 510,
    "is_aoe": True,
    "kb_limit": 5,
    "cooldown": 5000,
    "cost": 5100,
    "width":400,
    "height": 200,
    "windup_duration": 500,
    "attack_duration": 500,
    "recovery_duration": 50,
    "attack_interval": 10000,
    "idle_frames": [f"cat_folder/chucky/walking/frame_{i:03d}.png" for i in range(1, 2)],#900
    "move_frames": [f"cat_folder/chucky/walking/frame_{i:03d}.png" for i in range(1, 17)]\
        ,
    
    "windup_frames": [f"cat_folder/chucky/walkingC/frame_{i:03d}.png" for i in range(17, 18)] \
        ,
    "attack_frames": [f"cat_folder/chucky/walkingC/frame_{i:03d}.png" for i in range(18, 19)], \

    "recovery_frames": [f"cat_folder/chucky/walkingC/frame_{i:03d}.png" for i in range(19, 20)],
    
    "kb_frames": [f"cat_folder/chucky/walking/frame_{i:03d}.png" for i in range(1, 2)],
    "delta_y": -52, # 微調 y 座標
    "ibtn_idle": "cat_folder/chucky/ibtn_idle.png",
    "ibtn_hover": "cat_folder/chucky/ibtn_hover.png",
    "ibtn_pressed": "cat_folder/chucky/ibtn_pressed.png",
    "attack_type": "physic",  # 攻擊類型
    "attack_type": "physic",  # 攻擊類型
    "cat_image": "cat_folder/chucky/cat_image.png",  # 放在levelselection的貓咪圖片
}