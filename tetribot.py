#COSC302 Final Project
#TETRIBOT: by Dwight Britton and Sidarth Kumar

import pygame
import random
import copy

#Screen and block dimensions
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
GRID_WIDTH = SCREEN_WIDTH // BLOCK_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE

#Basic color definitions
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)

# defines various color palettes for different visual themes
PALETTES = {
    'Classic':    [(0,255,255),(0,0,255),(255,165,0),(255,255,0),(0,255,0),(128,0,128),(255,50,150)],
    'Pastel':     [(179,236,255),(179,204,255),(255,204,229),(255,255,179),(204,255,204),(229,204,255),(200,120,210)],
    'Dark':       [(0,128,128),(0,0,128),(128,64,0),(128,128,0),(0,128,0),(64,0,64),(128,64,64)],
    'Neon':       [(57,255,20),(255,0,255),(0,255,238),(255,255,0),(255,105,180),(0,255,0),(255,69,0)],
    'Earth':      [(139,69,19),(34,139,34),(160,82,45),(85,107,47),(107,142,35),(210,180,140),(244,164,96)],
    'Monochrome': [(50,50,50),(100,100,100),(150,150,150),(200,200,200),(80,80,80),(120,120,120),(160,160,160)],
    'Sunset':     [(255,94,77),(255,149,128),(255,205,178),(255,255,204),(204,229,255),(153,204,255),(102,178,255)]
}

#sets the initial color theme
current_palette_name = 'Classic'
COLORS = PALETTES[current_palette_name]

#standard shapes of pieces
SHAPE_TEMPLATES = [
    [[1,1,1,1]],
    [[1,0,0],[1,1,1]],
    [[0,0,1],[1,1,1]],
    [[1,1],[1,1]],
    [[0,1,1],[1,1,0]],
    [[0,1,0],[1,1,1]],
    [[1,1,0],[0,1,1]]
]

# Generates all unique rotations of a piece
def get_rotations(matrix):
    rots, curr = [], matrix
    for _ in range(4):
        rots.append(curr)
        curr = [list(r) for r in zip(*curr[::-1])]
    unique = []
    for r in rots:
        if r not in unique:
            unique.append(r)
    return unique

# creates list of all shapes with their possible rotations
SHAPES = [get_rotations(s) for s in SHAPE_TEMPLATES]

# class representing a tetris block
class Block:
    def __init__(self, x, y, rotations):
        self.x, self.y = x, y
        self.rotations = rotations
        self.rotation = 0
        self.color = random.choice(COLORS)

    def image(self):
        return self.rotations[self.rotation % len(self.rotations)]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.rotations)

# makes the game grid, filled with black and locked positions
def create_grid(locked):
    grid = [[BLACK]*GRID_WIDTH for _ in range(GRID_HEIGHT)]
    for (x, y), c in locked.items():
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            grid[y][x] = c
    return grid

#Converts the shape's relative coordinates to grid coordinates
def convert_shape(p):
    return [(p.x + j, p.y + i) for i, row in enumerate(p.image()) for j, v in enumerate(row) if v]

#Checks if the piece is in a valid position on the grid
def valid_space(p, grid):
    for x, y in convert_shape(p):
        if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
            return False
        if y >= 0 and grid[y][x] != BLACK:
            return False
    return True

# clears the filled rows from the grid and shift others down
def clear_rows(locked):
    grid = create_grid(locked)
    full = [y for y in range(GRID_HEIGHT) if all(grid[y][x] != BLACK for x in range(GRID_WIDTH))]
    if not full:
        return 0, locked
    for y in full:
        for x in range(GRID_WIDTH):
            locked.pop((x, y), None)
    for y in sorted(full):
        new_locked = {}
        for (x0, y0), c in locked.items():
            new_locked[(x0, y0 + 1 if y0 < y else y0)] = c
        locked = new_locked
    return len(full), locked

# Checks if any locked blocks are in top row
def check_lost(locked):
    return any(y == 0 for (_, y) in locked)

