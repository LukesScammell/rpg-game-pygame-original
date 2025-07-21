#!/usr/bin/env python
print("--- RUNNING PYGAME VERSION ---")
import random
import os
import json
import pygame
import math
from collections import deque

# --- Constants ---
SCREEN_WIDTH = 1920  # Increased for larger display
SCREEN_HEIGHT = 1080  # Increased for larger display
MAP_WIDTH = 40
MAP_HEIGHT = 20
TILE_SIZE = 64  # Larger tiles to better fill screen space
# Dynamic viewport - will be calculated based on screen size
VIEWPORT_WIDTH = 26  # Increased to show more of the world (was 20)
VIEWPORT_HEIGHT = 18  # Increased to show more of the world (was 15)
# Game area positioning for centering
GAME_AREA_WIDTH = 1600  # Default, will be updated dynamically
GAME_AREA_HEIGHT = 800  # Default, will be updated dynamically
GAME_OFFSET_X = 0  # Default, will be updated dynamically
GAME_OFFSET_Y = 0  # Default, will be updated dynamically
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

# --- Settings System ---
def load_settings():
    """Load game settings from file."""
    default_settings = {
        "use_emojis": True,
        "wall_sprite": "stone_brick1.png",
        "floor_sprite": "sandstone_floor0.png",
        "resolution": [1920, 1080],  # [width, height]
        "music_volume": 0.5,  # 0.0 to 1.0
        "sound_volume": 0.7,  # 0.0 to 1.0
        "fullscreen": True
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

# Apply resolution settings
SCREEN_WIDTH = game_settings["resolution"][0]
SCREEN_HEIGHT = game_settings["resolution"][1]

# Initialize screen with settings-based resolution
def apply_resolution_settings():
    global screen, SCREEN_WIDTH, SCREEN_HEIGHT, VIEWPORT_WIDTH, VIEWPORT_HEIGHT, GAME_AREA_WIDTH, GAME_AREA_HEIGHT, GAME_OFFSET_X, GAME_OFFSET_Y
    SCREEN_WIDTH = game_settings["resolution"][0]
    SCREEN_HEIGHT = game_settings["resolution"][1]
    
    if game_settings["fullscreen"]:
        # Get desktop resolution for proper fullscreen
        desktop_info = pygame.display.Info()
        screen = pygame.display.set_mode((desktop_info.current_w, desktop_info.current_h), pygame.FULLSCREEN)
        # Update SCREEN dimensions to actual fullscreen size
        SCREEN_WIDTH = desktop_info.current_w
        SCREEN_HEIGHT = desktop_info.current_h
    else:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("RPG Game - Undertale Edition")
    
    # Calculate game area and viewport to fill most of the screen
    # Reserve minimal space for UI: 80px top, 120px bottom, 260px right for minimap
    ui_top_height = 80
    ui_bottom_height = 120
    ui_right_width = 260
    
    GAME_AREA_WIDTH = SCREEN_WIDTH - ui_right_width
    GAME_AREA_HEIGHT = SCREEN_HEIGHT - ui_top_height - ui_bottom_height
    
    # Calculate viewport size to fit the available game area
    VIEWPORT_WIDTH = max(25, GAME_AREA_WIDTH // TILE_SIZE)
    VIEWPORT_HEIGHT = max(18, GAME_AREA_HEIGHT // TILE_SIZE)
    
    # Center the game area in the available space
    GAME_OFFSET_X = (GAME_AREA_WIDTH - (VIEWPORT_WIDTH * TILE_SIZE)) // 2
    GAME_OFFSET_Y = ui_top_height + (GAME_AREA_HEIGHT - (VIEWPORT_HEIGHT * TILE_SIZE)) // 2

# Initial screen setup - Apply settings immediately
apply_resolution_settings()

# Apply audio volume settings
def apply_audio_settings():
    pygame.mixer.music.set_volume(game_settings["music_volume"])
    # Note: Sound volume will be applied per-sound when playing

apply_audio_settings()

# --- Sprite Loading ---
sprites = {}
ui_elements = {}

# --- Animation System ---
class PortraitAnimation:
    def __init__(self, frames, frame_duration=500):
        self.frames = frames  # List of pygame surfaces
        self.frame_duration = frame_duration  # Duration per frame in milliseconds
        self.current_frame = 0
        self.last_frame_time = pygame.time.get_ticks()
    
    def update(self):
        """Update animation frame based on time"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_frame_time > self.frame_duration and len(self.frames) > 1:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_frame_time = current_time
    
    def get_current_frame(self):
        """Get the current frame surface"""
        if not self.frames:
            return None
        return self.frames[self.current_frame]

# Global animation storage
portrait_animations = {}

def load_sprites():
    """Load all sprite images with Undertale character system."""
    global sprites, portrait_animations
    
    print("=== Loading Undertale-based sprites ===")
    
    # Load wall sprites
    print("Loading wall sprites...")
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
    
    # Load Undertale player sprites with directional movement
    print("Loading Undertale player sprites...")
    
    # Warrior = Frisk (main character with full directional sprites)
    frisk_path = os.path.join("assets", "undertale", "Characters", "Frisk")
    frisk_directions = {
        "down": ["spr_maincharad_0.png", "spr_maincharad_1.png", "spr_maincharad_2.png", "spr_maincharad_3.png"],
        "left": ["spr_maincharal_0.png", "spr_maincharal_1.png"],
        "right": ["spr_maincharar_0.png", "spr_maincharar_1.png"],
        "up": ["spr_maincharau_0.png", "spr_maincharau_1.png", "spr_maincharau_2.png", "spr_maincharau_3.png"]
    }
    
    for direction, sprite_files in frisk_directions.items():
        frames = []
        for sprite_file in sprite_files:
            sprite_path = os.path.join(frisk_path, sprite_file)
            if os.path.exists(sprite_path):
                try:
                    frame = pygame.image.load(sprite_path)
                    frames.append(pygame.transform.scale(frame, (TILE_SIZE, TILE_SIZE)))
                except pygame.error:
                    continue
        
        if frames:
            sprites[f"player_warrior_{direction}"] = frames[0]  # First frame for static display
            portrait_animations[f"warrior_{direction}"] = PortraitAnimation(frames, 300)
            print(f"  Loaded: warrior (Frisk) {direction} - {len(frames)} frames")
    
    # Set default warrior sprite
    if "player_warrior_down" in sprites:
        sprites["player_warrior"] = sprites["player_warrior_down"]
    
    # Mage = Asriel (has directional sprites)
    asriel_path = os.path.join("assets", "undertale", "Characters", "Asriel")
    asriel_directions = {
        "down": ["spr_asriel_d_0.png"],
        "left": ["spr_asriel_l_0.png", "spr_asriel_l_1.png"],
        "right": ["spr_asriel_r_0.png", "spr_asriel_r_1.png"],
        "up": ["spr_asriel_u_0.png", "spr_asriel_u_1.png", "spr_asriel_u_2.png", "spr_asriel_u_3.png"]
    }
    
    asriel_loaded = False
    for direction, sprite_files in asriel_directions.items():
        frames = []
        for sprite_file in sprite_files:
            sprite_path = os.path.join(asriel_path, sprite_file)
            if os.path.exists(sprite_path):
                try:
                    frame = pygame.image.load(sprite_path)
                    frames.append(pygame.transform.scale(frame, (TILE_SIZE, TILE_SIZE)))
                    asriel_loaded = True
                except pygame.error:
                    continue
        
        if frames:
            sprites[f"player_mage_{direction}"] = frames[0]  # First frame for static display
            portrait_animations[f"mage_{direction}"] = PortraitAnimation(frames, 300)
            print(f"  Loaded: mage (Asriel) {direction} - {len(frames)} frames")
    
    # Set default mage sprite
    if "player_mage_down" in sprites:
        sprites["player_mage"] = sprites["player_mage_down"]
        print("  Loaded: mage (Asriel)")
    
    if not asriel_loaded:
        # Fallback: Use Frisk for mage too
        if "player_warrior" in sprites:
            sprites["player_mage"] = sprites["player_warrior"]
            for direction in ["down", "left", "right", "up"]:
                if f"player_warrior_{direction}" in sprites:
                    sprites[f"player_mage_{direction}"] = sprites[f"player_warrior_{direction}"]
                    if f"warrior_{direction}" in portrait_animations:
                        portrait_animations[f"mage_{direction}"] = portrait_animations[f"warrior_{direction}"]
            print("  Loaded: mage (Frisk fallback)")
    
    # Archer = Monster Kid (has full directional sprites)
    monster_kid_path = os.path.join("assets", "undertale", "Characters", "Monster Kid")
    mk_directions = {
        "down": ["spr_mkid_d_0.png", "spr_mkid_d_1.png", "spr_mkid_d_2.png"],
        "left": ["spr_mkid_l_0.png", "spr_mkid_l_1.png", "spr_mkid_l_2.png"],
        "right": ["spr_mkid_r_0.png", "spr_mkid_r_1.png", "spr_mkid_r_2.png"],
        "up": ["spr_mkid_u_0.png", "spr_mkid_u_1.png", "spr_mkid_u_2.png"]
    }
    
    mk_loaded = False
    for direction, sprite_files in mk_directions.items():
        frames = []
        for sprite_file in sprite_files:
            sprite_path = os.path.join(monster_kid_path, sprite_file)
            if os.path.exists(sprite_path):
                try:
                    frame = pygame.image.load(sprite_path)
                    frames.append(pygame.transform.scale(frame, (TILE_SIZE, TILE_SIZE)))
                    mk_loaded = True
                except pygame.error:
                    continue
        
        if frames:
            sprites[f"player_archer_{direction}"] = frames[0]  # First frame for static display
            portrait_animations[f"archer_{direction}"] = PortraitAnimation(frames, 300)
            print(f"  Loaded: archer (Monster Kid) {direction} - {len(frames)} frames")
    
    # Set default archer sprite
    if "player_archer_down" in sprites:
        sprites["player_archer"] = sprites["player_archer_down"]
        print("  Loaded: archer (Monster Kid)")
    
    if not mk_loaded:
        print("  Warning: Monster Kid directional sprites not found for archer")
    
    # Load Undertale enemy sprites with animated portraits
    print("Loading Undertale enemy sprites...")
    
    enemy_sprite_mapping = {
        # Training dummy
        "dummy": {
            "path": os.path.join("assets", "undertale", "Characters", "Dummies"),
            "files": ["spr_dummy_0.png"],
            "portrait_files": ["spr_dummy_0.png"]
        },
        
        # Ruins enemies (Froggit & Vegetoid from actual enemy sprites)
        "froggit": {
            "path": os.path.join("assets", "undertale", "Characters", "# NPCs", "01 - Ruins"),
            "files": ["spr_smallfrog_0.png"],
            "portrait_files": ["spr_smallfrog_0.png", "spr_smallfrog_1.png", "spr_smallfrog_2.png", "spr_smallfrog_3.png"]
        },
        
        "vegetoid": {
            "path": os.path.join("assets", "undertale", "Characters", "# NPCs", "01 - Ruins"),
            "files": ["spr_vegetableoutside_0.png"],
            "portrait_files": ["spr_vegetableoutside_0.png", "spr_vegetableoutside_1.png"]
        },
        
        # Snowdin enemies (using actual area sprites)
        "snowdrake": {
            "path": os.path.join("assets", "undertale", "Characters", "# NPCs", "02 - Snowdin", "Snowdin Forest"),
            "files": ["spr_snowdrakenpc_0.png"],
            "portrait_files": ["spr_snowdrakenpc_0.png", "spr_snowdrakenpc_1.png"]
        },
        
        "icecap": {
            "path": os.path.join("assets", "undertale", "Characters", "# NPCs", "02 - Snowdin", "Snowdin Forest"),
            "files": ["spr_icecapb_npc_0.png"],
            "portrait_files": ["spr_icecapb_npc_0.png", "spr_icecapb_npc_1.png", "spr_icecapg_npc_0.png", "spr_icecapr_npc_0.png"]
        },
        
        "gyftrot": {
            "path": os.path.join("assets", "undertale", "Characters", "# NPCs", "02 - Snowdin", "Snowdin Forest"),
            "files": ["spr_gyftrotnpc_0.png"],
            "portrait_files": ["spr_gyftrotnpc_0.png", "spr_gyftrotnpc_1.png"]
        },
        
        # Special enemies using creature sprites
        "whimsun": {
            "path": os.path.join("assets", "undertale", "Characters", "# NPCs", "02 - Snowdin", "Snowdin Forest"),
            "files": ["spr_faun_0.png"],
            "portrait_files": ["spr_faun_0.png", "spr_faun_1.png"]
        },
        
        "loox": {
            "path": os.path.join("assets", "undertale", "Characters", "Mysteryman & Gaster Followers"),
            "files": ["spr_g_follower_1.png"] if os.path.exists(os.path.join("assets", "undertale", "Characters", "Mysteryman & Gaster Followers", "spr_g_follower_1.png")) else ["spr_dummy_0.png"],
            "portrait_files": ["spr_g_follower_1.png"] if os.path.exists(os.path.join("assets", "undertale", "Characters", "Mysteryman & Gaster Followers", "spr_g_follower_1.png")) else ["spr_dummy_0.png"],
            "fallback_path": os.path.join("assets", "undertale", "Characters", "Dummies")
        },
        
        "moldsmal": {
            "path": os.path.join("assets", "undertale", "Characters", "Amalgamates"),
            "files": ["spr_amalgam_save_0.png"],
            "portrait_files": ["spr_amalgam_save_0.png", "spr_amalgam_save_1.png", "spr_amalgam_save_2.png"]
        },
        
        # Underground creatures
        "pyrope": {
            "path": os.path.join("assets", "undertale", "Characters", "Amalgamates"),
            "files": ["spr_amalgam_exc_0.png"],
            "portrait_files": ["spr_amalgam_exc_0.png", "spr_amalgam_exc_1.png", "spr_amalgam_exc_2.png", "spr_amalgam_exc_3.png"]
        },
        
        "vulkin": {
            "path": os.path.join("assets", "undertale", "Characters", "Amalgamates"),
            "files": ["spr_amalgam_fridge_0.png"],
            "portrait_files": ["spr_amalgam_fridge_0.png", "spr_amalgam_fridge_1.png", "spr_amalgam_fridge_2.png"]
        },
        
        "tsunderplane": {
            "path": os.path.join("assets", "undertale", "Characters", "Amalgamates"),
            "files": ["spr_amalgam_dogball_0.png"],
            "portrait_files": ["spr_amalgam_dogball_0.png", "spr_amalgam_dogball_1.png", "spr_amalgam_dogball_2.png"]
        },
        
        # Special creature - Temmie
        "temmie": {
            "path": os.path.join("assets", "undertale", "Characters", "Temmie"),
            "files": ["spr_temmie_hive_0.png"],
            "portrait_files": ["spr_temmie_hive_0.png", "spr_temmie_hive_1.png", "spr_temmie_hive_2.png", "spr_temmie_hive_3.png"]
        },
        
        # Boss-level Spider
        "muffet": {
            "path": os.path.join("assets", "undertale", "Characters", "Muffet"),
            "files": ["spr_muffet_overworld_0.png"],
            "portrait_files": ["spr_muffet_overworld_0.png", "spr_muffet_overworld_1.png", "spr_muffet_overworld_2.png", "spr_muffet_overworld_3.png"]
        },
        
        # Flowey (multiple animation frames)
        "flowey": {
            "path": os.path.join("assets", "undertale", "Characters", "Flowey"),
            "files": ["spr_flowey_0.png"],
            "portrait_files": ["spr_flowey_0.png", "spr_flowey_1.png", "spr_floweylaughoverworld_0.png", "spr_floweylaughoverworld_1.png"]
        },
        
        # Sans (multiple poses for animation)
        "sans": {
            "path": os.path.join("assets", "undertale", "Characters", "sans"),
            "files": ["spr_sans_d_0.png"],
            "portrait_files": ["spr_sans_d_0.png", "spr_sans_d_1.png", "spr_sans_d_2.png", "spr_sans_d_3.png"],
            "portrait_path": os.path.join("assets", "undertale", "Characters", "Portraits-20250721T005640Z-1-001", "Portraits", "Sans")
        },
        
        # Papyrus
        "papyrus": {
            "path": os.path.join("assets", "undertale", "Characters", "Papyrus"),
            "files": ["spr_papyrus_d_0.png"],
            "portrait_files": ["spr_papyrus_d_0.png", "spr_papyrus_d_1.png", "spr_papyrus_d_2.png", "spr_papyrus_d_3.png"],
            "portrait_path": os.path.join("assets", "undertale", "Characters", "Portraits-20250721T005640Z-1-001", "Portraits", "Papyrus")
        },
        
        # Undyne  
        "undyne": {
            "path": os.path.join("assets", "undertale", "Characters", "Undyne", "No Armor"),
            "files": ["spr_undyne_d_0.png"],
            "portrait_files": ["spr_undyne_d_0.png", "spr_undyne_d_1.png", "spr_undyne_d_2.png", "spr_undyne_d_3.png"],
            "portrait_path": os.path.join("assets", "undertale", "Characters", "Portraits-20250721T005640Z-1-001", "Portraits", "Undyne")
        },
        
        # Mettaton
        "mettaton": {
            "path": os.path.join("assets", "undertale", "Characters", "Mettaton"),
            "files": ["spr_mettaton_talk_0.png"],
            "portrait_files": ["spr_mettaton_talk_0.png", "spr_mettaton_talk_1.png", "spr_mettaton_wave_0.png", "spr_mettaton_wave_1.png"]
        },
        
        # Alphys
        "alphys": {
            "path": os.path.join("assets", "undertale", "Characters", "Alphys"),
            "files": ["spr_alphys_d_0.png"],
            "portrait_files": ["spr_alphys_d_0.png", "spr_alphys_d_1.png", "spr_alphys_d_2.png", "spr_alphys_d_3.png"],
            "portrait_path": os.path.join("assets", "undertale", "Characters", "Portraits-20250721T005640Z-1-001", "Portraits", "Alphys")
        },
        
        # Toriel
        "toriel": {
            "path": os.path.join("assets", "undertale", "Characters", "Toriel"),
            "files": ["spr_toriel_d_0.png"],
            "portrait_files": ["spr_toriel_d_0.png", "spr_toriel_d_1.png", "spr_toriel_d_2.png", "spr_toriel_d_3.png"],
            "portrait_path": os.path.join("assets", "undertale", "Characters", "Portraits-20250721T005640Z-1-001", "Portraits", "Toriel")
        },
        
        # Asgore
        "asgore": {
            "path": os.path.join("assets", "undertale", "Characters", "Asgore"), 
            "files": ["spr_asgore_d_0.png"],
            "portrait_files": ["spr_asgore_d_0.png", "spr_asgore_d_1.png", "spr_asgore_d_2.png", "spr_asgore_d_3.png"],
            "portrait_path": os.path.join("assets", "undertale", "Characters", "Portraits-20250721T005640Z-1-001", "Portraits", "Asgore")
        },
        
        # Ghost enemy
        "napstablook": {
            "path": os.path.join("assets", "undertale", "Characters", "Napstablook"),
            "files": ["spr_napstablook_d_0.png"],
            "portrait_files": ["spr_napstablook_d_0.png", "spr_napstablook_l_0.png", "spr_napstablook_r_0.png"]
        },
        
        # Fire creature
        "grillby": {
            "path": os.path.join("assets", "undertale", "Characters", "Grillby"),
            "files": ["spr_grillby_d_0.png"],
            "portrait_files": ["spr_grillby_d_0.png", "spr_grillby_d_1.png", "spr_grillby_d_2.png", "spr_grillby_d_3.png"]
        },
        
        # Sea creature
        "onionsan": {
            "path": os.path.join("assets", "undertale", "Characters", "Onionsan"),
            "files": ["spr_onionsan_bright_0.png"],
            "portrait_files": ["spr_onionsan_bright_0.png", "spr_onionsan_bright_1.png", "spr_onionsan_kawaii_0.png", "spr_onionsan_kawaii_1.png"]
        }
    }
    
    # Load all enemy sprites and portraits
    for enemy_name, config in enemy_sprite_mapping.items():
        # Load main sprite
        sprite_loaded = False
        for sprite_file in config["files"]:
            sprite_path = os.path.join(config["path"], sprite_file)
            # Try fallback path if main path doesn't work
            if not os.path.exists(sprite_path) and "fallback_path" in config:
                sprite_path = os.path.join(config["fallback_path"], sprite_file)
            
            if os.path.exists(sprite_path):
                try:
                    enemy_sprite = pygame.image.load(sprite_path)
                    sprites[f"monster_{enemy_name}"] = pygame.transform.scale(enemy_sprite, (TILE_SIZE, TILE_SIZE))
                    sprite_loaded = True
                    break
                except pygame.error:
                    continue
        
        # Load portrait animation frames
        portrait_frames = []
        
        # Try portrait-specific path first
        if "portrait_path" in config and os.path.exists(config["portrait_path"]):
            for portrait_file in os.listdir(config["portrait_path"]):
                if portrait_file.endswith('.png') and not portrait_file.startswith('Unused'):
                    portrait_path = os.path.join(config["portrait_path"], portrait_file)
                    try:
                        portrait_frame = pygame.image.load(portrait_path)
                        portrait_frames.append(pygame.transform.scale(portrait_frame, (128, 128)))
                    except pygame.error:
                        continue
        
        # Fallback to main character folder
        if not portrait_frames:
            for portrait_file in config["portrait_files"]:
                portrait_path = os.path.join(config["path"], portrait_file)
                # Try fallback path if main path doesn't work
                if not os.path.exists(portrait_path) and "fallback_path" in config:
                    portrait_path = os.path.join(config["fallback_path"], portrait_file)
                
                if os.path.exists(portrait_path):
                    try:
                        portrait_frame = pygame.image.load(portrait_path)
                        portrait_frames.append(pygame.transform.scale(portrait_frame, (128, 128)))
                    except pygame.error:
                        continue
        
        if portrait_frames:
            portrait_animations[f"enemy_{enemy_name}"] = PortraitAnimation(portrait_frames, 800)
        
        if sprite_loaded:
            print(f"  Loaded: {enemy_name} - {len(portrait_frames)} portrait frames")
        else:
            print(f"  Warning: Could not load sprite for {enemy_name}")
    
    # No longer need simplified enemies mapping - all enemies now have proper sprites!
    
    # Load original crawl enemies as fallbacks
    print("Loading original crawl enemy sprites...")
    original_enemies = {
        "goblin": "goblin.png",
        "orc": "orc_warrior.png", 
        "troll": "troll.png",
        "dragon": "dragon.png"
    }
    
    monster_path = os.path.join("assets", "crawl-tiles Oct-5-2010", "dc-mon")
    for enemy_name, sprite_file in original_enemies.items():
        sprite_path = os.path.join(monster_path, sprite_file)
        if os.path.exists(sprite_path):
            try:
                enemy_sprite = pygame.image.load(sprite_path)
                sprites[f"monster_{enemy_name}"] = pygame.transform.scale(enemy_sprite, (TILE_SIZE, TILE_SIZE))
                # Create simple portrait animation
                portrait_frames = [pygame.transform.scale(enemy_sprite, (128, 128))]
                portrait_animations[f"enemy_{enemy_name}"] = PortraitAnimation(portrait_frames, 1000)
                print(f"  Loaded: {enemy_name} (original)")
            except pygame.error:
                continue
    
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
    
    print(f"Sprite loading complete. Loaded {len(sprites)} sprites and {len(portrait_animations)} portrait animations.")

    # Load skill spell icons
    print("Loading skill spell icons...")
    spell_base_path = os.path.join("assets", "crawl-tiles Oct-5-2010", "spells")
    effect_base_path = os.path.join("assets", "crawl-tiles Oct-5-2010", "effect")
    
    # Load warrior skill icon (Power Strike)
    power_strike_path = os.path.join(spell_base_path, "enchantment", "berserker_rage.png")
    if os.path.exists(power_strike_path):
        sprites["skill_power_strike"] = pygame.image.load(power_strike_path)
        sprites["skill_power_strike"] = pygame.transform.scale(sprites["skill_power_strike"], (TILE_SIZE, TILE_SIZE))
        print("  Loaded: Power Strike skill icon")
    else:
        print("  Warning: Power Strike skill icon not found")
    
    # Load mage skill icon (Fireball)
    fireball_path = os.path.join(spell_base_path, "fire", "fireball.png")
    if os.path.exists(fireball_path):
        sprites["skill_fireball"] = pygame.image.load(fireball_path)
        sprites["skill_fireball"] = pygame.transform.scale(sprites["skill_fireball"], (TILE_SIZE, TILE_SIZE))
        print("  Loaded: Fireball skill icon")
    else:
        print("  Warning: Fireball skill icon not found")
    
    # Load archer skill icon (Double Shot)
    double_shot_path = os.path.join(effect_base_path, "arrow0.png")
    if os.path.exists(double_shot_path):
        sprites["skill_double_shot"] = pygame.image.load(double_shot_path)
        sprites["skill_double_shot"] = pygame.transform.scale(sprites["skill_double_shot"], (TILE_SIZE, TILE_SIZE))
        print("  Loaded: Double Shot skill icon")
    else:
        print("  Warning: Double Shot skill icon not found")
    
    print(f"Skill icon loading complete.")

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

# --- Enhanced UI Functions and Visual Effects ---
def lerp(a, b, t):
    """Linear interpolation between two values."""
    return a + (b - a) * t

def smooth_color_transition(color1, color2, progress):
    """Smooth transition between two colors."""
    r = int(lerp(color1[0], color2[0], progress))
    g = int(lerp(color1[1], color2[1], progress))
    b = int(lerp(color1[2], color2[2], progress))
    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

def draw_text_with_shadow(surface, text, x, y, color, font_obj=None, shadow_offset=2):
    """Draw text with a subtle shadow for better readability."""
    if font_obj is None:
        font_obj = font
    
    # Draw shadow
    shadow_surface = font_obj.render(text, True, (0, 0, 0))
    surface.blit(shadow_surface, (x + shadow_offset, y + shadow_offset))
    
    # Draw main text
    text_surface = font_obj.render(text, True, color)
    surface.blit(text_surface, (x, y))
    return text_surface.get_rect(x=x, y=y)

def draw_gradient_rect(surface, rect, color1, color2, vertical=True):
    """Draw a rectangle with a gradient fill."""
    if vertical:
        for y in range(rect.height):
            progress = y / rect.height
            color = smooth_color_transition(color1, color2, progress)
            pygame.draw.line(surface, color, 
                           (rect.x, rect.y + y), 
                           (rect.x + rect.width - 1, rect.y + y))
    else:
        for x in range(rect.width):
            progress = x / rect.width
            color = smooth_color_transition(color1, color2, progress)
            pygame.draw.line(surface, color,
                           (rect.x + x, rect.y),
                           (rect.x + x, rect.y + rect.height - 1))

def draw_fancy_button(surface, rect, text, font_obj, base_color, hover_color, pressed_color, 
                     is_hovered=False, is_pressed=False, border_radius=8):
    """Draw an enhanced button with gradient, shadow, and hover effects."""
    # Determine current color
    if is_pressed:
        current_color = pressed_color
        shadow_offset = 1
    elif is_hovered:
        current_color = hover_color
        shadow_offset = 3
    else:
        current_color = base_color
        shadow_offset = 2
    
    # Draw button shadow
    shadow_rect = rect.copy()
    shadow_rect.x += shadow_offset
    shadow_rect.y += shadow_offset
    pygame.draw.rect(surface, (0, 0, 0, 100), shadow_rect, border_radius=border_radius)
    
    # Draw gradient background
    gradient_color2 = (
        max(0, min(255, current_color[0] - 30)),
        max(0, min(255, current_color[1] - 30)),
        max(0, min(255, current_color[2] - 30))
    )
    draw_gradient_rect(surface, rect, current_color, gradient_color2, vertical=True)
    
    # Draw border
    border_color = (
        max(0, min(255, current_color[0] + 50)),
        max(0, min(255, current_color[1] + 50)),
        max(0, min(255, current_color[2] + 50))
    )
    pygame.draw.rect(surface, border_color, rect, width=2, border_radius=border_radius)
    
    # Draw text
    text_color = WHITE if sum(current_color) < 400 else BLACK
    text_surface = font_obj.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)
    
    return rect

def draw_health_bar_fancy(surface, x, y, width, height, current_hp, max_hp, 
                         bar_color=GREEN, bg_color=DARK_GRAY, border_color=WHITE):
    """Draw an enhanced health bar with gradients and animations."""
    percentage = current_hp / max_hp if max_hp > 0 else 0
    
    # Background
    bg_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, bg_color, bg_rect)
    
    # Health bar with gradient
    if percentage > 0:
        health_width = int(width * percentage)
        health_rect = pygame.Rect(x, y, health_width, height)
        
        # Color changes based on health percentage
        if percentage > 0.6:
            color1 = GREEN
            color2 = (0, 200, 0)
        elif percentage > 0.3:
            color1 = YELLOW
            color2 = (255, 200, 0)
        else:
            color1 = RED
            color2 = (200, 0, 0)
            
        draw_gradient_rect(surface, health_rect, color1, color2, vertical=False)
    
    # Border
    pygame.draw.rect(surface, border_color, bg_rect, width=2)
    
    # Health text
    health_text = f"{current_hp}/{max_hp}"
    text_surface = small_font.render(health_text, True, WHITE)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    
    # Text shadow
    shadow_surface = small_font.render(health_text, True, BLACK)
    surface.blit(shadow_surface, (text_rect.x + 1, text_rect.y + 1))
    surface.blit(text_surface, text_rect)

def create_particle_effect(x, y, color, count=10, speed_range=(1, 3)):
    """Create particle effect data for animations."""
    particles = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(*speed_range)
        particles.append({
            'x': x,
            'y': y,
            'vx': math.cos(angle) * speed,
            'vy': math.sin(angle) * speed,
            'life': 60,  # frames
            'max_life': 60,
            'color': color,
            'size': random.randint(2, 4)
        })
    return particles

def update_and_draw_particles(surface, particles):
    """Update and draw particle effects."""
    for particle in particles[:]:  # Use slice to avoid modification during iteration
        # Update position
        particle['x'] += particle['vx']
        particle['y'] += particle['vy']
        
        # Update life
        particle['life'] -= 1
        
        # Fade out
        life_ratio = particle['life'] / particle['max_life']
        alpha = int(255 * life_ratio)
        
        # Draw particle
        if particle['life'] > 0:
            color_with_alpha = (*particle['color'][:3], alpha)
            size = max(1, int(particle['size'] * life_ratio))
            pygame.draw.circle(surface, particle['color'], 
                             (int(particle['x']), int(particle['y'])), size)
        else:
            particles.remove(particle)

# Enhanced color scheme
ENHANCED_COLORS = {
    'primary_dark': (25, 30, 35),
    'primary_light': (45, 55, 65),
    'secondary_dark': (35, 25, 45),
    'secondary_light': (65, 45, 75),
    'accent_blue': (70, 130, 180),
    'accent_gold': (255, 215, 0),
    'accent_silver': (192, 192, 192),
    'success_green': (46, 125, 50),
    'warning_orange': (255, 152, 0),
    'danger_red': (211, 47, 47),
    'text_primary': (245, 245, 245),
    'text_secondary': (189, 189, 189),
    'text_disabled': (117, 117, 117),
    'background_dark': (15, 20, 25),
    'background_light': (35, 40, 45),
    'panel_dark': (40, 45, 50),
    'panel_light': (55, 60, 65),
    'button_normal': (40, 45, 50),
    'button_hover': (55, 60, 65),
    'button_selected': (70, 130, 180)
}

# Animation system
class AnimationManager:
    def __init__(self):
        self.animations = []
        self.particles = []
    
    def add_fade_in(self, duration, callback=None):
        """Add a fade-in animation."""
        self.animations.append({
            'type': 'fade_in',
            'duration': duration,
            'current': 0,
            'callback': callback
        })
    
    def add_slide_in(self, start_pos, end_pos, duration, callback=None):
        """Add a slide-in animation."""
        self.animations.append({
            'type': 'slide_in',
            'start_pos': start_pos,
            'end_pos': end_pos,
            'duration': duration,
            'current': 0,
            'callback': callback
        })
    
    def add_particles(self, x, y, color, count=10):
        """Add particle effect."""
        new_particles = create_particle_effect(x, y, color, count)
        self.particles.extend(new_particles)
    
    def update(self):
        """Update all animations."""
        for anim in self.animations[:]:
            anim['current'] += 1
            if anim['current'] >= anim['duration']:
                if anim.get('callback'):
                    anim['callback']()
                self.animations.remove(anim)
    
    def get_fade_alpha(self, anim_type='fade_in'):
        """Get current fade alpha value."""
        for anim in self.animations:
            if anim['type'] == anim_type:
                progress = anim['current'] / anim['duration']
                return int(255 * progress)
        return 255
    
    def get_slide_position(self, anim_type='slide_in'):
        """Get current slide position."""
        for anim in self.animations:
            if anim['type'] == anim_type:
                progress = anim['current'] / anim['duration']
                # Smooth easing
                progress = progress * progress * (3.0 - 2.0 * progress)  # Smoothstep
                start_x, start_y = anim['start_pos']
                end_x, end_y = anim['end_pos']
                current_x = lerp(start_x, end_x, progress)
                current_y = lerp(start_y, end_y, progress)
                return (current_x, current_y)
        return None
    
    def draw_particles(self, surface):
        """Draw all particles."""
        update_and_draw_particles(surface, self.particles)

# Initialize animation manager
animation_manager = AnimationManager()

# Mouse hover tracking for buttons
button_hover_states = {}

def update_button_hover(button_id, rect, mouse_pos):
    """Update button hover state."""
    was_hovered = button_hover_states.get(button_id, False)
    is_hovered = rect.collidepoint(mouse_pos)
    
    if is_hovered and not was_hovered:
        # Just started hovering
        play_sound("button_hover", 0.3)
    
    button_hover_states[button_id] = is_hovered
    return is_hovered

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
    "combat_asgore": "Dummy!_music.ogg"
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
    # Priority order for Undertale enemies: boss > strong > medium > weak
    enemy_types = [enemy.enemy_type for enemy in enemies]
    
    # Boss enemies
    if any(boss in enemy_types for boss in ["asgore", "undyne", "mettaton", "papyrus", "toriel"]):
        return "combat_asgore"
    # Strong enemies
    elif any(strong in enemy_types for strong in ["mad_dummy", "lesser_dog", "greater_dog", "muffet", "alphys"]):
        return "combat_troll"
    # Medium enemies
    elif any(medium in enemy_types for medium in ["pyrope", "vulkin", "tsunderplane", "temmie", "napstablook", "sans"]):
        return "combat_orc"
    # Weak enemies
    elif any(weak in enemy_types for weak in ["dummy", "froggit", "whimsun", "vegetoid", "moldsmal", "loox"]):
        return "combat_goblin"
    else:
        return "combat_goblin"  # Default fallback

def play_sound(sound_name, volume=1.0):
    """Play a sound effect if it exists."""
    if sound_name in sounds and sounds[sound_name]:
        sound = sounds[sound_name]
        # Apply global sound volume setting
        final_volume = volume * game_settings["sound_volume"]
        sound.set_volume(final_volume)
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
    "warrior": {"hp": 100, "attack": 12, "defense": 8, "icon": UI["warrior"], "weapon": "Sword", "mana": 0},
    "mage": {"hp": 70, "attack": 15, "defense": 4, "icon": UI["mage"], "weapon": "Staff", "mana": 20},
    "archer": {"hp": 85, "attack": 10, "defense": 6, "icon": UI["archer"], "weapon": "Bow", "mana": 0}
}

# --- Enemy Types ---
ENEMIES = {
    # Early game enemies (Levels 1-2)
    "dummy": {"hp": 30, "attack": 8, "defense": 2, "xp": 10, "icon": UI["goblin"]},
    "froggit": {"hp": 40, "attack": 10, "defense": 4, "xp": 15, "icon": UI["goblin"]}, 
    "whimsun": {"hp": 35, "attack": 9, "defense": 3, "xp": 12, "icon": UI["goblin"]},
    
    # Mid game enemies (Levels 2-3)  
    "loox": {"hp": 60, "attack": 14, "defense": 5, "xp": 20, "icon": UI["orc"]},
    "vegetoid": {"hp": 70, "attack": 16, "defense": 6, "xp": 25, "icon": UI["orc"]},
    "moldsmal": {"hp": 50, "attack": 12, "defense": 4, "xp": 18, "icon": UI["orc"]},
    
    # Medium difficulty enemies (Levels 3-4)
    "pyrope": {"hp": 85, "attack": 18, "defense": 7, "xp": 30, "icon": UI["troll"]},
    "icecap": {"hp": 90, "attack": 20, "defense": 8, "xp": 35, "icon": UI["troll"]},
    "gyftrot": {"hp": 110, "attack": 22, "defense": 9, "xp": 40, "icon": UI["troll"]},
    
    # High level enemies (Levels 4-5)
    "pyrope": {"hp": 130, "attack": 25, "defense": 12, "xp": 50, "icon": UI["troll"]},
    "vulkin": {"hp": 140, "attack": 28, "defense": 14, "xp": 55, "icon": UI["troll"]},
    "tsunderplane": {"hp": 160, "attack": 30, "defense": 16, "xp": 65, "icon": UI["troll"]},
    "mad_dummy": {"hp": 150, "attack": 26, "defense": 13, "xp": 60, "icon": UI["troll"]},
    "lesser_dog": {"hp": 120, "attack": 24, "defense": 11, "xp": 48, "icon": UI["troll"]},
    "greater_dog": {"hp": 170, "attack": 29, "defense": 15, "xp": 70, "icon": UI["troll"]},
    
    # Special creature enemies
    "temmie": {"hp": 75, "attack": 15, "defense": 8, "xp": 35, "icon": UI["orc"]},
    "muffet": {"hp": 180, "attack": 26, "defense": 12, "xp": 80, "icon": UI["troll"]},
    "napstablook": {"hp": 65, "attack": 12, "defense": 15, "xp": 30, "icon": UI["orc"]},
    "grillby": {"hp": 100, "attack": 20, "defense": 10, "xp": 45, "icon": UI["troll"]},
    "onionsan": {"hp": 95, "attack": 18, "defense": 12, "xp": 42, "icon": UI["troll"]},
    
    # Boss enemies (Level 5)
    "papyrus": {"hp": 200, "attack": 32, "defense": 18, "xp": 100, "icon": UI["dragon"]},
    "undyne": {"hp": 250, "attack": 36, "defense": 20, "xp": 120, "icon": UI["dragon"]},
    "sans": {"hp": 180, "attack": 40, "defense": 15, "xp": 150, "icon": UI["dragon"]},
    "mettaton": {"hp": 280, "attack": 35, "defense": 22, "xp": 180, "icon": UI["dragon"]},
    "flowey": {"hp": 350, "attack": 42, "defense": 25, "xp": 250, "icon": UI["dragon"]},
    
    # Ultimate bosses
    "toriel": {"hp": 220, "attack": 28, "defense": 16, "xp": 110, "icon": UI["dragon"]},
    "alphys": {"hp": 160, "attack": 24, "defense": 20, "xp": 85, "icon": UI["troll"]},
    "asgore": {"hp": 400, "attack": 45, "defense": 28, "xp": 300, "icon": UI["dragon"]},
    
    # Original enemies (balanced)
    "goblin": {"hp": 45, "attack": 10, "defense": 3, "xp": 15, "icon": UI["goblin"]},
    "orc": {"hp": 75, "attack": 16, "defense": 6, "xp": 25, "icon": UI["orc"]},
    "troll": {"hp": 120, "attack": 22, "defense": 10, "xp": 40, "icon": UI["troll"]},
    "dragon": {"hp": 300, "attack": 35, "defense": 18, "xp": 200, "icon": UI["dragon"]}
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
        self.direction = "down"  # Default direction for sprite display
        self.xp = 0
        self.level = 1
        self.gold = 100  # Starting gold for shopping
        
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
    def __init__(self, x, y, enemy_type, dungeon_level=1):
        base_hp = ENEMIES[enemy_type]["hp"]
        base_attack = ENEMIES[enemy_type]["attack"]
        base_defense = ENEMIES[enemy_type]["defense"]
        
        # Scale stats based on dungeon level (minor scaling to maintain balance)
        level_multiplier = 1.0 + (dungeon_level - 1) * 0.15  # 15% increase per level
        
        scaled_hp = int(base_hp * level_multiplier)
        scaled_attack = int(base_attack * level_multiplier)
        scaled_defense = int(base_defense * level_multiplier)
        
        super().__init__(x, y, enemy_type.capitalize(), scaled_hp, scaled_attack, scaled_defense, ENEMIES[enemy_type]["icon"])
        self.enemy_type = enemy_type  # Store the enemy type for music selection
        
        # Scale XP based on level as well
        base_xp = ENEMIES[enemy_type]["xp"]
        self.xp = int(base_xp * level_multiplier)
        self.weapon_drops = []  # List of possible weapon drops

class Shopkeeper:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.name = "Temmie"
        self.icon = "temmie"  # Use temmie sprite instead of emoji
        self.inventory = []  # Shop's inventory
        self.generate_shop_inventory()
    
    def generate_shop_inventory(self):
        """Generate random items for the shop."""
        self.inventory = []
        
        # Generate 4-6 items for sale
        num_items = random.randint(4, 6)
        
        for _ in range(num_items):
            item_type = random.choice(["weapon", "armor", "potion"])
            
            if item_type == "weapon":
                weapon = self.generate_random_weapon()
                if weapon:
                    self.inventory.append(weapon)
            elif item_type == "armor":
                armor = self.generate_random_armor()
                if armor:
                    self.inventory.append(armor)
            else:  # potion
                chosen_potion = random.choice(ALL_POTIONS)
                potion_copy = Potion(chosen_potion.name, chosen_potion.hp_gain, chosen_potion.rarity)
                self.inventory.append(potion_copy)
    
    def generate_random_weapon(self):
        """Generate a random weapon for the shop inventory."""
        available_weapons = ALL_WEAPONS
        if available_weapons:
            chosen_weapon = random.choice(available_weapons)
            return Weapon(chosen_weapon.name, chosen_weapon.attack_bonus, 
                         chosen_weapon.allowed_classes, chosen_weapon.rarity, 
                         chosen_weapon.sprite_name)
        return None
    
    def generate_random_armor(self):
        """Generate a random armor for the shop inventory."""
        available_armor = ALL_ARMOR
        if available_armor:
            chosen_armor = random.choice(available_armor)
            return Armor(chosen_armor.name, chosen_armor.defense_bonus,
                        chosen_armor.allowed_classes, chosen_armor.rarity,
                        chosen_armor.sprite_name)
        return None
    
    def get_item_price(self, item):
        """Calculate the price of an item based on its rarity and type."""
        base_price = 50  # Base price for common items
        
        # Price multipliers based on rarity
        rarity_multipliers = {
            "common": 1.0,
            "uncommon": 2.0,
            "rare": 4.0,
            "epic": 8.0
        }
        
        # Get item rarity
        if hasattr(item, 'rarity'):
            multiplier = rarity_multipliers.get(item.rarity, 1.0)
        else:
            multiplier = 1.0  # Default for potions
        
        # Different base prices for different item types
        if isinstance(item, Weapon):
            base_price = 75
        elif isinstance(item, Armor):
            base_price = 60
        elif isinstance(item, Potion):
            base_price = 25
        
        return int(base_price * multiplier)
    
    def sell_item_price(self, item):
        """Calculate how much the shop will pay for an item (50% of buy price)."""
        return self.get_item_price(item) // 2

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
        self.shopkeepers = []  # Shop NPCs
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
        chest_room_placed = False
        chest_room_attempts = 0
        
        for room_num in range(MAX_ROOMS):
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
            
            # Determine room type and place content accordingly
            room_type = self.determine_room_type(room_num, chest_room_placed, chest_room_attempts)
            if room_type == "shop_room":
                self.place_shop_room_content(new_room)
                self.shop_room_placed = True
            elif room_type == "chest_room":
                self.place_chest_room_content(new_room)
                chest_room_placed = True
            elif room_type == "treasure_room":
                self.place_treasure_room_content(new_room) 
                chest_room_attempts += 1
            else:
                self.place_content(new_room)
            
            self.rooms.append(new_room)
        
        # Ensure at least one chest room if none was placed (but only 25% chance - much rarer)
        if not chest_room_placed and self.rooms and random.random() < 0.25:
            # Convert a random middle room to a chest room
            room_idx = random.randint(1, len(self.rooms) - 2) if len(self.rooms) > 2 else 0
            chest_room = self.rooms[room_idx]
            # Clear existing content from this room
            self.clear_room_content(chest_room)
            self.place_chest_room_content(chest_room)
        
        if self.level < MAX_DUNGEON_LEVEL:
            last_room = self.rooms[-1]
            self.stairs_down = last_room.center()
            self.grid[self.stairs_down[1]][self.stairs_down[0]] = UI["stairs"]
        else: # Boss level
            boss_room = self.rooms[-1]
            boss_x, boss_y = boss_room.center()
            self.enemies.append(Enemy(boss_x, boss_y, "asgore", self.level))

    def determine_room_type(self, room_num, chest_room_placed, chest_room_attempts):
        """Determine what type of room to generate."""
        # Never make first or last room special (first = entrance, last = stairs/boss)
        if room_num == 0 or room_num >= MAX_ROOMS - 1:
            return "normal"
        
        # Shop room (15% chance, max 1 per level) - increased for better gameplay
        if not hasattr(self, 'shop_room_placed'):
            self.shop_room_placed = False
        if not self.shop_room_placed and random.random() < 0.15:
            return "shop_room"
        
        # One guaranteed chest room per level but much rarer (3% chance on each applicable room)
        if not chest_room_placed and random.random() < 0.03:
            return "chest_room"
        
        # Additional treasure rooms (reduced chance, 2% per room, max 1 per level)
        if chest_room_attempts < 1 and random.random() < 0.02:
            return "treasure_room"
        
        return "normal"

    def place_chest_room_content(self, room):
        """Place content for a special chest room - guaranteed multiple chests, no enemies."""
        room_size = (room.x2 - room.x1) * (room.y2 - room.y1)
        
        # Number of chests based on room size (2-4 chests)
        if room_size >= 60:  # Large room
            num_chests = random.randint(3, 4)
        elif room_size >= 35:  # Medium room  
            num_chests = random.randint(2, 3)
        else:  # Small room
            num_chests = 2
        
        # Place chests with guaranteed spacing
        chest_positions = []
        max_attempts = 50
        
        for _ in range(num_chests):
            attempts = 0
            while attempts < max_attempts:
                x = random.randint(room.x1 + 1, room.x2 - 1)
                y = random.randint(room.y1 + 1, room.y2 - 1)
                
                # Ensure minimum distance between chests
                too_close = False
                for chest_x, chest_y in chest_positions:
                    if abs(x - chest_x) <= 1 and abs(y - chest_y) <= 1:
                        too_close = True
                        break
                
                if not too_close:
                    chest_positions.append((x, y))
                    
                    # Generate higher-quality chest contents for chest rooms
                    chest_items = []
                    num_items = random.randint(2, 4)  # More items per chest
                    
                    for _ in range(num_items):
                        item_type = random.random()
                        if item_type < 0.45:  # 45% chance for weapon (slightly increased)
                            available_weapons = self.get_available_weapons_for_players()
                            if available_weapons:
                                # Reduced bias toward higher-tier weapons in chest rooms for balance
                                rarity_bonus = random.random()
                                if rarity_bonus < 0.15:  # Reduced from 30% to 15% chance for rare+ weapons
                                    rare_weapons = [w for w in available_weapons if w.rarity in ['rare', 'epic']]
                                    chosen_weapon = random.choice(rare_weapons) if rare_weapons else random.choice(available_weapons)
                                else:
                                    chosen_weapon = random.choice(available_weapons)
                                
                                weapon_copy = Weapon(chosen_weapon.name, chosen_weapon.attack_bonus, 
                                                   chosen_weapon.allowed_classes, chosen_weapon.rarity, 
                                                   chosen_weapon.sprite_name)
                                chest_items.append(weapon_copy)
                                # Mark as obtained for single player
                                self.mark_item_obtained(chosen_weapon.name)
                        elif item_type < 0.75:  # 30% chance for armor
                            available_armor = self.get_available_armor_for_players()
                            if available_armor:
                                # Reduced bias toward higher-tier armor in chest rooms for balance
                                rarity_bonus = random.random()
                                if rarity_bonus < 0.12:  # Reduced from 25% to 12% chance for rare+ armor
                                    rare_armor = [a for a in available_armor if a.rarity in ['rare', 'epic']]
                                    chosen_armor = random.choice(rare_armor) if rare_armor else random.choice(available_armor)
                                else:
                                    chosen_armor = random.choice(available_armor)
                                
                                armor_copy = Armor(chosen_armor.name, chosen_armor.defense_bonus,
                                                 chosen_armor.allowed_classes, chosen_armor.rarity,
                                                 chosen_armor.sprite_name)
                                chest_items.append(armor_copy)
                                # Mark as obtained for single player
                                self.mark_item_obtained(chosen_armor.name)
                        else:  # 25% chance for potion (reduced since more items per chest)
                            chosen_potion = random.choice(ALL_POTIONS)
                            potion_copy = Potion(chosen_potion.name, chosen_potion.hp_gain, chosen_potion.rarity)
                            chest_items.append(potion_copy)
                    
                    treasure = Treasure(x, y, chest_items)
                    self.treasures.append(treasure)
                    break
                
                attempts += 1

    def get_enemy_type_for_level(self):
        """Get an appropriate enemy type based on current dungeon level."""
        # Use Undertale enemy names based on level progression
        if self.level == 1:
            # Level 1: Weak enemies (80% weak, 20% medium)
            return random.choices(
                ['dummy', 'froggit', 'whimsun'],
                weights=[40, 30, 30]
            )[0]
        elif self.level == 2:
            # Level 2: Mix of weak and medium enemies
            return random.choices(
                ['froggit', 'whimsun', 'vegetoid', 'moldsmal', 'loox'],
                weights=[25, 25, 20, 15, 15]
            )[0]
        elif self.level == 3:
            # Level 3: Medium difficulty enemies
            return random.choices(
                ['vegetoid', 'loox', 'moldsmal', 'pyrope', 'vulkin'],
                weights=[25, 25, 25, 15, 10]
            )[0]
        elif self.level == 4:
            # Level 4: Stronger enemies
            return random.choices(
                ['pyrope', 'vulkin', 'tsunderplane', 'temmie', 'mad_dummy'],
                weights=[25, 25, 20, 15, 15]
            )[0]
        else:
            # Level 5+: Strong enemies and bosses
            return random.choices(
                ['mad_dummy', 'lesser_dog', 'greater_dog', 'papyrus', 'undyne', 'mettaton'],
                weights=[20, 15, 15, 20, 15, 15]
            )[0]

    def place_treasure_room_content(self, room):
        """Place content for a treasure room - higher chest chance, fewer enemies."""
        # Reduced enemy count for treasure rooms
        num_enemies = random.randint(0, 1)  # 0-1 instead of 0-3
        for _ in range(num_enemies):
            x = random.randint(room.x1 + 1, room.x2 - 1)
            y = random.randint(room.y1 + 1, room.y2 - 1)
            if not any(e.x == x and e.y == y for e in self.enemies):
                enemy_type = self.get_enemy_type_for_level()
                enemy = Enemy(x, y, enemy_type, self.level)
                
                # Same weapon drops as normal rooms
                if enemy_type in ["dummy", "froggit", "whimsun"]:
                    enemy.weapon_drops = [WARRIOR_WEAPONS[0], ARCHER_WEAPONS[0]]
                elif enemy_type in ["vegetoid", "moldsmal", "loox"]:
                    enemy.weapon_drops = WARRIOR_WEAPONS[1:3] + ARCHER_WEAPONS[1:2]
                elif enemy_type in ["pyrope", "vulkin", "tsunderplane", "temmie"]:
                    enemy.weapon_drops = WARRIOR_WEAPONS[3:5] + ALL_ARMOR[2:5]
                elif enemy_type in ["mad_dummy", "lesser_dog", "greater_dog", "papyrus", "undyne", "mettaton", "asgore"]:
                    enemy.weapon_drops = WARRIOR_WEAPONS[6:] + MAGE_WEAPONS[3:] + ARCHER_WEAPONS[3:]
                
                self.enemies.append(enemy)
        
        # Higher chance for treasure chests (60% instead of 25%)
        if random.random() < 0.60:
            chest_x = random.randint(room.x1 + 1, room.x2 - 1)
            chest_y = random.randint(room.y1 + 1, room.y2 - 1)
            
            # Generate better chest contents for treasure rooms
            chest_items = []
            num_items = random.randint(2, 3)  # Slightly more items
            
            for _ in range(num_items):
                item_type = random.random()
                if item_type < 0.42:  # 42% chance for weapon
                    available_weapons = self.get_available_weapons_for_players()
                    if available_weapons:
                        chosen_weapon = random.choice(available_weapons)
                        weapon_copy = Weapon(chosen_weapon.name, chosen_weapon.attack_bonus, 
                                           chosen_weapon.allowed_classes, chosen_weapon.rarity, 
                                           chosen_weapon.sprite_name)
                        chest_items.append(weapon_copy)
                        # Mark as obtained for single player
                        self.mark_item_obtained(chosen_weapon.name)
                elif item_type < 0.72:  # 30% chance for armor
                    available_armor = self.get_available_armor_for_players()
                    if available_armor:
                        chosen_armor = random.choice(available_armor)
                        armor_copy = Armor(chosen_armor.name, chosen_armor.defense_bonus,
                                         chosen_armor.allowed_classes, chosen_armor.rarity,
                                         chosen_armor.sprite_name)
                        chest_items.append(armor_copy)
                        # Mark as obtained for single player
                        self.mark_item_obtained(chosen_armor.name)
                else:  # 28% chance for potion
                    chosen_potion = random.choice(ALL_POTIONS)
                    potion_copy = Potion(chosen_potion.name, chosen_potion.hp_gain, chosen_potion.rarity)
                    chest_items.append(potion_copy)
            
            treasure = Treasure(chest_x, chest_y, chest_items)
            self.treasures.append(treasure)
        
        # Slightly increased ground loot for treasure rooms
        num_items = random.randint(0, 2)  # 0-2 instead of 0-1
        for _ in range(num_items):
            x = random.randint(room.x1 + 1, room.x2 - 1)
            y = random.randint(room.y1 + 1, room.y2 - 1)
            if not any(i.x == x and i.y == y for i in self.items):
                item_choice = random.random()
                if item_choice < 0.5:  # 50% potions (reduced from 60% to balance with chests)
                    chosen_potion = random.choice(ALL_POTIONS)
                    item = Potion(chosen_potion.name, chosen_potion.hp_gain, chosen_potion.rarity)
                elif item_choice < 0.75:  # 25% weapons
                    available_weapons = self.get_available_weapons_for_players()
                    if available_weapons:
                        chosen_weapon = random.choice(available_weapons)
                        item = Weapon(chosen_weapon.name, chosen_weapon.attack_bonus,
                                    chosen_weapon.allowed_classes, chosen_weapon.rarity,
                                    chosen_weapon.sprite_name)
                        # Mark as obtained for single player
                        self.mark_item_obtained(chosen_weapon.name)
                    else:
                        chosen_potion = random.choice(ALL_POTIONS)
                        item = Potion(chosen_potion.name, chosen_potion.hp_gain, chosen_potion.rarity)
                else:  # 25% armor
                    available_armor = self.get_available_armor_for_players()
                    if available_armor:
                        chosen_armor = random.choice(available_armor)
                        item = Armor(chosen_armor.name, chosen_armor.defense_bonus,
                                   chosen_armor.allowed_classes, chosen_armor.rarity,
                                   chosen_armor.sprite_name)
                        # Mark as obtained for single player
                        self.mark_item_obtained(chosen_armor.name)
                    else:
                        chosen_potion = random.choice(ALL_POTIONS)
                        item = Potion(chosen_potion.name, chosen_potion.hp_gain, chosen_potion.rarity)
                
                item.x = x
                item.y = y
                self.items.append(item)

    def place_shop_room_content(self, room):
        """Place content for a shop room - shopkeeper with no enemies."""
        # Place shopkeeper at the center of the room
        center_x, center_y = room.center()
        shopkeeper = Shopkeeper(center_x, center_y)
        self.shopkeepers.append(shopkeeper)
        
        # No enemies in shop rooms for peaceful trading
        # No other items on the ground - everything sold by shopkeeper

    def clear_room_content(self, room):
        """Clear all enemies, items, treasures, and shopkeepers from a specific room."""
        # Remove enemies in this room
        self.enemies = [e for e in self.enemies if not (room.x1 < e.x < room.x2 and room.y1 < e.y < room.y2)]
        
        # Remove items in this room
        self.items = [i for i in self.items if not (room.x1 < i.x < room.x2 and room.y1 < i.y < room.y2)]
        
        # Remove treasures in this room
        self.treasures = [t for t in self.treasures if not (room.x1 < t.x < room.x2 and room.y1 < t.y < room.y2)]
        
        # Remove shopkeepers in this room
        self.shopkeepers = [s for s in self.shopkeepers if not (room.x1 < s.x < room.x2 and room.y1 < s.y < room.y2)]

    def place_content(self, room):
        # Normal room: balanced enemy and loot distribution with level-based enemy scaling
        
        # Scale enemy count based on level - early levels have more enemies but weaker
        if self.level == 1:
            num_enemies = random.randint(1, 4)  # More enemies on level 1 (mostly weak goblins)
        elif self.level == 2:
            num_enemies = random.randint(1, 3)  # Moderate enemy count
        else:
            num_enemies = random.randint(0, 3)  # Standard enemy count for higher levels
            
        for _ in range(num_enemies):
            x = random.randint(room.x1 + 1, room.x2 - 1)
            y = random.randint(room.y1 + 1, room.y2 - 1)
            if not any(e.x == x and e.y == y for e in self.enemies):
                enemy_type = self.get_enemy_type_for_level()
                enemy = Enemy(x, y, enemy_type, self.level)
                
                # Add weapon drops based on enemy type
                if enemy_type in ["dummy", "froggit", "whimsun"]:
                    enemy.weapon_drops = [WARRIOR_WEAPONS[0], ARCHER_WEAPONS[0]]  # Basic weapons
                elif enemy_type in ["vegetoid", "moldsmal", "loox"]:
                    enemy.weapon_drops = WARRIOR_WEAPONS[1:3] + ARCHER_WEAPONS[1:2]  # Intermediate weapons
                elif enemy_type in ["pyrope", "vulkin", "tsunderplane", "temmie"]:
                    enemy.weapon_drops = WARRIOR_WEAPONS[3:5] + ALL_ARMOR[2:5]  # Advanced weapons and armor
                elif enemy_type in ["mad_dummy", "lesser_dog", "greater_dog", "papyrus", "undyne", "mettaton", "asgore"]:
                    enemy.weapon_drops = WARRIOR_WEAPONS[6:] + MAGE_WEAPONS[3:] + ARCHER_WEAPONS[3:]  # Epic weapons
                
                self.enemies.append(enemy)
        
        # Balanced treasure chest placement (30% chance - increased from 25%)
        if random.random() < 0.30:
            chest_x = random.randint(room.x1 + 1, room.x2 - 1)
            chest_y = random.randint(room.y1 + 1, room.y2 - 1)
            
            # Generate balanced treasure chest contents
            chest_items = []
            num_items = random.randint(1, 3)
            
            for _ in range(num_items):
                item_type = random.random()
                if item_type < 0.35:  # 35% chance for weapon (reduced from 40% for balance)
                    available_weapons = self.get_available_weapons_for_players()
                    if available_weapons:
                        chosen_weapon = random.choice(available_weapons)
                        weapon_copy = Weapon(chosen_weapon.name, chosen_weapon.attack_bonus, 
                                           chosen_weapon.allowed_classes, chosen_weapon.rarity, 
                                           chosen_weapon.sprite_name)
                        chest_items.append(weapon_copy)
                        # Mark as obtained for single player
                        self.mark_item_obtained(chosen_weapon.name)
                elif item_type < 0.65:  # 30% chance for armor (same)
                    available_armor = self.get_available_armor_for_players()
                    if available_armor:
                        chosen_armor = random.choice(available_armor)
                        armor_copy = Armor(chosen_armor.name, chosen_armor.defense_bonus,
                                         chosen_armor.allowed_classes, chosen_armor.rarity,
                                         chosen_armor.sprite_name)
                        chest_items.append(armor_copy)
                        # Mark as obtained for single player
                        self.mark_item_obtained(chosen_armor.name)
                else:  # 35% chance for potion (increased from 30% to balance weapons)
                    chosen_potion = random.choice(ALL_POTIONS)
                    potion_copy = Potion(chosen_potion.name, chosen_potion.hp_gain, chosen_potion.rarity)
                    chest_items.append(potion_copy)
            
            treasure = Treasure(chest_x, chest_y, chest_items)
            self.treasures.append(treasure)
        
        # Adjusted ground item distribution (better balance)
        item_chance = random.random()
        if item_chance < 0.70:  # 70% chance for ground loot (increased from ~50%)
            num_items = 1 if item_chance < 0.45 else 2 if item_chance < 0.60 else 1  # Weighted toward 1 item
            
            for _ in range(num_items):
                x = random.randint(room.x1 + 1, room.x2 - 1)
                y = random.randint(room.y1 + 1, room.y2 - 1)
                if not any(i.x == x and i.y == y for i in self.items) and not any(t.x == x and t.y == y for t in self.treasures):
                    item_choice = random.random()
                    if item_choice < 0.55:  # 55% potions (reduced from 60% for better balance)
                        chosen_potion = random.choice(ALL_POTIONS)
                        item = Potion(chosen_potion.name, chosen_potion.hp_gain, chosen_potion.rarity)
                    elif item_choice < 0.75:  # 20% weapons (increased from ~18% in old system)
                        available_weapons = self.get_available_weapons_for_players()
                        if available_weapons:
                            chosen_weapon = random.choice(available_weapons)
                            item = Weapon(chosen_weapon.name, chosen_weapon.attack_bonus,
                                        chosen_weapon.allowed_classes, chosen_weapon.rarity,
                                        chosen_weapon.sprite_name)
                            # Mark as obtained for single player
                            self.mark_item_obtained(chosen_weapon.name)
                        else:
                            chosen_potion = random.choice(ALL_POTIONS)
                            item = Potion(chosen_potion.name, chosen_potion.hp_gain, chosen_potion.rarity)
                    else:  # 25% armor (increased from ~20% in old system)
                        available_armor = self.get_available_armor_for_players()
                        if available_armor:
                            chosen_armor = random.choice(available_armor)
                            item = Armor(chosen_armor.name, chosen_armor.defense_bonus,
                                       chosen_armor.allowed_classes, chosen_armor.rarity,
                                       chosen_armor.sprite_name)
                            # Mark as obtained for single player
                            self.mark_item_obtained(chosen_armor.name)
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
                # Level-based rarity restrictions
                if not self.is_weapon_available_for_level(weapon):
                    continue
                    
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
                # Level-based rarity restrictions
                if not self.is_armor_available_for_level(armor):
                    continue
                    
                # Check if this is single player and item hasn't been obtained
                if hasattr(self, 'is_single_player') and self.is_single_player:
                    if armor.name not in self.obtained_items:
                        available.append(armor)
                else:
                    available.append(armor)
        return available
    
    def is_weapon_available_for_level(self, weapon):
        """Check if weapon rarity is appropriate for current dungeon level."""
        if weapon.rarity == "common":
            return True  # Always available
        elif weapon.rarity == "uncommon":
            return self.level >= 2  # Level 2+
        elif weapon.rarity == "rare":
            return self.level >= 3  # Level 3+
        elif weapon.rarity == "epic":
            return self.level >= 4  # Level 4+ only
        return True
    
    def is_armor_available_for_level(self, armor):
        """Check if armor rarity is appropriate for current dungeon level."""
        if armor.rarity == "common":
            return True  # Always available
        elif armor.rarity == "uncommon":
            return self.level >= 2  # Level 2+
        elif armor.rarity == "rare":
            return self.level >= 3  # Level 3+
        elif armor.rarity == "epic":
            return self.level >= 4  # Level 4+ only
        return True
    
    def mark_item_obtained(self, item_name):
        """Mark an item as obtained (for single player duplicate prevention)."""
        if hasattr(self, 'is_single_player') and self.is_single_player:
            self.obtained_items.add(item_name)

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
        # Camera system with smooth movement
        self.camera_x = 0
        self.camera_y = 0
        self.target_camera_x = 0
        self.target_camera_y = 0
        self.camera_speed = 0.1  # Smooth camera following speed
        self.clock = pygame.time.Clock()  # For frame rate limiting
        # Inventory system
        self.inventory_state = "closed"  # closed, open, selecting
        self.selected_player_idx = 0
        self.selected_item_idx = 0
        # Shop system
        self.shop_state = "closed"  # closed, open, buying, selling
        self.current_shopkeeper = None
        self.shop_mode = "buy"  # buy or sell
        self.selected_shop_item_idx = 0
        # Item replacement system
        self.pending_replacement = None
    def draw_combat_screen(self):
        """Draw the enhanced combat screen with improved visuals."""
        # Enhanced background with battle atmosphere
        bg_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        draw_gradient_rect(screen, bg_rect, ENHANCED_COLORS['background_dark'], (40, 20, 20))  # Dark red tint for combat
        
        # Update animations
        animation_manager.update()
        
        # Combat title with dramatic effect
        title_y = 30
        title_bg_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, title_y - 10, 240, 60)
        draw_gradient_rect(screen, title_bg_rect, ENHANCED_COLORS['danger_red'], (150, 30, 30))
        pygame.draw.rect(screen, ENHANCED_COLORS['accent_gold'], title_bg_rect, width=3, border_radius=8)
        
        draw_text_with_shadow(screen, "⚔️ BATTLE ⚔️", SCREEN_WIDTH // 2 - 100, title_y, 
                            ENHANCED_COLORS['accent_gold'], shadow_offset=3)
        
        # Combat turn indicator
        current_entity = self.turn_order[self.combat_turn_idx]
        turn_text = f"Turn: {current_entity.name}"
        turn_surface = small_font.render(turn_text, True, ENHANCED_COLORS['text_primary'])
        turn_rect = turn_surface.get_rect(center=(SCREEN_WIDTH // 2, title_y + 70))
        screen.blit(turn_surface, turn_rect)
        
        # Enhanced players section
        player_section_x = 50
        player_section_y = 150
        
        # Player panel background
        player_panel_rect = pygame.Rect(player_section_x - 20, player_section_y - 30, 600, 
                                       len(self.players) * 120 + 80)  # Extra space for title
        draw_gradient_rect(screen, player_panel_rect, ENHANCED_COLORS['panel_dark'], ENHANCED_COLORS['panel_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['success_green'], player_panel_rect, width=2, border_radius=10)
        
        # Section title
        draw_text_with_shadow(screen, "🛡️ Your Party", player_section_x, player_section_y - 10, 
                            ENHANCED_COLORS['success_green'])
        
        for i, player in enumerate(self.players):
            y_pos = player_section_y + 40 + i * 120  # More space between title and first player
            
            # Highlight current player's turn with glow effect
            is_current = player == current_entity
            
            if is_current:
                glow_rect = pygame.Rect(player_section_x - 10, y_pos - 10, 580, 110)
                draw_gradient_rect(screen, glow_rect, (255, 255, 0, 50), (255, 215, 0, 30))
                pygame.draw.rect(screen, ENHANCED_COLORS['accent_gold'], glow_rect, width=3, border_radius=8)
            
            # Player name and class with animated portraits and icons
            if game_settings['use_emojis']:
                status = f'{player.icon} {player.name} (Lv.{player.level})'
                # Draw static sprite as fallback
                class_sprite_key = f"player_{player.char_class}"
                if class_sprite_key in sprites:
                    screen.blit(sprites[class_sprite_key], (player_section_x, y_pos))
            else:
                class_sprite_key = f"player_{player.char_class}"
                # Try to draw animated portrait first, fallback to static sprite
                portrait_key = f"{player.char_class}_{player.direction}"  # Use player's actual direction
                if portrait_key in portrait_animations:
                    # Update and draw animated portrait
                    portrait_animations[portrait_key].update()
                    current_frame = portrait_animations[portrait_key].get_current_frame()
                    if current_frame:
                        # Scale portrait for combat display
                        portrait_scaled = pygame.transform.scale(current_frame, (TILE_SIZE, TILE_SIZE))
                        screen.blit(portrait_scaled, (player_section_x, y_pos))
                elif class_sprite_key in sprites:
                    screen.blit(sprites[class_sprite_key], (player_section_x, y_pos))
                status = f'{player.name} (Lv.{player.level}, {player.char_class.title()})'
            
            text_color = ENHANCED_COLORS['accent_gold'] if is_current else ENHANCED_COLORS['text_primary']
            draw_text_with_shadow(screen, status, player_section_x + 60, y_pos, text_color)
            
            # Enhanced health bar
            hp_bar_y = y_pos + 30
            draw_health_bar_fancy(screen, player_section_x + 60, hp_bar_y, 200, 25, 
                                player.hp, player.max_hp)
            
            # Mana bar for mages
            if player.char_class == "mage":
                mana_bar_y = y_pos + 60
                mana_percentage = player.mana / player.max_mana if player.max_mana > 0 else 0
                
                # Mana bar background
                mana_bg_rect = pygame.Rect(player_section_x + 60, mana_bar_y, 200, 20)
                pygame.draw.rect(screen, DARK_GRAY, mana_bg_rect)
                
                # Mana bar fill with gradient
                if mana_percentage > 0:
                    mana_width = int(200 * mana_percentage)
                    mana_rect = pygame.Rect(player_section_x + 60, mana_bar_y, mana_width, 20)
                    draw_gradient_rect(screen, mana_rect, BLUE, (0, 150, 255), vertical=False)
                
                pygame.draw.rect(screen, WHITE, mana_bg_rect, width=2)
                
                # Mana text
                mana_text = f"Mana: {player.mana}/{player.max_mana}"
                mana_surface = small_font.render(mana_text, True, ENHANCED_COLORS['text_primary'])
                mana_text_rect = mana_surface.get_rect(center=(player_section_x + 160, mana_bar_y + 10))
                screen.blit(mana_surface, mana_text_rect)
            
            # Enhanced skill icon and status
            skill_icon_x = player_section_x + 280
            skill_icon_y = y_pos + 25
            
            # Skill background panel
            skill_bg_rect = pygame.Rect(skill_icon_x - 5, skill_icon_y - 5, 280, 58)
            draw_gradient_rect(screen, skill_bg_rect, (30, 30, 40), (50, 50, 60))
            pygame.draw.rect(screen, ENHANCED_COLORS['accent_silver'], skill_bg_rect, width=1, border_radius=5)
            
            # Draw class skill icon
            if player.char_class == "warrior" and "skill_power_strike" in sprites:
                screen.blit(sprites["skill_power_strike"], (skill_icon_x, skill_icon_y))
            elif player.char_class == "mage" and "skill_fireball" in sprites:
                screen.blit(sprites["skill_fireball"], (skill_icon_x, skill_icon_y))
            elif player.char_class == "archer" and "skill_double_shot" in sprites:
                screen.blit(sprites["skill_double_shot"], (skill_icon_x, skill_icon_y))
            
            # Skill status text
            skill_text_x = skill_icon_x + 55
            if hasattr(player, 'skill_cooldown') and player.skill_cooldown > 0:
                cooldown_text = f"Cooldown: {player.skill_cooldown}"
                draw_text_with_shadow(screen, cooldown_text, skill_text_x, skill_icon_y + 5, 
                                    ENHANCED_COLORS['danger_red'], small_font, 1)
            else:
                skill_name = ""
                if player.char_class == "warrior":
                    skill_name = "Power Strike"
                elif player.char_class == "mage":
                    skill_name = "Fireball"
                elif player.char_class == "archer":
                    skill_name = "Double Shot"
                
                if skill_name and self.is_skill_available(player):
                    draw_text_with_shadow(screen, skill_name + " ✓", skill_text_x, skill_icon_y + 5, 
                                        ENHANCED_COLORS['success_green'], small_font, 1)
                elif skill_name:
                    level_req = 2 if player.char_class in ["warrior", "archer"] else 3
                    req_text = f"{skill_name} (Lv{level_req})"
                    draw_text_with_shadow(screen, req_text, skill_text_x, skill_icon_y + 5, 
                                        ENHANCED_COLORS['text_disabled'], small_font, 1)

        # Enhanced enemies section
        enemy_section_x = SCREEN_WIDTH - 550
        enemy_section_y = 150
        
        # Enemy panel background
        enemy_panel_rect = pygame.Rect(enemy_section_x - 20, enemy_section_y - 30, 520, 
                                      len(self.combat_enemies) * 100 + 60)
        draw_gradient_rect(screen, enemy_panel_rect, ENHANCED_COLORS['panel_dark'], (60, 40, 40))
        pygame.draw.rect(screen, ENHANCED_COLORS['danger_red'], enemy_panel_rect, width=2, border_radius=10)
        
        # Section title
        draw_text_with_shadow(screen, "⚔️ Enemies", enemy_section_x, enemy_section_y - 10, 
                            ENHANCED_COLORS['danger_red'])
        
        for i, enemy in enumerate(self.combat_enemies):
            y_pos = enemy_section_y + 20 + i * 100
            
            # Highlight current enemy's turn
            is_current = enemy == current_entity
            
            if is_current:
                glow_rect = pygame.Rect(enemy_section_x - 10, y_pos - 10, 500, 90)
                draw_gradient_rect(screen, glow_rect, (255, 0, 0, 50), (255, 100, 100, 30))
                pygame.draw.rect(screen, ENHANCED_COLORS['danger_red'], glow_rect, width=3, border_radius=8)
            
            # Enemy sprite and name with animated portraits
            if game_settings['use_emojis']:
                status = f'{enemy.icon} {enemy.name} (Lv.{self.dungeon_level})'
                # Draw static sprite as fallback
                enemy_sprite_key = f"monster_{enemy.enemy_type}"
                if enemy_sprite_key in sprites:
                    screen.blit(sprites[enemy_sprite_key], (enemy_section_x, y_pos))
            else:
                enemy_sprite_key = f"monster_{enemy.enemy_type}"
                # Try to draw animated portrait first, fallback to static sprite
                enemy_portrait_key = f"enemy_{enemy.enemy_type}"
                if enemy_portrait_key in portrait_animations:
                    # Update and draw animated portrait
                    portrait_animations[enemy_portrait_key].update()
                    current_frame = portrait_animations[enemy_portrait_key].get_current_frame()
                    if current_frame:
                        # Scale portrait for combat display - make enemies slightly larger
                        portrait_scaled = pygame.transform.scale(current_frame, (48, 48))
                        screen.blit(portrait_scaled, (enemy_section_x, y_pos))
                elif enemy_sprite_key in sprites:
                    screen.blit(sprites[enemy_sprite_key], (enemy_section_x, y_pos))
                status = f'{enemy.name} (Level {self.dungeon_level})'
            
            text_color = ENHANCED_COLORS['danger_red'] if is_current else ENHANCED_COLORS['text_primary']
            draw_text_with_shadow(screen, status, enemy_section_x + 60, y_pos, text_color)
            
            # Enhanced enemy health bar
            hp_bar_y = y_pos + 30
            draw_health_bar_fancy(screen, enemy_section_x + 60, hp_bar_y, 200, 25, 
                                enemy.hp, enemy.max_hp, bar_color=RED)
            
            # Enemy stats display
            stats_text = f"ATK: {enemy.attack} | DEF: {enemy.defense}"
            stats_surface = small_font.render(stats_text, True, ENHANCED_COLORS['text_secondary'])
            screen.blit(stats_surface, (enemy_section_x + 60, y_pos + 60))

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
        # Check level requirements first
        if player.char_class == "warrior" and player.level < 2:
            return False  # Power Strike requires level 2
        elif player.char_class == "mage" and player.level < 3:
            return False  # Fireball requires level 3
        elif player.char_class == "archer" and player.level < 2:
            return False  # Double Shot requires level 2
        
        # Check resource requirements
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
        """Draw the enhanced inventory management screen with better visuals."""
        # Enhanced background
        bg_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        draw_gradient_rect(screen, bg_rect, ENHANCED_COLORS['background_dark'], ENHANCED_COLORS['primary_dark'])
        
        # Update animations
        animation_manager.update()
        
        # Title with enhanced styling
        title_y = 30
        title_bg_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, title_y - 10, 300, 60)
        draw_gradient_rect(screen, title_bg_rect, ENHANCED_COLORS['panel_dark'], ENHANCED_COLORS['panel_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['accent_gold'], title_bg_rect, width=3, border_radius=10)
        
        draw_text_with_shadow(screen, "⚔️ INVENTORY ⚔️", SCREEN_WIDTH // 2 - 120, title_y, 
                            ENHANCED_COLORS['accent_gold'])
        
        # Enhanced instruction panel
        instruction_panel_rect = pygame.Rect(50, 110, 400, 180)
        draw_gradient_rect(screen, instruction_panel_rect, ENHANCED_COLORS['panel_dark'], ENHANCED_COLORS['panel_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['accent_silver'], instruction_panel_rect, width=2, border_radius=8)
        
        draw_text_with_shadow(screen, "Controls:", 70, 125, ENHANCED_COLORS['accent_silver'], small_font, 1)
        
        instructions = [
            "← → : Switch Player",
            "↑ ↓ : Navigate Items", 
            "ENTER : Use/Equip Item",
            "X : Drop Item",
            "Q : Quit to Menu",
            "I/ESC : Close Inventory"
        ]
        
        for i, instruction in enumerate(instructions):
            # Parse instruction for key highlighting
            if ":" in instruction:
                key_part, desc_part = instruction.split(":", 1)
                draw_text_with_shadow(screen, key_part, 80, 150 + i * 20, ENHANCED_COLORS['accent_gold'], 
                                    small_font, 1)
                draw_text_with_shadow(screen, ":" + desc_part, 80 + len(key_part) * 8, 150 + i * 20, 
                                    ENHANCED_COLORS['text_secondary'], small_font, 1)
            else:
                draw_text_with_shadow(screen, instruction, 80, 150 + i * 20, ENHANCED_COLORS['text_secondary'], 
                                    small_font, 1)
        
        # Enhanced player tabs
        tab_width = 250
        tab_height = 50
        tab_y = 320
        total_tabs_width = len(self.players) * tab_width + (len(self.players) - 1) * 20
        tab_start_x = (SCREEN_WIDTH - total_tabs_width) // 2
        
        for i, player in enumerate(self.players):
            tab_x = tab_start_x + i * (tab_width + 20)
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width, tab_height)
            
            # Tab styling
            is_selected = i == self.selected_player_idx
            
            if is_selected:
                # Selected tab with glow
                glow_rect = pygame.Rect(tab_x - 5, tab_y - 5, tab_width + 10, tab_height + 10)
                draw_gradient_rect(screen, glow_rect, ENHANCED_COLORS['accent_gold'], (200, 170, 0))
                draw_gradient_rect(screen, tab_rect, ENHANCED_COLORS['accent_blue'], (50, 100, 150))
                pygame.draw.rect(screen, ENHANCED_COLORS['accent_gold'], tab_rect, width=3, border_radius=8)
                text_color = WHITE
            else:
                # Unselected tab
                draw_gradient_rect(screen, tab_rect, ENHANCED_COLORS['panel_dark'], ENHANCED_COLORS['panel_light'])
                pygame.draw.rect(screen, ENHANCED_COLORS['text_disabled'], tab_rect, width=2, border_radius=8)
                text_color = ENHANCED_COLORS['text_secondary']
            
            # Player character sprite
            if not game_settings['use_emojis']:
                class_sprite_key = f"player_{player.char_class}"
                if class_sprite_key in sprites:
                    sprite_rect = sprites[class_sprite_key].get_rect(center=(tab_x + 30, tab_y + 25))
                    screen.blit(sprites[class_sprite_key], sprite_rect)
            
            # Player info
            player_text = f"{player.icon if game_settings['use_emojis'] else ''} {player.name}"
            class_text = f"Lv.{player.level} {player.char_class.title()}"
            
            draw_text_with_shadow(screen, player_text, tab_x + (50 if not game_settings['use_emojis'] else 20), 
                                tab_y + 8, text_color, font, 1)
            draw_text_with_shadow(screen, class_text, tab_x + (50 if not game_settings['use_emojis'] else 20), 
                                tab_y + 28, text_color, small_font, 1)
        
        # Current player's inventory panel
        current_player = self.players[self.selected_player_idx]
        inventory_panel_rect = pygame.Rect(100, 400, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 450)
        draw_gradient_rect(screen, inventory_panel_rect, ENHANCED_COLORS['panel_dark'], ENHANCED_COLORS['panel_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['accent_blue'], inventory_panel_rect, width=3, border_radius=10)
        
        # Player detailed stats panel
        stats_panel_rect = pygame.Rect(120, 420, 300, 120)
        draw_gradient_rect(screen, stats_panel_rect, ENHANCED_COLORS['primary_dark'], ENHANCED_COLORS['primary_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['success_green'], stats_panel_rect, width=2, border_radius=6)
        
        draw_text_with_shadow(screen, f"{current_player.name}", 140, 435, ENHANCED_COLORS['accent_gold'], font, 1)
        draw_text_with_shadow(screen, f"Level {current_player.level} {current_player.char_class.title()}", 
                            140, 460, ENHANCED_COLORS['text_primary'], small_font, 1)
        draw_text_with_shadow(screen, f"HP: {current_player.hp}/{current_player.max_hp}", 
                            140, 480, GREEN if current_player.hp == current_player.max_hp else RED, small_font, 1)
        draw_text_with_shadow(screen, f"ATK: {current_player.attack} | DEF: {current_player.defense}", 
                            140, 500, ENHANCED_COLORS['text_secondary'], small_font, 1)
        
        # Gold display
        draw_text_with_shadow(screen, f"💰 Gold: {current_player.gold}", 
                            140, 520, ENHANCED_COLORS['accent_gold'], small_font, 1)
        
        if current_player.char_class == "mage":
            draw_text_with_shadow(screen, f"Mana: {current_player.mana}/{current_player.max_mana}", 
                                140, 540, BLUE, small_font, 1)
        
        # Equipped items (positioned below the stats panel)
        equipped_y = 580  # Moved down to accommodate gold display
        draw_text_with_shadow(screen, "Equipped:", 140, equipped_y, ENHANCED_COLORS['accent_silver'], font, 1)
        
        weapon_text = f"Weapon: {current_player.weapon.name if current_player.weapon else 'None'}"
        weapon_color = ENHANCED_COLORS['success_green'] if current_player.weapon else ENHANCED_COLORS['text_disabled']
        draw_text_with_shadow(screen, weapon_text, 140, equipped_y + 30, weapon_color, small_font, 1)
        
        armor_text = f"Armor: {current_player.armor.name if current_player.armor else 'None'}"
        armor_color = ENHANCED_COLORS['success_green'] if current_player.armor else ENHANCED_COLORS['text_disabled']
        draw_text_with_shadow(screen, armor_text, 140, equipped_y + 50, armor_color, small_font, 1)
        
        # Categorized inventory items (positioned in the right side of the panel)
        items_start_x = 460
        items_y = 460
        
        # Separate items by category
        weapons = [item for item in current_player.inventory if isinstance(item, Weapon)]
        armor_items = [item for item in current_player.inventory if isinstance(item, Armor)]
        potions = [item for item in current_player.inventory if isinstance(item, Potion)]
        
        current_y = items_y
        item_index = 0
        
        # Draw Weapons category
        if weapons:
            weapon_count_text = f"⚔️ WEAPONS ({len(weapons)}/{current_player.max_weapons}):"
            draw_text_with_shadow(screen, weapon_count_text, items_start_x, current_y, ENHANCED_COLORS['accent_gold'], small_font, 1)
            current_y += 35
            for item in weapons:
                self.draw_inventory_item(item, item_index, current_y, current_player)
                current_y += 30
                item_index += 1
            current_y += 10
        else:
            weapon_count_text = f"⚔️ WEAPONS (0/{current_player.max_weapons}): Empty"
            draw_text_with_shadow(screen, weapon_count_text, items_start_x, current_y, ENHANCED_COLORS['text_disabled'], small_font, 1)
            current_y += 45
        
        # Draw Armor category
        if armor_items:
            armor_count_text = f"🛡️ ARMOR ({len(armor_items)}/{current_player.max_armor}):"
            draw_text_with_shadow(screen, armor_count_text, items_start_x, current_y, ENHANCED_COLORS['accent_gold'], small_font, 1)
            current_y += 35
            for item in armor_items:
                self.draw_inventory_item(item, item_index, current_y, current_player)
                current_y += 30
                item_index += 1
            current_y += 10
        else:
            armor_count_text = f"🛡️ ARMOR (0/{current_player.max_armor}): Empty"
            draw_text_with_shadow(screen, armor_count_text, items_start_x, current_y, ENHANCED_COLORS['text_disabled'], small_font, 1)
            current_y += 45
        
        # Draw Consumables category
        if potions:
            potion_count_text = f"🧪 CONSUMABLES ({len(potions)}/{current_player.max_potions}):"
            draw_text_with_shadow(screen, potion_count_text, items_start_x, current_y, ENHANCED_COLORS['accent_gold'], small_font, 1)
            current_y += 35
            for item in potions:
                self.draw_inventory_item(item, item_index, current_y, current_player)
                current_y += 30
                item_index += 1
        else:
            potion_count_text = f"🧪 CONSUMABLES (0/{current_player.max_potions}): Empty"
            draw_text_with_shadow(screen, potion_count_text, items_start_x, current_y, ENHANCED_COLORS['text_disabled'], small_font, 1)
            current_y += 45
        
        # Show inventory management instructions
        if current_y < SCREEN_HEIGHT - 100:
            draw_text_with_shadow(screen, "Inventory Limits: Weapons/Armor have limited slots", 
                                140, current_y + 20, ENHANCED_COLORS['text_secondary'], small_font, 1)
            draw_text_with_shadow(screen, "Better items will auto-replace when looting chests", 
                                140, current_y + 40, ENHANCED_COLORS['text_secondary'], small_font, 1)
        
        pygame.display.flip()
    
    def draw_inventory_item(self, item, item_index, y_pos, player):
        """Draw a single inventory item with proper highlighting and stats."""
        items_start_x = 460  # Match the x position used for categories
        
        # Highlight selected item
        is_selected_item = item_index == self.selected_item_idx
        if is_selected_item:
            highlight_rect = pygame.Rect(items_start_x - 10, y_pos - 5, 350, 28)
            draw_gradient_rect(screen, highlight_rect, ENHANCED_COLORS['accent_gold'], (200, 170, 0))
            pygame.draw.rect(screen, ENHANCED_COLORS['accent_gold'], highlight_rect, width=2, border_radius=5)
        
        # Item color based on equipment status and class compatibility
        if isinstance(item, Weapon):
            if item == player.weapon:
                item_color = ENHANCED_COLORS['success_green']  # Equipped weapon
            elif not item.can_use(player.char_class):
                item_color = ENHANCED_COLORS['text_disabled']  # Cannot use
            else:
                item_color = ENHANCED_COLORS['text_primary']
        elif isinstance(item, Armor):
            if item == player.armor:
                item_color = ENHANCED_COLORS['success_green']  # Equipped armor
            elif not item.can_use(player.char_class):
                item_color = ENHANCED_COLORS['text_disabled']  # Cannot use
            else:
                item_color = ENHANCED_COLORS['text_primary']
        else:
            item_color = ENHANCED_COLORS['text_primary']
        
        # Draw item with rarity color border
        rarity_colors = {
            "common": ENHANCED_COLORS['text_primary'],
            "uncommon": ENHANCED_COLORS['success_green'],
            "rare": ENHANCED_COLORS['accent_blue'],
            "epic": (128, 0, 128)  # Purple
        }
        
        if hasattr(item, 'rarity'):
            # Small colored square to indicate rarity
            rarity_color = rarity_colors.get(item.rarity, ENHANCED_COLORS['text_primary'])
            pygame.draw.rect(screen, rarity_color, (items_start_x - 5, y_pos + 5, 8, 8))
        
        # Draw item sprite if available and not in emoji mode
        sprite_x = items_start_x + 15
        text_x = sprite_x
        
        if not game_settings['use_emojis']:
            sprite_key = None
            
            # Determine sprite key based on item type
            if isinstance(item, Weapon) and hasattr(item, 'sprite_name') and item.sprite_name:
                sprite_key = f"weapon_{item.sprite_name}"
            elif isinstance(item, Armor) and hasattr(item, 'sprite_name') and item.sprite_name:
                sprite_key = f"armor_{item.sprite_name}"
            elif isinstance(item, Potion):
                sprite_key = "item_potion"
            
            # Draw the sprite if available
            if sprite_key and sprite_key in sprites:
                # Scale sprite to fit in inventory (smaller than tile size)
                sprite_size = 24  # Smaller than TILE_SIZE for inventory
                item_sprite = pygame.transform.scale(sprites[sprite_key], (sprite_size, sprite_size))
                screen.blit(item_sprite, (sprite_x, y_pos - 2))
                text_x = sprite_x + sprite_size + 5  # Move text to the right of sprite
        
        # Item icon and name
        if game_settings['use_emojis']:
            item_text = f"{item.icon} {item.name}"
        else:
            item_text = f"{item.name}"
        
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
        
        draw_text_with_shadow(screen, item_text, text_x, y_pos, item_color, small_font, 1)

    def add_message(self, text):
        self.messages.appendleft(text)
    
    def draw_shop_screen(self):
        """Draw the shop interface for buying and selling items."""
        # Enhanced background
        bg_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        draw_gradient_rect(screen, bg_rect, ENHANCED_COLORS['background_dark'], ENHANCED_COLORS['background_light'])
        
        # Shop title
        title_y = 20
        title_bg_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, title_y - 10, 300, 60)
        draw_gradient_rect(screen, title_bg_rect, ENHANCED_COLORS['panel_dark'], ENHANCED_COLORS['panel_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['accent_gold'], title_bg_rect, width=3, border_radius=10)
        
        draw_text_with_shadow(screen, "🏪 SHOP 🏪", SCREEN_WIDTH // 2 - 100, title_y, 
                            ENHANCED_COLORS['accent_gold'])
        
        # Shop mode tabs (Buy/Sell) - Enhanced visual indication
        tab_y = 100
        buy_tab_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, tab_y, 140, 50)
        sell_tab_rect = pygame.Rect(SCREEN_WIDTH // 2 - 10, tab_y, 140, 50)
        
        # Draw tabs with enhanced visual feedback
        if self.shop_mode == "buy":
            draw_gradient_rect(screen, buy_tab_rect, ENHANCED_COLORS['accent_gold'], (200, 170, 0))
            pygame.draw.rect(screen, ENHANCED_COLORS['accent_gold'], buy_tab_rect, width=3, border_radius=8)
            draw_gradient_rect(screen, sell_tab_rect, ENHANCED_COLORS['panel_dark'], ENHANCED_COLORS['panel_light'])
            pygame.draw.rect(screen, ENHANCED_COLORS['text_disabled'], sell_tab_rect, width=2, border_radius=8)
        else:
            draw_gradient_rect(screen, sell_tab_rect, ENHANCED_COLORS['accent_gold'], (200, 170, 0))
            pygame.draw.rect(screen, ENHANCED_COLORS['accent_gold'], sell_tab_rect, width=3, border_radius=8)
            draw_gradient_rect(screen, buy_tab_rect, ENHANCED_COLORS['panel_dark'], ENHANCED_COLORS['panel_light'])
            pygame.draw.rect(screen, ENHANCED_COLORS['text_disabled'], buy_tab_rect, width=2, border_radius=8)
        
        draw_text_with_shadow(screen, "BUY", SCREEN_WIDTH // 2 - 120, tab_y + 15, 
                            ENHANCED_COLORS['text_primary'], font, 1)
        draw_text_with_shadow(screen, "SELL", SCREEN_WIDTH // 2 + 20, tab_y + 15, 
                            ENHANCED_COLORS['text_primary'], font, 1)
        
        # TAB key instruction prominently displayed
        tab_instruction_y = tab_y + 60
        tab_bg_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, tab_instruction_y, 200, 30)
        draw_gradient_rect(screen, tab_bg_rect, (50, 50, 80), (70, 70, 100))
        pygame.draw.rect(screen, ENHANCED_COLORS['accent_gold'], tab_bg_rect, width=2, border_radius=6)
        draw_text_with_shadow(screen, "Press [TAB] to Switch", SCREEN_WIDTH // 2 - 85, tab_instruction_y + 5, 
                            ENHANCED_COLORS['accent_gold'], small_font, 1)
        
        # Instructions panel (moved down to accommodate TAB instruction)
        instruction_panel_rect = pygame.Rect(50, 200, 400, 150)
        draw_gradient_rect(screen, instruction_panel_rect, ENHANCED_COLORS['panel_dark'], ENHANCED_COLORS['panel_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['accent_silver'], instruction_panel_rect, width=2, border_radius=8)
        
        draw_text_with_shadow(screen, "Controls:", 70, 215, ENHANCED_COLORS['accent_silver'], small_font, 1)
        instructions = [
            "← → : Switch Player", 
            "↑ ↓ : Navigate Items",
            "ENTER : Buy/Sell Item",
            "ESC/Q : Close Shop"
        ]
        
        for i, instruction in enumerate(instructions):
            key_part, desc_part = instruction.split(":", 1)
            draw_text_with_shadow(screen, key_part.strip(), 70, 235 + i * 20, ENHANCED_COLORS['accent_gold'], small_font, 1)
            draw_text_with_shadow(screen, ":" + desc_part, 130, 235 + i * 20, ENHANCED_COLORS['text_secondary'], small_font, 1)
        
        # Current player info (adjusted position)
        current_player = self.players[self.selected_player_idx]
        player_panel_rect = pygame.Rect(500, 200, 300, 150)
        draw_gradient_rect(screen, player_panel_rect, ENHANCED_COLORS['primary_dark'], ENHANCED_COLORS['primary_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['success_green'], player_panel_rect, width=2, border_radius=6)
        
        draw_text_with_shadow(screen, f"{current_player.name}", 520, 215, ENHANCED_COLORS['accent_gold'], font, 1)
        draw_text_with_shadow(screen, f"Level {current_player.level} {current_player.char_class.title()}", 
                            520, 240, ENHANCED_COLORS['text_primary'], small_font, 1)
        draw_text_with_shadow(screen, f"Gold: {current_player.gold}", 520, 265, 
                            (255, 215, 0), font, 1)  # Gold color for gold amount
        draw_text_with_shadow(screen, f"HP: {current_player.hp}/{current_player.max_hp}", 
                            520, 290, GREEN if current_player.hp == current_player.max_hp else RED, small_font, 1)
        
        # Main shop panel
        shop_panel_rect = pygame.Rect(100, 350, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 400)
        draw_gradient_rect(screen, shop_panel_rect, ENHANCED_COLORS['panel_dark'], ENHANCED_COLORS['panel_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['accent_blue'], shop_panel_rect, width=3, border_radius=10)
        
        if self.shop_mode == "buy":
            self.draw_shop_buy_items(shop_panel_rect)
        else:
            self.draw_shop_sell_items(shop_panel_rect)
        
        pygame.display.flip()
    
    def draw_shop_buy_items(self, panel_rect):
        """Draw items available for purchase."""
        draw_text_with_shadow(screen, f"🛒 {self.current_shopkeeper.name}'s Wares", 
                            panel_rect.x + 20, panel_rect.y + 20, ENHANCED_COLORS['accent_gold'], font, 1)
        
        if not self.current_shopkeeper.inventory:
            draw_text_with_shadow(screen, "Shop is sold out!", panel_rect.x + 20, panel_rect.y + 60, 
                                ENHANCED_COLORS['text_disabled'], small_font, 1)
            return
        
        y_offset = 60
        for i, item in enumerate(self.current_shopkeeper.inventory):
            y_pos = panel_rect.y + y_offset + i * 40
            if y_pos > panel_rect.y + panel_rect.height - 40:
                break  # Don't draw items outside the panel
            
            # Highlight selected item
            if i == self.selected_shop_item_idx:
                highlight_rect = pygame.Rect(panel_rect.x + 10, y_pos - 5, panel_rect.width - 20, 35)
                draw_gradient_rect(screen, highlight_rect, ENHANCED_COLORS['accent_gold'], (200, 170, 0))
                pygame.draw.rect(screen, ENHANCED_COLORS['accent_gold'], highlight_rect, width=2, border_radius=5)
            
            # Draw item sprite if available
            sprite_x = panel_rect.x + 25
            text_x = sprite_x + 35
            
            if hasattr(item, 'sprite_name') and item.sprite_name:
                sprite_key = None
                if isinstance(item, Weapon):
                    sprite_key = f"weapon_{item.sprite_name}"
                elif isinstance(item, Armor):
                    sprite_key = f"armor_{item.sprite_name}"
                elif isinstance(item, Potion):
                    sprite_key = "item_potion"
                
                if sprite_key and sprite_key in sprites:
                    sprite = pygame.transform.scale(sprites[sprite_key], (24, 24))
                    screen.blit(sprite, (sprite_x, y_pos))
            
            # Item name and stats with affordability indicators
            price = self.current_shopkeeper.get_item_price(item)
            current_player = self.players[self.selected_player_idx]
            
            item_text = f"{item.name}"
            
            if isinstance(item, Weapon):
                item_text += f" (ATK +{item.attack_bonus}) - {price}g"
            elif isinstance(item, Armor):
                item_text += f" (DEF +{item.defense_bonus}) - {price}g"
            elif isinstance(item, Potion):
                item_text += f" (Heals {item.hp_gain} HP) - {price}g"
            
            # Color based on affordability and inventory space
            can_afford = current_player.gold >= price
            can_carry = current_player.can_carry_item(item)
            
            if not can_afford:
                text_color = ENHANCED_COLORS['danger_red']
                item_text += " [TOO EXPENSIVE]"
            elif not can_carry:
                text_color = ENHANCED_COLORS['warning_orange']
                item_text += " [INVENTORY FULL]"
            else:
                text_color = ENHANCED_COLORS['text_primary']
            
            draw_text_with_shadow(screen, item_text, text_x, y_pos, text_color, small_font, 1)
    
    def draw_shop_sell_items(self, panel_rect):
        """Draw player items available for sale."""
        current_player = self.players[self.selected_player_idx]
        draw_text_with_shadow(screen, f"💰 Sell {current_player.name}'s Items", 
                            panel_rect.x + 20, panel_rect.y + 20, ENHANCED_COLORS['accent_gold'], font, 1)
        
        if not current_player.inventory:
            draw_text_with_shadow(screen, "No items to sell!", panel_rect.x + 20, panel_rect.y + 60, 
                                ENHANCED_COLORS['text_disabled'], small_font, 1)
            return
        
        y_offset = 60
        for i, item in enumerate(current_player.inventory):
            y_pos = panel_rect.y + y_offset + i * 40
            if y_pos > panel_rect.y + panel_rect.height - 40:
                break  # Don't draw items outside the panel
            
            # Highlight selected item
            if i == self.selected_item_idx:
                highlight_rect = pygame.Rect(panel_rect.x + 10, y_pos - 5, panel_rect.width - 20, 35)
                draw_gradient_rect(screen, highlight_rect, ENHANCED_COLORS['accent_gold'], (200, 170, 0))
                pygame.draw.rect(screen, ENHANCED_COLORS['accent_gold'], highlight_rect, width=2, border_radius=5)
            
            # Draw item sprite if available
            sprite_x = panel_rect.x + 25
            text_x = sprite_x + 35
            
            if hasattr(item, 'sprite_name') and item.sprite_name:
                sprite_key = None
                if isinstance(item, Weapon):
                    sprite_key = f"weapon_{item.sprite_name}"
                elif isinstance(item, Armor):
                    sprite_key = f"armor_{item.sprite_name}"
                elif isinstance(item, Potion):
                    sprite_key = "item_potion"
                
                if sprite_key and sprite_key in sprites:
                    sprite = pygame.transform.scale(sprites[sprite_key], (24, 24))
                    screen.blit(sprite, (sprite_x, y_pos))
            
            # Item name and sell price
            price = self.current_shopkeeper.sell_item_price(item)
            item_text = f"{item.name}"
            
            if isinstance(item, Weapon):
                item_text += f" (ATK +{item.attack_bonus}) - {price}g"
            elif isinstance(item, Armor):
                item_text += f" (DEF +{item.defense_bonus}) - {price}g"
            elif isinstance(item, Potion):
                item_text += f" (Heals {item.hp_gain} HP) - {price}g"
            
            # Show if equipped (can't sell equipped items)
            is_equipped = hasattr(item, 'equipped') and item.equipped
            if is_equipped:
                item_text += " [EQUIPPED]"
            
            text_color = ENHANCED_COLORS['text_disabled'] if is_equipped else ENHANCED_COLORS['text_primary']
            
            draw_text_with_shadow(screen, item_text, text_x, y_pos, text_color, small_font, 1)
    
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
                    "gold": getattr(player, 'gold', 100),  # Save gold with default fallback
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
                player.gold = player_data.get("gold", 100)  # Load gold with default fallback
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
        """Update camera position with smooth following."""
        if self.players:
            player = self.players[0]  # Follow the first player
            
            # Calculate target camera position
            self.target_camera_x = player.x - VIEWPORT_WIDTH // 2
            self.target_camera_y = player.y - VIEWPORT_HEIGHT // 2
            
            # Keep target within dungeon bounds
            self.target_camera_x = max(0, min(self.target_camera_x, self.dungeon.width - VIEWPORT_WIDTH))
            self.target_camera_y = max(0, min(self.target_camera_y, self.dungeon.height - VIEWPORT_HEIGHT))
            
            # Smooth camera interpolation
            camera_diff_x = self.target_camera_x - self.camera_x
            camera_diff_y = self.target_camera_y - self.camera_y
            
            # If the difference is small enough, snap to target (prevents endless tiny movements)
            if abs(camera_diff_x) < 0.1:
                self.camera_x = self.target_camera_x
            else:
                self.camera_x += camera_diff_x * self.camera_speed
            
            if abs(camera_diff_y) < 0.1:
                self.camera_y = self.target_camera_y
            else:
                self.camera_y += camera_diff_y * self.camera_speed
            
            # Update fog of war for all players
            for p in self.players:
                self.dungeon.update_visibility(p.x, p.y)

    def draw_text(self, text, x, y, color=WHITE, padding=0):
        """Draw text with optional padding background."""
        text_surface = font.render(text, True, color)
        
        if padding > 0:
            # Create a padded background
            text_rect = text_surface.get_rect()
            padded_rect = pygame.Rect(x - padding, y - padding, 
                                    text_rect.width + padding * 2, 
                                    text_rect.height + padding * 2)
            
            # Semi-transparent dark background
            padding_surface = pygame.Surface((padded_rect.width, padded_rect.height))
            padding_surface.set_alpha(180)
            padding_surface.fill((0, 0, 0))
            screen.blit(padding_surface, (padded_rect.x, padded_rect.y))
        
        screen.blit(text_surface, (x, y))

    def main_menu(self):
        # Enhanced background with gradient
        bg_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        draw_gradient_rect(screen, bg_rect, ENHANCED_COLORS['background_dark'], ENHANCED_COLORS['primary_dark'])
        
        # Update animations
        animation_manager.update()
        
        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()
        
        # Animated title with shadow
        title_y = SCREEN_HEIGHT // 2 - 200
        title_x = SCREEN_WIDTH // 2 - 180
        
        # Title background panel
        title_bg_rect = pygame.Rect(title_x - 40, title_y - 20, 400, 80)
        draw_gradient_rect(screen, title_bg_rect, ENHANCED_COLORS['panel_dark'], ENHANCED_COLORS['panel_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['accent_gold'], title_bg_rect, width=3, border_radius=10)
        
        # Main title with enhanced text
        draw_text_with_shadow(screen, "Python RPG Adventure", title_x, title_y, ENHANCED_COLORS['accent_gold'])
        
        # Subtitle
        subtitle_text = "A Tale of Heroes and Dragons"
        subtitle_surface = small_font.render(subtitle_text, True, ENHANCED_COLORS['text_secondary'])
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, title_y + 50))
        screen.blit(subtitle_surface, subtitle_rect)
        
        # Menu options with fancy buttons
        menu_start_y = title_y + 120
        button_width = 300
        button_height = 50
        button_spacing = 60
        has_save = self.has_save_file()
        
        buttons = []
        if has_save:
            buttons = [
                ("continue", "Continue Game", "C"),
                ("new", "New Game", "N"),
                ("delete", "Delete Save", "D"),
                ("settings", "Settings", "S"),
                ("quit", "Quit", "Q")
            ]
        else:
            buttons = [
                ("start", "Start Adventure", "ENTER"),
                ("settings", "Settings", "S"),
                ("quit", "Quit", "Q")
            ]
        
        # Draw fancy buttons
        for i, (button_id, text, key) in enumerate(buttons):
            button_x = SCREEN_WIDTH // 2 - button_width // 2
            button_y = menu_start_y + i * button_spacing
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            # Determine colors based on button type
            if button_id == "continue":
                base_color = ENHANCED_COLORS['success_green']
                hover_color = (66, 165, 70)
                pressed_color = (26, 105, 30)
            elif button_id == "new" or button_id == "start":
                base_color = ENHANCED_COLORS['accent_blue']
                hover_color = (90, 150, 200)
                pressed_color = (50, 110, 160)
            elif button_id == "delete":
                base_color = ENHANCED_COLORS['danger_red']
                hover_color = (231, 67, 67)
                pressed_color = (191, 27, 27)
            elif button_id == "quit":
                base_color = ENHANCED_COLORS['text_disabled']
                hover_color = (137, 137, 137)
                pressed_color = (97, 97, 97)
            else:  # settings
                base_color = ENHANCED_COLORS['accent_gold']
                hover_color = (255, 235, 20)
                pressed_color = (235, 195, 0)
            
            # Check hover state
            is_hovered = update_button_hover(button_id, button_rect, mouse_pos)
            
            # Draw fancy button
            button_text = f"{text} ({key})"
            draw_fancy_button(screen, button_rect, button_text, font, 
                            base_color, hover_color, pressed_color, 
                            is_hovered=is_hovered, border_radius=12)
        
        # Game info panel at bottom
        info_panel_rect = pygame.Rect(50, SCREEN_HEIGHT - 120, SCREEN_WIDTH - 100, 70)
        draw_gradient_rect(screen, info_panel_rect, ENHANCED_COLORS['panel_dark'], ENHANCED_COLORS['panel_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['accent_silver'], info_panel_rect, width=2, border_radius=8)
        
        # Show current display mode and version info
        mode_text = "Display: " + ("Emoji Mode" if game_settings['use_emojis'] else "Sprite Mode")
        version_text = "Version 1.22 - UI Enhancement & Optimization Edition"
        
        mode_surface = small_font.render(mode_text, True, ENHANCED_COLORS['text_secondary'])
        version_surface = small_font.render(version_text, True, ENHANCED_COLORS['text_secondary'])
        
        screen.blit(mode_surface, (info_panel_rect.x + 20, info_panel_rect.y + 15))
        screen.blit(version_surface, (info_panel_rect.x + 20, info_panel_rect.y + 35))
        
        # Draw particles if any
        animation_manager.draw_particles(screen)
        
        pygame.display.flip()
        
        # Handle events with enhanced feedback
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            elif event.type == pygame.KEYDOWN:
                play_sound("menu_select", 0.5)  # Sound feedback
                
                if event.key == pygame.K_RETURN and not has_save:
                    animation_manager.add_particles(SCREEN_WIDTH // 2, menu_start_y, ENHANCED_COLORS['accent_blue'], 15)
                    self.reset_game_state()
                    self.game_state = "setup_num_players"
                elif event.key == pygame.K_n:
                    animation_manager.add_particles(SCREEN_WIDTH // 2, menu_start_y + button_spacing, ENHANCED_COLORS['accent_blue'], 15)
                    self.reset_game_state()
                    self.game_state = "setup_num_players"
                elif event.key == pygame.K_c and has_save:
                    animation_manager.add_particles(SCREEN_WIDTH // 2, menu_start_y, ENHANCED_COLORS['success_green'], 15)
                    if self.load_game():
                        self.game_state = "playing"
                    else:
                        self.add_message("Failed to load save file!")
                        play_sound("error", 0.7)
                elif event.key == pygame.K_d and has_save:
                    if self.delete_save_file():
                        animation_manager.add_particles(SCREEN_WIDTH // 2, menu_start_y + button_spacing * 2, ENHANCED_COLORS['danger_red'], 10)
                        self.add_message("Save file deleted!")
                        play_sound("success", 0.5)
                elif event.key == pygame.K_s:
                    animation_manager.add_particles(SCREEN_WIDTH // 2, menu_start_y + button_spacing * (3 if has_save else 1), ENHANCED_COLORS['accent_gold'], 12)
                    self.game_state = "settings_menu"
                elif event.key == pygame.K_q:
                    play_sound("menu_back", 0.5)
                    self.game_over = True

    def settings_menu(self):
        global game_settings
        # Enhanced background with gradient (matching main menu)
        bg_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        draw_gradient_rect(screen, bg_rect, ENHANCED_COLORS['background_dark'], ENHANCED_COLORS['primary_dark'])
        
        # Update animations
        animation_manager.update()
        
        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()
        
        # Animated title with shadow (matching main menu)
        title_y = SCREEN_HEIGHT // 2 - 250
        title_x = SCREEN_WIDTH // 2 - 120
        
        # Title background panel
        title_bg_rect = pygame.Rect(title_x - 40, title_y - 20, 320, 80)
        draw_gradient_rect(screen, title_bg_rect, ENHANCED_COLORS['panel_dark'], ENHANCED_COLORS['panel_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['accent_gold'], title_bg_rect, width=3, border_radius=10)
        
        # Main title with enhanced text
        draw_text_with_shadow(screen, "Game Settings", title_x, title_y, ENHANCED_COLORS['accent_gold'])
        
        # Settings panel
        panel_y = title_y + 100
        panel_width = SCREEN_WIDTH - 200
        panel_height = 420
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        draw_gradient_rect(screen, panel_rect, ENHANCED_COLORS['panel_dark'], ENHANCED_COLORS['panel_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['accent_silver'], panel_rect, width=2, border_radius=8)
        
        # Settings options
        settings_x = panel_x + 50
        start_y = panel_y + 30
        line_height = 50
        
        # 1. Resolution setting
        res_text = f"Resolution: {game_settings['resolution'][0]}x{game_settings['resolution'][1]}"
        if game_settings['fullscreen']:
            res_text += " (Fullscreen)"
        
        setting_rect_1 = pygame.Rect(settings_x - 20, start_y - 10, 250, 35)
        draw_gradient_rect(screen, setting_rect_1, ENHANCED_COLORS['button_normal'], ENHANCED_COLORS['button_hover'])
        draw_text_with_shadow(screen, "1.", settings_x - 10, start_y, ENHANCED_COLORS['accent_gold'])
        draw_text_with_shadow(screen, res_text, settings_x + 30, start_y, ENHANCED_COLORS['text_primary'])
        
        # 2. Music Volume
        music_vol = int(game_settings['music_volume'] * 100)
        setting_rect_2 = pygame.Rect(settings_x - 20, start_y + line_height - 10, 250, 35)
        draw_gradient_rect(screen, setting_rect_2, ENHANCED_COLORS['button_normal'], ENHANCED_COLORS['button_hover'])
        draw_text_with_shadow(screen, "2.", settings_x - 10, start_y + line_height, ENHANCED_COLORS['accent_gold'])
        draw_text_with_shadow(screen, f"Music Volume: {music_vol}%", settings_x + 30, start_y + line_height, ENHANCED_COLORS['text_primary'])
        
        # Enhanced volume bar for music
        bar_x = settings_x + 300
        bar_y = start_y + line_height + 5
        bar_width = 200
        bar_height = 20
        bar_bg_rect = pygame.Rect(bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4)
        draw_gradient_rect(screen, bar_bg_rect, ENHANCED_COLORS['panel_dark'], ENHANCED_COLORS['panel_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['accent_silver'], bar_bg_rect, width=1, border_radius=10)
        
        pygame.draw.rect(screen, ENHANCED_COLORS['background_dark'], (bar_x, bar_y, bar_width, bar_height), border_radius=8)
        fill_width = int(bar_width * game_settings['music_volume'])
        if fill_width > 0:
            pygame.draw.rect(screen, ENHANCED_COLORS['success_green'], (bar_x, bar_y, fill_width, bar_height), border_radius=8)
        
        # 3. Sound Volume  
        sound_vol = int(game_settings['sound_volume'] * 100)
        setting_rect_3 = pygame.Rect(settings_x - 20, start_y + line_height * 2 - 10, 250, 35)
        draw_gradient_rect(screen, setting_rect_3, ENHANCED_COLORS['button_normal'], ENHANCED_COLORS['button_hover'])
        draw_text_with_shadow(screen, "3.", settings_x - 10, start_y + line_height * 2, ENHANCED_COLORS['accent_gold'])
        draw_text_with_shadow(screen, f"Sound Volume: {sound_vol}%", settings_x + 30, start_y + line_height * 2, ENHANCED_COLORS['text_primary'])
        
        # Enhanced volume bar for sound
        bar_y = start_y + line_height * 2 + 5
        bar_bg_rect = pygame.Rect(bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4)
        draw_gradient_rect(screen, bar_bg_rect, ENHANCED_COLORS['panel_dark'], ENHANCED_COLORS['panel_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['accent_silver'], bar_bg_rect, width=1, border_radius=10)
        
        pygame.draw.rect(screen, ENHANCED_COLORS['background_dark'], (bar_x, bar_y, bar_width, bar_height), border_radius=8)
        fill_width = int(bar_width * game_settings['sound_volume'])
        if fill_width > 0:
            pygame.draw.rect(screen, ENHANCED_COLORS['accent_blue'], (bar_x, bar_y, fill_width, bar_height), border_radius=8)
        
        # 4. Display mode (emoji/sprite)
        emoji_status = "ON" if game_settings['use_emojis'] else "OFF"
        status_color = ENHANCED_COLORS['success_green'] if game_settings['use_emojis'] else ENHANCED_COLORS['danger_red']
        
        setting_rect_4 = pygame.Rect(settings_x - 20, start_y + line_height * 3 - 10, 350, 35)
        draw_gradient_rect(screen, setting_rect_4, ENHANCED_COLORS['button_normal'], ENHANCED_COLORS['button_hover'])
        draw_text_with_shadow(screen, "4.", settings_x - 10, start_y + line_height * 3, ENHANCED_COLORS['accent_gold'])
        draw_text_with_shadow(screen, f"Use Emojis: ", settings_x + 30, start_y + line_height * 3, ENHANCED_COLORS['text_primary'])
        draw_text_with_shadow(screen, emoji_status, settings_x + 160, start_y + line_height * 3, status_color)
        
        # Only show sprite options if not using emojis
        current_line = 4
        if not game_settings['use_emojis']:
            # 5. Wall Style
            wall_name = game_settings['wall_sprite'].replace('.png', '').replace('_', ' ').title()
            setting_rect_5 = pygame.Rect(settings_x - 20, start_y + line_height * current_line - 10, 250, 35)
            draw_gradient_rect(screen, setting_rect_5, ENHANCED_COLORS['button_normal'], ENHANCED_COLORS['button_hover'])
            draw_text_with_shadow(screen, "5.", settings_x - 10, start_y + line_height * current_line, ENHANCED_COLORS['accent_gold'])
            draw_text_with_shadow(screen, f"Wall Style: {wall_name}", settings_x + 30, start_y + line_height * current_line, ENHANCED_COLORS['text_primary'])
            
            # Wall preview with border
            sprite_key = f"wall_{game_settings['wall_sprite']}"
            if sprite_key in sprites:
                preview_x = settings_x + 300
                preview_y = start_y + line_height * current_line - 5
                preview_rect = pygame.Rect(preview_x - 2, preview_y - 2, 36, 36)
                pygame.draw.rect(screen, ENHANCED_COLORS['accent_silver'], preview_rect, border_radius=4)
                preview_sprite = pygame.transform.scale(sprites[sprite_key], (32, 32))
                screen.blit(preview_sprite, (preview_x, preview_y))
            
            current_line += 1
            # 6. Floor Style
            floor_name = game_settings['floor_sprite'].replace('.png', '').replace('_', ' ').title()
            setting_rect_6 = pygame.Rect(settings_x - 20, start_y + line_height * current_line - 10, 250, 35)
            draw_gradient_rect(screen, setting_rect_6, ENHANCED_COLORS['button_normal'], ENHANCED_COLORS['button_hover'])
            draw_text_with_shadow(screen, "6.", settings_x - 10, start_y + line_height * current_line, ENHANCED_COLORS['accent_gold'])
            draw_text_with_shadow(screen, f"Floor Style: {floor_name}", settings_x + 30, start_y + line_height * current_line, ENHANCED_COLORS['text_primary'])
            
            # Floor preview with border
            sprite_key = f"floor_{game_settings['floor_sprite']}"
            if sprite_key in sprites:
                preview_x = settings_x + 300
                preview_y = start_y + line_height * current_line - 5
                preview_rect = pygame.Rect(preview_x - 2, preview_y - 2, 36, 36)
                pygame.draw.rect(screen, ENHANCED_COLORS['accent_silver'], preview_rect, border_radius=4)
                preview_sprite = pygame.transform.scale(sprites[sprite_key], (32, 32))
                screen.blit(preview_sprite, (preview_x, preview_y))
        
        # Instructions panel at bottom
        instructions_y = panel_y + panel_height + 20
        instructions_rect = pygame.Rect(panel_x, instructions_y, panel_width, 120)
        draw_gradient_rect(screen, instructions_rect, ENHANCED_COLORS['panel_dark'], ENHANCED_COLORS['panel_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['accent_silver'], instructions_rect, width=2, border_radius=8)
        
        # Enhanced instructions with proper spacing
        inst_x = instructions_rect.x + 30
        inst_y = instructions_y + 20
        draw_text_with_shadow(screen, "Controls:", inst_x, inst_y, ENHANCED_COLORS['accent_gold'])
        
        instructions = [
            "Numbers 1-6: Select setting to change",
            "← → Arrow Keys: Adjust volume (hold number + arrow)",
            "F11: Toggle fullscreen mode",
            "ESC: Return to main menu"
        ]
        
        for i, instruction in enumerate(instructions):
            draw_text_with_shadow(screen, instruction, inst_x, inst_y + 25 + i * 20, ENHANCED_COLORS['text_secondary'])
        
        # Draw particles if any
        animation_manager.draw_particles(screen)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            if event.type == pygame.KEYDOWN:
                play_sound("menu_select", 0.5)  # Sound feedback
                
                if event.key == pygame.K_1:
                    animation_manager.add_particles(settings_x + 100, start_y, ENHANCED_COLORS['accent_gold'], 10)
                    self.game_state = "resolution_selection"
                elif event.key == pygame.K_2 or event.key == pygame.K_3:
                    # Volume adjustment with arrow keys
                    pass  # Handle below
                elif event.key == pygame.K_4:
                    animation_manager.add_particles(settings_x + 100, start_y + line_height * 3, ENHANCED_COLORS['accent_gold'], 10)
                    game_settings['use_emojis'] = not game_settings['use_emojis']
                    save_settings(game_settings)
                elif event.key == pygame.K_5 and not game_settings['use_emojis']:
                    animation_manager.add_particles(settings_x + 100, start_y + line_height * 4, ENHANCED_COLORS['accent_gold'], 10)
                    self.game_state = "wall_selection"
                elif event.key == pygame.K_6 and not game_settings['use_emojis']:
                    animation_manager.add_particles(settings_x + 100, start_y + line_height * 5, ENHANCED_COLORS['accent_gold'], 10)
                    self.game_state = "floor_selection"
                elif event.key == pygame.K_F11:
                    animation_manager.add_particles(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, ENHANCED_COLORS['accent_blue'], 15)
                    game_settings['fullscreen'] = not game_settings['fullscreen']
                    save_settings(game_settings)
                    apply_resolution_settings()
                elif event.key == pygame.K_LEFT:
                    # Decrease volume
                    if pygame.key.get_pressed()[pygame.K_2]:  # Music volume
                        game_settings['music_volume'] = max(0.0, game_settings['music_volume'] - 0.1)
                        apply_audio_settings()
                        save_settings(game_settings)
                        animation_manager.add_particles(bar_x + fill_width, start_y + line_height + 10, ENHANCED_COLORS['success_green'], 5)
                    elif pygame.key.get_pressed()[pygame.K_3]:  # Sound volume
                        game_settings['sound_volume'] = max(0.0, game_settings['sound_volume'] - 0.1)
                        save_settings(game_settings)
                        animation_manager.add_particles(bar_x + fill_width, start_y + line_height * 2 + 10, ENHANCED_COLORS['accent_blue'], 5)
                elif event.key == pygame.K_RIGHT:
                    # Increase volume
                    if pygame.key.get_pressed()[pygame.K_2]:  # Music volume
                        game_settings['music_volume'] = min(1.0, game_settings['music_volume'] + 0.1)
                        apply_audio_settings()
                        save_settings(game_settings)
                        animation_manager.add_particles(bar_x + fill_width, start_y + line_height + 10, ENHANCED_COLORS['success_green'], 5)
                    elif pygame.key.get_pressed()[pygame.K_3]:  # Sound volume
                        game_settings['sound_volume'] = min(1.0, game_settings['sound_volume'] + 0.1)
                        save_settings(game_settings)
                        animation_manager.add_particles(bar_x + fill_width, start_y + line_height * 2 + 10, ENHANCED_COLORS['accent_blue'], 5)
                elif event.key == pygame.K_ESCAPE:
                    play_sound("menu_back", 0.5)
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

    def resolution_selection(self):
        global game_settings
        # Enhanced background with gradient (matching main menu)
        bg_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        draw_gradient_rect(screen, bg_rect, ENHANCED_COLORS['background_dark'], ENHANCED_COLORS['primary_dark'])
        
        # Update animations
        animation_manager.update()
        
        # Animated title with shadow
        title_y = SCREEN_HEIGHT // 2 - 250
        title_x = SCREEN_WIDTH // 2 - 150
        
        # Title background panel
        title_bg_rect = pygame.Rect(title_x - 40, title_y - 20, 340, 80)
        draw_gradient_rect(screen, title_bg_rect, ENHANCED_COLORS['panel_dark'], ENHANCED_COLORS['panel_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['accent_gold'], title_bg_rect, width=3, border_radius=10)
        
        # Main title with enhanced text
        draw_text_with_shadow(screen, "Select Resolution", title_x, title_y, ENHANCED_COLORS['accent_gold'])
        
        # Common resolution options
        resolution_options = [
            [1024, 768],   # 4:3
            [1280, 720],   # 16:9 HD
            [1366, 768],   # 16:9 HD+
            [1920, 1080],  # 16:9 Full HD
            [2560, 1440],  # 16:9 QHD
            [3840, 2160]   # 16:9 4K
        ]
        
        resolution_names = [
            "1024x768 (4:3)",
            "1280x720 (HD)",
            "1366x768 (HD+)",
            "1920x1080 (Full HD)",
            "2560x1440 (QHD)",
            "3840x2160 (4K)"
        ]
        
        current_res = game_settings['resolution']
        
        # Resolution panel
        panel_y = title_y + 100
        panel_width = 500
        panel_height = 350
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        draw_gradient_rect(screen, panel_rect, ENHANCED_COLORS['panel_dark'], ENHANCED_COLORS['panel_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['accent_silver'], panel_rect, width=2, border_radius=8)
        
        # Display resolution options
        options_x = panel_x + 30
        start_y = panel_y + 30
        for i, (res, name) in enumerate(zip(resolution_options, resolution_names)):
            y_pos = start_y + i * 40
            
            # Create selection rectangle for current resolution
            if res == current_res:
                selection_rect = pygame.Rect(options_x - 15, y_pos - 8, 440, 32)
                draw_gradient_rect(screen, selection_rect, ENHANCED_COLORS['accent_gold'], ENHANCED_COLORS['accent_blue'])
                pygame.draw.rect(screen, ENHANCED_COLORS['accent_gold'], selection_rect, width=2, border_radius=6)
            
            # Number and resolution text
            number_color = ENHANCED_COLORS['accent_gold'] if res == current_res else ENHANCED_COLORS['text_secondary']
            text_color = ENHANCED_COLORS['background_dark'] if res == current_res else ENHANCED_COLORS['text_primary']
            
            draw_text_with_shadow(screen, f"{i+1}.", options_x, y_pos, number_color)
            draw_text_with_shadow(screen, name, options_x + 30, y_pos, text_color)
        
        # Fullscreen toggle section
        fs_y = start_y + len(resolution_options) * 40 + 20
        fs_status = "ON" if game_settings['fullscreen'] else "OFF"
        fs_status_color = ENHANCED_COLORS['success_green'] if game_settings['fullscreen'] else ENHANCED_COLORS['danger_red']
        
        fs_rect = pygame.Rect(options_x - 15, fs_y - 8, 200, 32)
        draw_gradient_rect(screen, fs_rect, ENHANCED_COLORS['button_normal'], ENHANCED_COLORS['button_hover'])
        
        draw_text_with_shadow(screen, "F.", options_x, fs_y, ENHANCED_COLORS['accent_gold'])
        draw_text_with_shadow(screen, "Fullscreen: ", options_x + 30, fs_y, ENHANCED_COLORS['text_primary'])
        draw_text_with_shadow(screen, fs_status, options_x + 150, fs_y, fs_status_color)
        
        # Instructions panel at bottom
        instructions_y = panel_y + panel_height + 20
        instructions_rect = pygame.Rect(panel_x, instructions_y, panel_width, 80)
        draw_gradient_rect(screen, instructions_rect, ENHANCED_COLORS['panel_dark'], ENHANCED_COLORS['panel_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['accent_silver'], instructions_rect, width=2, border_radius=8)
        
        # Enhanced instructions
        inst_x = instructions_rect.x + 20
        inst_y = instructions_y + 15
        
        instructions = [
            "Press number (1-6) to select resolution",
            "Press F to toggle fullscreen mode", 
            "Press ESC to return to settings"
        ]
        
        for i, instruction in enumerate(instructions):
            draw_text_with_shadow(screen, instruction, inst_x, inst_y + i * 18, ENHANCED_COLORS['text_secondary'])
        
        # Draw particles if any
        animation_manager.draw_particles(screen)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            if event.type == pygame.KEYDOWN:
                play_sound("menu_select", 0.5)  # Sound feedback
                
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6]:
                    idx = int(pygame.key.name(event.key)) - 1
                    if 0 <= idx < len(resolution_options):
                        animation_manager.add_particles(options_x + 200, start_y + idx * 40, ENHANCED_COLORS['accent_gold'], 12)
                        game_settings['resolution'] = resolution_options[idx]
                        save_settings(game_settings)
                        apply_resolution_settings()
                elif event.key == pygame.K_f:
                    animation_manager.add_particles(options_x + 100, fs_y, ENHANCED_COLORS['accent_blue'], 10)
                    game_settings['fullscreen'] = not game_settings['fullscreen']
                    save_settings(game_settings)
                    apply_resolution_settings()
                elif event.key == pygame.K_ESCAPE:
                    play_sound("menu_back", 0.5)
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
            "warrior": ("High HP, strong attacks, Power Strike skill (Level 2)", "⚔️" if game_settings['use_emojis'] else "WAR"),
            "mage": ("Magic damage, area spells, Fireball skill (Level 3)", "🧙" if game_settings['use_emojis'] else "MAG"),
            "archer": ("Balanced stats, ranged attacks, Double Shot skill (Level 2)", "🏹" if game_settings['use_emojis'] else "ARC")
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
            elif self.game_state == "resolution_selection":
                self.resolution_selection()
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
        # Update animations and camera
        animation_manager.update()
        self.update_camera()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            if event.type == pygame.KEYDOWN:
                self.handle_input(event.key)
        self.draw_game()

    def handle_input(self, key):
        if self.shop_state == "open":
            self.handle_shop_input(key)
        elif self.inventory_state == "open":
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
        # Check for shopkeeper at player's position
        for shopkeeper in self.dungeon.shopkeepers:
            if shopkeeper.x == player.x and shopkeeper.y == player.y:
                self.open_shop(shopkeeper)
                return
        
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

    def open_shop(self, shopkeeper):
        """Open the shop interface."""
        self.shop_state = "open"
        self.current_shopkeeper = shopkeeper
        self.shop_mode = "buy"
        self.selected_shop_item_idx = 0
        self.selected_player_idx = 0
        play_sound("interface1", 0.7)  # Shop open sound
        self.add_message(f"Welcome to {shopkeeper.name}'s shop!")

    def handle_shop_input(self, key):
        """Handle input while in shop mode."""
        if key == pygame.K_ESCAPE or key == pygame.K_q:
            self.shop_state = "closed"
            self.current_shopkeeper = None
            play_sound("interface2", 0.7)
            return
        
        if key == pygame.K_TAB:  # Switch between buy/sell modes
            self.shop_mode = "sell" if self.shop_mode == "buy" else "buy"
            self.selected_shop_item_idx = 0
            play_sound("interface3", 0.7)
            return
        
        # Navigation
        if key == pygame.K_UP:
            if self.shop_mode == "buy":
                self.selected_shop_item_idx = max(0, self.selected_shop_item_idx - 1)
            else:  # sell mode
                self.selected_item_idx = max(0, self.selected_item_idx - 1)
        elif key == pygame.K_DOWN:
            if self.shop_mode == "buy":
                max_items = len(self.current_shopkeeper.inventory) - 1
                self.selected_shop_item_idx = min(max_items, self.selected_shop_item_idx + 1)
            else:  # sell mode
                player_inventory = self.players[self.selected_player_idx].inventory
                max_items = len(player_inventory) - 1
                self.selected_item_idx = min(max_items, self.selected_item_idx + 1)
        elif key == pygame.K_LEFT:
            self.selected_player_idx = max(0, self.selected_player_idx - 1)
        elif key == pygame.K_RIGHT:
            self.selected_player_idx = min(len(self.players) - 1, self.selected_player_idx + 1)
        
        # Buy/Sell action
        if key == pygame.K_RETURN:
            if self.shop_mode == "buy":
                self.buy_item()
            else:
                self.sell_item()

    def buy_item(self):
        """Handle buying an item from the shop."""
        if not self.current_shopkeeper.inventory:
            self.add_message("The shop has no items for sale!")
            play_sound("error", 0.7)
            return
        
        if self.selected_shop_item_idx >= len(self.current_shopkeeper.inventory):
            return
        
        item = self.current_shopkeeper.inventory[self.selected_shop_item_idx]
        price = self.current_shopkeeper.get_item_price(item)
        player = self.players[self.selected_player_idx]
        
        # Check if player has enough gold
        if player.gold < price:
            self.add_message(f"❌ Not enough gold! Need {price}g, have {player.gold}g")
            play_sound("error", 0.7)  # Error sound
            return
        
        # Check if player can carry the item
        if not player.can_carry_item(item):
            item_type = type(item).__name__.lower()
            if isinstance(item, Weapon):
                max_items = player.max_weapons
                current_count = len([i for i in player.inventory if isinstance(i, Weapon)])
                self.add_message(f"❌ Weapon inventory full! ({current_count}/{max_items})")
            elif isinstance(item, Armor):
                max_items = player.max_armor
                current_count = len([i for i in player.inventory if isinstance(i, Armor)])
                self.add_message(f"❌ Armor inventory full! ({current_count}/{max_items})")
            elif isinstance(item, Potion):
                max_items = player.max_potions
                current_count = len([i for i in player.inventory if isinstance(i, Potion)])
                self.add_message(f"❌ Potion inventory full! ({current_count}/{max_items})")
            else:
                self.add_message(f"❌ Cannot carry more {item_type}s!")
            play_sound("error", 0.7)
            return
        
        # Complete the transaction
        player.inventory.append(item)
        player.gold -= price
        self.current_shopkeeper.inventory.remove(item)
        self.add_message(f"✅ Bought {item.name} for {price} gold!")
        play_sound("pickup_coin", 0.8)
        
        # Adjust selection if we removed the last item
        if self.selected_shop_item_idx >= len(self.current_shopkeeper.inventory):
            self.selected_shop_item_idx = max(0, len(self.current_shopkeeper.inventory) - 1)

    def sell_item(self):
        """Handle selling an item to the shop."""
        player = self.players[self.selected_player_idx]
        
        if not player.inventory:
            self.add_message("❌ You have no items to sell!")
            play_sound("error", 0.7)
            return
        
        if self.selected_item_idx >= len(player.inventory):
            return
        
        item = player.inventory[self.selected_item_idx]
        
        # Check if item is equipped (can't sell equipped items)
        if ((isinstance(item, Weapon) and item == player.weapon) or
            (isinstance(item, Armor) and item == player.armor)):
            self.add_message("❌ Cannot sell equipped items!")
            play_sound("error", 0.7)  # Error sound
            return
        
        price = self.current_shopkeeper.sell_item_price(item)
        
        # Complete the transaction
        player.inventory.remove(item)
        player.gold += price
        self.add_message(f"✅ Sold {item.name} for {price} gold!")
        play_sound("pickup_coin2", 0.8)
        
        # Adjust selection if we removed the last item
        if self.selected_item_idx >= len(player.inventory):
            self.selected_item_idx = max(0, len(player.inventory) - 1)

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
        # Map movement keys to directions and update player direction
        if direction == 'w': 
            dy = -1
            player.direction = "up"
        if direction == 's': 
            dy = 1
            player.direction = "down"
        if direction == 'a': 
            dx = -1
            player.direction = "left"
        if direction == 'd': 
            dx = 1
            player.direction = "right"

        new_x, new_y = player.x + dx, player.y + dy

        if not (0 <= new_x < self.dungeon.width and 0 <= new_y < self.dungeon.height):
            self.add_message("You can't move off the map.")
            play_sound("error", 0.3)
            return

        if self.dungeon.grid[new_y][new_x] == UI["stairs"]:
            # Add particle effect for stairs
            screen_x = GAME_OFFSET_X + (new_x - self.camera_x) * TILE_SIZE + TILE_SIZE // 2
            screen_y = GAME_OFFSET_Y + (new_y - self.camera_y) * TILE_SIZE + TILE_SIZE // 2
            animation_manager.add_particles(screen_x, screen_y, ENHANCED_COLORS['accent_gold'], 20)
            
            self.dungeon_level += 1
            self.new_level()
            play_sound("door_open", 0.8)
            return

        if self.dungeon.grid[new_y][new_x] == UI["floor"]:
            enemies_in_pos = [e for e in self.dungeon.enemies if e.x == new_x and e.y == new_y]
            if enemies_in_pos:
                # Add combat particles
                screen_x = GAME_OFFSET_X + (new_x - self.camera_x) * TILE_SIZE + TILE_SIZE // 2
                screen_y = GAME_OFFSET_Y + (new_y - self.camera_y) * TILE_SIZE + TILE_SIZE // 2
                animation_manager.add_particles(screen_x, screen_y, ENHANCED_COLORS['danger_red'], 15)
                self.start_combat(enemies_in_pos)
            else:
                # Move player successfully
                player.x, player.y = new_x, new_y
                self.update_camera()  # Update camera after movement
                
                # Check for item pickup with visual feedback
                for item in list(self.dungeon.items):
                    if item.x == new_x and item.y == new_y:
                        success, message = player.try_add_item(item, auto_replace=True)
                        if success:
                            # Add pickup particle effect
                            screen_x = GAME_OFFSET_X + (new_x - self.camera_x) * TILE_SIZE + TILE_SIZE // 2
                            screen_y = GAME_OFFSET_Y + (new_y - self.camera_y) * TILE_SIZE + TILE_SIZE // 2
                            
                            # Different particles for different item types
                            if isinstance(item, Weapon):
                                animation_manager.add_particles(screen_x, screen_y, ENHANCED_COLORS['accent_silver'], 8)
                                play_sound("pickup_metal", 0.7)
                            elif isinstance(item, Armor):
                                animation_manager.add_particles(screen_x, screen_y, ENHANCED_COLORS['accent_blue'], 8)
                                play_sound("pickup_armor", 0.7)
                            elif isinstance(item, Potion):
                                animation_manager.add_particles(screen_x, screen_y, ENHANCED_COLORS['success_green'], 8)
                                play_sound("pickup_bottle", 0.7)
                            else:
                                animation_manager.add_particles(screen_x, screen_y, ENHANCED_COLORS['accent_gold'], 8)
                                play_sound("pickup_coin", 0.7)
                            
                            self.dungeon.items.remove(item)
                            self.add_message(f"{player.name} picked up {item.name}.")
                            
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
        else:
            # Can't move to wall - add small particle effect
            play_sound("error", 0.2)
            self.add_message("You can't move there.")

    def draw_game(self):
        if self.shop_state == "open":
            self.draw_shop_screen()
        elif self.inventory_state == "open":
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
        viewport_start_x = max(0, int(self.camera_x))
        viewport_start_y = max(0, int(self.camera_y))
        viewport_end_x = min(self.dungeon.width, int(self.camera_x) + VIEWPORT_WIDTH)
        viewport_end_y = min(self.dungeon.height, int(self.camera_y) + VIEWPORT_HEIGHT)
        
        # Draw map tiles in viewport
        for world_y in range(viewport_start_y, viewport_end_y):
            for world_x in range(viewport_start_x, viewport_end_x):
                screen_x = GAME_OFFSET_X + (world_x - self.camera_x) * TILE_SIZE
                screen_y = GAME_OFFSET_Y + (world_y - self.camera_y) * TILE_SIZE
                
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
                
                screen_x = GAME_OFFSET_X + (item.x - self.camera_x) * TILE_SIZE
                screen_y = GAME_OFFSET_Y + (item.y - self.camera_y) * TILE_SIZE
                
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
                
                screen_x = GAME_OFFSET_X + (treasure.x - self.camera_x) * TILE_SIZE
                screen_y = GAME_OFFSET_Y + (treasure.y - self.camera_y) * TILE_SIZE
                
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
                
                screen_x = GAME_OFFSET_X + (enemy.x - self.camera_x) * TILE_SIZE
                screen_y = GAME_OFFSET_Y + (enemy.y - self.camera_y) * TILE_SIZE
                
                if game_settings['use_emojis']:
                    text = font.render(enemy.icon, True, RED)
                    screen.blit(text, (screen_x, screen_y))
                else:
                    # Use Undertale enemy sprites
                    sprite_drawn = False
                    
                    # Try Undertale enemy sprite first (from enemy_sprite_mapping)
                    enemy_type = enemy.enemy_type
                    sprite_key = f"monster_{enemy_type}"
                    if sprite_key in sprites:
                        screen.blit(sprites[sprite_key], (screen_x, screen_y))
                        sprite_drawn = True
                    
                    # Final fallback to colored rectangle if sprite not available
                    if not sprite_drawn:
                        pygame.draw.rect(screen, RED, (screen_x + 2, screen_y + 2, TILE_SIZE - 4, TILE_SIZE - 4))
                
        # Draw shopkeepers (only if visible)
        for shopkeeper in self.dungeon.shopkeepers:
            if (viewport_start_x <= shopkeeper.x < viewport_end_x and 
                viewport_start_y <= shopkeeper.y < viewport_end_y and
                self.dungeon.is_visible(shopkeeper.x, shopkeeper.y)):
                
                screen_x = GAME_OFFSET_X + (shopkeeper.x - self.camera_x) * TILE_SIZE
                screen_y = GAME_OFFSET_Y + (shopkeeper.y - self.camera_y) * TILE_SIZE
                
                if game_settings['use_emojis']:
                    # Use temmie emoji for consistency
                    text = font.render("🐱", True, (255, 215, 0))  # Cat emoji for Temmie
                    screen.blit(text, (screen_x, screen_y))
                else:
                    # For sprite mode, use temmie sprite
                    sprite_key = f"monster_{shopkeeper.icon}"
                    if sprite_key in sprites:
                        screen.blit(sprites[sprite_key], (screen_x, screen_y))
                    elif "monster_temmie" in sprites:
                        screen.blit(sprites["monster_temmie"], (screen_x, screen_y))
                    else:
                        # Gold-colored rectangle for merchant as fallback
                        pygame.draw.rect(screen, (255, 215, 0), (screen_x + 4, screen_y + 4, TILE_SIZE - 8, TILE_SIZE - 8))

        # Draw players
        for player in self.players:
            if (viewport_start_x <= player.x < viewport_end_x and 
                viewport_start_y <= player.y < viewport_end_y):
                
                screen_x = GAME_OFFSET_X + (player.x - self.camera_x) * TILE_SIZE
                screen_y = GAME_OFFSET_Y + (player.y - self.camera_y) * TILE_SIZE
                
                if game_settings['use_emojis']:
                    text = font.render(player.icon, True, GREEN)
                    screen.blit(text, (screen_x, screen_y))
                else:
                    # Use directional sprites for better Undertale character movement
                    sprite_drawn = False
                    
                    # Try directional sprite first
                    directional_sprite_key = f"player_{player.char_class}_{player.direction}"
                    if directional_sprite_key in sprites:
                        screen.blit(sprites[directional_sprite_key], (screen_x, screen_y))
                        sprite_drawn = True
                    # Fallback to static sprite
                    elif f"player_{player.char_class}" in sprites:
                        screen.blit(sprites[f"player_{player.char_class}"], (screen_x, screen_y))
                        sprite_drawn = True
                    
                    # Final fallback to colored rectangle
                    if not sprite_drawn:
                        pygame.draw.rect(screen, GREEN, (screen_x + 6, screen_y + 6, TILE_SIZE - 12, TILE_SIZE - 12))

        # Draw minimap
        self.draw_minimap()
        
        # Draw UI
        self.draw_ui()
        
        # Draw particle effects on top of everything
        animation_manager.draw_particles(screen)
        
        pygame.display.flip()

    def draw_minimap(self):
        """Draw a small overview map in the top right corner."""
        # Position minimap to align with the right panel
        minimap_x = SCREEN_WIDTH - 240 - 5  # Align with right panel
        minimap_y = 15  # Small offset from top
        
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
        # Remove the top black bar - now we'll use floating text with padding
        
        # Player status in top-left corner with padding
        status_y = 15
        status_x = 25
        for i, p in enumerate(self.players):
            if game_settings['use_emojis']:
                status_text = f'{p.icon} {p.name} ({p.char_class}) | {UI["level"]} {p.level} | {UI["hp"]} {p.hp}/{p.max_hp}'
            else:
                status_text = f'{p.name} ({p.char_class}) | Lv.{p.level} | HP {p.hp}/{p.max_hp}'
                
            # Add mana for mages
            if p.char_class == "mage":
                if game_settings['use_emojis']:
                    status_text += f' | {UI["mana"]} {p.mana}/{p.max_mana}'
                else:
                    status_text += f' | MP {p.mana}/{p.max_mana}'
                    
            self.draw_text(status_text, status_x, status_y, WHITE, padding=8)
            status_y += 45  # Increased spacing between player status lines
        
        # Bottom message area - only when there are messages, with padding
        if self.messages:
            msg_y = SCREEN_HEIGHT - 60
            for i, msg in enumerate(self.messages):
                if i < 3:  # Show only last 3 messages
                    self.draw_text(msg, 25, msg_y - i * 25, WHITE, padding=6)
        
        # Right panel for minimap and info (keep the panel but make it smaller)
        right_panel_width = 240
        right_panel_x = SCREEN_WIDTH - right_panel_width - 10
        
        # Smaller semi-transparent background for right panel (starts after minimap area)
        panel_start_y = MINIMAP_SIZE + 50
        panel_height = SCREEN_HEIGHT - panel_start_y - 20
        right_panel_surface = pygame.Surface((right_panel_width, panel_height))
        right_panel_surface.set_alpha(160)
        right_panel_surface.fill((0, 0, 0))
        screen.blit(right_panel_surface, (right_panel_x, panel_start_y))
        
        # Info text in right panel with padding
        info_x = right_panel_x + 15
        info_start_y = panel_start_y + 15
        
        # Dungeon level
        level_text = f"Dungeon Level: {self.dungeon_level}"
        self.draw_text(level_text, info_x, info_start_y, LIGHT_GRAY, padding=4)
        
        # Inventory status for current player
        if self.players:
            current_player = self.players[self.current_player_idx]
            weapons = len(current_player.get_inventory_by_type(Weapon))
            armor = len(current_player.get_inventory_by_type(Armor))
            potions = len(current_player.get_inventory_by_type(Potion))
            
            inv_text = f"Inventory:"
            self.draw_text(inv_text, info_x, info_start_y + 35, LIGHT_GRAY, padding=4)
            
            weapon_text = f"⚔️ {weapons}/{current_player.max_weapons}"
            armor_text = f"🛡️ {armor}/{current_player.max_armor}" 
            potion_text = f"🧪 {potions}/{current_player.max_potions}"
            
            self.draw_text(weapon_text, info_x, info_start_y + 65, WHITE, padding=3)
            self.draw_text(armor_text, info_x, info_start_y + 95, WHITE, padding=3)
            self.draw_text(potion_text, info_x, info_start_y + 125, WHITE, padding=3)
        
        # Controls at bottom of right panel with padding
        controls_y = SCREEN_HEIGHT - 140
        self.draw_text("Controls:", info_x, controls_y, GRAY, padding=4)
        self.draw_text("WASD - Move", info_x, controls_y + 25, GRAY, padding=3)
        self.draw_text("E - Interact", info_x, controls_y + 50, GRAY, padding=3)
        self.draw_text("I - Inventory", info_x, controls_y + 75, GRAY, padding=3)
        self.draw_text("Q - Menu", info_x, controls_y + 100, GRAY, padding=3)


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
            
            # Check if Asgore was defeated (victory condition)
            asgore_defeated = any(enemy.enemy_type == "asgore" for enemy in self.combat_enemies)
            
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
            if asgore_defeated:
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
            # Improved damage calculation: base damage reduced by percentage based on defense
            base_damage = player.attack + random.randint(0, 3)  # Add small random variance
            defense_reduction = min(0.75, target.defense * 0.05)  # Max 75% damage reduction
            damage = max(1, int(base_damage * (1 - defense_reduction)))  # Minimum 1 damage
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
            # Improved damage calculation: base damage reduced by percentage based on defense
            base_damage = enemy.attack + random.randint(0, 2)  # Add small random variance
            defense_reduction = min(0.75, target.defense * 0.05)  # Max 75% damage reduction
            damage = max(1, int(base_damage * (1 - defense_reduction)))  # Minimum 1 damage
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
            if player.level < 2:
                self.add_message(f"Power Strike requires level 2. Current level: {player.level}")
                return
            if player.skill_cooldown > 0:
                self.add_message(f"Power Strike is on cooldown for {player.skill_cooldown} more turns.")
                return
            play_sound("sword_draw", 0.7)
            target = random.choice(alive_enemies)
            # Power Strike: 2x base attack with improved damage calculation
            base_damage = (player.attack * 2) + random.randint(2, 6)
            defense_reduction = min(0.75, target.defense * 0.05)
            damage = max(2, int(base_damage * (1 - defense_reduction)))
            target.take_damage(damage)
            self.add_message(f"{player.name} uses Power Strike on {target.name} for {damage} damage!")
            player.skill_cooldown = 3
        elif player.char_class == "mage":
            if player.level < 3:
                self.add_message(f"Fireball requires level 3. Current level: {player.level}")
                return
            if player.mana < 10:
                self.add_message("Not enough mana for Fireball.")
                return
            play_sound("magic_spell", 0.7)
            self.add_message(f"{player.name} casts Fireball!")
            for enemy in alive_enemies:
                # Fireball: Area damage with balanced calculation
                base_damage = int(player.attack * 0.8) + random.randint(3, 7)
                defense_reduction = min(0.75, enemy.defense * 0.05)
                damage = max(2, int(base_damage * (1 - defense_reduction)))
                enemy.take_damage(damage)
                self.add_message(f"Fireball hits {enemy.name} for {damage} damage.")
            player.mana -= 10
        elif player.char_class == "archer":
            if player.level < 2:
                self.add_message(f"Double Shot requires level 2. Current level: {player.level}")
                return
            if player.skill_cooldown > 0:
                self.add_message(f"Double Shot is on cooldown for {player.skill_cooldown} more turns.")
                return
            play_random_sound(["sword_attack", "sword_attack2"], 0.5)
            self.add_message(f"{player.name} uses Double Shot!")
            for _ in range(2):
                if alive_enemies:  # Check if there are still alive enemies for each shot
                    target = random.choice(alive_enemies)
                    # Double Shot: Normal damage per shot with balanced calculation
                    base_damage = player.attack + random.randint(1, 4)
                    defense_reduction = min(0.75, target.defense * 0.05)
                    damage = max(1, int(base_damage * (1 - defense_reduction)))
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
