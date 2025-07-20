#!/usr/bin/env python
print("--- RUNNING PYGAME VERSION ---")
import random
import os
import json
import pygame
from collections import deque

# --- Constants ---
SCREEN_WIDTH = 1920  # Increased for larger display
SCREEN_HEIGHT = 1080  # Increased for larger display
MAP_WIDTH = 40
MAP_HEIGHT = 20
TILE_SIZE = 48  # Increased tile size for better visibility
VIEWPORT_WIDTH = 20  # More tiles visible horizontally
VIEWPORT_HEIGHT = 15  # More tiles visible vertically
MINIMAP_SIZE = 250  # Larger minimap
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 15
MAX_DUNGEON_LEVEL = 5
HIGHSCORE_FILE = "rpg_highscores.json"
SETTINGS_FILE = "rpg_settings.json"
SAVE_FILE = "rpg_save_game.json"

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)
FOG_COLOR = (40, 40, 60)  # Dark blue-ish for unexplored areas

# --- Pygame Setup ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Python RPG Adventure")

# --- Settings System ---
def load_settings():
    """Load game settings from file."""
    default_settings = {
        "use_emojis": True,
        "wall_sprite": "stone_brick1.png",
        "floor_sprite": "sandstone_floor0.png"
    }
    try:
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
            # Ensure all default keys exist
            for key, value in default_settings.items():
                if key not in settings:
                    settings[key] = value
            return settings
    except (FileNotFoundError, json.JSONDecodeError):
        return default_settings

def save_settings(settings):
    """Save game settings to file."""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"Could not save settings: {e}")

# Load game settings
game_settings = load_settings()

# --- Sprite Loading ---
sprites = {}
ui_elements = {}

def load_sprites():
    """Load all sprite images."""
    global sprites
    sprite_path = os.path.join("assets", "crawl-tiles Oct-5-2010", "dc-dngn")
    
    # Load wall sprites
    wall_path = os.path.join(sprite_path, "wall")
    floor_path = os.path.join(sprite_path, "floor")
    
    # Load specific wall and floor sprites
    wall_files = ["stone_brick1.png", "stone_dark0.png", "brick_brown0.png", "marble_wall1.png"]
    floor_files = ["sandstone_floor0.png", "dirt0.png", "pebble_brown0.png", "marble_floor1.png"]
    
    print("Loading wall sprites...")
    for wall_file in wall_files:
        try:
            wall_sprite_path = os.path.join(wall_path, wall_file)
            if os.path.exists(wall_sprite_path):
                sprites[f"wall_{wall_file}"] = pygame.image.load(wall_sprite_path)
                sprites[f"wall_{wall_file}"] = pygame.transform.scale(sprites[f"wall_{wall_file}"], (TILE_SIZE, TILE_SIZE))
                print(f"  Loaded: {wall_file}")
            else:
                print(f"  Warning: Wall sprite not found: {wall_sprite_path}")
        except pygame.error as e:
            print(f"  Error loading wall sprite {wall_file}: {e}")
    
    print("Loading floor sprites...")
    for floor_file in floor_files:
        try:
            floor_sprite_path = os.path.join(floor_path, floor_file)
            if os.path.exists(floor_sprite_path):
                sprites[f"floor_{floor_file}"] = pygame.image.load(floor_sprite_path)
                sprites[f"floor_{floor_file}"] = pygame.transform.scale(sprites[f"floor_{floor_file}"], (TILE_SIZE, TILE_SIZE))
                print(f"  Loaded: {floor_file}")
            else:
                print(f"  Warning: Floor sprite not found: {floor_sprite_path}")
        except pygame.error as e:
            print(f"  Error loading floor sprite {floor_file}: {e}")
    
    # Load stairs sprite
    print("Loading stairs sprite...")
    try:
        stairs_path = os.path.join(sprite_path, "dngn_closed_door.png")
        if os.path.exists(stairs_path):
            sprites["stairs"] = pygame.image.load(stairs_path)
            sprites["stairs"] = pygame.transform.scale(sprites["stairs"], (TILE_SIZE, TILE_SIZE))
            print("  Loaded: stairs (dngn_closed_door.png)")
        else:
            print(f"  Warning: Stairs sprite not found: {stairs_path}")
    except pygame.error as e:
        print(f"  Error loading stairs sprite: {e}")
    
    # Load player sprites
    print("Loading player sprites...")
    player_base_path = os.path.join("assets", "crawl-tiles Oct-5-2010", "player", "base")
    player_sprites = {
        "warrior": "human_m.png",       # Male human warrior
        "mage": "human_f.png",         # Female human mage  
        "archer": "elf_m.png",         # Male elf archer
        "rogue": "elf_f.png"           # Female elf rogue
    }
    
    for class_name, sprite_file in player_sprites.items():
        try:
            sprite_file_path = os.path.join(player_base_path, sprite_file)
            if os.path.exists(sprite_file_path):
                sprites[f"player_{class_name}"] = pygame.image.load(sprite_file_path)
                sprites[f"player_{class_name}"] = pygame.transform.scale(sprites[f"player_{class_name}"], (TILE_SIZE, TILE_SIZE))
                print(f"  Loaded: {class_name} ({sprite_file})")
            else:
                print(f"  Warning: Player sprite not found: {sprite_file_path}")
        except pygame.error as e:
            print(f"  Error loading player sprite {sprite_file}: {e}")
    
    # Load monster sprites
    print("Loading monster sprites...")
    monster_path = os.path.join("assets", "crawl-tiles Oct-5-2010", "dc-mon")
    monster_sprites = {
        "goblin": "goblin.png",
        "orc": "orc_warrior.png", 
        "troll": "troll.png",
        "dragon": "dragon.png"      # Changed from dragon_gold.png to dragon.png
    }
    
    for monster_name, sprite_file in monster_sprites.items():
        try:
            sprite_file_path = os.path.join(monster_path, sprite_file)
            if os.path.exists(sprite_file_path):
                sprites[f"monster_{monster_name}"] = pygame.image.load(sprite_file_path)
                sprites[f"monster_{monster_name}"] = pygame.transform.scale(sprites[f"monster_{monster_name}"], (TILE_SIZE, TILE_SIZE))
                print(f"  Loaded: {monster_name} ({sprite_file})")
            else:
                print(f"  Warning: Monster sprite not found: {sprite_file_path}")
        except pygame.error as e:
            print(f"  Error loading monster sprite {sprite_file}: {e}")
    
    # Load item sprites  
    print("Loading item sprites...")
    item_base_path = os.path.join("assets", "crawl-tiles Oct-5-2010", "item")
    
    # Load potions
    potion_path = os.path.join(item_base_path, "potion", "i-heal-wounds.png")
    if os.path.exists(potion_path):
        sprites["item_potion"] = pygame.image.load(potion_path)
        sprites["item_potion"] = pygame.transform.scale(sprites["item_potion"], (TILE_SIZE, TILE_SIZE))
        print("  Loaded: potion (i-heal-wounds.png)")
    else:
        print("  Warning: Potion sprite not found")
    
    # Load weapon sprites
    print("Loading weapon sprites...")
    weapon_path = os.path.join(item_base_path, "weapon")
    weapon_sprites = [
        "dagger.png", "short_sword1.png", "long_sword1.png", "battle_axe1.png", 
        "war_axe1.png", "greatsword1.png", "executioner_axe1.png", "demon_blade.png",
        "quarterstaff.png", "elven_dagger.png", "blessed_blade.png", "demon_trident.png", "trishula.png"
    ]
    
    # Load ranged weapons
    ranged_path = os.path.join(weapon_path, "ranged")
    ranged_sprites = ["sling1.png", "bow1.png", "bow2.png", "crossbow1.png", "longbow.png", "throwing_net.png"]
    
    for weapon_file in weapon_sprites:
        try:
            weapon_sprite_path = os.path.join(weapon_path, weapon_file)
            if os.path.exists(weapon_sprite_path):
                sprite_key = f"weapon_{weapon_file.replace('.png', '')}"
                sprites[sprite_key] = pygame.image.load(weapon_sprite_path)
                sprites[sprite_key] = pygame.transform.scale(sprites[sprite_key], (TILE_SIZE, TILE_SIZE))
                print(f"  Loaded: {weapon_file}")
            else:
                print(f"  Warning: Weapon sprite not found: {weapon_file}")
        except pygame.error as e:
            print(f"  Error loading weapon sprite {weapon_file}: {e}")
    
    for ranged_file in ranged_sprites:
        try:
            ranged_sprite_path = os.path.join(ranged_path, ranged_file)
            if os.path.exists(ranged_sprite_path):
                sprite_key = f"weapon_{ranged_file.replace('.png', '')}"
                sprites[sprite_key] = pygame.image.load(ranged_sprite_path)
                sprites[sprite_key] = pygame.transform.scale(sprites[sprite_key], (TILE_SIZE, TILE_SIZE))
                print(f"  Loaded: ranged/{ranged_file}")
            else:
                print(f"  Warning: Ranged weapon sprite not found: {ranged_file}")
        except pygame.error as e:
            print(f"  Error loading ranged weapon sprite {ranged_file}: {e}")
    
    # Load armor sprites
    print("Loading armor sprites...")
    armor_path = os.path.join(item_base_path, "armour")
    armor_sprites = [
        "leather_armour1.png", "leather_armour2.png", "elven_leather_armor.png", "troll_hide.png",
        "ring_mail1.png", "scale_mail1.png", "chain_mail1.png", "banded_mail1.png",
        "splint_mail1.png", "plate_mail1.png", "crystal_plate_mail.png"
    ]
    
    for armor_file in armor_sprites:
        try:
            armor_sprite_path = os.path.join(armor_path, armor_file)
            if os.path.exists(armor_sprite_path):
                sprite_key = f"armor_{armor_file.replace('.png', '')}"
                sprites[sprite_key] = pygame.image.load(armor_sprite_path)
                sprites[sprite_key] = pygame.transform.scale(sprites[sprite_key], (TILE_SIZE, TILE_SIZE))
                print(f"  Loaded: {armor_file}")
            else:
                print(f"  Warning: Armor sprite not found: {armor_file}")
        except pygame.error as e:
            print(f"  Error loading armor sprite {armor_file}: {e}")
    
    # Load treasure chest sprite from dungeon folder
    print("Loading treasure chest sprites...")
    dungeon_path = os.path.join("assets", "dungeon")
    chest_files = ["chest.png", "chest2.png"]
    
    for chest_file in chest_files:
        try:
            chest_sprite_path = os.path.join(dungeon_path, chest_file)
            if os.path.exists(chest_sprite_path):
                sprite_key = "chest_closed" if "chest.png" == chest_file else "chest_open"
                sprites[sprite_key] = pygame.image.load(chest_sprite_path)
                sprites[sprite_key] = pygame.transform.scale(sprites[sprite_key], (TILE_SIZE, TILE_SIZE))
                print(f"  Loaded: {sprite_key} ({chest_file})")
            else:
                print(f"  Warning: Chest sprite not found: {chest_sprite_path}")
        except pygame.error as e:
            print(f"  Error loading chest sprite {chest_file}: {e}")
    
    # Also load from Dungeon Crawl Stone Soup Full for additional weapons
    print("Loading additional weapon sprites from Dungeon Crawl Stone Soup Full...")
    full_weapon_path = os.path.join("assets", "Dungeon Crawl Stone Soup Full", "item", "weapon")
    
    # Additional weapon sprites to load (using actual available files)
    additional_weapons = [
        "ancient_sword.png", "axe.png", "claymore.png", "cutlass_1.png", "golden_sword.png",
        "halberd_1.png", "hammer_1_new.png", "katana.png", "mace_1_new.png", "rapier_1.png",
        "scimitar_1_new.png", "scythe_1_new.png", "trident_1.png", "war_hammer.png"
    ]
    
    for weapon_file in additional_weapons:
        try:
            weapon_sprite_path = os.path.join(full_weapon_path, weapon_file)
            if os.path.exists(weapon_sprite_path):
                sprite_key = f"weapon_{weapon_file.replace('.png', '')}"
                sprites[sprite_key] = pygame.image.load(weapon_sprite_path)
                sprites[sprite_key] = pygame.transform.scale(sprites[sprite_key], (TILE_SIZE, TILE_SIZE))
                print(f"  Loaded: {weapon_file}")
            else:
                print(f"  Warning: Additional weapon sprite not found: {weapon_file}")
        except pygame.error as e:
            print(f"  Error loading additional weapon sprite {weapon_file}: {e}")
    
    print(f"Sprite loading complete. Loaded {len(sprites)} sprites.")

    # Load UI elements
    print("Loading UI elements...")
    gui_path = os.path.join("assets", "crawl-tiles Oct-5-2010", "gui")
    
    # Load individual UI elements
    ui_files = {
        "tab_selected": "tab_selected.png",
        "tab_unselected": "tab_unselected.png", 
        "tab_mouseover": "tab_mouseover.png",
        "tab_item": "tab_label_item.png",
        "tab_spell": "tab_label_spell.png",
        "tab_monster": "tab_label_monster.png"
    }
    
    for ui_name, ui_file in ui_files.items():
        try:
            ui_file_path = os.path.join(gui_path, ui_file)
            if os.path.exists(ui_file_path):
                ui_elements[ui_name] = pygame.image.load(ui_file_path)
                ui_elements[ui_name] = pygame.transform.scale(ui_elements[ui_name], (64, 32))  # Standard button size
                print(f"  Loaded: {ui_name} ({ui_file})")
            else:
                print(f"  Warning: UI element not found: {ui_file_path}")
        except pygame.error as e:
            print(f"  Error loading UI element {ui_file}: {e}")
    
    print(f"UI loading complete. Loaded {len(ui_elements)} UI elements.")

# Load sprites
load_sprites()

# --- Font Setup ---
# Use a font that supports emojis, with a fallback to the default font
try:
    font = pygame.font.Font("C:/Windows/Fonts/seguiemj.ttf", 28)
except FileNotFoundError:
    print("Warning: Segoe UI Emoji font not found. Using default font. Emojis may not render correctly.")
    font = pygame.font.Font(None, 32)

small_font = pygame.font.Font(None, 24)

# --- Sound and Music Assets ---
sounds = {}
music_tracks = {}
current_music = None
current_music_state = None

# Music mapping for different game states and enemies
MUSIC_CONFIG = {
    "menu": "Start_Menu_music.ogg",
    "gameplay": "Ruins_(Soundtrack)_music.ogg",
    "combat_goblin": "Spider_Dance_music.ogg",
    "combat_orc": "Heartache_music.ogg",
    "combat_troll": "Heartache_music.ogg", 
    "combat_dragon": "Dummy!_music.ogg"
}

