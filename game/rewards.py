# game/rewards.py

import random
from typing import List, Dict, Any

"""
完整的獎勵系統（2025 版）

功能特色：
- repeatable      : 每次通關都會抽一次（刷關動力）
- first_clear      : 只有第一次通關才會抽一次（稀有貓咪、金幣大包）
- speed_bonus      : 多階速度通關獎勵（僅首次通關可領）
                    → 改為 list，按時間從嚴到寬排序
                    → 只給符合的最高一階（不重複領）

支援的 reward 內容：
    - gold: int
    - souls: int
    - unlock_cat: str (貓咪類型名稱)
    - item: str (未來道具用，可擴充)

draw_reward() 會從帶權重的池子抽取一個 reward dict
"""

LEVEL_REWARDS: Dict[int, Dict[str, Any]] = {
    0: {  # 新手關卡
        "first_clear": [
            {"weight": 5, "reward": {"gold": 200, "souls": 30}},
            {"weight": 60,  "reward": {"gold": 300, "souls": 50}},
            # {"weight": 30,  "reward": {"unlock_cat": "tank_cat"}},
            # {"weight": 15,  "reward": {"unlock_cat": "laser_cat"}},
            {"weight": 100,   "reward": {"gold": 500, "souls": 100, "unlock_cat": "mtank"}},
        ],
        "repeatable": [
            {"weight": 100, "reward": {"gold": 100, "souls": 10}},
            {"weight": 60,  "reward": {"gold": 150, "souls": 20}},
            {"weight": 30,  "reward": {"gold": 200, "souls": 30}},
            {"weight": 10,  "reward": {"gold": 300, "souls": 50}},
        ],
        "speed_bonus": [
            {
                "threshold": 120,   # ≤ 2分鐘（神速）
                "gold": 500,
                "souls": 100,
                "bonus_name": "★★★ Perfect Clear!"
            },
            {
                "threshold": 180,   # ≤ 3分鐘
                "gold": 300,
                "souls": 60,
                "bonus_name": "★★ Speed Clear!"
            },
            {
                "threshold": 240,   # ≤ 4分鐘
                "gold": 150,
                "souls": 30,
                "bonus_name": "★ Fast Clear"
            }
        ]
    },

    1: {
        "first_clear": [
            {"weight": 10, "reward": {"gold": 400, "souls": 60}},
            {"weight": 60,  "reward": {"gold": 600, "souls": 90}},
            {"weight": 70,  "reward": {"unlock_cat": "speedy"}},
            # {"weight": 15,  "reward": {"unlock_cat": "mythic_cat"}},
            {"weight": 8,   "reward": {"gold": 1000, "souls": 200, "unlock_cat": "uber_cat"}},
        ],
        "repeatable": [
            {"weight": 100, "reward": {"gold": 120, "souls": 15}},
            {"weight": 60,  "reward": {"gold": 180, "souls": 25}},
            {"weight": 30,  "reward": {"gold": 250, "souls": 40}},
        ],
        "speed_bonus": [
            {
                "threshold": 180,   # ≤ 3分鐘（極難）
                "gold": 800,
                "souls": 150,
                "bonus_name": "★★★ Master Clear!"
            },
            {
                "threshold": 240,
                "gold": 400,
                "souls": 80,
                "bonus_name": "★★ Speed Clear!"
            },
            {
                "threshold": 300,
                "gold": 200,
                "souls": 50,
                "bonus_name": "★ Fast Clear"
            }
        ]
    },

    2: {
        "first_clear": [
            {"weight": 100, "reward": {"gold": 600, "souls": 100}},
            {"weight": 60,  "reward": {"gold": 800, "souls": 140}},
            # {"weight": 35,  "reward": {"unlock_cat": "jammer_cat"}},
            {"weight": 20,  "reward": {"unlock_cat": "tank"}},
            {"weight": 10,  "reward": {"gold": 1500, "souls": 300, "unlock_cat": "bahamut_cat"}},
        ],
        "repeatable": [
            {"weight": 100, "reward": {"gold": 150, "souls": 20}},
            {"weight": 70,  "reward": {"gold": 220, "souls": 35}},
            {"weight": 40,  "reward": {"gold": 320, "souls": 55}},
        ],
        "speed_bonus": [
            {
                "threshold": 240,   # ≤ 4分鐘
                "gold": 1000,
                "souls": 200,
                "bonus_name": "★★★ Insane Speed!"
            },
            {
                "threshold": 300,
                "gold": 500,
                "souls": 100,
                "bonus_name": "★★ Speed Clear!"
            },
            {
                "threshold": 360,
                "gold": 250,
                "souls": 60,
                "bonus_name": "★ Fast Clear"
            }
        ]
    },

    3: {
        "first_clear": [
            {"weight": 100, "reward": {"gold": 800, "souls": 150}},
            {"weight": 70,  "reward": {"gold": 1200, "souls": 220}},
            # {"weight": 40,  "reward": {"unlock_cat": "cyborg_cat"}},
            # {"weight": 25,  "reward": {"unlock_cat": "dark_cat"}},
            {"weight": 12,  "reward": {"gold": 2000, "souls": 400, "unlock_cat": "mitama_cat"}},
        ],
        "repeatable": [
            {"weight": 100, "reward": {"gold": 180, "souls": 25}},
            {"weight": 70,  "reward": {"gold": 260, "souls": 45}},
            {"weight": 40,  "reward": {"gold": 380, "souls": 65}},
        ],
        "speed_bonus": [
            {
                "threshold": 300,   # ≤ 5分鐘
                "gold": 1500,
                "souls": 300,
                "bonus_name": "★★★ Godlike Clear!"
            },
            {
                "threshold": 360,
                "gold": 700,
                "souls": 150,
                "bonus_name": "★★ Speed Clear!"
            },
            {
                "threshold": 480,
                "gold": 350,
                "souls": 80,
                "bonus_name": "★ Fast Clear"
            }
        ]
    },

    4: {  # 最終關卡
        "first_clear": [
            {"weight": 100, "reward": {"gold": 1500, "souls": 300}},
            {"weight": 60,  "reward": {"gold": 2500, "souls": 500}},
            # {"weight": 40,  "reward": {"gold": 3000, "souls": 600, "unlock_cat": "legend_cat"}},
            # {"weight": 20,  "reward": {"gold": 5000, "souls": 1000, "unlock_cat": "true_form_cat"}},
            # {"weight": 8,   "reward": {"gold": 8000, "souls": 1500, "unlock_cat": "ancient_cat"}},
        ],
        "repeatable": [
            {"weight": 100, "reward": {"gold": 250, "souls": 40}},
            {"weight": 70,  "reward": {"gold": 400, "souls": 70}},
            {"weight": 40,  "reward": {"gold": 600, "souls": 100}},
        ],
        "speed_bonus": [
            {
                "threshold": 360,   # ≤ 6分鐘（傳說級）
                "gold": 5000,
                "souls": 1000,
                "bonus_name": "★★★ Legendary Speed!"
            },
            {
                "threshold": 480,   # ≤ 8分鐘
                "gold": 2000,
                "souls": 400,
                "bonus_name": "★★ Extreme Clear!"
            },
            {
                "threshold": 600,   # ≤ 10分鐘
                "gold": 800,
                "souls": 200,
                "bonus_name": "★ Speed Clear"
            }
        ]
    }
}


def draw_reward(pool: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    從帶權重的獎勵池中隨機抽取一個獎勵。
    返回 reward dict（例如 {"gold": 200, "souls": 30, "unlock_cat": "dragon_cat"}）
    若 pool 為空，返回空 dict。
    """
    if not pool:
        return {}

    total_weight = sum(item["weight"] for item in pool)
    if total_weight == 0:
        return {}

    r = random.randint(1, total_weight)
    current = 0
    for item in pool:
        current += item["weight"]
        if r <= current:
            return item["reward"]

    # 保底（理論上不會執行到這裡）
    return pool[-1]["reward"]