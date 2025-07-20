#!/usr/bin/env python
print("--- RUNNING PYGAME VERSION ---")
import random
import os
import json
import pygame
from collections import deque

# --- Constants ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
MAP_WIDTH = 40
MAP_HEIGHT = 20
TILE_SIZE = 32  # Increased to better fit sprites
VIEWPORT_WIDTH = 15  # Tiles visible horizontally
VIEWPORT_HEIGHT = 12  # Tiles visible vertically
MINIMAP_SIZE = 200  # Size of the minimap
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 15
MAX_DUNGEON_LEVEL = 5
HIGHSCORE_FILE = "rpg_highscores.json"
SETTINGS_FILE = "rpg_settings.json"

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
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
    
    # Load weapons
    weapon_path = os.path.join(item_base_path, "weapon", "long_sword1.png")
    if os.path.exists(weapon_path):
        sprites["item_weapon"] = pygame.image.load(weapon_path)
        sprites["item_weapon"] = pygame.transform.scale(sprites["item_weapon"], (TILE_SIZE, TILE_SIZE))
        print("  Loaded: weapon (long_sword1.png)")
    else:
        print("  Warning: Weapon sprite not found")
    
    # For armor, we'll use a fallback since armour is in item/armour folder (need to check that)
    armor_path = os.path.join(item_base_path, "armour")
    if os.path.exists(armor_path):
        # Try to find a leather armor or similar
        try:
            armor_files = os.listdir(armor_path)
            if armor_files:
                armor_file = armor_files[0]  # Use first available armor sprite
                full_armor_path = os.path.join(armor_path, armor_file)
                sprites["item_armor"] = pygame.image.load(full_armor_path)
                sprites["item_armor"] = pygame.transform.scale(sprites["item_armor"], (TILE_SIZE, TILE_SIZE))
                print(f"  Loaded: armor ({armor_file})")
            else:
                print("  Warning: No armor sprites found")
        except (FileNotFoundError, pygame.error) as e:
            print(f"  Warning: Could not load armor sprite: {e}")
    else:
        print("  Warning: Armor folder not found")
    
    print(f"Sprite loading complete. Loaded {len(sprites)} sprites.")

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

# --- Sound Assets ---
music_loaded = False
try:
    pygame.mixer.music.load(os.path.join("assets", "music.ogg"))
    music_loaded = True
    sword_sound = pygame.mixer.Sound(os.path.join("assets", "sword.wav"))
    magic_sound = pygame.mixer.Sound(os.path.join("assets", "magic.wav"))
    arrow_sound = pygame.mixer.Sound(os.path.join("assets", "arrow.wav"))
    damage_sound = pygame.mixer.Sound(os.path.join("assets", "damage.wav"))
except pygame.error:
    print("Warning: Could not load sound assets. Game will run without sound.")
    sword_sound = None
    magic_sound = None
    arrow_sound = None
    damage_sound = None

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

class Potion(Item):
    def __init__(self, name, hp_gain):
        super().__init__(name, UI["potion"])
        self.hp_gain = hp_gain

    def use(self, target):
        target.hp = min(target.max_hp, target.hp + self.hp_gain)
        return f'{target.name} used {self.name} and gained {self.hp_gain} HP.'

class Weapon(Item):
    def __init__(self, name, attack_bonus):
        super().__init__(name, UI["weapon"])
        self.attack_bonus = attack_bonus

class Armor(Item):
    def __init__(self, name, defense_bonus):
        super().__init__(name, UI["armor"])
        self.defense_bonus = defense_bonus

# --- Pre-defined Items ---
WEAPONS = [
    Weapon("Dagger", 3),
    Weapon("Short Sword", 5),
    Weapon("Long Sword", 7),
    Weapon("Battle Axe", 10)
]

