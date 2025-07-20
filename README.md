# Python RPG Adventure - Pygame Version

This file documents the development of a graphical RPG created with Pygame, with the help of a large language model. It tracks the game's evolution through different versions, detailing the features added at each stage and the prompts used to generate them.

This version was started by user **LukesScammell**.

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
    *   **Combat:** When you move into an enemy, combat begins. On a hero's turn, use the number keys:
        *   **(1) Attack:** Perform a basic attack on a random enemy.
        *   **(2) Skill:** Use your class's unique, more powerful skill.
    *   **Descending:** Find the stairs (a down arrow) to proceed to the next, more difficult dungeon level.
    *   **Winning:** Defeat the final boss (a dragon) on the last level to win the game.

4.  **(Optional) Sound:**
    *   For sound effects and music, create a folder named `assets` in the same directory as the game.
    *   Place the following sound files inside it: `music.ogg`, `sword.wav`, `magic.wav`, `arrow.wav`, `damage.wav`.

## Features

*   **Visual Modes:** Toggle between emoji-based graphics and detailed pixel art sprites
*   **Customizable Appearance:** Choose from multiple wall and floor styles with visual previews
*   **Persistent Settings:** All preferences are automatically saved and restored
*   **Multi-Character Parties:** Create up to 3 heroes with different classes
*   **Turn-Based Combat:** Strategic combat system with unique class abilities
*   **Progressive Difficulty:** Multiple dungeon levels with increasing challenge
*   **Asset Integration:** Uses professional dungeon crawler sprite assets

## Settings Guide

The game includes a comprehensive settings system accessible from the main menu:

*   **Press S** from the main menu to access settings
*   **Emoji Toggle:** Switch between emoji characters and sprite graphics
*   **Wall Selection:** Choose from Stone Brick, Stone Dark, Brick Brown, or Marble Wall styles
*   **Floor Selection:** Choose from Sandstone, Dirt, Pebble Brown, or Marble Floor styles
*   **Visual Previews:** See actual sprite images when selecting wall and floor styles
*   **Real-time Updates:** Changes take effect immediately in the game

## Version History

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
