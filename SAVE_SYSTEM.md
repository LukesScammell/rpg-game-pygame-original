# RPG Save System Documentation

## Save System Features

### Automatic Save
- Game automatically saves when you quit to main menu (Q key)
- Game automatically saves when you exit during combat (Q key)
- Manual save available with F5 key during gameplay

### Save File Location
- Save file: `rpg_save_game.json`
- Located in the same directory as the game

### What Gets Saved
- Player positions and stats (HP, mana, level, XP)
- Player inventories (all items, weapons, armor)
- Currently equipped weapons and armor
- Dungeon level progression
- Camera position

### What Doesn't Get Saved
- Current dungeon layout (regenerated on load for variety)
- Enemy positions (new enemies spawn on load)
- Treasure chest locations (new chests generate on load)

## Controls

### Main Menu
- **ENTER**: Start new game (when no save exists)
- **N**: Start new game (overwrites existing save)
- **C**: Continue from saved game
- **D**: Delete saved game
- **S**: Settings menu
- **Q**: Quit game

### During Gameplay
- **WASD**: Move player
- **E**: Interact with objects (chests, items)
- **I**: Open inventory
- **Q**: Quit to main menu (auto-saves)
- **F5**: Quick save

### In Combat
- **1**: Attack
- **2**: Use class skill
- **3**: Use item (potions)
- **4**: Try to flee
- **Q**: Quit to main menu (auto-saves)

### In Inventory
- **← →**: Switch between players
- **↑ ↓**: Navigate items
- **ENTER**: Use/equip selected item
- **X**: Drop selected item
- **Q**: Quit to main menu (auto-saves)
- **I/ESC**: Close inventory

## Technical Notes

### Save File Format
The save file uses JSON format and contains:
```json
{
  "players": [...],
  "dungeon_level": 1,
  "current_player_idx": 0,
  "game_state": "playing",
  "camera_x": 0,
  "camera_y": 0
}
```

### Error Handling
- If save file is corrupted, the game will display an error message
- Failed save attempts show "Error saving game!" message
- Failed load attempts return to main menu

### Backup Recommendations
- The save file can be manually backed up by copying `rpg_save_game.json`
- Save file is human-readable JSON, allowing for manual editing if needed
