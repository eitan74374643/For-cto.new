from typing import List, Optional, Tuple
from cards.base_card import BaseCard

class GameState:
    """Manages the overall game state including cards, resources, and game flow"""
    
    def __init__(self):
        """Initialize the game state"""
        self.cards: List[BaseCard] = []
        self.player_mana = 10
        self.enemy_mana = 10
        self.max_mana = 10
        self.mana_regen_rate = 1.0  # Mana per second
        self.mana_timer = 0.0
        self.grid_size = 8
        self.selected_card_type = "archer"  # Default selected card for placement
        self.game_time = 0.0
        
    def add_card(self, card: BaseCard) -> bool:
        """
        Add a card to the game state
        
        Args:
            card: The card to add
            
        Returns:
            True if card was added successfully, False otherwise
        """
        # Check if position is valid
        if not self._is_valid_position(card.get_position()):
            return False
        
        # Check if player has enough mana
        if card.owner == "player" and self.player_mana < card.cost:
            return False
        
        # Deduct mana cost
        if card.owner == "player":
            self.player_mana -= card.cost
        else:
            self.enemy_mana -= card.cost
        
        self.cards.append(card)
        return True
    
    def remove_card(self, card: BaseCard):
        """Remove a card from the game state"""
        if card in self.cards:
            self.cards.remove(card)
    
    def get_all_cards(self) -> List[BaseCard]:
        """Get all cards in the game"""
        return self.cards
    
    def get_player_cards(self) -> List[BaseCard]:
        """Get all player-owned cards"""
        return [card for card in self.cards if card.owner == "player"]
    
    def get_enemy_cards(self) -> List[BaseCard]:
        """Get all enemy-owned cards"""
        return [card for card in self.cards if card.owner == "enemy"]
    
    def get_cards_at_position(self, x: int, y: int) -> List[BaseCard]:
        """Get all cards at a specific grid position"""
        return [card for card in self.cards if card.get_position() == (x, y)]
    
    def get_alive_cards(self) -> List[BaseCard]:
        """Get all cards that are still alive"""
        return [card for card in self.cards if card.is_alive()]
    
    def update(self, dt: float):
        """Update the game state"""
        self.game_time += dt
        
        # Update mana regeneration
        self._update_mana(dt)
        
        # Update all cards
        for card in self.cards[:]:  # Use slice to avoid modification during iteration
            card.update(dt)
            
            # Remove dead cards
            if not card.is_alive():
                self.remove_card(card)
        
        # Handle combat between cards
        self._handle_combat()
    
    def _update_mana(self, dt: float):
        """Update mana regeneration"""
        self.mana_timer += dt
        if self.mana_timer >= 1.0:  # Regenerate every second
            self.mana_timer = 0.0
            
            # Regenerate player mana
            if self.player_mana < self.max_mana:
                self.player_mana = min(self.player_mana + self.mana_regen_rate, self.max_mana)
            
            # Regenerate enemy mana
            if self.enemy_mana < self.max_mana:
                self.enemy_mana = min(self.enemy_mana + self.mana_regen_rate, self.max_mana)
    
    def _handle_combat(self):
        """Handle combat between cards"""
        alive_cards = self.get_alive_cards()
        
        for attacker in alive_cards:
            if attacker.get_card_type() == "spell":
                continue  # Spells handle their own effects
            
            # Find targets for attacking cards
            if attacker.can_attack() and attacker.attack > 0:
                targets = self._get_targets_in_range(attacker)
                if targets:
                    # Attack the closest target
                    closest_target = min(targets, key=lambda t: self._get_distance(attacker, t))
                    attacker.attack_target(closest_target)
    
    def _get_targets_in_range(self, attacker: BaseCard) -> List[BaseCard]:
        """Get all valid targets in range of an attacker"""
        targets = []
        for card in self.get_alive_cards():
            # Don't target self or allies
            if card.owner == attacker.owner:
                continue
            
            # Check if target is in range
            if attacker._is_in_range(card):
                targets.append(card)
        
        return targets
    
    def _get_distance(self, card1: BaseCard, card2: BaseCard) -> float:
        """Calculate distance between two cards"""
        import math
        dx = card1.position[0] - card2.position[0]
        dy = card1.position[1] - card2.position[1]
        return math.sqrt(dx * dx + dy * dy)
    
    def _is_valid_position(self, position: Tuple[int, int]) -> bool:
        """Check if a position is valid on the grid"""
        x, y = position
        return 0 <= x < self.grid_size and 0 <= y < self.grid_size
    
    def can_afford_card(self, card_type: str, owner: str = "player") -> bool:
        """Check if a player can afford a specific card type"""
        # This would need to be connected to the card factory
        # For now, return True as a placeholder
        return True
    
    def get_game_status(self) -> dict:
        """Get current game status information"""
        return {
            "player_mana": self.player_mana,
            "enemy_mana": self.enemy_mana,
            "total_cards": len(self.cards),
            "player_cards": len(self.get_player_cards()),
            "enemy_cards": len(self.get_enemy_cards()),
            "game_time": self.game_time
        }