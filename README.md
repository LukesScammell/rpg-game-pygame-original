# Python RPG Adventure - Pygame Version (v1.13)

This file documents the development of a graphical RPG created with Pygame, with the help of a large language model. It tracks the game's evolution through different versions, detailing the features added at each stage and the prompts used to generate them.

This version was started by user **LukesScammell**.

## Version 1.13 Features

**Clean Classic Interface Restoration:**
- Removed all Undertale UI elements and sprites for a clean, traditional RPG look
- Maintains enhanced turn-based combat system with health bars and status indicators
- Keeps comprehensive inventory management system
- Uses original dungeon crawler sprites with simple UI elements
- Streamlined codebase without animation complexity

**Enhanced Combat System:**
- Turn-based combat with clear visual indicators
- Player and enemy health bars with real-time updates
- Skill cooldown tracking and mana management for mages
- Simple button interface with availability indicators
- Combat message system for battle feedback

**Complete Inventory System:**
- Press **I** to access inventory management
- Multi-character inventory tabs with navigation (← →)
- Item interaction: Use/Equip with Enter, Drop with X
- Equipment system with attack/defense bonuses
- Visual indicators for equipped items

## How to Play

1.  **Installation:**
    *   Make sure you have Python installed.
    *   Install the Pygame library by opening a terminal (like in VS Code) and running: `pip install pygame` or `py -m pip install pygame`

2.  **Running the Game:**
    *   Navigate to the game's directory in your terminal.
    *   Run the script using: `python rpg_pygame.py` or `py rpg_pygame.py`

3.  **Gameplay:**
    *   **Character Creation:** Follow the on-screen prompts to choose the number of heroes, their names, and their classes (Warrior, Mage, Archer).
    *   **Settings:** Press **S** in the main menu to access settings:
        *   Toggle between emoji and sprite display modes
        *   Select different wall styles (Stone Brick, Stone Dark, Brick Brown, Marble Wall)
        *   Select different floor styles (Sandstone, Dirt, Pebble Brown, Marble Floor)
    *   **Exploration:** Use the **W, A, S, D** keys to move your party through the dungeon.
    *   **Inventory:** Press **I** to access the inventory system:
        *   Use arrow keys (← → ↑ ↓) to navigate between players and items
        *   Press **Enter** to use/equip items
        *   Press **X** to drop items
        *   Press **I** or **ESC** to close inventory
    *   **Combat:** When you move into an enemy, enhanced turn-based combat begins. On a hero's turn, use the number keys:
        *   **(1) Attack:** Perform a basic attack on a random enemy.
        *   **(2) Skill:** Use your class's unique, more powerful skill.
        *   **(3) Item:** Use a potion from your inventory to heal.
        *   **(4) Flee:** Attempt to escape from combat.
    *   **Descending:** Find the stairs (a door sprite or stairs emoji) to proceed to the next, more difficult dungeon level.
    *   **Winning:** Defeat the final boss (a dragon) on the last level to win the game.

4.  **(Optional) Sound:**
    *   For sound effects and music, create a folder named `assets` in the same directory as the game.
    *   Place the following sound files inside it: `music.ogg`, `sword.wav`, `magic.wav`, `arrow.wav`, `damage.wav`.

## Features

*   **Clean Traditional Interface:** Simple, uncluttered UI focusing on gameplay
*   **Visual Modes:** Toggle between emoji-based graphics and detailed pixel art sprites
*   **Customizable Appearance:** Choose from multiple wall and floor styles with visual previews
*   **Persistent Settings:** All preferences are automatically saved and restored
*   **Multi-Character Parties:** Create up to 3 heroes with different classes
*   **Enhanced Turn-Based Combat:** Strategic combat with health bars, status indicators, and visual feedback
*   **Complete Inventory System:** Full item management with use/equip/drop functionality
*   **Progressive Difficulty:** Multiple dungeon levels with increasing challenge
*   **Asset Integration:** Uses professional dungeon crawler sprite assets from Crawl tiles

## Settings Guide

The game includes a comprehensive settings system accessible from the main menu:

*   **Press S** from the main menu to access settings
*   **Emoji Toggle:** Switch between emoji characters and sprite graphics
*   **Wall Selection:** Choose from Stone Brick, Stone Dark, Brick Brown, or Marble Wall styles
*   **Floor Selection:** Choose from Sandstone, Dirt, Pebble Brown, or Marble Floor styles
*   **Visual Previews:** See actual sprite images when selecting wall and floor styles
*   **Real-time Updates:** Changes take effect immediately in the game

