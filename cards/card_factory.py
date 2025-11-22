from .base_card import BaseCard
from typing import Dict, Type, Optional

class CardFactory:
    """Factory class for creating different types of cards"""
    
    def __init__(self):
        """Initialize the card factory with available card types"""
        self._card_registry: Dict[str, Type[BaseCard]] = {}
        self._register_default_cards()
    
    def _register_default_cards(self):
        """Register default card types"""
        # Import card classes here to avoid circular imports
        from .unit_cards import Archer, Knight, Goblin
        from .spell_cards import Fireball, Lightning
        from .building_cards import Tower, Wall
        
        # Register unit cards
        self.register_card("archer", Archer)
        self.register_card("knight", Knight)
        self.register_card("goblin", Goblin)
        
        # Register spell cards
        self.register_card("fireball", Fireball)
        self.register_card("lightning", Lightning)
        
        # Register building cards
        self.register_card("tower", Tower)
        self.register_card("wall", Wall)
    
    def register_card(self, card_type: str, card_class: Type[BaseCard]):
        """Register a new card type"""
        self._card_registry[card_type.lower()] = card_class
    
    def create_card(self, card_type: str, position: tuple = (0, 0), owner: str = "player") -> Optional[BaseCard]:
        """
        Create a card instance
        
        Args:
            card_type: Type of card to create
            position: Grid position to place the card
            owner: Who owns this card ("player" or "enemy")
            
        Returns:
            BaseCard instance or None if card type not found
        """
        card_type = card_type.lower()
        if card_type not in self._card_registry:
            print(f"Unknown card type: {card_type}")
            return None
        
        card_class = self._card_registry[card_type]
        return card_class(position=position, owner=owner)
    
    def get_available_cards(self) -> list:
        """Get list of available card types"""
        return list(self._card_registry.keys())
    
    def get_card_info(self, card_type: str) -> Optional[dict]:
        """Get information about a specific card type"""
        card_type = card_type.lower()
        if card_type not in self._card_registry:
            return None
        
        # Create a temporary instance to get stats
        temp_card = self.create_card(card_type)
        if temp_card:
            return {
                "name": temp_card.name,
                "type": temp_card.get_card_type(),
                "health": temp_card.max_health,
                "attack": temp_card.attack,
                "speed": temp_card.speed,
                "cost": temp_card.cost,
                "deployment_time": temp_card.deployment_time
            }
        return None