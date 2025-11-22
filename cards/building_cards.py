from .base_card import BaseCard
from typing import Tuple

class Tower(BaseCard):
    """Defensive building with long range attacks"""
    
    def __init__(self, position: Tuple[int, int] = (0, 0), owner: str = "player"):
        super().__init__(
            name="Tower",
            health=150,
            attack=20,
            speed=0,  # Buildings don't move
            cost=6,
            deployment_time=3.0,
            position=position,
            owner=owner
        )
        self.attack_range = 4.0  # Very long range
        self.is_deployed = True  # Buildings are immediately deployed after construction
    
    def get_card_type(self) -> str:
        return "building"
    
    def update(self, dt: float):
        """Override update for building behavior"""
        # Buildings don't move, but they can attack
        if self.is_deployed:
            self._update_combat(dt)

class Wall(BaseCard):
    """Defensive structure that blocks movement"""
    
    def __init__(self, position: Tuple[int, int] = (0, 0), owner: str = "player"):
        super().__init__(
            name="Wall",
            health=200,
            attack=0,  # Walls don't attack
            speed=0,
            cost=2,
            deployment_time=1.5,
            position=position,
            owner=owner
        )
        self.is_deployed = True  # Walls are immediately deployed after construction
    
    def get_card_type(self) -> str:
        return "building"
    
    def can_attack(self) -> bool:
        """Walls cannot attack"""
        return False
    
    def update(self, dt: float):
        """Walls don't need to update much"""
        pass