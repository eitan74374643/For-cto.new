import * as THREE from 'three';

export class Agent {
    constructor(gridWorld, startX = 0, startZ = 0) {
        this.gridWorld = gridWorld;
        this.gridX = startX;
        this.gridZ = startZ;
        this.isMoving = false;
        this.currentAnimation = null;
        
        this.createAgentMesh();
        this.gridWorld.addBlock(this.mesh);
        this.gridWorld.markCellOccupied(this.gridX, 0, this.gridZ);
    }

    createAgentMesh() {
        const group = new THREE.Group();
        
        const bodyGeometry = new THREE.BoxGeometry(0.6, 0.8, 0.6);
        const bodyMaterial = new THREE.MeshLambertMaterial({ color: 0x9B59B6 });
        const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
        body.position.y = 0.5;
        body.castShadow = true;
        body.receiveShadow = true;
        group.add(body);

        const headGeometry = new THREE.BoxGeometry(0.45, 0.45, 0.45);
        const headMaterial = new THREE.MeshLambertMaterial({ color: 0x3498DB });
        const head = new THREE.Mesh(headGeometry, headMaterial);
        head.position.y = 1.1;
        head.castShadow = true;
        head.receiveShadow = true;
        group.add(head);

        const antennaGeometry = new THREE.BoxGeometry(0.06, 0.25, 0.06);
        const antennaMaterial = new THREE.MeshLambertMaterial({ color: 0xE74C3C });
        
        const antenna1 = new THREE.Mesh(antennaGeometry, antennaMaterial);
        antenna1.position.set(-0.12, 1.45, 0);
        group.add(antenna1);

        const antenna2 = new THREE.Mesh(antennaGeometry, antennaMaterial);
        antenna2.position.set(0.12, 1.45, 0);
        group.add(antenna2);

        const eyeGeometry = new THREE.BoxGeometry(0.1, 0.1, 0.12);
        const eyeMaterial = new THREE.MeshBasicMaterial({ color: 0xFFFFFF });
        
        const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
        leftEye.position.set(-0.12, 1.15, 0.23);
        group.add(leftEye);

        const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
        rightEye.position.set(0.12, 1.15, 0.23);
        group.add(rightEye);

        const pupilGeometry = new THREE.BoxGeometry(0.04, 0.04, 0.08);
        const pupilMaterial = new THREE.MeshBasicMaterial({ color: 0x2C3E50 });
        
        const leftPupil = new THREE.Mesh(pupilGeometry, pupilMaterial);
        leftPupil.position.set(-0.12, 1.15, 0.28);
        group.add(leftPupil);

        const rightPupil = new THREE.Mesh(pupilGeometry, pupilMaterial);
        rightPupil.position.set(0.12, 1.15, 0.28);
        group.add(rightPupil);

        const offset = (this.gridWorld.gridSize - 1) / 2;
        group.position.set(this.gridX - offset, 0, this.gridZ - offset);
        
        this.mesh = group;
        this.startPosition = group.position.clone();
    }

    move(direction) {
        if (this.isMoving) {
            return { success: false, message: 'Agent is already moving' };
        }

        let newX = this.gridX;
        let newZ = this.gridZ;

        switch (direction.toLowerCase()) {
            case 'up':
                newZ = this.gridZ - 1;
                break;
            case 'down':
                newZ = this.gridZ + 1;
                break;
            case 'left':
                newX = this.gridX - 1;
                break;
            case 'right':
                newX = this.gridX + 1;
                break;
            default:
                return { success: false, message: 'Invalid direction. Use: up, down, left, right' };
        }

        if (!this.gridWorld.isInBounds(newX, newZ)) {
            return { success: false, message: 'Cannot move outside the grid' };
        }

        if (this.gridWorld.isCellOccupied(newX, 0, newZ)) {
            return { success: false, message: 'Target cell is occupied' };
        }

        this.animateMove(newX, newZ);
        return { success: true, message: `Moving ${direction} to (${newX}, ${newZ})` };
    }

    animateMove(targetGridX, targetGridZ) {
        this.isMoving = true;
        this.gridWorld.unmarkCellOccupied(this.gridX, 0, this.gridZ);
        
        this.startPosition = this.mesh.position.clone();
        const offset = (this.gridWorld.gridSize - 1) / 2;
        const targetPosition = new THREE.Vector3(
            targetGridX - offset,
            0,
            targetGridZ - offset
        );

        const duration = 300;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const easedProgress = this.easeInOutQuad(progress);
            
            this.mesh.position.lerpVectors(this.startPosition, targetPosition, easedProgress);

            const jumpHeight = Math.sin(progress * Math.PI) * 0.3;
            this.mesh.position.y = jumpHeight;

            if (progress < 1) {
                this.currentAnimation = requestAnimationFrame(animate);
            } else {
                this.mesh.position.copy(targetPosition);
                this.mesh.position.y = 0;
                this.gridX = targetGridX;
                this.gridZ = targetGridZ;
                this.gridWorld.markCellOccupied(this.gridX, 0, this.gridZ);
                this.isMoving = false;
                this.currentAnimation = null;
            }
        };

        this.currentAnimation = requestAnimationFrame(animate);
    }

    easeInOutQuad(t) {
        return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
    }

    getPosition() {
        return { x: this.gridX, z: this.gridZ };
    }
}
