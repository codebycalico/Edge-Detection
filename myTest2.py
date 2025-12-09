# Initial Source:
# https://www.youtube.com/watch?v=hU2bqajRcew

import cv2
import numpy as np
import pygame
import random

pygame.init()
WIDTH, HEIGHT = 800, 600
HALO_BLUR = 6                     # strength of edge halo
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Matrix")
clock = pygame.time.Clock()

font = pygame.font.SysFont("couriernew",14)
char_set = "0123456789:・.=*+-<>"
# 日ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

columns = []
column_width = 10

for i in range(WIDTH // column_width):
    columns.append(
        { 'y': random.randint(-200, 0),
          'speed': random.uniform(1.0, 5.0),
          'chars': [random.choice(char_set) for _ in range(HEIGHT // 20)]
         }
    )

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ret, frame = cap.read()
    if not ret:
        continue

    screen.fill((0,0,0))

    frame = cv2.resize(frame, (WIDTH, HEIGHT))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 1. Canny edges
    edges = cv2.Canny(gray, 40, 120)

    # 2. Halo around edges (distance field)
    halo = cv2.GaussianBlur(edges.astype(np.float32), (0,0), HALO_BLUR)
    if halo.max() > 0:
        halo /= halo.max()   # 0–1

    # 3. Sample halo on the character grid
    brightness = np.zeros((HEIGHT / 20, columns), dtype=np.float32)

    for i, column in enumerate(columns):
        x = i * column_width
        column['y'] += column['speed']

        if column['y'] > HEIGHT:
            column['y'] = -300
            column['chars'] = [random.choice(char_set) for _ in range(HEIGHT // 20)]

        for j, char in enumerate(column['chars']):
            y_pos = column['y'] + j * 20
            if 0 <= y_pos < HEIGHT:
                # here is where we would compare the x and y to the x and y of the lines
                # to see if the char is within a certain distance of the detected lines
                # and make brighter if so
                # if(y_pos )
                brightness = max(0, 255 - j * 20)
                color = (0, min(255, brightness + 100), 0)

                if random.random() < 0.05:
                    column['chars'][j] = random.choice(char_set)

                text = font.render(char, True, color)
                screen.blit(text, (x, y_pos))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()