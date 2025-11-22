from abc import ABC, abstractmethod
from typing import Tuple, Optional
import pygame
import math

class BaseCard(ABC):
    """Abstract base class for all game cards"""
    
    def __init__(self, name: str, health: int, attack: int, speed: float, 
                 cost: int, deployment_time: float, position: Tuple[int, int] = (0, 0), 
                 owner: str = "player"):
        """
        Initialize a base card
        
        Args:
            name: Card name
            health: Maximum health points
            attack: Attack damage
            speed: Movement speed (tiles per second)
            cost: Mana cost to deploy
            deployment_time: Time to deploy (seconds)
            position: Grid position (x, y)
            owner: Who owns this card ("player" or "enemy")
        """
        self.name = name
        self.max_health = health
        self.health = health
        self.attack = attack
        self.speed = speed
        self.cost = cost
        self.deployment_time = deployment_time
        self.position = list(position)
        self.owner = owner
        self.is_deployed = False
        self.deployment_timer = 0.0
        self.target = None
        self.attack_cooldown = 0.0
        self.attack_range = 1.0  # Default attack range in tiles
        
    @abstractmethod
    def get_card_type(self) -> str:
        """Return the type of card (unit, spell, building, etc.)"""
        pass
    
    def update(self, dt: float):
        """Update card state"""
        # Handle deployment timer
        if not self.is_deployed:
            self.deployment_timer += dt
            if self.deployment_timer >= self.deployment_time:
                self.is_deployed = True
            return
        
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        
        # Movement and targeting logic
        if self.get_card_type() == "unit":
            self._update_movement(dt)
            self._update_combat(dt)
    
    def _update_movement(self, dt: float):
        """Update unit movement"""
        if self.target and self._is_in_range(self.target):
            return  # Don't move if target is in range
        
        # Simple movement towards nearest enemy (can be improved with pathfinding)
        # This is a placeholder for more sophisticated pathfinding
        pass
    
    def _update_combat(self, dt: float):
        """Update combat logic"""
        if self.attack_cooldown > 0:
            return
        
        # Find and attack targets in range
        # This will be implemented when we have the game state
        pass
    
    def _is_in_range(self, target) -> bool:
        """Check if target is within attack range"""
        distance = math.sqrt(
            (self.position[0] - target.position[0]) ** 2 +
            (self.position[1] - target.position[1]) ** 2
        )
        return distance <= self.attack_range
    
    def take_damage(self, damage: int):
        """Apply damage to the card"""
        self.health -= damage
        if self.health < 0:
            self.health = 0
    
    def is_alive(self) -> bool:
        """Check if the card is still alive"""
        return self.health > 0
    
    def can_attack(self) -> bool:
        """Check if the card can attack"""
        return self.is_deployed and self.attack_cooldown <= 0
    
    def attack_target(self, target):
        """Attack a target"""
        if self.can_attack() and self._is_in_range(target):
            target.take_damage(self.attack)
            self.attack_cooldown = 1.0  # 1 second cooldown
            return True
        return False
    
    def set_position(self, x: int, y: int):
        """Set the card's grid position"""
        self.position = [x, y]
    
    def get_position(self) -> Tuple[int, int]:
        """Get the card's grid position"""
        return tuple(self.position)
    
    def get_deploy_progress(self) -> float:
        """Get deployment progress (0.0 to 1.0)"""
        if self.is_deployed:
            return 1.0
        return min(self.deployment_timer / self.deployment_time, 1.0)
    
    def __str__(self) -> str:
        """String representation of the card"""
        return f"{self.name} (HP: {self.health}/{self.max_health}, ATK: {self.attack}, POS: {self.position})"