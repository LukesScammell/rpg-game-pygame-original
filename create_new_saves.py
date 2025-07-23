#!/usr/bin/env python
"""
Create properly formatted save files for the multiple save system
"""

import os
import json
from datetime import datetime, timedelta

# Create saves directory
SAVE_FOLDER = "saves"
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

# Create 5 different test save files with complete structure
test_saves = [
    {
        "players": [{
            "x": 5,
            "y": 5,
            "name": "Alexander",
            "char_class": "warrior",
            "hp": 85,
            "max_hp": 100,
            "base_attack": 18,
            "base_defense": 12,
            "level": 6,
            "xp": 1800,
            "mana": 25,
            "max_mana": 25,
            "gold": 250,
            "skill_cooldown": 0,
            "inventory": [
                {
                    "type": "Potion",
                    "name": "Health Potion",
                    "healing": 30,
                    "rarity": "common",
                    "sprite_name": "potion"
                }
            ],
            "weapon": {
                "name": "Iron Sword",
                "attack_bonus": 8,
                "allowed_classes": ["warrior"],
                "rarity": "common",
                "sprite_name": "short_sword1"
            },
            "armor": {
                "name": "Leather Armor",
                "defense_bonus": 5,
                "allowed_classes": ["warrior", "archer"],
                "rarity": "common",
                "sprite_name": "leather_armour1"
            }
        }],
        "dungeon_level": 4,
        "current_player_idx": 0,
        "game_state": "playing",
        "camera_x": 0,
        "camera_y": 0,
        "obtained_items": [],
        "dungeon": None,
        "timestamp": (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "players": [{
            "x": 8,
            "y": 12,
            "name": "Merlin",
            "char_class": "mage",
            "hp": 70,
            "max_hp": 90,
            "base_attack": 14,
            "base_defense": 8,
            "level": 9,
            "xp": 3200,
            "mana": 95,
            "max_mana": 100,
            "gold": 420,
            "skill_cooldown": 0,
            "inventory": [
                {
                    "type": "Potion",
                    "name": "Mana Potion",
                    "healing": 20,
                    "rarity": "common",
                    "sprite_name": "potion"
                },
                {
                    "type": "Potion",
                    "name": "Health Potion",
                    "healing": 30,
                    "rarity": "common",
                    "sprite_name": "potion"
                }
            ],
            "weapon": {
                "name": "Magic Staff",
                "attack_bonus": 10,
                "allowed_classes": ["mage"],
                "rarity": "uncommon",
                "sprite_name": "quarterstaff"
            },
            "armor": None
        }],
        "dungeon_level": 6,
        "current_player_idx": 0,
        "game_state": "playing",
        "camera_x": 0,
        "camera_y": 0,
        "obtained_items": [],
        "dungeon": None,
        "timestamp": (datetime.now() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "players": [{
            "x": 3,
            "y": 7,
            "name": "Robin",
            "char_class": "archer",
            "hp": 60,
            "max_hp": 80,
            "base_attack": 16,
            "base_defense": 10,
            "level": 4,
            "xp": 800,
            "mana": 40,
            "max_mana": 40,
            "gold": 180,
            "skill_cooldown": 0,
            "inventory": [],
            "weapon": {
                "name": "Hunter's Bow",
                "attack_bonus": 12,
                "allowed_classes": ["archer"],
                "rarity": "common",
                "sprite_name": "bow1"
            },
            "armor": {
                "name": "Studded Leather",
                "defense_bonus": 3,
                "allowed_classes": ["archer", "warrior"],
                "rarity": "common",
                "sprite_name": "leather_armour2"
            }
        }],
        "dungeon_level": 3,
        "current_player_idx": 0,
        "game_state": "playing",
        "camera_x": 0,
        "camera_y": 0,
        "obtained_items": [],
        "dungeon": None,
        "timestamp": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "players": [{
            "x": 10,
            "y": 15,
            "name": "Gandalf",
            "char_class": "mage",
            "hp": 45,
            "max_hp": 70,
            "base_attack": 12,
            "base_defense": 6,
            "level": 2,
            "xp": 150,
            "mana": 50,
            "max_mana": 50,
            "gold": 75,
            "skill_cooldown": 0,
            "inventory": [
                {
                    "type": "Potion",
                    "name": "Health Potion",
                    "healing": 30,
                    "rarity": "common",
                    "sprite_name": "potion"
                }
            ],
            "weapon": None,
            "armor": None
        }],
        "dungeon_level": 1,
        "current_player_idx": 0,
        "game_state": "playing",
        "camera_x": 0,
        "camera_y": 0,
        "obtained_items": [],
        "dungeon": None,
        "timestamp": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "players": [{
            "x": 7,
            "y": 9,
            "name": "Legolas",
            "char_class": "archer",
            "hp": 95,
            "max_hp": 110,
            "base_attack": 22,
            "base_defense": 14,
            "level": 12,
            "xp": 5500,
            "mana": 60,
            "max_mana": 60,
            "gold": 680,
            "skill_cooldown": 0,
            "inventory": [
                {
                    "type": "Weapon",
                    "name": "Elven Dagger",
                    "attack_bonus": 6,
                    "allowed_classes": ["archer", "warrior"],
                    "rarity": "rare",
                    "sprite_name": "elven_dagger"
                },
                {
                    "type": "Potion",
                    "name": "Health Potion",
                    "healing": 30,
                    "rarity": "common",
                    "sprite_name": "potion"
                }
            ],
            "weapon": {
                "name": "Elven Longbow",
                "attack_bonus": 18,
                "allowed_classes": ["archer"],
                "rarity": "epic",
                "sprite_name": "longbow"
            },
            "armor": {
                "name": "Elven Leather Armor",
                "defense_bonus": 8,
                "allowed_classes": ["archer"],
                "rarity": "rare",
                "sprite_name": "elven_leather_armor"
            }
        }],
        "dungeon_level": 8,
        "current_player_idx": 0,
        "game_state": "playing",
        "camera_x": 0,
        "camera_y": 0,
        "obtained_items": [],
        "dungeon": None,
        "timestamp": (datetime.now() - timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
    }
]

# Create properly formatted save files
for i, save_data in enumerate(test_saves, 1):
    filename = os.path.join(SAVE_FOLDER, f"save_slot_{i:02d}.json")
    with open(filename, 'w') as f:
        json.dump(save_data, f, indent=2)
    print(f"Created save: {filename} - {save_data['players'][0]['name']} (Level {save_data['players'][0]['level']} {save_data['players'][0]['char_class'].title()})")

print(f"\n✅ Created 5 properly formatted save files in new format!")
print("All saves include complete player data and should load without issues.")
