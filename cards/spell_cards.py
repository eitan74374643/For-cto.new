from .base_card import BaseCard
from typing import Tuple

class Fireball(BaseCard):
    """Area damage spell that damages all units in target area"""
    
    def __init__(self, position: Tuple[int, int] = (0, 0), owner: str = "player"):
        super().__init__(
            name="Fireball",
            health=1,  # Spells have minimal "health" just to be consistent
            attack=40,
            speed=0,  # Spells don't move
            cost=4,
            deployment_time=0.5,
            position=position,
            owner=owner
        )
        self.area_of_effect = 2.0  # Affects tiles within 2 tile radius
        self.is_deployed = True  # Spells deploy immediately
        self.has_exploded = False
    
    def get_card_type(self) -> str:
        return "spell"
    
    def update(self, dt: float):
        """Override update for spell behavior"""
        if not self.has_exploded and self.is_deployed:
            self.explode()
            self.health = 0  # Remove spell after explosion
    
    def explode(self):
        """Trigger the fireball explosion"""
        self.has_exploded = True
        # The actual damage application will be handled by the game state
        # This method just marks that the spell should trigger
    
    def is_alive(self) -> bool:
        """Spells are considered 'alive' until they explode"""
        return not self.has_exploded

class Lightning(BaseCard):
    """Single target high damage spell"""
    
    def __init__(self, position: Tuple[int, int] = (0, 0), owner: str = "player"):
        super().__init__(
            name="Lightning",
            health=1,
            attack=60,
            speed=0,
            cost=6,
            deployment_time=0.3,
            position=position,
            owner=owner
        )
        self.is_deployed = True
        self.has_struck = False
    
    def get_card_type(self) -> str:
        return "spell"
    
    def update(self, dt: float):
        """Override update for spell behavior"""
        if not self.has_struck and self.is_deployed:
            self.strike()
            self.health = 0  # Remove spell after striking
    
    def strike(self):
        """Trigger the lightning strike"""
        self.has_struck = True
    
    def is_alive(self) -> bool:
        """Spells are considered 'alive' until they strike"""
        return not self.has_struck