import pygame

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("4-Point Fill Paint App")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Grid properties
GRID_SIZE = 8
CELL_SIZE = 50
RECT_X, RECT_Y = 200, 150
RECT_WIDTH = GRID_SIZE * CELL_SIZE
RECT_HEIGHT = GRID_SIZE * CELL_SIZE

# Create a 2D grid to keep track of filled cells (0 = white, 1 = blue, -1 = border)
grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Add borders (for demo, let's border the grid edges)
for i in range(GRID_SIZE):
    grid[0][i] = -1
    grid[GRID_SIZE-1][i] = -1
    grid[i][0] = -1
    grid[i][GRID_SIZE-1] = -1

def four_point_fill(grid, x, y, target, replacement):
    if target == replacement:
        return

    stack = [(x, y)]

    while stack:
        cx, cy = stack.pop()

        if cx < 0 or cx >= GRID_SIZE or cy < 0 or cy >= GRID_SIZE:
            continue

        if grid[cy][cx] != target:
            continue

        grid[cy][cx] = replacement

        # Push neighbors (4-directional)
        stack.append((cx+1, cy))
        stack.append((cx-1, cy))
        stack.append((cx, cy+1))
        stack.append((cx, cy-1))

def draw_grid():
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            rect = pygame.Rect(RECT_X + x * CELL_SIZE, RECT_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if grid[y][x] == 1:
                color = BLUE
            elif grid[y][x] == -1:
                color = BLACK
            else:
                color = WHITE
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)  # Grid lines

def main():
    running = True
    clock = pygame.time.Clock()

    while running:
        screen.fill(WHITE)
        draw_grid()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if (RECT_X <= x < RECT_X + RECT_WIDTH and 
                    RECT_Y <= y < RECT_Y + RECT_HEIGHT):
                    grid_x = (x - RECT_X) // CELL_SIZE
                    grid_y = (y - RECT_Y) // CELL_SIZE

                    if grid[grid_y][grid_x] == 0:  # Only fill if white
                        four_point_fill(grid, grid_x, grid_y, 0, 1)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
