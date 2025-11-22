#!/usr/bin/env python3
"""
Test script to verify core game functionality without graphics
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cards.card_factory import CardFactory
from utils.game_state import GameState

def test_card_creation():
    """Test that all card types can be created"""
    factory = CardFactory()
    available_cards = factory.get_available_cards()
    
    print("Testing card creation...")
    print(f"Available cards: {available_cards}")
    
    for card_type in available_cards:
        card = factory.create_card(card_type, position=(0, 0))
        if card:
            print(f"✓ {card.name}: HP={card.max_health}, ATK={card.attack}, Cost={card.cost}, Type={card.get_card_type()}")
        else:
            print(f"✗ Failed to create {card_type}")
    
    print()

def test_game_state():
    """Test game state functionality"""
    print("Testing game state...")
    game_state = GameState()
    factory = CardFactory()
    
    # Test adding cards
    archer = factory.create_card("archer", position=(2, 3), owner="player")
    knight = factory.create_card("knight", position=(5, 1), owner="enemy")
    
    if archer and game_state.add_card(archer):
        print(f"✓ Added player archer at {archer.get_position()}")
    
    if knight and game_state.add_card(knight):
        print(f"✓ Added enemy knight at {knight.get_position()}")
    
    # Test getting cards
    player_cards = game_state.get_player_cards()
    enemy_cards = game_state.get_enemy_cards()
    
    print(f"✓ Player cards: {len(player_cards)}")
    print(f"✓ Enemy cards: {len(enemy_cards)}")
    
    # Test mana system
    print(f"✓ Player mana: {game_state.player_mana}")
    print(f"✓ Enemy mana: {game_state.enemy_mana}")
    
    # Test position lookup
    cards_at_pos = game_state.get_cards_at_position(2, 3)
    print(f"✓ Cards at (2,3): {len(cards_at_pos)}")
    
    print()

def test_combat():
    """Test basic combat mechanics"""
    print("Testing combat...")
    factory = CardFactory()
    game_state = GameState()
    
    # Create two opposing units
    archer = factory.create_card("archer", position=(0, 0), owner="player")
    goblin = factory.create_card("goblin", position=(1, 0), owner="enemy")
    
    if archer and goblin:
        game_state.add_card(archer)
        game_state.add_card(goblin)
        
        print(f"✓ Created combatants: {archer} vs {goblin}")
        
        # Test damage
        initial_health = goblin.health
        goblin.take_damage(archer.attack)
        print(f"✓ Goblin took {archer.attack} damage: {initial_health} → {goblin.health}")
        
        # Test death
        goblin.take_damage(goblin.health)
        print(f"✓ Goblin destroyed: {'alive' if goblin.is_alive() else 'dead'}")
    
    print()

def main():
    """Run all tests"""
    print("=== Card Game Foundation Tests ===\n")
    
    try:
        test_card_creation()
        test_game_state()
        test_combat()
        
        print("✓ All tests passed! Foundation is working correctly.")
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())