# Card Battle Game

A tactical card-based battle game built with Pygame.

## Installation

1. Install Python 3.7 or higher
2. Install Pygame:
```bash
pip install pygame
```

## How to Run

```bash
python main.py
```

## Game Controls

### Card Selection
- **1**: Select Archer card
- **2**: Select Knight card  
- **3**: Select Goblin card
- **4**: Select Fireball spell
- **5**: Select Lightning spell
- **6**: Select Tower building
- **7**: Select Wall building

### Gameplay
- **Space**: Toggle card placement mode
- **Left Click**: Place selected card on grid (when in placement mode)
- **Right Click**: Cancel card placement
- **Escape**: Exit game

## Game Rules

### Resources
- Start with 10 mana
- Mana regenerates at 1 mana per second
- Each card costs mana to deploy

### Card Types

#### Units
- **Archer** (3 mana): Ranged unit, fast movement, 3 tile attack range
- **Knight** (5 mana): Heavy melee unit, slow but high health
- **Goblin** (1 mana): Fast weak melee unit, cheap to deploy

#### Spells  
- **Fireball** (4 mana): Area damage spell, affects 2 tile radius
- **Lightning** (6 mana): Single target high damage spell

#### Buildings
- **Tower** (6 mana): Defensive building with long range attacks
- **Wall** (2 mana): Defensive structure that blocks movement

### Grid System
- 8x8 grid battlefield
- Cards occupy single grid tiles
- Range is calculated in tile distance

## Game Features

Currently Implemented (Step 1):
- ✅ Basic file structure and architecture
- ✅ Pygame initialization with 500x500 viewport
- ✅ Abstract BaseCard class with core attributes
- ✅ Base game loop and event handling
- ✅ 7 different card types (units, spells, buildings)
- ✅ Grid-based board system (8x8 tiles)
- ✅ Card spawning/placement mechanics
- ✅ Basic collision detection
- ✅ Resource management (mana system)
- ✅ Combat system (damage, health tracking)

Planned (Steps 2-4):
- 🔄 Unit movement and pathfinding
- 🔄 Advanced AI opponent
- 🔄 Visual effects and animations
- 🔄 Sound effects and music
- 🔄 Enhanced UI overlay
- 🔄 Performance optimization

## Architecture

The game follows a modular architecture:

- `main.py`: Entry point and main game loop
- `cards/`: All card-related classes and factory
  - `base_card.py`: Abstract base class for all cards
  - `unit_cards.py`: Unit card implementations
  - `spell_cards.py`: Spell card implementations  
  - `building_cards.py`: Building card implementations
  - `card_factory.py`: Factory pattern for card creation
- `utils/`: Game utilities and management
  - `game_state.py`: Centralized game state management
  - `event_handler.py`: Input and event processing
- `assets/`: Game assets (images, sounds, etc.)

## iOS Deployment Note

This game is built with Pygame, which doesn't natively support iOS. For iOS deployment, consider:
1. Using Kivy instead of Pygame (can be packaged for iOS via Buildozer)
2. Converting to a web app (Flask + Pygame-Web)
3. Building for desktop first, then exploring iOS alternatives

The current implementation focuses on desktop platforms (Windows, macOS, Linux) for easy development and testing.