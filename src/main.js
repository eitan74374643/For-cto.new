import { GridWorld } from './grid-world.js';
import { Player } from './player.js';
import { Agent } from './agent.js';

const gridWorld = new GridWorld('canvas-container');
const player = new Player(gridWorld, 0, 0);
const agent = new Agent(gridWorld, -2, -2);

function spawnBlock(x, y, z, color = '#FF6B6B') {
    if (typeof color === 'string' && color.startsWith('#')) {
        color = parseInt(color.replace('#', ''), 16);
    }

    if (gridWorld.isCellOccupied(x, y, z)) {
        console.warn(`Cell (${x}, ${y}, ${z}) is already occupied`);
        return null;
    }

    const geometry = new THREE.BoxGeometry(0.9, 0.9, 0.9);
    const material = new THREE.MeshLambertMaterial({ color: color });
    const block = new THREE.Mesh(geometry, material);
    
    const offset = (gridWorld.gridSize - 1) / 2;
    block.position.set(x - offset, y + 0.5, z - offset);
    block.castShadow = true;
    block.receiveShadow = true;
    
    gridWorld.addBlock(block);
    gridWorld.markCellOccupied(x, y, z);
    
    block.userData = { type: 'block', gridX: x, gridY: y, gridZ: z };
    
    return block;
}

function moveAgent(direction) {
    const result = agent.move(direction);
    
    if (result.success) {
        console.log(`✅ ${result.message}`);
    } else {
        console.warn(`❌ ${result.message}`);
    }
    
    return result;
}

window.moveAgent = moveAgent;
window.spawnBlock = spawnBlock;
window.gridWorld = gridWorld;
window.player = player;
window.agent = agent;

console.log('🎮 Grid World initialized!');
console.log('Available functions:');
console.log('  - moveAgent("up" | "down" | "left" | "right")');
console.log('  - spawnBlock(x, y, z, color)');
console.log('');
console.log('Examples:');
console.log('  moveAgent("right")');
console.log('  spawnBlock(2, 1, 2, "#FF6B6B")');
