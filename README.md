# Three.js Grid World

A colorful, low-poly 3D grid playground built with Three.js featuring a Player block and an AI Agent that can move between grid cells.

## Features

- 🎨 **Colorful 10x10 Grid Floor** - Bright, vibrant low-poly tiles
- 🟢 **Player Character** - Green block-style character at center
- 🤖 **AI Agent** - Purple character with antennas, movable between cells
- 🎮 **Smooth Animations** - Animated agent movement with jump effects
- 🎯 **External API** - Functions for controlling the world from console/external scripts

## Quick Start

1. **Start a local server** (required for ES modules):
   ```bash
   npm run dev
   # or
   bun run dev
   ```

2. **Open in browser**:
   ```
   http://localhost:8080
   ```

## API

### `moveAgent(direction)`

Moves the AI agent one grid cell in the specified direction.

**Parameters:**
- `direction` - One of: `'up'`, `'down'`, `'left'`, `'right'`

**Returns:**
- Object with `success` (boolean) and `message` (string)

**Example:**
```javascript
moveAgent('right')  // Moves agent one cell to the right
moveAgent('up')     // Moves agent one cell up (negative Z)
```

### `spawnBlock(x, y, z, color)`

Creates a colored block at the specified grid coordinates.

**Parameters:**
- `x` - Grid X coordinate (-5 to 4)
- `y` - Height level (0 = floor, 1 = one block high, etc.)
- `z` - Grid Z coordinate (-5 to 4)
- `color` - Color as hex string (e.g., '#FF6B6B') or color name

**Returns:**
- The created Three.js mesh object, or `null` if cell is occupied

**Examples:**
```javascript
spawnBlock(2, 1, 2, '#FF6B6B')      // Red block at (2, 1, 2)
spawnBlock(-3, 1, 1, '#4ECDC4')     // Teal block at (-3, 1, 1)
spawnBlock(0, 2, 0, '#FFE66D')      // Yellow block stacked 2 high at center
```

## Grid Coordinate System

- **X axis**: -5 to 4 (left to right)
- **Z axis**: -5 to 4 (bottom to top)
- **Y axis**: 0+ (height above floor)
- Origin (0, 0, 0) is at the center of the grid

## Controls

- **Mouse drag** - Rotate camera view
- **Mouse wheel** - Zoom in/out
- **Console** - Use `moveAgent()` and `spawnBlock()` functions

## Architecture

```
src/
├── grid-world.js    # Main scene setup, grid creation, lighting
├── player.js        # Player character class
├── agent.js         # AI Agent with movement logic and animation
└── main.js          # Entry point, exports API to window object
```

## Tech Stack

- Three.js r160 (loaded via CDN)
- Vanilla JavaScript (ES6 modules)
- No build tools required

## License

MIT
