#!/usr/bin/env python3
import pygame
import os
import time
import math
import sys
import threading
from datetime import datetime

# ================= LOG CORE =================

LOG_DIR = "logs"
# base names only – we will try *.txt first then *.log
LOG_SOURCES = [
    "wifi", "sniffer", "deauth",
    "eviltwin", "rfid", "nfc"
]

def collect_logs():
    """
    Read the tail of all log files and return a flat list:
    [(source_file, line_text, timestamp), ...]
    Prefers *.txt, falls back to *.log.
    """
    logs = []
    for base in LOG_SOURCES:
        path = None
        for ext in (".txt", ".log"):
            candidate = os.path.join(LOG_DIR, base + ext)
            if os.path.exists(candidate):
                path = candidate
                break
        if not path:
            continue

        try:
            mtime = os.path.getmtime(path)
            with open(path, "r", buffering=1, errors="ignore") as fh:
                lines = fh.readlines()[-200:]
        except Exception:
            continue

        for line in lines:
            logs.append((base, line.rstrip("\n"), mtime))

    return logs[-1000:]


def export_report(logs):
    """
    Export all currently loaded logs into a timestamped report file.
    """
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(LOG_DIR, f"report_{stamp}.txt")

    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("=== UZUMAKI CYBERSEC LOG REPORT ===\n")
            f.write(f"Generated at: {datetime.now().isoformat()}\n")
            f.write("===================================\n\n")

            last_src = None
            for src, line, ts in logs:
                if src != last_src:
                    f.write(f"\n--- {src} ---\n")
                    last_src = src
                t_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
                f.write(f"[{t_str}] {line}\n")

        return report_path
    except Exception:
        return None


def log_viewer():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("LIVE LOG VIEWER")

    font = pygame.font.SysFont("DejaVu Sans", 16)
    small = pygame.font.SysFont("DejaVu Sans", 13)
    clock = pygame.time.Clock()
    running = True
    angle = 0.0
    last_refresh = 0.0

    logs = collect_logs() or [("system", "(No logs yet)", time.time())]

    # scrolling state
    VISIBLE_LINES = 24
    scroll = max(0, len(logs) - VISIBLE_LINES)
    auto_follow = True      # like "tail -f"
    status_msg = ""
    status_until = 0.0

    while running:
        now = time.time()

        # periodic refresh
        if now - last_refresh > 0.6:
            new_logs = collect_logs() or [("system", "(No logs yet)", time.time())]
            last_refresh = now

            logs = new_logs
            if auto_follow:
                scroll = max(0, len(logs) - VISIBLE_LINES)
            else:
                scroll = min(scroll, max(0, len(logs) - VISIBLE_LINES))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

            # mouse wheel scrolling
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 4:   # wheel up
                    auto_follow = False
                    scroll = max(0, scroll - 3)
                elif e.button == 5: # wheel down
                    auto_follow = False
                    scroll = min(max(0, len(logs) - VISIBLE_LINES),
                                 scroll + 3)

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False

                # scroll up/down with keys
                if e.key in (pygame.K_UP, pygame.K_PAGEUP):
                    auto_follow = False
                    scroll = max(0, scroll - 1)
                if e.key in (pygame.K_DOWN, pygame.K_PAGEDOWN):
                    auto_follow = False
                    scroll = min(max(0, len(logs) - VISIBLE_LINES),
                                 scroll + 1)

                # jump to end & re-enable auto follow
                if e.key in (pygame.K_END, pygame.K_f):
                    auto_follow = True
                    scroll = max(0, len(logs) - VISIBLE_LINES)

                # export as report
                if e.key == pygame.K_r:
                    path = export_report(logs)
                    if path:
                        status_msg = f"Report saved: {path}"
                    else:
                        status_msg = "Failed to save report!"
                    status_until = now + 4.0

        # drawing
        screen.fill((8, 8, 14))
        angle += 0.01
        cx, cy = 400, 330

        # spiral particle background
        for i, (src, line, tstamp) in enumerate(logs[-160:]):
            a = i * 0.35 + angle
            r = 8 + i * 4
            x = cx + math.cos(a) * r
            y = cy + math.sin(a) * r

            age = now - tstamp
            glow = max(0.1, 1.0 - age / 20.0)
            base_col = (180, 200, 255) if i % 2 else (200, 150, 220)
            col = (
                min(255, int(base_col[0] + glow * 40)),
                min(255, int(base_col[1] + glow * 40)),
                min(255, int(base_col[2] + glow * 40)),
            )
            size = 2 + int(glow * 3)
            pygame.draw.circle(screen, col, (int(x), int(y)), size)

        # log text area
        pygame.draw.rect(screen, (10, 10, 18), (20, 20, 760, 480))
        pygame.draw.rect(screen, (80, 80, 120), (20, 20, 760, 480), 2)

        start = max(0, scroll)
        end = min(len(logs), start + VISIBLE_LINES)
        y_text = 26
        for src, line, tstamp in logs[start:end]:
            msg = f"[{src}] {line}"
            txt = font.render(msg[:120], True, (210, 220, 210))
            screen.blit(txt, (26, y_text))
            y_text += 19

        # footer
        footer = small.render(
            "ESC=Close  Wheel/↑↓=Scroll  F/End=Follow tail  R=Export Report",
            True, (230, 180, 120)
        )
        screen.blit(footer, (20, 510))

        # status message
        if status_msg and now < status_until:
            sm = small.render(status_msg, True, (255, 200, 80))
            screen.blit(sm, (20, 540))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


# ================= SIMPLE FRONT UI =================

pygame.init()
W, H = 600, 300
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("SYSTEM LOG VIEW")

FONT = pygame.font.SysFont("consolas", 18)
BIG  = pygame.font.SysFont("consolas", 26)

BLACK = (10, 10, 10)
ORANGE = (255, 120, 0)
DARK = (35, 15, 10)

clock = pygame.time.Clock()
running = True


def splash():
    screen.fill(BLACK)
    screen.blit(BIG.render("INITIALIZING LOG CORE", True, ORANGE), (140, 140))
    pygame.display.flip()
    time.sleep(1.5)


def button(text, x, y):
    pygame.draw.rect(screen, ORANGE, (x, y, 180, 32), 2)
    screen.blit(FONT.render(text, True, ORANGE), (x + 10, y + 6))


def draw_menu():
    screen.fill(BLACK)
    pygame.draw.rect(screen, ORANGE, (0, 0, W, H), 3)
    pygame.draw.rect(screen, DARK, (30, 40, 250, 200))

    screen.blit(BIG.render("LOG MODULE", True, ORANGE), (40, 60))
    button("OPEN LOG VIEW", 60, 120)
    button("EXIT", 60, 170)


def launch_viewer():
    threading.Thread(target=log_viewer, daemon=True).start()


# ================= RUN =================
splash()

while running:
    draw_menu()

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

        if e.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if 60 <= mx <= 240 and 120 <= my <= 152:
                launch_viewer()
            if 60 <= mx <= 240 and 170 <= my <= 202:
                running = False

        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            running = False

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
