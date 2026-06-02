#!/usr/bin/env python3
import pygame # type: ignore
import subprocess
import os
import sys
import time

pygame.init()

WIDTH, HEIGHT = 950, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CYBER WAR PANEL")

FONT = pygame.font.SysFont("consolas", 18)
BIG = pygame.font.SysFont("consolas", 28)

BLACK = (8,8,8)
ORANGE = (255,130,0)
GREEN = (0,255,140)
DARK = (35,18,10)

clock = pygame.time.Clock()
wifi_list = []
selected = 0
running = True


# ---------------- SPLASH SCREEN ----------------
def splash():
    screen.fill(BLACK)
    text = BIG.render("INITIALIZING CYBER MODULE", True, ORANGE)
    screen.blit(text, (250,130))
    pygame.display.flip()
    time.sleep(2)


# ---------------- WIFI DETECT ----------------
def detect_wifi():
    adapters = []
    try:
        output = subprocess.check_output(
            "iw dev | grep Interface | awk '{print $2}'",
            shell=True
        )
        adapters = output.decode().split()
    except:
        adapters = ["wlan0"]
    return adapters


# ---------------- RUN AIRGEDDON ----------------
def run_airgeddon():
    global selected
    iface = wifi_list[selected]

    # SAME LOGIC as your core file
    os.system(f"x-terminal-emulator -e 'cd airgeddon && sudo bash airgeddon.sh {iface}'")


# ---------------- UI ----------------
def draw_panel():
    screen.fill(BLACK)
    pygame.draw.rect(screen, ORANGE, (0,0,WIDTH,HEIGHT), 4)

    pygame.draw.rect(screen, DARK, (15, 20, 300, 80))
    pygame.draw.rect(screen, DARK, (15, 105, 300, 175))
    pygame.draw.rect(screen, DARK, (330, 20, 600, 260))

    screen.blit(BIG.render("CYBER CONTROL CENTER", True, ORANGE), (25, 30))
    screen.blit(FONT.render("WiFi Adapters:", True, GREEN), (25, 60))

    y = 130
    for i, w in enumerate(wifi_list):
        color = GREEN if i == selected else ORANGE
        screen.blit(FONT.render(w, True, color), (35, y))
        y += 25

    draw_button("LAUNCH AIRGEDDON", 170, 130)
    draw_button("EXIT", 170, 180)


def draw_button(txt, x, y):
    pygame.draw.rect(screen, ORANGE, (x, y, 140, 34), 2)
    screen.blit(FONT.render(txt, True, ORANGE), (x+10, y+8))


# ---------------- START ----------------
splash()
wifi_list = detect_wifi()


# ---------------- LOOP ----------------
while running:
    draw_panel()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                selected = (selected + 1) % len(wifi_list)
            if event.key == pygame.K_UP:
                selected = (selected - 1) % len(wifi_list)

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            if 170 <= mx <= 310 and 130 <= my <= 164:
                run_airgeddon()

            if 170 <= mx <= 310 and 180 <= my <= 214:
                running = False

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
