#!/usr/bin/env python
"""
Create proper test save files with complete structure for the multiple save system
"""

import os
import json
from datetime import datetime

# Create saves directory
SAVE_FOLDER = "saves"
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

# Create proper test save files with complete structure
test_saves = [
    {
        "players": [{
            "x": 5,
            "y": 5,
            "name": "TestWarrior",
            "char_class": "warrior",
            "hp": 75,
            "max_hp": 100,
            "base_attack": 15,
            "base_defense": 10,
            "level": 5,
            "xp": 1200,
            "mana": 20,
            "max_mana": 20,
            "gold": 150,
            "skill_cooldown": 0,
            "inventory": [],
            "weapon": None,
            "armor": None
        }],
        "dungeon_level": 3,
        "current_player_idx": 0,
        "game_state": "playing",
        "camera_x": 0,
        "camera_y": 0,
        "obtained_items": [],
        "dungeon": None,
        "timestamp": "2025-01-20 14:30:00"
    },
    {
        "players": [{
            "x": 8,
            "y": 10,
            "name": "TestMage",
            "char_class": "mage",
            "hp": 60,
            "max_hp": 80,
            "base_attack": 12,
            "base_defense": 8,
            "level": 8,
            "xp": 2800,
            "mana": 80,
            "max_mana": 80,
            "gold": 300,
            "skill_cooldown": 0,
            "inventory": [],
            "weapon": None,
            "armor": None
        }],
        "dungeon_level": 5,
        "current_player_idx": 0,
        "game_state": "playing",
        "camera_x": 0,
        "camera_y": 0,
        "obtained_items": [],
        "dungeon": None,
        "timestamp": "2025-01-21 10:15:00"
    },
    {
        "players": [{
            "x": 3,
            "y": 7,
            "name": "TestArcher",
            "char_class": "archer",
            "hp": 50,
            "max_hp": 70,
            "base_attack": 14,
            "base_defense": 9,
            "level": 3,
            "xp": 500,
            "mana": 30,
            "max_mana": 30,
            "gold": 80,
            "skill_cooldown": 0,
            "inventory": [],
            "weapon": None,
            "armor": None
        }],
        "dungeon_level": 2,
        "current_player_idx": 0,
        "game_state": "playing",
        "camera_x": 0,
        "camera_y": 0,
        "obtained_items": [],
        "dungeon": None,
        "timestamp": "2025-01-22 16:45:00"
    }
]

# Remove old incomplete saves
for i in range(1, 4):
    filename = os.path.join(SAVE_FOLDER, f"save_slot_{i:02d}.json")
    if os.path.exists(filename):
        os.remove(filename)
        print(f"Removed old incomplete save: {filename}")

# Create proper test save files
for i, save_data in enumerate(test_saves, 1):
    filename = os.path.join(SAVE_FOLDER, f"save_slot_{i:02d}.json")
    with open(filename, 'w') as f:
        json.dump(save_data, f, indent=2)
    print(f"Created proper test save: {filename}")

print("\nComplete test save files created successfully!")
print("These saves now include all required player attributes and should load properly.")
