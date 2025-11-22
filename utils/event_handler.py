import pygame
from typing import Optional
from cards.card_factory import CardFactory

class EventHandler:
    """Handles all game events and user input"""
    
    def __init__(self, game_state):
        """
        Initialize the event handler
        
        Args:
            game_state: The game state object to manipulate
        """
        self.game_state = game_state
        self.card_factory = CardFactory()
        self.selected_card_type = "archer"
        self.is_placing_card = False
        
        # Key bindings for card selection
        self.card_keys = {
            pygame.K_1: "archer",
            pygame.K_2: "knight", 
            pygame.K_3: "goblin",
            pygame.K_4: "fireball",
            pygame.K_5: "lightning",
            pygame.K_6: "tower",
            pygame.K_7: "wall"
        }
    
    def handle_event(self, event):
        """
        Handle a pygame event
        
        Args:
            event: The pygame event to handle
        """
        if event.type == pygame.KEYDOWN:
            self._handle_key_press(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_click(event.pos, event.button)
        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event.pos)
    
    def _handle_key_press(self, key):
        """Handle keyboard input"""
        # Card selection with number keys
        if key in self.card_keys:
            self.selected_card_type = self.card_keys[key]
            print(f"Selected card type: {self.selected_card_type}")
        
        # Toggle card placement mode with space
        elif key == pygame.K_SPACE:
            self.is_placing_card = not self.is_placing_card
            print(f"Card placement mode: {'ON' if self.is_placing_card else 'OFF'}")
        
        # Exit game with Escape
        elif key == pygame.K_ESCAPE:
            pygame.quit()
    
    def _handle_mouse_click(self, pos, button):
        """Handle mouse clicks"""
        if button == 1:  # Left click
            grid_pos = self._screen_to_grid(pos)
            if grid_pos and self.is_placing_card:
                self._place_card(grid_pos)
        elif button == 3:  # Right click
            # Cancel card placement
            self.is_placing_card = False
    
    def _handle_mouse_motion(self, pos):
        """Handle mouse movement"""
        # Could be used for hover effects or preview
        pass
    
    def _place_card(self, grid_pos):
        """Place a card at the specified grid position"""
        x, y = grid_pos
        
        # Check if position is already occupied
        existing_cards = self.game_state.get_cards_at_position(x, y)
        if existing_cards:
            print(f"Position ({x}, {y}) is already occupied!")
            return
        
        # Create and try to add the card
        card = self.card_factory.create_card(
            self.selected_card_type, 
            position=grid_pos,
            owner="player"
        )
        
        if card:
            # Check if player can afford it
            if self.game_state.player_mana >= card.cost:
                if self.game_state.add_card(card):
                    print(f"Placed {card.name} at position ({x}, {y})")
                else:
                    print(f"Failed to place {card.name}")
            else:
                print(f"Not enough mana! Need {card.cost}, have {self.game_state.player_mana}")
        else:
            print(f"Unknown card type: {self.selected_card_type}")
    
    def _screen_to_grid(self, pos) -> Optional[tuple]:
        """Convert screen coordinates to grid coordinates"""
        x, y = pos
        tile_size = 500 // self.game_state.grid_size  # 500 is screen width from main.py
        
        grid_x = x // tile_size
        grid_y = y // tile_size
        
        # Check if within grid bounds
        if 0 <= grid_x < self.game_state.grid_size and 0 <= grid_y < self.game_state.grid_size:
            return (grid_x, grid_y)
        
        return None
    
    def get_selected_card_info(self):
        """Get information about the currently selected card type"""
        return self.card_factory.get_card_info(self.selected_card_type)
    
    def get_available_cards(self):
        """Get list of available card types"""
        return self.card_factory.get_available_cards()