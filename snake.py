import pygame
import random
import sys

# --- Constants ---
WINDOW_W, WINDOW_H = 640, 480
CELL = 20
COLS = WINDOW_W // CELL
ROWS = WINDOW_H // CELL

BASE_FPS = 8
FPS_PER_POINT = 0.4   # speed increase per point scored
MAX_FPS = 30

BG        = (15,  15,  15)
GRID      = (30,  30,  30)
SNAKE_H   = (80,  200,  80)   # head
SNAKE_B   = (50,  160,  50)   # body
FOOD_C    = (220,  60,  60)
TEXT_C    = (230, 230, 230)
SCORE_C   = (120, 220, 120)
OVER_BG   = (0,   0,   0)

UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = (1,  0)
OPPOSITES = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}


def new_food(snake):
    occupied = set(snake)
    while True:
        pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
        if pos not in occupied:
            return pos


def draw_grid(surface):
    for x in range(0, WINDOW_W, CELL):
        pygame.draw.line(surface, GRID, (x, 0), (x, WINDOW_H))
    for y in range(0, WINDOW_H, CELL):
        pygame.draw.line(surface, GRID, (0, y), (WINDOW_W, y))


def draw_cell(surface, pos, color, shrink=0):
    r = pygame.Rect(pos[0] * CELL + shrink, pos[1] * CELL + shrink,
                    CELL - shrink * 2, CELL - shrink * 2)
    pygame.draw.rect(surface, color, r, border_radius=4)


def draw_snake(surface, snake):
    for i, seg in enumerate(snake):
        color = SNAKE_H if i == 0 else SNAKE_B
        shrink = 1 if i == 0 else 3
        draw_cell(surface, seg, color, shrink)


def draw_food(surface, food, tick):
    # Subtle pulse: radius oscillates slightly
    pulse = abs((tick % 30) - 15) / 15  # 0..1
    shrink = int(2 + pulse * 3)
    draw_cell(surface, food, FOOD_C, shrink)


def current_fps(score):
    return min(BASE_FPS + score * FPS_PER_POINT, MAX_FPS)


