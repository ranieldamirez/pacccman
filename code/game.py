import pygame
from player import Player
from enemy import Enemy
from maze import Maze
from score_manager import ScoreManager
from game_event_manager import GameEventManager
import sys

pygame.init()

# Screen configuration
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
cell_size = 25
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

# Fonts
title_font = pygame.font.Font(None, 100)
text_font = pygame.font.Font(None, 36)
small_text_font = pygame.font.Font(None, 28)

# Load the PAAAC-MAN image
try:
    paaacman_image = pygame.image.load("./resources/PAAAC.jpg")
    paaacman_image = pygame.transform.scale(paaacman_image, (100, 100))
except pygame.error:
    print("ERROR: UNABLE TO LOAD THE IMAGE")
    sys.exit()

class GameEngine:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("PACCC-MAN Arcade Game")
        self.clock = pygame.time.Clock()

        # Initializing game elements
        self.map = Maze(SCREEN_WIDTH, SCREEN_HEIGHT, cell_size)
        self.player = Player(cell_size, self.map, lives=3)
        self.ghosts = [Enemy(cell_size, self.map) for _ in range(4)]
        self.score_manager = ScoreManager()
        self.event_manager = GameEventManager()

        self.running = True
        self.state = "start_menu"
        self.ghost_speed = 5

    def start_menu(self):
        # Display start menu
        self.screen.fill(BLACK)
        title_text = title_font.render("PACCC-MAN", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 4))
        self.screen.blit(title_text, title_rect)

        image_x = title_rect.right + 20
        image_y = title_rect.centery - paaacman_image.get_height() // 2
        self.screen.blit(paaacman_image, (image_x, image_y))

        high_scores = self.score_manager.getInstance().get_high_scores()
        for i, (username, score) in enumerate(high_scores):
            score_text = text_font.render(f"{i + 1}. {username}: {score}", True, WHITE)
            self.screen.blit(score_text, (self.screen.get_width() // 3, (self.screen.get_height() // 2) + i * 40))

        credits_text = small_text_font.render("© 2024 CPSC 6119 Team 4", True, WHITE)
        self.screen.blit(credits_text, (SCREEN_WIDTH // 2 - credits_text.get_width() // 2, SCREEN_HEIGHT - 50))

        prompt = text_font.render("Press any key to start", True, WHITE)
        self.screen.blit(prompt, (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2 - 50))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                self.state = "playing"
            elif event.type == pygame.QUIT:
                self.running = False

    def game_over_screen(self):
        self.screen.fill(BLACK)
        
        # Render "Game Over" message
        game_over_text = title_font.render("Game Over", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(game_over_text, text_rect)

        # Display score when the game is over
        score_text = text_font.render(f"Score: {self.score_manager.get_current_score()}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)

        pygame.display.flip()
        pygame.time.wait(3000)  # Wait for 3 seconds before quitting
        self.running = False

    def main_game(self):
        self.screen.fill(BLACK)
        self.map.draw(self.screen)
        self.player.update(self.map)
        self.player.collect_pellet(self.map)
        self.player.draw(self.screen)

        for ghost in self.ghosts:
            if pygame.time.get_ticks() % self.ghost_speed == 0:
                ghost.update(self.map, self.player)
            ghost.draw(self.screen)

        # Get score from the score manager
        score_text = text_font.render(f"Score: {self.score_manager.get_current_score()}", True, WHITE)
        lives_text = text_font.render(f"Lives: {self.player.lives}", True, WHITE)
        
        # Display score and lives
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 50))

        # Check for collisions with ghosts
        if self.player.collides_with_ghost(self.ghosts, pygame.time.get_ticks()):
            if self.player.lives > 0:
                self.player.lives -= 1  # Decrease the player's life
                self.player.reset_position(self.map)  # Reset player's position (respawn)
            else:
                self.game_over_screen()

        # Check if all pellets are collected
        if self.map.all_pellets_collected():
            self.state = "game_over"

        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if self.state == "playing" and event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    self.state = "paused"

            if self.state == "start_menu":
                self.start_menu()
            elif self.state == "playing":
                self.main_game()
            elif self.state == "paused":
                self.pause_screen()
            elif self.state == "game_over":
                self.game_over_screen()

            self.clock.tick(FPS)

if __name__ == "__main__":
    game = GameEngine()
    game.run()
