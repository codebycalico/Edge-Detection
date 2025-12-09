import cv2
import numpy as np
import pygame
import random
import string

# -----------------------
# CONFIG
# -----------------------
WIDTH = 800
HEIGHT = 600

NUM_COLUMNS = 90            # many narrow thin columns
FONT_SIZE = WIDTH // NUM_COLUMNS

FALL_SPEED = 1.1
TRAIL_LENGTH = 12

HALO_BLUR = 6               # small! sharp edges
EDGE_GAIN = 2.2             # stronger silhouette
BACKGROUND_DENSITY = 0.0015 # almost no background rain

# -----------------------
# INIT
# -----------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Matrix Silhouette - Thin Sharp Version")

font = pygame.font.SysFont("Consolas", FONT_SIZE, bold=True)
clock = pygame.time.Clock()

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

columns = [None] * NUM_COLUMNS

def rand_char():
    return random.choice("0123456789")

class Stream:
    def __init__(self, col, brightness):
        self.col = col
        self.y = -FONT_SIZE
        self.brightness = brightness
        self.chars = [rand_char() for _ in range(TRAIL_LENGTH)]

    def step(self):
        self.y += FALL_SPEED * FONT_SIZE

    def dead(self):
        return self.y > HEIGHT + TRAIL_LENGTH * FONT_SIZE

# -----------------------
# LOOP
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

    # 1. Canny
    edges = cv2.Canny(gray, 60, 130)

    # 2. SMALL halo (thin glow)
    halo = cv2.GaussianBlur(edges.astype(np.float32), (0,0), HALO_BLUR)
    if halo.max() > 0:
        halo /= halo.max()

    # Per-column sharp edge intensity
    col_w = WIDTH // NUM_COLUMNS
    edge_force = []

    for c in range(NUM_COLUMNS):
        x0 = c * col_w
        x1 = x0 + col_w
        force = np.mean(halo[:, x0:x1])
        edge_force.append(force)

    # fade layer
    fade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    fade.fill((0, 0, 0, 50))
    screen.blit(fade, (0, 0))

    # Update & draw
    for c in range(NUM_COLUMNS):

        force = edge_force[c]
        spawn_prob = BACKGROUND_DENSITY + force * 0.25

        # spawn?
        if columns[c] is None and random.random() < spawn_prob:
            bright = min(255, int(force * EDGE_GAIN * 255))
            bright = max(50, bright)
            columns[c] = Stream(c, bright)

        s = columns[c]
        if s is not None:
            s.step()
            x = c * col_w

            # draw trail
            for j, char in enumerate(s.chars):
                cy = int(s.y - j * FONT_SIZE)
                if 0 <= cy < HEIGHT:
                    decay = max(30, s.brightness - j * (s.brightness // TRAIL_LENGTH))
                    screen.blit(font.render(char, True, (0, decay, 0)), (x, cy))

            if s.dead():
                columns[c] = None

    pygame.display.flip()
    clock.tick(30)

cap.release()
pygame.quit()
