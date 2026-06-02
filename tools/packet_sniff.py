import pygame
import random
import time
import sys
import threading

# ---------------- INIT ----------------
pygame.init()
WIDTH, HEIGHT = 1000, 420
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CYBER SNIFFER MODULE")

clock = pygame.time.Clock()

FONT = pygame.font.SysFont("consolas", 16)
BIG = pygame.font.SysFont("consolas", 28)

BLACK = (10, 10, 10)
ORANGE = (255, 140, 0)
DARK = (25, 15, 10)
GREEN = (0, 255, 100)
RED = (255, 60, 60)
GRAY = (60, 60, 60)

log_lines = []
sniffing_active = False
packet_count = 0

# --------------- PACKET GENERATOR ---------------
def generate_fake_packet():
    protocols = ["TCP", "UDP", "ICMP", "HTTP", "DNS"]
    ip = lambda: ".".join(str(random.randint(1, 254)) for _ in range(4))
    port = random.randint(20, 9000)
    length = random.randint(40, 1500)

    proto = random.choice(protocols)
    src = ip()
    dst = ip()

    return f"{time.strftime('%H:%M:%S')} {proto:<5} {src}:{port}  >  {dst}:{port}  Len={length}"

# --------------- SNIFFER THREAD ---------------
def start_sniffer():
    global sniffing_active, packet_count
    sniffing_active = True
    packet_count = 0
    log_lines.append("[+] Sniffer started (Simulation Mode)")
    while sniffing_active:
        packet = generate_fake_packet()
        log_lines.append(packet)
        packet_count += 1
        time.sleep(0.25)

def stop_sniffer():
    global sniffing_active
    sniffing_active = False
    log_lines.append("[!] Sniffer stopped")

# --------------- DRAWING FUNCTIONS ---------------
def draw_background():
    screen.fill(BLACK)
    for i in range(0, WIDTH, 40):
        pygame.draw.line(screen, (20, 20, 20), (i, 0), (i, HEIGHT))
    for i in range(0, HEIGHT, 40):
        pygame.draw.line(screen, (20, 20, 20), (0, i), (WIDTH, i))

def draw_panel():
    pygame.draw.rect(screen, ORANGE, (0, 0, WIDTH, HEIGHT), 3)

    # Title
    title = BIG.render("CYBER SNIFFER CONTROL PANEL", True, ORANGE)
    screen.blit(title, (20, 15))

    # Packet Counter
    counter = FONT.render(f"Packets Captured: {packet_count}", True, GREEN)
    screen.blit(counter, (25, 65))

    # Live Indicator
    if sniffing_active:
        blink = int(time.time() * 2) % 2
        if blink:
            live = FONT.render("● LIVE CAPTURE", True, RED)
            screen.blit(live, (250, 65))

    # Buttons
    draw_button("START", 30, 100)
    draw_button("STOP", 160, 100)

    # Log Panel
    pygame.draw.rect(screen, DARK, (350, 60, 620, 330))
    pygame.draw.rect(screen, ORANGE, (350, 60, 620, 330), 2)

    draw_logs()

def draw_button(text, x, y):
    pygame.draw.rect(screen, GRAY, (x, y, 100, 35))
    pygame.draw.rect(screen, ORANGE, (x, y, 100, 35), 2)
    label = FONT.render(text, True, ORANGE)
    screen.blit(label, (x + 25, y + 8))

def draw_logs():
    y = 75
    for line in log_lines[-15:]:
        text = FONT.render(line[:95], True, GREEN)
        screen.blit(text, (365, y))
        y += 20

# --------------- MAIN LOOP ---------------
running = True

while running:
    draw_background()
    draw_panel()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            # START button
            if 30 <= mx <= 130 and 100 <= my <= 135:
                if not sniffing_active:
                    threading.Thread(target=start_sniffer, daemon=True).start()

            # STOP button
            if 160 <= mx <= 260 and 100 <= my <= 135:
                stop_sniffer()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()