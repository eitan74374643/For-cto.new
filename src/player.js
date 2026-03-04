import * as THREE from 'three';

export class Player {
    constructor(gridWorld, startX = 0, startZ = 0) {
        this.gridWorld = gridWorld;
        this.gridX = startX;
        this.gridZ = startZ;
        
        this.createPlayerMesh();
        this.gridWorld.addBlock(this.mesh);
        this.gridWorld.markCellOccupied(this.gridX, 0, this.gridZ);
    }

    createPlayerMesh() {
        const group = new THREE.Group();
        
        const bodyGeometry = new THREE.BoxGeometry(0.6, 0.7, 0.6);
        const bodyMaterial = new THREE.MeshLambertMaterial({ color: 0x2ECC71 });
        const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
        body.position.y = 0.4;
        body.castShadow = true;
        body.receiveShadow = true;
        group.add(body);

        const headGeometry = new THREE.BoxGeometry(0.4, 0.4, 0.4);
        const headMaterial = new THREE.MeshLambertMaterial({ color: 0xF1C40F });
        const head = new THREE.Mesh(headGeometry, headMaterial);
        head.position.y = 0.95;
        head.castShadow = true;
        head.receiveShadow = true;
        group.add(head);

        const eyeGeometry = new THREE.BoxGeometry(0.08, 0.08, 0.1);
        const eyeMaterial = new THREE.MeshBasicMaterial({ color: 0x2C3E50 });
        
        const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
        leftEye.position.set(-0.1, 0.98, 0.2);
        group.add(leftEye);

        const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
        rightEye.position.set(0.1, 0.98, 0.2);
        group.add(rightEye);

        const offset = (this.gridWorld.gridSize - 1) / 2;
        group.position.set(this.gridX - offset, 0, this.gridZ - offset);
        
        this.mesh = group;
    }

    moveTo(gridX, gridZ) {
        if (!this.gridWorld.isInBounds(gridX, gridZ)) {
            return false;
        }

        if (this.gridWorld.isCellOccupied(gridX, 0, gridZ)) {
            return false;
        }

        this.gridWorld.unmarkCellOccupied(this.gridX, 0, this.gridZ);
        
        this.gridX = gridX;
        this.gridZ = gridZ;
        
        const offset = (this.gridWorld.gridSize - 1) / 2;
        this.mesh.position.set(this.gridX - offset, 0, this.gridZ - offset);
        
        this.gridWorld.markCellOccupied(this.gridX, 0, this.gridZ);
        return true;
    }

    getPosition() {
        return { x: this.gridX, z: this.gridZ };
    }
}
