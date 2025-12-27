import json
import random
import os

from  .constants import GACHA_COST_GOLD, GACHA_COST_SOULS, RESOURCE_FILE, UNLOCKED_FILE

def perform_gacha():
    """
    執行轉蛋邏輯
    回傳: (success, result_dict)
    """
    if not os.path.exists(RESOURCE_FILE):
        return False, {"msg": "File Missing"}
    
    with open(RESOURCE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. 資源檢查
    if data["gold"] < GACHA_COST_GOLD or data["souls"] < GACHA_COST_SOULS:
        return False, {"msg": "Insufficient Resources!"}

    # 2. 扣除資源並存檔
    data["gold"] -= GACHA_COST_GOLD
    data["souls"] -= GACHA_COST_SOULS
    with open(RESOURCE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    # 3. 抽獎
    all_cats = ["basic", 
                "speedy", 
                "eraser", 
                "mtank", 
                "tank", 
                "kp",
                "rickroll",
                "oiia",
                ]
    result = {"won_id": None, "is_new": False, "msg": ""}

    if random.random() < 0.5: # 20% 沒抽中
        result["msg"] = "Try Again!"
    else:
        won_cat = random.choice(all_cats)
        result["won_id"] = won_cat
        
        # 讀取已解鎖清單
        unlocked = []
        if os.path.exists(UNLOCKED_FILE):
            with open(UNLOCKED_FILE, "r", encoding="utf-8") as f:
                unlocked = json.load(f)
        
        if won_cat not in unlocked:
            unlocked.append(won_cat)
            result["is_new"] = True
            with open(UNLOCKED_FILE, "w", encoding="utf-8") as f:
                json.dump(unlocked, f, indent=4)
            result["msg"] = f"NEW HERO: {won_cat.upper()}!"
        else:
            result["is_new"] = False
            result["msg"] = f"GOT {won_cat.upper()} (Duplicate)"

    return True, result