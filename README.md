# Python RPG Adventure - Pygame Version (v1.20)

A modern graphical RPG adventure game built with Pygame, featuring enhanced visuals, strategic combat, immersive dungeon exploration, and shop system. Created with the help of large language models by **LukesScammell**.

## Features

*   **Enhanced Visual Experience:** Modern UI with advanced visual effects and professional design
    *   **Comprehensive Visual Overhaul:** Professional color palette, gradient backgrounds, and shadow text rendering
    *   **Advanced Animation System:** Particle effects, smooth transitions, and coordinated visual timing
    *   **Enhanced Combat Interface:** Fixed UI overlapping issues, professional health/mana bars with gradients
    *   **Enhanced Inventory System:** Visual item sprites displayed alongside text, categorized display, rarity color coding, and interactive feedback
*   **Dynamic Shop System:** Trade with merchant NPCs for weapons, armor, and potions
    *   **Shop Rooms:** Merchant rooms (15% spawn chance) with peaceful trading environments
    *   **Buy & Sell Interface:** Professional shop UI with separate buy/sell modes and item pricing
    *   **Gold Economy:** Complete currency system with starting gold and item-based pricing
    *   **Smart Pricing:** Dynamic pricing based on item rarity and type with 50% sell-back value
*   **Dynamic Audio System:** Context-aware background music with 6+ tracks and 26+ professional sound effects
*   **Full-Screen Gaming Experience:** 1920x1080 optimized display with 64+ professional sprites and 48px tile system
*   **Dual Display Modes:** Toggle between emoji-based graphics and detailed pixel art sprites with visual previews
*   **Customizable Environments:** Choose from multiple wall and floor styles with real-time visual selection
*   **Strategic Combat System:** Enhanced turn-based battles with visual effects, turn indicators, and skill management
*   **Complete Inventory Management:** Full item system with use/equip/drop functionality across multiple characters
*   **Progressive Equipment System:** Extensive weapon/armor progression from basic to epic tier with visual rarity indicators
*   **Exploration & Discovery:** Treasure chests, fog of war system, dynamic camera following, and rare room generation
*   **Multi-Character Parties:** Create up to 3 heroes with unique classes and individual inventories
*   **Professional Asset Integration:** Multiple sprite sources including Crawl tiles and Dungeon Crawl Stone Soup Full
*   **Persistent Game State:** Comprehensive save/load system with settings preservation and auto-save functionality
*   **Cross-Platform Compatibility:** Windows/Linux/Mac support with optimized font and audio handling

## How to Play

1.  **Installation:**
    *   **Python Requirements:** Python 3.13.5+ (compatible with modern Python versions)
    *   **Pygame Installation:** Install Pygame 2.6.1+ by running: `pip install pygame` or `py -m pip install pygame`
    *   **Font Support:** Windows users automatically get Segoe UI Emoji support for proper emoji rendering

2.  **Running the Game:**
    *   Navigate to the game's directory in your terminal
    *   Run the script using: `python rpg_pygame.py` or `py rpg_pygame.py`
    *   **System Check:** Game will display asset loading status with detailed feedback

3.  **Audio Setup (Optional but Recommended):**
    *   **Background Music:** Place music files in `/music/` folder:
        - `Start_Menu_music.ogg` - Main menu background
        - `Ruins_(Soundtrack)_music.ogg` - Exploration music
        - `Spider_Dance_music.ogg` - Goblin combat music
        - `Heartache_music.ogg` - Orc/Troll combat music
        - `Dummy!_music.ogg` - Dragon boss battle music
    *   **Sound Effects:** Place RPG Sound Pack files in `/RPG Sound Pack/` with subfolders:
        - `/battle/` - Combat sounds (swing.wav, magic1.wav, etc.)
        - `/interface/` - Menu sounds (interface1.wav through interface6.wav)
        - `/inventory/` - Item sounds (coin.wav, chainmail1.wav, bottle.wav, etc.)
        - `/world/` - Environmental sounds (door.wav)
        - `/NPC/` - Enemy-specific audio in appropriate subfolders