## Version History

### v1.12: Classic Combat with Enhanced UI & Full Inventory System
**Major Features:**
- **Enhanced Turn-Based Combat**: Restored classic RPG mechanics with modern Undertale-inspired UI
  - ATTACK/SKILL/ITEM/FLEE buttons using extracted Undertale Battle Menu sprites
  - Visual health bars and status indicators for all combatants
  - Turn-based system with cooldown management and skill availability indicators
  - Professional battle interface with dark theme and highlighted current turn
- **Complete Inventory Management System**: Full-featured inventory with multiple interaction modes
  - Press **I** to open/close inventory during exploration
  - Multi-player inventory tabs with individual character management
  - Use items (potions heal instantly if not at full health)
  - Equip weapons and armor with automatic stat bonuses
  - Drop unwanted items back into the dungeon
  - Visual indicators for equipped items and item effects
- **Enhanced UI Integration**: Seamless blend of modern and classic RPG elements
  - Battle buttons extracted from Undertale Battle Menu sprite sheet
  - Inventory screen with player tabs and item categorization
  - Equipment status and character stats display
  - Professional visual feedback for all interactions
- **Quality of Life Improvements**: Better gameplay experience and information display
  - Control hints shown during gameplay (WASD=Move, I=Inventory)
  - Item descriptions showing stat bonuses and effects
  - Cannot drop equipped items protection
  - Automatic inventory index adjustment when items are used/dropped

**User Request**: "could you make it go back to the old fighting mechanics but use the ui still but for the right buttons and could you implement the inventory system"

**Technical Implementation**: 
- Restored traditional turn-based combat with enhanced visual presentation
- Added comprehensive inventory system with use/equip/drop functionality
- Created inventory screen with player tabs and item management
- Enhanced combat UI using extracted Undertale Battle Menu elements
- Added input handling for inventory navigation and item interaction

### v1.11: Enhanced Battle System & Full Screen Experience
**Major Features:**
- **Undertale-Style Battle System**: Complete reimplementation of combat using Undertale's iconic battle interface
  - Bullet hell attack phases with dodge mechanics
  - FIGHT/ACT/ITEM/MERCY button system extracted from Battle Menu sprite
  - Soul heart movement during enemy attacks  
  - Typewriter text effects for battle dialogue
  - Professional battle UI using PC Computer - Undertale - Battle Menu.png asset
- **Full Screen Gaming**: Increased display resolution for immersive experience
  - Screen resolution expanded to 1920x1080 for modern displays
  - Larger tile size (48px) for enhanced sprite visibility
  - Extended viewport (20x15 tiles) showing more of the dungeon
  - Enlarged minimap (250px) for better navigation
- **Enhanced Sprite System**: Improved visual rendering across all game elements
  - Battle UI elements automatically extracted from Undertale sprite sheet
  - Scaled interface elements for proper full-screen presentation
  - Maintained compatibility with existing sprite and emoji systems
- **Technical Improvements**: Updated game architecture for better performance
  - Delta time-based animations for smooth 60 FPS gameplay
  - Optimized battle state management and event handling
  - Enhanced camera system for larger viewport coverage

**User Request**: "could you use for the combat part the undertale battle ui and could you make the game take up more of the screen"

**Technical Implementation**: 
- Added UndertaleBattle class handling FIGHT/ACT/ITEM/MERCY mechanics
- Implemented bullet hell attack system with collision detection
- Created UISpriteCutter for extracting battle elements from sprite sheets
- Updated Game class to use new battle system with proper state management
- Enhanced resolution and tile sizing for optimal visual experience

### v1.10: Professional UI Sprite System

*   **Prompt:** "could you select the different parts of the ui sheet the has the different actions and make it so the sprite isnt just a box with the whole ui sheet"
*   **Changes:**
    *   **UI Sprite Extraction System:** Implemented UISpriteCutter class for cutting specific elements from UI sprite sheets
    *   **Button Sprite Integration:** Combat menu now uses proper UI button sprites instead of plain text
    *   **Settings Menu Enhancement:** Settings options now display with appropriate UI button backgrounds
    *   **Dynamic Button States:** Buttons show different sprites based on state (normal, selected, disabled, hover)
    *   **Custom UI Sheet Support:** Added system to load and cut custom UI sprite sheets with defined button positions
    *   **GUI Element Loading:** Integrated crawl-tiles GUI elements (tabs, buttons, labels)
    *   **Smart Button Function:** Created create_ui_button() function for consistent UI element rendering
    *   **Flexible Sprite Cutting:** Support for extracting any rectangular region from UI sprite sheets
    *   **State-Based Visual Feedback:** Disabled skills show grayed out buttons, available skills show highlighted buttons
    *   **Modular UI System:** Easy to extend with new UI elements and sprite sheets

