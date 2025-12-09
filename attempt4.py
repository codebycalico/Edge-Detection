import cv2
import numpy as np
import pygame
import random
import string

# --------------------------
# CONFIG (ADJUST THESE)
# --------------------------
WIDTH = 800
HEIGHT = 600

NUM_COLUMNS = 60         # FEW columns → clean silhouette
FONT_SIZE = WIDTH // NUM_COLUMNS

FALL_SPEED = 1.0
SPAWN_BASE = 0.002         # small background spawn
SPAWN_EDGE_BOOST = 0.15    # edges make spawning much more likely

BRIGHTNESS_MIN = 150
BRIGHTNESS_MAX = 255
TRAIL_LENGTH = 12          # fixed, clean trail

# --------------------------
# INITIALIZE
# --------------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Clean Matrix Silhouette")

font = pygame.font.SysFont("Consolas", FONT_SIZE, bold=True)
clock = pygame.time.Clock()

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

columns = [None] * NUM_COLUMNS   # each entry stores a stream or None

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

# --------------------------
# MAIN LOOP
# --------------------------
running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ---- CAMERA ----
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.resize(frame, (WIDTH, HEIGHT))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 70, 150)

    # compute average edge strength per column
    col_width = WIDTH // NUM_COLUMNS
    edge_strength = []

    for i in range(NUM_COLUMNS):
        x0 = i * col_width
        x1 = x0 + col_width
        col_val = np.mean(edges[:, x0:x1]) / 255.0
        edge_strength.append(col_val)

    # ---- DRAW FADE LAYER ----
    fade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    fade.fill((0, 0, 0, 60))
    screen.blit(fade, (0, 0))

    # ---- UPDATE & DRAW STREAMS ----
    for i in range(NUM_COLUMNS):

        strength = edge_strength[i]

        # SPAWN CONTROL
        spawn_prob = SPAWN_BASE + strength * SPAWN_EDGE_BOOST

        if columns[i] is None and random.random() < spawn_prob:
            brightness = int(BRIGHTNESS_MIN + strength * (BRIGHTNESS_MAX - BRIGHTNESS_MIN))
            columns[i] = Stream(i, brightness)

        # DRAW STREAM
        s = columns[i]
        if s is not None:
            s.step()
            x = i * col_width

            for j, char in enumerate(s.chars):
                cy = int(s.y - j * FONT_SIZE)
                if 0 <= cy < HEIGHT:
                    fade_amount = max(30, s.brightness - j * (s.brightness // TRAIL_LENGTH))
                    color = (0, fade_amount, 0)
                    screen.blit(font.render(char, True, color), (x, cy))

            if s.dead():
                columns[i] = None

    pygame.display.flip()
    clock.tick(30)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
pygame.quit()
