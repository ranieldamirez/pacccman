# STRATEGY PATTERN
import random
import heapq  # For priority queue

class MovementStrategy:
    def move(self, ghost, maze, player):
        """
        Defines how the ghost moves.
        :param ghost: The Enemy instance (ghost).
        :param maze: The Maze instance.
        :param player: The Player instance.
        """
        raise NotImplementedError("Subclasses must implement the move() method")

class RandomMovement(MovementStrategy):
    def move(self, ghost, maze, player):
        ghost.timer_counter += 1
        if ghost.timer_counter >= ghost.direction_timer:
            # Change direction after the timer expires
            ghost.current_direction = random.choice(["x", "y"])
            ghost.current_step = random.choice([-ghost.speed, ghost.speed])
            ghost.timer_counter = 0

        if ghost.current_direction == "x":
            ghost.rect.x += ghost.current_step
            if ghost.check_wall_or_restricted_cell(maze):
                ghost.rect.x -= ghost.current_step
                ghost.timer_counter = ghost.direction_timer  # Force direction change
        elif ghost.current_direction == "y":
            ghost.rect.y += ghost.current_step
            if ghost.check_wall_or_restricted_cell(maze):
                ghost.rect.y -= ghost.current_step
                ghost.timer_counter = ghost.direction_timer  # Force direction change

class ChaseMovement(MovementStrategy):
    def __init__(self):
        self.path = []  # List of (x, y) grid positions to follow
        self.target_cell = None  # The current target cell on the path

    def move(self, ghost, maze, player):
        # Recalculate the path if necessary
        ghost.timer_counter += 1
        if ghost.timer_counter >= ghost.direction_timer or not self.path:
            self.path = self._calculate_path(ghost, player, maze)
            ghost.timer_counter = 0  # Reset the timer

        # Follow the path if it exists
        if self.path:
            if not self.target_cell:  # Get the next cell if no target is set
                self.target_cell = self.path.pop(0)

            # Move toward the target cell
            self._move_toward_target(ghost)

    def _move_toward_target(self, ghost):
        """Move the ghost toward the target cell."""
        target_x, target_y = self.target_cell

        # Gradually move toward the target cell
        if ghost.rect.centerx < target_x:
            ghost.rect.x += ghost.speed
        elif ghost.rect.centerx > target_x:
            ghost.rect.x -= ghost.speed

        if ghost.rect.centery < target_y:
            ghost.rect.y += ghost.speed
        elif ghost.rect.centery > target_y:
            ghost.rect.y -= ghost.speed

        # Check if the ghost is aligned with the target cell
        if abs(ghost.rect.centerx - target_x) <= ghost.speed and abs(ghost.rect.centery - target_y) <= ghost.speed:
            # Snap to the target cell to ensure precise alignment
            ghost.rect.centerx = target_x
            ghost.rect.centery = target_y

            # Set the next target cell or finish the path
            self.target_cell = None if not self.path else self.path.pop(0)

    def _calculate_path(self, ghost, player, maze):
        """A* algorithm to find the shortest path to the player."""
        start = (ghost.rect.centerx // maze.cell_size, ghost.rect.centery // maze.cell_size)
        goal = (player.rect.centerx // maze.cell_size, player.rect.centery // maze.cell_size)

        # Priority queue for A*
        open_set = []
        heapq.heappush(open_set, (0, start))  # (priority, cell)

        came_from = {}  # Track the best path
        g_score = {start: 0}  # Cost from start to the current cell
        f_score = {start: self._heuristic(start, goal)}  # Estimated cost from start to goal

        while open_set:
            _, current = heapq.heappop(open_set)

            # If we reach the goal, reconstruct the path
            if current == goal:
                return self._reconstruct_path(came_from, current, maze.cell_size)

            # Explore neighbors
            for neighbor in self._get_neighbors(current, maze):
                tentative_g_score = g_score[current] + 1  # Distance is always 1 in a grid

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    # This path is better
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self._heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        # If no path is found, return an empty list
        return []

    def _heuristic(self, cell, goal):
        """Heuristic function for A* (Manhattan distance)."""
        return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])

    def _get_neighbors(self, cell, maze):
        """Get walkable neighbors of a cell."""
        x, y = cell
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Left, Right, Up, Down
            nx, ny = x + dx, y + dy
            # Check bounds and walkable cells
            if 0 <= ny < len(maze.layout) and 0 <= nx < len(maze.layout[ny]) and maze.layout[ny][nx] != 1:
                neighbors.append((nx, ny))
        return neighbors

    def _reconstruct_path(self, came_from, current, cell_size):
        """Reconstruct the path from the came_from map."""
        path = []
        while current in came_from:
            x, y = current
            path.append((x * cell_size + cell_size // 2, y * cell_size + cell_size // 2))  # Convert to pixel positions
            current = came_from[current]
        path.reverse()  # Reverse to get the path from start to goal
        return path