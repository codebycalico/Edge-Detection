import cv2
import numpy as np
import pygame
import random
import string
import time

# --------------------------
# CONFIG
# --------------------------
WIDTH = 800
HEIGHT = 600
FONT_SIZE = 16

FALL_SPEED = 1.2
DENSITY_FACTOR = 5
HEAD_WHITE_PROB = 0.08
TRAIL_MIN = 8
TRAIL_MAX = 25

# --------------------------
# INITIALIZE
# --------------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Matrix Rain Stable Version")

font = pygame.font.SysFont("Consolas", FONT_SIZE, bold=True)
clock = pygame.time.Clock()

# VERY IMPORTANT: explicit backend (more stable)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    raise RuntimeError("Could not access webcam")

cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

columns = WIDTH // FONT_SIZE

drops = [random.uniform(-HEIGHT, 0) for _ in range(columns)]
trail_len = [random.randint(TRAIL_MIN, TRAIL_MAX) for _ in range(columns)]

def random_char():
    return random.choice(string.ascii_letters + string.digits)

# --------------------------
# MAIN LOOP
# --------------------------
running = True
last_good_frame_time = time.time()

while running:
    # --- Pygame events first (to avoid OS killing window) ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Webcam frame fetch ---
    ret, frame = cap.read()

    if not ret:
        # If camera fails briefly, retry instead of quitting
        if time.time() - last_good_frame_time > 3:
            print("Camera inactive for too long. Exiting.")
            break
        continue  # try again next loop

    last_good_frame_time = time.time()

    # Edge detection
    frame = cv2.resize(frame, (WIDTH, HEIGHT))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    edge_density = cv2.resize(edges, (columns, HEIGHT // FONT_SIZE)) / 255.0

    # Semi-transparent fade
    fade_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    fade_surface.fill((0, 0, 0, 40))
    screen.blit(fade_surface, (0, 0))

    # --- MATRIX RAIN ---
    for i in range(columns):
        x = i * FONT_SIZE
        y = int(drops[i])

        row_index = int((drops[i] // FONT_SIZE) % (HEIGHT // FONT_SIZE))
        condense_strength = edge_density[row_index, i] * DENSITY_FACTOR

        for r in range(trail_len[i]):
            cy = int(drops[i] - r * FONT_SIZE)
            if cy < 0 or cy >= HEIGHT:
                continue

            char = random_char()

            if r == 0:
                head_color = (255, 255, 255) if random.random() < HEAD_WHITE_PROB else (180, 255, 180)
                text = font.render(char, True, head_color)
            else:
                fade = max(0, 255 - r * (255 // trail_len[i]))
                text = font.render(char, True, (0, fade, 0))

            screen.blit(text, (x, cy))

        drops[i] += FALL_SPEED * FONT_SIZE

        if drops[i] > HEIGHT + trail_len[i] * FONT_SIZE:
            drops[i] = random.uniform(-200, -20)
            trail_len[i] = random.randint(TRAIL_MIN, TRAIL_MAX)

    pygame.display.flip()
    clock.tick(30)  # <- Prevents overload crashes

cap.release()
pygame.quit()