#Generates a new random piece
def get_piece():
    return Block(GRID_WIDTH//2 - 2, 0, random.choice(SHAPES))

# evaluates the grid for the bot using height, holes, and bumpiness
def evaluate_grid(grid):
    heights = [0]*GRID_WIDTH
    holes = 0
    for x in range(GRID_WIDTH):
        seen = False
        for y in range(GRID_HEIGHT):
            if grid[y][x] != BLACK:
                if not seen:
                    heights[x] = GRID_HEIGHT - y
                    seen = True
            elif seen:
                holes += 1
    bump = sum(abs(heights[i] - heights[i+1]) for i in range(GRID_WIDTH-1))
    return .5*sum(heights) + .7*holes + .2*bump

# uses bot to choose best rotation and position for a piece
def pick_best_move(p, locked):
    best = float('inf')
    move = (p.rotation, p.x)
    for r in range(len(p.rotations)):
        q = copy.deepcopy(p)
        q.rotation = r
        for col in range(-2, GRID_WIDTH):
            q.x, q.y = col, 0
            while valid_space(q, create_grid(locked)):
                q.y += 1
            q.y -= 1
            if not valid_space(q, create_grid(locked)):
                continue
            g = create_grid(locked)
            for tx, ty in convert_shape(q):
                g[ty][tx] = q.color
            s = evaluate_grid(g)
            if s < best:
                best, move = s, (r, col)
    return move

# draws centered text on screen
def draw_text(s, t, size, c, y):
    f = pygame.font.SysFont(None, size)
    l = f.render(t, True, c)
    s.blit(l, (SCREEN_WIDTH//2 - l.get_width()//2, y))

# Renders the main menu screen

def start_screen(win):
    bg = PALETTES[current_palette_name][-1]
    win.fill(bg)
    text_color = PALETTES[current_palette_name][0]
    draw_text(win, 'TETRIBOT', 64, text_color, 80)
    draw_text(win, f'Theme: {current_palette_name}', 28, text_color, 160)
    draw_text(win, 'P: Play   B: Bot   T: Change Theme', 24, text_color, 240)
    pygame.display.update()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_p: return 'play'
                if e.key == pygame.K_b: return 'bot'
                if e.key == pygame.K_t: return 'theme'
                if e.key == pygame.K_r: return 'menu'
            elif e.type == pygame.QUIT:
                pygame.quit()
                exit()

#renders the theme selection screen

def theme_screen(win):
    global COLORS, current_palette_name
    bg = PALETTES[current_palette_name][-1]
    win.fill(bg)
    text_color = PALETTES[current_palette_name][0]
    draw_text(win, 'Select Theme', 48, text_color, 80)
    for i, name in enumerate(PALETTES.keys()):
        draw_text(win, f'{i+1}: {name}', 32, text_color, 160 + i*40)
    hint = 'R: Menu'
    hint_surf = pygame.font.SysFont(None, 24).render(hint, True, text_color)
    win.blit(hint_surf, (SCREEN_WIDTH - hint_surf.get_width() - 5, 5))
    pygame.display.update()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: return
                idx = e.key - pygame.K_1
                names = list(PALETTES.keys())
                if 0 <= idx < len(names):
                    current_palette_name = names[idx]
                    COLORS = PALETTES[current_palette_name]
                    return
            elif e.type == pygame.QUIT:
                pygame.quit()
                exit()

# renders game over screen and score

def game_over_screen(win, score):
    bg = PALETTES[current_palette_name][-1]
    win.fill(bg)
    text_color = PALETTES[current_palette_name][0]
    draw_text(win, 'YOU LOST', 64, text_color, 140)
    draw_text(win, f'Score: {score}', 32, text_color, 220)
    draw_text(win, 'R: Return to Main Menu or Q: Quit', 24, text_color, 300)
    pygame.display.update()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: return 'restart'
                if e.key == pygame.K_q:
                    pygame.quit()
                    exit()
            elif e.type == pygame.QUIT:
                pygame.quit()
                exit()

# the main game function

def main():
    pygame.init()
    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Tetribot')
    while True:
        mode = start_screen(win)
        if mode == 'theme':
            theme_screen(win)
            continue
        clock = pygame.time.Clock()
        locked = {}
        current, next_piece = get_piece(), get_piece()
        fall_time, fall_speed = 0, 0.1
        score = 0
        target_rot, target_x = pick_best_move(current, locked)
        running = True
        while running:
            fall_time += clock.get_rawtime()
            clock.tick(60)
            grid = create_grid(locked)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    return
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_r:
                        running = False
                        break
                if mode == 'play' and e.type == pygame.KEYDOWN:
                    old = (current.x, current.y, current.rotation)
                    if e.key == pygame.K_LEFT:
                        current.x -= 1
                    elif e.key == pygame.K_RIGHT:
                        current.x += 1
                    elif e.key == pygame.K_DOWN:
                        current.y += 1
                    elif e.key == pygame.K_UP:
                        current.rotate()
                    if not valid_space(current, grid):
                        current.x, current.y, current.rotation = old
            if not running:
                break
            aligned = (current.rotation == target_rot and current.x == target_x)
            if mode == 'bot':
                if not aligned:
                    if current.rotation != target_rot:
                        current.rotate()
                    elif current.x < target_x:
                        current.x += 1
                    else:
                        current.x -= 1
                else:
                    current.y += 1
                    if not valid_space(current, grid):
                        current.y -= 1
                        for pos in convert_shape(current):
                            locked[pos] = current.color
                        c, locked = clear_rows(locked)
                        score += c*10
                        current, next_piece = next_piece, get_piece()
                        target_rot, target_x = pick_best_move(current, locked)
                        continue
            if fall_time/1000 >= fall_speed:
                fall_time = 0
                current.y += 1
                if not valid_space(current, grid):
                    current.y -= 1
                    for pos in convert_shape(current):
                        locked[pos] = current.color
                    c, locked = clear_rows(locked)
                    score += c*10
                    current, next_piece = next_piece, get_piece()
                    target_rot, target_x = pick_best_move(current, locked)
            win.fill(BLACK)
            for (x,y),c in locked.items():
                pygame.draw.rect(win,c,(x*BLOCK_SIZE,y*BLOCK_SIZE,BLOCK_SIZE,BLOCK_SIZE))
            for px,py in convert_shape(current):
                pygame.draw.rect(win,current.color,(px*BLOCK_SIZE,py*BLOCK_SIZE,BLOCK_SIZE,BLOCK_SIZE))
            text_color = PALETTES[current_palette_name][0]
            hint = 'R: Menu'
            hint_surf = pygame.font.SysFont(None, 24).render(hint, True, text_color)
            win.blit(hint_surf, (SCREEN_WIDTH - hint_surf.get_width() - 5, 5))
            draw_text(win, f'Score: {score}', 24, text_color, 5)
            for x in range(GRID_WIDTH+1):
                pygame.draw.line(win,GRAY,(x*BLOCK_SIZE,0),(x*BLOCK_SIZE,SCREEN_HEIGHT))
            for y in range(GRID_HEIGHT+1):
                pygame.draw.line(win,GRAY,(0,y*BLOCK_SIZE),(SCREEN_WIDTH,y*BLOCK_SIZE))
            pygame.display.update()
            if check_lost(locked):
                pygame.time.delay(300)
                action = game_over_screen(win, score)
                running = False

# Start the game loop when the script is run
if __name__ == '__main__':
    main()
