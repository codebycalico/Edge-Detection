import cv2
import numpy as np
import pygame
import random
import string

# --------------------------
# CONFIG
# --------------------------
WIDTH = 800
HEIGHT = 600
FONT_SIZE = 16
DENSITY_FACTOR = 5       # Higher → more rain where edges detected
RAIN_SPEED = 4

# --------------------------
# INITIALIZE
# --------------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Matrix Rain with Edge Attraction")

font = pygame.font.SysFont("Consolas", FONT_SIZE, bold=True)
clock = pygame.time.Clock()

# Camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

# Create Columns
columns = int(WIDTH / FONT_SIZE)
drops = [random.randint(-HEIGHT, 0) for _ in range(columns)]

def random_char():
    return random.choice(string.ascii_letters + string.digits)

# --------------------------
# MAIN LOOP
# --------------------------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ------------------------------------------
    # 1. Read webcam frame + detect edges
    # ------------------------------------------
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (WIDTH, HEIGHT))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)

    # Convert edges to density map (scaled down to column resolution)
    edge_density = cv2.resize(edges, (columns, HEIGHT // FONT_SIZE))
    edge_density = edge_density / 255.0  # 0 → no edge, 1 → strong edge

    # ------------------------------------------
    # 2. Draw black background (transparent fade)
    # ------------------------------------------
    screen.fill((0, 0, 0))

    # ------------------------------------------
    # 3. Matrix rain
    # ------------------------------------------
    for i in range(columns):
        # X position of this rain column
        x = i * FONT_SIZE

        # Y position
        y = drops[i] * FONT_SIZE

        # Determine if this column should be more active based on edges
        row_index = drops[i] % (HEIGHT // FONT_SIZE)
        condense_strength = edge_density[row_index, i] * DENSITY_FACTOR

        # Generate several characters if high density (edge present)
        repeat = 1 + int(condense_strength)

        for _ in range(repeat):
            char = random_char()
            text = font.render(char, True, (0, 255, 70))
            screen.blit(text, (x, y))

        # Move downward
        drops[i] += RAIN_SPEED

        # Reset when reaching bottom
        if drops[i] * FONT_SIZE > HEIGHT:
            drops[i] = random.randint(-20, -1)

    # ------------------------------------------
    # 4. Update display
    # ------------------------------------------
    pygame.display.flip()
    clock.tick(30)

# Cleanup
cap.release()
pygame.quit()
