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
}