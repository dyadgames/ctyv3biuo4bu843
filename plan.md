# RPG Visual Novel Template - Project Plan

## Phase 1: Core Game Engine & JSON Data System ✅
- [x] Design and implement JSON data structure for game content (scenes, characters, dialogue, choices)
- [x] Create file organization system for game assets (JSON files, character images, backgrounds)
- [x] Build core game state management (current scene, variables, player choices, history)
- [x] Implement scene renderer that reads JSON and displays content
- [x] Add dialogue system with character portraits and text display
- [x] Create choice system that branches story based on player decisions

## Phase 2: Visual Novel UI & Game Controls ✅
- [x] Design main game screen with layered components (background, character sprites, dialogue box, UI controls)
- [x] Implement character sprite system with positions (left, center, right) and expressions
- [x] Build dialogue box with character name, text display, and continue/auto-play controls
- [x] Add choice buttons that appear when player decisions are required
- [x] Create game menu overlay (save, load, settings, title screen)
- [x] Implement text history/backlog viewer
- [x] Add skip and auto-play functionality

## Phase 3: Game Management & Content Editor ✅
- [x] Implement save/load system using browser storage (15 save slots with timestamps and thumbnails)
- [x] Add settings panel integration with game menu (text speed, auto-play speed)
- [x] Build content preview/editor for creating new games (Monaco editor with file browser)
- [x] Add example game with complete story demonstrating all features (7 scenes, 3 characters, branching paths)
- [x] Create documentation for JSON data format and folder structure

---

## Phase 4: Character Stats & Attributes System ✅
- [x] Design JSON schema for character stats (STR, DEX, CON, INT, WIS, CHA - fully customizable names)
- [x] Create player character data structure with stat values
- [x] Build character stats display panel/overlay accessible from game UI
- [x] Implement stat modification system (level up, training, equipment bonuses)
- [x] Add stat checks for dialogue choices and scene branches
- [x] Create example stat configurations for different game themes (fantasy, sci-fi, modern)

## Phase 5: Inventory System with Sidebar ✅
- [x] Design JSON schema for items (id, name, description, icon, type, properties, usable, effects)
- [x] Create inventory state management (add, remove, use, equip items)
- [x] Build collapsible sidebar inventory UI (toggle open/close, grid or list view)
- [x] Implement item display with icons, names, quantities, and tooltips
- [x] Add item usage system (consumables, equipment, key items)
- [x] Create crafting materials category and item organization
- [x] Integrate inventory access from all game modes (hide in map mode)

## Phase 6: World Map & Location System ✅
- [x] Design JSON schema for world map (100 major locations with coordinates, names, unlock conditions)
- [x] Design JSON schema for regional maps (6-20 minor locations per major location)
- [x] Create map mode state management (separate from visual novel mode)
- [x] Build world map UI showing all major locations with interactive markers
- [x] Implement location selection and navigation between world map and regional maps
- [x] Add regional map view showing minor locations within selected major location
- [x] Create location unlock/discovery system based on game progress
- [x] Add visual indicators for completed/incomplete locations

## Phase 7: Context Menu & Location Actions
- [ ] Design context menu mode (separate from visual novel and map modes)
- [ ] Create diamond-shaped masked image buttons for actions
- [ ] Implement 6 default actions with swappable images:
  - Explore: Trigger random scenarios/events
  - Gather: Resource collection with random rewards
  - Travel: Return to regional or world map
  - Train: Stat increase mini-game or time-based progression
  - Craft: Combine crafting materials into items
  - Rest: Advance time 4 hours, restore health/stamina
- [ ] Build action result system (success/failure, rewards, consequences)
- [ ] Add time tracking system for Rest and other time-based mechanics
- [ ] Create action availability conditions (location-specific, time-based, stat requirements)

---

## Current Status
- Phase 1: Complete ✅
- Phase 2: Complete ✅
- Phase 3: Complete ✅
- Phase 4: Complete ✅ (Character Stats & Attributes)
- Phase 5: Complete ✅ (Inventory System)
- Phase 6: Complete ✅ (World Map & Locations)
- Phase 7: Context Menu & Actions - Not Started 🔴

## Session Summary
✅ **3 Phases Completed This Session:**
1. **Phase 4** - Character Stats System with customizable attributes (fantasy/sci-fi/modern configs)
2. **Phase 5** - Inventory System with collapsible sidebar, item categories, and JSON-driven items
3. **Phase 6** - World Map System with major/regional locations and navigation

## Next Session Goals
Complete Phase 7 (Context Menu & Location Actions) - the final phase!

## Architecture Notes
- **Game Modes**: Visual Novel Mode, Map Mode (world/regional), Context Menu Mode (location actions)
- **Data Structure**: All content (stats, items, locations, actions) defined in JSON for easy swapping
- **Image Assets**: Action button images stored in organized folders with swappable references
- **State Management**: Separate state classes for different game modes with shared player data