def load_sounds():
    """Load all sound effects from the RPG Sound Pack."""
    global sounds
    sound_pack_path = "RPG Sound Pack"
    
    print("Loading sound effects...")
    
    # Battle sounds
    battle_sounds = {
        "sword_attack": "battle/swing.wav",
        "sword_attack2": "battle/swing2.wav", 
        "sword_attack3": "battle/swing3.wav",
        "magic_spell": "battle/magic1.wav",
        "spell_cast": "battle/spell.wav",
        "sword_draw": "battle/sword-unsheathe.wav",
        "sword_draw2": "battle/sword-unsheathe2.wav"
    }
    
    # Interface sounds
    interface_sounds = {
        "menu_select": "interface/interface1.wav",
        "menu_confirm": "interface/interface2.wav",
        "menu_back": "interface/interface3.wav",
        "button_hover": "interface/interface4.wav",
        "error": "interface/interface5.wav",
        "success": "interface/interface6.wav"
    }
    
    # Inventory sounds
    inventory_sounds = {
        "pickup_coin": "inventory/coin.wav",
        "pickup_coin2": "inventory/coin2.wav",
        "pickup_armor": "inventory/chainmail1.wav",
        "pickup_cloth": "inventory/cloth.wav",
        "pickup_metal": "inventory/metal-small1.wav",
        "pickup_bottle": "inventory/bottle.wav",
        "equip_armor": "inventory/armor-light.wav",
        "drop_item": "inventory/wood-small.wav"
    }
    
    # World sounds
    world_sounds = {
        "door_open": "world/door.wav"
    }
    
    # Enemy sounds
    enemy_sounds = {
        "goblin_hit": "NPC/misc/wolfman.wav",  # Using misc sound for goblin
        "orc_attack": "NPC/ogre/ogre1.wav",
        "orc_hit": "NPC/ogre/ogre2.wav",
        "troll_attack": "NPC/giant/giant1.wav",
        "dragon_roar": "NPC/gutteral beast/beast1.wav"
    }
    
    # Load all sound categories
    all_sounds = {**battle_sounds, **interface_sounds, **inventory_sounds, **world_sounds, **enemy_sounds}
    
    loaded_count = 0
    for sound_name, sound_path in all_sounds.items():
        try:
            full_path = os.path.join(sound_pack_path, sound_path)
            if os.path.exists(full_path):
                sounds[sound_name] = pygame.mixer.Sound(full_path)
                print(f"  Loaded: {sound_name}")
                loaded_count += 1
            else:
                print(f"  Warning: Sound not found: {full_path}")
        except pygame.error as e:
            print(f"  Error loading {sound_name}: {e}")
    
    print(f"Sound loading complete. Loaded {loaded_count} sound effects.")

def load_music_tracks():
    """Load all background music tracks."""
    global music_tracks
    music_path = "music"
    
    print("Loading background music...")
    
    loaded_count = 0
    for music_state, filename in MUSIC_CONFIG.items():
        try:
            full_path = os.path.join(music_path, filename)
            if os.path.exists(full_path):
                music_tracks[music_state] = full_path
                print(f"  Loaded: {music_state} -> {filename}")
                loaded_count += 1
            else:
                print(f"  Warning: Music not found: {full_path}")
        except Exception as e:
            print(f"  Error loading {music_state}: {e}")
    
    print(f"Music loading complete. Loaded {loaded_count} music tracks.")

def play_music(music_state, loop=True, volume=0.7):
    """Play background music for the given state."""
    global current_music, current_music_state
    
    # Don't restart the same music
    if current_music_state == music_state and pygame.mixer.music.get_busy():
        return
    
    if music_state in music_tracks:
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(music_tracks[music_state])
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1 if loop else 0)
            current_music = music_tracks[music_state]
            current_music_state = music_state
            print(f"Playing music: {music_state}")
        except pygame.error as e:
            print(f"Error playing music {music_state}: {e}")
    else:
        print(f"Music state '{music_state}' not found")

def stop_music():
    """Stop all background music."""
    global current_music, current_music_state
    pygame.mixer.music.stop()
    current_music = None
    current_music_state = None

def get_combat_music_for_enemies(enemies):
    """Determine which combat music to play based on enemy types."""
    # Priority order: dragon > troll > orc > goblin
    enemy_types = [enemy.enemy_type for enemy in enemies]
    
    if "dragon" in enemy_types:
        return "combat_dragon"
    elif "troll" in enemy_types:
        return "combat_troll"
    elif "orc" in enemy_types:
        return "combat_orc"
    elif "goblin" in enemy_types:
        return "combat_goblin"
    else:
        return "combat_goblin"  # Default fallback

def play_sound(sound_name, volume=1.0):
    """Play a sound effect if it exists."""
    if sound_name in sounds and sounds[sound_name]:
        sound = sounds[sound_name]
        sound.set_volume(volume)
        sound.play()

def play_random_sound(sound_list, volume=1.0):
    """Play a random sound from a list of sound names."""
    if sound_list:
        import random
        sound_name = random.choice(sound_list)
        play_sound(sound_name, volume)

# Load all sounds
load_sounds()

# Load all music tracks
load_music_tracks()

# Legacy sound variables for compatibility
sword_sound = sounds.get("sword_attack")
magic_sound = sounds.get("magic_spell") 
arrow_sound = sounds.get("sword_attack")  # Using sword sound for arrows temporarily
damage_sound = sounds.get("sword_attack2")

# --- UI Elements ---
UI = {
    "player": "🧑",
    "warrior": "🤺",
    "mage": "🧙",
    "archer": "🏹",
    "goblin": "👺",
    "orc": "👹",
    "troll": "🗿",
    "dragon": "🐉",
    "potion": "🧪",
    "weapon": "⚔️",
    "armor": "🛡️",
    "wall": "🧱",
    "floor": ".",
    "stairs": "🔽",
    "hp": "❤️",
    "xp": "✨",
    "mana": "💧",
    "attack": "💥",
    "defense": "🛡️",
    "level": "🌟"
}

# --- Character Classes ---
CLASSES = {
    "warrior": {"hp": 120, "attack": 15, "defense": 10, "icon": UI["warrior"], "weapon": "Sword", "mana": 0},
    "mage": {"hp": 80, "attack": 20, "defense": 5, "icon": UI["mage"], "weapon": "Staff", "mana": 20},
    "archer": {"hp": 100, "attack": 12, "defense": 8, "icon": UI["archer"], "weapon": "Bow", "mana": 0}
}

# --- Enemy Types ---
ENEMIES = {
    "goblin": {"hp": 30, "attack": 8, "defense": 2, "xp": 50, "icon": UI["goblin"]},
    "orc": {"hp": 50, "attack": 12, "defense": 4, "xp": 100, "icon": UI["orc"]},
    "troll": {"hp": 80, "attack": 15, "defense": 6, "xp": 150, "icon": UI["troll"]},
    "dragon": {"hp": 250, "attack": 25, "defense": 15, "xp": 1000, "icon": UI["dragon"]}
}

# --- Items ---
class Item:
    def __init__(self, name, icon):
        self.name = name
        self.icon = icon
        self.rarity = "common"  # common, uncommon, rare, epic
        self.value = 1

class Potion(Item):
    def __init__(self, name, hp_gain, rarity="common"):
        super().__init__(name, UI["potion"])
        self.hp_gain = hp_gain
        self.rarity = rarity
        self.value = hp_gain // 5

    def use(self, target):
        target.hp = min(target.max_hp, target.hp + self.hp_gain)
        return f'{target.name} used {self.name} and gained {self.hp_gain} HP.'

class Weapon(Item):
    def __init__(self, name, attack_bonus, allowed_classes=None, rarity="common", sprite_name=None):
        super().__init__(name, UI["weapon"])
        self.attack_bonus = attack_bonus
        self.allowed_classes = allowed_classes or ["warrior", "mage", "archer"]  # Default: all classes
        self.rarity = rarity
        self.sprite_name = sprite_name
        self.value = attack_bonus * 10

    def can_use(self, character_class):
        return character_class in self.allowed_classes

class Armor(Item):
    def __init__(self, name, defense_bonus, allowed_classes=None, rarity="common", sprite_name=None):
        super().__init__(name, UI["armor"])
        self.defense_bonus = defense_bonus
        self.allowed_classes = allowed_classes or ["warrior", "mage", "archer"]  # Default: all classes
        self.rarity = rarity
        self.sprite_name = sprite_name
        self.value = defense_bonus * 8

    def can_use(self, character_class):
        return character_class in self.allowed_classes

class Treasure:
    """Treasure chests and containers that hold items."""
    def __init__(self, x, y, items=None):
        self.x = x
        self.y = y
        self.items = items or []
        self.opened = False
        self.icon = "💰"  # Treasure chest icon

# --- Enhanced Weapon Definitions ---
WARRIOR_WEAPONS = [
    Weapon("Rusty Dagger", 2, ["warrior"], "common", "dagger"),
    Weapon("Short Sword", 4, ["warrior"], "common", "short_sword1"),
    Weapon("Long Sword", 6, ["warrior"], "common", "long_sword1"),
    Weapon("Battle Axe", 8, ["warrior"], "uncommon", "battle_axe1"),
    Weapon("War Axe", 10, ["warrior"], "uncommon", "war_axe1"),
    Weapon("Greatsword", 12, ["warrior"], "rare", "greatsword1"),
    Weapon("Executioner's Axe", 15, ["warrior"], "rare", "executioner_axe1"),
    Weapon("Demon Blade", 18, ["warrior"], "epic", "demon_blade"),
    Weapon("Ancient Sword", 20, ["warrior"], "epic", "ancient_sword"),
    Weapon("Golden Sword", 22, ["warrior"], "epic", "golden_sword"),
    Weapon("War Hammer", 11, ["warrior"], "rare", "war_hammer"),
    Weapon("Halberd", 13, ["warrior"], "rare", "halberd_1"),
    Weapon("Scythe", 14, ["warrior"], "rare", "scythe_1_new"),
    Weapon("Katana", 16, ["warrior"], "epic", "katana"),
    Weapon("Claymore", 17, ["warrior"], "epic", "claymore"),
]

ARCHER_WEAPONS = [
    Weapon("Sling", 3, ["archer"], "common", "sling1"),
    Weapon("Short Bow", 5, ["archer"], "common", "bow1"),
    Weapon("Crossbow", 7, ["archer"], "uncommon", "crossbow1"),
    Weapon("Long Bow", 9, ["archer"], "uncommon", "longbow"),
    Weapon("Elven Bow", 12, ["archer"], "rare", "bow2"),
    Weapon("Throwing Net", 4, ["archer"], "uncommon", "throwing_net"),
]

MAGE_WEAPONS = [
    Weapon("Quarterstaff", 3, ["mage"], "common", "quarterstaff"),
    Weapon("Elven Dagger", 4, ["mage"], "common", "elven_dagger"),
    Weapon("Blessed Blade", 8, ["mage"], "uncommon", "blessed_blade"),
    Weapon("Demon Trident", 12, ["mage"], "rare", "demon_trident"),
    Weapon("Trishula", 15, ["mage"], "epic", "trishula"),
    Weapon("Mage's Mace", 9, ["mage"], "uncommon", "mace_1_new"),
    Weapon("Scimitar", 10, ["mage"], "rare", "scimitar_1_new"),
    Weapon("Rapier", 11, ["mage"], "rare", "rapier_1"),
]

# Enhanced Armor Definitions
LIGHT_ARMOR = [
    Armor("Leather Vest", 2, ["mage", "archer"], "common", "leather_armour1"),
    Armor("Studded Leather", 3, ["mage", "archer"], "common", "leather_armour2"),
    Armor("Elven Leather", 5, ["mage", "archer"], "uncommon", "elven_leather_armor"),
    Armor("Troll Hide", 4, ["archer"], "uncommon", "troll_hide"),
]

MEDIUM_ARMOR = [
    Armor("Ring Mail", 4, ["warrior", "archer"], "common", "ring_mail1"),
    Armor("Scale Mail", 5, ["warrior", "archer"], "common", "scale_mail1"),
    Armor("Chain Mail", 6, ["warrior"], "uncommon", "chain_mail1"),
    Armor("Banded Mail", 7, ["warrior"], "uncommon", "banded_mail1"),
]

HEAVY_ARMOR = [
    Armor("Splint Mail", 8, ["warrior"], "uncommon", "splint_mail1"),
    Armor("Plate Mail", 10, ["warrior"], "rare", "plate_mail1"),
    Armor("Crystal Plate", 15, ["warrior"], "epic", "crystal_plate_mail"),
]

# Enhanced Potion Definitions
POTIONS = [
    Potion("Minor Healing", 15, "common"),
    Potion("Healing Potion", 25, "common"),
    Potion("Greater Healing", 40, "uncommon"),
    Potion("Superior Healing", 60, "rare"),
]

# --- Pre-defined Items (Updated) ---
ALL_WEAPONS = WARRIOR_WEAPONS + ARCHER_WEAPONS + MAGE_WEAPONS
ALL_ARMOR = LIGHT_ARMOR + MEDIUM_ARMOR + HEAVY_ARMOR
ALL_POTIONS = POTIONS

# --- Entities ---
class Entity:
    def __init__(self, x, y, name, hp, attack, defense, icon):
        self.x = x
        self.y = y
        self.name = name
        self.base_attack = attack
        self.base_defense = defense
        self.max_hp = hp
        self.hp = hp
        self.icon = icon

    @property
    def attack(self):
        bonus = self.weapon.attack_bonus if hasattr(self, 'weapon') and self.weapon else 0
        return self.base_attack + bonus

    @property
    def defense(self):
        bonus = self.armor.defense_bonus if hasattr(self, 'armor') and self.armor else 0
        return self.base_defense + bonus

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, damage):
        if damage > 0 and damage_sound:
            damage_sound.play()
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

