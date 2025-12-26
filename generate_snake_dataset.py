import argparse
import json
import random
from datetime import datetime
from string import Template


PYGAME_SNAKE_TEMPLATE = Template(
    r'''"""
Snake Game (pygame) - Variation: $variant_id

Controls:
- $up_key/$down_key/$left_key/$right_key: move
- P: pause
- R: restart after game over
- ESC: quit
"""

import sys
import random
import pygame


# -----------------------------
# Configuration
# -----------------------------
CELL_SIZE = $cell_size
GRID_W = $grid_w
GRID_H = $grid_h
FPS = $fps

WRAP_EDGES = $wrap_edges
SHOW_GRID = $show_grid
ADD_OBSTACLES = $add_obstacles
OBSTACLE_COUNT = $obstacle_count

WINDOW_W = GRID_W * CELL_SIZE
WINDOW_H = GRID_H * CELL_SIZE + 60  # HUD bar

BG = $bg
GRID = $grid
SNAKE = $snake
SNAKE_HEAD = $snake_head
FOOD = $food
HUD_BG = $hud_bg
HUD_FG = $hud_fg
OBST = $obst

FONT_NAME = None  # default


# -----------------------------
# Helpers
# -----------------------------
def new_food(snake, obstacles):
    while True:
        p = (random.randrange(GRID_W), random.randrange(GRID_H))
        if p not in snake and p not in obstacles:
            return p


def new_obstacles(snake, count):
    obs = set()
    while len(obs) < count:
        p = (random.randrange(GRID_W), random.randrange(GRID_H))
        if p not in snake:
            obs.add(p)
    return obs


def draw_cell(screen, x, y, color):
    r = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE + 60, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, color, r)


def draw_grid(screen):
    if not SHOW_GRID:
        return
    for x in range(GRID_W):
        px = x * CELL_SIZE
        pygame.draw.line(screen, GRID, (px, 60), (px, WINDOW_H))
    for y in range(GRID_H):
        py = 60 + y * CELL_SIZE
        pygame.draw.line(screen, GRID, (0, py), (WINDOW_W, py))


def step_position(pos, direction):
    x, y = pos
    dx, dy = direction
    nx, ny = x + dx, y + dy
    if WRAP_EDGES:
        nx %= GRID_W
        ny %= GRID_H
    return nx, ny


# -----------------------------
# Main
# -----------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("Snake Coder AI - Snake (Variation $variant_id)")
    clock = pygame.time.Clock()
    font = pygame.font.Font(FONT_NAME, 20)

    def reset():
        snake = [(GRID_W // 2, GRID_H // 2)]
        direction = $initial_dir
        pending_dir = direction
        score = 0
        game_over = False
        paused = False

        obstacles = set()
        if ADD_OBSTACLES and OBSTACLE_COUNT > 0:
            obstacles = new_obstacles(snake, OBSTACLE_COUNT)

        food = new_food(snake, obstacles)
        return snake, direction, pending_dir, food, obstacles, score, game_over, paused

    snake, direction, pending_dir, food, obstacles, score, game_over, paused = reset()

    keymap = {
        pygame.K_$up_key: (0, -1),
        pygame.K_$down_key: (0, 1),
        pygame.K_$left_key: (-1, 0),
        pygame.K_$right_key: (1, 0),
    }

    def is_opposite(a, b):
        return a[0] == -b[0] and a[1] == -b[1]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)

                if event.key == pygame.K_p:
                    if not game_over:
                        paused = not paused

                if event.key == pygame.K_r:
                    if game_over:
                        snake, direction, pending_dir, food, obstacles, score, game_over, paused = reset()

                if event.key in keymap and (not game_over):
                    cand = keymap[event.key]
                    if len(snake) == 1 or not is_opposite(cand, direction):
                        pending_dir = cand

        if not paused and not game_over:
            direction = pending_dir
            head = snake[0]
            new_head = step_position(head, direction)

            if not WRAP_EDGES:
                if new_head[0] < 0 or new_head[0] >= GRID_W or new_head[1] < 0 or new_head[1] >= GRID_H:
                    game_over = True

            if not game_over:
                if new_head in snake:
                    game_over = True
                elif new_head in obstacles:
                    game_over = True
                else:
                    snake.insert(0, new_head)

                    if new_head == food:
                        score += 1
                        food = new_food(snake, obstacles)
                    else:
                        snake.pop()

        # Render
        screen.fill(BG)
        hud = pygame.Rect(0, 0, WINDOW_W, 60)
        pygame.draw.rect(screen, HUD_BG, hud)

        info = f"Score: {score}  |  Wrap: {'ON' if WRAP_EDGES else 'OFF'}  |  Obstacles: {len(obstacles)}"
        if paused:
            info += "  |  PAUSED"
        if game_over:
            info += "  |  GAME OVER (R to restart)"
        text = font.render(info, True, HUD_FG)
        screen.blit(text, (12, 18))

        draw_grid(screen)

        for ox, oy in obstacles:
            draw_cell(screen, ox, oy, OBST)

        draw_cell(screen, food[0], food[1], FOOD)

        for i, (sx, sy) in enumerate(snake):
            c = SNAKE_HEAD if i == 0 else SNAKE
            draw_cell(screen, sx, sy, c)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
'''
)


