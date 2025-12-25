# game/rewards.py
# Reward settings for each level (index corresponds to the order in the levels list)
LEVEL_REWARDS = {
    0: {  # Level 1
        "base_gold": 200,
        "base_souls": 20,
        "speed_bonus": {             # Speed Clear Bonus (in seconds)
            "threshold": 300,       # Clear within 5 minutes
            "gold": 150,
            "souls": 15
        },
        "first_clear": {
            "gold": 300,
            "souls": 50,
            "unlock_cat": "speed_cat"  # Optional: unlock a new cat
        }
    },
    1: {  # Level 2
        "base_gold": 300,
        "base_souls": 30,
        "speed_bonus": {
            "threshold": 360,       # Clear within 6 minutes
            "gold": 200,
            "souls": 20
        },
        "first_clear": {
            "gold": 400,
            "souls": 60
        }
    },
    # Add rewards for more levels here if needed
    # 2: { ... },
    2:{  # Level 3
        "base_gold": 400,
        "base_souls": 40,
        "speed_bonus": {
            "threshold": 420,       # Clear within 7 minutes
            "gold": 250,
            "souls": 25
        },
        "first_clear": {
            "gold": 500,
            "souls": 70,
            # "unlock_cat": "tank_cat"
        }
    },
    3:{  # Level 4
        "base_gold": 500,
        "base_souls": 50,
        "speed_bonus": {
            "threshold": 480,       # Clear within 8 minutes
            "gold": 300,
            "souls": 30
        },
        "first_clear": {
            "gold": 600,
            "souls": 80,
            # "unlock_cat": "air_cat"
        }
    },
    4: {  # Level 5
        "base_gold": 600,
        "base_souls": 60,
        "speed_bonus": {
            "threshold": 540,       # Clear within 9 minutes
            "gold": 350,
            "souls": 35
        }
    },
}