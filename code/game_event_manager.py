import pygame


class GameEventManager:
    def __init__(self):
        pass

    def check_collision(self, player, ghosts):
        """
        Check if the player collides with any ghost.
        """
        for ghost in ghosts:
            if player.rect.colliderect(ghost.rect):
                if ghost.is_frightened:  # Handle frightened state
                    ghost.reset_to_start()  # Reset ghost to its starting position
                    return "ghost_captured"
                return "player_hit"
        return "no_collision"

    def check_pellet_collection(self, player, maze):
        """
        Check if the player collects a pellet.
        """
        for pellet in maze.pellets:
            if player.rect.colliderect(pellet.rect):
                maze.pellets.remove(pellet)  # Remove pellet from the maze
                return "pellet_collected"
        return None

    def check_power_up(self, player, maze):
        """
        Check if the player collects a power-up.
        """
        for power_up in maze.power_ups:
            if player.rect.colliderect(power_up.rect):
                maze.power_ups.remove(power_up)  # Remove power-up from the maze
                return "power_up_collected"
        return None

    def check_game_win(self, maze):
        """
        Check if all pellets are collected (win condition).
        """
        return len(maze.pellets) == 0