def rgb():
    return (random.randint(0, 40), random.randint(0, 40), random.randint(0, 40))


def bright():
    return (random.randint(120, 255), random.randint(120, 255), random.randint(120, 255))


def choose_palette():
    bg = rgb()
    grid = (min(255, bg[0] + 20), min(255, bg[1] + 20), min(255, bg[2] + 20))
    snake = bright()
    snake_head = (min(255, snake[0] + 20), min(255, snake[1] + 20), min(255, snake[2] + 20))
    food = (255, random.randint(60, 160), random.randint(60, 160))
    hud_bg = (15, 18, 25)
    hud_fg = (220, 230, 245)
    obst = (random.randint(160, 255), random.randint(80, 140), random.randint(0, 80))
    return bg, grid, snake, snake_head, food, hud_bg, hud_fg, obst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="snake_dataset.jsonl", help="Output JSONL path")
    ap.add_argument("--n", type=int, default=120, help="Number of variations (100+ recommended)")
    ap.add_argument("--seed", type=int, default=1337)
    args = ap.parse_args()

    random.seed(args.seed)

    key_sets = [
        {
            "display": ("W", "S", "A", "D"),
            "pygame": ("w", "s", "a", "d"),
        },
        {
            "display": ("UP", "DOWN", "LEFT", "RIGHT"),
            "pygame": ("UP", "DOWN", "LEFT", "RIGHT"),
        },
        {
            "display": ("I", "K", "J", "L"),
            "pygame": ("i", "k", "j", "l"),
        },
    ]
    initial_dirs = [(1, 0), (0, 1), (-1, 0)]

    seen_prompts = set()

    with open(args.out, "w", encoding="utf-8") as f:
        for i in range(args.n):
            grid_w = random.choice([20, 24, 28, 30])
            grid_h = random.choice([16, 18, 20, 22])
            cell_size = random.choice([18, 20, 22, 24])
            fps = random.choice([10, 12, 14, 16])

            wrap_edges = random.choice([True, False])
            show_grid = random.choice([True, False])
            add_obstacles = random.choice([True, False])
            obstacle_count = random.choice([0, 5, 8, 12]) if add_obstacles else 0

            keyset = random.choice(key_sets)
            (up_disp, down_disp, left_disp, right_disp) = keyset["display"]
            (up_key, down_key, left_key, right_key) = keyset["pygame"]

            initial_dir = random.choice(initial_dirs)

            bg, grid, snake, snake_head, food, hud_bg, hud_fg, obst = choose_palette()

            code = PYGAME_SNAKE_TEMPLATE.substitute(
                variant_id=i + 1,
                cell_size=cell_size,
                grid_w=grid_w,
                grid_h=grid_h,
                fps=fps,
                wrap_edges=str(wrap_edges),
                show_grid=str(show_grid),
                add_obstacles=str(add_obstacles),
                obstacle_count=obstacle_count,
                up_key=up_key,
                down_key=down_key,
                left_key=left_key,
                right_key=right_key,
                initial_dir=str(initial_dir),
                bg=str(bg),
                grid=str(grid),
                snake=str(snake),
                snake_head=str(snake_head),
                food=str(food),
                hud_bg=str(hud_bg),
                hud_fg=str(hud_fg),
                obst=str(obst),
            )

            feature_bits = [
                "pygame snake game",
                f"{grid_w}x{grid_h} grid",
                f"CELL_SIZE={cell_size}",
                f"FPS={fps}",
                "wrap edges" if wrap_edges else "wall collision",
                "grid overlay" if show_grid else "no grid overlay",
            ]
            if add_obstacles and obstacle_count > 0:
                feature_bits.append(f"{obstacle_count} obstacles")

            prompt = (
                "Write a complete, runnable Python Snake game using pygame. "
                f"Requirements: {', '.join(feature_bits)}. "
                f"Controls: {up_disp}/{down_disp}/{left_disp}/{right_disp}. "
                "Include scoring HUD, pause with P, restart with R, and clean structure."
            )
            prompt = f"[Variation {i+1}] {prompt}"

            if prompt in seen_prompts:
                prompt = f"{prompt} (seed={args.seed}, ts={datetime.utcnow().isoformat()})"
            seen_prompts.add(prompt)

            ex = {"prompt": prompt, "response": code}
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"Wrote {args.n} examples to: {args.out}")


if __name__ == "__main__":
    main()
