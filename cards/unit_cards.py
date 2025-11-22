from .base_card import BaseCard
from typing import Tuple

class Archer(BaseCard):
    """Fast ranged unit with moderate damage"""
    
    def __init__(self, position: Tuple[int, int] = (0, 0), owner: str = "player"):
        super().__init__(
            name="Archer",
            health=50,
            attack=15,
            speed=2.0,
            cost=3,
            deployment_time=1.0,
            position=position,
            owner=owner
        )
        self.attack_range = 3.0  # Can attack from 3 tiles away
    
    def get_card_type(self) -> str:
        return "unit"

class Knight(BaseCard):
    """Slow but heavily armored melee unit"""
    
    def __init__(self, position: Tuple[int, int] = (0, 0), owner: str = "player"):
        super().__init__(
            name="Knight",
            health=120,
            attack=25,
            speed=0.8,
            cost=5,
            deployment_time=2.0,
            position=position,
            owner=owner
        )
        self.attack_range = 1.0  # Melee range
    
    def get_card_type(self) -> str:
        return "unit"

class Goblin(BaseCard):
    """Very fast but weak melee unit"""
    
    def __init__(self, position: Tuple[int, int] = (0, 0), owner: str = "player"):
        super().__init__(
            name="Goblin",
            health=30,
            attack=10,
            speed=3.5,
            cost=1,
            deployment_time=0.5,
            position=position,
            owner=owner
        )
        self.attack_range = 1.0  # Melee range
    
    def get_card_type(self) -> str:
        return "unit"