class Player(Entity):
    def __init__(self, x, y, name, char_class):
        super().__init__(x, y, name, CLASSES[char_class]["hp"], CLASSES[char_class]["attack"], CLASSES[char_class]["defense"], CLASSES[char_class]["icon"])
        self.char_class = char_class
        self.xp = 0
        self.level = 1
        
        # Class-specific starting weapon
        if char_class == "warrior":
            starting_weapon = Weapon("Iron Sword", 5, ["warrior"], "common", "long_sword1")
        elif char_class == "mage":
            starting_weapon = Weapon("Wooden Staff", 3, ["mage"], "common", "quarterstaff")
        else:  # archer
            starting_weapon = Weapon("Hunter's Bow", 4, ["archer"], "common", "bow1")
        
        self.inventory = [starting_weapon]
        self.weapon = starting_weapon
        self.armor = None
        self.max_mana = CLASSES[char_class]["mana"]
        self.mana = self.max_mana
        self.skill_cooldown = 0
        
        # Inventory limits by item type
        self.max_weapons = 3
        self.max_armor = 2
        self.max_potions = 5

    def get_inventory_by_type(self, item_type):
        """Get items of a specific type from inventory."""
        if item_type == Weapon:
            return [item for item in self.inventory if isinstance(item, Weapon)]
        elif item_type == Armor:
            return [item for item in self.inventory if isinstance(item, Armor)]
        elif item_type == Potion:
            return [item for item in self.inventory if isinstance(item, Potion)]
        return []
    
    def get_max_for_type(self, item_type):
        """Get maximum slots for an item type."""
        if item_type == Weapon:
            return self.max_weapons
        elif item_type == Armor:
            return self.max_armor
        elif item_type == Potion:
            return self.max_potions
        return 0
    
    def can_carry_item(self, item):
        """Check if player can carry this item type."""
        item_type = type(item)
        current_items = self.get_inventory_by_type(item_type)
        max_items = self.get_max_for_type(item_type)
        return len(current_items) < max_items
    
    def get_worst_item(self, item_type):
        """Get the worst item of a specific type for replacement."""
        items = self.get_inventory_by_type(item_type)
        if not items:
            return None
        
        if item_type == Weapon:
            # Return weapon with lowest attack bonus
            return min(items, key=lambda x: x.attack_bonus)
        elif item_type == Armor:
            # Return armor with lowest defense bonus
            return min(items, key=lambda x: x.defense_bonus)
        elif item_type == Potion:
            # Return potion with lowest healing value
            return min(items, key=lambda x: x.hp_gain)
        return None
    
    def should_replace_item(self, new_item):
        """Check if new item is better than worst item of same type."""
        item_type = type(new_item)
        worst_item = self.get_worst_item(item_type)
        
        if not worst_item:
            return False
        
        if isinstance(new_item, Weapon):
            return new_item.attack_bonus > worst_item.attack_bonus
        elif isinstance(new_item, Armor):
            return new_item.defense_bonus > worst_item.defense_bonus
        elif isinstance(new_item, Potion):
            return new_item.hp_gain > worst_item.hp_gain
        
        return False
    
    def try_add_item(self, item, auto_replace=False):
        """Try to add item to inventory with smart replacement logic."""
        item_type = type(item)
        
        # First check if we can just add it
        if self.can_carry_item(item):
            self.inventory.append(item)
            return True, f"Added {item.name} to inventory."
        
        # If auto_replace is enabled and new item is better
        if auto_replace and self.should_replace_item(item):
            worst_item = self.get_worst_item(item_type)
            if worst_item:
                # Don't replace equipped items unless the new item is significantly better
                if ((isinstance(worst_item, Weapon) and worst_item == self.weapon) or
                    (isinstance(worst_item, Armor) and worst_item == self.armor)):
                    # Only replace equipped items if new item is at least 50% better
                    if isinstance(item, Weapon) and item.attack_bonus >= worst_item.attack_bonus * 1.5:
                        self.inventory.remove(worst_item)
                        self.inventory.append(item)
                        return True, f"Replaced {worst_item.name} with {item.name} (much better)."
                    elif isinstance(item, Armor) and item.defense_bonus >= worst_item.defense_bonus * 1.5:
                        self.inventory.remove(worst_item)
                        self.inventory.append(item)
                        return True, f"Replaced {worst_item.name} with {item.name} (much better)."
                    else:
                        return False, f"Inventory full. {item.name} not good enough to replace equipped {worst_item.name}."
                else:
                    # Replace non-equipped item
                    self.inventory.remove(worst_item)
                    self.inventory.append(item)
                    return True, f"Replaced {worst_item.name} with {item.name}."
        
        return False, f"Inventory full. Cannot carry more {item_type.__name__.lower()}s."

    def gain_xp(self, xp):
        self.xp += xp
        if self.xp >= self.level * 100:
            return self.level_up()
        return None

    def level_up(self):
        self.level += 1
        self.max_hp += 20
        self.hp = self.max_hp
        self.base_attack += 5
        self.base_defense += 2
        self.max_mana += 5
        self.mana = self.max_mana
        self.xp = 0
        return f'\n{self.name} leveled up to level {self.level}! Stats increased.'

class Enemy(Entity):
    def __init__(self, x, y, enemy_type):
        super().__init__(x, y, enemy_type.capitalize(), ENEMIES[enemy_type]["hp"], ENEMIES[enemy_type]["attack"], ENEMIES[enemy_type]["defense"], ENEMIES[enemy_type]["icon"])
        self.enemy_type = enemy_type  # Store the enemy type for music selection
        self.xp = ENEMIES[enemy_type]["xp"]
        self.weapon_drops = []  # List of possible weapon drops