### v1.9: Animated Player Sprites and Movement System

*   **Prompt:** "i just added a new png file which is a sprite sheet could you implement moving animations and change the player to have the character in this sprite sheet and also cut it out"
*   **Changes:**
    *   **Sprite Sheet Animation System:** Implemented a complete animation framework for handling sprite sheets
    *   **Character Animation:** Added SpriteAnimation class with frame extraction, timing, and direction handling
    *   **Frisk Character Integration:** Integrated the Undertale Frisk sprite sheet as the new player character
    *   **Directional Movement:** Players now face the correct direction when moving (up, down, left, right)
    *   **Walking Animation:** Smooth walking animations that cycle through frames when moving
    *   **Smart Frame Extraction:** Automatic sprite sheet cutting with support for various layouts and dimensions
    *   **Animation Timing:** Proper frame timing system running at 60 FPS with smooth transitions
    *   **Fallback System:** Maintains compatibility with static sprites if animations fail
    *   **Movement State Tracking:** Players remember their last direction and movement state for proper animation
    *   **Idle Animation:** Characters return to idle pose when not moving

### v1.8: Fog of War and Camera System

*   **Prompt:** "could you make it so the camera is more closer so it only shows the room the person is in becuase i dont want people to know the whole map and also implement a system which makes it so you have to discover and it will reveal the rest of the dungeon on a little screen at the top anything that the player cant see will have less light"
*   **Changes:**
    *   **Camera System:** Implemented a dynamic camera that follows the player, showing only a limited viewport (15x12 tiles)
    *   **Fog of War:** Added exploration system where players must discover the dungeon by moving around
    *   **Room-Based Visibility:** When entering a room, the entire room becomes visible and explored
    *   **Corridor Vision:** Small radius visibility (2 tiles) for navigating corridors between rooms
    *   **Minimap:** Added a minimap in the top-right corner showing the overall layout of explored areas
    *   **Visual Dimming:** Explored but not currently visible areas appear dimmed/darker
    *   **Unexplored Areas:** Areas not yet visited are shown as dark fog
    *   **Enhanced Immersion:** Players can only see enemies and items when they're in visible areas
    *   **Strategic Exploration:** Encourages careful movement and room-by-room exploration

### v1.7.2: Enhanced Sprite Support and Visual Improvements

*   **Prompt:** "could you add that to my read me and also, could you bring back the player and enemy and item ui"
*   **Changes:**
    *   **Complete Sprite System:** Successfully implemented comprehensive sprite support for all game elements
    *   **Character Sprites:** Added dedicated sprites from Crawl tiles for different character classes:
        *   Warrior (human male), Mage (human female), Archer (elf male), Rogue (elf female)
    *   **Enemy Sprites:** Integrated visual sprites for all enemy types including goblin, orc, troll, and dragon
    *   **Item Sprites:** Added proper sprite representations for potions (healing wounds), weapons (long sword), and armor (animal skin)
    *   **Asset Integration:** Successfully loaded 20 sprites from the crawl-tiles asset pack
    *   **Visual Consistency:** Complete sprite mode functionality with fallback to colored rectangles when needed
    *   **Fixed Sprite Paths:** Corrected all sprite file paths to match the actual asset folder structure
    *   **Performance:** Efficient sprite loading with proper error handling and status reporting

### v1.7.1: UI Improvements and Bug Fixes

*   **Prompt:** "could you add what i updated to my readme and make it so there isnt any overlap of text and hide it if its not being used and could you make in the combat part ui put in good places"
*   **Changes:**
    *   **Fixed Text Overlap:** Eliminated all text overlap issues throughout the game interface
    *   **Enhanced Combat UI:** Completely redesigned combat screen with:
        *   Clear party and enemy sections with proper spacing
        *   Turn indicator highlighting (yellow glow for current entity)
        *   Dynamic skill descriptions with cooldown and mana status
        *   Semi-transparent background panels for better readability
        *   Organized combat messages and action feedback
    *   **Improved Settings Interface:** 
        *   Settings now hide sprite options when emoji mode is enabled
        *   Better visual organization with larger sprite previews
        *   Conditional display of relevant options based on current mode
    *   **Enhanced Character Setup:**
        *   Added detailed class descriptions during character creation
        *   Visual input indicators and better spacing
        *   Name length limits and improved text input handling
    *   **Better Main Game UI:**
        *   Semi-transparent backgrounds for status bars and messages
        *   Improved player status display with conditional icons/text
        *   Separate mana display for mage characters
        *   Limited message history to prevent screen clutter
    *   **Quality of Life Improvements:**
        *   Current display mode shown on main menu
        *   Skill cooldowns now properly decrease each turn
        *   Enhanced game over screen with player statistics
        *   Consistent spacing and layout across all screens
    *   **User Settings Update:** Default changed from emoji to sprite mode for better visual experience