ARMOR = [
    Armor("Leather Armor", 3),
    Armor("Chainmail", 5),
    Armor("Plate Armor", 7)
]

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
        self.inventory = [Weapon(CLASSES[char_class]["weapon"], 5)]
        self.weapon = self.inventory[0]
        self.armor = None
        self.max_mana = CLASSES[char_class]["mana"]
        self.mana = self.max_mana
        self.skill_cooldown = 0

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
        self.xp = ENEMIES[enemy_type]["xp"]

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
        self.stairs_down = None
        # Fog of war system
        self.explored = [[False for _ in range(width)] for _ in range(height)]
        self.visible = [[False for _ in range(width)] for _ in range(height)]

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
                self.enemies.append(Enemy(x, y, enemy_type))
        
        num_items = random.randint(0, 2)
        for _ in range(num_items):
            x = random.randint(room.x1 + 1, room.x2 - 1)
            y = random.randint(room.y1 + 1, room.y2 - 1)
            if not any(i.x == x and i.y == y for i in self.items):
                item_choice = random.random()
                if item_choice < 0.4:
                    item = Potion("Health Potion", 20)
                elif item_choice < 0.7:
                    item = random.choice(WEAPONS)
                else:
                    item = random.choice(ARMOR)
                item.x = x
                item.y = y
                self.items.append(item)

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

    def add_message(self, text):
        self.messages.appendleft(text)

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
        title_y = SCREEN_HEIGHT // 2 - 100
        self.draw_text("Python RPG Adventure", SCREEN_WIDTH // 2 - 150, title_y)
        
        # Menu options with proper spacing
        self.draw_text("Press ENTER to start", SCREEN_WIDTH // 2 - 120, title_y + 80)
        self.draw_text("Press S for settings", SCREEN_WIDTH // 2 - 100, title_y + 120)
        
        # Show current display mode
        mode_text = "Current mode: " + ("Emoji" if game_settings['use_emojis'] else "Sprite")
        self.draw_text(mode_text, SCREEN_WIDTH // 2 - 80, title_y + 160, GRAY)
        
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.game_state = "setup_num_players"
                elif event.key == pygame.K_s:
                    self.game_state = "settings_menu"

    def settings_menu(self):
        global game_settings
        screen.fill(BLACK)
        self.draw_text("Settings", SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 200)
        
        # Show emoji setting
        emoji_status = "ON" if game_settings['use_emojis'] else "OFF"
        self.draw_text(f"1. Use Emojis: {emoji_status}", 
                      SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 150)
        
        # Only show sprite options if not using emojis
        if not game_settings['use_emojis']:
            # Show current wall selection with preview
            wall_name = game_settings['wall_sprite'].replace('.png', '').replace('_', ' ').title()
            self.draw_text(f"2. Wall Style: {wall_name}", 
                          SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 100)
            
            # Show wall preview
            sprite_key = f"wall_{game_settings['wall_sprite']}"
            if sprite_key in sprites:
                preview_sprite = pygame.transform.scale(sprites[sprite_key], (48, 48))
                screen.blit(preview_sprite, (SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2 - 115))
            
            # Show current floor selection with preview
            floor_name = game_settings['floor_sprite'].replace('.png', '').replace('_', ' ').title()
            self.draw_text(f"3. Floor Style: {floor_name}", 
                          SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50)
            
            # Show floor preview
            sprite_key = f"floor_{game_settings['floor_sprite']}"
            if sprite_key in sprites:
                preview_sprite = pygame.transform.scale(sprites[sprite_key], (48, 48))
                screen.blit(preview_sprite, (SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2 - 65))
                
            # Show instruction for sprite mode
            self.draw_text("Use numbers 2-3 to change sprite styles", 
                          SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 20, GRAY)
        else:
            # Show emoji mode message
            self.draw_text("Emoji mode enabled - sprite options hidden", 
                          SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 80, GRAY)
        
        self.draw_text("Press ESC to go back", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 60)
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
        self.dungeon.generate()
        start_room = self.dungeon.rooms[0]
        for player in self.players:
            player.x, player.y = start_room.center()
        self.update_camera()  # Initialize camera and fog of war
        self.add_message(f"You have entered dungeon level {self.dungeon_level}.")

    def main_loop(self):
        if music_loaded:
            try:
                pygame.mixer.music.play(-1)
            except pygame.error:
                self.add_message("Could not play music.")

        while not self.game_over:
            if self.game_state == "main_menu":
                self.main_menu()
            elif self.game_state == "settings_menu":
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
                self.run_game()
            elif self.game_state == "combat":
                self.run_combat()
            elif self.game_state == "game_over":
                self.game_over_screen()

    def run_game(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            if event.type == pygame.KEYDOWN:
                self.handle_input(event.key)
        self.draw_game()

    def handle_input(self, key):
        player = self.players[self.current_player_idx]
        if key == pygame.K_w:
            self.move_player(player, 'w')
        elif key == pygame.K_s:
            self.move_player(player, 's')
        elif key == pygame.K_a:
            self.move_player(player, 'a')
        elif key == pygame.K_d:
            self.move_player(player, 'd')
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)

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
                player.x = new_x
                player.y = new_y
                self.update_camera()  # Update camera after movement
                for item in list(self.dungeon.items):
                    if item.x == new_x and item.y == new_y:
                        player.inventory.append(item)
                        self.dungeon.items.remove(item)
                        self.add_message(f"{player.name} picked up a {item.name}.")
        else:
            self.add_message("You can't move there.")

    def draw_game(self):
        screen.fill(BLACK)
        
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
                    # Use item sprites when available
                    sprite_drawn = False
                    if isinstance(item, Potion) and "item_potion" in sprites:
                        screen.blit(sprites["item_potion"], (screen_x, screen_y))
                        sprite_drawn = True
                    elif isinstance(item, Weapon) and "item_weapon" in sprites:
                        screen.blit(sprites["item_weapon"], (screen_x, screen_y))
                        sprite_drawn = True
                    elif isinstance(item, Armor) and "item_armor" in sprites:
                        screen.blit(sprites["item_armor"], (screen_x, screen_y))
                        sprite_drawn = True
                    
                    # Fallback to colored rectangle if sprite not available
                    if not sprite_drawn:
                        pygame.draw.rect(screen, BLUE, (screen_x + 4, screen_y + 4, TILE_SIZE - 8, TILE_SIZE - 8))
                
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
                    # Use enemy sprites when available
                    sprite_drawn = False
                    enemy_type = enemy.name.lower()
                    sprite_key = f"monster_{enemy_type}"
                    if sprite_key in sprites:
                        screen.blit(sprites[sprite_key], (screen_x, screen_y))
                        sprite_drawn = True
                    
                    # Fallback to colored rectangle if sprite not available
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
                    # Use player class sprites when available
                    sprite_drawn = False
                    sprite_key = f"player_{player.char_class}"
                    if sprite_key in sprites:
                        screen.blit(sprites[sprite_key], (screen_x, screen_y))
                        sprite_drawn = True
                    
                    # Fallback to colored rectangle if sprite not available
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
        
        # Draw current dungeon level
        level_text = f"Dungeon Level: {self.dungeon_level}"
        self.draw_text(level_text, 15, 155, LIGHT_GRAY)


    def start_combat(self, enemies):
        self.game_state = "combat"
        self.combat_enemies = enemies
        self.turn_order = self.players + self.combat_enemies
        random.shuffle(self.turn_order)
        self.combat_turn_idx = 0
        self.add_message("You've entered combat!")

    def run_combat(self):
        self.draw_combat_screen()
        entity = self.turn_order[self.combat_turn_idx]

        if isinstance(entity, Player):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.player_attack()
                    elif event.key == pygame.K_2:
                        self.use_skill(entity, self.combat_enemies)
        else: # Enemy turn
            pygame.time.wait(500) # Pause for half a second to show enemy turn
            self.enemy_attack(entity)

        if not any(p.is_alive() for p in self.players):
            self.add_message("Your party has been defeated. Game Over.")
            self.game_state = "game_over"
        elif not any(e.is_alive() for e in self.combat_enemies):
            self.add_message("You won the battle!")
            self.game_state = "playing"
            total_xp = sum(e.xp for e in self.combat_enemies)
            xp_per_player = total_xp // len(self.players) if self.players else 0
            for p in self.players:
                if p.is_alive():
                    msg = p.gain_xp(xp_per_player)
                    if msg: self.add_message(msg)
            self.dungeon.enemies = [e for e in self.dungeon.enemies if e not in self.combat_enemies]

    def player_attack(self):
        player = self.turn_order[self.combat_turn_idx]
        alive_enemies = [e for e in self.combat_enemies if e.is_alive()]
        if alive_enemies:
            target = random.choice(alive_enemies)
            damage = max(0, player.attack - target.defense)
            target.take_damage(damage)
            self.add_message(f"{player.name} hits {target.name} for {damage} damage.")
        self.next_turn()

    def enemy_attack(self, enemy):
        alive_players = [p for p in self.players if p.is_alive()]
        if alive_players:
            target = random.choice(alive_players)
            damage = max(0, enemy.attack - target.defense)
            target.take_damage(damage)
            self.add_message(f"{enemy.name} hits {target.name} for {damage} damage.")
        self.next_turn()

    def next_turn(self):
        self.combat_turn_idx = (self.combat_turn_idx + 1) % len(self.turn_order)
        
        # Reduce skill cooldowns for players at the start of their turn
        current_entity = self.turn_order[self.combat_turn_idx]
        if isinstance(current_entity, Player) and hasattr(current_entity, 'skill_cooldown'):
            if current_entity.skill_cooldown > 0:
                current_entity.skill_cooldown -= 1
        
        # Skip turns for dead entities
        while not self.turn_order[self.combat_turn_idx].is_alive():
            self.combat_turn_idx = (self.combat_turn_idx + 1) % len(self.turn_order)


    def draw_combat_screen(self):
        screen.fill(BLACK)
        
        # Draw combat title
        self.draw_text("COMBAT", SCREEN_WIDTH // 2 - 50, 20, WHITE)
        
        # Draw players section
        player_section_x = 50
        player_section_y = 80
        self.draw_text("Your Party:", player_section_x, player_section_y, GREEN)
        
        for i, player in enumerate(self.players):
            y_pos = player_section_y + 40 + i * 50
            
            # Highlight current player's turn
            current_entity = self.turn_order[self.combat_turn_idx]
            color = (255, 255, 0) if player == current_entity else WHITE  # Yellow for current turn
            
            if game_settings['use_emojis']:
                status = f'{player.icon} {player.name}'
            else:
                status = f'• {player.name} ({player.char_class})'
            
            self.draw_text(status, player_section_x, y_pos, color)
            
            # Health bar representation
            hp_text = f"HP: {player.hp}/{player.max_hp}"
            self.draw_text(hp_text, player_section_x, y_pos + 20, color)
            
            # Mana for mages
            if player.char_class == "mage":
                mana_text = f"Mana: {player.mana}/{player.max_mana}"
                self.draw_text(mana_text, player_section_x + 120, y_pos + 20, color)
            
            # Skill cooldown indicators
            if hasattr(player, 'skill_cooldown') and player.skill_cooldown > 0:
                cooldown_text = f"Cooldown: {player.skill_cooldown}"
                self.draw_text(cooldown_text, player_section_x + 200, y_pos + 20, (255, 100, 100))

        # Draw enemies section
        enemy_section_x = SCREEN_WIDTH - 350
        enemy_section_y = 80
        self.draw_text("Enemies:", enemy_section_x, enemy_section_y, RED)
        
        for i, enemy in enumerate(self.combat_enemies):
            y_pos = enemy_section_y + 40 + i * 50
            
            # Highlight current enemy's turn
            current_entity = self.turn_order[self.combat_turn_idx]
            color = (255, 255, 0) if enemy == current_entity else WHITE  # Yellow for current turn
            
            if game_settings['use_emojis']:
                status = f'{enemy.icon} {enemy.name}'
            else:
                status = f'• {enemy.name}'
            
            self.draw_text(status, enemy_section_x, y_pos, color)
            
            # Health display
            hp_text = f"HP: {enemy.hp}/{enemy.max_hp}"
            self.draw_text(hp_text, enemy_section_x, y_pos + 20, color)

        # Draw combat menu at bottom
        menu_y = SCREEN_HEIGHT - 150
        menu_surface = pygame.Surface((SCREEN_WIDTH, 100))
        menu_surface.set_alpha(200)
        menu_surface.fill((50, 50, 50))
        screen.blit(menu_surface, (0, menu_y))
        
        current_entity = self.turn_order[self.combat_turn_idx]
        if isinstance(current_entity, Player):
            self.draw_text(f"{current_entity.name}'s Turn - Choose Action:", 50, menu_y + 10, WHITE)
            self.draw_text("1. Attack - Basic attack on random enemy", 50, menu_y + 35, WHITE)
            
            # Dynamic skill description
            if current_entity.char_class == "warrior":
                skill_text = "2. Power Strike - 2x damage attack"
                if current_entity.skill_cooldown > 0:
                    skill_text += f" (Cooldown: {current_entity.skill_cooldown})"
            elif current_entity.char_class == "mage":
                skill_text = "2. Fireball - AoE damage to all enemies"
                if current_entity.mana < 10:
                    skill_text += " (Not enough mana!)"
            elif current_entity.char_class == "archer":
                skill_text = "2. Double Shot - Two attacks"
                if current_entity.skill_cooldown > 0:
                    skill_text += f" (Cooldown: {current_entity.skill_cooldown})"
            else:
                skill_text = "2. Special Skill"
                
            self.draw_text(skill_text, 50, menu_y + 60, WHITE)
        else:
            self.draw_text(f"{current_entity.name} is thinking...", 50, menu_y + 25, (255, 200, 200))

        # Draw messages in combat
        if self.messages:
            msg_y = menu_y - 120
            for i, msg in enumerate(self.messages):
                if i < 3:  # Show only last 3 messages in combat
                    self.draw_text(msg, 50, msg_y - i * 25, (200, 200, 200))
                    
        pygame.display.flip()

    def use_skill(self, player, enemies):
        if player.char_class == "warrior":
            if player.skill_cooldown > 0:
                self.add_message(f"Power Strike is on cooldown for {player.skill_cooldown} more turns.")
                return
            if sword_sound:
                sword_sound.play()
            target = random.choice([e for e in enemies if e.is_alive()])
            damage = player.attack * 2
            target.take_damage(damage)
            self.add_message(f"{player.name} uses Power Strike on {target.name} for {damage} damage!")
            player.skill_cooldown = 3
        elif player.char_class == "mage":
            if player.mana < 10:
                self.add_message("Not enough mana for Fireball.")
                return
            if magic_sound:
                magic_sound.play()
            self.add_message(f"{player.name} casts Fireball!")
            for enemy in enemies:
                if enemy.is_alive():
                    damage = player.attack // 2
                    enemy.take_damage(damage)
                    self.add_message(f"Fireball hits {enemy.name} for {damage} damage.")
            player.mana -= 10
        elif player.char_class == "archer":
            if player.skill_cooldown > 0:
                self.add_message(f"Double Shot is on cooldown for {player.skill_cooldown} more turns.")
                return
            if arrow_sound:
                arrow_sound.play()
            self.add_message(f"{player.name} uses Double Shot!")
            for _ in range(2):
                target = random.choice([e for e in enemies if e.is_alive()])
                damage = player.attack
                target.take_damage(damage)
                self.add_message(f"{player.name} shoots {target.name} for {damage} damage.")
            player.skill_cooldown = 2
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


if __name__ == "__main__":
    game = Game()
    game.main_loop()