4.  **Gameplay:**
    *   **Character Creation:** Follow the on-screen prompts to choose the number of heroes, their names, and their classes (Warrior, Mage, Archer).
    *   **Settings:** Press **S** in the main menu to access settings:
        *   Toggle between emoji and sprite display modes
        *   Select different wall styles (Stone Brick, Stone Dark, Brick Brown, Marble Wall)
        *   Select different floor styles (Sandstone, Dirt, Pebble Brown, Marble Floor)
    *   **Exploration:** Use the **W, A, S, D** keys to move your party through the dungeon.
    *   **Interaction:** Press **E** when standing on objects to interact:
        *   **Treasure Chests:** Open chests to collect multiple items
        *   **Items:** Pick up weapons, armor, and potions from the ground
        *   **Shop NPCs:** Trade with merchants in special shop rooms (🧙‍♂️)
    *   **Shopping:** When you find a merchant, press **E** to open the shop:
        *   Use **TAB** to switch between Buy and Sell modes
        *   Use arrow keys (← → ↑ ↓) to navigate players and items
        *   Press **Enter** to complete purchases/sales
        *   Press **ESC** or **Q** to close the shop
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
    *   **Victory:** Defeat the final boss (dragon) on the last level to trigger the victory screen:
        *   View your final statistics and achievements
        *   Choose to start a new game (deletes current save)
        *   Return to main menu (keeps save for future play)
        *   Exit the game completely

## Technical Specifications

**Tested Environment:**
- **Python:** 3.13.5 (compatible with 3.8+)
- **Pygame:** 2.6.1 with SDL 2.28.4
- **Platform:** Windows 11 (cross-platform compatible)
- **Resolution:** 1920x1080 optimized (scalable)
- **Frame Rate:** 60 FPS with smooth gameplay

**Asset Requirements:**
- **Total Sprites:** 64+ game sprites + 6 UI elements
- **Audio Files:** 6 music tracks + 26 sound effects  
- **Font Support:** Segoe UI Emoji (Windows) with fallback support
- **File Formats:** PNG (sprites), OGG (music), WAV (sound effects)

**Performance:**
- **Memory Usage:** Optimized sprite loading and caching
- **CPU Usage:** Efficient 60 FPS game loop with delta timing
- **Storage:** ~50MB for full asset package
- **Load Time:** <5 seconds for complete asset initialization

## Documentation

For detailed information about specific game systems, see these documentation files:

- **[💾 Save System](./SAVE_SYSTEM.md)** - Complete guide to saving/loading games, controls, and file management
- **[🎒 Item System Improvements](./ITEM_IMPROVEMENTS.md)** - Enhanced item display and duplicate prevention features
- **[⚙️ Settings & Configuration](./README.md#settings-guide)** - Visual customization and game options

### Quick Links
- [How to Play](#how-to-play) - Game basics and controls
- [Save System Features](./SAVE_SYSTEM.md#save-system-features) - Auto-save, manual save, and file management
- [Combat Controls](./SAVE_SYSTEM.md#in-combat) - Battle system commands
- [Item Display Improvements](./ITEM_IMPROVEMENTS.md#enhanced-item-sprite-display) - Visual enhancements and sprite system

## Settings Guide

The game includes a comprehensive settings system accessible from the main menu:

*   **Press S** from the main menu to access settings
*   **Emoji Toggle:** Switch between emoji characters and sprite graphics
*   **Wall Selection:** Choose from Stone Brick, Stone Dark, Brick Brown, or Marble Wall styles
*   **Floor Selection:** Choose from Sandstone, Dirt, Pebble Brown, or Marble Floor styles
*   **Visual Previews:** See actual sprite images when selecting wall and floor styles
*   **Real-time Updates:** Changes take effect immediately in the game

---

## Version History & Development Notes

### v1.20.1: Enhanced Shop UX & Error Handling
**Improved Shop Interface & User Experience:**
- **Enhanced TAB Key Visibility**: Prominent "Press [TAB] to Switch" instruction displayed below Buy/Sell tabs
  - **Golden Highlighting**: TAB instruction shown in highlighted box with gradient background for maximum visibility
  - **Better Layout**: Reorganized shop interface to accommodate TAB instruction without clutter
  - **Clear Visual Hierarchy**: TAB switching instruction is now unmistakable and prominently positioned
- **Comprehensive Error Messages**: Professional error handling for all shop transaction failures
  - **Insufficient Gold**: Shows "❌ Not enough gold! Need Xg, have Yg" with specific amounts
  - **Full Inventory**: Detailed messages showing current/max capacity by item type:
    - "❌ Weapon inventory full! (3/3)"
    - "❌ Armor inventory full! (2/2)"
    - "❌ Potion inventory full! (5/5)"
  - **Enhanced Visual Feedback**: Success messages with "✅" and error messages with "❌" for clarity
- **Smart Purchase Indicators**: Visual cues for item availability in shop interface
  - **Unaffordable Items**: Items too expensive display in red with "[TOO EXPENSIVE]" tag
  - **Full Inventory**: Items that can't be carried show in orange with "[INVENTORY FULL]" tag
  - **Available Items**: Purchaseable items display in normal color for clear distinction
- **Improved Audio Feedback**: Proper sound effects for all shop interactions
  - **Error Sounds**: Dedicated error sound for failed transactions (insufficient gold, full inventory)
  - **Success Sounds**: Coin pickup sounds for successful purchases and sales
  - **Interactive Audio**: Different sound cues for different types of shop feedback

**User Request**: "could you show that tab is the button to press to change from buy to sell and could you have a message pop up if someone tries to buy an item with a full backpack or they dont have enough gold"

**Technical Implementation**:
- Enhanced `draw_shop_screen()` with prominent TAB instruction display and improved layout
- Updated `buy_item()` method with comprehensive error checking and detailed feedback messages
- Added visual affordability indicators in `draw_shop_buy_items()` with color-coded item status
- Improved `sell_item()` method with better equipped item detection and error messaging
- Integrated proper sound effects for all shop transaction outcomes

### v1.20: Shop System Implementation
**Dynamic Trading & Economy System:**
- **Shop Room Generation**: Added merchant rooms (15% spawn chance, max 1 per level) with peaceful trading environments
  - **Shopkeeper NPCs**: Friendly merchant characters (🧙‍♂️) that spawn in special shop rooms
  - **No Combat Zones**: Shop rooms contain no enemies, providing safe trading havens
  - **Smart Room Placement**: Shop rooms never spawn in first or last rooms of each dungeon level
- **Complete Shop Interface**: Professional trading UI with buy/sell functionality
  - **Dual Mode System**: TAB to switch between Buy and Sell modes with visual indicators
  - **Visual Item Display**: Items show sprites, stats, and prices with clear affordability indicators  
  - **Player Selection**: Navigate between party members for individual gold management
  - **Intuitive Controls**: Arrow keys for navigation, ENTER to trade, ESC to close
- **Gold Economy System**: Full currency implementation with balanced pricing
  - **Starting Capital**: All players begin with 100 gold for early purchases
  - **Smart Pricing**: Dynamic pricing based on item rarity (common=50g, epic=400g+) and type
  - **Sell-Back Value**: Items sell for 50% of purchase price, encouraging strategic trading
  - **Persistent Wealth**: Gold amounts saved and loaded with game progress
- **Merchant Inventory**: Randomly generated shop contents with 4-6 items per visit
  - **Mixed Stock**: Balanced selection of weapons, armor, and potions for all classes
  - **Rarity Distribution**: Higher-tier items available but more expensive
  - **Dynamic Restocking**: Each shop visit generates new random inventory

**User Request**: "how easy would it be to implement a room that spawns with a shop" → "could you implement that"

**Technical Implementation**:
- Added `Shopkeeper` class with inventory generation and pricing methods
- Enhanced `determine_room_type()` to include shop room generation with spawn tracking
- Implemented `place_shop_room_content()` for peaceful merchant room setup
- Created complete shop UI system with `draw_shop_screen()`, buy/sell interfaces, and input handling
- Extended Player class with gold tracking and integrated with save/load system
- Added shopkeeper rendering to main game display with proper visibility and sprite support

### v1.19: Enhanced Inventory Visual System
**Enhanced Item Display & User Experience:**
- **Visual Item Identification**: Complete inventory overhaul with sprite display system
  - **Item Sprites in Inventory**: All weapons, armor, and potions now display their actual sprites alongside text descriptions
  - **Smart Sprite Detection**: Automatic sprite key detection based on item type and sprite naming conventions
  - **Scaled Visual Display**: Items rendered at optimal 24x24 pixel size for clear visibility in inventory interface
  - **Dynamic Positioning**: Text automatically repositioned to accommodate sprite display without overlap
  - **Fallback System**: Graceful handling when item sprites are not found, maintaining text-only display
- **Professional Item Presentation**: Enhanced visual hierarchy with sprites providing immediate item recognition
  - **Weapon Sprites**: Swords, hammers, bows, and staffs visually represented with proper scaling
  - **Armor Sprites**: Leather, chainmail, and plate armor shown with distinctive visual indicators
  - **Potion Sprites**: Healing potions displayed with recognizable potion bottle graphics
  - **Consistent Layout**: Uniform spacing and alignment for professional inventory appearance

**User Request**: "could you show the item image on the inventory screen"

**Technical Implementation**:
- Enhanced `draw_inventory_item()` method with sprite rendering capabilities
- Added smart sprite key detection for weapons ("weapon_{sprite_name}"), armor ("armor_{sprite_name}"), and potions ("item_potion")
- Implemented scaled sprite rendering (24x24) with proper positioning relative to text elements
- Created fallback system maintaining text-only display when sprites unavailable
- Integrated with existing sprite loading system for seamless asset utilization

### v1.18: Enhanced Visual Experience & UI Overhaul
**Enhanced Visual & UI System:**
- **Complete Visual Enhancement**: Comprehensive modernization of the entire game interface
  - **Professional Color Palette**: Themed color system with primary/secondary variations, success/danger/warning states
  - **Advanced Gradient System**: Dynamic gradient backgrounds, panels, buttons, and health bars for visual depth
  - **Animation & Particle Effects**: Coordinated animation manager with particle systems for magical effects
  - **Enhanced Text Rendering**: Professional text with shadow effects for optimal readability
- **Combat Interface Improvements**: Fixed overlapping UI elements and enhanced battle screen layout
  - **Resolved UI Conflicts**: Fixed yellow glow box overlapping "Your Party" text in combat
  - **Better Spacing**: Increased spacing between combat title and player panels (20px → 40px additional spacing)
  - **Professional Layout**: Enhanced player/enemy panels with proper visual hierarchy and organization
  - **Turn Indicators**: Dramatic glow effects for current turn without interfering with text elements
- **Modern Inventory System**: Complete overhaul of inventory management interface
  - **Categorized Display**: Professional organization with Weapons/Armor/Consumables sections and counters
  - **Rarity System**: Color-coded items (common/uncommon/rare/epic) with visual indicators
  - **Enhanced Item Interaction**: Equipment status display, usage feedback, and professional item descriptions
- **Enhanced Main Menu**: Modernized menu system with gradient backgrounds, hover effects, and particle animations

**User Request**: "the yellow box in the combat ui is overlapping the party text" + comprehensive UI enhancement requests

**Technical Implementation**:
- Added complete ENHANCED_COLORS system with professional color palette
- Implemented draw_gradient_rect() and draw_text_with_shadow() functions
- Created AnimationManager class for coordinated visual effects
- Fixed combat UI positioning by adjusting player_section spacing and panel heights
- Enhanced inventory system with categorized display and visual feedback systems

### v1.17: Game Balance & Progression Overhaul
**Balanced Loot System:**
- **Rare Chest Rooms**: Significantly reduced chest room spawn rates for better game balance
  - Chest room chance: 15% → 6% per room (much more rare and exciting to find)
  - Treasure room chance: 8% → 4% per room, max reduced from 2 to 1 per level
  - Fallback chest room: Now only 50% chance instead of guaranteed
  - Creates more meaningful exploration and discovery moments
- **Single Player Duplicate Prevention**: Fixed item duplication issue for solo players
  - **No More Duplicates**: Single players can only obtain one of each unique weapon/armor
  - **Smart Tracking**: Items marked as obtained from all sources (ground, chests, auto-pickup)
  - **Multi-player Preservation**: Party mode still allows duplicate items for different members
  - **Better Progression**: Forces players to explore more to find variety instead of duplicates
- **Improved Loot Distribution**: Rebalanced item spawn rates across all room types
  - **Regular Rooms**: 30% chest chance (↑5%), 70% ground loot chance (↑20%)
  - **Ground Loot Mix**: 55% potions, 20% weapons (↑2%), 25% armor (↑5%) - better equipment balance
  - **Chest Rooms**: Enhanced with 2-4 chests, 30% rare+ weapon bias, 25% rare+ armor bias
  - **Treasure Rooms**: 60% chest chance, fewer enemies (0-1), better reward-to-risk ratio

**User Request**: "could you make the chest rooms more rare and also fix the double up on items, could you make it so if your playing single player youll only get one"

**Technical Implementation**:
- Modified `determine_room_type()` with reduced spawn probabilities and limits
- Enhanced all item generation methods to call `mark_item_obtained()` for single player tracking
- Added single player duplicate prevention in `get_available_weapons/armor_for_players()`
- Updated pickup systems in `open_treasure_chest()`, manual pickup, and auto-pickup during movement
- Improved fallback chest room generation with 50% probability instead of guaranteed

### v1.15.1: Critical Combat Bug Fix
**Bug Fixes:**
- **Combat Skill Crash Prevention**: Fixed critical crash occurring when players used skills with no alive enemies
  - **IndexError Fix**: Resolved `random.choice()` from empty sequence when all enemies were defeated
  - **Warrior Power Strike**: Added alive enemy check before targeting single enemy
  - **Archer Double Shot**: Enhanced to handle enemies dying between shots with dynamic target list updates
  - **Mage Fireball**: Optimized to use pre-filtered alive enemies list for better performance
  - **User Feedback**: Added clear "No enemies to target!" message when skills cannot be used
  - **Race Condition Prevention**: Prevents skills from executing when last enemy dies in same turn
- **Enhanced Combat Flow**: Skills now gracefully handle edge cases during battle end conditions
  - Early return system when no valid targets exist
  - Dynamic enemy list updates for multi-target skills
  - Improved combat stability and user experience

**User Report**: "IndexError: Cannot choose from an empty sequence" crash traceback when using combat skills

**Technical Implementation**:
- Added `alive_enemies = [e for e in enemies if e.is_alive()]` check at start of `use_skill()`
- Early return with user message when no enemies available for targeting
- Enhanced archer logic to refresh target list between Double Shot attacks
- Optimized mage Fireball to iterate over pre-filtered alive enemies list

### v1.15: Victory Screen & Game Completion
**Major Features:**
- **Complete Victory Screen Implementation**: Fixed dragon defeat not triggering proper game ending
  - Comprehensive victory display with final player statistics (level, HP, weapon, dungeon progress)
  - Gold-colored "VICTORY!" title with congratulatory messages
  - Fixed main game loop to continue running instead of closing after victory
  - Proper victory state management with `game_won` flag and state transitions
- **Enhanced Post-Victory Options**: Multiple user choices after defeating the final boss
  - **New Game (N)**: Automatically deletes current save and starts completely fresh
  - **Return to Main Menu (M)**: Preserves current save file and returns to main menu
  - **Quit Game (Q)**: Clean exit from the application
  - Clear on-screen instructions explaining each option's effect on save data
- **Improved Dragon Defeat Detection**: Reliable final boss victory condition
  - Fixed detection logic using `enemy.enemy_type == "dragon"` instead of capitalized name
  - Proper combat end flow that triggers victory instead of returning to normal gameplay
  - Victory message: "The dragon has been slain! You are victorious!"
- **Game State Reset System**: Complete cleanup for new playthroughs
  - Enhanced `reset_game_state()` method that properly resets `game_won` flag
  - Maintained save file integrity with user-controlled deletion
  - Seamless transitions between victory, menu, and new game initialization

### v1.14: Enhanced Audio & Asset System
**Major Features:**
- **Dynamic Music System**: Context-aware background music with 6+ tracks
  - Menu background music ("Start_Menu_music.ogg")
  - Exploration music ("Ruins_(Soundtrack)_music.ogg") 
  - Enemy-specific combat music: Spider Dance (goblin), Heartache (orc/troll), Dummy! (dragon)
  - Smooth music transitions between game states without interruption
  - Volume control and loop management for seamless audio experience
- **Professional Sound Effects Package**: 26+ sound effects from RPG Sound Pack
  - **Combat Audio**: Multiple sword attacks, magic spells, weapon drawing sounds
  - **Interface Audio**: Menu navigation, confirmations, button hovers, error/success feedback
  - **Inventory Audio**: Coin pickup, armor equipping, item drops, bottle sounds
  - **World Audio**: Door opening, enemy-specific combat sounds
  - **Dynamic Sound Selection**: Random sound variations for repeated actions
- **Expanded Sprite Collection**: Professional asset integration with 64+ sprites
  - **Enhanced Weapon Arsenal**: Added 14 additional epic weapons from Dungeon Crawl Stone Soup Full
    - Ancient Sword, Golden Sword, Katana, Claymore, War Hammer, Halberd, Scythe
    - Mage weapons: Scimitar, Rapier, enhanced tridents and staffs
  - **Complete Armor Progression**: Full armor sets from leather to crystal plate mail
  - **Environmental Assets**: Treasure chests with open/closed states for better visual feedback
  - **UI Elements**: 6 professional UI elements (tabs, buttons, labels) from crawl-tiles GUI
- **Advanced Asset Management**: Multi-source loading system with comprehensive error handling
  - **Dual Asset Sources**: Primary crawl-tiles Oct-5-2010 + Secondary Dungeon Crawl Stone Soup Full
  - **Intelligent Loading**: Detailed success/failure reporting with 64 sprites + 6 UI elements
  - **Automatic Optimization**: All sprites scaled to optimal TILE_SIZE (48px) for crisp display
  - **Fallback Systems**: Graceful degradation when assets are missing
- **System Compatibility**: Updated for modern gaming environments
  - **Python 3.13.5** with **Pygame 2.6.1** and **SDL 2.28.4**
  - **Enhanced Font Support**: Segoe UI Emoji integration for proper Windows emoji rendering
  - **Audio Architecture**: Professional sound mixing with volume controls and format support

**User Request**: "Continue to iterate?" (following music system implementation)

**Technical Implementation**: 
- Enhanced load_sounds() function loading 26 categorized sound effects
- Added get_combat_music_for_enemies() for dynamic music selection
- Expanded sprite loading with secondary asset source integration
- Implemented play_music() with state tracking and transition management
- Added comprehensive error handling and asset validation systems

### v1.13: Classic Interface Restoration
**Major Features:**
- **Clean Traditional Interface**: Complete removal of all Undertale UI elements and dependencies
  - Eliminated Frisk animation system and UISpriteCutter class for streamlined codebase
  - Restored classic RPG aesthetic while maintaining modern combat enhancements
  - Simplified player rendering using static sprites from dungeon crawler assets
- **Preserved Enhanced Systems**: Kept all gameplay improvements while simplifying presentation
  - **Turn-Based Combat**: Maintained health bars, status indicators, and visual feedback
  - **Complete Inventory**: Preserved all inventory functionality with multi-character tabs
  - **Equipment System**: Kept weapon/armor bonuses and equipment management
- **Code Optimization**: Streamlined architecture without animation complexity
  - Reduced from complex animation framework to efficient static sprite rendering
  - Maintained compatibility with 20 core sprites and 6 UI elements from crawl-tiles
  - Simple geometric combat buttons instead of Undertale-style elements
  - Clean, maintainable codebase focused on core RPG mechanics

**User Request**: "could you undo everything you just did"

**Technical Implementation**: 
- Removed SpriteAnimation class and AnimatedEntity mixin system
- Restored original Entity, Player, and Enemy classes without animation code
- Eliminated animation update loops and delta time calculations from game logic
- Simplified rendering system back to static sprite display
- Maintained enhanced combat UI and inventory systems without animation dependencies

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