### v1.7: Settings System and Sprite Integration

*   **Prompt:** "could you make it so that you can toggle the emojis in the settings and also imnplement the sprites in the assests folder to be used for the map and select specific pcitures for the walls and floor"
*   **Changes:**
    *   Added a comprehensive settings system with persistent storage to `rpg_settings.json`
    *   Implemented emoji toggle functionality - players can now switch between emoji and sprite display modes
    *   Integrated dungeon crawler sprites from the assets folder for walls, floors, and stairs
    *   Added visual selection menus for wall styles: Stone Brick, Stone Dark, Brick Brown, and Marble Wall
    *   Added visual selection menus for floor styles: Sandstone, Dirt, Pebble Brown, and Marble Floor  
    *   Enhanced main menu with settings access (press 'S')
    *   Improved tile rendering system to support both emoji and sprite modes
    *   Increased tile size to 32x32 pixels for better sprite visibility
    *   All settings are automatically saved and restored between game sessions

### v1.6.1: Emoji Font Fix

*   **Prompt:** "it runs now, could you make a seperate readme file for the pygame version showing how to play and the versions if i update it with the prompts i gave you to make the feature and also the ui emojis arnt showing right in the pygame"
*   **Changes:**
    *   Updated the Pygame font handling to use "Segoe UI Emoji" to correctly display emoji icons on Windows.
    *   Added a fallback to the default font to prevent crashes if the specified font is not found.

### v1.6: Pygame GUI Implementation (by user)

*   **Prompt:** "can i run the game yet or is there anything i need to add and could you add to the readme all of the new versions that got added and explain that i made the pygame version"
*   **Changes:**
    *   The user, LukesScammell, initiated the creation of a new version of the RPG with a graphical user interface using the Pygame library.
    *   The initial `rpg_pygame.py` file was created, laying the foundation for the GUI.
    *   The emoji-based UI from the command-line version was carried over as a placeholder.

### v1.13: Classic Interface Restoration

*   **Prompt:** "could you make it so it doesnt use any of the undetale ui and sprites and go back to what i had before but keep the combat system and inventory look"
*   **Changes:**
    *   Complete removal of all Undertale UI elements and sprite dependencies
    *   Eliminated Frisk animation system and UISpriteCutter class for streamlined code
    *   Restored clean, traditional RPG interface while maintaining enhanced combat system
    *   Kept comprehensive inventory management with all functionality intact
    *   Simplified player rendering to use static sprites from original dungeon crawler assets
    *   Maintained turn-based combat enhancements: health bars, status indicators, and visual feedback
    *   Preserved all inventory features: multi-character tabs, item interactions, equipment system
    *   Updated combat interface to use simple geometric buttons instead of Undertale-style elements
    *   Reduced code complexity by removing animation systems while keeping core gameplay improvements
    *   Game now loads with original 20 sprites and 6 UI elements from crawl-tiles collection only

### v1.12: Classic Combat + Comprehensive Inventory (Previous Version)

*   **Prompt:** "could you make it go back to the old fighting mechanics but use the ui still but for the right buttons and could you implement the inventory system"
*   **Changes:**
    *   Reverted from Undertale bullet-hell combat back to classic turn-based mechanics
    *   Maintained Undertale UI aesthetics for battle interface styling
    *   Implemented complete inventory management system with multi-character support
    *   Added inventory access with 'I' key, navigation with arrow keys
    *   Full item interaction system: use/equip with Enter, drop with X
    *   Equipment system with attack/defense bonuses displayed
    *   Enhanced combat screen showing player/enemy health bars and turn indicators
    *   Four combat options: Attack, Skill, Item, and Flee with availability checking
    *   Inventory tabs for each player with visual equipment status
    *   Real-time stat updates when equipping weapons and armor
