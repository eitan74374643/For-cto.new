import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

export class GridWorld {
    constructor(containerId = 'canvas-container') {
        this.container = document.getElementById(containerId);
        this.gridSize = 10;
        this.cellSize = 1;
        this.blocks = [];
        this.occupiedCells = new Set();
        
        this.initScene();
        this.initLights();
        this.initCamera();
        this.initRenderer();
        this.initControls();
        this.createGrid();
        this.animate();
    }

    initScene() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x87CEEB);
        this.scene.fog = new THREE.Fog(0x87CEEB, 15, 40);
    }

    initLights() {
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 20, 10);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        directionalLight.shadow.camera.near = 0.5;
        directionalLight.shadow.camera.far = 50;
        directionalLight.shadow.camera.left = -15;
        directionalLight.shadow.camera.right = 15;
        directionalLight.shadow.camera.top = 15;
        directionalLight.shadow.camera.bottom = -15;
        this.scene.add(directionalLight);

        const hemisphereLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.5);
        this.scene.add(hemisphereLight);
    }

    initCamera() {
        const aspect = window.innerWidth / window.innerHeight;
        this.camera = new THREE.PerspectiveCamera(60, aspect, 0.1, 1000);
        this.camera.position.set(12, 12, 12);
        this.camera.lookAt(0, 0, 0);
    }

    initRenderer() {
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.container.appendChild(this.renderer.domElement);

        window.addEventListener('resize', () => this.onWindowResize());
    }

    initControls() {
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.maxPolarAngle = Math.PI / 2.2;
        this.controls.minDistance = 5;
        this.controls.maxDistance = 30;
        this.controls.target.set(0, 0, 0);
    }

    createGrid() {
        const brightColors = [
            0xFF6B6B, 0x4ECDC4, 0xFFE66D, 0x95E1D3, 
            0xF38181, 0xAA96DA, 0xFCBAD3, 0xA8D8EA,
            0xFF9F43, 0x5F27CD, 0x00D2D3, 0xFF6B6B
        ];

        const offset = (this.gridSize - 1) / 2;

        for (let x = 0; x < this.gridSize; x++) {
            for (let z = 0; z < this.gridSize; z++) {
                const colorIndex = (x + z) % brightColors.length;
                const color = brightColors[colorIndex];
                
                const geometry = new THREE.BoxGeometry(this.cellSize * 0.95, 0.1, this.cellSize * 0.95);
                const material = new THREE.MeshLambertMaterial({ 
                    color: color,
                });
                
                const tile = new THREE.Mesh(geometry, material);
                tile.position.set(
                    x - offset,
                    -0.05,
                    z - offset
                );
                tile.receiveShadow = true;
                this.scene.add(tile);
            }
        }

        const gridHelper = new THREE.GridHelper(this.gridSize, this.gridSize, 0xffffff, 0xffffff);
        gridHelper.position.y = 0.01;
        gridHelper.material.opacity = 0.15;
        gridHelper.material.transparent = true;
        this.scene.add(gridHelper);
    }

    addBlock(block) {
        this.scene.add(block);
        this.blocks.push(block);
    }

    isCellOccupied(x, y, z) {
        return this.occupiedCells.has(`${x},${y},${z}`);
    }

    markCellOccupied(x, y, z) {
        this.occupiedCells.add(`${x},${y},${z}`);
    }

    unmarkCellOccupied(x, y, z) {
        this.occupiedCells.delete(`${x},${y},${z}`);
    }

    isInBounds(x, z) {
        const offset = (this.gridSize - 1) / 2;
        return x >= -offset && x <= offset && z >= -offset && z <= offset;
    }

    onWindowResize() {
        const aspect = window.innerWidth / window.innerHeight;
        this.camera.aspect = aspect;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }

    getScene() {
        return this.scene;
    }
}
