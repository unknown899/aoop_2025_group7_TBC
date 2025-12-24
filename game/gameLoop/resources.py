# game/gameLoop/resources.py
import json
import os

PLAYER_RESOURCES_FILE = "data/player_resources.json"

class ResourceManager:
    def __init__(self):
        self.gold = 0
        self.souls = 0
        self.load()

    def load(self):
        try:
            if os.path.exists(PLAYER_RESOURCES_FILE):
                with open(PLAYER_RESOURCES_FILE, "r") as f:
                    data = json.load(f)
                    self.gold = data.get("gold", 0)
                    self.souls = data.get("souls", 0)
        except Exception as e:
            print(f"Warning: failed to load resources: {e}")

    def save(self):
        try:
            os.makedirs(os.path.dirname(PLAYER_RESOURCES_FILE), exist_ok=True)
            with open(PLAYER_RESOURCES_FILE, "w") as f:
                json.dump({"gold": self.gold, "souls": self.souls}, f, indent=4)
        except Exception as e:
            print(f"Failed to save resources: {e}")

    def add(self, gold=0, souls=0):
        self.gold += gold
        self.souls += souls
        self.save()

    def reset(self):
        self.gold = 0
        self.souls = 0
        self.save()

    def draw(self, screen, font):
        text = f"Gold: {self.gold}    Souls: {self.souls}"
        shadow = font.render(text, True, (0, 0, 0))
        surf = font.render(text, True, (255, 215, 0))
        screen.blit(shadow, (52, 32))
        screen.blit(surf, (50, 30))