# --- Map Generation ---
class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return (center_x, center_y)

    def intersects(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

class Dungeon:
    def __init__(self, width, height, level):
        self.width = width
        self.height = height
        self.level = level
        self.grid = [[UI["wall"] for _ in range(width)] for _ in range(height)]
        self.rooms = []
        self.items = []
        self.enemies = []
        self.treasures = []  # New: treasure chests
        self.stairs_down = None
        # Fog of war system
        self.explored = [[False for _ in range(width)] for _ in range(height)]
        self.visible = [[False for _ in range(width)] for _ in range(height)]
        # Track obtained items for single player to prevent duplicates
        self.obtained_items = set()  # Track item names that have been obtained

    def create_room(self, room):
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.grid[y][x] = UI["floor"]

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.grid[y][x] = UI["floor"]

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.grid[y][x] = UI["floor"]

    def generate(self):
        for _ in range(MAX_ROOMS):
            w = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            h = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            x = random.randint(0, self.width - w - 1)
            y = random.randint(0, self.height - h - 1)

            new_room = Rect(x, y, w, h)
            if any(new_room.intersects(other_room) for other_room in self.rooms):
                continue

            self.create_room(new_room)
            (new_x, new_y) = new_room.center()

            if self.rooms:
                (prev_x, prev_y) = self.rooms[-1].center()
                if random.randint(0, 1) == 1:
                    self.create_h_tunnel(prev_x, new_x, prev_y)
                    self.create_v_tunnel(prev_y, new_y, new_x)
                else:
                    self.create_v_tunnel(prev_y, new_y, prev_x)
                    self.create_h_tunnel(prev_x, new_x, new_y)
            
            self.place_content(new_room)
            self.rooms.append(new_room)
        
        if self.level < MAX_DUNGEON_LEVEL:
            last_room = self.rooms[-1]
            self.stairs_down = last_room.center()
            self.grid[self.stairs_down[1]][self.stairs_down[0]] = UI["stairs"]
        else: # Boss level
            boss_room = self.rooms[-1]
            boss_x, boss_y = boss_room.center()
            self.enemies.append(Enemy(boss_x, boss_y, "dragon"))

    def place_content(self, room):
        num_enemies = random.randint(0, 3)
        for _ in range(num_enemies):
            x = random.randint(room.x1 + 1, room.x2 - 1)
            y = random.randint(room.y1 + 1, room.y2 - 1)
            if not any(e.x == x and e.y == y for e in self.enemies):
                enemy_type = random.choice(list(ENEMIES.keys() - {'dragon'}))
                enemy = Enemy(x, y, enemy_type)
                
                # Add weapon drops based on enemy type
                if enemy_type == "goblin":
                    enemy.weapon_drops = [WARRIOR_WEAPONS[0], ARCHER_WEAPONS[0]]  # Basic weapons
                elif enemy_type == "orc":
                    enemy.weapon_drops = WARRIOR_WEAPONS[1:3] + ARCHER_WEAPONS[1:2]  # Intermediate weapons
                elif enemy_type == "troll":
                    enemy.weapon_drops = WARRIOR_WEAPONS[3:5] + ALL_ARMOR[2:5]  # Advanced weapons and armor
                elif enemy_type == "dragon":
                    enemy.weapon_drops = WARRIOR_WEAPONS[6:] + MAGE_WEAPONS[3:] + ARCHER_WEAPONS[3:]  # Epic weapons
                
                self.enemies.append(enemy)
        
        # Place treasure chests (25% chance per room)
        if random.random() < 0.25:
            chest_x = random.randint(room.x1 + 1, room.x2 - 1)
            chest_y = random.randint(room.y1 + 1, room.y2 - 1)
            
            # Generate treasure chest contents
            chest_items = []
            num_items = random.randint(1, 3)
            
            for _ in range(num_items):
                item_type = random.random()
                if item_type < 0.4:  # 40% chance for weapon
                    available_weapons = self.get_available_weapons_for_players()
                    if available_weapons:
                        chosen_weapon = random.choice(available_weapons)
                        # Create a copy of the weapon to avoid reference issues
                        weapon_copy = Weapon(chosen_weapon.name, chosen_weapon.attack_bonus, 
                                           chosen_weapon.allowed_classes, chosen_weapon.rarity, 
                                           chosen_weapon.sprite_name)
                        chest_items.append(weapon_copy)
                elif item_type < 0.7:  # 30% chance for armor
                    available_armor = self.get_available_armor_for_players()
                    if available_armor:
                        chosen_armor = random.choice(available_armor)
                        # Create a copy of the armor to avoid reference issues
                        armor_copy = Armor(chosen_armor.name, chosen_armor.defense_bonus,
                                         chosen_armor.allowed_classes, chosen_armor.rarity,
                                         chosen_armor.sprite_name)
                        chest_items.append(armor_copy)
                else:  # 30% chance for potion
                    chosen_potion = random.choice(ALL_POTIONS)
                    # Create a copy of the potion to avoid reference issues
                    potion_copy = Potion(chosen_potion.name, chosen_potion.hp_gain, chosen_potion.rarity)
                    chest_items.append(potion_copy)
            
            treasure = Treasure(chest_x, chest_y, chest_items)
            self.treasures.append(treasure)
        
        # Place random items (reduced frequency due to chests)
        num_items = random.randint(0, 1)  # Reduced from 0-2
        for _ in range(num_items):
            x = random.randint(room.x1 + 1, room.x2 - 1)
            y = random.randint(room.y1 + 1, room.y2 - 1)
            if not any(i.x == x and i.y == y for i in self.items):
                item_choice = random.random()
                if item_choice < 0.6:  # Favor potions for ground loot
                    chosen_potion = random.choice(ALL_POTIONS)
                    item = Potion(chosen_potion.name, chosen_potion.hp_gain, chosen_potion.rarity)
                elif item_choice < 0.8:
                    available_weapons = self.get_available_weapons_for_players()
                    if available_weapons:
                        chosen_weapon = random.choice(available_weapons)
                        item = Weapon(chosen_weapon.name, chosen_weapon.attack_bonus,
                                    chosen_weapon.allowed_classes, chosen_weapon.rarity,
                                    chosen_weapon.sprite_name)
                    else:
                        chosen_potion = random.choice(ALL_POTIONS)
                        item = Potion(chosen_potion.name, chosen_potion.hp_gain, chosen_potion.rarity)
                else:
                    available_armor = self.get_available_armor_for_players()
                    if available_armor:
                        chosen_armor = random.choice(available_armor)
                        item = Armor(chosen_armor.name, chosen_armor.defense_bonus,
                                   chosen_armor.allowed_classes, chosen_armor.rarity,
                                   chosen_armor.sprite_name)
                    else:
                        chosen_potion = random.choice(ALL_POTIONS)
                        item = Potion(chosen_potion.name, chosen_potion.hp_gain, chosen_potion.rarity)
                
                item.x = x
                item.y = y
                self.items.append(item)
    
    def get_available_weapons_for_players(self):
        """Get weapons that can be used by the current players' classes."""
        # This will be set by the game when initializing the dungeon
        if not hasattr(self, 'player_classes'):
            return ALL_WEAPONS  # Default to all weapons
        
        available = []
        for weapon in ALL_WEAPONS:
            if any(cls in weapon.allowed_classes for cls in self.player_classes):
                # Check if this is single player and item hasn't been obtained
                if hasattr(self, 'is_single_player') and self.is_single_player:
                    if weapon.name not in self.obtained_items:
                        available.append(weapon)
                else:
                    available.append(weapon)
        return available
    
    def get_available_armor_for_players(self):
        """Get armor that can be used by the current players' classes."""
        if not hasattr(self, 'player_classes'):
            return ALL_ARMOR  # Default to all armor
        
        available = []
        for armor in ALL_ARMOR:
            if any(cls in armor.allowed_classes for cls in self.player_classes):
                # Check if this is single player and item hasn't been obtained
                if hasattr(self, 'is_single_player') and self.is_single_player:
                    if armor.name not in self.obtained_items:
                        available.append(armor)
                else:
                    available.append(armor)
        return available
    
    def mark_item_obtained(self, item_name):
        """Mark an item as obtained (for single player duplicate prevention)."""
        if hasattr(self, 'is_single_player') and self.is_single_player:
            self.obtained_items.add(item_name)
    
    def get_available_armor_for_players(self):
        """Get armor that can be used by the current players' classes."""
        if not hasattr(self, 'player_classes'):
            return ALL_ARMOR  # Default to all armor
        
        available = []
        for armor in ALL_ARMOR:
            if any(cls in armor.allowed_classes for cls in self.player_classes):
                available.append(armor)
        return available

    def get_room_at(self, x, y):
        """Get the room that contains the given coordinates."""
        for room in self.rooms:
            if room.x1 < x < room.x2 and room.y1 < y < room.y2:
                return room
        return None

    def update_visibility(self, player_x, player_y):
        """Update fog of war based on player position."""
        # Clear current visibility
        for y in range(self.height):
            for x in range(self.width):
                self.visible[y][x] = False
        
        # Get current room
        current_room = self.get_room_at(player_x, player_y)
        
        if current_room:
            # Make entire current room visible and explored
            for x in range(max(0, current_room.x1), min(self.width, current_room.x2 + 1)):
                for y in range(max(0, current_room.y1), min(self.height, current_room.y2 + 1)):
                    if 0 <= x < self.width and 0 <= y < self.height:
                        self.visible[y][x] = True
                        self.explored[y][x] = True
        
        # Also make a small radius around player visible (for corridors)
        vision_radius = 2
        for dy in range(-vision_radius, vision_radius + 1):
            for dx in range(-vision_radius, vision_radius + 1):
                x, y = player_x + dx, player_y + dy
                if 0 <= x < self.width and 0 <= y < self.height:
                    # Only if it's a floor tile (don't see through walls)
                    if self.grid[y][x] == UI["floor"] or self.grid[y][x] == UI["stairs"]:
                        self.visible[y][x] = True
                        self.explored[y][x] = True

    def is_visible(self, x, y):
        """Check if a position is currently visible."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.visible[y][x]
        return False

    def is_explored(self, x, y):
        """Check if a position has been explored before."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.explored[y][x]
        return False

# --- Game ---
class Game:
    def __init__(self):
        self.players = []
        self.dungeon = None
        self.current_player_idx = 0
        self.game_over = False
        self.game_won = False
        self.dungeon_level = 1
        self.messages = deque(maxlen=5)
        self.game_state = "main_menu"
        self.num_players = 0
        self.current_hero_setup = 1
        self.player_name = ""
        self.combat_enemies = []
        self.turn_order = []
        self.combat_turn_idx = 0
        # Camera system
        self.camera_x = 0
        self.camera_y = 0
        self.clock = pygame.time.Clock()  # For frame rate limiting
        # Inventory system
        self.inventory_state = "closed"  # closed, open, selecting
        self.selected_player_idx = 0
        self.selected_item_idx = 0
        # Item replacement system
        self.pending_replacement = None
    def draw_combat_screen(self):
        """Draw the enhanced combat screen with simple UI."""
        screen.fill(BLACK)  # Simple black background
        
        # Draw combat title
        title_surface = font.render("COMBAT", True, WHITE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(title_surface, title_rect)
        
        # Draw players section on the left
        player_section_x = 50
        player_section_y = 120
        self.draw_text("Your Party:", player_section_x, player_section_y, GREEN)
        
        for i, player in enumerate(self.players):
            y_pos = player_section_y + 40 + i * 80
            
            # Highlight current player's turn
            current_entity = self.turn_order[self.combat_turn_idx]
            is_current = player == current_entity
            color = YELLOW if is_current else WHITE
            
            # Player name and class
            if game_settings['use_emojis']:
                status = f'{player.icon} {player.name}'
            else:
                status = f'{player.name} ({player.char_class})'
            
            self.draw_text(status, player_section_x, y_pos, color)
            
            # Health bar
            hp_bar_width = 200
            hp_bar_height = 20
            hp_percentage = player.hp / player.max_hp
            
            # HP bar background
            hp_rect = pygame.Rect(player_section_x, y_pos + 25, hp_bar_width, hp_bar_height)
            pygame.draw.rect(screen, RED, hp_rect)
            pygame.draw.rect(screen, GREEN, (hp_rect.x, hp_rect.y, int(hp_bar_width * hp_percentage), hp_bar_height))
            pygame.draw.rect(screen, WHITE, hp_rect, 2)
            
            # HP text
            hp_text = f"HP: {player.hp}/{player.max_hp}"
            self.draw_text(hp_text, player_section_x + hp_bar_width + 10, y_pos + 25, color)
            
            # Mana for mages
            if player.char_class == "mage":
                mana_percentage = player.mana / player.max_mana
                mana_rect = pygame.Rect(player_section_x, y_pos + 50, hp_bar_width, hp_bar_height)
                pygame.draw.rect(screen, DARK_GRAY, mana_rect)
                pygame.draw.rect(screen, BLUE, (mana_rect.x, mana_rect.y, int(hp_bar_width * mana_percentage), hp_bar_height))
                pygame.draw.rect(screen, WHITE, mana_rect, 2)
                
                mana_text = f"Mana: {player.mana}/{player.max_mana}"
                self.draw_text(mana_text, player_section_x + hp_bar_width + 10, y_pos + 50, color)
            
            # Skill cooldown indicators
            if hasattr(player, 'skill_cooldown') and player.skill_cooldown > 0:
                cooldown_text = f"Cooldown: {player.skill_cooldown}"
                self.draw_text(cooldown_text, player_section_x + hp_bar_width + 150, y_pos + 25, RED)

        # Draw enemies section on the right
        enemy_section_x = SCREEN_WIDTH - 400
        enemy_section_y = 120
        self.draw_text("Enemies:", enemy_section_x, enemy_section_y, RED)
        
        for i, enemy in enumerate(self.combat_enemies):
            y_pos = enemy_section_y + 40 + i * 80
            
            # Highlight current enemy's turn
            current_entity = self.turn_order[self.combat_turn_idx]
            is_current = enemy == current_entity
            color = YELLOW if is_current else WHITE
            
            # Enemy name
            if game_settings['use_emojis']:
                status = f'{enemy.icon} {enemy.name}'
            else:
                status = f'{enemy.name}'
            
            self.draw_text(status, enemy_section_x, y_pos, color)
            
            # Enemy health bar
            hp_bar_width = 200
            hp_bar_height = 20
            hp_percentage = enemy.hp / enemy.max_hp
            
            hp_rect = pygame.Rect(enemy_section_x, y_pos + 25, hp_bar_width, hp_bar_height)
            pygame.draw.rect(screen, RED, hp_rect)
            pygame.draw.rect(screen, GREEN, (hp_rect.x, hp_rect.y, int(hp_bar_width * hp_percentage), hp_bar_height))
            pygame.draw.rect(screen, WHITE, hp_rect, 2)
            
            # HP text
            hp_text = f"HP: {enemy.hp}/{enemy.max_hp}"
            self.draw_text(hp_text, enemy_section_x + hp_bar_width + 10, y_pos + 25, color)

        # Draw action buttons at the bottom with simple UI
        current_entity = self.turn_order[self.combat_turn_idx]
        if isinstance(current_entity, Player):
            button_y = SCREEN_HEIGHT - 150
            button_width = 180
            button_height = 50
            button_spacing = (SCREEN_WIDTH - 5 * button_width) // 6
            
            # Button data: (text, key, available)
            buttons = [
                ("1. ATTACK", "1", True),
                ("2. SKILL", "2", self.is_skill_available(current_entity)),
                ("3. ITEM", "3", len([i for i in current_entity.inventory if isinstance(i, Potion)]) > 0),
                ("4. FLEE", "4", True),
                ("Q. QUIT", "Q", True)
            ]
            
            for i, (button_text, key, available) in enumerate(buttons):
                button_x = button_spacing + i * (button_width + button_spacing)
                
                # Choose button color and background
                if available:
                    button_color = WHITE
                    bg_color = (40, 40, 40)
                    border_color = WHITE
                else:
                    button_color = GRAY
                    bg_color = (20, 20, 20)
                    border_color = GRAY
                
                # Draw button background
                button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                pygame.draw.rect(screen, bg_color, button_rect)
                pygame.draw.rect(screen, border_color, button_rect, 3)
                
                # Draw button text
                button_surface = font.render(button_text, True, button_color)
                text_rect = button_surface.get_rect(center=button_rect.center)
                screen.blit(button_surface, text_rect)
            
            # Current player turn indicator
            turn_text = f"{current_entity.name}'s Turn"
            turn_surface = font.render(turn_text, True, YELLOW)
            turn_rect = turn_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 200))
            screen.blit(turn_surface, turn_rect)
        else:
            # Enemy turn
            turn_text = f"{current_entity.name} is attacking..."
            turn_surface = font.render(turn_text, True, RED)
            turn_rect = turn_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120))
            screen.blit(turn_surface, turn_rect)

        # Draw messages
        if self.messages:
            msg_y = SCREEN_HEIGHT - 250
            msg_surface = pygame.Surface((SCREEN_WIDTH, 80))
            msg_surface.set_alpha(200)
            msg_surface.fill(BLACK)
            screen.blit(msg_surface, (0, msg_y))
            
            for i, msg in enumerate(self.messages):
                if i < 3:  # Show only last 3 messages in combat
                    self.draw_text(msg, 50, msg_y + 10 + i * 25, WHITE)
                    
        pygame.display.flip()
    
    def is_skill_available(self, player):
        """Check if player's skill is available."""
        if player.char_class == "warrior" and player.skill_cooldown > 0:
            return False
        elif player.char_class == "mage" and player.mana < 10:
            return False
        elif player.char_class == "archer" and player.skill_cooldown > 0:
            return False
        return True
    
    def handle_inventory_input(self, key):
        """Handle input while inventory is open."""
        if key == pygame.K_ESCAPE or key == pygame.K_i:
            play_sound("menu_back", 0.5)
            self.inventory_state = "closed"
        elif key == pygame.K_q:  # Quit to main menu from inventory
            play_sound("menu_confirm", 0.5)
            self.inventory_state = "closed"
            self.save_game()
            play_music("menu")  # Return to menu music
            self.game_state = "main_menu"
            self.reset_game_state()
        elif key == pygame.K_LEFT and self.selected_player_idx > 0:
            play_sound("menu_select", 0.4)
            self.selected_player_idx -= 1
            self.selected_item_idx = 0
        elif key == pygame.K_RIGHT and self.selected_player_idx < len(self.players) - 1:
            play_sound("menu_select", 0.4)
            self.selected_player_idx += 1
            self.selected_item_idx = 0
        elif key == pygame.K_UP and self.selected_item_idx > 0:
            play_sound("menu_select", 0.3)
            self.selected_item_idx -= 1
        elif key == pygame.K_DOWN:
            current_player = self.players[self.selected_player_idx]
            displayed_items = self.get_displayed_inventory(current_player)
            if self.selected_item_idx < len(displayed_items) - 1:
                play_sound("menu_select", 0.3)
                self.selected_item_idx += 1
        elif key == pygame.K_RETURN:
            play_sound("menu_confirm", 0.5)
            self.use_inventory_item()
        elif key == pygame.K_DELETE or key == pygame.K_x:
            self.drop_inventory_item()
    
    def get_displayed_inventory(self, player):
        """Get items in the order they are displayed on screen."""
        weapons = [item for item in player.inventory if isinstance(item, Weapon)]
        armor_items = [item for item in player.inventory if isinstance(item, Armor)]
        potions = [item for item in player.inventory if isinstance(item, Potion)]
        return weapons + armor_items + potions
    
    def use_inventory_item(self):
        """Use the currently selected inventory item."""
        current_player = self.players[self.selected_player_idx]
        displayed_items = self.get_displayed_inventory(current_player)
        
        if self.selected_item_idx < len(displayed_items):
            item = displayed_items[self.selected_item_idx]
            
            if isinstance(item, Potion):
                if current_player.hp < current_player.max_hp:
                    result = item.use(current_player)
                    current_player.inventory.remove(item)
                    play_sound("pickup_bottle", 0.6)  # Potion use sound
                    self.add_message(result)
                    # Adjust selected index if needed
                    if self.selected_item_idx >= len(self.get_displayed_inventory(current_player)) and self.selected_item_idx > 0:
                        self.selected_item_idx -= 1
                else:
                    play_sound("error", 0.5)
                    self.add_message(f"{current_player.name} is already at full health!")
            elif isinstance(item, Weapon):
                # Check if player can use this weapon
                if not item.can_use(current_player.char_class):
                    play_sound("error", 0.5)
                    self.add_message(f"{current_player.name} cannot use {item.name}!")
                    return
                
                # Equip weapon
                if current_player.weapon != item:
                    old_weapon = current_player.weapon
                    current_player.weapon = item
                    play_sound("pickup_metal", 0.7)  # Weapon equip sound
                    self.add_message(f"{current_player.name} equipped {item.name}!")
                    # Put old weapon back in inventory if it's not already there and we have space
                    if old_weapon and old_weapon != item and old_weapon not in current_player.inventory:
                        # Check if we can add the old weapon back (this should usually be fine since we just freed a slot)
                        if current_player.can_carry_item(old_weapon):
                            current_player.inventory.append(old_weapon)
                        else:
                            # This shouldn't normally happen since we just equipped an item, but just in case
                            old_weapon.x = current_player.x
                            old_weapon.y = current_player.y
                            self.dungeon.items.append(old_weapon)
                            self.add_message(f"Old weapon {old_weapon.name} dropped on ground (inventory full).")
                else:
                    play_sound("error", 0.5)
                    self.add_message(f"{item.name} is already equipped!")
            elif isinstance(item, Armor):
                # Check if player can use this armor
                if not item.can_use(current_player.char_class):
                    play_sound("error", 0.5)
                    self.add_message(f"{current_player.name} cannot use {item.name}!")
                    return
                
                # Equip armor
                if current_player.armor != item:
                    old_armor = current_player.armor
                    current_player.armor = item
                    play_sound("equip_armor", 0.7)  # Armor equip sound
                    self.add_message(f"{current_player.name} equipped {item.name}!")
                    # Put old armor back in inventory if it's not already there and we have space
                    if old_armor and old_armor != item and old_armor not in current_player.inventory:
                        if current_player.can_carry_item(old_armor):
                            current_player.inventory.append(old_armor)
                        else:
                            # This shouldn't normally happen since we just equipped an item, but just in case
                            old_armor.x = current_player.x
                            old_armor.y = current_player.y
                            self.dungeon.items.append(old_armor)
                            self.add_message(f"Old armor {old_armor.name} dropped on ground (inventory full).")
                else:
                    play_sound("error", 0.5)
                    self.add_message(f"{item.name} is already equipped!")
    
    def drop_inventory_item(self):
        """Drop the currently selected inventory item."""
        current_player = self.players[self.selected_player_idx]
        displayed_items = self.get_displayed_inventory(current_player)
        
        if self.selected_item_idx < len(displayed_items):
            item = displayed_items[self.selected_item_idx]
            
            # Don't allow dropping equipped items
            if ((isinstance(item, Weapon) and item == current_player.weapon) or
                (isinstance(item, Armor) and item == current_player.armor)):
                play_sound("error", 0.5)
                self.add_message("Cannot drop equipped item!")
                return
            
            # Drop the item at player's location
            item.x = current_player.x
            item.y = current_player.y
            self.dungeon.items.append(item)
            current_player.inventory.remove(item)
            play_sound("drop_item", 0.6)  # Item drop sound
            self.add_message(f"{current_player.name} dropped {item.name}")
            
            # Adjust selected index if needed
            displayed_items_after = self.get_displayed_inventory(current_player)
            if self.selected_item_idx >= len(displayed_items_after) and self.selected_item_idx > 0:
                self.selected_item_idx -= 1
    
    def draw_inventory_screen(self):
        """Draw the enhanced inventory management screen with item categories."""
        screen.fill((20, 20, 40))  # Dark background
        
        # Title
        title_surface = font.render("INVENTORY", True, WHITE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(title_surface, title_rect)
        
        # Instructions
        instructions = [
            "← → : Switch Player",
            "↑ ↓ : Navigate Items", 
            "ENTER : Use/Equip Item",
            "X : Drop Item",
            "Q : Quit to Menu",
            "I/ESC : Close Inventory"
        ]
        
        for i, instruction in enumerate(instructions):
            text_surface = small_font.render(instruction, True, GRAY)
            screen.blit(text_surface, (50, 100 + i * 25))
        
        # Player tabs
        tab_width = 200
        tab_height = 40
        tab_y = 200
        tab_spacing = (SCREEN_WIDTH - len(self.players) * tab_width) // (len(self.players) + 1)
        
        for i, player in enumerate(self.players):
            tab_x = tab_spacing + i * (tab_width + tab_spacing)
            
            # Tab background
            is_selected = i == self.selected_player_idx
            tab_color = (60, 60, 100) if is_selected else (40, 40, 60)
            border_color = YELLOW if is_selected else WHITE
            
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width, tab_height)
            pygame.draw.rect(screen, tab_color, tab_rect)
            pygame.draw.rect(screen, border_color, tab_rect, 3)
            
            # Player name
            name_surface = font.render(player.name, True, WHITE)
            name_rect = name_surface.get_rect(center=tab_rect.center)
            screen.blit(name_surface, name_rect)
        
        # Current player's inventory
        current_player = self.players[self.selected_player_idx]
        inventory_y = 280
        
        # Player stats
        stats_text = f"Level {current_player.level} {current_player.char_class.title()}"
        stats_surface = font.render(stats_text, True, WHITE)
        screen.blit(stats_surface, (50, inventory_y))
        
        hp_text = f"HP: {current_player.hp}/{current_player.max_hp}"
        hp_surface = font.render(hp_text, True, GREEN if current_player.hp == current_player.max_hp else RED)
        screen.blit(hp_surface, (300, inventory_y))
        
        if current_player.char_class == "mage":
            mana_text = f"Mana: {current_player.mana}/{current_player.max_mana}"
            mana_surface = font.render(mana_text, True, BLUE)
            screen.blit(mana_surface, (500, inventory_y))
        
        # Equipped items
        equipped_y = inventory_y + 40
        self.draw_text("Equipped:", 50, equipped_y, YELLOW)
        
        weapon_text = f"Weapon: {current_player.weapon.name if current_player.weapon else 'None'}"
        weapon_color = GREEN if current_player.weapon else GRAY
        self.draw_text(weapon_text, 50, equipped_y + 30, weapon_color)
        
        armor_text = f"Armor: {current_player.armor.name if current_player.armor else 'None'}"
        armor_color = GREEN if current_player.armor else GRAY
        self.draw_text(armor_text, 50, equipped_y + 60, armor_color)
        
        # Categorized inventory items
        items_y = equipped_y + 120
        
        # Separate items by category
        weapons = [item for item in current_player.inventory if isinstance(item, Weapon)]
        armor_items = [item for item in current_player.inventory if isinstance(item, Armor)]
        potions = [item for item in current_player.inventory if isinstance(item, Potion)]
        
        current_y = items_y
        item_index = 0
        
        # Draw Weapons category
        if weapons:
            weapon_count_text = f"⚔️ WEAPONS ({len(weapons)}/{current_player.max_weapons}):"
            self.draw_text(weapon_count_text, 50, current_y, YELLOW)
            current_y += 35
            for item in weapons:
                self.draw_inventory_item(item, item_index, current_y, current_player)
                current_y += 30
                item_index += 1
            current_y += 10
        else:
            weapon_count_text = f"⚔️ WEAPONS (0/{current_player.max_weapons}): Empty"
            self.draw_text(weapon_count_text, 50, current_y, GRAY)
            current_y += 45
        
        # Draw Armor category
        if armor_items:
            armor_count_text = f"🛡️ ARMOR ({len(armor_items)}/{current_player.max_armor}):"
            self.draw_text(armor_count_text, 50, current_y, YELLOW)
            current_y += 35
            for item in armor_items:
                self.draw_inventory_item(item, item_index, current_y, current_player)
                current_y += 30
                item_index += 1
            current_y += 10
        else:
            armor_count_text = f"🛡️ ARMOR (0/{current_player.max_armor}): Empty"
            self.draw_text(armor_count_text, 50, current_y, GRAY)
            current_y += 45
        
        # Draw Consumables category
        if potions:
            potion_count_text = f"🧪 CONSUMABLES ({len(potions)}/{current_player.max_potions}):"
            self.draw_text(potion_count_text, 50, current_y, YELLOW)
            current_y += 35
            for item in potions:
                self.draw_inventory_item(item, item_index, current_y, current_player)
                current_y += 30
                item_index += 1
        else:
            potion_count_text = f"🧪 CONSUMABLES (0/{current_player.max_potions}): Empty"
            self.draw_text(potion_count_text, 50, current_y, GRAY)
            current_y += 45
        
        # Show inventory management instructions
        if current_y < SCREEN_HEIGHT - 100:
            self.draw_text("Inventory Limits: Weapons/Armor have limited slots", 50, current_y + 20, GRAY)
            self.draw_text("Better items will auto-replace when looting chests", 50, current_y + 40, GRAY)
        
        pygame.display.flip()
    
    def draw_inventory_item(self, item, item_index, y_pos, player):
        """Draw a single inventory item with proper highlighting and stats."""
        # Highlight selected item
        is_selected_item = item_index == self.selected_item_idx
        if is_selected_item:
            highlight_rect = pygame.Rect(45, y_pos - 5, SCREEN_WIDTH - 90, 28)
            pygame.draw.rect(screen, (60, 60, 100), highlight_rect)
            pygame.draw.rect(screen, YELLOW, highlight_rect, 2)
        
        # Item color based on equipment status and class compatibility
        item_color = WHITE
        if isinstance(item, Weapon):
            if item == player.weapon:
                item_color = GREEN  # Equipped weapon
            elif not item.can_use(player.char_class):
                item_color = DARK_GRAY  # Cannot use
        elif isinstance(item, Armor):
            if item == player.armor:
                item_color = GREEN  # Equipped armor
            elif not item.can_use(player.char_class):
                item_color = DARK_GRAY  # Cannot use
        
        # Draw item with rarity color border
        rarity_colors = {
            "common": WHITE,
            "uncommon": GREEN,
            "rare": BLUE,
            "epic": (128, 0, 128)  # Purple
        }
        
        if hasattr(item, 'rarity'):
            # Small colored square to indicate rarity
            rarity_color = rarity_colors.get(item.rarity, WHITE)
            pygame.draw.rect(screen, rarity_color, (50, y_pos + 5, 8, 8))
        
        # Item icon and name
        if game_settings['use_emojis']:
            item_text = f"{item.icon} {item.name}"
        else:
            item_text = f"• {item.name}"
        
        # Add item description
        if isinstance(item, Weapon):
            item_text += f" (Attack +{item.attack_bonus})"
            if not item.can_use(player.char_class):
                item_text += " [Unusable]"
        elif isinstance(item, Armor):
            item_text += f" (Defense +{item.defense_bonus})"
            if not item.can_use(player.char_class):
                item_text += " [Unusable]"
        elif isinstance(item, Potion):
            item_text += f" (Heals {item.hp_gain} HP)"
        
        self.draw_text(item_text, 70, y_pos, item_color)

    def add_message(self, text):
        self.messages.appendleft(text)
    
    def log_action(self, text):
        """Log action for debugging or history purposes."""
        print(f"LOG: {text}")
    
    def save_game(self):
        """Save the current game state."""
        try:
            save_data = {
                "players": [],
                "dungeon_level": self.dungeon_level,
                "current_player_idx": self.current_player_idx,
                "game_state": "playing",  # Always save as playing state
                "camera_x": self.camera_x,
                "camera_y": self.camera_y,
                "obtained_items": list(self.obtained_items) if hasattr(self, 'obtained_items') else []
            }
            
            # Save player data
            for player in self.players:
                player_data = {
                    "x": player.x,
                    "y": player.y,
                    "name": player.name,
                    "char_class": player.char_class,
                    "hp": player.hp,
                    "max_hp": player.max_hp,
                    "base_attack": player.base_attack,
                    "base_defense": player.base_defense,
                    "level": player.level,
                    "xp": player.xp,
                    "mana": player.mana,
                    "max_mana": player.max_mana,
                    "skill_cooldown": getattr(player, 'skill_cooldown', 0),
                    "inventory": [],
                    "weapon": None,
                    "armor": None
                }
                
                # Save inventory items
                for item in player.inventory:
                    item_data = {
                        "type": type(item).__name__,
                        "name": item.name,
                        "rarity": getattr(item, 'rarity', 'common')
                    }
                    
                    if isinstance(item, Weapon):
                        item_data.update({
                            "attack_bonus": item.attack_bonus,
                            "allowed_classes": item.allowed_classes,
                            "sprite_name": item.sprite_name
                        })
                    elif isinstance(item, Armor):
                        item_data.update({
                            "defense_bonus": item.defense_bonus,
                            "allowed_classes": item.allowed_classes,
                            "sprite_name": item.sprite_name
                        })
                    elif isinstance(item, Potion):
                        item_data["hp_gain"] = item.hp_gain
                    
                    player_data["inventory"].append(item_data)
                
                # Save equipped weapon
                if player.weapon:
                    weapon_data = {
                        "name": player.weapon.name,
                        "attack_bonus": player.weapon.attack_bonus,
                        "allowed_classes": player.weapon.allowed_classes,
                        "rarity": player.weapon.rarity,
                        "sprite_name": player.weapon.sprite_name
                    }
                    player_data["weapon"] = weapon_data
                
                # Save equipped armor
                if player.armor:
                    armor_data = {
                        "name": player.armor.name,
                        "defense_bonus": player.armor.defense_bonus,
                        "allowed_classes": player.armor.allowed_classes,
                        "rarity": player.armor.rarity,
                        "sprite_name": player.armor.sprite_name
                    }
                    player_data["armor"] = armor_data
                
                save_data["players"].append(player_data)
            
            # Save to file
            with open(SAVE_FILE, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            self.add_message("Game saved successfully!")
            return True
            
        except Exception as e:
            print(f"Error saving game: {e}")
            self.add_message("Error saving game!")
            return False
    
    def load_game(self):
        """Load a saved game state."""
        try:
            if not os.path.exists(SAVE_FILE):
                return False
            
            with open(SAVE_FILE, 'r') as f:
                save_data = json.load(f)
            
            # Clear current state
            self.players = []
            
            # Load players
            for player_data in save_data["players"]:
                # Create player
                player = Player(
                    player_data["x"],
                    player_data["y"],
                    player_data["name"],
                    player_data["char_class"]
                )
                
                # Restore player stats
                player.hp = player_data["hp"]
                player.max_hp = player_data["max_hp"]
                player.base_attack = player_data["base_attack"]
                player.base_defense = player_data["base_defense"]
                player.level = player_data["level"]
                player.xp = player_data["xp"]
                player.mana = player_data["mana"]
                player.max_mana = player_data["max_mana"]
                player.skill_cooldown = player_data.get("skill_cooldown", 0)
                
                # Clear starting inventory
                player.inventory = []
                player.weapon = None
                player.armor = None
                
                # Restore inventory
                for item_data in player_data["inventory"]:
                    item = self.create_item_from_data(item_data)
                    if item:
                        player.inventory.append(item)
                
                # Restore equipped weapon
                if player_data["weapon"]:
                    weapon_data = player_data["weapon"]
                    weapon = Weapon(
                        weapon_data["name"],
                        weapon_data["attack_bonus"],
                        weapon_data["allowed_classes"],
                        weapon_data["rarity"],
                        weapon_data["sprite_name"]
                    )
                    player.weapon = weapon
                
                # Restore equipped armor
                if player_data["armor"]:
                    armor_data = player_data["armor"]
                    armor = Armor(
                        armor_data["name"],
                        armor_data["defense_bonus"],
                        armor_data["allowed_classes"],
                        armor_data["rarity"],
                        armor_data["sprite_name"]
                    )
                    player.armor = armor
                
                self.players.append(player)
            
            # Restore game state
            self.dungeon_level = save_data["dungeon_level"]
            self.current_player_idx = save_data["current_player_idx"]
            self.camera_x = save_data.get("camera_x", 0)
            self.camera_y = save_data.get("camera_y", 0)
            
            # Restore obtained items for single player
            if "obtained_items" in save_data:
                self.obtained_items = set(save_data["obtained_items"])
            elif len(self.players) == 1:
                self.obtained_items = set()
            
            # Generate new level (we don't save dungeon layout for simplicity)
            self.new_level()
            
            # Set player classes for dungeon generation
            if self.dungeon:
                self.dungeon.player_classes = [p.char_class for p in self.players]
            
            return True
            
        except Exception as e:
            print(f"Error loading game: {e}")
            return False
    
    def create_item_from_data(self, item_data):
        """Create an item object from save data."""
        try:
            item_type = item_data["type"]
            name = item_data["name"]
            rarity = item_data.get("rarity", "common")
            
            if item_type == "Weapon":
                return Weapon(
                    name,
                    item_data["attack_bonus"],
                    item_data["allowed_classes"],
                    rarity,
                    item_data["sprite_name"]
                )
            elif item_type == "Armor":
                return Armor(
                    name,
                    item_data["defense_bonus"],
                    item_data["allowed_classes"],
                    rarity,
                    item_data["sprite_name"]
                )
            elif item_type == "Potion":
                return Potion(name, item_data["hp_gain"], rarity)
            
        except Exception as e:
            print(f"Error creating item from data: {e}")
        
        return None
    
    def has_save_file(self):
        """Check if a save file exists."""
        return os.path.exists(SAVE_FILE)
    
    def delete_save_file(self):
        """Delete the save file."""
        try:
            if os.path.exists(SAVE_FILE):
                os.remove(SAVE_FILE)
                return True
        except Exception as e:
            print(f"Error deleting save file: {e}")
        return False
    
    def reset_game_state(self):
        """Reset game state to initial values."""
        self.players = []
        self.dungeon = None
        self.current_player_idx = 0
        self.game_won = False
        self.dungeon_level = 1
        self.messages = deque(maxlen=5)
        self.num_players = 0
        self.current_hero_setup = 1
        self.player_name = ""
        self.combat_enemies = []
        self.turn_order = []
        self.combat_turn_idx = 0
        self.camera_x = 0
        self.camera_y = 0
        self.inventory_state = "closed"
        self.selected_player_idx = 0
        self.selected_item_idx = 0
        self.pending_replacement = None
        # Reset obtained items for single player
        if hasattr(self, 'obtained_items'):
            self.obtained_items = set()

    def update_camera(self):
        """Update camera position to follow the current player."""
        if self.players:
            player = self.players[0]  # Follow the first player
            # Center camera on player
            self.camera_x = player.x - VIEWPORT_WIDTH // 2
            self.camera_y = player.y - VIEWPORT_HEIGHT // 2
            
            # Keep camera within dungeon bounds
            self.camera_x = max(0, min(self.camera_x, self.dungeon.width - VIEWPORT_WIDTH))
            self.camera_y = max(0, min(self.camera_y, self.dungeon.height - VIEWPORT_HEIGHT))
            
            # Update fog of war for all players
            for p in self.players:
                self.dungeon.update_visibility(p.x, p.y)

    def draw_text(self, text, x, y, color=WHITE):
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (x, y))

    def main_menu(self):
        screen.fill(BLACK)
        
        # Title with better positioning
        title_y = SCREEN_HEIGHT // 2 - 150
        self.draw_text("Python RPG Adventure", SCREEN_WIDTH // 2 - 150, title_y)
        
        # Menu options with proper spacing
        menu_start_y = title_y + 80
        has_save = self.has_save_file()
        
        if has_save:
            self.draw_text("Press C to continue", SCREEN_WIDTH // 2 - 100, menu_start_y)
            self.draw_text("Press N for new game", SCREEN_WIDTH // 2 - 100, menu_start_y + 40)
            self.draw_text("Press D to delete save", SCREEN_WIDTH // 2 - 100, menu_start_y + 80)
            self.draw_text("Press S for settings", SCREEN_WIDTH // 2 - 100, menu_start_y + 120)
            self.draw_text("Press Q to quit", SCREEN_WIDTH // 2 - 80, menu_start_y + 160)
        else:
            self.draw_text("Press ENTER to start", SCREEN_WIDTH // 2 - 120, menu_start_y)
            self.draw_text("Press S for settings", SCREEN_WIDTH // 2 - 100, menu_start_y + 40)
            self.draw_text("Press Q to quit", SCREEN_WIDTH // 2 - 80, menu_start_y + 80)
        
        # Show current display mode
        mode_text = "Current mode: " + ("Emoji" if game_settings['use_emojis'] else "Sprite")
        self.draw_text(mode_text, SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT - 100, GRAY)
        
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and not has_save:
                    self.reset_game_state()
                    self.game_state = "setup_num_players"
                elif event.key == pygame.K_n:
                    self.reset_game_state()
                    self.game_state = "setup_num_players"
                elif event.key == pygame.K_c and has_save:
                    if self.load_game():
                        self.game_state = "playing"
                    else:
                        self.add_message("Failed to load save file!")
                elif event.key == pygame.K_d and has_save:
                    if self.delete_save_file():
                        self.add_message("Save file deleted!")
                elif event.key == pygame.K_s:
                    self.game_state = "settings_menu"
                elif event.key == pygame.K_q:
                    self.game_over = True

    def settings_menu(self):
        global game_settings
        screen.fill(BLACK)
        self.draw_text("Settings", SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 200)
        
        # Draw emoji setting with UI button sprite
        emoji_status = "ON" if game_settings['use_emojis'] else "OFF"
        button_x = SCREEN_WIDTH // 2 - 200
        button_y = SCREEN_HEIGHT // 2 - 150
        
        # Use different sprite based on setting state
        button_sprite = "tab_selected" if game_settings['use_emojis'] else "tab_unselected"
        if button_sprite in ui_elements:
            screen.blit(ui_elements[button_sprite], (button_x - 30, button_y - 5))
        
        self.draw_text(f"1. Use Emojis: {emoji_status}", button_x, button_y)
        
        # Only show sprite options if not using emojis
        if not game_settings['use_emojis']:
            # Show current wall selection with preview and UI button
            wall_name = game_settings['wall_sprite'].replace('.png', '').replace('_', ' ').title()
            wall_button_y = SCREEN_HEIGHT // 2 - 100
            
            if "tab_unselected" in ui_elements:
                screen.blit(ui_elements["tab_unselected"], (button_x - 30, wall_button_y - 5))
            
            self.draw_text(f"2. Wall Style: {wall_name}", button_x, wall_button_y)
            
            # Show wall preview
            sprite_key = f"wall_{game_settings['wall_sprite']}"
            if sprite_key in sprites:
                preview_sprite = pygame.transform.scale(sprites[sprite_key], (48, 48))
                screen.blit(preview_sprite, (SCREEN_WIDTH // 2 + 150, wall_button_y - 5))
            
            # Show current floor selection with preview and UI button
            floor_name = game_settings['floor_sprite'].replace('.png', '').replace('_', ' ').title()
            floor_button_y = SCREEN_HEIGHT // 2 - 50
            
            if "tab_unselected" in ui_elements:
                screen.blit(ui_elements["tab_unselected"], (button_x - 30, floor_button_y - 5))
            
            self.draw_text(f"3. Floor Style: {floor_name}", button_x, floor_button_y)
            
            # Show floor preview
            sprite_key = f"floor_{game_settings['floor_sprite']}"
            if sprite_key in sprites:
                preview_sprite = pygame.transform.scale(sprites[sprite_key], (48, 48))
                screen.blit(preview_sprite, (SCREEN_WIDTH // 2 + 150, floor_button_y - 5))
                
            # Show instruction for sprite mode
            self.draw_text("Use numbers 2-3 to change sprite styles", 
                          SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 20, GRAY)
        else:
            # Show emoji mode message
            self.draw_text("Emoji mode enabled - sprite options hidden", 
                          SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 80, GRAY)
        
        # Back button with UI sprite
        back_button_y = SCREEN_HEIGHT // 2 + 60
        if "tab_mouseover" in ui_elements:
            screen.blit(ui_elements["tab_mouseover"], (SCREEN_WIDTH // 2 - 130, back_button_y - 5))
        
        self.draw_text("Press ESC to go back", SCREEN_WIDTH // 2 - 100, back_button_y)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    game_settings['use_emojis'] = not game_settings['use_emojis']
                    save_settings(game_settings)
                elif event.key == pygame.K_2 and not game_settings['use_emojis']:
                    self.game_state = "wall_selection"
                elif event.key == pygame.K_3 and not game_settings['use_emojis']:
                    self.game_state = "floor_selection"
                elif event.key == pygame.K_ESCAPE:
                    self.game_state = "main_menu"

    def wall_selection(self):
        global game_settings
        screen.fill(BLACK)
        wall_options = ["stone_brick1.png", "stone_dark0.png", "brick_brown0.png", "marble_wall1.png"]
        wall_names = ["Stone Brick", "Stone Dark", "Brick Brown", "Marble Wall"]
        
        self.draw_text("Select Wall Style", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 150)
        
        # Display wall options with previews
        for i, (wall, name) in enumerate(zip(wall_options, wall_names)):
            y_pos = SCREEN_HEIGHT // 2 - 80 + i * 60
            marker = ">" if wall == game_settings['wall_sprite'] else " "
            
            # Draw the sprite preview
            sprite_key = f"wall_{wall}"
            if sprite_key in sprites:
                preview_size = 48  # Larger preview size
                preview_sprite = pygame.transform.scale(sprites[sprite_key], (preview_size, preview_size))
                screen.blit(preview_sprite, (SCREEN_WIDTH // 2 - 200, y_pos - 5))
            
            # Draw the option text
            self.draw_text(f"{marker} {i+1}. {name}", 
                          SCREEN_WIDTH // 2 - 140, y_pos + 10)
        
        self.draw_text("Press ESC to go back", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 120)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    idx = int(pygame.key.name(event.key)) - 1
                    if 0 <= idx < len(wall_options):
                        game_settings['wall_sprite'] = wall_options[idx]
                        save_settings(game_settings)
                elif event.key == pygame.K_ESCAPE:
                    self.game_state = "settings_menu"

    def floor_selection(self):
        global game_settings
        screen.fill(BLACK)
        floor_options = ["sandstone_floor0.png", "dirt0.png", "pebble_brown0.png", "marble_floor1.png"]
        floor_names = ["Sandstone Floor", "Dirt Floor", "Pebble Brown", "Marble Floor"]
        
        self.draw_text("Select Floor Style", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 150)
        
        # Display floor options with previews
        for i, (floor, name) in enumerate(zip(floor_options, floor_names)):
            y_pos = SCREEN_HEIGHT // 2 - 80 + i * 60
            marker = ">" if floor == game_settings['floor_sprite'] else " "
            
            # Draw the sprite preview
            sprite_key = f"floor_{floor}"
            if sprite_key in sprites:
                preview_size = 48  # Larger preview size
                preview_sprite = pygame.transform.scale(sprites[sprite_key], (preview_size, preview_size))
                screen.blit(preview_sprite, (SCREEN_WIDTH // 2 - 200, y_pos - 5))
            
            # Draw the option text
            self.draw_text(f"{marker} {i+1}. {name}", 
                          SCREEN_WIDTH // 2 - 140, y_pos + 10)
        
        self.draw_text("Press ESC to go back", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 120)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    idx = int(pygame.key.name(event.key)) - 1
                    if 0 <= idx < len(floor_options):
                        game_settings['floor_sprite'] = floor_options[idx]
                        save_settings(game_settings)
                elif event.key == pygame.K_ESCAPE:
                    self.game_state = "settings_menu"

    def setup_num_players(self):
        screen.fill(BLACK)
        title_y = SCREEN_HEIGHT // 2 - 80
        self.draw_text("Enter number of heroes (1-3):", SCREEN_WIDTH // 2 - 150, title_y)
        
        # Show current selection more prominently
        if self.num_players > 0:
            self.draw_text(str(self.num_players), SCREEN_WIDTH // 2 - 10, title_y + 50, GREEN)
        else:
            self.draw_text("_", SCREEN_WIDTH // 2 - 10, title_y + 50, GRAY)
            
        self.draw_text("Press ENTER to continue", SCREEN_WIDTH // 2 - 100, title_y + 100, GRAY)
        
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    self.num_players = int(pygame.key.name(event.key))
                if event.key == pygame.K_RETURN and self.num_players > 0:
                    self.game_state = "setup_player_name"

    def setup_player_name(self):
        screen.fill(BLACK)
        title_y = SCREEN_HEIGHT // 2 - 80
        self.draw_text(f"Enter name for hero {self.current_hero_setup}:", SCREEN_WIDTH // 2 - 150, title_y)
        
        # Show name input with cursor
        name_display = self.player_name + "_" if len(self.player_name) < 20 else self.player_name
        self.draw_text(name_display, SCREEN_WIDTH // 2 - 100, title_y + 50)
        
        if self.player_name:
            self.draw_text("Press ENTER to continue", SCREEN_WIDTH // 2 - 100, title_y + 100, GRAY)
        else:
            self.draw_text("Type a name for your hero", SCREEN_WIDTH // 2 - 100, title_y + 100, GRAY)
            
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self.player_name:
                    self.game_state = "setup_player_class"
                elif event.key == pygame.K_BACKSPACE:
                    self.player_name = self.player_name[:-1]
                elif len(self.player_name) < 15 and event.unicode.isprintable():
                    self.player_name += event.unicode

    def setup_player_class(self):
        screen.fill(BLACK)
        title_y = SCREEN_HEIGHT // 2 - 120
        self.draw_text(f"Choose class for {self.player_name}:", SCREEN_WIDTH // 2 - 150, title_y)
        
        # Show class options with descriptions
        class_info = {
            "warrior": ("High HP, strong attacks, Power Strike skill", "⚔️" if game_settings['use_emojis'] else "WAR"),
            "mage": ("Magic damage, area spells, Fireball skill", "🧙" if game_settings['use_emojis'] else "MAG"),
            "archer": ("Balanced stats, ranged attacks, Double Shot skill", "🏹" if game_settings['use_emojis'] else "ARC")
        }
        
        classes = ["warrior", "mage", "archer"]
        for i, class_name in enumerate(classes):
            y_pos = title_y + 60 + i * 60
            icon, desc = class_info[class_name]
            
            if game_settings['use_emojis']:
                class_text = f"{i+1}. {icon} {class_name.title()}"
            else:
                class_text = f"{i+1}. [{icon}] {class_name.title()}"
                
            self.draw_text(class_text, SCREEN_WIDTH // 2 - 200, y_pos)
            self.draw_text(desc, SCREEN_WIDTH // 2 - 190, y_pos + 25, GRAY)
        
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            if event.type == pygame.KEYDOWN:
                class_choice = None
                if event.key == pygame.K_1:
                    class_choice = "warrior"
                elif event.key == pygame.K_2:
                    class_choice = "mage"
                elif event.key == pygame.K_3:
                    class_choice = "archer"
                if class_choice:
                    self.players.append(Player(0, 0, self.player_name, class_choice))
                    self.player_name = ""
                    if self.current_hero_setup < self.num_players:
                        self.current_hero_setup += 1
                        self.game_state = "setup_player_name"
                    else:
                        self.new_level()
                        self.game_state = "playing"

    def new_level(self):
        self.dungeon = Dungeon(MAP_WIDTH, MAP_HEIGHT, self.dungeon_level)
        
        # Set player classes for item generation
        self.dungeon.player_classes = [player.char_class for player in self.players]
        
        # Set single player flag for duplicate prevention
        self.dungeon.is_single_player = len(self.players) == 1
        
        # Pass previously obtained items for single player
        if hasattr(self, 'obtained_items'):
            self.dungeon.obtained_items = self.obtained_items.copy()
        elif self.dungeon.is_single_player:
            # Initialize obtained items tracking for single player
            self.obtained_items = set()
            # Add starting equipment to obtained items
            for player in self.players:
                if player.weapon:
                    self.obtained_items.add(player.weapon.name)
                if player.armor:
                    self.obtained_items.add(player.armor.name)
            self.dungeon.obtained_items = self.obtained_items.copy()
        
        self.dungeon.generate()
        start_room = self.dungeon.rooms[0]
        for player in self.players:
            player.x, player.y = start_room.center()
        self.update_camera()  # Initialize camera and fog of war
        self.add_message(f"You have entered dungeon level {self.dungeon_level}.")

    def main_loop(self):
        # Start with menu music
        play_music("menu")

        while not self.game_over:
            # Limit frame rate to 60 FPS
            self.clock.tick(60)
            
            if self.game_state == "main_menu":
                # Ensure menu music is playing
                if current_music_state != "menu":
                    play_music("menu")
                self.main_menu()
            elif self.game_state == "settings_menu":
                # Keep menu music playing
                if current_music_state != "menu":
                    play_music("menu")
                self.settings_menu()
            elif self.game_state == "wall_selection":
                self.wall_selection()
            elif self.game_state == "floor_selection":
                self.floor_selection()
            elif self.game_state == "setup_num_players":
                self.setup_num_players()
            elif self.game_state == "setup_player_name":
                self.setup_player_name()
            elif self.game_state == "setup_player_class":
                self.setup_player_class()
            elif self.game_state == "playing":
                # Switch to gameplay music when playing
                if current_music_state != "gameplay":
                    play_music("gameplay")
                self.run_game()
            elif self.game_state == "combat":
                # Combat music is handled in start_combat method
                self.run_combat()
            elif self.game_state == "game_over":
                self.game_over_screen()
            elif self.game_state == "victory":
                self.victory_screen()

    def run_game(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            if event.type == pygame.KEYDOWN:
                self.handle_input(event.key)
        self.draw_game()

    def handle_input(self, key):
        if self.inventory_state == "open":
            self.handle_inventory_input(key)
        else:
            player = self.players[self.current_player_idx]
            if key == pygame.K_w:
                self.move_player(player, 'w')
            elif key == pygame.K_s:
                self.move_player(player, 's')
            elif key == pygame.K_a:
                self.move_player(player, 'a')
            elif key == pygame.K_d:
                self.move_player(player, 'd')
            elif key == pygame.K_e:  # Interact
                self.handle_interaction(player)
            elif key == pygame.K_i:  # Open inventory
                self.inventory_state = "open"
                self.selected_player_idx = 0
                self.selected_item_idx = 0
            elif key == pygame.K_q:  # Quit to main menu
                self.save_game()
                play_music("menu")  # Return to menu music
                self.game_state = "main_menu"
                self.reset_game_state()
            elif key == pygame.K_F5:  # Quick save
                self.save_game()
            elif key == pygame.K_r:  # Replace item
                self.handle_item_replacement()
            # Only cycle through players if there are any
            if len(self.players) > 0:
                self.current_player_idx = (self.current_player_idx + 1) % len(self.players)

    def handle_interaction(self, player):
        """Handle player interaction with objects."""
        # Check for treasure chest at player's position
        for treasure in self.dungeon.treasures:
            if treasure.x == player.x and treasure.y == player.y and not treasure.opened:
                self.open_treasure_chest(treasure, player)
                return
        
        # Check for items to pick up manually
        items_at_position = [item for item in self.dungeon.items if item.x == player.x and item.y == player.y]
        if items_at_position:
            item = items_at_position[0]
            success, message = player.try_add_item(item, auto_replace=False)  # Manual pickup - ask before replacing
            
            if success:
                self.dungeon.items.remove(item)
                self.add_message(f"{player.name} picked up {item.name}!")
                
                # Play appropriate pickup sound based on item type
                if isinstance(item, Weapon):
                    play_sound("pickup_metal", 0.7)
                elif isinstance(item, Armor):
                    play_sound("pickup_armor", 0.7)
                elif isinstance(item, Potion):
                    play_sound("pickup_bottle", 0.7)
                else:
                    play_sound("pickup_coin", 0.7)
                
                # Mark item as obtained for single player
                if hasattr(self, 'obtained_items') and len(self.players) == 1:
                    self.obtained_items.add(item.name)
                    self.dungeon.mark_item_obtained(item.name)
                    
                # Show replacement message if applicable
                if "Replaced" in message:
                    self.add_message(message)
            else:
                # Show why pickup failed and offer replacement option
                self.add_message(message)
                if player.should_replace_item(item):
                    worst_item = player.get_worst_item(type(item))
                    self.add_message(f"Press R to replace {worst_item.name} with {item.name}")
                    # Store the item for potential replacement (we'll handle 'R' key in input handling)
                    self.pending_replacement = {'item': item, 'player': player}
                    
            return
        
        self.add_message("Nothing to interact with here.")

    def handle_item_replacement(self):
        """Handle player pressing R to replace an item."""
        if not self.pending_replacement:
            self.add_message("No item replacement available.")
            return
            
        item = self.pending_replacement['item']
        player = self.pending_replacement['player']
        
        # Check if player is still at the same position as the item
        if not (player.x == item.x and player.y == item.y):
            self.add_message("You've moved away from the item.")
            self.pending_replacement = None
            return
        
        # Perform the replacement
        worst_item = player.get_worst_item(type(item))
        if worst_item:
            # Drop the worse item
            worst_item.x = player.x
            worst_item.y = player.y
            self.dungeon.items.append(worst_item)
            player.inventory.remove(worst_item)
            
            # Pick up the new item
            self.dungeon.items.remove(item)
            player.inventory.append(item)
            
            # Play sounds and show message
            play_sound("pickup_metal" if isinstance(item, Weapon) else 
                      "pickup_armor" if isinstance(item, Armor) else "pickup_bottle", 0.7)
            play_sound("drop_item", 0.5)
            
            self.add_message(f"Replaced {worst_item.name} with {item.name}!")
            
            # Mark item as obtained for single player
            if hasattr(self, 'obtained_items') and len(self.players) == 1:
                self.obtained_items.add(item.name)
                self.dungeon.mark_item_obtained(item.name)
                
            # Show inventory status
            item_type = type(item)
            current_count = len(player.get_inventory_by_type(item_type))
            max_count = player.get_max_for_type(item_type)
            item_type_name = item_type.__name__.lower() + "s"
            self.add_message(f"Inventory: {current_count}/{max_count} {item_type_name}")
        
        self.pending_replacement = None

    def open_treasure_chest(self, treasure, player):
        """Open a treasure chest and give items to player."""
        treasure.opened = True
        play_sound("door_open", 0.8)  # Chest opening sound
        self.add_message(f"{player.name} opened a treasure chest!")
        
        # Give all items from the treasure chest
        for item in treasure.items:
            success, message = player.try_add_item(item, auto_replace=True)
            
            if success:
                # Mark item as obtained for single player
                if hasattr(self, 'obtained_items') and len(self.players) == 1:
                    self.obtained_items.add(item.name)
                    self.dungeon.mark_item_obtained(item.name)
                
                # Play pickup sound and show message
                if isinstance(item, Weapon):
                    play_sound("pickup_metal", 0.6)
                    self.add_message(f"Found {item.name}! Attack +{item.attack_bonus}")
                elif isinstance(item, Armor):
                    play_sound("pickup_armor", 0.6)
                    self.add_message(f"Found {item.name}! Defense +{item.defense_bonus}")
                else:
                    play_sound("pickup_bottle", 0.6)
                    self.add_message(f"Found {item.name}!")
                
                # Show replacement message if applicable
                if "Replaced" in message:
                    self.add_message(message)
            else:
                # Drop item on ground if inventory full or not good enough
                item.x = treasure.x
                item.y = treasure.y
                self.dungeon.items.append(item)
                play_sound("drop_item", 0.5)
                self.add_message(f"{item.name} dropped on ground. {message}")
                
        # Show inventory status after looting
        weapons = len(player.get_inventory_by_type(Weapon))
        armor = len(player.get_inventory_by_type(Armor))
        potions = len(player.get_inventory_by_type(Potion))
        self.add_message(f"Inventory: {weapons}/{player.max_weapons} weapons, {armor}/{player.max_armor} armor, {potions}/{player.max_potions} potions")

    def move_player(self, player, direction):
        dx, dy = 0, 0
        if direction == 'w': dy = -1
        if direction == 's': dy = 1
        if direction == 'a': dx = -1
        if direction == 'd': dx = 1

        new_x, new_y = player.x + dx, player.y + dy

        if not (0 <= new_x < self.dungeon.width and 0 <= new_y < self.dungeon.height):
            self.add_message("You can't move off the map.")
            return

        if self.dungeon.grid[new_y][new_x] == UI["stairs"]:
            self.dungeon_level += 1
            self.new_level()
            return

        if self.dungeon.grid[new_y][new_x] == UI["floor"]:
            enemies_in_pos = [e for e in self.dungeon.enemies if e.x == new_x and e.y == new_y]
            if enemies_in_pos:
                self.start_combat(enemies_in_pos)
            else:
                # Move player
                player.x, player.y = new_x, new_y
                self.update_camera()  # Update camera after movement
                for item in list(self.dungeon.items):
                    if item.x == new_x and item.y == new_y:
                        success, message = player.try_add_item(item, auto_replace=True)
                        if success:
                            self.dungeon.items.remove(item)
                            self.add_message(f"{player.name} picked up {item.name}.")
                            
                            # Play appropriate pickup sound based on item type
                            if isinstance(item, Weapon):
                                play_sound("pickup_metal", 0.7)
                            elif isinstance(item, Armor):
                                play_sound("pickup_armor", 0.7)
                            elif isinstance(item, Potion):
                                play_sound("pickup_bottle", 0.7)
                            else:
                                play_sound("pickup_coin", 0.7)
                                
                            # Mark item as obtained for single player
                            if hasattr(self, 'obtained_items') and len(self.players) == 1:
                                self.obtained_items.add(item.name)
                                self.dungeon.mark_item_obtained(item.name)
                                
                            # Show replacement message if applicable
                            if "Replaced" in message:
                                self.add_message(message)
                        else:
                            # Item couldn't be picked up automatically
                            self.add_message(f"Can't pick up {item.name}: {message}")
                            # Show hint about manual interaction
                            if player.should_replace_item(item):
                                self.add_message("Press E to interact and choose replacement.")
        else:
            self.add_message("You can't move there.")

    def draw_game(self):
        if self.inventory_state == "open":
            self.draw_inventory_screen()
        else:
            self.draw_main_game()
    
    def draw_main_game(self):
        screen.fill(BLACK)
        
        # Check if dungeon exists before drawing
        if not self.dungeon:
            # Show loading or waiting message
            loading_text = font.render("Setting up dungeon...", True, WHITE)
            text_rect = loading_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(loading_text, text_rect)
            pygame.display.flip()
            return
        
        # Draw main viewport with camera offset
        viewport_start_x = max(0, self.camera_x)
        viewport_start_y = max(0, self.camera_y)
        viewport_end_x = min(self.dungeon.width, self.camera_x + VIEWPORT_WIDTH)
        viewport_end_y = min(self.dungeon.height, self.camera_y + VIEWPORT_HEIGHT)
        
        # Draw map tiles in viewport
        for world_y in range(viewport_start_y, viewport_end_y):
            for world_x in range(viewport_start_x, viewport_end_x):
                screen_x = (world_x - self.camera_x) * TILE_SIZE
                screen_y = (world_y - self.camera_y) * TILE_SIZE
                
                tile_type = self.dungeon.grid[world_y][world_x]
                is_visible = self.dungeon.is_visible(world_x, world_y)
                is_explored = self.dungeon.is_explored(world_x, world_y)
                
                if is_explored:
                    if game_settings['use_emojis']:
                        # Use emojis
                        color = WHITE if is_visible else GRAY
                        text = font.render(tile_type, True, color)
                        screen.blit(text, (screen_x, screen_y))
                    else:
                        # Use sprites with fallback
                        sprite_drawn = False
                        if tile_type == UI["wall"]:
                            sprite_key = f"wall_{game_settings['wall_sprite']}"
                            if sprite_key in sprites:
                                sprite = sprites[sprite_key].copy()
                                if not is_visible:
                                    sprite.set_alpha(128)  # Make dimmer if not visible
                                screen.blit(sprite, (screen_x, screen_y))
                                sprite_drawn = True
                        elif tile_type == UI["floor"]:
                            sprite_key = f"floor_{game_settings['floor_sprite']}"
                            if sprite_key in sprites:
                                sprite = sprites[sprite_key].copy()
                                if not is_visible:
                                    sprite.set_alpha(128)  # Make dimmer if not visible
                                screen.blit(sprite, (screen_x, screen_y))
                                sprite_drawn = True
                        elif tile_type == UI["stairs"]:
                            if "stairs" in sprites:
                                sprite = sprites["stairs"].copy()
                                if not is_visible:
                                    sprite.set_alpha(128)  # Make dimmer if not visible
                                screen.blit(sprite, (screen_x, screen_y))
                                sprite_drawn = True
                        
                        # Fallback to colored rectangles if sprite not available
                        if not sprite_drawn:
                            color = WHITE if is_visible else DARK_GRAY
                            if tile_type == UI["wall"]:
                                pygame.draw.rect(screen, GRAY if is_visible else DARK_GRAY, 
                                               (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                            elif tile_type == UI["floor"]:
                                pygame.draw.rect(screen, (101, 67, 33) if is_visible else (50, 33, 16), 
                                               (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                            elif tile_type == UI["stairs"]:
                                pygame.draw.rect(screen, (255, 255, 0) if is_visible else (128, 128, 0), 
                                               (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                else:
                    # Unexplored areas - draw fog
                    pygame.draw.rect(screen, FOG_COLOR, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))

        # Draw items (only if visible)
        for item in self.dungeon.items:
            if (viewport_start_x <= item.x < viewport_end_x and 
                viewport_start_y <= item.y < viewport_end_y and
                self.dungeon.is_visible(item.x, item.y)):
                
                screen_x = (item.x - self.camera_x) * TILE_SIZE
                screen_y = (item.y - self.camera_y) * TILE_SIZE
                
                if game_settings['use_emojis']:
                    text = font.render(item.icon, True, WHITE)
                    screen.blit(text, (screen_x, screen_y))
                else:
                    # Use specific item sprites when available
                    sprite_drawn = False
                    
                    # Try to use the specific sprite for this item
                    if hasattr(item, 'sprite_name') and item.sprite_name:
                        # Try the sprite_name directly first
                        if item.sprite_name in sprites:
                            screen.blit(sprites[item.sprite_name], (screen_x, screen_y))
                            sprite_drawn = True
                        else:
                            # Try with weapon_ prefix for weapons
                            if isinstance(item, Weapon):
                                weapon_key = f"weapon_{item.sprite_name}"
                                if weapon_key in sprites:
                                    screen.blit(sprites[weapon_key], (screen_x, screen_y))
                                    sprite_drawn = True
                            # Try with armor_ prefix for armor
                            elif isinstance(item, Armor):
                                armor_key = f"armor_{item.sprite_name}"
                                if armor_key in sprites:
                                    screen.blit(sprites[armor_key], (screen_x, screen_y))
                                    sprite_drawn = True
                    
                    # Fallback to generic sprites if specific sprite not found
                    if not sprite_drawn:
                        if isinstance(item, Potion) and "item_potion" in sprites:
                            screen.blit(sprites["item_potion"], (screen_x, screen_y))
                            sprite_drawn = True
                        elif isinstance(item, Weapon) and "item_weapon" in sprites:
                            screen.blit(sprites["item_weapon"], (screen_x, screen_y))
                            sprite_drawn = True
                        elif isinstance(item, Armor) and "item_armor" in sprites:
                            screen.blit(sprites["item_armor"], (screen_x, screen_y))
                            sprite_drawn = True
                    
                    # If still no sprite found, show a simple text representation
                    if not sprite_drawn:
                        # Display item name as text instead of colored rectangles
                        item_text = item.name[:3].upper()  # First 3 letters of item name
                        text_surface = small_font.render(item_text, True, WHITE)
                        # Center the text in the tile
                        text_rect = text_surface.get_rect(center=(screen_x + TILE_SIZE//2, screen_y + TILE_SIZE//2))
                        # Draw a small background for visibility
                        bg_rect = pygame.Rect(screen_x + 4, screen_y + 4, TILE_SIZE - 8, TILE_SIZE - 8)
                        pygame.draw.rect(screen, (60, 60, 60), bg_rect)
                        pygame.draw.rect(screen, WHITE, bg_rect, 1)
                        screen.blit(text_surface, text_rect)
                
        # Draw treasure chests (only if visible)
        for treasure in self.dungeon.treasures:
            if (viewport_start_x <= treasure.x < viewport_end_x and 
                viewport_start_y <= treasure.y < viewport_end_y and
                self.dungeon.is_visible(treasure.x, treasure.y)):
                
                screen_x = (treasure.x - self.camera_x) * TILE_SIZE
                screen_y = (treasure.y - self.camera_y) * TILE_SIZE
                
                if game_settings['use_emojis']:
                    chest_icon = "📦" if not treasure.opened else "📭"
                    text = font.render(chest_icon, True, (218, 165, 32))  # Gold color
                    screen.blit(text, (screen_x, screen_y))
                else:
                    # Use chest sprites when available
                    sprite_drawn = False
                    sprite_key = "chest_closed" if not treasure.opened else "chest_open"
                    if sprite_key in sprites:
                        screen.blit(sprites[sprite_key], (screen_x, screen_y))
                        sprite_drawn = True
                    
                    # Fallback to colored rectangle
                    if not sprite_drawn:
                        chest_color = (218, 165, 32) if not treasure.opened else (139, 115, 85)  # Gold or brown
                        pygame.draw.rect(screen, chest_color, (screen_x + 2, screen_y + 2, TILE_SIZE - 4, TILE_SIZE - 4))
                
        # Draw enemies (only if visible)
        for enemy in self.dungeon.enemies:
            if (viewport_start_x <= enemy.x < viewport_end_x and 
                viewport_start_y <= enemy.y < viewport_end_y and
                self.dungeon.is_visible(enemy.x, enemy.y)):
                
                screen_x = (enemy.x - self.camera_x) * TILE_SIZE
                screen_y = (enemy.y - self.camera_y) * TILE_SIZE
                
                if game_settings['use_emojis']:
                    text = font.render(enemy.icon, True, RED)
                    screen.blit(text, (screen_x, screen_y))
                else:
                    # Use static sprites
                    sprite_drawn = False
                    
                    # Use static enemy sprites
                    enemy_type = enemy.name.lower()
                    sprite_key = f"monster_{enemy_type}"
                    if sprite_key in sprites:
                        screen.blit(sprites[sprite_key], (screen_x, screen_y))
                        sprite_drawn = True
                    
                    # Final fallback to colored rectangle if sprite not available
                    if not sprite_drawn:
                        pygame.draw.rect(screen, RED, (screen_x + 2, screen_y + 2, TILE_SIZE - 4, TILE_SIZE - 4))
                
        # Draw players
        for player in self.players:
            if (viewport_start_x <= player.x < viewport_end_x and 
                viewport_start_y <= player.y < viewport_end_y):
                
                screen_x = (player.x - self.camera_x) * TILE_SIZE
                screen_y = (player.y - self.camera_y) * TILE_SIZE
                
                if game_settings['use_emojis']:
                    text = font.render(player.icon, True, GREEN)
                    screen.blit(text, (screen_x, screen_y))
                else:
                    # Use static sprites
                    sprite_drawn = False
                    
                    # Use static player sprites
                    sprite_key = f"player_{player.char_class}"
                    if sprite_key in sprites:
                        screen.blit(sprites[sprite_key], (screen_x, screen_y))
                        sprite_drawn = True
                    
                    # Final fallback to colored rectangle
                    if not sprite_drawn:
                        pygame.draw.rect(screen, GREEN, (screen_x + 6, screen_y + 6, TILE_SIZE - 12, TILE_SIZE - 12))

        # Draw minimap
        self.draw_minimap()
        
        # Draw UI
        self.draw_ui()
        pygame.display.flip()

    def draw_minimap(self):
        """Draw a small overview map in the top right corner."""
        minimap_x = SCREEN_WIDTH - MINIMAP_SIZE - 10
        minimap_y = 10
        
        # Draw minimap background
        minimap_surface = pygame.Surface((MINIMAP_SIZE, MINIMAP_SIZE))
        minimap_surface.fill(BLACK)
        
        # Calculate scale
        scale_x = MINIMAP_SIZE / self.dungeon.width
        scale_y = MINIMAP_SIZE / self.dungeon.height
        scale = min(scale_x, scale_y)
        
        # Draw explored areas
        for y in range(self.dungeon.height):
            for x in range(self.dungeon.width):
                if self.dungeon.is_explored(x, y):
                    pixel_x = int(x * scale)
                    pixel_y = int(y * scale)
                    pixel_size = max(1, int(scale))
                    
                    tile_type = self.dungeon.grid[y][x]
                    is_visible = self.dungeon.is_visible(x, y)
                    
                    # Choose color based on tile type and visibility
                    if tile_type == UI["wall"]:
                        color = GRAY if is_visible else DARK_GRAY
                    elif tile_type == UI["floor"]:
                        color = LIGHT_GRAY if is_visible else GRAY
                    elif tile_type == UI["stairs"]:
                        color = (255, 255, 0) if is_visible else (128, 128, 0)
                    else:
                        color = DARK_GRAY
                    
                    pygame.draw.rect(minimap_surface, color, 
                                   (pixel_x, pixel_y, pixel_size, pixel_size))
        
        # Draw players on minimap
        for player in self.players:
            pixel_x = int(player.x * scale)
            pixel_y = int(player.y * scale)
            pixel_size = max(2, int(scale * 1.5))
            pygame.draw.rect(minimap_surface, GREEN, 
                           (pixel_x - pixel_size//2, pixel_y - pixel_size//2, 
                            pixel_size, pixel_size))
        
        # Draw visible enemies on minimap
        for enemy in self.dungeon.enemies:
            if self.dungeon.is_visible(enemy.x, enemy.y):
                pixel_x = int(enemy.x * scale)
                pixel_y = int(enemy.y * scale)
                pixel_size = max(1, int(scale))
                pygame.draw.rect(minimap_surface, RED, 
                               (pixel_x, pixel_y, pixel_size, pixel_size))
        
        # Draw minimap border
        pygame.draw.rect(minimap_surface, WHITE, (0, 0, MINIMAP_SIZE, MINIMAP_SIZE), 2)
        
        # Blit minimap to screen
        screen.blit(minimap_surface, (minimap_x, minimap_y))
        
        # Draw minimap title
        minimap_text = small_font.render("Map", True, WHITE)
        screen.blit(minimap_text, (minimap_x, minimap_y - 20))

    def draw_ui(self):
        # Create a semi-transparent background for UI elements
        ui_surface = pygame.Surface((SCREEN_WIDTH - MINIMAP_SIZE - 30, 150))  # Leave space for minimap
        ui_surface.set_alpha(200)
        ui_surface.fill(BLACK)
        screen.blit(ui_surface, (0, 0))
        
        # Draw player status with better spacing
        y = 15
        for i, p in enumerate(self.players):
            # Use conditional icons based on emoji setting
            if game_settings['use_emojis']:
                status_text = f'{p.icon} {p.name} ({p.char_class}) | {UI["level"]} {p.level} | {UI["hp"]} {p.hp}/{p.max_hp}'
            else:
                # Use text-based display when sprites are enabled
                status_text = f'{p.name} ({p.char_class}) | Level {p.level} | HP {p.hp}/{p.max_hp}'
                
            # Add mana display for mage characters
            if p.char_class == "mage":
                if game_settings['use_emojis']:
                    status_text += f' | {UI["mana"]} {p.mana}/{p.max_mana}'
                else:
                    status_text += f' | Mana {p.mana}/{p.max_mana}'
                    
            self.draw_text(status_text, 15, y, WHITE)
            y += 35

        # Draw messages with background (positioned to not overlap with minimap)
        if self.messages:
            msg_surface = pygame.Surface((SCREEN_WIDTH - MINIMAP_SIZE - 30, 120))
            msg_surface.set_alpha(180)
            msg_surface.fill(BLACK)
            screen.blit(msg_surface, (0, SCREEN_HEIGHT - 120))
            
            y = SCREEN_HEIGHT - 110
            for i, msg in enumerate(self.messages):
                if i < 4:  # Limit to 4 messages to prevent overlap
                    self.draw_text(msg, 15, y - i * 25, WHITE)
        
        # Draw current dungeon level and inventory status
        level_text = f"Dungeon Level: {self.dungeon_level}"
        self.draw_text(level_text, 15, 155, LIGHT_GRAY)
        
        # Show inventory status for current player
        if self.players:
            current_player = self.players[self.current_player_idx]
            weapons = len(current_player.get_inventory_by_type(Weapon))
            armor = len(current_player.get_inventory_by_type(Armor))
            potions = len(current_player.get_inventory_by_type(Potion))
            inventory_text = f"Inventory: {weapons}/{current_player.max_weapons}⚔️ {armor}/{current_player.max_armor}🛡️ {potions}/{current_player.max_potions}🧪"
            self.draw_text(inventory_text, 15, 175, LIGHT_GRAY)
        
        # Draw controls hint
        controls_text = "Controls: WASD=Move, E=Interact, R=Replace, I=Inventory, Q=Menu"
        self.draw_text(controls_text, 15, 200, GRAY)


    def start_combat(self, enemies):
        """Start turn-based combat with enhanced UI."""
        self.game_state = "combat"
        self.combat_enemies = enemies
        self.turn_order = self.players + self.combat_enemies
        random.shuffle(self.turn_order)
        self.combat_turn_idx = 0
        self.add_message("You've entered combat!")
        
        # Play appropriate combat music based on enemy types
        combat_music = get_combat_music_for_enemies(enemies)
        play_music(combat_music)

    def run_combat(self):
        """Run the enhanced turn-based combat system."""
        # Draw the combat screen
        self.draw_combat_screen()
        
        # Get current entity
        entity = self.turn_order[self.combat_turn_idx]
        
        if isinstance(entity, Player):
            # Player turn - handle input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.player_attack()
                    elif event.key == pygame.K_2:
                        self.use_skill(entity, self.combat_enemies)
                    elif event.key == pygame.K_3:
                        self.show_inventory(entity)
                    elif event.key == pygame.K_4:
                        self.try_flee()
                    elif event.key == pygame.K_q:  # Quit to main menu during combat
                        self.save_game()
                        self.game_state = "main_menu"
                        self.reset_game_state()
        else:
            # Enemy turn
            pygame.time.wait(500)  # Pause for half a second to show enemy turn
            self.enemy_attack(entity)
        
        # Check battle end conditions
        if not any(p.is_alive() for p in self.players):
            play_sound("error", 0.7)  # Defeat sound
            self.add_message("Your party has been defeated. Game Over.")
            stop_music()  # Stop music on game over
            self.game_state = "game_over"
        elif not any(e.is_alive() for e in self.combat_enemies):
            play_sound("success", 0.8)  # Victory sound
            self.add_message("You won the battle!")
            
            # Check if dragon was defeated (victory condition)
            dragon_defeated = any(enemy.enemy_type == "dragon" for enemy in self.combat_enemies)
            
            # Handle enemy weapon drops before removing enemies
            for enemy in self.combat_enemies:
                if hasattr(enemy, 'weapon_drops') and enemy.weapon_drops and random.random() < 0.3:  # 30% drop chance
                    # Filter available drops for single player to prevent duplicates
                    available_drops = enemy.weapon_drops
                    if hasattr(self, 'obtained_items') and len(self.players) == 1:
                        available_drops = [item for item in enemy.weapon_drops if item.name not in self.obtained_items]
                    
                    if available_drops:  # Only drop if there are available items
                        chosen_drop = random.choice(available_drops)
                        # Create a copy to avoid reference issues
                        if isinstance(chosen_drop, Weapon):
                            dropped_item = Weapon(chosen_drop.name, chosen_drop.attack_bonus,
                                                chosen_drop.allowed_classes, chosen_drop.rarity,
                                                chosen_drop.sprite_name)
                        elif isinstance(chosen_drop, Armor):
                            dropped_item = Armor(chosen_drop.name, chosen_drop.defense_bonus,
                                               chosen_drop.allowed_classes, chosen_drop.rarity,
                                               chosen_drop.sprite_name)
                        else:
                            dropped_item = chosen_drop
                        
                        dropped_item.x = enemy.x
                        dropped_item.y = enemy.y
                        self.dungeon.items.append(dropped_item)
                        self.add_message(f"{enemy.name} dropped a {dropped_item.name}!")
            
            # Check for victory condition
            if dragon_defeated:
                self.add_message("The dragon has been slain! You are victorious!")
                stop_music()  # Stop current music
                self.game_won = True
                self.game_state = "victory"
            else:
                # Return to gameplay music after combat
                play_music("gameplay")
                self.game_state = "playing"
                
            # Award XP to players
            total_xp = sum(e.xp for e in self.combat_enemies)
            xp_per_player = total_xp // len(self.players) if self.players else 0
            for p in self.players:
                if p.is_alive():
                    msg = p.gain_xp(xp_per_player)
                    if msg: 
                        self.add_message(msg)
            # Remove defeated enemies from dungeon
            self.dungeon.enemies = [e for e in self.dungeon.enemies if e not in self.combat_enemies]
    
    def player_attack(self):
        """Handle player basic attack."""
        player = self.turn_order[self.combat_turn_idx]
        alive_enemies = [e for e in self.combat_enemies if e.is_alive()]
        if alive_enemies:
            # Play attack animation
            if hasattr(player, 'start_animation'):
                player.start_animation("attack", ATTACK_SPEED)
            
            # Play attack sound based on player class
            play_random_sound(["sword_attack", "sword_attack2", "sword_attack3"], 0.6)
            target = random.choice(alive_enemies)
            damage = max(0, player.attack - target.defense)
            target.take_damage(damage)
            self.add_message(f"{player.name} hits {target.name} for {damage} damage.")
        self.next_turn()

    def enemy_attack(self, enemy):
        """Handle enemy attack."""
        alive_players = [p for p in self.players if p.is_alive()]
        if alive_players:
            # Play attack animation for enemy
            if hasattr(enemy, 'attack_animation'):
                enemy.attack_animation()
            
            # Play random enemy attack sound
            play_sound("orc_attack", 0.5)  # Generic enemy attack sound
            target = random.choice(alive_players)
            damage = max(0, enemy.attack - target.defense)
            target.take_damage(damage)
            self.add_message(f"{enemy.name} hits {target.name} for {damage} damage.")
        self.next_turn()

    def next_turn(self):
        """Move to the next entity's turn."""
        self.combat_turn_idx = (self.combat_turn_idx + 1) % len(self.turn_order)
        
        # Reduce skill cooldowns for players at the start of their turn
        current_entity = self.turn_order[self.combat_turn_idx]
        if isinstance(current_entity, Player) and hasattr(current_entity, 'skill_cooldown'):
            if current_entity.skill_cooldown > 0:
                current_entity.skill_cooldown -= 1
        
        # Skip turns for dead entities
        while not self.turn_order[self.combat_turn_idx].is_alive():
            self.combat_turn_idx = (self.combat_turn_idx + 1) % len(self.turn_order)

    def use_skill(self, player, enemies):
        """Use player's special skill."""
        # Check if there are any alive enemies before using skills
        alive_enemies = [e for e in enemies if e.is_alive()]
        if not alive_enemies:
            self.add_message("No enemies to target!")
            return
            
        if player.char_class == "warrior":
            if player.skill_cooldown > 0:
                self.add_message(f"Power Strike is on cooldown for {player.skill_cooldown} more turns.")
                return
            play_sound("sword_draw", 0.7)
            target = random.choice(alive_enemies)
            damage = player.attack * 2
            target.take_damage(damage)
            self.add_message(f"{player.name} uses Power Strike on {target.name} for {damage} damage!")
            player.skill_cooldown = 3
        elif player.char_class == "mage":
            if player.mana < 10:
                self.add_message("Not enough mana for Fireball.")
                return
            play_sound("magic_spell", 0.7)
            self.add_message(f"{player.name} casts Fireball!")
            for enemy in alive_enemies:
                damage = player.attack // 2
                enemy.take_damage(damage)
                self.add_message(f"Fireball hits {enemy.name} for {damage} damage.")
            player.mana -= 10
        elif player.char_class == "archer":
            if player.skill_cooldown > 0:
                self.add_message(f"Double Shot is on cooldown for {player.skill_cooldown} more turns.")
                return
            play_random_sound(["sword_attack", "sword_attack2"], 0.5)
            self.add_message(f"{player.name} uses Double Shot!")
            for _ in range(2):
                if alive_enemies:  # Check if there are still alive enemies for each shot
                    target = random.choice(alive_enemies)
                    damage = player.attack
                    target.take_damage(damage)
                    self.add_message(f"{player.name} shoots {target.name} for {damage} damage.")
                    # Update alive enemies list in case the target died
                    alive_enemies = [e for e in enemies if e.is_alive()]
            player.skill_cooldown = 2
        self.next_turn()
    
    def show_inventory(self, player):
        """Show and use items from inventory."""
        potions = [item for item in player.inventory if isinstance(item, Potion)]
        if potions:
            # Use the first available potion
            potion = potions[0]
            result = potion.use(player)
            player.inventory.remove(potion)
            self.add_message(result)
        else:
            self.add_message("No usable items in inventory!")
        self.next_turn()
    
    def try_flee(self):
        """Attempt to flee from combat."""
        if random.random() < 0.7:  # 70% chance to escape
            self.add_message("Your party escaped successfully!")
            self.game_state = "playing"
        else:
            self.add_message("Couldn't escape!")
            self.next_turn()

    def game_over_screen(self):
        screen.fill(BLACK)
        title_y = SCREEN_HEIGHT // 2 - 50
        
        self.draw_text("Game Over", SCREEN_WIDTH // 2 - 60, title_y, RED)
        self.draw_text("Press ENTER to return to the main menu", SCREEN_WIDTH // 2 - 200, title_y + 50)
        
        # Show some stats if available
        if self.players:
            highest_level = max(p.level for p in self.players)
            self.draw_text(f"Highest level reached: {highest_level}", SCREEN_WIDTH // 2 - 120, title_y + 100, GRAY)
            self.draw_text(f"Dungeon level reached: {self.dungeon_level}", SCREEN_WIDTH // 2 - 120, title_y + 125, GRAY)
        
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # Reset game state for a new game
                        self.__init__()
                        waiting = False

    def victory_screen(self):
        screen.fill(BLACK)
        title_y = SCREEN_HEIGHT // 2 - 120
        
        # Victory title with gold color
        GOLD = (255, 215, 0)
        self.draw_text("VICTORY!", SCREEN_WIDTH // 2 - 70, title_y, GOLD)
        self.draw_text("You have defeated the dragon and conquered the dungeon!", 
                      SCREEN_WIDTH // 2 - 300, title_y + 50, WHITE)
        
        # Show final stats
        if self.players:
            highest_level = max(p.level for p in self.players)
            self.draw_text(f"Final level reached: {highest_level}", SCREEN_WIDTH // 2 - 120, title_y + 100, GREEN)
            self.draw_text(f"Dungeon fully conquered: {self.dungeon_level}/5", SCREEN_WIDTH // 2 - 140, title_y + 125, GREEN)
            
            # Show some additional victory stats
            player = self.players[0]  # Main player
            self.draw_text(f"Final HP: {player.hp}/{player.max_hp}", SCREEN_WIDTH // 2 - 80, title_y + 150, GRAY)
            if hasattr(player, 'weapon') and player.weapon:
                self.draw_text(f"Weapon: {player.weapon.name}", SCREEN_WIDTH // 2 - 100, title_y + 175, GRAY)
        
        self.draw_text("Congratulations, Hero!", SCREEN_WIDTH // 2 - 150, title_y + 200, GOLD)
        
        # Victory screen options
        self.draw_text("Press N for new game (deletes current save)", SCREEN_WIDTH // 2 - 200, title_y + 240, WHITE)
        self.draw_text("Press M to return to main menu", SCREEN_WIDTH // 2 - 150, title_y + 270, WHITE)
        self.draw_text("Press Q to quit game", SCREEN_WIDTH // 2 - 100, title_y + 300, WHITE)
        
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_n:  # New game - delete save
                        self.delete_save_file()
                        play_music("menu")  # Return to menu music
                        self.game_state = "main_menu"
                        self.reset_game_state()
                        self.game_won = False  # Reset victory state
                        waiting = False
                    elif event.key == pygame.K_m:  # Return to main menu
                        play_music("menu")  # Return to menu music
                        self.game_state = "main_menu"
                        self.reset_game_state()
                        self.game_won = False  # Reset victory state
                        waiting = False
                    elif event.key == pygame.K_q:  # Quit game
                        self.game_over = True
                        waiting = False


if __name__ == "__main__":
    game = Game()
    game.main_loop()
