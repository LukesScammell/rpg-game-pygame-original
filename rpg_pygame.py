#!/usr/bin/env python
print("--- RUNNING PYGAME VERSION ---")

# ANCHOR Imports and Dependencies
# File: imports.py - Contains all import statements and external dependencies
import random
import os
import json
import pygame
import math
from collections import deque
from datetime import datetime

# ANCHOR Game Constants and Configuration
# File: constants.py - Contains all game constants, colors, and configuration values

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
SAVE_FILE = "rpg_save_game.json"  # Legacy single save file
SAVE_FOLDER = "saves"
MAX_SAVE_SLOTS = 5

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

# Pygame Setup ---
pygame.init()
pygame.mixer.init()

# ANCHOR Settings System
# File: settings.py - Contains settings management functions and configuration

# --- Settings System ---
def load_settings():
    """Load game settings from file."""
    default_settings = {
        "use_emojis": True,
        "wall_sprite": "stone_brick1.png",
        "floor_sprite": "sandstone_floor0.png",
        "resolution": [1920, 1080],  # [width, height]
        "music_volume": 0.1,  # 0.0 to 1.0 - Lower default for Bluetooth compatibility
        "sound_volume": 0.2,  # 0.0 to 1.0 - Lower default for Bluetooth compatibility
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
    """Apply current audio settings to the game."""
    pygame.mixer.music.set_volume(game_settings["music_volume"])
    # Note: Sound volume will be applied per-sound when playing

apply_audio_settings()

# ANCHOR Sprite Loading and Graphics System
# File: graphics.py - Contains sprite loading, animation system, and graphics utilities

# --- Sprite Loading ---
sprites = {}
ui_elements = {}

# ANCHOR Animation System
# File: animations.py - Contains animation classes and management

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

class DamageNumber:
    """Animated damage number that floats up and fades away."""
    def __init__(self, x, y, damage, is_critical=False):
        self.x = float(x)
        self.y = float(y)
        self.start_y = float(y)
        self.damage = damage
        self.is_critical = is_critical
        self.creation_time = pygame.time.get_ticks()
        self.lifetime = 2000  # 2 seconds
        self.float_speed = -50  # Pixels per second upward
        self.fade_speed = 255 / self.lifetime  # Alpha fade rate
        self.alpha = 255
        self.wobble_offset = 0
        self.scale = 1.5 if is_critical else 1.0
        
        # Create damage text surface
        font_size = 32 if is_critical else 24
        font = pygame.font.Font(None, font_size)
        color = (255, 100, 100) if is_critical else (255, 255, 255)  # Red for crits, white for normal
        self.text_surface = font.render(str(damage), True, color)
        
        # Scale the surface if it's a critical hit
        if is_critical:
            original_size = self.text_surface.get_size()
            new_size = (int(original_size[0] * self.scale), int(original_size[1] * self.scale))
            self.text_surface = pygame.transform.scale(self.text_surface, new_size)
    
    def update(self, dt):
        """Update the damage number animation."""
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.creation_time
        
        if elapsed >= self.lifetime:
            return False  # Mark for removal
        
        # Move upward
        self.y += self.float_speed * dt / 1000.0
        
        # Add slight wobble effect
        self.wobble_offset = math.sin(elapsed * 0.01) * 5
        
        # Fade out
        progress = elapsed / self.lifetime
        self.alpha = max(0, 255 * (1 - progress))
        
        # Scale effect for critical hits
        if self.is_critical:
            bounce_factor = 1 + 0.3 * math.sin(elapsed * 0.015)
            self.scale = 1.5 * bounce_factor
        
        return True  # Still alive
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw the damage number on screen."""
        if self.alpha <= 0:
            return
        
        # Apply alpha to the surface
        temp_surface = self.text_surface.copy()
        temp_surface.set_alpha(int(self.alpha))
        
        # Calculate screen position with camera offset and wobble
        screen_x = self.x - camera_x + self.wobble_offset
        screen_y = self.y - camera_y
        
        # Center the text
        rect = temp_surface.get_rect()
        rect.centerx = screen_x
        rect.centery = screen_y
        
        screen.blit(temp_surface, rect)

# Global animation storage
portrait_animations = {}
damage_numbers = []  # List to store active damage numbers

def add_damage_number(x, y, damage, is_critical=False):
    """Add a new damage number to the display."""
    global damage_numbers
    damage_numbers.append(DamageNumber(x, y, damage, is_critical))

def update_damage_numbers(dt):
    """Update all active damage numbers and remove expired ones."""
    global damage_numbers
    damage_numbers = [dn for dn in damage_numbers if dn.update(dt)]

def draw_damage_numbers(screen, camera_x=0, camera_y=0):
    """Draw all active damage numbers."""
    for damage_number in damage_numbers:
        damage_number.draw(screen, camera_x, camera_y)

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
    
    # Load player sprites from the new sprites folder
    print("Loading player sprites from sprites folder...")
    sprite_folder_path = os.path.join("assets", "sprites")
    
    # Warrior = Main character (spr_mainchara)
    warrior_directions = {
        "down": ["spr_maincharad_0.png", "spr_maincharad_1.png", "spr_maincharad_2.png", "spr_maincharad_3.png"],
        "left": ["spr_maincharal_0.png", "spr_maincharal_1.png"],
        "right": ["spr_maincharar_0.png", "spr_maincharar_1.png"],
        "up": ["spr_maincharau_0.png", "spr_maincharau_1.png", "spr_maincharau_2.png", "spr_maincharau_3.png"]
    }
    
    for direction, sprite_files in warrior_directions.items():
        frames = []
        for sprite_file in sprite_files:
            sprite_path = os.path.join(sprite_folder_path, sprite_file)
            if os.path.exists(sprite_path):
                try:
                    frame = pygame.image.load(sprite_path)
                    frames.append(pygame.transform.scale(frame, (TILE_SIZE, TILE_SIZE)))
                except pygame.error as e:
                    print(f"  Error loading {sprite_file}: {e}")
                    continue
        
        if frames:
            sprites[f"player_warrior_{direction}"] = frames[0]  # First frame for static display
            portrait_animations[f"warrior_{direction}"] = PortraitAnimation(frames, 150)  # Faster animation
            print(f"  Loaded: warrior {direction} - {len(frames)} frames")
    
    # Set default warrior sprite
    if "player_warrior_down" in sprites:
        sprites["player_warrior"] = sprites["player_warrior_down"]
    
    # Mage = Sans (spr_sans_[direction])
    sans_directions = {
        "down": ["spr_sans_d_0.png", "spr_sans_d_1.png", "spr_sans_d_2.png", "spr_sans_d_3.png"],
        "left": ["spr_sans_l_0.png", "spr_sans_l_1.png", "spr_sans_l_2.png", "spr_sans_l_3.png"],
        "right": ["spr_sans_r_0.png", "spr_sans_r_1.png", "spr_sans_r_2.png", "spr_sans_r_3.png"],
        "up": ["spr_sans_u_0.png", "spr_sans_u_1.png", "spr_sans_u_2.png", "spr_sans_u_3.png"]
    }
    
    for direction, sprite_files in sans_directions.items():
        frames = []
        for sprite_file in sprite_files:
            sprite_path = os.path.join(sprite_folder_path, sprite_file)
            if os.path.exists(sprite_path):
                try:
                    frame = pygame.image.load(sprite_path)
                    frames.append(pygame.transform.scale(frame, (TILE_SIZE, TILE_SIZE)))
                except pygame.error as e:
                    print(f"  Error loading {sprite_file}: {e}")
                    continue
        
        if frames:
            sprites[f"player_mage_{direction}"] = frames[0]  # First frame for static display
            portrait_animations[f"mage_{direction}"] = PortraitAnimation(frames, 150)
            print(f"  Loaded: mage (Sans) {direction} - {len(frames)} frames")
    
    # Set default mage sprite
    if "player_mage_down" in sprites:
        sprites["player_mage"] = sprites["player_mage_down"]
    
    # Archer = Papyrus (spr_papyrus_[direction])
    papyrus_directions = {
        "down": ["spr_papyrus_d_0.png", "spr_papyrus_d_1.png", "spr_papyrus_d_2.png", "spr_papyrus_d_3.png"],
        "left": ["spr_papyrus_l_0.png", "spr_papyrus_l_1.png", "spr_papyrus_l_2.png", "spr_papyrus_l_3.png"],
        "right": ["spr_papyrus_r_0.png", "spr_papyrus_r_1.png", "spr_papyrus_r_2.png", "spr_papyrus_r_3.png"],
        "up": ["spr_papyrus_u_0.png", "spr_papyrus_u_1.png", "spr_papyrus_u_2.png", "spr_papyrus_u_3.png"]
    }
    
    for direction, sprite_files in papyrus_directions.items():
        frames = []
        for sprite_file in sprite_files:
            sprite_path = os.path.join(sprite_folder_path, sprite_file)
            if os.path.exists(sprite_path):
                try:
                    frame = pygame.image.load(sprite_path)
                    frames.append(pygame.transform.scale(frame, (TILE_SIZE, TILE_SIZE)))
                except pygame.error as e:
                    print(f"  Error loading {sprite_file}: {e}")
                    continue
        
        if frames:
            sprites[f"player_archer_{direction}"] = frames[0]  # First frame for static display
            portrait_animations[f"archer_{direction}"] = PortraitAnimation(frames, 150)
            print(f"  Loaded: archer (Papyrus) {direction} - {len(frames)} frames")
    
    # Set default archer sprite
    if "player_archer_down" in sprites:
        sprites["player_archer"] = sprites["player_archer_down"]
    
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
        },
        
        # Dog enemies
        "lesser_dog": {
            "path": os.path.join("assets", "undertale", "Characters", "# NPCs", "02 - Snowdin", "Snowdin Town"),
            "files": ["spr_dogamy_npc_0.png"],
            "portrait_files": ["spr_dogamy_npc_0.png", "spr_dogamy_npc_1.png"]
        },
        
        "greater_dog": {
            "path": os.path.join("assets", "undertale", "Characters", "# NPCs", "02 - Snowdin", "Snowdin Town"),
            "files": ["spr_dogaressa_npc_0.png"],
            "portrait_files": ["spr_dogaressa_npc_0.png", "spr_dogaressa_npc_1.png"]
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

    # Load Temmie shop sprites
    print("Loading Temmie shop sprites...")
    temmie_shop_path = os.path.join("assets", "undertale", "Shops-20250721T005643Z-1-001", "Shops", "Temmie")
    temmie_bg_path = os.path.join(temmie_shop_path, "Backgrounds")
    
    # Load Temmie shop background
    try:
        bg_shop_path = os.path.join(temmie_bg_path, "bg_temshop.png")
        if os.path.exists(bg_shop_path):
            sprites["bg_temshop"] = pygame.image.load(bg_shop_path)
            print("  Loaded: Temmie shop background")
        else:
            print("  Warning: Temmie shop background not found")
    except pygame.error as e:
        print(f"  Error loading Temmie shop background: {e}")
    
    # Load Temmie character sprites
    temmie_sprites = [
        "spr_5_tembody_0.png", "spr_temhat_0.png", "spr_5_eyes1_0.png", "spr_5_eyes2_0.png",
        "spr_5_eyes3_0.png", "spr_5_eyes4_0.png", "spr_5_eyes5_0.png", "spr_5_eyes6_0.png",
        "spr_5_mouth1_0.png", "spr_5_mouth2_0.png", "spr_5_mouth3_0.png", "spr_5_sellface_0.png",
        "spr_5_tembox_0.png"  # Add the tembox sprite
    ]
    
    for temmie_sprite in temmie_sprites:
        try:
            temmie_sprite_path = os.path.join(temmie_shop_path, temmie_sprite)
            if os.path.exists(temmie_sprite_path):
                sprite_key = temmie_sprite.replace('.png', '')
                sprites[sprite_key] = pygame.image.load(temmie_sprite_path)
                print(f"  Loaded: {temmie_sprite}")
            else:
                print(f"  Warning: Temmie sprite not found: {temmie_sprite}")
        except pygame.error as e:
            print(f"  Error loading Temmie sprite {temmie_sprite}: {e}")
    
    # Load Bratty & Catty shop sprites
    print("Loading Bratty & Catty shop sprites...")
    bratty_catty_shop_path = os.path.join("assets", "undertale", "Shops-20250721T005643Z-1-001", "Shops", "Catty & Bratty")
    bratty_catty_bg_path = os.path.join(bratty_catty_shop_path, "Backgrounds")
    
    # Load Bratty & Catty shop background
    try:
        bg_bratty_path = os.path.join(bratty_catty_bg_path, "bg_brattybg.png")
        if os.path.exists(bg_bratty_path):
            sprites["bg_brattybg"] = pygame.image.load(bg_bratty_path)
            print("  Loaded: Bratty & Catty shop background")
        else:
            print("  Warning: Bratty & Catty shop background not found")
    except pygame.error as e:
        print(f"  Error loading Bratty & Catty shop background: {e}")
    
    # Load Bratty & Catty character sprites
    merchant_sprites = [
        # Bratty sprites
        "spr_brattybody_0.png", "spr_brattybody_1.png",
        "spr_brattyface_0.png", "spr_brattyface_1.png", "spr_brattyface_2.png", "spr_brattyface_3.png",
        "spr_brattyface_4.png", "spr_brattyface_5.png", "spr_brattyarm_l_0.png", "spr_brattyarm_r_0.png",
        
        # Catty sprites  
        "spr_cattybody_0.png", "spr_cattybody_1.png",
        "spr_cattyface_0.png", "spr_cattyface_1.png", "spr_cattyface_2.png", "spr_cattyface_3.png",
        "spr_cattyface_4.png", "spr_cattyface_5.png", "spr_cattyface_6.png", "spr_cattyface_7.png",
        "spr_catarm_0.png", "spr_catarm_1.png", "spr_catarm_2.png"
    ]
    
    for merchant_sprite in merchant_sprites:
        try:
            merchant_sprite_path = os.path.join(bratty_catty_shop_path, merchant_sprite)
            if os.path.exists(merchant_sprite_path):
                sprite_key = merchant_sprite.replace('.png', '')
                sprites[sprite_key] = pygame.image.load(merchant_sprite_path)
                print(f"  Loaded: {merchant_sprite}")
            else:
                print(f"  Note: Merchant sprite not found: {merchant_sprite}")
        except pygame.error as e:
            print(f"  Error loading merchant sprite {merchant_sprite}: {e}")
    
    print(f"Bratty & Catty sprites loading complete.")
    
    # Load Snowdin shopkeeper sprites (if available)
    print("Loading Snowdin shopkeeper sprites...")
    snowdin_shop_path = os.path.join("assets", "undertale", "Shops-20250721T005643Z-1-001", "Shops")
    
    # Try to find shopkeeper sprites in various possible locations
    shopkeeper_sprite_locations = [
        os.path.join(snowdin_shop_path, "Snowdin"),
        os.path.join("assets", "sprites"),
        os.path.join("assets", "undertale", "Characters")
    ]
    
    shopkeeper_sprites = [
        "spr_shopkeeper1_0.png", "spr_shopkeeper1_face0_0.png", "spr_shopkeeper1_face1_0.png",
        "spr_shopkeeper1_face2_0.png", "spr_shopkeeper1_face3_0.png", "spr_shopkeeper1_face4_0.png",
        "spr_shopkeeper1_face5_0.png", "spr_shopkeeper1_face6_0.png", "spr_shopkeeper1eyes_0.png",
        "spr_shopkeeper1eyes_1.png", "spr_shopkeeper1eyes_2.png", "spr_shopkeeper1eyes_3.png",
        "spr_shopkeeper1mouth_0.png", "spr_shopkeeper1mouth_1.png",
        "spr_shopkeeper2_body_0.png", "spr_shopkeeper2_arm_0.png", "spr_shopkeeper2_eyes_0.png"
    ]
    
    for shopkeeper_sprite in shopkeeper_sprites:
        sprite_loaded = False
        for location in shopkeeper_sprite_locations:
            try:
                shopkeeper_sprite_path = os.path.join(location, shopkeeper_sprite)
                if os.path.exists(shopkeeper_sprite_path):
                    sprite_key = shopkeeper_sprite.replace('.png', '')
                    sprites[sprite_key] = pygame.image.load(shopkeeper_sprite_path)
                    print(f"  Loaded: {shopkeeper_sprite} from {location}")
                    sprite_loaded = True
                    break
            except pygame.error as e:
                continue
        
        if not sprite_loaded:
            print(f"  Note: Shopkeeper sprite not found: {shopkeeper_sprite}")
    
    print(f"Snowdin shopkeeper sprites loading complete.")
    
    # Load Burgerpants shop sprites
    print("Loading Burgerpants shop sprites...")
    burgerpants_shop_path = os.path.join("assets", "undertale", "Shops-20250721T005643Z-1-001", "Shops", "Burgerpants")
    
    # Load Burgerpants sprites if folder exists
    if os.path.exists(burgerpants_shop_path):
        burgerpants_sprites = [
            "spr_bpants_face_0.png", "spr_bpants_face_1.png", "spr_bpants_face_2.png", "spr_bpants_face_3.png",
            "spr_bpants_face_4.png", "spr_bpants_face_5.png", "spr_bpants_face_6.png", "spr_bpants_arms_0.png",
        ]
        
        for bp_sprite in burgerpants_sprites:
            try:
                bp_sprite_path = os.path.join(burgerpants_shop_path, bp_sprite)
                if os.path.exists(bp_sprite_path):
                    sprite_key = bp_sprite.replace('.png', '')
                    sprites[sprite_key] = pygame.image.load(bp_sprite_path)
                    print(f"  Loaded: {bp_sprite}")
                else:
                    print(f"  Note: Burgerpants sprite not found: {bp_sprite}")
            except pygame.error as e:
                print(f"  Error loading Burgerpants sprite {bp_sprite}: {e}")
    
    print(f"Burgerpants sprites loading complete.")

# Load sprites
load_sprites()

# ANCHOR Undertale Font System
# File: font_system.py - Contains Undertale-style font rendering and text management

# --- Undertale Font System ---
class UndertaleFontRenderer:
    def __init__(self):
        # Load pre-rendered text sprites for special cases
        self.special_text_sprites = {}
        self.load_special_text_sprites()
        
        # Main font setup - use a monospace font that resembles Undertale's style
        self.setup_fonts()
    
    def load_special_text_sprites(self):
        """Load special pre-rendered text sprites from assets"""
        special_texts = [
            "congratulations", "missionfailed", "restart", 
            "restaurant", "shot"
        ]
        
        for text_name in special_texts:
            try:
                sprite_path = f"assets/sprites/spr_text_{text_name}_0.png"
                if os.path.exists(sprite_path):
                    self.special_text_sprites[text_name] = pygame.image.load(sprite_path).convert_alpha()
                    print(f"Loaded special text sprite: {text_name}")
            except Exception as e:
                print(f"Could not load special text sprite {text_name}: {e}")
    
    def setup_fonts(self):
        """Setup fonts that match Undertale's pixelated style"""
        # Try to find a suitable monospace/pixel font
        font_candidates = [
            "C:/Windows/Fonts/cour.ttf",      # Courier New - monospace
            "C:/Windows/Fonts/courbd.ttf",    # Courier New Bold
            "C:/Windows/Fonts/consola.ttf",   # Consolas - monospace coding font
            None  # Fallback to default
        ]
        
        self.font = None
        self.small_font = None
        
        # Try each font candidate
        for font_path in font_candidates:
            try:
                if font_path:
                    self.font = pygame.font.Font(font_path, 28)
                    self.small_font = pygame.font.Font(font_path, 20)
                    print(f"Using font: {font_path}")
                    break
                else:
                    # Fallback to default
                    self.font = pygame.font.Font(None, 32)
                    self.small_font = pygame.font.Font(None, 24)
                    print("Using default system font")
                    break
            except (FileNotFoundError, OSError):
                continue
        
        # If no font was set, use default
        if not self.font:
            self.font = pygame.font.Font(None, 32)
            self.small_font = pygame.font.Font(None, 24)
    
    def render_text(self, text, font_size="normal", color=WHITE, antialias=False):
        """Render text with Undertale-style appearance"""
        # Check if we have a special sprite for this text
        text_lower = text.lower().replace(" ", "")
        if text_lower in self.special_text_sprites:
            # Return the special sprite, scaled appropriately
            sprite = self.special_text_sprites[text_lower]
            scale_factor = 3 if font_size == "normal" else 2
            return pygame.transform.scale(sprite, 
                                        (sprite.get_width() * scale_factor, 
                                         sprite.get_height() * scale_factor))
        
        # Use regular font rendering with pixelated style
        selected_font = self.small_font if font_size == "small" else self.font
        
        # Render without antialiasing for pixel-perfect look
        text_surface = selected_font.render(text, antialias, color)
        
        # Scale up slightly to make it more pixelated
        if font_size != "small":
            # Scale up by 1.5x for a slightly more blocky appearance
            new_width = int(text_surface.get_width() * 1.2)
            new_height = int(text_surface.get_height() * 1.2)
            text_surface = pygame.transform.scale(text_surface, (new_width, new_height))
        
        return text_surface
    
    def get_text_size(self, text, font_size="normal"):
        """Get the size that rendered text would occupy"""
        text_surface = self.render_text(text, font_size, WHITE)
        return text_surface.get_size()

# Initialize the Undertale font system
undertale_font = UndertaleFontRenderer()

# Create global font references for backwards compatibility
font = undertale_font.font
small_font = undertale_font.small_font

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

# ANCHOR Utility Functions and Helpers
# File: utils.py - Contains drawing utilities, text helpers, and common functions

def draw_text_with_shadow(surface, text, x, y, color, font_obj=None, shadow_offset=2):
    """Draw text with a subtle shadow for better readability using Undertale font system."""
    if font_obj is None:
        # Use the Undertale font system
        text_surface = undertale_font.render_text(text, "normal", color)
        shadow_surface = undertale_font.render_text(text, "normal", (0, 0, 0))
    else:
        # Use the provided font object (for backwards compatibility)
        shadow_surface = font_obj.render(text, True, (0, 0, 0))
        text_surface = font_obj.render(text, True, color)
    
    # Draw shadow
    surface.blit(shadow_surface, (x + shadow_offset, y + shadow_offset))
    
    # Draw main text
    surface.blit(text_surface, (x, y))
    return text_surface.get_rect(x=x, y=y)

def wrap_text(text, max_width, font_obj=None, font_size="normal"):
    """Wrap text to fit within a maximum width."""
    # Safety check: ensure text is a string
    if not isinstance(text, str):
        if isinstance(text, list):
            return text  # Already wrapped
        text = str(text)  # Convert to string
    
    if font_obj is None:
        # Use Undertale font system for size calculation
        def get_text_width(text_str):
            return undertale_font.get_text_size(text_str, font_size)[0]
    else:
        # Use provided font object
        def get_text_width(text_str):
            return font_obj.size(text_str)[0]
    
    # If the entire text fits, return it as is
    if get_text_width(text) <= max_width:
        return [text]
    
    words = text.split(' ')
    lines = []
    current_line = ""
    
    for word in words:
        # Check if adding this word would exceed the width
        test_line = current_line + (" " if current_line else "") + word
        
        if get_text_width(test_line) <= max_width:
            current_line = test_line
        else:
            # If current line has content, add it to lines
            if current_line:
                lines.append(current_line)
                current_line = word
            else:
                # Word itself is too long, truncate it
                if get_text_width(word) > max_width:
                    # Truncate the word and add "..."
                    truncated = word
                    while get_text_width(truncated + "...") > max_width and len(truncated) > 0:
                        truncated = truncated[:-1]
                    lines.append(truncated + "...")
                    current_line = ""
                else:
                    current_line = word
    
    # Add the last line if it has content
    if current_line:
        lines.append(current_line)
    
    return lines

def draw_wrapped_text_with_shadow(surface, text, x, y, max_width, color, font_obj=None, shadow_offset=2, line_spacing=5):
    """Draw wrapped text with shadow that fits within max_width."""
    lines = wrap_text(text, max_width, font_obj)
    current_y = y
    
    for line in lines:
        draw_text_with_shadow(surface, line, x, current_y, color, font_obj, shadow_offset)
        # Calculate line height
        if font_obj is None:
            line_height = undertale_font.get_text_size(line, "normal")[1]
        else:
            line_height = font_obj.get_height()
        current_y += line_height + line_spacing
    
    return current_y  # Return the Y position after all lines

def draw_undertale_text(surface, text, x, y, color=WHITE, font_size="normal", shadow=True, shadow_offset=2):
    """Draw text using the Undertale font system with optional shadow."""
    if shadow:
        # Draw shadow
        shadow_surface = undertale_font.render_text(text, font_size, (0, 0, 0))
        surface.blit(shadow_surface, (x + shadow_offset, y + shadow_offset))
    
    # Draw main text
    text_surface = undertale_font.render_text(text, font_size, color)
    surface.blit(text_surface, (x, y))
    return text_surface.get_rect(x=x, y=y)

def draw_gradient_rect(surface, rect, color1, color2, vertical=True):
    """Draw a rectangle with a gradient fill."""
    # Convert RGBA to RGB if needed (pygame drawing functions don't support alpha in color tuples)
    if len(color1) > 3:
        color1 = color1[:3]
    if len(color2) > 3:
        color2 = color2[:3]
        
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
    text_surface = undertale_font.render_text(health_text, "small", WHITE)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    
    # Text shadow
    shadow_surface = undertale_font.render_text(health_text, "small", BLACK)
    surface.blit(shadow_surface, (text_rect.x + 1, text_rect.y + 1))
    surface.blit(text_surface, text_rect)

# ANCHOR Particle Effects System
# File: particles.py - Contains particle effect creation and management

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

# ANCHOR Color Schemes and UI Themes
# File: ui_themes.py - Contains color schemes and UI theming

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

# ANCHOR Advanced Animation Manager
# File: animation_manager.py - Contains advanced animation system for smooth effects

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

# ANCHOR Audio System and Sound Management
# File: audio.py - Contains sound loading, music management, and audio utilities

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

def play_music(music_state, loop=True, volume=None):
    """Play background music for the given state."""
    global current_music, current_music_state
    
    # Use game settings volume if no specific volume is provided
    if volume is None:
        volume = game_settings["music_volume"]
    
    # Don't restart the same music
    if current_music_state == music_state and pygame.mixer.music.get_busy():
        # Still apply volume change in case settings changed
        pygame.mixer.music.set_volume(volume)
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

# ANCHOR Enemy Definitions
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

# ANCHOR Item System and Equipment
# File: items.py - Contains all item classes, weapons, armor, potions, and treasure

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
# ANCHOR Weapon and Equipment Definitions
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
# ANCHOR Entity System and Game Characters
# File: entities.py - Contains base Entity class, Player, Enemy, and Shopkeeper classes

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
        
        # Animation properties
        self.is_moving = False
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 200  # milliseconds per frame
        self.last_move_time = 0
        
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

    def start_movement_animation(self):
        """Start movement animation when player begins moving"""
        self.is_moving = True
        self.last_move_time = pygame.time.get_ticks()
        self.animation_timer = 0

    def stop_movement_animation(self):
        """Stop movement animation when player stops moving"""
        self.is_moving = False
        self.animation_frame = 0

    def update_animation(self):
        """Update movement animation frames"""
        current_time = pygame.time.get_ticks()
        
        # If moving, cycle through animation frames
        if self.is_moving:
            if current_time - self.animation_timer > self.animation_speed:
                self.animation_timer = current_time
                # Get the number of available frames for this character and direction
                animation_key = f"{self.char_class}_{self.direction}"
                if animation_key in portrait_animations:
                    max_frames = len(portrait_animations[animation_key].frames)
                    self.animation_frame = (self.animation_frame + 1) % max_frames
                else:
                    # Default to 4 frames if no specific animation found
                    self.animation_frame = (self.animation_frame + 1) % 4
        
        # Stop movement animation if we haven't moved recently
        if current_time - self.last_move_time > 100:  # Stop animation 100ms after last movement
            self.stop_movement_animation()

    def get_current_sprite_key(self):
        """Get the current animated sprite key based on direction and animation frame"""
        return f"player_{self.char_class}_{self.direction}"
    
    def get_current_animated_frame(self):
        """Get the current animated frame surface for the player"""
        if self.is_moving:
            animation_key = f"{self.char_class}_{self.direction}"
            if animation_key in portrait_animations:
                return portrait_animations[animation_key].get_current_frame()
        
        # Return static frame if not moving or no animation available
        static_key = f"player_{self.char_class}_{self.direction}"
        if static_key in sprites:
            return sprites[static_key]
        
        # Final fallback
        fallback_key = f"player_{self.char_class}"
        if fallback_key in sprites:
            return sprites[fallback_key]
        
        return None

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
        
        # Initialize gold based on enemy type and level
        base_gold = max(5, base_xp // 2)  # Base gold is roughly half the XP value, minimum 5
        self.gold = int(base_gold * level_multiplier)
        
        self.weapon_drops = []  # List of possible weapon drops
        
        # Door guardian properties
        self.is_door_guardian = False
        self.special_drops = []  # Special items for door guardians

class Shopkeeper:
    def __init__(self, x, y, merchant_type="temmie"):
        self.x = x
        self.y = y
        self.merchant_type = merchant_type
        
        # Configure merchant based on type
        if merchant_type == "temmie":
            self.name = "Temmie"
            self.icon = "temmie"
            self.specialization = "weapons"
            self.dialogue = ["* hOI!", "* welcom to...", "* da TEM SHOP!!!", "* tEM sell u WEAPONS!"]
        elif merchant_type == "bratty_catty":
            self.name = "Bratty & Catty"
            self.icon = "bratty_catty" 
            self.specialization = "armor"
            self.dialogue = ["* Like, OMG, hi!", "* We're like, totally selling armor!", "* It's like, super cute AND protective!", "* You should like, totally buy some!"]
        elif merchant_type == "snowdin_shopkeeper":
            self.name = "Snowdin Shopkeeper"
            self.icon = "snowdin_shopkeeper"
            self.specialization = "potions"
            self.dialogue = ["* Welcome to Snowdin Shop!", "* I've got the best potions in the Underground!", "* They'll keep you warm and healthy!", "* Perfect for your journey!"]
        elif merchant_type == "burgerpants":
            self.name = "Burgerpants"
            self.icon = "burgerpants"
            self.specialization = "mixed"  # Sells everything but less variety
            self.dialogue = ["* Ugh... welcome to the shop.", "* I guess you want items?", "* These'll keep you alive...", "* ...probably."]
        else:
            # Default fallback
            self.name = "Shopkeeper"
            self.icon = "temmie"
            self.specialization = "mixed"
            self.dialogue = ["* Welcome to my shop!", "* Take a look around!", "* I have items for sale!", "* Come back anytime!"]
        
        self.inventory = []  # Shop's inventory
        self.generate_shop_inventory()
    
    def generate_shop_inventory(self):
        """Generate items for the shop based on merchant specialization."""
        self.inventory = []
        
        if self.specialization == "weapons":
            # Temmie sells weapons (4-6 weapons)
            num_items = random.randint(4, 6)
            available_weapons = ALL_WEAPONS
            
            for _ in range(num_items):
                if available_weapons:
                    chosen_weapon = random.choice(available_weapons)
                    weapon_copy = Weapon(chosen_weapon.name, chosen_weapon.attack_bonus, 
                                       chosen_weapon.allowed_classes, chosen_weapon.rarity, 
                                       chosen_weapon.sprite_name)
                    self.inventory.append(weapon_copy)
        
        elif self.specialization == "armor":
            # Bratty & Catty sell armor (4-6 pieces)
            num_items = random.randint(4, 6)
            available_armor = ALL_ARMOR
            
            for _ in range(num_items):
                if available_armor:
                    chosen_armor = random.choice(available_armor)
                    armor_copy = Armor(chosen_armor.name, chosen_armor.defense_bonus,
                                     chosen_armor.allowed_classes, chosen_armor.rarity,
                                     chosen_armor.sprite_name)
                    self.inventory.append(armor_copy)
        
        elif self.specialization == "potions":
            # Snowdin Shopkeeper sells potions (5-8 potions)
            num_items = random.randint(5, 8)
            
            for _ in range(num_items):
                chosen_potion = random.choice(ALL_POTIONS)
                potion_copy = Potion(chosen_potion.name, chosen_potion.hp_gain, chosen_potion.rarity)
                self.inventory.append(potion_copy)
        
        else:  # mixed specialization
            # Burgerpants sells everything but smaller selection
            num_items = random.randint(3, 5)
            
            for _ in range(num_items):
                item_type = random.choice(["weapon", "armor", "potion"])
                
                if item_type == "weapon":
                    chosen_weapon = random.choice(ALL_WEAPONS)
                    weapon_copy = Weapon(chosen_weapon.name, chosen_weapon.attack_bonus, 
                                       chosen_weapon.allowed_classes, chosen_weapon.rarity, 
                                       chosen_weapon.sprite_name)
                    self.inventory.append(weapon_copy)
                elif item_type == "armor":
                    chosen_armor = random.choice(ALL_ARMOR)
                    armor_copy = Armor(chosen_armor.name, chosen_armor.defense_bonus,
                                     chosen_armor.allowed_classes, chosen_armor.rarity,
                                     chosen_armor.sprite_name)
                    self.inventory.append(armor_copy)
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

# ANCHOR Dungeon Generation and World Building
# File: dungeon.py - Contains dungeon generation algorithms and world management

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
            
        # Chance to place a door guardian enemy in the tunnel
        if random.random() < 0.15:  # 15% chance for door guardian
            guard_x = (min(x1, x2) + max(x1, x2)) // 2  # Place in middle of tunnel
            guard_y = y
            
            # Check if position is valid and no existing enemy
            if (self.is_valid_spawn_position(guard_x, guard_y) and 
                not any(e.x == guard_x and e.y == guard_y for e in self.enemies)):
                # Create a stronger enemy as door guardian
                enemy_type = self.get_door_guardian_type()
                guardian = Enemy(guard_x, guard_y, enemy_type, self.level)
                guardian.is_door_guardian = True  # Mark as door guardian
                
                # Door guardians are stronger
                guardian.max_hp = int(guardian.max_hp * 1.3)
                guardian.hp = guardian.max_hp
                guardian.base_attack = int(guardian.base_attack * 1.2)
                guardian.base_defense = int(guardian.base_defense * 1.1)
                
                # Better loot for door guardians
                guardian.gold = int(guardian.gold * 1.5)
                if enemy_type == "temmie":
                    # Temmie door guardian has special shop items
                    guardian.special_drops = ["tem_flakes", "tem_armor"]
                
                self.enemies.append(guardian)

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.grid[y][x] = UI["floor"]
            
        # Chance to place a door guardian enemy in the tunnel
        if random.random() < 0.15:  # 15% chance for door guardian
            guard_x = x
            guard_y = (min(y1, y2) + max(y1, y2)) // 2  # Place in middle of tunnel
            
            # Check if position is valid and no existing enemy
            if (self.is_valid_spawn_position(guard_x, guard_y) and 
                not any(e.x == guard_x and e.y == guard_y for e in self.enemies)):
                # Create a stronger enemy as door guardian
                enemy_type = self.get_door_guardian_type()
                guardian = Enemy(guard_x, guard_y, enemy_type, self.level)
                guardian.is_door_guardian = True  # Mark as door guardian
                
                # Door guardians are stronger
                guardian.max_hp = int(guardian.max_hp * 1.3)
                guardian.hp = guardian.max_hp
                guardian.base_attack = int(guardian.base_attack * 1.2)
                guardian.base_defense = int(guardian.base_defense * 1.1)
                
                # Better loot for door guardians
                guardian.gold = int(guardian.gold * 1.5)
                if enemy_type == "temmie":
                    # Temmie door guardian has special shop items
                    guardian.special_drops = ["tem_flakes", "tem_armor"]
                
                self.enemies.append(guardian)
    
    def get_door_guardian_type(self):
        """Get appropriate enemy type for door guardians based on level."""
        if self.level == 1:
            # Early level door guardians
            return random.choice(["froggit", "whimsun", "vegetoid"])
        elif self.level == 2:
            # Mid level door guardians  
            return random.choice(["loox", "moldsmal", "temmie"])
        elif self.level == 3:
            # Higher level door guardians
            return random.choice(["pyrope", "vulkin", "temmie"])
        else:
            # High level door guardians
            return random.choice(["temmie", "lesser_dog", "greater_dog"])

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
        
        # Shop room (80% chance for testing, max 1 per level) - increased for animation testing
        if not hasattr(self, 'shop_room_placed'):
            self.shop_room_placed = False
        if not self.shop_room_placed and random.random() < 0.80:
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
            attempts = 0
            max_attempts = 50  # Prevent infinite loops
            
            while attempts < max_attempts:
                x = random.randint(room.x1 + 1, room.x2 - 1)
                y = random.randint(room.y1 + 1, room.y2 - 1)
                
                # Check if position is valid for spawning and no existing enemy
                if (self.is_valid_spawn_position(x, y) and 
                    not any(e.x == x and e.y == y for e in self.enemies)):
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
                    break  # Successfully placed enemy
                
                attempts += 1
        
        # Higher chance for treasure chests (60% instead of 25%)
        if random.random() < 0.60:
            attempts = 0
            max_attempts = 50
            
            while attempts < max_attempts:
                chest_x = random.randint(room.x1 + 1, room.x2 - 1)
                chest_y = random.randint(room.y1 + 1, room.y2 - 1)
                
                # Check if position is valid for spawning
                if self.is_valid_spawn_position(chest_x, chest_y):
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
                    break  # Successfully placed chest
                
                attempts += 1
        
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
        """Place content for a shop room - randomly choose merchant type."""
        # Place shopkeeper at the center of the room
        center_x, center_y = room.center()
        
        # Randomly choose merchant type based on level and chance
        merchant_types = ["temmie", "bratty_catty", "snowdin_shopkeeper", "burgerpants"]
        
        # Weight the selection based on dungeon level for variety
        if self.level == 1:
            # Early level - mostly Temmie (weapons needed early)
            merchant_type = random.choices(
                merchant_types,
                weights=[50, 20, 20, 10]  # Favor Temmie for weapons
            )[0]
        elif self.level == 2:
            # Mid level - balanced mix
            merchant_type = random.choices(
                merchant_types,
                weights=[30, 30, 25, 15]  # More balanced
            )[0]
        else:
            # Higher levels - any merchant is equally useful
            merchant_type = random.choices(
                merchant_types,
                weights=[25, 25, 25, 25]  # Equal chance
            )[0]
        
        shopkeeper = Shopkeeper(center_x, center_y, merchant_type)
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
            attempts = 0
            max_attempts = 50  # Prevent infinite loops
            
            while attempts < max_attempts:
                x = random.randint(room.x1 + 1, room.x2 - 1)
                y = random.randint(room.y1 + 1, room.y2 - 1)
                
                # Check if position is valid for spawning and no existing enemy
                if (self.is_valid_spawn_position(x, y) and 
                    not any(e.x == x and e.y == y for e in self.enemies)):
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
                    break  # Successfully placed enemy
                
                attempts += 1
        
        # Balanced treasure chest placement (30% chance - increased from 25%)
        if random.random() < 0.30:
            attempts = 0
            max_attempts = 50
            
            while attempts < max_attempts:
                chest_x = random.randint(room.x1 + 1, room.x2 - 1)
                chest_y = random.randint(room.y1 + 1, room.y2 - 1)
                
                # Check if position is valid for spawning
                if self.is_valid_spawn_position(chest_x, chest_y):
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
                    break  # Successfully placed chest
                
                attempts += 1
        
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
    
    def is_valid_spawn_position(self, x, y):
        """Check if a position is valid for spawning enemies or items.
        Prevents spawning on stairs, doors, or impassable tiles."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        
        # Check tile type
        tile_type = self.grid[y][x]
        
        # Don't spawn on stairs/doors or walls
        if tile_type in [UI["stairs"], UI["wall"]]:
            return False
        
        # Only allow spawning on floor tiles
        return tile_type == UI["floor"]

# ANCHOR Main Game Class and Game Loop
# File: game.py - Contains the main Game class with game loop, state management, 
#                  UI rendering, combat system, and all game logic

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
        # Pause system
        self.is_paused = False
        self.previous_game_state = None
        
        # Multi-save system
        self.selected_save_idx = 0
        self.save_files = []
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
        turn_surface = undertale_font.render_text(turn_text, "small", ENHANCED_COLORS['text_primary'])
        turn_rect = turn_surface.get_rect(center=(SCREEN_WIDTH // 2, title_y + 70))
        screen.blit(turn_surface, turn_rect)
        
        # Enhanced players section
        player_section_x = 50
        player_section_y = 150
        
        # Player panel background - increased width for skill panels
        player_panel_rect = pygame.Rect(player_section_x - 20, player_section_y - 30, 620, 
                                       len(self.players) * 120 + 80)  # Extra space for title and skills
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
                glow_rect = pygame.Rect(player_section_x - 10, y_pos - 10, 600, 110)  # Increased width for skills
                draw_gradient_rect(screen, glow_rect, (255, 255, 0, 50), (255, 215, 0, 30))
                pygame.draw.rect(screen, ENHANCED_COLORS['accent_gold'], glow_rect, width=3, border_radius=8)
            
            # Player name and class with animated portraits and icons - with text wrapping
            player_text_max_width = 480  # Max width for player text display
            
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
            
            # Use text wrapping to handle long player status text
            max_text_width = player_text_max_width
            if undertale_font.get_text_size(status, "normal")[0] > max_text_width:
                wrapped_status = wrap_text(status, max_text_width, font)
                draw_wrapped_text_with_shadow(screen, wrapped_status, player_section_x + 60, y_pos, 
                                             max_text_width, text_color, font, 1, 5)
            else:
                draw_text_with_shadow(screen, status, player_section_x + 60, y_pos, text_color, font, 1)
            
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
                mana_surface = undertale_font.render_text(mana_text, "small", ENHANCED_COLORS['text_primary'])
                mana_text_rect = mana_surface.get_rect(center=(player_section_x + 160, mana_bar_y + 10))
                screen.blit(mana_surface, mana_text_rect)
            
            # Enhanced skill icon and status with proper text wrapping
            skill_icon_x = player_section_x + 280
            skill_icon_y = y_pos + 25
            skill_panel_width = 300  # Increased width for better text display
            
            # Skill background panel
            skill_bg_rect = pygame.Rect(skill_icon_x - 5, skill_icon_y - 5, skill_panel_width, 58)
            draw_gradient_rect(screen, skill_bg_rect, (30, 30, 40), (50, 50, 60))
            pygame.draw.rect(screen, ENHANCED_COLORS['accent_silver'], skill_bg_rect, width=1, border_radius=5)
            
            # Draw class skill icon
            if player.char_class == "warrior" and "skill_power_strike" in sprites:
                screen.blit(sprites["skill_power_strike"], (skill_icon_x, skill_icon_y))
            elif player.char_class == "mage" and "skill_fireball" in sprites:
                screen.blit(sprites["skill_fireball"], (skill_icon_x, skill_icon_y))
            elif player.char_class == "archer" and "skill_double_shot" in sprites:
                screen.blit(sprites["skill_double_shot"], (skill_icon_x, skill_icon_y))
            
            # Skill status text with wrapping
            skill_text_x = skill_icon_x + 55
            skill_text_max_width = skill_panel_width - 70  # Account for icon and padding
            
            if hasattr(player, 'skill_cooldown') and player.skill_cooldown > 0:
                cooldown_text = f"Cooldown: {player.skill_cooldown}"
                if undertale_font.get_text_size(cooldown_text, "small")[0] > skill_text_max_width:
                    wrapped_cooldown = wrap_text(cooldown_text, skill_text_max_width, small_font)
                    draw_wrapped_text_with_shadow(screen, wrapped_cooldown, skill_text_x, skill_icon_y + 5, 
                                                 skill_text_max_width, ENHANCED_COLORS['danger_red'], small_font, 1, 5)
                else:
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
                    skill_text = skill_name + " ✓"
                    if undertale_font.get_text_size(skill_text, "small")[0] > skill_text_max_width:
                        wrapped_skill = wrap_text(skill_text, skill_text_max_width, small_font)
                        draw_wrapped_text_with_shadow(screen, wrapped_skill, skill_text_x, skill_icon_y + 5, 
                                                     skill_text_max_width, ENHANCED_COLORS['success_green'], small_font, 1, 5)
                    else:
                        draw_text_with_shadow(screen, skill_text, skill_text_x, skill_icon_y + 5, 
                                            ENHANCED_COLORS['success_green'], small_font, 1)
                elif skill_name:
                    level_req = 2 if player.char_class in ["warrior", "archer"] else 3
                    req_text = f"{skill_name} (Lv{level_req})"
                    if undertale_font.get_text_size(req_text, "small")[0] > skill_text_max_width:
                        wrapped_req = wrap_text(req_text, skill_text_max_width, small_font)
                        draw_wrapped_text_with_shadow(screen, wrapped_req, skill_text_x, skill_icon_y + 5, 
                                                     skill_text_max_width, ENHANCED_COLORS['text_disabled'], small_font, 1, 5)
                    else:
                        draw_text_with_shadow(screen, req_text, skill_text_x, skill_icon_y + 5, 
                                            ENHANCED_COLORS['text_disabled'], small_font, 1)

        # Enhanced enemies section - adjusted positioning for wider skill panels
        enemy_section_x = SCREEN_WIDTH - 570  # Moved left to accommodate wider skill panels
        enemy_section_y = 150
        
        # Enemy panel background - increased width to match
        enemy_panel_rect = pygame.Rect(enemy_section_x - 20, enemy_section_y - 30, 540, 
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
                glow_rect = pygame.Rect(enemy_section_x - 10, y_pos - 10, 520, 90)  # Increased width
                draw_gradient_rect(screen, glow_rect, (255, 0, 0, 50), (255, 100, 100, 30))
                pygame.draw.rect(screen, ENHANCED_COLORS['danger_red'], glow_rect, width=3, border_radius=8)
            
            # Enemy sprite and name with animated portraits - with text wrapping
            enemy_text_max_width = 420  # Max width for enemy text display
            
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
            
            # Use text wrapping to handle long enemy status text
            max_text_width = enemy_text_max_width
            if undertale_font.get_text_size(status, "normal")[0] > max_text_width:
                draw_wrapped_text_with_shadow(screen, status, enemy_section_x + 60, y_pos, 
                                             max_text_width, text_color, font, 1, 5)
            else:
                draw_text_with_shadow(screen, status, enemy_section_x + 60, y_pos, text_color, font, 1)
            
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
            
            # Current player turn indicator with text wrapping for long names
            turn_text = f"{current_entity.name}'s Turn"
            max_turn_text_width = SCREEN_WIDTH - 200  # Leave margin on both sides
            
            if undertale_font.get_text_size(turn_text, "normal")[0] > max_turn_text_width:
                wrapped_turn = wrap_text(turn_text, max_turn_text_width, font)
                
                # Calculate centered x position for wrapped text
                if len(wrapped_turn) > 0:
                    first_line_width = font.get_width(wrapped_turn[0]) if hasattr(font, 'get_width') else len(wrapped_turn[0]) * 10
                    centered_x = (SCREEN_WIDTH - first_line_width) // 2
                else:
                    centered_x = SCREEN_WIDTH // 2
                
                draw_wrapped_text_with_shadow(screen, wrapped_turn, centered_x, SCREEN_HEIGHT - 200, 
                                             max_turn_text_width, YELLOW, font, 2, 5)
            else:
                # Draw single line centered
                turn_surface = font.render(turn_text, True, YELLOW)
                turn_rect = turn_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 200))
                screen.blit(turn_surface, turn_rect)
        else:
            # Enemy turn with text wrapping for long names  
            turn_text = f"{current_entity.name} is attacking..."
            max_turn_text_width = SCREEN_WIDTH - 200  # Leave margin on both sides
            
            if undertale_font.get_text_size(turn_text, "normal")[0] > max_turn_text_width:
                wrapped_turn = wrap_text(turn_text, max_turn_text_width, font)
                
                # Calculate centered x position for wrapped text
                if len(wrapped_turn) > 0:
                    first_line_width = font.get_width(wrapped_turn[0]) if hasattr(font, 'get_width') else len(wrapped_turn[0]) * 10
                    centered_x = (SCREEN_WIDTH - first_line_width) // 2
                else:
                    centered_x = SCREEN_WIDTH // 2
                    
                draw_wrapped_text_with_shadow(screen, wrapped_turn, centered_x, SCREEN_HEIGHT - 120, 
                                             max_turn_text_width, RED, font, 2, 5)
            else:
                # Draw single line centered
                turn_surface = font.render(turn_text, True, RED)
                turn_rect = turn_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120))
                screen.blit(turn_surface, turn_rect)

        # Draw messages with text wrapping
        if self.messages:
            msg_y = SCREEN_HEIGHT - 250
            msg_surface = pygame.Surface((SCREEN_WIDTH, 80))
            msg_surface.set_alpha(200)
            msg_surface.fill(BLACK)
            screen.blit(msg_surface, (0, msg_y))
            
            current_y = msg_y + 10
            msg_width = SCREEN_WIDTH - 100  # 50px margin on each side
            messages_shown = 0
            
            for msg in list(self.messages)[:3]:  # Show only last 3 messages in combat
                if messages_shown >= 3 or current_y > msg_y + 70:
                    break
                    
                # Wrap long messages to fit within the screen
                wrapped_lines = wrap_text(msg, msg_width, font_size="normal")
                
                for line in wrapped_lines:
                    if current_y > msg_y + 70:
                        break  # Stop if we're running out of space
                    
                    self.draw_text(line, 50, current_y, WHITE)
                    current_y += 20  # Line spacing
                
                messages_shown += 1
                current_y += 5  # Extra spacing between messages
        
        # Draw damage numbers
        draw_damage_numbers(screen)
                    
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
        elif key == pygame.K_q:  # Pause menu from inventory
            play_sound("menu_confirm", 0.5)
            self.inventory_state = "closed"
            # Pause the game instead of going directly to main menu
            self.is_paused = True
            self.previous_game_state = "playing"
            self.game_state = "paused"
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
            "Q : Pause Menu",
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
        
        # Show inventory management instructions with wrapping
        if current_y < SCREEN_HEIGHT - 100:
            instruction_width = SCREEN_WIDTH - 280  # Account for margins
            
            instruction1 = "Inventory Limits: Weapons/Armor have limited slots"
            instruction2 = "Better items will auto-replace when looting chests"
            
            # Wrap instructions if needed
            wrapped1 = wrap_text(instruction1, instruction_width, font_size="small")
            wrapped2 = wrap_text(instruction2, instruction_width, font_size="small")
            
            for line in wrapped1:
                draw_text_with_shadow(screen, line, 140, current_y + 20, ENHANCED_COLORS['text_secondary'], small_font, 1)
                current_y += 20
                
            for line in wrapped2:
                draw_text_with_shadow(screen, line, 140, current_y + 20, ENHANCED_COLORS['text_secondary'], small_font, 1)
                current_y += 20
        
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
        
        # Calculate available width for text to prevent overflow
        available_width = SCREEN_WIDTH - text_x - 50  # 50px margin from right edge
        
        # Use text wrapping for long item names/descriptions
        if undertale_font.get_text_size(item_text, "small")[0] > available_width:
            # Wrap the text if it's too long
            wrapped_lines = wrap_text(item_text, available_width, font_size="small")
            for i, line in enumerate(wrapped_lines[:2]):  # Show maximum 2 lines
                draw_text_with_shadow(screen, line, text_x, y_pos + i * 12, item_color, small_font, 1)
        else:
            draw_text_with_shadow(screen, item_text, text_x, y_pos, item_color, small_font, 1)

    def add_message(self, text):
        self.messages.appendleft(text)
    
    def draw_shop_screen(self):
        """Draw the Undertale-style shop interface with different merchant portraits."""
        # Black background like Undertale
        screen.fill(BLACK)
        
        # Get current shopkeeper type to determine background
        merchant_type = self.current_shopkeeper.merchant_type if self.current_shopkeeper else "temmie"
        
        # Draw appropriate shop background (LARGER SIZE)
        bg_sprite = None
        if merchant_type == "bratty_catty" and "bg_brattybg" in sprites:
            bg_sprite = sprites["bg_brattybg"]
        elif "bg_temshop" in sprites:
            bg_sprite = sprites["bg_temshop"]  # Fallback to Temmie shop for others
        
        if bg_sprite:
            # Scale up the background to be much larger
            bg_scale = 2.5  # Make background 2.5x bigger
            scaled_bg = pygame.transform.scale(bg_sprite, 
                                             (int(bg_sprite.get_width() * bg_scale), 
                                              int(bg_sprite.get_height() * bg_scale)))
            
            # Center the larger background
            bg_x = (SCREEN_WIDTH - scaled_bg.get_width()) // 2
            bg_y = 30  # Position near top
            screen.blit(scaled_bg, (bg_x, bg_y))
            
            # Position character sprite components on top of larger background
            character_center_x = bg_x + scaled_bg.get_width() // 2
            character_center_y = bg_y + scaled_bg.get_height() // 2
            
        else:
            # Fallback positioning if no background
            character_center_x = SCREEN_WIDTH // 2
            character_center_y = 200
        
        # Get current shopkeeper type and draw appropriate character
        merchant_type = self.current_shopkeeper.merchant_type if self.current_shopkeeper else "temmie"
        character_scale = 3.0  # Make characters 3x bigger to take up more screen
        
        if merchant_type == "temmie":
            self.draw_temmie_portrait(character_center_x, character_center_y, character_scale)
        elif merchant_type == "bratty_catty":
            self.draw_bratty_catty_portrait(character_center_x, character_center_y, character_scale)
        elif merchant_type == "snowdin_shopkeeper":
            self.draw_snowdin_shopkeeper_portrait(character_center_x, character_center_y, character_scale)
        elif merchant_type == "burgerpants":
            self.draw_burgerpants_portrait(character_center_x, character_center_y, character_scale)
        else:
            # Fallback for unknown merchant types
            self.draw_generic_merchant_sprite(character_center_x, character_center_y, character_scale, merchant_type)
        
        # Undertale-style dialogue box (left side)
        dialogue_x = 50
        dialogue_y = 400
        dialogue_width = 600
        dialogue_height = 150
        
        # Draw dialogue box background (white with black border)
        dialogue_rect = pygame.Rect(dialogue_x, dialogue_y, dialogue_width, dialogue_height)
        pygame.draw.rect(screen, WHITE, dialogue_rect)
        pygame.draw.rect(screen, BLACK, dialogue_rect, 4)  # Black border
        
        # Get merchant-specific dialogue
        dialogue_lines = self.current_shopkeeper.dialogue if self.current_shopkeeper else ["* Welcome to my shop!"]
        
        for i, line in enumerate(dialogue_lines[:3]):  # Show max 3 lines
            text_y = dialogue_y + 20 + i * 30
            # Use undertale font for authentic feel
            if undertale_font:
                text_surface = undertale_font.render_text(line, "normal", BLACK)
                screen.blit(text_surface, (dialogue_x + 20, text_y))
            else:
                # Fallback to regular font
                text_surface = font.render(line, True, BLACK)
                screen.blit(text_surface, (dialogue_x + 20, text_y))
        
        # Menu options (right side, Undertale style)
        menu_x = 750
        menu_y = 400
        menu_width = 200
        menu_height = 200
        
        # Menu background (white with black border)
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        pygame.draw.rect(screen, WHITE, menu_rect)
        pygame.draw.rect(screen, BLACK, menu_rect, 4)
        
        # Menu options
        menu_options = ["❤ Buy", "Sell", "Talk", "Exit"]
        
        for i, option in enumerate(menu_options):
            option_y = menu_y + 20 + i * 40
            
            # Highlight selected option (heart indicates selection in Undertale)
            if (self.shop_mode == "buy" and i == 0) or (self.shop_mode == "sell" and i == 1):
                # Selected option - already has heart
                text_color = BLACK
            elif i == 0 and self.shop_mode != "buy":
                # Unselected buy option - remove heart
                option = "Buy"
                text_color = BLACK
            else:
                text_color = BLACK
            
            if undertale_font:
                text_surface = undertale_font.render_text(option, "normal", text_color)
                screen.blit(text_surface, (menu_x + 20, option_y))
            else:
                text_surface = font.render(option, True, text_color)
                screen.blit(text_surface, (menu_x + 20, option_y))
        
        # Show current player and gold (bottom left)
        current_player = self.players[self.selected_player_idx]
        player_info_y = SCREEN_HEIGHT - 100
        
        player_text = f"Player: {current_player.name}"
        gold_text = f"Gold: {current_player.gold}G"
        
        if undertale_font:
            player_surface = undertale_font.render_text(player_text, "small", WHITE)
            gold_surface = undertale_font.render_text(gold_text, "small", (255, 215, 0))  # Gold color
        else:
            player_surface = small_font.render(player_text, True, WHITE)
            gold_surface = small_font.render(gold_text, True, (255, 215, 0))
        
        screen.blit(player_surface, (50, player_info_y))
        screen.blit(gold_surface, (50, player_info_y + 25))
        
        # Draw shop inventory or sell items based on mode
        if self.shop_mode == "buy":
            self.draw_undertale_shop_buy_items()
        else:
            self.draw_undertale_shop_sell_items()
        
        # Instructions (bottom right)
        instructions = [
            "TAB - Switch Buy/Sell",
            "↑↓ - Navigate items",
            "← → - Switch player",
            "ENTER - Confirm",
            "ESC - Exit"
        ]
        
        inst_y = SCREEN_HEIGHT - 120
        for i, instruction in enumerate(instructions):
            if undertale_font:
                inst_surface = undertale_font.render_text(instruction, "small", WHITE)
            else:
                inst_surface = small_font.render(instruction, True, WHITE)
            screen.blit(inst_surface, (SCREEN_WIDTH - 250, inst_y + i * 20))
        
        pygame.display.flip()
    
    def draw_temmie_portrait(self, center_x, center_y, scale):
        """Draw Temmie's layered portrait sprites."""
        # Draw Temmie body
        if "spr_5_tembody_0" in sprites:
            body_sprite = sprites["spr_5_tembody_0"]
            scaled_body = pygame.transform.scale(body_sprite, 
                                               (int(body_sprite.get_width() * scale), 
                                                int(body_sprite.get_height() * scale)))
            body_x = center_x - scaled_body.get_width() // 2
            body_y = center_y - scaled_body.get_height() // 2
            screen.blit(scaled_body, (body_x, body_y))
        
        # Draw Temmie's hat
        if "spr_temhat_0" in sprites:
            hat_sprite = sprites["spr_temhat_0"]
            scaled_hat = pygame.transform.scale(hat_sprite, 
                                              (int(hat_sprite.get_width() * scale), 
                                               int(hat_sprite.get_height() * scale)))
            hat_x = center_x - scaled_hat.get_width() // 2
            hat_y = center_y - scaled_hat.get_height() // 2 - int(20 * scale)
            screen.blit(scaled_hat, (hat_x, hat_y))
        
        # Draw animated eyes
        current_time = pygame.time.get_ticks()
        eye_frame = (current_time // 500) % 6
        eye_sprite_name = f"spr_5_eyes{eye_frame + 1}_0"
        
        if eye_sprite_name in sprites:
            eye_sprite = sprites[eye_sprite_name]
            scaled_eyes = pygame.transform.scale(eye_sprite, 
                                                (int(eye_sprite.get_width() * scale), 
                                                 int(eye_sprite.get_height() * scale)))
            eye_x = center_x - scaled_eyes.get_width() // 2
            eye_y = center_y - scaled_eyes.get_height() // 2
            screen.blit(scaled_eyes, (eye_x, eye_y))
        
        # Draw animated mouth
        mouth_frame = (current_time // 800) % 3
        if mouth_frame == 0 and "spr_5_mouth1_0" in sprites:
            mouth_sprite = sprites["spr_5_mouth1_0"]
        elif mouth_frame == 1 and "spr_5_mouth2_0" in sprites:
            mouth_sprite = sprites["spr_5_mouth2_0"]
        elif "spr_5_mouth3_0" in sprites:
            mouth_sprite = sprites["spr_5_mouth3_0"]
        else:
            mouth_sprite = None
            
        if mouth_sprite:
            scaled_mouth = pygame.transform.scale(mouth_sprite, 
                                                 (int(mouth_sprite.get_width() * scale), 
                                                  int(mouth_sprite.get_height() * scale)))
            mouth_x = center_x - scaled_mouth.get_width() // 2
            mouth_y = center_y - scaled_mouth.get_height() // 2 + int(10 * scale)
            screen.blit(scaled_mouth, (mouth_x, mouth_y))
        
        # Draw Temmie's animated shop counter/box in front with gentle bobbing motion
        tembox_hover_offset = int(3 * scale * math.sin(current_time * 0.002))  # Gentle bobbing motion
        
        if "spr_tembox_0" in sprites:
            box_sprite = sprites["spr_tembox_0"]
            scaled_box = pygame.transform.scale(box_sprite, 
                                              (int(box_sprite.get_width() * scale), 
                                               int(box_sprite.get_height() * scale)))
            box_x = center_x - scaled_box.get_width() // 2
            box_y = center_y + int(20 * scale) + tembox_hover_offset  # Position with animation
            screen.blit(scaled_box, (box_x, box_y))
        elif "spr_5_tembox_0" in sprites:
            # Alternative box sprite name
            box_sprite = sprites["spr_5_tembox_0"]
            scaled_box = pygame.transform.scale(box_sprite, 
                                              (int(box_sprite.get_width() * scale), 
                                               int(box_sprite.get_height() * scale)))
            box_x = center_x - scaled_box.get_width() // 2
            box_y = center_y + int(10 * scale) + tembox_hover_offset  # Position with animation
            screen.blit(scaled_box, (box_x, box_y))
        else:
            # Draw a simple fallback counter if no sprite found with animation
            counter_width = int(80 * scale)
            counter_height = int(20 * scale)
            counter_x = center_x - counter_width // 2
            counter_y = center_y + int(30 * scale) + tembox_hover_offset
            
            # Draw wooden-looking counter
            counter_color = (139, 69, 19)  # Brown color
            pygame.draw.rect(screen, counter_color, (counter_x, counter_y, counter_width, counter_height))
            pygame.draw.rect(screen, BLACK, (counter_x, counter_y, counter_width, counter_height), 2)
            
            # Add some simple details to make it look like a shop counter
            pygame.draw.line(screen, (160, 82, 45), (counter_x, counter_y + 5), (counter_x + counter_width, counter_y + 5), 1)
            pygame.draw.line(screen, (101, 67, 33), (counter_x, counter_y + counter_height - 3), (counter_x + counter_width, counter_y + counter_height - 3), 1)
    
    def draw_bratty_catty_portrait(self, center_x, center_y, scale):
        """Draw Bratty and Catty portrait with body sprites and simple mouth animations."""
        current_time = pygame.time.get_ticks()
        
        # Position for Bratty (left side)
        bratty_x = center_x - int(80 * scale)
        bratty_y = center_y - int(5 * scale)
        
        # Draw Bratty's body sprite only (no face overlay to avoid tongue out issue)
        body_frame = (current_time // 1200) % 2  # Slower animation for body (2 frames)
        bratty_body_sprite_name = f"spr_brattybody_{body_frame}"
        
        if bratty_body_sprite_name in sprites:
            bratty_body_sprite = sprites[bratty_body_sprite_name]
            scaled_bratty_body = pygame.transform.scale(bratty_body_sprite, 
                                                (int(bratty_body_sprite.get_width() * scale), 
                                                 int(bratty_body_sprite.get_height() * scale)))
            bratty_body_x = bratty_x - scaled_bratty_body.get_width() // 2
            bratty_body_y = bratty_y - scaled_bratty_body.get_height() // 2
            screen.blit(scaled_bratty_body, (bratty_body_x, bratty_body_y))
        
        # Add hovering arms animation for Bratty using left and right arm sprites
        bratty_hover_offset = int(5 * scale * math.sin(current_time * 0.003))  # Gentle hovering motion
        
        # Draw Bratty's left arm (positioned to align with left side of body)
        if "spr_brattyarm_l_0" in sprites:
            bratty_left_arm = sprites["spr_brattyarm_l_0"]
            scaled_left_arm = pygame.transform.scale(bratty_left_arm,
                                               (int(bratty_left_arm.get_width() * scale),
                                                int(bratty_left_arm.get_height() * scale)))
            # Align with left edge of body instead of arbitrary offset
            left_arm_x = bratty_x - int(60 * scale)  # Move further left to align with body edge
            left_arm_y = bratty_y + int(10 * scale) + bratty_hover_offset  # Slightly higher
            screen.blit(scaled_left_arm, (left_arm_x, left_arm_y))
        
        # Draw Bratty's right arm (positioned to align with right side of body)
        if "spr_brattyarm_r_0" in sprites:
            bratty_right_arm = sprites["spr_brattyarm_r_0"]
            scaled_right_arm = pygame.transform.scale(bratty_right_arm,
                                                (int(bratty_right_arm.get_width() * scale),
                                                 int(bratty_right_arm.get_height() * scale)))
            # Align with right edge of body instead of arbitrary offset
            right_arm_x = bratty_x + int(40 * scale) - scaled_right_arm.get_width()  # Move further right and account for arm width
            right_arm_y = bratty_y + int(10 * scale) + bratty_hover_offset  # Slightly higher
            screen.blit(scaled_right_arm, (right_arm_x, right_arm_y))
        
        # Position for Catty (right side)
        catty_x = center_x + int(80 * scale)
        catty_y = center_y - int(5 * scale)
        
        # First, draw Catty's body sprite (behind face expressions, in front of background)
        catty_body_sprite_name = f"spr_cattybody_{body_frame}"
        
        if catty_body_sprite_name in sprites:
            catty_body_sprite = sprites[catty_body_sprite_name]
            scaled_catty_body = pygame.transform.scale(catty_body_sprite, 
                                                (int(catty_body_sprite.get_width() * scale), 
                                                 int(catty_body_sprite.get_height() * scale)))
            catty_body_x = catty_x - scaled_catty_body.get_width() // 2
            catty_body_y = catty_y - scaled_catty_body.get_height() // 2
            screen.blit(scaled_catty_body, (catty_body_x, catty_body_y))
        
        # Then, draw Catty's mouth animation (simple open/close)
        mouth_frame = (current_time // 1500) % 2  # Slower mouth animation (open/close)
        catty_face_sprite_name = f"spr_cattyface_{mouth_frame}"  # Use only frames 0 and 1
        
        if catty_face_sprite_name in sprites:
            catty_face_sprite = sprites[catty_face_sprite_name]
            scaled_catty_face = pygame.transform.scale(catty_face_sprite, 
                                                (int(catty_face_sprite.get_width() * scale), 
                                                 int(catty_face_sprite.get_height() * scale)))
            # Position face slightly higher to align with body's face area
            catty_face_x = catty_x - scaled_catty_face.get_width() // 2
            catty_face_y = catty_y - scaled_catty_face.get_height() // 2 - int(10 * scale)  # Offset up slightly
            screen.blit(scaled_catty_face, (catty_face_x, catty_face_y))
        
        # Add 3-frame arm animation for Catty using catarm sprites
        arm_frame = (current_time // 800) % 3  # Cycle through 3 frames every 800ms
        catty_arms_sprite_name = f"spr_catarm_{arm_frame}"
        
        if catty_arms_sprite_name in sprites:
            catty_arms_sprite = sprites[catty_arms_sprite_name]
            scaled_catty_arms = pygame.transform.scale(catty_arms_sprite, 
                                                (int(catty_arms_sprite.get_width() * scale), 
                                                 int(catty_arms_sprite.get_height() * scale)))
            
            # Create hovering motion - up and down movement (slightly different timing than Burgerpants)
            catty_hover_offset = int(6 * scale * math.sin(current_time * 0.0035))  # Slower and smaller motion
            # Position arms on the right side of Catty's body instead of center
            catty_arms_x = catty_x + int(30 * scale)  # Move to right side of body
            catty_arms_y = catty_y + int(20 * scale) + catty_hover_offset  # Position below face
            screen.blit(scaled_catty_arms, (catty_arms_x, catty_arms_y))
    
    def draw_snowdin_shopkeeper_portrait(self, center_x, center_y, scale):
        """Draw Snowdin Shopkeeper portrait using layered components."""
        # Try to draw shopkeeper using layered sprites  
        shopkeeper_drawn = False
        if "spr_shopkeeper1_0" in sprites:
            # Draw main shopkeeper sprite
            shopkeeper_sprite = sprites["spr_shopkeeper1_0"]
            scaled_sprite = pygame.transform.scale(shopkeeper_sprite, 
                                                 (int(shopkeeper_sprite.get_width() * scale), 
                                                  int(shopkeeper_sprite.get_height() * scale)))
            sprite_x = center_x - scaled_sprite.get_width() // 2
            sprite_y = center_y - scaled_sprite.get_height() // 2
            screen.blit(scaled_sprite, (sprite_x, sprite_y))
            shopkeeper_drawn = True
            
            # Add animated face if available
            current_time = pygame.time.get_ticks()
            face_frame = (current_time // 800) % 7  # Cycle through face expressions
            face_sprite_name = f"spr_shopkeeper1_face{face_frame}_0"
            
            if face_sprite_name in sprites:
                face_sprite = sprites[face_sprite_name]
                scaled_face = pygame.transform.scale(face_sprite, 
                                                    (int(face_sprite.get_width() * scale), 
                                                     int(face_sprite.get_height() * scale)))
                # Position face on the shopkeeper body (moved up slightly)
                face_x = sprite_x + (scaled_sprite.get_width() - scaled_face.get_width()) // 2 
                face_y = sprite_y + (scaled_sprite.get_height() - scaled_face.get_height()) // 4
                screen.blit(scaled_face, (face_x, face_y))
        
        elif "spr_shopkeeper2_body_0" in sprites:
            # Try alternative shopkeeper 2 sprites
            shopkeeper_body = sprites["spr_shopkeeper2_body_0"]
            scaled_body = pygame.transform.scale(shopkeeper_body, 
                                                (int(shopkeeper_body.get_width() * scale), 
                                                 int(shopkeeper_body.get_height() * scale)))
            body_x = center_x - scaled_body.get_width() // 2
            body_y = center_y - scaled_body.get_height() // 2
            screen.blit(scaled_body, (body_x, body_y))
            shopkeeper_drawn = True
            
            # Add eyes if available
            current_time = pygame.time.get_ticks()
            eye_frame = (current_time // 600) % 5
            eye_sprite_name = f"spr_shopkeeper2_eyes_{eye_frame}_0"
            
            if eye_sprite_name in sprites:
                eye_sprite = sprites[eye_sprite_name]
                scaled_eyes = pygame.transform.scale(eye_sprite, 
                                                   (int(eye_sprite.get_width() * scale), 
                                                    int(eye_sprite.get_height() * scale)))
                eye_x = body_x + (scaled_body.get_width() - scaled_eyes.get_width()) // 2
                eye_y = body_y + (scaled_body.get_height() - scaled_eyes.get_height()) // 3
                screen.blit(scaled_eyes, (eye_x, eye_y))
        
        # Fallback if no sprites found
        if not shopkeeper_drawn:
            self.draw_generic_merchant_sprite(center_x, center_y, scale, "snowdin_shopkeeper")
    
    def draw_burgerpants_portrait(self, center_x, center_y, scale):
        """Draw Burgerpants portrait using layered sprite components with animation."""
        # Draw Burgerpants using available sprite components
        burgerpants_drawn = False
        current_time = pygame.time.get_ticks()
        
        # Animate through all 7 face expressions (0-6)
        face_frame = (current_time // 600) % 7  # Change every 600ms through all face expressions
        face_sprite_name = f"spr_bpants_face_{face_frame}"
        
        # Try to load the animated face sprite
        face_sprite = None
        if face_sprite_name in sprites:
            face_sprite = sprites[face_sprite_name]
        
        # If no animated sprite found, try basic static sprite (frame 0)
        if not face_sprite and "spr_bpants_face_0" in sprites:
            face_sprite = sprites["spr_bpants_face_0"]
        
        if face_sprite:
            scaled_face = pygame.transform.scale(face_sprite, 
                                                (int(face_sprite.get_width() * scale), 
                                                 int(face_sprite.get_height() * scale)))
            face_x = center_x - scaled_face.get_width() // 2
            face_y = center_y - scaled_face.get_height() // 2
            screen.blit(scaled_face, (face_x, face_y))
            burgerpants_drawn = True
            
            # Add animated arms if available (hovering up and down motion)
            if "spr_bpants_arms_0" in sprites:
                arms_sprite = sprites["spr_bpants_arms_0"]
                scaled_arms = pygame.transform.scale(arms_sprite, 
                                                    (int(arms_sprite.get_width() * scale), 
                                                     int(arms_sprite.get_height() * scale)))
                
                # Create hovering motion - up and down movement
                hover_offset = int(8 * scale * math.sin(current_time * 0.004))  # Smooth hover motion
                arms_x = center_x - scaled_arms.get_width() // 2
                arms_y = face_y + scaled_face.get_height() - int(15 * scale) + hover_offset
                screen.blit(scaled_arms, (arms_x, arms_y))
        
        # Fallback if no sprites found
        if not burgerpants_drawn:
            self.draw_generic_merchant_sprite(center_x, center_y, scale, "burgerpants")
    
    def draw_generic_merchant_sprite(self, center_x, center_y, scale, merchant_name):
        """Draw a generic merchant sprite as fallback."""
        if merchant_name == "bratty_catty":
            # Draw two separate characters for Bratty & Catty
            rect_size = int(50 * scale)
            
            # Draw Bratty (left character)
            bratty_color = (255, 120, 180)  # Pink
            bratty_x = center_x - rect_size - int(15 * scale)
            bratty_y = center_y - rect_size // 2
            
            pygame.draw.rect(screen, bratty_color, (bratty_x, bratty_y, rect_size, rect_size))
            pygame.draw.rect(screen, BLACK, (bratty_x, bratty_y, rect_size, rect_size), 2)
            
            # Draw Bratty's face (simple circle) - positioned properly on the face area
            face_center_x = bratty_x + rect_size // 2
            face_center_y = bratty_y + int(rect_size * 0.25)  # Move face higher up
            pygame.draw.circle(screen, BLACK, (face_center_x, face_center_y), int(3 * scale))
            
            # Draw Bratty's "B" - positioned below the face
            if undertale_font:
                text_surface = undertale_font.render_text("B", "normal", BLACK)
            else:
                text_surface = font.render("B", True, BLACK)
            text_rect = text_surface.get_rect(center=(face_center_x, bratty_y + int(rect_size * 0.7)))
            screen.blit(text_surface, text_rect)
            
            # Draw Catty (right character)
            catty_color = (150, 100, 255)  # Purple
            catty_x = center_x + int(15 * scale)
            catty_y = center_y - rect_size // 2
            
            pygame.draw.rect(screen, catty_color, (catty_x, catty_y, rect_size, rect_size))
            pygame.draw.rect(screen, BLACK, (catty_x, catty_y, rect_size, rect_size), 2)
            
            # Draw Catty's face (simple circle) - positioned properly on the face area
            face_center_x = catty_x + rect_size // 2
            face_center_y = catty_y + int(rect_size * 0.25)  # Move face higher up
            pygame.draw.circle(screen, BLACK, (face_center_x, face_center_y), int(3 * scale))
            
            # Draw Catty's "C" - positioned below the face
            if undertale_font:
                text_surface = undertale_font.render_text("C", "normal", BLACK)
            else:
                text_surface = font.render("C", True, BLACK)
            text_rect = text_surface.get_rect(center=(face_center_x, catty_y + int(rect_size * 0.7)))
            screen.blit(text_surface, text_rect)
            
        elif merchant_name == "burgerpants":
            # Draw animated Burgerpants character
            current_time = pygame.time.get_ticks()
            
            # Main body
            body_color = (255, 200, 100)  # Orange/yellow
            rect_size = int(64 * scale)
            rect_x = center_x - rect_size // 2
            rect_y = center_y - rect_size // 2
            
            pygame.draw.rect(screen, body_color, (rect_x, rect_y, rect_size, rect_size))
            pygame.draw.rect(screen, BLACK, (rect_x, rect_y, rect_size, rect_size), 3)
            
            # Animated face - cycle through different expressions
            face_frame = (current_time // 800) % 3  # Change every 800ms
            face_center_x = center_x
            face_center_y = rect_y + int(rect_size * 0.3)
            
            # Draw different face expressions
            if face_frame == 0:
                # Normal face
                pygame.draw.circle(screen, BLACK, (face_center_x - int(8 * scale), face_center_y), int(2 * scale))  # Left eye
                pygame.draw.circle(screen, BLACK, (face_center_x + int(8 * scale), face_center_y), int(2 * scale))  # Right eye
                pygame.draw.arc(screen, BLACK, (face_center_x - int(6 * scale), face_center_y + int(5 * scale), int(12 * scale), int(8 * scale)), 0, 3.14159, 2)  # Mouth
            elif face_frame == 1:
                # Tired/annoyed face
                pygame.draw.line(screen, BLACK, (face_center_x - int(10 * scale), face_center_y), (face_center_x - int(6 * scale), face_center_y), 2)  # Left eye
                pygame.draw.line(screen, BLACK, (face_center_x + int(6 * scale), face_center_y), (face_center_x + int(10 * scale), face_center_y), 2)  # Right eye
                pygame.draw.line(screen, BLACK, (face_center_x - int(6 * scale), face_center_y + int(8 * scale)), (face_center_x + int(6 * scale), face_center_y + int(8 * scale)), 2)  # Flat mouth
            else:
                # Worried face
                pygame.draw.circle(screen, BLACK, (face_center_x - int(8 * scale), face_center_y), int(3 * scale))  # Left eye (bigger)
                pygame.draw.circle(screen, BLACK, (face_center_x + int(8 * scale), face_center_y), int(3 * scale))  # Right eye (bigger)
                pygame.draw.arc(screen, BLACK, (face_center_x - int(6 * scale), face_center_y + int(8 * scale), int(12 * scale), int(6 * scale)), 3.14159, 6.28, 2)  # Frown
            
            # Animated arms - move up and down
            arm_offset = int(3 * scale * math.sin(current_time * 0.003))  # Slow up-down motion
            arm_y = rect_y + int(rect_size * 0.5) + arm_offset
            
            # Left arm
            pygame.draw.line(screen, BLACK, (rect_x, arm_y), (rect_x - int(15 * scale), arm_y - int(5 * scale)), 4)
            # Right arm  
            pygame.draw.line(screen, BLACK, (rect_x + rect_size, arm_y), (rect_x + rect_size + int(15 * scale), arm_y - int(5 * scale)), 4)
            
            # Draw "BP" for Burgerpants
            if undertale_font:
                text_surface = undertale_font.render_text("BP", "normal", BLACK)
            else:
                text_surface = font.render("BP", True, BLACK)
            text_rect = text_surface.get_rect(center=(center_x, rect_y + int(rect_size * 0.8)))
            screen.blit(text_surface, text_rect)
            
        else:
            # Draw single character for other merchants
            colors = {
                "snowdin_shopkeeper": (150, 150, 255),  # Light blue
                "burgerpants": (255, 200, 100)  # Orange/yellow
            }
            
            color = colors.get(merchant_name, (128, 128, 128))  # Default gray
            rect_size = int(64 * scale)
            rect_x = center_x - rect_size // 2
            rect_y = center_y - rect_size // 2
            
            # Draw colored rectangle
            pygame.draw.rect(screen, color, (rect_x, rect_y, rect_size, rect_size))
            pygame.draw.rect(screen, BLACK, (rect_x, rect_y, rect_size, rect_size), 3)
            
            # Draw merchant initial
            initial = merchant_name[0].upper()
            if undertale_font:
                text_surface = undertale_font.render_text(initial, "normal", BLACK)
            else:
                text_surface = font.render(initial, True, BLACK)
            
            text_rect = text_surface.get_rect(center=(center_x, center_y))
            screen.blit(text_surface, text_rect)
    
    def draw_undertale_shop_buy_items(self):
        """Draw items available for purchase in Undertale style."""
        if not self.current_shopkeeper.inventory:
            return
        
        # Items display area (below dialogue box)
        items_x = 50
        items_y = 570
        items_width = 600
        items_height = 150
        
        # Items background (white with black border)
        items_rect = pygame.Rect(items_x, items_y, items_width, items_height)
        pygame.draw.rect(screen, WHITE, items_rect)
        pygame.draw.rect(screen, BLACK, items_rect, 4)
        
        # Show available items
        visible_items = self.current_shopkeeper.inventory[:4]  # Show max 4 items
        current_player = self.players[self.selected_player_idx]
        
        for i, item in enumerate(visible_items):
            item_y = items_y + 15 + i * 30
            
            # Highlight selected item
            if i == self.selected_shop_item_idx:
                highlight_rect = pygame.Rect(items_x + 5, item_y - 5, items_width - 10, 28)
                pygame.draw.rect(screen, (200, 200, 255), highlight_rect)  # Light blue highlight
            
            # Item info
            price = self.current_shopkeeper.get_item_price(item)
            can_afford = current_player.gold >= price
            can_carry = current_player.can_carry_item(item)
            
            # Item text with stats
            if isinstance(item, Weapon):
                item_text = f"{item.name} - ATK+{item.attack_bonus} - {price}G"
            elif isinstance(item, Armor):
                item_text = f"{item.name} - DEF+{item.defense_bonus} - {price}G"
            elif isinstance(item, Potion):
                item_text = f"{item.name} - Heals {item.hp_gain}HP - {price}G"
            else:
                item_text = f"{item.name} - {price}G"
            
            # Color based on affordability and inventory space
            if not can_afford:
                text_color = (150, 150, 150)  # Gray for unaffordable
            elif not can_carry:
                text_color = (150, 100, 100)  # Reddish for inventory full
            else:
                text_color = BLACK
            
            # Use text wrapping for long item names
            max_item_width = items_width - 40
            if undertale_font:
                if undertale_font.get_text_size(item_text, "normal")[0] > max_item_width:
                    wrapped_lines = wrap_text(item_text, max_item_width, font_size="normal")
                    for j, line in enumerate(wrapped_lines[:1]):  # Show only first line to save space
                        text_surface = undertale_font.render_text(line, "normal", text_color)
                        screen.blit(text_surface, (items_x + 15, item_y + j * 15))
                else:
                    text_surface = undertale_font.render_text(item_text, "normal", text_color)
                    screen.blit(text_surface, (items_x + 15, item_y))
            else:
                # Fallback to regular font with wrapping
                if font.size(item_text)[0] > max_item_width:
                    wrapped_lines = wrap_text(item_text, max_item_width, font)
                    for j, line in enumerate(wrapped_lines[:1]):
                        text_surface = font.render(line, True, text_color)
                        screen.blit(text_surface, (items_x + 15, item_y + j * 15))
                else:
                    text_surface = font.render(item_text, True, text_color)
                    screen.blit(text_surface, (items_x + 15, item_y))
    
    def draw_undertale_shop_sell_items(self):
        """Draw player items available for sale in Undertale style."""
        current_player = self.players[self.selected_player_idx]
        if not current_player.inventory:
            return
        
        # Items display area (below dialogue box)
        items_x = 50
        items_y = 570
        items_width = 600
        items_height = 150
        
        # Items background (white with black border)
        items_rect = pygame.Rect(items_x, items_y, items_width, items_height)
        pygame.draw.rect(screen, WHITE, items_rect)
        pygame.draw.rect(screen, BLACK, items_rect, 4)
        
        # Show player's items
        visible_items = current_player.inventory[:4]  # Show max 4 items
        
        for i, item in enumerate(visible_items):
            item_y = items_y + 15 + i * 30
            
            # Highlight selected item
            if i == self.selected_item_idx:
                highlight_rect = pygame.Rect(items_x + 5, item_y - 5, items_width - 10, 28)
                pygame.draw.rect(screen, (200, 200, 255), highlight_rect)  # Light blue highlight
            
            # Item info
            price = self.current_shopkeeper.sell_item_price(item)
            is_equipped = ((isinstance(item, Weapon) and item == current_player.weapon) or
                          (isinstance(item, Armor) and item == current_player.armor))
            
            # Item text with stats
            if isinstance(item, Weapon):
                item_text = f"{item.name} - ATK+{item.attack_bonus} - Sell: {price}G"
            elif isinstance(item, Armor):
                item_text = f"{item.name} - DEF+{item.defense_bonus} - Sell: {price}G"
            elif isinstance(item, Potion):
                item_text = f"{item.name} - Heals {item.hp_gain}HP - Sell: {price}G"
            else:
                item_text = f"{item.name} - Sell: {price}G"
            
            if is_equipped:
                item_text += " [Equipped]"
            
            # Color based on whether item can be sold
            text_color = (150, 150, 150) if is_equipped else BLACK
            
            # Use text wrapping for long item names
            max_item_width = items_width - 40
            if undertale_font:
                if undertale_font.get_text_size(item_text, "normal")[0] > max_item_width:
                    wrapped_lines = wrap_text(item_text, max_item_width, font_size="normal")
                    for j, line in enumerate(wrapped_lines[:1]):  # Show only first line to save space
                        text_surface = undertale_font.render_text(line, "normal", text_color)
                        screen.blit(text_surface, (items_x + 15, item_y + j * 15))
                else:
                    text_surface = undertale_font.render_text(item_text, "normal", text_color)
                    screen.blit(text_surface, (items_x + 15, item_y))
            else:
                # Fallback to regular font with wrapping
                if font.size(item_text)[0] > max_item_width:
                    wrapped_lines = wrap_text(item_text, max_item_width, font)
                    for j, line in enumerate(wrapped_lines[:1]):
                        text_surface = font.render(line, True, text_color)
                        screen.blit(text_surface, (items_x + 15, item_y + j * 15))
                else:
                    text_surface = font.render(item_text, True, text_color)
                    screen.blit(text_surface, (items_x + 15, item_y))
    
    def log_action(self, text):
        """Log action for debugging or history purposes."""
        print(f"LOG: {text}")
    
    def get_save_files(self):
        """Get all available save files with their information."""
        save_files = []
        
        # Create saves directory if it doesn't exist
        if not os.path.exists(SAVE_FOLDER):
            os.makedirs(SAVE_FOLDER)
        
        # Check for legacy save file
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, 'r') as f:
                    save_data = json.load(f)
                
                # Get creation time from file stats
                creation_time = os.path.getctime(SAVE_FILE)
                timestamp = datetime.fromtimestamp(creation_time).strftime("%Y-%m-%d %H:%M")
                
                if save_data.get("players"):
                    player_name = save_data["players"][0].get("name", "Unknown")
                    level = save_data["players"][0].get("level", 1)
                    dungeon_level = save_data.get("dungeon_level", 1)
                    
                    save_files.append({
                        "filename": SAVE_FILE,
                        "display_name": f"{player_name} (Legacy Save)",
                        "player_name": player_name,
                        "level": level,
                        "dungeon_level": dungeon_level,
                        "timestamp": timestamp,
                        "is_legacy": True
                    })
            except:
                pass
        
        # Check for new save files in saves folder
        for filename in os.listdir(SAVE_FOLDER):
            if filename.endswith('.json'):
                filepath = os.path.join(SAVE_FOLDER, filename)
                try:
                    with open(filepath, 'r') as f:
                        save_data = json.load(f)
                    
                    if save_data.get("players"):
                        player_name = save_data["players"][0].get("name", "Unknown")
                        level = save_data["players"][0].get("level", 1)
                        dungeon_level = save_data.get("dungeon_level", 1)
                        timestamp = save_data.get("timestamp", "Unknown")
                        
                        save_files.append({
                            "filename": filepath,
                            "display_name": f"{player_name} - Lv.{level} (Floor {dungeon_level})",
                            "player_name": player_name,
                            "level": level,
                            "dungeon_level": dungeon_level,
                            "timestamp": timestamp,
                            "is_legacy": False
                        })
                except:
                    pass
        
        # Sort by timestamp (newest first)
        save_files.sort(key=lambda x: x["timestamp"], reverse=True)
        return save_files
    
    def get_next_save_filename(self):
        """Get the next available save filename."""
        if not os.path.exists(SAVE_FOLDER):
            os.makedirs(SAVE_FOLDER)
        
        for i in range(1, MAX_SAVE_SLOTS + 1):
            filename = os.path.join(SAVE_FOLDER, f"save_slot_{i:02d}.json")
            if not os.path.exists(filename):
                return filename
        
        # If all slots are full, overwrite the oldest
        save_files = self.get_save_files()
        if save_files:
            # Find the oldest non-legacy save
            non_legacy_saves = [sf for sf in save_files if not sf["is_legacy"]]
            if non_legacy_saves:
                return non_legacy_saves[-1]["filename"]
        
        # Fallback to slot 1
        return os.path.join(SAVE_FOLDER, "save_slot_01.json")
    
    def delete_save_file_by_path(self, filepath):
        """Delete a specific save file."""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
        except Exception as e:
            print(f"Error deleting save file: {e}")
        return False

    # ANCHOR Save and Load System
    # Methods for saving and loading game state, managing save files

    def save_game(self):
        """Save the current game state including dungeon layout."""
        try:
            save_data = {
                "players": [],
                "dungeon_level": self.dungeon_level,
                "current_player_idx": self.current_player_idx,
                "game_state": "playing",  # Always save as playing state
                "camera_x": self.camera_x,
                "camera_y": self.camera_y,
                "obtained_items": list(self.obtained_items) if hasattr(self, 'obtained_items') else [],
                "dungeon": None  # Add dungeon data
            }
            
            # Save dungeon layout if it exists
            if self.dungeon:
                dungeon_data = {
                    "width": self.dungeon.width,
                    "height": self.dungeon.height,
                    "level": self.dungeon.level,
                    "grid": self.dungeon.grid,  # Save the complete map layout
                    "rooms": [],  # Save room positions
                    "items": [],  # Save items on the ground
                    "enemies": [],  # Save enemies
                    "treasures": [],  # Save treasure chests
                    "shopkeepers": [],  # Save shop NPCs
                    "stairs_down": self.dungeon.stairs_down,
                    "explored": self.dungeon.explored,  # Save fog of war
                    "visible": self.dungeon.visible
                }
                
                # Save room data
                for room in self.dungeon.rooms:
                    room_data = {
                        "x1": room.x1,
                        "y1": room.y1,
                        "x2": room.x2,
                        "y2": room.y2
                    }
                    dungeon_data["rooms"].append(room_data)
                
                # Save items on the ground
                for item in self.dungeon.items:
                    item_data = {
                        "x": item.x,
                        "y": item.y,
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
                    
                    dungeon_data["items"].append(item_data)
                
                # Save enemies
                for enemy in self.dungeon.enemies:
                    enemy_data = {
                        "x": enemy.x,
                        "y": enemy.y,
                        "name": enemy.name,
                        "enemy_type": enemy.enemy_type,
                        "hp": enemy.hp,
                        "max_hp": enemy.max_hp,
                        "attack": enemy.attack,
                        "defense": enemy.defense,
                        "xp": enemy.xp
                    }
                    dungeon_data["enemies"].append(enemy_data)
                
                # Save treasure chests
                for treasure in self.dungeon.treasures:
                    treasure_data = {
                        "x": treasure.x,
                        "y": treasure.y,
                        "opened": treasure.opened,
                        "items": []
                    }
                    
                    # Save items in treasure chest
                    for item in treasure.items:
                        chest_item_data = {
                            "type": type(item).__name__,
                            "name": item.name,
                            "rarity": getattr(item, 'rarity', 'common')
                        }
                        
                        if isinstance(item, Weapon):
                            chest_item_data.update({
                                "attack_bonus": item.attack_bonus,
                                "allowed_classes": item.allowed_classes,
                                "sprite_name": item.sprite_name
                            })
                        elif isinstance(item, Armor):
                            chest_item_data.update({
                                "defense_bonus": item.defense_bonus,
                                "allowed_classes": item.allowed_classes,
                                "sprite_name": item.sprite_name
                            })
                        elif isinstance(item, Potion):
                            chest_item_data["hp_gain"] = item.hp_gain
                        
                        treasure_data["items"].append(chest_item_data)
                    
                    dungeon_data["treasures"].append(treasure_data)
                
                # Save shopkeepers
                for shopkeeper in self.dungeon.shopkeepers:
                    shopkeeper_data = {
                        "x": shopkeeper.x,
                        "y": shopkeeper.y,
                        "name": shopkeeper.name,
                        "merchant_type": shopkeeper.merchant_type,  # Save merchant type
                        "inventory": []
                    }
                    
                    # Save shopkeeper inventory
                    for item in shopkeeper.inventory:
                        shop_item_data = {
                            "type": type(item).__name__,
                            "name": item.name,
                            "rarity": getattr(item, 'rarity', 'common')
                        }
                        
                        if isinstance(item, Weapon):
                            shop_item_data.update({
                                "attack_bonus": item.attack_bonus,
                                "allowed_classes": item.allowed_classes,
                                "sprite_name": item.sprite_name
                            })
                        elif isinstance(item, Armor):
                            shop_item_data.update({
                                "defense_bonus": item.defense_bonus,
                                "allowed_classes": item.allowed_classes,
                                "sprite_name": item.sprite_name
                            })
                        elif isinstance(item, Potion):
                            shop_item_data["hp_gain"] = item.hp_gain
                        
                        shopkeeper_data["inventory"].append(shop_item_data)
                    
                    dungeon_data["shopkeepers"].append(shopkeeper_data)
                
                save_data["dungeon"] = dungeon_data
            
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
            
            # Add timestamp for save organization
            save_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Get next available save filename
            save_filename = self.get_next_save_filename()
            
            # Save to file
            with open(save_filename, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            self.add_message("Game saved successfully!")
            return True
            
        except Exception as e:
            print(f"Error saving game: {e}")
            self.add_message("Error saving game!")
            return False
    
    def load_game(self, save_filename=None):
        """Load a saved game state including dungeon layout."""
        try:
            # Use provided filename or default to legacy save file
            filename = save_filename or SAVE_FILE
            
            if not os.path.exists(filename):
                return False
            
            with open(filename, 'r') as f:
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
            
            # Load dungeon from save data if available
            if "dungeon" in save_data and save_data["dungeon"]:
                dungeon_data = save_data["dungeon"]
                
                # Create dungeon with saved dimensions
                self.dungeon = Dungeon(dungeon_data["width"], dungeon_data["height"], dungeon_data["level"])
                
                # Restore the map grid
                self.dungeon.grid = dungeon_data["grid"]
                
                # Restore fog of war
                self.dungeon.explored = dungeon_data["explored"]
                self.dungeon.visible = dungeon_data["visible"]
                
                # Restore stairs
                self.dungeon.stairs_down = dungeon_data["stairs_down"]
                
                # Restore rooms
                self.dungeon.rooms = []
                for room_data in dungeon_data["rooms"]:
                    room = Rect(
                        room_data["x1"],
                        room_data["y1"], 
                        room_data["x2"] - room_data["x1"],
                        room_data["y2"] - room_data["y1"]
                    )
                    self.dungeon.rooms.append(room)
                
                # Restore items on the ground
                self.dungeon.items = []
                for item_data in dungeon_data["items"]:
                    item = self.create_item_from_data(item_data)
                    if item:
                        item.x = item_data["x"]
                        item.y = item_data["y"]
                        self.dungeon.items.append(item)
                
                # Restore enemies
                self.dungeon.enemies = []
                for enemy_data in dungeon_data["enemies"]:
                    enemy = Enemy(
                        enemy_data["x"],
                        enemy_data["y"],
                        enemy_data["name"],
                        enemy_data["enemy_type"]
                    )
                    enemy.hp = enemy_data["hp"]
                    enemy.max_hp = enemy_data["max_hp"]
                    enemy.attack = enemy_data["attack"]
                    enemy.defense = enemy_data["defense"]
                    enemy.xp = enemy_data["xp"]
                    self.dungeon.enemies.append(enemy)
                
                # Restore treasure chests
                self.dungeon.treasures = []
                for treasure_data in dungeon_data["treasures"]:
                    treasure = Treasure(treasure_data["x"], treasure_data["y"])
                    treasure.opened = treasure_data["opened"]
                    treasure.items = []
                    
                    # Restore items in treasure chest
                    for item_data in treasure_data["items"]:
                        item = self.create_item_from_data(item_data)
                        if item:
                            treasure.items.append(item)
                    
                    self.dungeon.treasures.append(treasure)
                
                # Restore shopkeepers
                self.dungeon.shopkeepers = []
                for shopkeeper_data in dungeon_data["shopkeepers"]:
                    merchant_type = shopkeeper_data.get("merchant_type", "temmie")  # Default to temmie if not saved
                    shopkeeper = Shopkeeper(shopkeeper_data["x"], shopkeeper_data["y"], merchant_type)
                    shopkeeper.name = shopkeeper_data["name"]
                    shopkeeper.inventory = []
                    
                    # Restore shopkeeper inventory
                    for item_data in shopkeeper_data["inventory"]:
                        item = self.create_item_from_data(item_data)
                        if item:
                            shopkeeper.inventory.append(item)
                    
                    self.dungeon.shopkeepers.append(shopkeeper)
                
                # Set player classes for dungeon
                self.dungeon.player_classes = [p.char_class for p in self.players]
                
                # Set obtained items
                if hasattr(self, 'obtained_items'):
                    self.dungeon.obtained_items = self.obtained_items.copy()
            
            else:
                # Fallback: Generate new level if no dungeon data (backward compatibility)
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
                # Handle both old and new potion data formats
                healing_amount = item_data.get("hp_gain", item_data.get("healing", 30))
                return Potion(name, healing_amount, rarity)
            
        except Exception as e:
            print(f"Error creating item from data: {e}")
        
        return None
    
    def has_save_file(self):
        """Check if any save files exist."""
        # Check for legacy save file
        if os.path.exists(SAVE_FILE):
            return True
        
        # Check for new save files in saves folder
        if os.path.exists(SAVE_FOLDER):
            for filename in os.listdir(SAVE_FOLDER):
                if filename.endswith('.json'):
                    return True
        
        return False
    
    def get_save_info(self):
        """Get basic information about the most recent saved game."""
        try:
            save_files = self.get_save_files()
            if save_files:
                # Get the most recent save (first in sorted list)
                recent_save = save_files[0]
                return {
                    "player_name": recent_save["player_name"],
                    "player_class": "Hero",  # Generic class since we have multiple save types
                    "level": recent_save["level"],
                    "dungeon_level": recent_save["dungeon_level"],
                    "num_players": 1,  # Will be updated when save is loaded
                    "filename": recent_save["filename"]
                }
        except Exception as e:
            print(f"Error reading save info: {e}")
        
        return None
    
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
        # Reset pause state
        self.is_paused = False
        self.previous_game_state = None
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

    # ANCHOR Menu Systems and User Interface
    # Methods for main menu, settings, pause menu, and all UI screens

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
        save_info = self.get_save_info() if has_save else None
        
        buttons = []
        if has_save:
            # Create continue button text with save info
            if save_info:
                # Check if there's a game in progress
                if self.players and self.dungeon and not self.game_over:
                    continue_text = f"Resume: {self.players[0].name} ({self.players[0].char_class.title()})"
                else:
                    # Check how many saves we have
                    all_saves = self.get_save_files()
                    if len(all_saves) > 1:
                        continue_text = f"Select Save ({len(all_saves)} available)"
                    else:
                        continue_text = f"Continue: {save_info['player_name']}"
                continue_key = "C"
            else:
                continue_text = "Continue Game"
                continue_key = "C"
                
            buttons = [
                ("continue", continue_text, continue_key),
                ("new", "New Game", "N"),
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
        
        # Show save game details if available (position it above the game info panel)
        if has_save and save_info:
            info_panel_y = menu_start_y + len(buttons) * button_spacing + 10
            info_panel_width = 350
            info_panel_height = 100
            info_panel_x = SCREEN_WIDTH // 2 - info_panel_width // 2
            
            info_panel_rect = pygame.Rect(info_panel_x, info_panel_y, info_panel_width, info_panel_height)
            draw_gradient_rect(screen, info_panel_rect, ENHANCED_COLORS['panel_dark'], ENHANCED_COLORS['panel_light'])
            
            # Different colors based on whether game is in progress
            if self.players and self.dungeon and not self.game_over:
                panel_color = ENHANCED_COLORS['accent_blue']  # Blue for current session
                header_text = "🎮 Current Session"
                player_info = self.players[0]
                player_text = f"Hero: {player_info.name} (Lv.{player_info.level} {player_info.char_class.title()})"
                location_text = f"Floor {self.dungeon_level} | Party: {len(self.players)} hero{'s' if len(self.players) > 1 else ''}"
            else:
                panel_color = ENHANCED_COLORS['success_green']  # Green for saved game
                header_text = "💾 Save Game Details"
                player_text = f"Hero: {save_info['player_name']} (Lv.{save_info['level']} {save_info['player_class']})"
                location_text = f"Floor {save_info['dungeon_level']} | Party: {save_info['num_players']} hero{'s' if save_info['num_players'] > 1 else ''}"
            
            pygame.draw.rect(screen, panel_color, info_panel_rect, width=2, border_radius=8)
            
            # Game details
            detail_y = info_panel_y + 10
            draw_text_with_shadow(screen, header_text, info_panel_x + 15, detail_y, 
                                panel_color, small_font, 1)
            
            # Player info
            draw_text_with_shadow(screen, player_text, info_panel_x + 15, detail_y + 25, 
                                ENHANCED_COLORS['text_primary'], small_font, 1)
            
            # Location and party info
            draw_text_with_shadow(screen, location_text, info_panel_x + 15, detail_y + 45, 
                                ENHANCED_COLORS['text_secondary'], small_font, 1)
        
        # Game info panel at bottom (adjust position if save info is shown)
        bottom_panel_y = SCREEN_HEIGHT - 120
        if has_save and save_info:
            bottom_panel_y = SCREEN_HEIGHT - 90  # Make it smaller when save info is shown
        
        info_panel_rect = pygame.Rect(50, bottom_panel_y, SCREEN_WIDTH - 100, 70)
        draw_gradient_rect(screen, info_panel_rect, ENHANCED_COLORS['panel_dark'], ENHANCED_COLORS['panel_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['accent_silver'], info_panel_rect, width=2, border_radius=8)
        
        # Show current display mode and version info
        mode_text = "Display: " + ("Emoji Mode" if game_settings['use_emojis'] else "Sprite Mode")
        version_text = "Version 1.24 - Enhanced Multi-Save System & Save State Management"
        
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
                    self.reset_game_state()  # Ensure clean state for new game
                    self.game_state = "setup_num_players"
                elif event.key == pygame.K_c and has_save:
                    animation_manager.add_particles(SCREEN_WIDTH // 2, menu_start_y, ENHANCED_COLORS['success_green'], 15)
                    
                    # Check if there's already a game in progress (from pause menu)
                    if self.players and self.dungeon and not self.game_over:
                        # Resume the current game session
                        self.game_state = "playing"
                        self.add_message(f"Resumed game with {self.players[0].name}")
                        play_sound("menu_back", 0.5)
                    else:
                        # Show save selection menu to choose which save to load
                        self.selected_save_idx = 0  # Always reset to top when entering save selection
                        self.save_files = []  # Clear cached save files to force refresh
                        self.game_state = "save_selection"
                elif event.key == pygame.K_s:
                    animation_manager.add_particles(SCREEN_WIDTH // 2, menu_start_y + button_spacing * (2 if has_save else 1), ENHANCED_COLORS['accent_gold'], 12)
                    self.game_state = "settings_menu"
                elif event.key == pygame.K_q:
                    play_sound("menu_back", 0.5)
                    self.game_over = True

    def save_selection_menu(self):
        """Display save selection menu with options to load or delete saves."""
        # Enhanced background with gradient
        bg_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        draw_gradient_rect(screen, bg_rect, ENHANCED_COLORS['background_dark'], ENHANCED_COLORS['primary_dark'])
        
        # Update animations
        animation_manager.update()
        
        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()
        
        # Animated title with shadow
        title_y = SCREEN_HEIGHT // 2 - 300
        title_x = SCREEN_WIDTH // 2 - 120
        
        # Title background panel
        title_bg_rect = pygame.Rect(title_x - 40, title_y - 20, 280, 80)
        draw_gradient_rect(screen, title_bg_rect, ENHANCED_COLORS['panel_dark'], ENHANCED_COLORS['panel_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['accent_gold'], title_bg_rect, width=3, border_radius=10)
        
        # Main title with enhanced text
        draw_text_with_shadow(screen, "Select Save File", title_x, title_y, ENHANCED_COLORS['accent_gold'], font, 1)
        
        # Get available save files (refresh each time to ensure up-to-date list)
        if not hasattr(self, 'save_files') or not self.save_files:
            self.save_files = self.get_save_files()
        
        # Ensure selected index is within bounds
        if self.save_files:
            self.selected_save_idx = max(0, min(self.selected_save_idx, len(self.save_files) - 1))
        else:
            self.selected_save_idx = 0
        
        # Save files panel
        panel_y = title_y + 100
        panel_width = SCREEN_WIDTH - 200
        panel_height = 400
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        draw_gradient_rect(screen, panel_rect, ENHANCED_COLORS['panel_dark'], ENHANCED_COLORS['panel_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['accent_silver'], panel_rect, width=2, border_radius=8)
        
        # Display save files
        if self.save_files:
            saves_x = panel_x + 30
            start_y = panel_y + 30
            line_height = 60
            
            for i, save_info in enumerate(self.save_files[:6]):  # Show max 6 saves
                save_y = start_y + i * line_height
                
                # Create save item background
                save_rect = pygame.Rect(saves_x - 15, save_y - 10, panel_width - 60, 50)
                
                # Highlight selected save
                if i == self.selected_save_idx:
                    draw_gradient_rect(screen, save_rect, ENHANCED_COLORS['accent_gold'], (255, 235, 59))
                    border_color = ENHANCED_COLORS['accent_gold']
                    text_color = ENHANCED_COLORS['background_dark']
                else:
                    draw_gradient_rect(screen, save_rect, ENHANCED_COLORS['button_normal'], ENHANCED_COLORS['button_hover'])
                    border_color = ENHANCED_COLORS['accent_silver']
                    text_color = ENHANCED_COLORS['text_primary']
                
                pygame.draw.rect(screen, border_color, save_rect, width=2, border_radius=8)
                
                # Save file number
                number_text = f"{i + 1}."
                draw_text_with_shadow(screen, number_text, saves_x, save_y, ENHANCED_COLORS['accent_gold'], font, 1)
                
                # Save file info - better formatted
                info_text = save_info["display_name"]
                draw_text_with_shadow(screen, info_text, saves_x + 40, save_y, text_color, font, 1)
                
                # Timestamp - smaller font and better positioned
                timestamp_text = f"Saved: {save_info['timestamp']}"
                draw_text_with_shadow(screen, timestamp_text, saves_x + 40, save_y + 25, ENHANCED_COLORS['text_secondary'], small_font, 1)
                
                # Legacy indicator - better positioning
                if save_info.get("is_legacy", False):
                    draw_text_with_shadow(screen, "(Legacy Save)", saves_x + panel_width - 250, save_y + 25, ENHANCED_COLORS['accent_gold'], small_font, 1)
        else:
            # No saves found - better formatted message
            no_saves_text = "No save files found"
            draw_text_with_shadow(screen, no_saves_text, SCREEN_WIDTH // 2 - 100, panel_y + panel_height // 2, ENHANCED_COLORS['text_secondary'], font, 1)
        
        # Instructions panel at bottom
        instructions_y = panel_y + panel_height + 20
        instructions_width = panel_width
        instructions_height = 120
        instructions_rect = pygame.Rect(panel_x, instructions_y, instructions_width, instructions_height)
        draw_gradient_rect(screen, instructions_rect, ENHANCED_COLORS['panel_dark'], ENHANCED_COLORS['panel_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['accent_silver'], instructions_rect, width=2, border_radius=8)
        
        # Enhanced instructions
        inst_x = instructions_rect.x + 30
        inst_y = instructions_y + 20
        
        instructions = [
            "↑↓ Arrow Keys: Navigate save files",
            "ENTER: Load selected save file",
            "DELETE: Delete selected save file",
            "ESC: Return to main menu"
        ]
        
        for i, instruction in enumerate(instructions):
            draw_text_with_shadow(screen, instruction, inst_x, inst_y + i * 25, ENHANCED_COLORS['text_secondary'], small_font, 1)
        
        # Draw particles if any
        animation_manager.draw_particles(screen)
        
        pygame.display.flip()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            elif event.type == pygame.KEYDOWN:
                play_sound("menu_select", 0.5)
                
                if event.key == pygame.K_UP:
                    if self.save_files and len(self.save_files) > 0:
                        self.selected_save_idx = (self.selected_save_idx - 1) % len(self.save_files)
                elif event.key == pygame.K_DOWN:
                    if self.save_files and len(self.save_files) > 0:
                        self.selected_save_idx = (self.selected_save_idx + 1) % len(self.save_files)
                elif event.key == pygame.K_RETURN:
                    if self.save_files and self.selected_save_idx < len(self.save_files):
                        selected_save = self.save_files[self.selected_save_idx]
                        if self.load_game(selected_save["filename"]):
                            self.game_state = "playing"
                            play_music("gameplay")  # Fixed: use "gameplay" instead of "dungeon"
                            self.add_message(f"Game loaded: {selected_save['player_name']}")
                            play_sound("success", 0.5)
                        else:
                            self.add_message("Failed to load save file!")
                            play_sound("error", 0.7)
                elif event.key == pygame.K_DELETE:
                    if self.save_files and self.selected_save_idx < len(self.save_files):
                        selected_save = self.save_files[self.selected_save_idx]
                        if self.delete_save_file_by_path(selected_save["filename"]):
                            self.add_message(f"Deleted save: {selected_save['player_name']}")
                            play_sound("success", 0.5)
                            # Refresh save files list immediately
                            self.save_files = self.get_save_files()
                            # Adjust selected index if needed
                            if self.selected_save_idx >= len(self.save_files) and self.save_files:
                                self.selected_save_idx = len(self.save_files) - 1
                            elif not self.save_files:
                                self.selected_save_idx = 0
                        else:
                            self.add_message("Failed to delete save file!")
                            play_sound("error", 0.7)
                elif event.key == pygame.K_ESCAPE:
                    play_sound("menu_back", 0.5)
                    # Reset save selection state when going back to main menu
                    self.selected_save_idx = 0
                    self.save_files = []
                    self.game_state = "main_menu"

    def pause_menu(self):
        """Display the pause menu with options to resume, save, or quit."""
        # Semi-transparent overlay to darken the game screen underneath
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)  # Semi-transparent
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Enhanced pause menu panel
        menu_width = 400
        menu_height = 300
        menu_x = (SCREEN_WIDTH - menu_width) // 2
        menu_y = (SCREEN_HEIGHT - menu_height) // 2
        
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        draw_gradient_rect(screen, menu_rect, ENHANCED_COLORS['panel_dark'], ENHANCED_COLORS['panel_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['accent_gold'], menu_rect, width=3, border_radius=15)
        
        # Title
        title_y = menu_y + 30
        draw_text_with_shadow(screen, "⏸️ GAME PAUSED", menu_x + menu_width // 2 - 100, title_y, 
                            ENHANCED_COLORS['accent_gold'], font)
        
        # Menu options
        button_width = 250
        button_height = 45
        button_spacing = 55
        menu_start_y = title_y + 80
        
        buttons = [
            ("resume", "Resume Game", "Q"),
            ("save", "Save Game", "S"),
            ("main_menu", "Main Menu", "M"),
            ("quit", "Quit Game", "ESC")
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        
        for i, (button_id, text, key) in enumerate(buttons):
            button_y = menu_start_y + i * button_spacing
            button_rect = pygame.Rect(menu_x + (menu_width - button_width) // 2, button_y, button_width, button_height)
            
            # Button colors
            if button_id == "resume":
                base_color = ENHANCED_COLORS['success_green']
                hover_color = (50, 205, 50)
                pressed_color = (34, 139, 34)
            elif button_id == "save":
                base_color = ENHANCED_COLORS['accent_blue']
                hover_color = (70, 130, 180)
                pressed_color = (25, 25, 112)
            elif button_id == "main_menu":
                base_color = ENHANCED_COLORS['accent_gold']
                hover_color = (255, 235, 20)
                pressed_color = (235, 195, 0)
            else:  # quit
                base_color = ENHANCED_COLORS['danger_red']
                hover_color = (231, 67, 67)
                pressed_color = (191, 27, 27)
            
            # Check hover state
            is_hovered = update_button_hover(button_id, button_rect, mouse_pos)
            
            # Draw fancy button
            button_text = f"{text} ({key})"
            draw_fancy_button(screen, button_rect, button_text, font, 
                            base_color, hover_color, pressed_color, 
                            is_hovered=is_hovered, border_radius=10)
        
        pygame.display.flip()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            elif event.type == pygame.KEYDOWN:
                play_sound("menu_select", 0.5)
                
                if event.key == pygame.K_q:  # Resume
                    self.is_paused = False
                    if self.previous_game_state:
                        self.game_state = self.previous_game_state
                        self.previous_game_state = None
                    play_sound("menu_back", 0.5)
                elif event.key == pygame.K_s:  # Save
                    if self.save_game():
                        self.add_message("Game saved successfully!")
                        play_sound("success", 0.5)
                    else:
                        self.add_message("Failed to save game!")
                        play_sound("error", 0.7)
                elif event.key == pygame.K_m:  # Main Menu
                    self.save_game()  # Auto-save before going to main menu
                    play_music("menu")
                    self.game_state = "main_menu"
                    self.is_paused = False
                    # Don't reset game state - preserve it for continue functionality
                    play_sound("menu_confirm", 0.5)
                elif event.key == pygame.K_ESCAPE:  # Quit Game
                    self.save_game()  # Auto-save before quitting
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

    # ANCHOR Core Game Loop and Gameplay
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
            elif self.game_state == "save_selection":
                # Keep menu music playing
                if current_music_state != "menu":
                    play_music("menu")
                self.save_selection_menu()
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
            elif self.game_state == "paused":
                # Keep current music playing (don't change)
                self.pause_menu()
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
        
        # Update damage numbers
        dt = self.clock.get_time()
        update_damage_numbers(dt)
        
        # Update portrait animations
        for animation in portrait_animations.values():
            animation.update()
        
        # Update player animations
        for player in self.players:
            player.update_animation()
        
        self.update_camera()
        
        # Handle continuous key input for movement
        keys_pressed = pygame.key.get_pressed()
        self.handle_continuous_input(keys_pressed)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            if event.type == pygame.KEYDOWN:
                self.handle_input(event.key)
        self.draw_game()

    def handle_continuous_input(self, keys_pressed):
        """Handle continuous movement input for smooth diagonal movement"""
        if self.shop_state == "open" or self.inventory_state == "open":
            return
            
        # Safety check to prevent index out of range
        if not self.players or self.current_player_idx >= len(self.players):
            return
            
        player = self.players[self.current_player_idx]
        
        # Check for movement keys
        dx, dy = 0, 0
        
        if keys_pressed[pygame.K_w] or keys_pressed[pygame.K_UP]:
            dy = -1
        if keys_pressed[pygame.K_s] or keys_pressed[pygame.K_DOWN]:
            dy = 1
        if keys_pressed[pygame.K_a] or keys_pressed[pygame.K_LEFT]:
            dx = -1
        if keys_pressed[pygame.K_d] or keys_pressed[pygame.K_RIGHT]:
            dx = 1
        
        # Only move if there's actual input and enough time has passed
        current_time = pygame.time.get_ticks()
        if not hasattr(self, 'last_movement_time'):
            self.last_movement_time = 0
        
        # Movement speed control (150ms between movements for smoother feel)
        if (dx != 0 or dy != 0) and (current_time - self.last_movement_time > 150):
            self.last_movement_time = current_time
            
            # Handle diagonal movement by trying both directions
            moved = False
            
            # Try horizontal movement first
            if dx != 0:
                new_x = player.x + dx
                if self.can_move_to(new_x, player.y):
                    player.x = new_x
                    if dx > 0:
                        player.direction = "right"
                    else:
                        player.direction = "left"
                    moved = True
                    
            # Try vertical movement
            if dy != 0:
                new_y = player.y + dy
                if self.can_move_to(player.x, new_y):
                    player.y = new_y
                    if dy > 0:
                        player.direction = "down"
                    else:
                        player.direction = "up"
                    moved = True
            
            # If we moved, handle all the movement consequences
            if moved:
                player.start_movement_animation()
                self.update_camera()
                
                # Check for stairs
                if self.dungeon.grid[player.y][player.x] == UI["stairs"]:
                    screen_x = GAME_OFFSET_X + (player.x - self.camera_x) * TILE_SIZE + TILE_SIZE // 2
                    screen_y = GAME_OFFSET_Y + (player.y - self.camera_y) * TILE_SIZE + TILE_SIZE // 2
                    animation_manager.add_particles(screen_x, screen_y, ENHANCED_COLORS['accent_gold'], 20)
                    
                    self.dungeon_level += 1
                    self.new_level()
                    play_sound("door_open", 0.8)
                    return
                
                # Check for enemies
                enemies_in_pos = [e for e in self.dungeon.enemies if e.x == player.x and e.y == player.y]
                if enemies_in_pos:
                    screen_x = GAME_OFFSET_X + (player.x - self.camera_x) * TILE_SIZE + TILE_SIZE // 2
                    screen_y = GAME_OFFSET_Y + (player.y - self.camera_y) * TILE_SIZE + TILE_SIZE // 2
                    animation_manager.add_particles(screen_x, screen_y, ENHANCED_COLORS['danger_red'], 15)
                    self.start_combat(enemies_in_pos)
                    return
                
                # Check for item pickup
                self.check_item_pickup(player)

    def can_move_to(self, x, y):
        """Check if a position is valid for movement"""
        if not (0 <= x < self.dungeon.width and 0 <= y < self.dungeon.height):
            return False
        return self.dungeon.grid[y][x] in [UI["floor"], UI["stairs"]]
    
    def check_item_pickup(self, player):
        """Check for and handle item pickup at player position"""
        for item in list(self.dungeon.items):
            if item.x == player.x and item.y == player.y:
                success, message = player.try_add_item(item, auto_replace=True)
                if success:
                    # Add pickup particle effect
                    screen_x = GAME_OFFSET_X + (player.x - self.camera_x) * TILE_SIZE + TILE_SIZE // 2
                    screen_y = GAME_OFFSET_Y + (player.y - self.camera_y) * TILE_SIZE + TILE_SIZE // 2
                    
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
                else:
                    # Show why pickup failed and offer replacement option
                    self.add_message(message)
                    if player.should_replace_item(item):
                        worst_item = player.get_worst_item(type(item))
                        self.add_message(f"Press R to replace {worst_item.name} with {item.name}")
                        self.pending_replacement = {'item': item, 'player': player}
                break

    def handle_input(self, key):
        if self.shop_state == "open":
            self.handle_shop_input(key)
        elif self.inventory_state == "open":
            self.handle_inventory_input(key)
        else:
            # Safety check to prevent index out of range
            if not self.players or self.current_player_idx >= len(self.players):
                return
            
            player = self.players[self.current_player_idx]
            
            # Non-movement keys only (movement is handled in handle_continuous_input)
            if key == pygame.K_e:  # Interact
                self.handle_interaction(player)
            elif key == pygame.K_i:  # Open inventory
                self.inventory_state = "open"
                self.selected_player_idx = 0
                self.selected_item_idx = 0
            elif key == pygame.K_q:  # Pause/Resume toggle
                if self.is_paused:
                    # Resume the game
                    self.is_paused = False
                    if self.previous_game_state:
                        self.game_state = self.previous_game_state
                        self.previous_game_state = None
                    play_sound("menu_back", 0.5)
                else:
                    # Pause the game
                    self.is_paused = True
                    self.previous_game_state = self.game_state
                    self.game_state = "paused"
                    play_sound("menu_select", 0.5)
            elif key == pygame.K_F5:  # Quick save
                self.save_game()
            elif key == pygame.K_r:  # Replace item
                self.handle_item_replacement()
            elif key == pygame.K_TAB:  # Cycle through players
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
                player.start_movement_animation()  # Start animation when moving
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
                
                # Draw door guardian glow effect if this is a door guardian
                if hasattr(enemy, 'is_door_guardian') and enemy.is_door_guardian:
                    # Draw a pulsing golden glow around door guardians
                    pulse = int(127 + 127 * math.sin(pygame.time.get_ticks() * 0.005))
                    glow_color = (255, 215, 0, pulse)  # Golden color with pulsing alpha
                    glow_surface = pygame.Surface((TILE_SIZE + 8, TILE_SIZE + 8), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surface, glow_color, (0, 0, TILE_SIZE + 8, TILE_SIZE + 8), 3)
                    screen.blit(glow_surface, (screen_x - 4, screen_y - 4))
                
                if game_settings['use_emojis']:
                    # Use different color for door guardians
                    color = (255, 215, 0) if (hasattr(enemy, 'is_door_guardian') and enemy.is_door_guardian) else RED
                    text = font.render(enemy.icon, True, color)
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
                        # Use golden color for door guardians
                        color = (255, 215, 0) if (hasattr(enemy, 'is_door_guardian') and enemy.is_door_guardian) else RED
                        pygame.draw.rect(screen, color, (screen_x + 2, screen_y + 2, TILE_SIZE - 4, TILE_SIZE - 4))
                
        # Draw shopkeepers (only if visible)
        for shopkeeper in self.dungeon.shopkeepers:
            if (viewport_start_x <= shopkeeper.x < viewport_end_x and 
                viewport_start_y <= shopkeeper.y < viewport_end_y and
                self.dungeon.is_visible(shopkeeper.x, shopkeeper.y)):
                
                screen_x = GAME_OFFSET_X + (shopkeeper.x - self.camera_x) * TILE_SIZE
                screen_y = GAME_OFFSET_Y + (shopkeeper.y - self.camera_y) * TILE_SIZE
                
                if game_settings['use_emojis']:
                    # Use different emojis for different merchant types
                    merchant_emojis = {
                        "temmie": "🐱",
                        "bratty_catty": "👯‍♀️", 
                        "snowdin_shopkeeper": "❄️",
                        "burgerpants": "🍔"
                    }
                    emoji = merchant_emojis.get(shopkeeper.merchant_type, "🐱")
                    text = font.render(emoji, True, (255, 215, 0))
                    screen.blit(text, (screen_x, screen_y))
                else:
                    # For sprite mode, try multiple sprite key formats for different merchants
                    sprite_drawn = False
                    
                    # Try various sprite naming conventions
                    sprite_keys = [
                        f"monster_{shopkeeper.icon}",  # monster_temmie, monster_bratty_catty, etc.
                        f"spr_{shopkeeper.icon}_0",    # spr_temmie_0, spr_bratty_catty_0, etc.
                        f"npc_{shopkeeper.icon}",      # npc_temmie, npc_bratty_catty, etc.
                        f"{shopkeeper.icon}",          # temmie, bratty_catty, etc.
                    ]
                    
                    for sprite_key in sprite_keys:
                        if sprite_key in sprites:
                            screen.blit(sprites[sprite_key], (screen_x, screen_y))
                            sprite_drawn = True
                            break
                    
                    if not sprite_drawn:
                        # Fallback colored rectangles with different colors per merchant
                        merchant_colors = {
                            "temmie": (255, 215, 0),        # Gold
                            "bratty_catty": (255, 105, 180), # Hot pink
                            "snowdin_shopkeeper": (173, 216, 230), # Light blue
                            "burgerpants": (255, 165, 0)    # Orange
                        }
                        color = merchant_colors.get(shopkeeper.merchant_type, (255, 215, 0))
                        pygame.draw.rect(screen, color, (screen_x + 4, screen_y + 4, TILE_SIZE - 8, TILE_SIZE - 8))

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
                    # Use directional sprites with animation
                    sprite_drawn = False
                    
                    # Get the animated frame directly
                    current_frame = player.get_current_animated_frame()
                    if current_frame:
                        screen.blit(current_frame, (screen_x, screen_y))
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
        
        # Draw damage numbers with camera offset
        draw_damage_numbers(screen, self.camera_x * TILE_SIZE, self.camera_y * TILE_SIZE)
        
        pygame.display.flip()

    def draw_minimap(self):
        """Draw a small overview map in the top right corner."""
        # Position minimap to align with the expanded right panel (320px wide + 10px margin)
        minimap_x = SCREEN_WIDTH - 320 - 10 + 10  # Align with right panel, small indent
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

    # ANCHOR Game Rendering and Drawing System
    # Methods for drawing UI, game world, minimap, and all visual elements

    def draw_ui(self):
        # Enhanced UI with better alignment and spacing
        
        # Player status in top-left corner with improved styling
        status_y = 20
        status_x = 30
        
        # Background panel for player status
        if self.players:
            max_text_width = 650  # Increased width to handle longer text
            status_panel_height = len(self.players) * 60 + 20  # Increased height for wrapped text
            status_panel_rect = pygame.Rect(status_x - 15, status_y - 10, max_text_width, status_panel_height)
            status_panel_surface = pygame.Surface((max_text_width, status_panel_height))
            status_panel_surface.set_alpha(180)
            status_panel_surface.fill((0, 0, 0))
            screen.blit(status_panel_surface, (status_x - 15, status_y - 10))
            
            # Border for status panel
            pygame.draw.rect(screen, ENHANCED_COLORS['accent_silver'], status_panel_rect, width=2, border_radius=8)
        
        for i, p in enumerate(self.players):
            # Highlight current player
            text_color = ENHANCED_COLORS['accent_gold'] if i == self.current_player_idx else WHITE
            
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
            
            # Check if text is too long and wrap if needed
            status_width = max_text_width - 40  # Account for padding
            if undertale_font.get_text_size(status_text, "normal")[0] > status_width:
                # Wrap long status text
                wrapped_lines = wrap_text(status_text, status_width, font_size="normal")
                for line_idx, line in enumerate(wrapped_lines[:2]):  # Maximum 2 lines per player
                    draw_text_with_shadow(screen, line, status_x, status_y + line_idx * 20, text_color)
                status_y += max(40, len(wrapped_lines[:2]) * 20 + 10)  # Adjust spacing based on wrapped lines
            else:
                draw_text_with_shadow(screen, status_text, status_x, status_y, text_color)
                status_y += 50  # Better spacing between player status lines
        
        # Enhanced message area with background panel
        if self.messages:
            msg_panel_width = 800
            msg_panel_height = 100
            msg_panel_x = (SCREEN_WIDTH - msg_panel_width) // 2
            msg_panel_y = SCREEN_HEIGHT - msg_panel_height - 10
            
            # Message background panel
            msg_panel_rect = pygame.Rect(msg_panel_x, msg_panel_y, msg_panel_width, msg_panel_height)
            msg_panel_surface = pygame.Surface((msg_panel_width, msg_panel_height))
            msg_panel_surface.set_alpha(190)
            msg_panel_surface.fill((0, 0, 0))
            screen.blit(msg_panel_surface, (msg_panel_x, msg_panel_y))
            
            # Border for message panel
            pygame.draw.rect(screen, ENHANCED_COLORS['accent_blue'], msg_panel_rect, width=2, border_radius=8)
            
            msg_y = msg_panel_y + 15
            msg_text_width = msg_panel_width - 40  # 20px padding on each side
            
            # Display up to 3 messages with text wrapping
            current_y = msg_y
            messages_shown = 0
            
            for msg in list(self.messages)[:3]:  # Show only last 3 messages
                if messages_shown >= 3 or current_y > msg_panel_y + msg_panel_height - 25:
                    break
                
                # Wrap long messages to fit within the panel
                wrapped_lines = wrap_text(msg, msg_text_width, font_size="small")
                
                for line in wrapped_lines:
                    if current_y > msg_panel_y + msg_panel_height - 25:
                        break  # Stop if we're running out of space
                    
                    draw_text_with_shadow(screen, line, msg_panel_x + 20, current_y, WHITE, small_font, 1)
                    current_y += 20  # Line spacing
                
                messages_shown += 1
                current_y += 5  # Extra spacing between messages
        
        # Enhanced right panel with better alignment
        right_panel_width = 320  # Increased width to prevent text cutoff
        right_panel_x = SCREEN_WIDTH - right_panel_width - 10  # Adjusted margin
        
        # Right panel background (starts after minimap area)
        panel_start_y = MINIMAP_SIZE + 60
        panel_height = SCREEN_HEIGHT - panel_start_y - 40
        right_panel_rect = pygame.Rect(right_panel_x, panel_start_y, right_panel_width, panel_height)
        right_panel_surface = pygame.Surface((right_panel_width, panel_height))
        right_panel_surface.set_alpha(180)
        right_panel_surface.fill((0, 0, 0))
        screen.blit(right_panel_surface, right_panel_rect)
        
        # Border for right panel
        pygame.draw.rect(screen, ENHANCED_COLORS['accent_silver'], right_panel_rect, width=2, border_radius=8)
        
        # Info text in right panel with better spacing and wrapping
        info_x = right_panel_x + 15
        info_start_y = panel_start_y + 20
        text_width = right_panel_width - 30  # Available text width with margins
        
        # Current player indicator (removed duplicate dungeon level)
        if self.players:
            current_player = self.players[self.current_player_idx]
            player_text = f"👤 Active: {current_player.name}"
            # Check if text is too long and wrap if needed
            if undertale_font.get_text_size(player_text, "normal")[0] > text_width:
                wrapped_lines = wrap_text(player_text, text_width, font_size="normal")
                current_y = info_start_y
                for line in wrapped_lines[:2]:  # Max 2 lines
                    draw_text_with_shadow(screen, line, info_x, current_y, ENHANCED_COLORS['accent_blue'])
                    current_y += 20
                info_y_offset = current_y - info_start_y + 15
            else:
                draw_text_with_shadow(screen, player_text, info_x, info_start_y, ENHANCED_COLORS['accent_blue'])
                info_y_offset = 35
        
        # Inventory status for current player with text wrapping
        if self.players:
            weapons = len(current_player.get_inventory_by_type(Weapon))
            armor = len(current_player.get_inventory_by_type(Armor))
            potions = len(current_player.get_inventory_by_type(Potion))
            
            inv_title = f"📦 Inventory:"
            draw_text_with_shadow(screen, inv_title, info_x, info_start_y + info_y_offset, ENHANCED_COLORS['accent_silver'])
            
            # Weapons with text wrapping
            weapon_text = f"⚔️  {weapons}/{current_player.max_weapons} Weapons"
            if undertale_font.get_text_size(weapon_text, "normal")[0] > text_width:
                wrapped_lines = wrap_text(weapon_text, text_width, font_size="normal")
                current_y = info_start_y + info_y_offset + 30
                for line in wrapped_lines:
                    draw_text_with_shadow(screen, line, info_x, current_y, WHITE)
                    current_y += 18
                weapons_end_y = current_y
            else:
                draw_text_with_shadow(screen, weapon_text, info_x, info_start_y + info_y_offset + 30, WHITE)
                weapons_end_y = info_start_y + info_y_offset + 50
            
            # Armor with text wrapping  
            armor_text = f"🛡️  {armor}/{current_player.max_armor} Armor"
            if undertale_font.get_text_size(armor_text, "normal")[0] > text_width:
                wrapped_lines = wrap_text(armor_text, text_width, font_size="normal")
                current_y = weapons_end_y + 5
                for line in wrapped_lines:
                    draw_text_with_shadow(screen, line, info_x, current_y, WHITE)
                    current_y += 18
                armor_end_y = current_y
            else:
                draw_text_with_shadow(screen, armor_text, info_x, weapons_end_y + 5, WHITE)
                armor_end_y = weapons_end_y + 25
            
            # Potions with text wrapping
            potion_text = f"🧪 {potions}/{current_player.max_potions} Potions"
            if undertale_font.get_text_size(potion_text, "normal")[0] > text_width:
                wrapped_lines = wrap_text(potion_text, text_width, font_size="normal")
                current_y = armor_end_y + 5
                for line in wrapped_lines:
                    draw_text_with_shadow(screen, line, info_x, current_y, WHITE)
                    current_y += 18
                inventory_end_y = current_y
            else:
                draw_text_with_shadow(screen, potion_text, info_x, armor_end_y + 5, WHITE)
                inventory_end_y = armor_end_y + 25
        
        # Enhanced controls section with text wrapping - positioned closer to inventory
        controls_y = inventory_end_y + 20  # Position controls right after inventory with small gap
        controls_title = "🎮 Controls:"
        draw_text_with_shadow(screen, controls_title, info_x, controls_y, ENHANCED_COLORS['accent_gold'])
        
        # Controls list with wrapping support
        controls = [
            ("WASD/Arrows - Move", GRAY),
            ("(Hold multiple for diagonal)", ENHANCED_COLORS['text_disabled']),
            ("E - Interact", GRAY),
            ("I - Inventory", GRAY),
            ("TAB - Switch Player", GRAY),
            ("Q - Main Menu", GRAY)
        ]
        
        current_control_y = controls_y + 30
        for i, (control_text, color) in enumerate(controls):
            # Check if text fits, wrap if needed
            if undertale_font.get_text_size(control_text, "small" if i == 1 else "normal")[0] > text_width:
                wrapped_lines = wrap_text(control_text, text_width, 
                                        font_size="small" if i == 1 else "normal")
                for line in wrapped_lines:
                    if current_control_y < right_panel_rect.bottom - 20:  # Stay within panel bounds
                        if i == 1:  # Diagonal instruction is indented
                            draw_text_with_shadow(screen, line, info_x + 20, current_control_y, 
                                                color, small_font)
                        else:
                            draw_text_with_shadow(screen, line, info_x, current_control_y, color, 
                                                small_font if i == 1 else font)
                        current_control_y += 18
            else:
                if current_control_y < right_panel_rect.bottom - 20:  # Stay within panel bounds
                    if i == 1:  # Diagonal instruction is indented and smaller
                        draw_text_with_shadow(screen, control_text, info_x + 20, current_control_y, 
                                            color, small_font)
                        current_control_y += 20
                    else:
                        draw_text_with_shadow(screen, control_text, info_x, current_control_y, color)
                        current_control_y += 25


    # ANCHOR Combat System
    # Methods for turn-based combat, player/enemy actions, and battle management

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
        # Update damage numbers
        dt = self.clock.get_time()
        update_damage_numbers(dt)
        
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
                    elif event.key == pygame.K_q:  # Pause during combat
                        self.is_paused = True
                        self.previous_game_state = "combat"
                        self.game_state = "paused"
                        play_sound("menu_select", 0.5)
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
            # Remove defeated enemies from dungeon and drop special loot for door guardians
            defeated_enemies = [e for e in self.combat_enemies if not e.is_alive()]
            for enemy in defeated_enemies:
                # Door guardians drop special loot
                if hasattr(enemy, 'is_door_guardian') and enemy.is_door_guardian:
                    self.add_message(f"The door guardian {enemy.name} has fallen!")
                    
                    # Drop special items for door guardians
                    if hasattr(enemy, 'special_drops') and enemy.special_drops:
                        for special_item_name in enemy.special_drops:
                            if special_item_name == "tem_flakes":
                                # Create special Tem Flakes item
                                tem_flakes = Potion("Tem Flakes", 30, "rare")
                                tem_flakes.description = "Temmie's favorite food! Fully restores HP."
                                tem_flakes.hp_gain = 999  # Full heal
                                tem_flakes.x = enemy.x
                                tem_flakes.y = enemy.y
                                self.dungeon.items.append(tem_flakes)
                                self.add_message("The door guardian dropped Tem Flakes!")
                            elif special_item_name == "tem_armor":
                                # Create special Tem Armor
                                tem_armor = Armor("Tem Armor", 20, ["warrior", "mage", "archer"], "epic")
                                tem_armor.description = "Legendary armor made by Temmie!"
                                tem_armor.x = enemy.x
                                tem_armor.y = enemy.y
                                self.dungeon.items.append(tem_armor)
                                self.add_message("The door guardian dropped legendary Tem Armor!")
                    
                    # Door guardians also drop extra gold
                    bonus_gold = random.randint(50, 100)
                    current_player = self.players[self.current_player_idx]
                    current_player.gold += bonus_gold
                    self.add_message(f"You found {bonus_gold} extra gold from the door guardian!")
            
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
            
            # Check for critical hit (20% chance)
            is_critical = random.random() < 0.2
            if is_critical:
                damage = int(damage * 1.5)  # 50% more damage on crit
            
            target.take_damage(damage)
            self.add_message(f"{player.name} hits {target.name} for {damage} damage{'!' if is_critical else '.'}")
            
            # Add damage number animation at enemy position
            # Convert enemy position to screen coordinates
            enemy_screen_x = target.x * TILE_SIZE + TILE_SIZE // 2
            enemy_screen_y = target.y * TILE_SIZE + TILE_SIZE // 2
            add_damage_number(enemy_screen_x, enemy_screen_y, damage, is_critical)
            
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
            
            # Enemies have lower crit chance (10%)
            is_critical = random.random() < 0.1
            if is_critical:
                damage = int(damage * 1.3)  # 30% more damage on crit for enemies
            
            target.take_damage(damage)
            self.add_message(f"{enemy.name} hits {target.name} for {damage} damage{'!' if is_critical else '.'}")
            
            # Add damage number animation at player position
            # Convert player position to screen coordinates
            player_screen_x = target.x * TILE_SIZE + TILE_SIZE // 2
            player_screen_y = target.y * TILE_SIZE + TILE_SIZE // 2
            add_damage_number(player_screen_x, player_screen_y, damage, is_critical)
            
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
            
            # Always critical for power strike visual effect
            is_critical = True
            
            target.take_damage(damage)
            self.add_message(f"{player.name} uses Power Strike on {target.name} for {damage} damage!")
            
            # Add damage number animation at enemy position
            enemy_screen_x = target.x * TILE_SIZE + TILE_SIZE // 2
            enemy_screen_y = target.y * TILE_SIZE + TILE_SIZE // 2
            add_damage_number(enemy_screen_x, enemy_screen_y, damage, is_critical)
            
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
                
                # Fireball has chance for critical hits
                is_critical = random.random() < 0.3  # 30% crit chance for magic
                if is_critical:
                    damage = int(damage * 1.4)  # 40% more damage on crit for fireball
                
                enemy.take_damage(damage)
                self.add_message(f"Fireball hits {enemy.name} for {damage} damage{'!' if is_critical else '.'}")
                
                # Add damage number animation at enemy position
                enemy_screen_x = enemy.x * TILE_SIZE + TILE_SIZE // 2
                enemy_screen_y = enemy.y * TILE_SIZE + TILE_SIZE // 2
                add_damage_number(enemy_screen_x, enemy_screen_y, damage, is_critical)
                
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
            for shot_num in range(2):
                if alive_enemies:  # Check if there are still alive enemies for each shot
                    target = random.choice(alive_enemies)
                    # Double Shot: Normal damage per shot with balanced calculation
                    base_damage = player.attack + random.randint(1, 4)
                    defense_reduction = min(0.75, target.defense * 0.05)
                    damage = max(1, int(base_damage * (1 - defense_reduction)))
                    
                    # Check for critical hit (25% chance per shot)
                    is_critical = random.random() < 0.25
                    if is_critical:
                        damage = int(damage * 1.5)  # 50% more damage on crit
                    
                    target.take_damage(damage)
                    self.add_message(f"{player.name} shoots {target.name} for {damage} damage{'!' if is_critical else '.'}")
                    
                    # Add damage number animation at enemy position with slight offset for multiple shots
                    enemy_screen_x = target.x * TILE_SIZE + TILE_SIZE // 2 + (shot_num * 15)  # Offset multiple shots
                    enemy_screen_y = target.y * TILE_SIZE + TILE_SIZE // 2 - (shot_num * 10)
                    add_damage_number(enemy_screen_x, enemy_screen_y, damage, is_critical)
                    
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
        
        # Wrap victory message to prevent overflow
        victory_message = "You have defeated the dragon and conquered the dungeon!"
        victory_lines = wrap_text(victory_message, SCREEN_WIDTH - 100, font_size="normal")
        
        current_y = title_y + 50
        for line in victory_lines:
            text_width = undertale_font.get_text_size(line, "normal")[0]
            x_pos = (SCREEN_WIDTH - text_width) // 2
            self.draw_text(line, x_pos, current_y, WHITE)
            current_y += 30
        
        # Show final stats
        if self.players:
            highest_level = max(p.level for p in self.players)
            self.draw_text(f"Final level reached: {highest_level}", SCREEN_WIDTH // 2 - 120, current_y + 50, GREEN)
            self.draw_text(f"Dungeon fully conquered: {self.dungeon_level}/5", SCREEN_WIDTH // 2 - 140, current_y + 75, GREEN)
            
            # Show some additional victory stats
            player = self.players[0]  # Main player
            self.draw_text(f"Final HP: {player.hp}/{player.max_hp}", SCREEN_WIDTH // 2 - 80, current_y + 100, GRAY)
            if hasattr(player, 'weapon') and player.weapon:
                weapon_text = f"Weapon: {player.weapon.name}"
                # Wrap weapon name if it's too long
                if undertale_font.get_text_size(weapon_text, "normal")[0] > SCREEN_WIDTH - 100:
                    weapon_lines = wrap_text(weapon_text, SCREEN_WIDTH - 200, font_size="normal")
                    weapon_y = current_y + 125
                    for line in weapon_lines:
                        text_width = undertale_font.get_text_size(line, "normal")[0]
                        x_pos = (SCREEN_WIDTH - text_width) // 2
                        self.draw_text(line, x_pos, weapon_y, GRAY)
                        weapon_y += 25
                    current_y = weapon_y - 25  # Adjust current_y for next elements
                else:
                    self.draw_text(weapon_text, SCREEN_WIDTH // 2 - 100, current_y + 125, GRAY)
        
        self.draw_text("Congratulations, Hero!", SCREEN_WIDTH // 2 - 150, current_y + 150, GOLD)
        
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


# =============================================================================
# MAIN PROGRAM EXECUTION
# =============================================================================
# Entry point for the game - creates Game instance and starts main loop

if __name__ == "__main__":
    game = Game()
    game.main_loop()
