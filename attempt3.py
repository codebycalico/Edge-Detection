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

FALL_SPEED = 0.3
BASE_SPAWN_CHANCE = 0.005       # background rain density
EDGE_SPAWN_MULTIPLIER = 0.25   # more rain where edges detected
HEAD_WHITE_PROB = 0.08
TRAIL_MIN = 8
TRAIL_MAX = 25

# --------------------------
# INITIALIZE
# --------------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Edge-Density Matrix Rain")

font = pygame.font.SysFont("Consolas", FONT_SIZE, bold=True)
clock = pygame.time.Clock()

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

columns = WIDTH // FONT_SIZE

# Streams: each column can have multiple trails active
streams = [[] for _ in range(columns)]

def random_char():
    return random.choice("0123456789日ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ:・.=*+-<>")

class Stream:
    def __init__(self, col, y, length):
        self.col = col
        self.y = y
        self.length = length

    def step(self):
        self.y += FALL_SPEED * FONT_SIZE

    def dead(self):
        return self.y > HEIGHT + self.length * FONT_SIZE

# --------------------------
# MAIN LOOP
# --------------------------
running = True
last_good_frame = time.time()
prev_char = "日"

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ret, frame = cap.read()
    if not ret:
        if time.time() - last_good_frame > 3:
            print("Camera stopped")
            break
        continue

    last_good_frame = time.time()

    frame = cv2.resize(frame, (WIDTH, HEIGHT))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)

    # Very important: get average edge value per column
    column_edges = np.mean(edges, axis=0)  # shape = (WIDTH,)
    column_edges = column_edges.reshape(columns, FONT_SIZE).mean(axis=1) / 255.0

    # Fading layer for smooth trails
    fade_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    fade_surface.fill((0, 0, 0, 45))
    screen.blit(fade_surface, (0, 0))

    # --- SPAWN LOGIC ---
    for col in range(columns):
        # Background rain
        spawn_prob = BASE_SPAWN_CHANCE

        # Add edge-based increase
        spawn_prob += column_edges[col] * EDGE_SPAWN_MULTIPLIER

        if random.random() < spawn_prob:
            length = random.randint(TRAIL_MIN, TRAIL_MAX)
            y_start = random.uniform(-length * (FONT_SIZE), 0)
            streams[col].append(Stream(col, y_start, length))

    # --- UPDATE + DRAW STREAMS ---
    for col in range(columns):
        for s in streams[col]:
            s.step()

            # Draw the trail
            for r in range(s.length):
                cy = int(s.y - r * FONT_SIZE)
                if cy < 0 or cy >= HEIGHT:
                    continue
                
                char = random_char()

                if random.randint(0, 50) <= 2:
                    prev_char = char
                else: 
                    char = prev_char

                x = col * FONT_SIZE

                if r == 0:
                    color = (255, 255, 255) if random.random() < HEAD_WHITE_PROB else (150, 255, 150)
                else:
                    fade = max(30, 255 - int(r * (255 / s.length)))
                    color = (0, fade, 0)

                screen.blit(font.render(char, True, color), (x, cy))

        # Remove dead streams
        streams[col] = [s for s in streams[col] if not s.dead()]

    pygame.display.flip()
    clock.tick(30)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
pygame.quit()
