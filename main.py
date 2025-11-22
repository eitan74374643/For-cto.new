import pygame
import sys
from cards.base_card import BaseCard
from cards.card_factory import CardFactory
from utils.game_state import GameState
from utils.event_handler import EventHandler

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
FPS = 60
GRID_SIZE = 8
TILE_SIZE = SCREEN_WIDTH // GRID_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

class Game:
    def __init__(self):
        """Initialize the game with core components"""
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Card Battle Game")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state management
        self.game_state = GameState()
        self.event_handler = EventHandler(self.game_state)
        self.card_factory = CardFactory()
        
        # Font for UI
        self.font = pygame.font.Font(None, 24)
        
    def handle_events(self):
        """Process all game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                self.event_handler.handle_event(event)
    
    def update(self, dt):
        """Update game logic"""
        self.game_state.update(dt)
    
    def draw_grid(self):
        """Draw the game board grid"""
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.screen, GRAY, rect, 1)
    
    def draw_cards(self):
        """Draw all cards on the board"""
        for card in self.game_state.get_all_cards():
            if card.is_alive():
                # Draw card as a colored rectangle
                color = BLUE if card.owner == "player" else RED
                rect = pygame.Rect(
                    card.position[0] * TILE_SIZE + 5,
                    card.position[1] * TILE_SIZE + 5,
                    TILE_SIZE - 10,
                    TILE_SIZE - 10
                )
                pygame.draw.rect(self.screen, color, rect)
                
                # Draw health bar
                health_percent = card.health / card.max_health
                health_bar_width = (TILE_SIZE - 10) * health_percent
                health_bar = pygame.Rect(
                    card.position[0] * TILE_SIZE + 5,
                    card.position[1] * TILE_SIZE + TILE_SIZE - 15,
                    health_bar_width,
                    5
                )
                pygame.draw.rect(self.screen, GREEN, health_bar)
    
    def draw_ui(self):
        """Draw UI elements"""
        # Draw mana counter
        mana_text = self.font.render(f"Mana: {self.game_state.player_mana}", True, BLACK)
        self.screen.blit(mana_text, (10, 10))
        
        # Draw FPS
        fps_text = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, BLACK)
        self.screen.blit(fps_text, (SCREEN_WIDTH - 80, 10))
    
    def draw(self):
        """Main drawing function"""
        self.screen.fill(WHITE)
        self.draw_grid()
        self.draw_cards()
        self.draw_ui()
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Convert to seconds
            
            self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()
        sys.exit()

def main():
    """Entry point for the game"""
    game = Game()
    game.run()

if __name__ == "__main__":
    main()