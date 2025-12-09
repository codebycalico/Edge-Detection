import cv2
import numpy as np
import pygame
import random
import string

# ----------------------------
# CONFIG — TUNE THESE
# ----------------------------
WIDTH = 800
HEIGHT = 600

NUM_COLUMNS = 60
FONT_SIZE = WIDTH // NUM_COLUMNS
FALL_SPEED = 1.3

TRAIL_LENGTH = 15

# How big the halo around edges should be (IN PIXELS)
EDGE_HALO_RADIUS = 35    # increase for bigger silhouette halo

# How bright the rain gets in edge zones
BRIGHT_MULTIPLIER = 2.5  # 1.0 = normal, 3.0 = very bright

# Background rain
BACKGROUND_DENSITY = 0.003

# ----------------------------
# INITIALIZATION
# ----------------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Matrix Silhouette - Halo Edge Version")

font = pygame.font.SysFont("Consolas", FONT_SIZE, bold=True)
clock = pygame.time.Clock()

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

columns = [None] * NUM_COLUMNS

def random_char():
    return random.choice(string.digits)

class Stream:
    def __init__(self, col, brightness):
        self.col = col
        self.y = -FONT_SIZE
        self.brightness = brightness
        self.chars = [random_char() for _ in range(TRAIL_LENGTH)]

    def step(self):
        self.y += FALL_SPEED * FONT_SIZE

    def dead(self):
        return self.y > HEIGHT + TRAIL_LENGTH * FONT_SIZE

# ----------------------------
# MAIN LOOP
# ----------------------------
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

    # ---- 1. Strong Canny edges ----
    edges = cv2.Canny(gray, 50, 120)

    # ---- 2. Create a HALO around edges using Gaussian blur ----
    # this expands edges into a thick influence field
    halo = cv2.GaussianBlur(edges.astype(np.float32),
                            (0, 0),
                            EDGE_HALO_RADIUS)

    # Normalize halo values to 0–1
    halo = halo / halo.max() if halo.max() > 0 else halo

    # ---- 3. Convert halo to per-column edge force ----
    col_w = WIDTH // NUM_COLUMNS
    edge_force = []

    for i in range(NUM_COLUMNS):
        x0 = i * col_w
        x1 = x0 + col_w
        value = np.mean(halo[:, x0:x1])
        edge_force.append(value)

    # ---- Fade layer ----
    fade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    fade.fill((0, 0, 0, 50))
    screen.blit(fade, (0, 0))

    # ---- Draw & update streams ----
    for i in range(NUM_COLUMNS):
        force = edge_force[i]

        # spawn chance boosted by edge halo
        spawn_prob = BACKGROUND_DENSITY + force * 0.2

        # spawn a new stream if none in that column
        if columns[i] is None and random.random() < spawn_prob:
            brightness = int(50 + force * BRIGHT_MULTIPLIER * 255)
            brightness = min(brightness, 255)
            columns[i] = Stream(i, brightness)

        # draw
        s = columns[i]
        if s:
            s.step()
            x = i * col_w

            for j, char in enumerate(s.chars):
                cy = int(s.y - j * FONT_SIZE)
                if 0 <= cy < HEIGHT:

                    fade_factor = max(25, s.brightness - j * (s.brightness // TRAIL_LENGTH))
                    color = (0, fade_factor, 0)

                    screen.blit(font.render(char, True, color), (x, cy))

            if s.dead():
                columns[i] = None

    pygame.display.flip()
    clock.tick(30)

cap.release()
pygame.quit()
