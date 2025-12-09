import cv2
import numpy as np
import pygame
import random
import string

# -----------------------
# CONFIG
# -----------------------
WIDTH  = 800
HEIGHT = 600

CELL_SIZE = 8                     # Matrix grid cell size
FALL_SPEED = 0.6                     # vertical scroll speed
HALO_BLUR = 6                     # strength of edge halo
BRIGHT_SCALE = 3.0                 # how bright edges become

# -----------------------
# INIT
# -----------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Matrix Silhouette - Full Grid Method")

font = pygame.font.SysFont("Consolas", CELL_SIZE, bold=True)
clock = pygame.time.Clock()

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

cols = WIDTH // CELL_SIZE
rows = HEIGHT // CELL_SIZE

# y offsets per column for scrolling rain
offsets = [random.uniform(0, rows) for _ in range(cols)]

def rand_char():
    return random.choice("0123456789日ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ:・.=*+-<>")

# Random characters for entire grid
chars = [[rand_char() for _ in range(cols)] for _ in range(rows)]

# -----------------------------------
# RAIN TRAIL SETUP
# -----------------------------------
trail_heads = [random.uniform(0, rows) for _ in range(cols)]
trail_lengths = [random.randint(5, 30) for _ in range(cols)]

def new_trail_length():
    return random.randint(5, 30)

# -----------------------
# MAIN LOOP
# -----------------------
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.resize(frame, (WIDTH, HEIGHT))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 1. Canny edges
    edges = cv2.Canny(gray, 40, 120)

    # 2. Halo around edges (distance field)
    halo = cv2.GaussianBlur(edges.astype(np.float32), (0,0), HALO_BLUR)
    if halo.max() > 0:
        halo /= halo.max()   # 0–1

    # 3. Sample halo on the character grid
    brightness = np.zeros((rows, cols), dtype=np.float32)

    for r in range(rows):
        y0 = int(r * CELL_SIZE)
        y1 = min(y0 + CELL_SIZE, HEIGHT)
        for c in range(cols):
            x0 = int(c * CELL_SIZE)
            x1 = min(x0 + CELL_SIZE, WIDTH)
            # avg halo inside this cell
            cell_val = np.mean(halo[y0:y1, x0:x1])
            brightness[r, c] = min(1.0, cell_val * BRIGHT_SCALE)

    # Fade the screen
    fade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    fade.fill((0, 0, 0, 55))
    screen.blit(fade, (0, 0))

# -----------------------------------
# DRAW MATRIX RAIN (UPDATED)
# -----------------------------------
for c in range(cols):

    # Move head downward
    trail_heads[c] = (trail_heads[c] + FALL_SPEED * 0.3) % rows
    head_r = int(trail_heads[c])

    # Occasionally refresh trail length (new drop)
    if random.random() < 0.01:
        trail_lengths[c] = new_trail_length()

    L = trail_lengths[c]

    # Draw this column’s trail
    for i in range(L):

        r = (head_r - i) % rows  # current cell in trail
        ch = chars[r][c]

        # Base matrix fade: head = 1.0 → tail = 0.0
        fade = 1.0 - (i / L)

        # brightness from video edges
        edge_b = brightness[r][c]  # 0–1
        edge_boost = 0.4 + edge_b * 0.6  # edges stay bright

        # combine matrix fade + edge brightness
        final_bright = min(1.0, fade * edge_boost)

        # green brightness
        g = int(40 + final_bright * 215)

        screen.blit(
            font.render(ch, True, (0, g, 0)),
            (c * CELL_SIZE, r * CELL_SIZE)
        )

    pygame.display.flip()
    clock.tick(30)

cap.release()
pygame.quit()