def show_start_screen(screen, clock, font_big, font_score, font_small):
    """Animated start screen. Returns 'start' or 'quit'."""
    # Build a demo snake that slowly slithers across the background
    demo_snake = [(COLS // 2 + i, ROWS // 2) for i in range(6, -1, -1)]
    demo_dir = RIGHT
    demo_food = (COLS // 2 + 10, ROWS // 2 - 3)
    tick = 0

    CONTROLS = [
        ("UP",    "Move up"),
        ("DOWN",  "Move down"),
        ("LEFT",  "Move left"),
        ("RIGHT", "Move right"),
    ]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    return "start"
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    return "quit"

        # Animate demo snake (moves every 8 ticks)
        if tick % 8 == 0:
            head = (demo_snake[0][0] + demo_dir[0], demo_snake[0][1] + demo_dir[1])
            # Bounce off edges
            if not (0 <= head[0] < COLS and 0 <= head[1] < ROWS):
                demo_dir = (demo_dir[0] * -1, demo_dir[1] * -1)
                head = (demo_snake[0][0] + demo_dir[0], demo_snake[0][1] + demo_dir[1])
            demo_snake.insert(0, head)
            demo_snake.pop()

        # --- Draw ---
        screen.fill(BG)
        draw_grid(screen)
        draw_food(screen, demo_food, tick)
        draw_snake(screen, demo_snake)

        # Dim overlay so text is readable
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))

        cx = WINDOW_W // 2
        cy = WINDOW_H // 2

        # Title with a gentle vertical bob
        bob = int(4 * abs((tick % 60) / 30 - 1))
        title = font_big.render("SNAKE", True, SNAKE_H)
        screen.blit(title, title.get_rect(center=(cx, cy - 110 + bob)))

        # Blinking "press to start"
        if (tick // 20) % 2 == 0:
            start_surf = font_score.render("Press  SPACE  to start", True, (200, 200, 200))
            screen.blit(start_surf, start_surf.get_rect(center=(cx, cy - 40)))

        # Divider
        pygame.draw.line(screen, (60, 60, 60), (cx - 120, cy - 10), (cx + 120, cy - 10), 1)

        # Controls list
        label = font_small.render("CONTROLS", True, (100, 100, 100))
        screen.blit(label, label.get_rect(center=(cx, cy + 15)))
        for i, (key, action) in enumerate(CONTROLS):
            line = font_small.render(f"{key:<6}  {action}", True, (160, 160, 160))
            screen.blit(line, line.get_rect(center=(cx, cy + 40 + i * 22)))

        quit_hint = font_small.render("Q  to quit", True, (80, 80, 80))
        screen.blit(quit_hint, quit_hint.get_rect(center=(cx, cy + 160)))

        pygame.display.flip()
        tick += 1
        clock.tick(30)


def run_game(screen, clock, font_score, font_big, font_small):
    """Run one game session. Returns when the player quits or restarts."""
    # Initial snake: 3 segments, heading right
    snake = [(COLS // 2, ROWS // 2),
             (COLS // 2 - 1, ROWS // 2),
             (COLS // 2 - 2, ROWS // 2)]
    direction = RIGHT
    next_dir = RIGHT
    food = new_food(snake)
    score = 0
    tick = 0
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        return "restart"
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        return "quit"
                else:
                    if event.key == pygame.K_UP    and direction != DOWN:
                        next_dir = UP
                    elif event.key == pygame.K_DOWN  and direction != UP:
                        next_dir = DOWN
                    elif event.key == pygame.K_LEFT  and direction != RIGHT:
                        next_dir = LEFT
                    elif event.key == pygame.K_RIGHT and direction != LEFT:
                        next_dir = RIGHT

        if not game_over:
            direction = next_dir
            head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

            # Wall collision
            if not (0 <= head[0] < COLS and 0 <= head[1] < ROWS):
                game_over = True
            # Self collision
            elif head in snake:
                game_over = True
            else:
                snake.insert(0, head)
                if head == food:
                    score += 1
                    food = new_food(snake)
                else:
                    snake.pop()

        # --- Draw ---
        screen.fill(BG)
        draw_grid(screen)
        draw_food(screen, food, tick)
        draw_snake(screen, snake)

        # Score HUD
        score_surf = font_score.render(f"Score: {score}", True, SCORE_C)
        screen.blit(score_surf, (10, 8))

        fps_surf = font_small.render(
            f"Speed: {current_fps(score):.0f}", True, (90, 90, 90))
        screen.blit(fps_surf, (WINDOW_W - fps_surf.get_width() - 10, 10))

        if game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            screen.blit(overlay, (0, 0))

            title_surf = font_big.render("GAME OVER", True, (220, 60, 60))
            score_big  = font_big.render(f"Score: {score}", True, TEXT_C)
            restart    = font_score.render("Press  R  to restart", True, (150, 220, 150))
            quit_hint  = font_score.render("Press  Q  to quit", True, (180, 180, 180))

            cx = WINDOW_W // 2
            cy = WINDOW_H // 2
            screen.blit(title_surf,  title_surf.get_rect(center=(cx, cy - 70)))
            screen.blit(score_big,   score_big.get_rect(center=(cx, cy - 10)))
            screen.blit(restart,     restart.get_rect(center=(cx, cy + 50)))
            screen.blit(quit_hint,   quit_hint.get_rect(center=(cx, cy + 90)))

        pygame.display.flip()
        tick += 1
        clock.tick(current_fps(score) if not game_over else 30)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()

    font_big   = pygame.font.SysFont("monospace", 48, bold=True)
    font_score = pygame.font.SysFont("monospace", 24)
    font_small = pygame.font.SysFont("monospace", 16)

    while True:
        action = show_start_screen(screen, clock, font_big, font_score, font_small)
        if action == "quit":
            break
        result = run_game(screen, clock, font_score, font_big, font_small)
        if result == "quit":
            break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
