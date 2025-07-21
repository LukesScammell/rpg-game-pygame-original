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
        "use_emojis": False,
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
    """Load all sprite images with Undertale theme."""
    global sprites
    
    print("=== Loading Undertale-themed sprites ===")
    
    # Load Undertale background/tileset sprites for walls and floors
    print("Loading Undertale tileset sprites...")
    undertale_tilesets_path = os.path.join("assets", "undertale", "Overworld", "Locations", "01 - Ruins", "Tilesets")
    
    # Load Undertale tileset sprites for walls and floors based on dungeon level
    print("Loading Undertale tileset sprites...")
    
    # Define different tilesets for different dungeon levels
    level_tilesets = {
        1: {  # Ruins (Level 1)
            "folder": os.path.join("assets", "undertale", "Overworld", "Locations", "01 - Ruins", "Tilesets"),
            "tileset": "bg_ruinseasynam1.png",
            "backup_tilesets": ["bg_ruinseasynam2.png", "bg_ruinseasynam3.png"]
        },
        2: {  # Snowdin (Level 2)
            "folder": os.path.join("assets", "undertale", "Overworld", "Locations", "02 - Snowdin", "Tilesets"),
            "tileset": "bg_tundratiles.png",
            "backup_tilesets": ["bg_icecave.png"]
        },
        3: {  # Waterfall (Level 3)
            "folder": os.path.join("assets", "undertale", "Overworld", "Locations", "03 - Waterfall", "Tilesets"),
            "tileset": "bg_watertiles.png",
            "backup_tilesets": ["bg_watertiles_2.png"]
        },
        4: {  # Hotland (Level 4)
            "folder": os.path.join("assets", "undertale", "Overworld", "Locations", "04 - Hotland", "Tilesets"),
            "tileset": "bg_firetiles.png",
            "backup_tilesets": ["bg_labtiles.png", "bg_brownground.png"]
        },
        5: {  # Core (Level 5) - fallback to Hotland if Core doesn't have tilesets
            "folder": os.path.join("assets", "undertale", "Overworld", "Locations", "04 - Hotland", "Tilesets"),
            "tileset": "bg_labtiles.png",
            "backup_tilesets": ["bg_girdertile.png", "bg_firetiles.png"]
        }
    }
    
    def score_corner_candidate(surface, corner_type, floor_ref, wall_ref):
        """Score a tile based on how well it could work as a rounded floor corner piece."""
        try:
            # Convert surface to analyze pixels
            pixels = pygame.PixelArray(surface)
            width, height = surface.get_size()
            
            # For Undertale-style rounded corners, we want floor-like pieces with curved edges
            # Score higher for tiles that:
            # 1. Have floor-like base colors (similar to the main floor tile)
            # 2. Have curved/rounded visual elements
            # 3. Are NOT solid wall colors
            
            # Sample key pixels to understand the tile structure
            center_pixels = []
            edge_pixels = []
            corner_pixels = []
            
            # Sample center area (should be floor-like)
            for i in range(width//3, 2*width//3, 2):
                for j in range(height//3, 2*height//3, 2):
                    center_pixels.append(pixels[i][j])
            
            # Sample edges and corners for curve detection
            for i in range(0, width, max(1, width//4)):
                edge_pixels.extend([pixels[i][0], pixels[i][height-1]])
            for j in range(0, height, max(1, height//4)):
                edge_pixels.extend([pixels[0][j], pixels[width-1][j]])
                
            # Sample actual corners
            corner_pixels = [pixels[0][0], pixels[width-1][0], pixels[0][height-1], pixels[width-1][height-1]]
            
            # Score based on color variety (good for detecting curves/gradients)
            all_pixels = center_pixels + edge_pixels + corner_pixels
            unique_colors = len(set(all_pixels))
            variety_score = min(unique_colors / 8.0, 2.0)
            
            # Score based on having different colors in center vs edges (indicates curves)
            center_unique = len(set(center_pixels)) if center_pixels else 0
            edge_unique = len(set(edge_pixels)) if edge_pixels else 0
            contrast_score = min((center_unique + edge_unique) / 6.0, 2.0)
            
            # Bonus for NOT being a solid color (avoid plain wall tiles)
            if unique_colors > 4:
                solid_penalty = 0.0
            else:
                solid_penalty = -1.0
            
            del pixels
            
            # Total score - higher is better
            total_score = variety_score + contrast_score + solid_penalty
            return max(0.0, total_score)
            
        except Exception:
            return 0.0
    
    def extract_tiles_from_tileset(tileset_path, tile_size=TILE_SIZE):
        """Extract floor and wall tiles from an Undertale tileset with proper tile cutting."""
        try:
            tileset_image = pygame.image.load(tileset_path)
            
            # Undertale tiles are typically 20x20 pixels in the original tilesets
            undertale_tile_size = 20
            img_width = tileset_image.get_width()
            img_height = tileset_image.get_height()
            
            # Calculate how many tiles fit in each direction
            tiles_per_row = img_width // undertale_tile_size
            tiles_per_col = img_height // undertale_tile_size
            
            print(f"    Tileset {os.path.basename(tileset_path)}: {img_width}x{img_height}, {tiles_per_row}x{tiles_per_col} tiles")
            
            # Define better tile extraction positions based on common Undertale tileset layouts
            floor_tile = None
            wall_tile = None
            
            # For Ruins tileset (bg_ruinseasynam1.png) - 160x100 = 8x5 tiles
            if "ruinseasynam" in tileset_path:
                # Ruins typically have floor tiles in specific positions
                floor_positions = [
                    (0, 0), (1, 0), (2, 0), (3, 0),  # Top row - often floor variants
                    (0, 1), (1, 1), (2, 1)           # Second row
                ]
                wall_positions = [
                    (4, 0), (5, 0), (6, 0), (7, 0),  # Top row - often wall variants  
                    (3, 1), (4, 1), (5, 1)           # Second row walls
                ]
            
            # For Snowdin tileset (bg_tundratiles.png) - 186x1500 - very tall
            elif "tundratiles" in tileset_path:
                floor_positions = [
                    (0, 0), (1, 0), (2, 0), (3, 0),  # Ice/snow floor tiles
                    (0, 1), (1, 1), (2, 1), (3, 1)   # More floor variants
                ]
                wall_positions = [
                    (4, 0), (5, 0), (6, 0), (7, 0),  # Ice walls
                    (0, 2), (1, 2), (2, 2), (3, 2)   # Wall variants deeper in tileset
                ]
            
            # For Waterfall tileset (bg_watertiles.png) - 280x320 = 14x16 tiles
            elif "watertiles" in tileset_path:
                # Try different positions for better cave/water floor tiles
                floor_positions = [
                    (2, 1), (3, 1), (4, 1), (5, 1),  # Second row - often better floor tiles
                    (1, 2), (2, 2), (3, 2), (4, 2),  # Third row alternatives
                    (0, 3), (1, 3), (2, 3)           # Fourth row for cave floors
                ]
                wall_positions = [
                    (0, 0), (1, 0), (6, 0), (7, 0),  # Top row walls
                    (0, 1), (1, 1), (6, 1), (7, 1),  # Second row walls
                    (5, 2), (6, 2), (7, 2)           # Different wall positions
                ]
            
            # For Hotland tileset (bg_firetiles.png) - 360x400 = 18x20 tiles
            elif "firetiles" in tileset_path or "labtiles" in tileset_path:
                # Try different positions for better lava/industrial floor
                floor_positions = [
                    (1, 1), (2, 1), (3, 1), (4, 1),  # Second row - often metallic floors
                    (0, 2), (1, 2), (2, 2), (3, 2),  # Third row alternatives
                    (1, 3), (2, 3), (3, 3)           # Fourth row for industrial floors
                ]
                wall_positions = [
                    (5, 0), (6, 0), (7, 0), (8, 0),  # Different wall positions
                    (4, 1), (5, 1), (6, 1), (7, 1),  # Industrial wall variants
                    (0, 4), (1, 4), (2, 4)           # Lower wall positions
                ]
            
            # Generic fallback positions
            else:
                floor_positions = [(0, 0), (1, 0), (2, 0), (0, 1)]
                wall_positions = [(3, 0), (4, 0), (1, 1), (2, 1)]
            
            # Try to extract floor tile
            for tile_x, tile_y in floor_positions:
                if tile_x < tiles_per_row and tile_y < tiles_per_col:
                    try:
                        x = tile_x * undertale_tile_size
                        y = tile_y * undertale_tile_size
                        floor_rect = pygame.Rect(x, y, undertale_tile_size, undertale_tile_size)
                        floor_tile = tileset_image.subsurface(floor_rect).copy()
                        floor_tile = pygame.transform.scale(floor_tile, (tile_size, tile_size))
                        print(f"      Floor tile extracted from position ({tile_x}, {tile_y})")
                        break
                    except (pygame.error, ValueError):
                        continue
            
            # Try to extract wall tile
            for tile_x, tile_y in wall_positions:
                if tile_x < tiles_per_row and tile_y < tiles_per_col:
                    try:
                        x = tile_x * undertale_tile_size
                        y = tile_y * undertale_tile_size
                        wall_rect = pygame.Rect(x, y, undertale_tile_size, undertale_tile_size)
                        wall_tile = tileset_image.subsurface(wall_rect).copy()
                        wall_tile = pygame.transform.scale(wall_tile, (tile_size, tile_size))
                        print(f"      Wall tile extracted from position ({tile_x}, {tile_y})")
                        break
                    except (pygame.error, ValueError):
                        continue
            
            # Try to extract corner tiles for 3D effect - systematically search for good corner pieces
            corner_tiles = {}
            
            print(f"      Searching for corner pieces in {tiles_per_row}x{tiles_per_col} grid...")
            
            # For Undertale rounded rooms, we want floor pieces with curved edges 
            # Focus on the key corner types that create smooth room curves
            corner_types = ['inner_top_left', 'inner_top_right', 'inner_bottom_left', 'inner_bottom_right']
            
            # Define search areas for each tileset - focus on floor-like rounded pieces
            if "bg_ruinseasynam1" in tileset_path:  # Level 1 - Ruins (8x5)
                # In ruins, look for floor tiles with rounded edges in rows 1-4
                # Avoid row 0 which tends to have basic tiles
                search_positions = [(x, y) for x in range(8) for y in range(1, 5)]
                print(f"      Ruins: Searching {len(search_positions)} positions for rounded floor pieces")
                
            elif "bg_tundratiles" in tileset_path:  # Level 2 - Snowdin (9x75) 
                # Large tileset - focus on early sections which often have floor variants
                search_positions = [(x, y) for x in range(9) for y in range(1, 15)]  # More focused search
                print(f"      Snowdin: Searching {len(search_positions)} positions for icy rounded floor pieces")
                
            elif "bg_watertiles" in tileset_path:  # Level 3 - Waterfall (14x16)
                # Focus on middle sections where floor variants are typically located
                search_positions = [(x, y) for x in range(14) for y in range(1, 12)]
                print(f"      Waterfall: Searching {len(search_positions)} positions for cave rounded floor pieces")
                
            elif "bg_firetiles" in tileset_path:  # Level 4 - Hotland (18x20)
                # Large tileset - search systematically for lava/industrial floor pieces  
                search_positions = [(x, y) for x in range(18) for y in range(1, 15)]
                print(f"      Hotland: Searching {len(search_positions)} positions for lava rounded floor pieces")
                
            elif "bg_labtiles" in tileset_path:  # Level 5 - Lab/Core (6x12)
                # Smaller tileset - search most areas for tech floor pieces
                search_positions = [(x, y) for x in range(6) for y in range(1, 10)]
                print(f"      Lab: Searching {len(search_positions)} positions for tech rounded floor pieces")
            else:
                # Generic search - focus on likely floor tile areas
                search_positions = [(x, y) for x in range(tiles_per_row) for y in range(1, min(tiles_per_col, 8))]
            
            # For each corner type, find the best candidate with position preferences
            corner_type_preferences = {
                'inner_top_left': 'prefer_top_left',
                'inner_top_right': 'prefer_top_right', 
                'inner_bottom_left': 'prefer_bottom_left',
                'inner_bottom_right': 'prefer_bottom_right'
            }
            
            for corner_type in corner_types:
                best_candidate = None
                best_score = 0
                preference = corner_type_preferences.get(corner_type, 'none')
                
                # Create weighted search based on corner type
                weighted_positions = []
                for tile_x, tile_y in search_positions:
                    weight = 1.0  # Base weight
                    
                    # Add positional preferences for different corner types
                    if preference == 'prefer_top_left' and tile_x < tiles_per_row//2 and tile_y < tiles_per_col//2:
                        weight = 1.5
                    elif preference == 'prefer_top_right' and tile_x >= tiles_per_row//2 and tile_y < tiles_per_col//2:
                        weight = 1.5  
                    elif preference == 'prefer_bottom_left' and tile_x < tiles_per_row//2 and tile_y >= tiles_per_col//2:
                        weight = 1.5
                    elif preference == 'prefer_bottom_right' and tile_x >= tiles_per_row//2 and tile_y >= tiles_per_col//2:
                        weight = 1.5
                    
                    weighted_positions.append((tile_x, tile_y, weight))
                
                # Sort by weight (higher weight first) 
                weighted_positions.sort(key=lambda x: x[2], reverse=True)
                
                for tile_x, tile_y, weight in weighted_positions:
                    if tile_x >= tiles_per_row or tile_y >= tiles_per_col:
                        continue
                        
                    try:
                        x = tile_x * undertale_tile_size
                        y = tile_y * undertale_tile_size
                        corner_rect = pygame.Rect(x, y, undertale_tile_size, undertale_tile_size)
                        
                        # Extract the tile for analysis
                        test_surface = pygame.Surface((undertale_tile_size, undertale_tile_size))
                        test_surface.blit(tileset_image, (0, 0), corner_rect)
                        
                        # Score this tile as a potential corner piece
                        base_score = score_corner_candidate(test_surface, corner_type, floor_tile, wall_tile)
                        # Apply positional weight
                        weighted_score = base_score * weight
                        
                        if weighted_score > best_score:
                            best_score = weighted_score
                            best_candidate = (tile_x, tile_y, test_surface.copy(), base_score)
                            
                    except (pygame.error, ValueError):
                        continue
                
                # If we found a good candidate, use it
                if best_candidate:
                    tile_x, tile_y, surface, base_score = best_candidate
                    corner_tile = pygame.transform.scale(surface, (tile_size, tile_size))
                    corner_tiles[corner_type] = corner_tile
                    print(f"      Rounded floor corner {corner_type} found at ({tile_x}, {tile_y}) [score: {base_score:.1f}]")
                else:
                    print(f"      No good rounded floor corner found for {corner_type}")
            
            return floor_tile, wall_tile, corner_tiles
            
        except pygame.error as e:
            print(f"  Error loading tileset {tileset_path}: {e}")
            return None, None, {}
    
    # Load tiles for all dungeon levels
    level_sprites = {}
    
    for level, tileset_config in level_tilesets.items():
        print(f"  Loading Level {level} tileset...")
        
        floor_tile = None
        wall_tile = None
        corner_tiles = {}
        tileset_loaded = None
        
        # Try primary tileset first
        primary_path = os.path.join(tileset_config["folder"], tileset_config["tileset"])
        if os.path.exists(primary_path):
            floor_tile, wall_tile, corner_tiles = extract_tiles_from_tileset(primary_path)
            if floor_tile and wall_tile:
                tileset_loaded = tileset_config["tileset"]
        
        # Try backup tilesets if primary failed
        if not (floor_tile and wall_tile) and "backup_tilesets" in tileset_config:
            for backup_tileset in tileset_config["backup_tilesets"]:
                backup_path = os.path.join(tileset_config["folder"], backup_tileset)
                if os.path.exists(backup_path):
                    floor_tile, wall_tile, corner_tiles = extract_tiles_from_tileset(backup_path)
                    if floor_tile and wall_tile:
                        tileset_loaded = backup_tileset
                        break
        
        # Create fallback tiles if extraction failed
        if not floor_tile:
            floor_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
            # Use level-appropriate colors based on authentic Undertale palettes
            if level == 1:  # Ruins - authentic pink from ruins
                floor_tile.fill((158, 130, 153))  # Darker pink from actual ruins
            elif level == 2:  # Snowdin - icy white/blue
                floor_tile.fill((225, 235, 245))  # Light icy blue
            elif level == 3:  # Waterfall - dark cave blue
                floor_tile.fill((85, 110, 140))   # Dark blue-gray
            elif level == 4:  # Hotland - orange/red lava
                floor_tile.fill((180, 90, 60))    # Dark orange-red
            elif level == 5:  # Core - metallic blue-gray
                floor_tile.fill((120, 130, 145))  # Metallic blue-gray
            
            print(f"      Using fallback floor color for Level {level}")
        
        if not wall_tile:
            wall_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
            # Use level-appropriate wall colors
            if level == 1:  # Ruins - dark purple/brown
                wall_tile.fill((85, 65, 75))      # Darker ruins wall
            elif level == 2:  # Snowdin - darker icy blue
                wall_tile.fill((90, 115, 140))    # Darker ice
            elif level == 3:  # Waterfall - very dark cave
                wall_tile.fill((45, 60, 80))      # Very dark cave
            elif level == 4:  # Hotland - dark red/black
                wall_tile.fill((80, 45, 30))      # Dark lava rock
            elif level == 5:  # Core - dark metallic
                wall_tile.fill((60, 65, 80))      # Dark metal
            
            print(f"      Using fallback wall color for Level {level}")
        
        # Store the tiles
        level_sprites[level] = {
            "floor": floor_tile,
            "wall": wall_tile,
            "corners": corner_tiles,
            "tileset_name": tileset_loaded or "fallback"
        }
        
        print(f"    Level {level}: {level_sprites[level]['tileset_name']}")
    
    # Use Level 1 (Ruins) as the default for now, but store all levels
    default_level = 1
    wall_sprite = level_sprites[default_level]["wall"]
    floor_sprite = level_sprites[default_level]["floor"]
    
    # Store level sprites globally so we can access them later
    sprites["level_sprites"] = level_sprites
    
    print(f"  Loaded tiles for {len(level_sprites)} dungeon levels")
    
    # Use the SAME consistent sprites for ALL wall and floor variants
    wall_variants = [
        "wall_stone_brick1.png", "wall_stone_dark0.png", "wall_brick_brown0.png", 
        "wall_marble_wall1.png", "wall_sandstone_wall0.png", "wall_metal_wall_brown.png"
    ]
    
    floor_variants = [
        "floor_sandstone_floor0.png", "floor_dirt0.png", "floor_pebble_brown0.png", 
        "floor_marble_floor1.png", "floor_stone_floor0.png", "floor_wooden_floor.png"
    ]
    
    # Assign the same consistent sprites to all variants
    for wall_variant in wall_variants:
        sprites[wall_variant] = wall_sprite.copy()
    
    for floor_variant in floor_variants:
        sprites[floor_variant] = floor_sprite.copy()
    
    print("  Loaded: Consistent wall and floor textures for all variants")
    
    # Load stairs sprite (using a ruins door/passage)
    print("Loading Undertale stairs sprite...")
    try:
        ruins_path = os.path.join("assets", "undertale", "Overworld", "Locations", "01 - Ruins")
        stairs_path = os.path.join(ruins_path, "spr_ruinsdoor1_0.png")
        if os.path.exists(stairs_path):
            sprites["stairs"] = pygame.image.load(stairs_path)
            sprites["stairs"] = pygame.transform.scale(sprites["stairs"], (TILE_SIZE, TILE_SIZE))
            print("  Loaded: stairs (Undertale ruins door)")
        else:
            print("  Warning: Undertale stairs sprite not found")
    except pygame.error as e:
        print(f"  Error loading Undertale stairs sprite: {e}")
    
    # Load Undertale player sprites (using different characters with directional movement)
    print("Loading Undertale player sprites with directional movement...")
    
    # Warrior = Frisk (main character)
    frisk_path = os.path.join("assets", "undertale", "Overworld", "Characters", "Frisk")
    frisk_sprites = {
        "down": "spr_maincharad_0.png",    # Frisk facing down
        "left": "spr_maincharal_0.png",    # Frisk facing left  
        "right": "spr_maincharar_0.png",   # Frisk facing right
        "up": "spr_maincharau_0.png"       # Frisk facing up
    }
    
    # Load all directional sprites for warrior (Frisk)
    for direction, sprite_file in frisk_sprites.items():
        try:
            sprite_file_path = os.path.join(frisk_path, sprite_file)
            if os.path.exists(sprite_file_path):
                frisk_sprite = pygame.image.load(sprite_file_path)
                sprites[f"player_warrior_{direction}"] = pygame.transform.scale(frisk_sprite, (TILE_SIZE, TILE_SIZE))
                
                # Also load larger portrait versions (for battle/inventory/shop screens)
                sprites[f"portrait_warrior_{direction}"] = pygame.transform.scale(frisk_sprite, (128, 128))
                
                print(f"  Loaded: warrior_{direction} (Frisk - {sprite_file}) with portrait")
            else:
                print(f"  Warning: Undertale Frisk sprite not found: {sprite_file_path}")
        except pygame.error as e:
            print(f"  Error loading Undertale Frisk sprite {sprite_file}: {e}")
    
    # Set default warrior sprite (facing down)
    if "player_warrior_down" in sprites:
        sprites["player_warrior"] = sprites["player_warrior_down"]
        sprites["portrait_warrior"] = sprites["portrait_warrior_down"]
    
    # Mage = Sans (skeleton mage)
    sans_path = os.path.join("assets", "undertale", "Overworld", "Characters", "sans")
    sans_files = ["spr_sans_0.png", "spr_sansoverworld_0.png"]
    sans_loaded = False
    
    # Try to find Sans sprite files
    for sans_file in sans_files:
        try:
            sans_sprite_path = os.path.join(sans_path, sans_file)
            if os.path.exists(sans_sprite_path):
                sans_base = pygame.image.load(sans_sprite_path)
                sans_base = pygame.transform.scale(sans_base, (TILE_SIZE, TILE_SIZE))
                
                # Create directional sprites for Sans (using same sprite, different rotations/flips)
                sprites[f"player_mage_down"] = sans_base.copy()
                sprites[f"player_mage_left"] = pygame.transform.flip(sans_base, True, False)  # Flip horizontally
                sprites[f"player_mage_right"] = sans_base.copy()  
                sprites[f"player_mage_up"] = sans_base.copy()  # Sans looks similar from all angles
                sprites["player_mage"] = sans_base  # Default
                
                # Create portrait versions for Sans
                sans_portrait = pygame.transform.scale(sans_base, (128, 128))
                sprites[f"portrait_mage_down"] = sans_portrait.copy()
                sprites[f"portrait_mage_left"] = pygame.transform.flip(sans_portrait, True, False)
                sprites[f"portrait_mage_right"] = sans_portrait.copy()
                sprites[f"portrait_mage_up"] = sans_portrait.copy()
                sprites["portrait_mage"] = sans_portrait  # Default
                
                print(f"  Loaded: mage (Sans - {sans_file}) with directional variants and portraits")
                sans_loaded = True
                break
        except pygame.error as e:
            print(f"  Error loading Sans sprite {sans_file}: {e}")
    
    if not sans_loaded:
        print("  Warning: No Sans sprite found for mage")
    
    # Archer = Monster Kid (dinosaur-like character)
    monster_kid_path = os.path.join("assets", "undertale", "Overworld", "Characters", "Monster Kid")
    monster_kid_files = ["spr_mkid_0.png", "spr_mkidoverworld_0.png", "spr_mkid_walk_0.png"]
    monster_kid_loaded = False
    
    # Try to find Monster Kid sprite files
    for mk_file in monster_kid_files:
        try:
            mk_sprite_path = os.path.join(monster_kid_path, mk_file)
            if os.path.exists(mk_sprite_path):
                mk_base = pygame.image.load(mk_sprite_path)
                mk_base = pygame.transform.scale(mk_base, (TILE_SIZE, TILE_SIZE))
                
                # Create directional sprites for Monster Kid
                sprites[f"player_archer_down"] = mk_base.copy()
                sprites[f"player_archer_left"] = pygame.transform.flip(mk_base, True, False)
                sprites[f"player_archer_right"] = mk_base.copy()
                sprites[f"player_archer_up"] = mk_base.copy()
                sprites["player_archer"] = mk_base  # Default
                
                # Create portrait versions for Monster Kid
                mk_portrait = pygame.transform.scale(mk_base, (128, 128))
                sprites[f"portrait_archer_down"] = mk_portrait.copy()
                sprites[f"portrait_archer_left"] = pygame.transform.flip(mk_portrait, True, False)
                sprites[f"portrait_archer_right"] = mk_portrait.copy()
                sprites[f"portrait_archer_up"] = mk_portrait.copy()
                sprites["portrait_archer"] = mk_portrait  # Default
                
                print(f"  Loaded: archer (Monster Kid - {mk_file}) with directional variants and portraits")
                monster_kid_loaded = True
                break
        except pygame.error as e:
            print(f"  Error loading Monster Kid sprite {mk_file}: {e}")
    
    # Fallback: Use Papyrus for archer if Monster Kid not found
    if not monster_kid_loaded:
        papyrus_path = os.path.join("assets", "undertale", "Overworld", "Characters", "Papyrus")
        papyrus_files = ["spr_papyrus_0.png", "spr_papyrusoverworld_0.png"]
        
        for papyrus_file in papyrus_files:
            try:
                papyrus_sprite_path = os.path.join(papyrus_path, papyrus_file)
                if os.path.exists(papyrus_sprite_path):
                    papyrus_base = pygame.image.load(papyrus_sprite_path)
                    papyrus_base = pygame.transform.scale(papyrus_base, (TILE_SIZE, TILE_SIZE))
                    
                    # Create directional sprites for Papyrus
                    sprites[f"player_archer_down"] = papyrus_base.copy()
                    sprites[f"player_archer_left"] = pygame.transform.flip(papyrus_base, True, False)
                    sprites[f"player_archer_right"] = papyrus_base.copy()
                    sprites[f"player_archer_up"] = papyrus_base.copy()
                    sprites["player_archer"] = papyrus_base  # Default
                    
                    # Create portrait versions for Papyrus
                    papyrus_portrait = pygame.transform.scale(papyrus_base, (128, 128))
                    sprites[f"portrait_archer_down"] = papyrus_portrait.copy()
                    sprites[f"portrait_archer_left"] = pygame.transform.flip(papyrus_portrait, True, False)
                    sprites[f"portrait_archer_right"] = papyrus_portrait.copy()
                    sprites[f"portrait_archer_up"] = papyrus_portrait.copy()
                    sprites["portrait_archer"] = papyrus_portrait  # Default
                    
                    print(f"  Loaded: archer (Papyrus fallback - {papyrus_file}) with directional variants and portraits")
                    break
            except pygame.error as e:
                print(f"  Error loading Papyrus fallback sprite {papyrus_file}: {e}")
    
    # Rogue class (if needed) = Chara
    chara_path = os.path.join("assets", "undertale", "Overworld", "Characters", "Chara")
    chara_files = ["spr_chara_0.png"]
    chara_loaded = False
    
    # Try to find Chara sprite files
    for chara_file in chara_files:
        try:
            chara_sprite_path = os.path.join(chara_path, chara_file)
            if os.path.exists(chara_sprite_path):
                chara_base = pygame.image.load(chara_sprite_path)
                chara_base = pygame.transform.scale(chara_base, (TILE_SIZE, TILE_SIZE))
                
                # Create directional sprites for Chara
                sprites[f"player_rogue_down"] = chara_base.copy()
                sprites[f"player_rogue_left"] = pygame.transform.flip(chara_base, True, False)
                sprites[f"player_rogue_right"] = chara_base.copy()
                sprites[f"player_rogue_up"] = chara_base.copy()
                sprites["player_rogue"] = chara_base  # Default
                
                # Create portrait versions for Chara
                chara_portrait = pygame.transform.scale(chara_base, (128, 128))
                sprites[f"portrait_rogue_down"] = chara_portrait.copy()
                sprites[f"portrait_rogue_left"] = pygame.transform.flip(chara_portrait, True, False)
                sprites[f"portrait_rogue_right"] = chara_portrait.copy()
                sprites[f"portrait_rogue_up"] = chara_portrait.copy()
                sprites["portrait_rogue"] = chara_portrait  # Default
                
                print(f"  Loaded: rogue (Chara - {chara_file}) with directional variants and portraits")
                chara_loaded = True
                break
        except pygame.error as e:
            print(f"  Error loading Chara sprite {chara_file}: {e}")
    
    # If no specific directional sprites exist, create fallbacks using the default sprite
    for class_name in ["warrior", "mage", "archer", "rogue"]:
        if f"player_{class_name}" in sprites:
            base_sprite = sprites[f"player_{class_name}"]
            base_portrait = pygame.transform.scale(base_sprite, (128, 128))
            sprites[f"portrait_{class_name}"] = base_portrait
            
            for direction in ["down", "left", "right", "up"]:
                if f"player_{class_name}_{direction}" not in sprites:
                    sprites[f"player_{class_name}_{direction}"] = base_sprite.copy()
                    sprites[f"portrait_{class_name}_{direction}"] = base_portrait.copy()
                    if direction == "left":  # Flip for left direction
                        sprites[f"player_{class_name}_{direction}"] = pygame.transform.flip(base_sprite, True, False)
                        sprites[f"portrait_{class_name}_{direction}"] = pygame.transform.flip(base_portrait, True, False)
    
    # Load Undertale monster sprites 
    print("Loading Undertale monster sprites...")
    
    # Load Dummy for goblin
    dummy_path = os.path.join("assets", "undertale", "Overworld", "Characters", "Dummies")
    try:
        dummy_sprite_path = os.path.join(dummy_path, "spr_dummy_0.png")
        if os.path.exists(dummy_sprite_path):
            dummy_sprite = pygame.image.load(dummy_sprite_path)
            sprites["monster_goblin"] = pygame.transform.scale(dummy_sprite, (TILE_SIZE, TILE_SIZE))
            sprites["portrait_goblin"] = pygame.transform.scale(dummy_sprite, (128, 128))
            print("  Loaded: goblin (Undertale Dummy) with portrait")
        else:
            print("  Warning: Undertale dummy sprite not found")
    except pygame.error as e:
        print(f"  Error loading Undertale dummy sprite: {e}")
    
    # Load Flowey for orc  
    flowey_path = os.path.join("assets", "undertale", "Overworld", "Characters", "Flowey")
    try:
        flowey_sprite_path = os.path.join(flowey_path, "spr_flowey_0.png")
        if os.path.exists(flowey_sprite_path):
            flowey_sprite = pygame.image.load(flowey_sprite_path)
            sprites["monster_orc"] = pygame.transform.scale(flowey_sprite, (TILE_SIZE, TILE_SIZE))
            sprites["portrait_orc"] = pygame.transform.scale(flowey_sprite, (128, 128))
            print("  Loaded: orc (Undertale Flowey) with portrait")
        else:
            print("  Warning: Undertale Flowey sprite not found")
    except pygame.error as e:
        print(f"  Error loading Undertale Flowey sprite: {e}")
    
    # Load Papyrus for troll
    papyrus_path = os.path.join("assets", "undertale", "Overworld", "Characters", "Papyrus")
    try:
        papyrus_files = ["spr_papyrus_0.png", "spr_papyrusoverworld_0.png"]
        papyrus_loaded = False
        for papyrus_file in papyrus_files:
            papyrus_sprite_path = os.path.join(papyrus_path, papyrus_file)
            if os.path.exists(papyrus_sprite_path):
                papyrus_sprite = pygame.image.load(papyrus_sprite_path)
                sprites["monster_troll"] = pygame.transform.scale(papyrus_sprite, (TILE_SIZE, TILE_SIZE))
                sprites["portrait_troll"] = pygame.transform.scale(papyrus_sprite, (128, 128))
                print(f"  Loaded: troll (Undertale Papyrus - {papyrus_file}) with portrait")
                papyrus_loaded = True
                break
        
        if not papyrus_loaded:
            print("  Warning: No Undertale Papyrus sprite found")
    except pygame.error as e:
        print(f"  Error loading Undertale Papyrus sprite: {e}")
    
    # Load Sans for dragon (boss)
    sans_path = os.path.join("assets", "undertale", "Overworld", "Characters", "sans")
    try:
        sans_files = ["spr_sans_0.png", "spr_sansoverworld_0.png"]
        sans_loaded = False
        for sans_file in sans_files:
            sans_sprite_path = os.path.join(sans_path, sans_file)
            if os.path.exists(sans_sprite_path):
                sans_sprite = pygame.image.load(sans_sprite_path)
                sprites["monster_dragon"] = pygame.transform.scale(sans_sprite, (TILE_SIZE, TILE_SIZE))
                sprites["portrait_dragon"] = pygame.transform.scale(sans_sprite, (128, 128))
                print(f"  Loaded: dragon (Undertale Sans - {sans_file}) with portrait")
                sans_loaded = True
                break
        
        if not sans_loaded:
            print("  Warning: No Undertale Sans sprite found")
    except pygame.error as e:
        print(f"  Error loading Undertale Sans sprite: {e}")
    
    # Load Undertale item sprites  
    print("Loading Undertale item sprites...")
    
    # Load potion sprite (use UI exclamation mark as potion)
    ui_path = os.path.join("assets", "undertale", "UI-20250721T005822Z-1-001", "UI")
    try:
        potion_path = os.path.join(ui_path, "spr_exc_0.png")
        if os.path.exists(potion_path):
            sprites["item_potion"] = pygame.image.load(potion_path)
            sprites["item_potion"] = pygame.transform.scale(sprites["item_potion"], (TILE_SIZE, TILE_SIZE))
            print("  Loaded: potion (Undertale UI exclamation)")
        else:
            print("  Warning: Undertale potion sprite not found")
    except pygame.error as e:
        print(f"  Error loading Undertale potion sprite: {e}")
    
    # Load weapon sprites (create simple placeholder weapons from UI elements)
    print("Loading Undertale-style weapon sprites...")
    weapon_sprites = [
        "dagger", "short_sword1", "long_sword1", "battle_axe1", 
        "war_axe1", "greatsword1", "executioner_axe1", "demon_blade",
        "quarterstaff", "elven_dagger", "blessed_blade", "demon_trident", "trishula"
    ]
    
    # Load weapon sprites from original Crawl tiles
    print("Loading original weapon sprites...")
    weapon_sprites = [
        "dagger", "short_sword1", "long_sword1", "battle_axe1", 
        "war_axe1", "greatsword1", "executioner_axe1", "demon_blade",
        "quarterstaff", "elven_dagger", "blessed_blade", "demon_trident", "trishula"
    ]
    
    # Load from crawl-tiles weapon folder
    weapon_folder = os.path.join("assets", "crawl-tiles Oct-5-2010", "item", "weapon")
    
    for weapon_name in weapon_sprites:
        try:
            weapon_path = os.path.join(weapon_folder, f"{weapon_name}.png")
            if os.path.exists(weapon_path):
                weapon_sprite = pygame.image.load(weapon_path)
                sprites[f"weapon_{weapon_name}"] = pygame.transform.scale(weapon_sprite, (TILE_SIZE, TILE_SIZE))
                print(f"  Loaded: {weapon_name} (original crawl sprite)")
            else:
                # Try alternative names or create fallback
                print(f"  Warning: {weapon_name} not found, using fallback")
                fallback_sprite = pygame.Surface((TILE_SIZE, TILE_SIZE))
                fallback_sprite.fill((100, 100, 100))  # Gray fallback
                sprites[f"weapon_{weapon_name}"] = fallback_sprite
        except pygame.error as e:
            print(f"  Error loading weapon sprite {weapon_name}: {e}")
    
    # Load ranged weapons
    ranged_sprites = ["sling1", "bow1", "bow2", "crossbow1", "longbow", "throwing_net"]
    ranged_folder = os.path.join("assets", "crawl-tiles Oct-5-2010", "item", "weapon", "ranged")
    
    for ranged_name in ranged_sprites:
        try:
            # Try different possible names
            possible_names = [ranged_name, ranged_name.replace("1", ""), ranged_name.replace("bow", "bow_")]
            loaded = False
            
            for possible_name in possible_names:
                ranged_path = os.path.join(ranged_folder, f"{possible_name}.png")
                if os.path.exists(ranged_path):
                    ranged_sprite = pygame.image.load(ranged_path)
                    sprites[f"weapon_{ranged_name}"] = pygame.transform.scale(ranged_sprite, (TILE_SIZE, TILE_SIZE))
                    print(f"  Loaded: ranged/{ranged_name} (original crawl sprite)")
                    loaded = True
                    break
            
            if not loaded:
                print(f"  Warning: ranged/{ranged_name} not found, using fallback")
                fallback_sprite = pygame.Surface((TILE_SIZE, TILE_SIZE))
                fallback_sprite.fill((120, 100, 80))  # Brown fallback for ranged
                sprites[f"weapon_{ranged_name}"] = fallback_sprite
        except pygame.error as e:
            print(f"  Error loading ranged weapon sprite {ranged_name}: {e}")
    
    # Load armor sprites from original Crawl tiles  
    print("Loading original armor sprites...")
    armor_sprites = [
        "leather_armour1", "leather_armour2", "elven_leather_armor", "troll_hide",
        "ring_mail1", "scale_mail1", "chain_mail1", "banded_mail1",
        "splint_mail1", "plate_mail1", "crystal_plate_mail"
    ]
    
    # Load from crawl-tiles armour folder
    armour_folder = os.path.join("assets", "crawl-tiles Oct-5-2010", "item", "armour")
    
    for armor_name in armor_sprites:
        try:
            # Try different possible names
            possible_names = [armor_name, armor_name.replace("armour", "armor"), armor_name.replace("1", "")]
            loaded = False
            
            for possible_name in possible_names:
                armor_path = os.path.join(armour_folder, f"{possible_name}.png")
                if os.path.exists(armor_path):
                    armor_sprite = pygame.image.load(armor_path)
                    sprites[f"armor_{armor_name}"] = pygame.transform.scale(armor_sprite, (TILE_SIZE, TILE_SIZE))
                    print(f"  Loaded: {armor_name} (original crawl sprite)")
                    loaded = True
                    break
            
            if not loaded:
                print(f"  Warning: {armor_name} not found, using fallback")
                fallback_sprite = pygame.Surface((TILE_SIZE, TILE_SIZE))
                fallback_sprite.fill((150, 120, 100))  # Brown fallback for armor
                sprites[f"armor_{armor_name}"] = fallback_sprite
        except pygame.error as e:
            print(f"  Error loading armor sprite {armor_name}: {e}")
    
    # Load treasure chest sprites (create from ruins objects)
    print("Loading Undertale treasure chest sprites...")
    ruins_path = os.path.join("assets", "undertale", "Overworld", "Locations", "01 - Ruins")
    
    # Use candy dish as chest
    chest_files = ["spr_candydish_0.png", "spr_candydish2_0.png"]
    for i, chest_file in enumerate(chest_files):
        try:
            chest_sprite_path = os.path.join(ruins_path, chest_file)
            if os.path.exists(chest_sprite_path):
                sprite_key = "chest_closed" if i == 0 else "chest_open"
                sprites[sprite_key] = pygame.image.load(chest_sprite_path)
                sprites[sprite_key] = pygame.transform.scale(sprites[sprite_key], (TILE_SIZE, TILE_SIZE))
                print(f"  Loaded: {sprite_key} (Undertale {chest_file})")
        except pygame.error as e:
            print(f"  Error loading Undertale chest sprite {chest_file}: {e}")
    
    # Load additional weapon sprites from both crawl folders
    print("Loading additional original weapon variants...")
    additional_weapons = [
        "ancient_sword", "axe", "claymore", "cutlass_1", "golden_sword",
        "halberd_1", "hammer_1_new", "katana", "mace_1_new", "rapier_1",
        "scimitar_1_new", "scythe_1_new", "trident_1", "war_hammer"
    ]
    
    # Try both weapon folders
    weapon_folders = [
        weapon_folder,  # crawl-tiles weapon folder
        os.path.join("assets", "Dungeon Crawl Stone Soup Full", "item", "weapon")  # DCSS weapon folder
    ]
    
    for weapon_name in additional_weapons:
        try:
            # Try different possible names
            possible_names = [weapon_name, weapon_name.replace("_1", ""), weapon_name.replace("_new", "")]
            loaded = False
            
            for folder in weapon_folders:
                if loaded:
                    break
                for possible_name in possible_names:
                    weapon_path = os.path.join(folder, f"{possible_name}.png")
                    if os.path.exists(weapon_path):
                        weapon_sprite = pygame.image.load(weapon_path)
                        sprites[f"weapon_{weapon_name}"] = pygame.transform.scale(weapon_sprite, (TILE_SIZE, TILE_SIZE))
                        print(f"  Loaded: {weapon_name} (original crawl sprite)")
                        loaded = True
                        break
            
            if not loaded:
                # Use a basic weapon sprite as fallback if we have one loaded
                if "weapon_dagger" in sprites:
                    sprites[f"weapon_{weapon_name}"] = sprites["weapon_dagger"].copy()
                    print(f"  Loaded: {weapon_name} (dagger fallback)")
                else:
                    fallback_sprite = pygame.Surface((TILE_SIZE, TILE_SIZE))
                    fallback_sprite.fill((100, 100, 100))
                    sprites[f"weapon_{weapon_name}"] = fallback_sprite
                    print(f"  Loaded: {weapon_name} (gray fallback)")
        except pygame.error as e:
            print(f"  Error loading additional weapon sprite {weapon_name}: {e}")
    
    # Load Undertale shopkeeper sprites
    print("Loading Undertale shopkeeper sprites...")
    
    # Load Gerson (turtle shopkeeper) from shop assets
    gerson_path = os.path.join("assets", "undertale", "Shops-20250721T005643Z-1-001", "Shops", "Gerson")
    try:
        # Try to load Gerson's body as the main shopkeeper sprite
        gerson_files = ["spr_shopkeeper2_body_0.png", "spr_shop2_bg_0.png"]
        shopkeeper_loaded = False
        
        for gerson_file in gerson_files:
            gerson_sprite_path = os.path.join(gerson_path, gerson_file)
            if os.path.exists(gerson_sprite_path):
                gerson_sprite = pygame.image.load(gerson_sprite_path)
                sprites["shopkeeper_npc"] = pygame.transform.scale(gerson_sprite, (TILE_SIZE, TILE_SIZE))
                sprites["portrait_shopkeeper"] = pygame.transform.scale(gerson_sprite, (128, 128))
                print(f"  Loaded: shopkeeper (Undertale Gerson - {gerson_file}) with portrait")
                shopkeeper_loaded = True
                break
        
        if not shopkeeper_loaded:
            # Fallback: use Papyrus as shopkeeper
            papyrus_path = os.path.join("assets", "undertale", "Overworld", "Characters", "Papyrus")
            papyrus_files = ["spr_papyrus_0.png", "spr_papyrusoverworld_0.png"]
            for papyrus_file in papyrus_files:
                papyrus_sprite_path = os.path.join(papyrus_path, papyrus_file)
                if os.path.exists(papyrus_sprite_path):
                    papyrus_sprite = pygame.image.load(papyrus_sprite_path)
                    sprites["shopkeeper_npc"] = pygame.transform.scale(papyrus_sprite, (TILE_SIZE, TILE_SIZE))
                    sprites["portrait_shopkeeper"] = pygame.transform.scale(papyrus_sprite, (128, 128))
                    print(f"  Loaded: shopkeeper (Undertale Papyrus fallback - {papyrus_file}) with portrait")
                    shopkeeper_loaded = True
                    break
        
        if not shopkeeper_loaded:
            print("  Warning: No Undertale shopkeeper sprite found")
            
    except pygame.error as e:
        print(f"  Error loading Undertale shopkeeper sprite: {e}")

    print(f"Undertale sprite loading complete. Loaded {len(sprites)} sprites.")

    # Load Undertale-style skill spell icons
    print("Loading Undertale skill spell icons...")
    
    # Use UI elements for skill icons
    ui_config_path = os.path.join("assets", "undertale", "UI-20250721T005822Z-1-001", "UI", "Config")
    
    # Load warrior skill icon (Power Strike) - use Z button
    power_strike_path = os.path.join(ui_config_path, "spr_test_zbutton_0.png")
    if os.path.exists(power_strike_path):
        sprites["skill_power_strike"] = pygame.image.load(power_strike_path)
        sprites["skill_power_strike"] = pygame.transform.scale(sprites["skill_power_strike"], (TILE_SIZE, TILE_SIZE))
        print("  Loaded: Power Strike skill icon (Undertale Z button)")
    
    # Load mage skill icon (Fireball) - use X button
    fireball_path = os.path.join(ui_config_path, "spr_test_xbutton_0.png")
    if os.path.exists(fireball_path):
        sprites["skill_fireball"] = pygame.image.load(fireball_path)
        sprites["skill_fireball"] = pygame.transform.scale(sprites["skill_fireball"], (TILE_SIZE, TILE_SIZE))
        print("  Loaded: Fireball skill icon (Undertale X button)")
    
    # Load archer skill icon (Double Shot) - use C button
    double_shot_path = os.path.join(ui_config_path, "spr_test_cbutton_0.png")
    if os.path.exists(double_shot_path):
        sprites["skill_double_shot"] = pygame.image.load(double_shot_path)
        sprites["skill_double_shot"] = pygame.transform.scale(sprites["skill_double_shot"], (TILE_SIZE, TILE_SIZE))
        print("  Loaded: Double Shot skill icon (Undertale C button)")
    
    print(f"Undertale skill icon loading complete.")

    # Load Undertale UI elements
    print("Loading Undertale UI elements...")
    
    # Create UI elements from Undertale assets
    ui_files = {
        "tab_selected": "spr_test_zbutton_1.png",      # Selected state
        "tab_unselected": "spr_test_zbutton_0.png",    # Normal state
        "tab_mouseover": "spr_test_zbutton_2.png",     # Hover state
        "tab_item": "spr_exc_0.png",                   # Item tab
        "tab_spell": "spr_exc_f_0.png",                # Spell tab
        "tab_monster": "spr_musblc_0.png"              # Monster tab
    }
    
    for ui_name, ui_file in ui_files.items():
        try:
            ui_file_path = os.path.join(ui_config_path, ui_file)
            if not os.path.exists(ui_file_path):
                # Try in main UI folder
                ui_file_path = os.path.join(ui_path, ui_file)
            
            if os.path.exists(ui_file_path):
                ui_elements[ui_name] = pygame.image.load(ui_file_path)
                ui_elements[ui_name] = pygame.transform.scale(ui_elements[ui_name], (64, 32))  # Standard button size
                print(f"  Loaded: {ui_name} (Undertale {ui_file})")
            else:
                print(f"  Warning: Undertale UI element not found: {ui_file}")
        except pygame.error as e:
            print(f"  Error loading Undertale UI element {ui_file}: {e}")
    
    print(f"Undertale UI loading complete. Loaded {len(ui_elements)} UI elements.")
    
    # Create fallback portraits for any missing sprites
    print("Creating fallback portraits...")
    
    # Ensure all character classes have portraits
    for class_name in ["warrior", "mage", "archer", "rogue"]:
        if f"portrait_{class_name}" not in sprites:
            if f"player_{class_name}" in sprites:
                # Create portrait from player sprite
                base_sprite = sprites[f"player_{class_name}"]
                sprites[f"portrait_{class_name}"] = pygame.transform.scale(base_sprite, (128, 128))
                print(f"  Created fallback portrait for {class_name}")
            else:
                # Create colored fallback
                fallback_surface = pygame.Surface((128, 128))
                fallback_surface.fill((100, 100, 150))  # Purple-ish color
                sprites[f"portrait_{class_name}"] = fallback_surface
                print(f"  Created colored fallback portrait for {class_name}")
    
    # Ensure all monsters have portraits
    for monster_name in ["goblin", "orc", "troll", "dragon"]:
        if f"portrait_{monster_name}" not in sprites:
            if f"monster_{monster_name}" in sprites:
                # Create portrait from monster sprite
                base_sprite = sprites[f"monster_{monster_name}"]
                sprites[f"portrait_{monster_name}"] = pygame.transform.scale(base_sprite, (128, 128))
                print(f"  Created fallback portrait for {monster_name}")
            else:
                # Create colored fallback
                fallback_surface = pygame.Surface((128, 128))
                fallback_surface.fill((150, 100, 100))  # Red-ish color for monsters
                sprites[f"portrait_{monster_name}"] = fallback_surface
                print(f"  Created colored fallback portrait for {monster_name}")
    
    # Ensure shopkeeper has portrait
    if "portrait_shopkeeper" not in sprites:
        if "shopkeeper_npc" in sprites:
            base_sprite = sprites["shopkeeper_npc"]
            sprites["portrait_shopkeeper"] = pygame.transform.scale(base_sprite, (128, 128))
            print("  Created fallback portrait for shopkeeper")
        else:
            fallback_surface = pygame.Surface((128, 128))
            fallback_surface.fill((100, 150, 100))  # Green-ish color for shopkeeper
            sprites["portrait_shopkeeper"] = fallback_surface
            print("  Created colored fallback portrait for shopkeeper")
    
    print("=== Undertale sprite conversion complete! ===")

def set_dungeon_level_tileset(level):
    """Change the tileset based on current dungeon level."""
    global sprites
    
    if "level_sprites" in sprites and level in sprites["level_sprites"]:
        level_data = sprites["level_sprites"][level]
        
        # Update all wall variants to use the new level's wall tile
        wall_variants = [
            "wall_stone_brick1.png", "wall_stone_dark0.png", "wall_brick_brown0.png", 
            "wall_marble_wall1.png", "wall_sandstone_wall0.png", "wall_metal_wall_brown.png"
        ]
        
        for wall_variant in wall_variants:
            sprites[wall_variant] = level_data["wall"].copy()
        
        # Update all floor variants to use the new level's floor tile
        floor_variants = [
            "floor_sandstone_floor0.png", "floor_dirt0.png", "floor_pebble_brown0.png", 
            "floor_marble_floor1.png", "floor_stone_floor0.png", "floor_wooden_floor.png"
        ]
        
        for floor_variant in floor_variants:
            sprites[floor_variant] = level_data["floor"].copy()
        
        # Store corner tiles for use in dungeon rendering
        if "corners" in level_data:
            for corner_name, corner_tile in level_data["corners"].items():
                sprites[f"corner_{corner_name}"] = corner_tile.copy()
        
        print(f"Switched to Level {level} tileset: {level_data['tileset_name']}")
        return True
    else:
        print(f"Warning: No tileset available for level {level}")
        return False

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

def draw_portrait(surface, entity, x, y, size=128, border_color=WHITE, border_width=3):
    """Draw a character/monster/shopkeeper portrait with a frame."""
    # Determine which portrait to use
    portrait_key = None
    
    if hasattr(entity, 'char_class'):
        # Player character
        direction = getattr(entity, 'direction', 'down')
        portrait_key = f"portrait_{entity.char_class}_{direction}"
        if portrait_key not in sprites:
            portrait_key = f"portrait_{entity.char_class}"
    elif hasattr(entity, 'enemy_type'):
        # Enemy/monster
        portrait_key = f"portrait_{entity.enemy_type}"
    elif hasattr(entity, 'name') and entity.name == "Merchant":
        # Shopkeeper
        portrait_key = "portrait_shopkeeper"
    
    # Draw portrait if available
    if portrait_key and portrait_key in sprites:
        portrait = sprites[portrait_key]
        # Scale to requested size if different
        if portrait.get_width() != size or portrait.get_height() != size:
            portrait = pygame.transform.scale(portrait, (size, size))
        
        # Draw border/frame
        border_rect = pygame.Rect(x - border_width, y - border_width, 
                                size + 2 * border_width, size + 2 * border_width)
        pygame.draw.rect(surface, border_color, border_rect, border_width)
        
        # Draw portrait
        surface.blit(portrait, (x, y))
    else:
        # Fallback: draw a colored square with the entity's icon
        fallback_rect = pygame.Rect(x, y, size, size)
        
        # Choose appropriate background color based on entity type
        if hasattr(entity, 'char_class'):
            bg_color = (60, 90, 140)  # Blue for players
        elif hasattr(entity, 'enemy_type'):
            bg_color = (140, 60, 60)  # Red for enemies  
        elif hasattr(entity, 'name') and entity.name == "Merchant":
            bg_color = (60, 140, 60)  # Green for shopkeeper
        else:
            bg_color = DARK_GRAY
        
        pygame.draw.rect(surface, bg_color, fallback_rect)
        pygame.draw.rect(surface, border_color, fallback_rect, border_width)
        
        # Draw icon text in center
        icon_text = getattr(entity, 'icon', '?')
        try:
            # Use a smaller font for better fit
            icon_font = pygame.font.Font(None, max(24, size // 4))
            icon_surface = icon_font.render(icon_text, True, WHITE)
            icon_rect = icon_surface.get_rect(center=fallback_rect.center)
            surface.blit(icon_surface, icon_rect)
        except:
            # If font rendering fails, just draw a simple shape
            pygame.draw.circle(surface, WHITE, fallback_rect.center, size // 6)

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
    'panel_light': (55, 60, 65)
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
    "warrior": {"hp": 100, "attack": 12, "defense": 8, "icon": UI["warrior"], "weapon": "Sword", "mana": 0},
    "mage": {"hp": 70, "attack": 15, "defense": 4, "icon": UI["mage"], "weapon": "Staff", "mana": 20},
    "archer": {"hp": 85, "attack": 10, "defense": 6, "icon": UI["archer"], "weapon": "Bow", "mana": 0}
}

# --- Enemy Types ---
ENEMIES = {
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
        self.xp = 0
        self.level = 1
        self.gold = 100  # Starting gold for shopping
        self.direction = "down"  # Track which direction the player is facing
        
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
    
    def update_direction(self, dx, dy):
        """Update the player's facing direction based on movement."""
        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"
        elif dy > 0:
            self.direction = "down"
        elif dy < 0:
            self.direction = "up"
    
    def get_current_sprite_key(self):
        """Get the sprite key for the player's current direction."""
        return f"player_{self.char_class}_{self.direction}"

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
        self.name = "Merchant"
        self.icon = "🧙‍♂️"  # Wizard emoji for shopkeeper
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
            self.enemies.append(Enemy(boss_x, boss_y, "dragon", self.level))

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
        if self.level == 1:
            # Level 1: Mostly goblins (80%), some orcs (20%)
            return random.choices(
                ['goblin', 'orc'],
                weights=[80, 20]
            )[0]
        elif self.level == 2:
            # Level 2: More balanced, goblins (60%), orcs (35%), few trolls (5%)
            return random.choices(
                ['goblin', 'orc', 'troll'],
                weights=[60, 35, 5]
            )[0]
        elif self.level == 3:
            # Level 3: Fewer goblins (30%), more orcs (50%), more trolls (20%)
            return random.choices(
                ['goblin', 'orc', 'troll'],
                weights=[30, 50, 20]
            )[0]
        elif self.level == 4:
            # Level 4: Rare goblins (15%), orcs (45%), trolls (40%)
            return random.choices(
                ['goblin', 'orc', 'troll'],
                weights=[15, 45, 40]
            )[0]
        else:
            # Level 5+: Boss level - orcs (30%), trolls (70%), dragons handled separately
            return random.choices(
                ['orc', 'troll'],
                weights=[30, 70]
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
                if enemy_type == "goblin":
                    enemy.weapon_drops = [WARRIOR_WEAPONS[0], ARCHER_WEAPONS[0]]
                elif enemy_type == "orc":
                    enemy.weapon_drops = WARRIOR_WEAPONS[1:3] + ARCHER_WEAPONS[1:2]
                elif enemy_type == "troll":
                    enemy.weapon_drops = WARRIOR_WEAPONS[3:5] + ALL_ARMOR[2:5]
                elif enemy_type == "dragon":
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
                if enemy_type == "goblin":
                    enemy.weapon_drops = [WARRIOR_WEAPONS[0], ARCHER_WEAPONS[0]]  # Basic weapons
                elif enemy_type == "orc":
                    enemy.weapon_drops = WARRIOR_WEAPONS[1:3] + ARCHER_WEAPONS[1:2]  # Intermediate weapons
                elif enemy_type == "troll":
                    enemy.weapon_drops = WARRIOR_WEAPONS[3:5] + ALL_ARMOR[2:5]  # Advanced weapons and armor
                elif enemy_type == "dragon":
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
            
            # Player name and class with icons
            if game_settings['use_emojis']:
                status = f'{player.icon} {player.name} (Lv.{player.level})'
            else:
                # Draw player portrait instead of small sprite
                draw_portrait(screen, player, player_section_x, y_pos, size=64, 
                            border_color=ENHANCED_COLORS['accent_gold'] if is_current else WHITE)
                status = f'{player.name} (Lv.{player.level}, {player.char_class.title()})'
            
            text_color = ENHANCED_COLORS['accent_gold'] if is_current else ENHANCED_COLORS['text_primary']
            draw_text_with_shadow(screen, status, player_section_x + 80, y_pos, text_color)
            
            # Enhanced health bar
            hp_bar_y = y_pos + 30
            draw_health_bar_fancy(screen, player_section_x + 80, hp_bar_y, 200, 25, 
                                player.hp, player.max_hp)
            
            # Mana bar for mages
            if player.char_class == "mage":
                mana_bar_y = y_pos + 60
                mana_percentage = player.mana / player.max_mana if player.max_mana > 0 else 0
                
                # Mana bar background
                mana_bg_rect = pygame.Rect(player_section_x + 80, mana_bar_y, 200, 20)
                pygame.draw.rect(screen, DARK_GRAY, mana_bg_rect)
                
                # Mana bar fill with gradient
                if mana_percentage > 0:
                    mana_width = int(200 * mana_percentage)
                    mana_rect = pygame.Rect(player_section_x + 80, mana_bar_y, mana_width, 20)
                    draw_gradient_rect(screen, mana_rect, BLUE, (0, 150, 255), vertical=False)
                
                pygame.draw.rect(screen, WHITE, mana_bg_rect, width=2)
                
                # Mana text
                mana_text = f"Mana: {player.mana}/{player.max_mana}"
                mana_surface = small_font.render(mana_text, True, ENHANCED_COLORS['text_primary'])
                mana_text_rect = mana_surface.get_rect(center=(player_section_x + 180, mana_bar_y + 10))
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
            
            # Enemy sprite and name
            if game_settings['use_emojis']:
                status = f'{enemy.icon} {enemy.name} (Lv.{self.dungeon_level})'
            else:
                # Draw enemy portrait
                draw_portrait(screen, enemy, enemy_section_x, y_pos, size=64, 
                            border_color=ENHANCED_COLORS['danger_red'] if is_current else WHITE)
                status = f'{enemy.name} (Level {self.dungeon_level})'
            
            text_color = ENHANCED_COLORS['danger_red'] if is_current else ENHANCED_COLORS['text_primary']
            draw_text_with_shadow(screen, status, enemy_section_x + 80, y_pos, text_color)
            
            # Enhanced enemy health bar
            hp_bar_y = y_pos + 30
            draw_health_bar_fancy(screen, enemy_section_x + 80, hp_bar_y, 200, 25, 
                                enemy.hp, enemy.max_hp, bar_color=RED)
            
            # Enemy stats display
            stats_text = f"ATK: {enemy.attack} | DEF: {enemy.defense}"
            stats_surface = small_font.render(stats_text, True, ENHANCED_COLORS['text_secondary'])
            screen.blit(stats_surface, (enemy_section_x + 80, y_pos + 60))

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
            
            # Player character portrait in tab
            if not game_settings['use_emojis']:
                # Draw smaller portrait for tab
                draw_portrait(screen, player, tab_x + 10, tab_y + 10, size=32, 
                            border_color=ENHANCED_COLORS['accent_gold'] if is_selected else WHITE, 
                            border_width=2)
            
            # Player info
            player_text = f"{player.icon if game_settings['use_emojis'] else ''} {player.name}"
            class_text = f"Lv.{player.level} {player.char_class.title()}"
            
            text_start_x = tab_x + (50 if not game_settings['use_emojis'] else 20)
            draw_text_with_shadow(screen, player_text, text_start_x, tab_y + 8, text_color, font, 1)
            draw_text_with_shadow(screen, class_text, text_start_x, tab_y + 28, text_color, small_font, 1)
        
        # Current player's inventory panel
        current_player = self.players[self.selected_player_idx]
        inventory_panel_rect = pygame.Rect(100, 400, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 450)
        draw_gradient_rect(screen, inventory_panel_rect, ENHANCED_COLORS['panel_dark'], ENHANCED_COLORS['panel_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['accent_blue'], inventory_panel_rect, width=3, border_radius=10)
        
        # Player detailed stats panel
        stats_panel_rect = pygame.Rect(120, 420, 380, 120)
        draw_gradient_rect(screen, stats_panel_rect, ENHANCED_COLORS['primary_dark'], ENHANCED_COLORS['primary_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['success_green'], stats_panel_rect, width=2, border_radius=6)
        
        # Draw player portrait in stats panel
        if not game_settings['use_emojis']:
            draw_portrait(screen, current_player, 130, 430, size=80, 
                        border_color=ENHANCED_COLORS['accent_gold'], border_width=3)
            text_start_x = 220
        else:
            text_start_x = 140
        
        draw_text_with_shadow(screen, f"{current_player.name}", text_start_x, 435, 
                            ENHANCED_COLORS['accent_gold'], font, 1)
        draw_text_with_shadow(screen, f"Level {current_player.level} {current_player.char_class.title()}", 
                            text_start_x, 460, ENHANCED_COLORS['text_primary'], small_font, 1)
        draw_text_with_shadow(screen, f"HP: {current_player.hp}/{current_player.max_hp}", 
                            text_start_x, 480, GREEN if current_player.hp == current_player.max_hp else RED, small_font, 1)
        draw_text_with_shadow(screen, f"ATK: {current_player.attack} | DEF: {current_player.defense}", 
                            text_start_x, 500, ENHANCED_COLORS['text_secondary'], small_font, 1)
        
        # Gold display
        draw_text_with_shadow(screen, f"💰 Gold: {current_player.gold}", 
                            text_start_x, 520, ENHANCED_COLORS['accent_gold'], small_font, 1)
        
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
        player_panel_rect = pygame.Rect(500, 200, 380, 150)
        draw_gradient_rect(screen, player_panel_rect, ENHANCED_COLORS['primary_dark'], ENHANCED_COLORS['primary_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['success_green'], player_panel_rect, width=2, border_radius=6)
        
        # Draw player portrait in shop
        if not game_settings['use_emojis']:
            draw_portrait(screen, current_player, 510, 210, size=80, 
                        border_color=ENHANCED_COLORS['success_green'], border_width=3)
            text_start_x = 600
        else:
            text_start_x = 520
        
        draw_text_with_shadow(screen, f"{current_player.name}", text_start_x, 215, 
                            ENHANCED_COLORS['accent_gold'], font, 1)
        draw_text_with_shadow(screen, f"Level {current_player.level} {current_player.char_class.title()}", 
                            text_start_x, 240, ENHANCED_COLORS['text_primary'], small_font, 1)
        draw_text_with_shadow(screen, f"Gold: {current_player.gold}", text_start_x, 265, 
                            (255, 215, 0), font, 1)  # Gold color for gold amount
        draw_text_with_shadow(screen, f"HP: {current_player.hp}/{current_player.max_hp}", 
                            text_start_x, 290, GREEN if current_player.hp == current_player.max_hp else RED, small_font, 1)
        
        # Shopkeeper info panel
        shopkeeper_panel_rect = pygame.Rect(900, 200, 300, 150)
        draw_gradient_rect(screen, shopkeeper_panel_rect, ENHANCED_COLORS['secondary_dark'], ENHANCED_COLORS['secondary_light'])
        pygame.draw.rect(screen, ENHANCED_COLORS['accent_blue'], shopkeeper_panel_rect, width=2, border_radius=6)
        
        # Draw shopkeeper portrait
        if not game_settings['use_emojis'] and self.current_shopkeeper:
            draw_portrait(screen, self.current_shopkeeper, 910, 210, size=80, 
                        border_color=ENHANCED_COLORS['accent_blue'], border_width=3)
            shop_text_start_x = 1000
        else:
            shop_text_start_x = 920
        
        if self.current_shopkeeper:
            draw_text_with_shadow(screen, f"{self.current_shopkeeper.name}", shop_text_start_x, 215, 
                                ENHANCED_COLORS['accent_blue'], font, 1)
            draw_text_with_shadow(screen, "Merchant", shop_text_start_x, 240, 
                                ENHANCED_COLORS['text_primary'], small_font, 1)
            draw_text_with_shadow(screen, f"Items: {len(self.current_shopkeeper.inventory)}", 
                                shop_text_start_x, 265, ENHANCED_COLORS['text_secondary'], small_font, 1)
        
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
            
            # Switch to the appropriate tileset for the loaded dungeon level
            set_dungeon_level_tileset(self.dungeon_level)
            
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

    def draw_text(self, text, x, y, color=WHITE):
        text_surface = font.render(text, True, color)
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
        version_text = "Version 1.17 - Enhanced Balance Edition"
        
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
        
        # Switch to the appropriate tileset for this dungeon level
        set_dungeon_level_tileset(self.dungeon_level)
        
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
        if direction == 'w': dy = -1
        if direction == 's': dy = 1
        if direction == 'a': dx = -1
        if direction == 'd': dx = 1

        # Update player direction based on movement
        player.update_direction(dx, dy)

        new_x, new_y = player.x + dx, player.y + dy

        if not (0 <= new_x < self.dungeon.width and 0 <= new_y < self.dungeon.height):
            self.add_message("You can't move off the map.")
            play_sound("error", 0.3)
            return

        if self.dungeon.grid[new_y][new_x] == UI["stairs"]:
            # Add particle effect for stairs
            screen_x = (new_x - self.camera_x) * TILE_SIZE + TILE_SIZE // 2
            screen_y = (new_y - self.camera_y) * TILE_SIZE + TILE_SIZE // 2
            animation_manager.add_particles(screen_x, screen_y, ENHANCED_COLORS['accent_gold'], 20)
            
            self.dungeon_level += 1
            # Switch to the new level's tileset
            set_dungeon_level_tileset(self.dungeon_level)
            self.new_level()
            play_sound("door_open", 0.8)
            return

        if self.dungeon.grid[new_y][new_x] == UI["floor"]:
            enemies_in_pos = [e for e in self.dungeon.enemies if e.x == new_x and e.y == new_y]
            if enemies_in_pos:
                # Add combat particles
                screen_x = (new_x - self.camera_x) * TILE_SIZE + TILE_SIZE // 2
                screen_y = (new_y - self.camera_y) * TILE_SIZE + TILE_SIZE // 2
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
                            screen_x = (new_x - self.camera_x) * TILE_SIZE + TILE_SIZE // 2
                            screen_y = (new_y - self.camera_y) * TILE_SIZE + TILE_SIZE // 2
                            
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
    
    def get_corner_type(self, x, y):
        """Detect if a floor tile should use a corner piece to create rounded room corners."""
        if not self.dungeon:
            return None
        
        # Check if this is a floor tile - we want to put corners on floor tiles, not walls
        if self.dungeon.grid[y][x] != UI["floor"]:
            return None
        
        # Get adjacent tiles (up, down, left, right)
        up = self.get_tile_at(x, y-1)
        down = self.get_tile_at(x, y+1) 
        left = self.get_tile_at(x-1, y)
        right = self.get_tile_at(x+1, y)
        
        # Detect room corners - where floor meets walls in corner patterns
        # These create the curved/rounded appearance in room corners
        
        # Top-left room corner: walls above and left, floor elsewhere
        if (up == UI["wall"] and left == UI["wall"] and 
            down == UI["floor"] and right == UI["floor"]):
            return "inner_top_left"
        
        # Top-right room corner: walls above and right, floor elsewhere  
        if (up == UI["wall"] and right == UI["wall"] and 
            down == UI["floor"] and left == UI["floor"]):
            return "inner_top_right"
        
        # Bottom-left room corner: walls below and left, floor elsewhere
        if (down == UI["wall"] and left == UI["wall"] and 
            up == UI["floor"] and right == UI["floor"]):
            return "inner_bottom_left"
        
        # Bottom-right room corner: walls below and right, floor elsewhere
        if (down == UI["wall"] and right == UI["wall"] and 
            up == UI["floor"] and left == UI["floor"]):
            return "inner_bottom_right"
        
        return None
    
    def get_tile_at(self, x, y):
        """Safely get the tile type at a position, returning wall for out-of-bounds."""
        if (x < 0 or y < 0 or x >= self.dungeon.width or y >= self.dungeon.height):
            return UI["wall"]  # Treat out-of-bounds as walls
        return self.dungeon.grid[y][x]

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
                            # Check if this wall position is a corner and use corner tile if available
                            corner_type = self.get_corner_type(world_x, world_y)
                            corner_sprite_used = False
                            
                            if corner_type:
                                # Try the full corner type first (e.g., "inner_top_left")
                                corner_sprite_key = f"corner_{corner_type}"
                                if corner_sprite_key in sprites:
                                    sprite = sprites[corner_sprite_key].copy()
                                    if not is_visible:
                                        sprite.set_alpha(128)
                                    screen.blit(sprite, (screen_x, screen_y))
                                    corner_sprite_used = True
                                    sprite_drawn = True
                                    # Debug: show corner usage in first room area  
                                    if world_x < 15 and world_y < 15:
                                        print(f"DEBUG: Corner {corner_type} at ({world_x}, {world_y}) on level {current_level}")
                                else:
                                    # Fallback: try simplified corner type (e.g., "top_left")
                                    simplified_type = corner_type.replace("inner_", "").replace("outer_", "")
                                    fallback_key = f"corner_{simplified_type}"
                                    if fallback_key in sprites:
                                        sprite = sprites[fallback_key].copy()
                                        if not is_visible:
                                            sprite.set_alpha(128)
                                        screen.blit(sprite, (screen_x, screen_y))
                                        corner_sprite_used = True
                                        sprite_drawn = True
                                        # Debug: show fallback corner usage
                                        if world_x < 15 and world_y < 15:
                                            print(f"DEBUG: Using fallback corner {simplified_type} at ({world_x}, {world_y})")
                            
                            # If no corner sprite was used, draw regular wall
                            if not corner_sprite_used:
                                sprite_key = f"wall_{game_settings['wall_sprite']}"
                                if sprite_key in sprites:
                                    sprite = sprites[sprite_key].copy()
                                    if not is_visible:
                                        sprite.set_alpha(128)
                                    screen.blit(sprite, (screen_x, screen_y))
                                    sprite_drawn = True
                        elif tile_type == UI["floor"]:
                            # Check if this floor position is a corner and use corner tile if available
                            corner_type = self.get_corner_type(world_x, world_y)
                            corner_sprite_used = False
                            
                            if corner_type:
                                # Try to get corner from current level's tileset
                                if ("level_sprites" in sprites and 
                                    self.dungeon_level in sprites["level_sprites"] and
                                    "corners" in sprites["level_sprites"][self.dungeon_level] and
                                    corner_type in sprites["level_sprites"][self.dungeon_level]["corners"]):
                                    
                                    corner_tile = sprites["level_sprites"][self.dungeon_level]["corners"][corner_type]
                                    sprite = corner_tile.copy()
                                    if not is_visible:
                                        sprite.set_alpha(128)
                                    screen.blit(sprite, (screen_x, screen_y))
                                    corner_sprite_used = True
                                    sprite_drawn = True
                            
                            # If no corner sprite was used, draw regular floor
                            if not corner_sprite_used:
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
                
        # Draw shopkeepers (only if visible)
        for shopkeeper in self.dungeon.shopkeepers:
            if (viewport_start_x <= shopkeeper.x < viewport_end_x and 
                viewport_start_y <= shopkeeper.y < viewport_end_y and
                self.dungeon.is_visible(shopkeeper.x, shopkeeper.y)):
                
                screen_x = (shopkeeper.x - self.camera_x) * TILE_SIZE
                screen_y = (shopkeeper.y - self.camera_y) * TILE_SIZE
                
                if game_settings['use_emojis']:
                    text = font.render(shopkeeper.icon, True, (255, 215, 0))  # Gold color
                    screen.blit(text, (screen_x, screen_y))
                else:
                    # Use Undertale shopkeeper sprite
                    sprite_key = "shopkeeper_npc"
                    if sprite_key in sprites:
                        screen.blit(sprites[sprite_key], (screen_x, screen_y))
                    else:
                        # Fallback: Gold-colored rectangle for merchant
                        pygame.draw.rect(screen, (255, 215, 0), (screen_x + 4, screen_y + 4, TILE_SIZE - 8, TILE_SIZE - 8))

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
                    # Use directional sprites
                    sprite_drawn = False
                    
                    # Try to use directional sprite first
                    directional_sprite_key = player.get_current_sprite_key()
                    if directional_sprite_key in sprites:
                        screen.blit(sprites[directional_sprite_key], (screen_x, screen_y))
                        sprite_drawn = True
                    else:
                        # Fallback to static sprite
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
        
        # Draw particle effects on top of everything
        animation_manager.draw_particles(screen)
        
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
