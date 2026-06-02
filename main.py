import os, sys, math, time, random, subprocess
import pygame  
import time as __time_for_esp
import math
from typing import Tuple
import threading, webbrowser, re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

try:
    import webview # type: ignore
    WEBVIEW_AVAILABLE = True
except Exception:
    webview = None; WEBVIEW_AVAILABLE = False
try:
    import RPi.GPIO as GPIO # type: ignore
    HAVE_GPIO = True
except Exception:
    GPIO = None; HAVE_GPIO = False
import socket

sock = socket.socket()
try:
    sock.bind(("127.0.0.1", 9999))
except:
    exit()
clock = pygame.time.Clock()
clock.tick(30)


STATE_WIFI = 11
wifi_networks = []
wifi_last_scan = 0
wifi_scan_running = False
wifi_interface = "wlan0" 
radar_angle = 0
ZOOM = 2.0

#scanning 
def scan_wifi_real():
    global wifi_networks

    try:
        result = subprocess.check_output(
            ["iwlist", wifi_interface, "scan"],
            stderr=subprocess.DEVNULL
        ).decode("utf-8", errors="ignore")

        networks = []
        cells = result.split("Cell ")

        for cell in cells[1:]:
            ssid_match = re.search(r'ESSID:"(.*?)"', cell)
            signal_match = re.search(r"Signal level=(-?\d+)", cell)

            if ssid_match and signal_match:
                ssid = ssid_match.group(1)
                signal = int(signal_match.group(1))
                networks.append((ssid, signal))

        wifi_networks = networks

    except Exception:
        wifi_networks = []

def wifi_scan_loop():
    global wifi_scan_running
    while wifi_scan_running:
        scan_wifi_real()
        time.sleep(5)

def start_wifi_scan():
    global wifi_scan_running
    wifi_scan_running = True
    threading.Thread(target=wifi_scan_loop, daemon=True).start()

def stop_wifi_scan():
    global wifi_scan_running
    wifi_scan_running = False
def wifi_draw():
    global radar_angle

    width, height = screen.get_size()
    screen.fill((5, 15, 5))

    center_x = width // 2
    center_y = height // 3
    radius = 200

    green = (0, 255, 120)
    dark_green = (0, 80, 40)

    # Radar circles
    for r in range(50, radius, 50):
        pygame.draw.circle(screen, dark_green, (center_x, center_y), r, 1)

    # Radar sweep
    radar_angle += 0.02
    end_x = center_x + radius * math.cos(radar_angle)
    end_y = center_y + radius * math.sin(radar_angle)

    pygame.draw.line(screen, green, (center_x, center_y), (end_x, end_y), 3)

    # WiFi dots
    for ssid, signal in wifi_networks:
        strength = max(0, min(100, 2 * (signal + 100)))

        # stronger signal = closer to center
        dist = radius - (strength * 2)

        angle = random.uniform(0, 2 * math.pi)
        x = center_x + dist * math.cos(angle)
        y = center_y + dist * math.sin(angle)

        pygame.draw.circle(screen, green, (int(x), int(y)), 6)

    # Title
    title = font.render("WIRELESS RADAR SCANNER", True, green)
    screen.blit(title, (40, 20))

    # Network list below
    y_offset = height // 2 + 50
    for ssid, signal in wifi_networks:
        text = font.render(f"{ssid}  ({signal} dBm)", True, green)
        screen.blit(text, (80, y_offset))
        y_offset += 30

def scan_wifi():
    global wifi_networks

    try:
        result = subprocess.check_output(
            ["iwlist", "wlan0", "scan"],
            stderr=subprocess.DEVNULL
        ).decode("utf-8")

        cells = result.split("Cell ")
        networks = []

        for cell in cells[1:]:
            ssid_match = re.search(r'ESSID:"(.*?)"', cell)
            signal_match = re.search(r"Signal level=(-?\d+)", cell)

            if ssid_match and signal_match:
                ssid = ssid_match.group(1)
                signal = int(signal_match.group(1))
                networks.append((ssid, signal))

        wifi_networks = networks

    except Exception:
        wifi_networks = []

def wifi_update(dt):
    global wifi_last_scan

    if time.time() - wifi_last_scan > 5:
        scan_wifi()
        wifi_last_scan = time.time()

def wifi_draw():
    width, height = screen.get_size()
    screen.fill((5,10,5))

    green = (0,255,120)
    orange = (255,140,0)

    title = font.render("WIRELESS SIGNAL SCANNER", True, orange)
    screen.blit(title, (40,30))

    y = 100
    bar_x = 100

    for ssid, signal in wifi_networks:
        # Convert RSSI (-90 to -30) into strength %
        strength = max(0, min(100, 2 * (signal + 100)))

        pygame.draw.rect(screen, green, (bar_x, y, strength*3, 25))
        pygame.draw.rect(screen, orange, (bar_x, y, 300, 25), 2)

        label = font.render(f"{ssid}  ({signal} dBm)", True, green)
        screen.blit(label, (bar_x + 320, y))

        y += 50

#sniffing
STATE_SNIFFER = 10
sniffer_active = False
sniffer_logs = []
sniffer_running = False
packet_count = 0

def sniffer_start():
    global sniffer_running
    sniffer_running = True
    sniffer_logs.append("[+] Sniffer started")

def sniffer_stop():
    global sniffer_running
    sniffer_running = False
    sniffer_logs.append("[!] Sniffer stopped")

def sniffer_update(dt):
    global packet_count

    if sniffer_running:
        if random.random() < 0.15:
            packet_count += 1

            proto = random.choice(["TCP", "UDP", "ICMP"])
            src = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"
            dst = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"
            port = random.randint(1000, 9000)
            length = random.randint(64, 1500)

            log = f"{time.strftime('%H:%M:%S')} {proto} {src}:{port} > {dst}:{port} Len={length}"
            sniffer_logs.append(log)

def sniffer_draw():
    global start_rect, stop_rect

    width, height = screen.get_size()
    screen.fill((10, 5, 2))

    orange = (255,140,0)
    green = (0,255,120)

    # Title
    screen.blit(font.render("CYBER SNIFFER CONTROL PANEL", True, orange), (40,30))
    screen.blit(font.render(f"Packets Captured: {packet_count}", True, green), (40,70))

    # Buttons
    button_y = 120
    button_w = 160
    button_h = 50
    gap = 40

    start_rect = pygame.Rect(60, button_y, button_w, button_h)
    stop_rect  = pygame.Rect(60 + button_w + gap, button_y, button_w, button_h)

    pygame.draw.rect(screen, orange, start_rect, 2)
    pygame.draw.rect(screen, orange, stop_rect, 2)

    screen.blit(font.render("START", True, orange), (start_rect.x+40, start_rect.y+12))
    screen.blit(font.render("STOP", True, orange), (stop_rect.x+50, stop_rect.y+12))

    # Log Panel
    panel_y = 200
    panel_rect = pygame.Rect(60, panel_y, width-120, height-panel_y-40)
    pygame.draw.rect(screen, orange, panel_rect, 2)

    y = panel_y + 20
    for line in sniffer_logs[-20:]:
        screen.blit(font.render(line, True, green), (panel_rect.x+20, y))
        y += 22

class VirtualJoystick:
    def __init__(self, screen, center_ratio=(0.17, 0.75), radius_ratio=0.12, dead_zone=0.12):
    
        self.screen = screen
        self.cx_ratio, self.cy_ratio = center_ratio
        self.radius_ratio = radius_ratio
        self.dead_zone = dead_zone
        self.active = False
        self.pointer_id = None  # track finger id if touch
        self._recalc()

    def _recalc(self):
        sw, sh = self.screen.get_size()
        base = min(sw, sh)
        self.radius = int(base * self.radius_ratio)
        self.center = (int(sw * self.cx_ratio), int(sh * self.cy_ratio))
        self.knob_pos = self.center
        self.norm = (0.0, 0.0)  # normalized vector -1..1

    def handle_event(self, event):
        # convert finger coords (0..1) to screen pixels
        if event.type == pygame.FINGERDOWN:
            x = int(event.x * self.screen.get_width())
            y = int(event.y * self.screen.get_height())
            if self._point_in_base(x, y):
                self.active = True
                self.pointer_id = ('finger', event.finger_id)
                self._update_knob(x, y)
        elif event.type == pygame.FINGERMOTION:
            if self.pointer_id == ('finger', event.finger_id):
                x = int(event.x * self.screen.get_width())
                y = int(event.y * self.screen.get_height())
                self._update_knob(x, y)
        elif event.type == pygame.FINGERUP:
            if self.pointer_id == ('finger', event.finger_id):
                self._reset()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in (1,):  # left click
                x, y = event.pos
                if self._point_in_base(x, y):
                    self.active = True
                    self.pointer_id = ('mouse', 'left')
                    self._update_knob(x, y)
        elif event.type == pygame.MOUSEMOTION:
            if self.active and self.pointer_id and self.pointer_id[0] == 'mouse' and pygame.mouse.get_pressed()[0]:
                x, y = event.pos
                self._update_knob(x, y)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button in (1,) and self.pointer_id and self.pointer_id[0] == 'mouse':
                self._reset()


    def _point_in_base(self, x, y):
        cx, cy = self.center
        return (x - cx) ** 2 + (y - cy) ** 2 <= (self.radius * 1.2) ** 2

    def _update_knob(self, x, y):
        cx, cy = self.center
        dx = x - cx
        dy = y - cy
        dist = math.hypot(dx, dy)
        if dist > self.radius:
            # clamp to circle edge
            factor = self.radius / dist
            dx *= factor
            dy *= factor
            dist = self.radius
        # normalized -1..1
        nx = dx / self.radius
        ny = dy / self.radius
        # apply dead zone
        if math.hypot(nx, ny) < self.dead_zone:
            nx = ny = 0.0
        self.norm = (nx, ny)
        self.knob_pos = (int(cx + dx), int(cy + dy))

    def _reset(self):
        self.active = False
        self.pointer_id = None
        self.knob_pos = self.center
        self.norm = (0.0, 0.0)

    def get_vector(self) -> Tuple[float, float]:
        """Return (x, y) normalized vector in range -1..1 (x right, y down)"""
        return self.norm

    def draw(self):
        cx, cy = self.center
        pygame.draw.circle(self.screen, (30, 30, 40), (cx, cy), self.radius)
        pygame.draw.circle(self.screen, (90, 90, 110), (cx, cy), self.radius, 3)
        dead_r = max(2, int(self.radius * self.dead_zone))
        pygame.draw.circle(self.screen, (50, 50, 60), (cx, cy), dead_r, 1)
        pygame.draw.circle(self.screen, (170, 170, 200), self.knob_pos, int(self.radius * 0.45))
        pygame.draw.circle(self.screen, (40, 40, 50), self.knob_pos, int(self.radius * 0.45), 2)


class VirtualButton:
    def __init__(self, screen, rect_ratio=(0.8, 0.72, 0.14, 0.12), label="A"):
        self.screen = screen
        self.rx_ratio, self.ry_ratio, self.rw_ratio, self.rh_ratio = rect_ratio
        self.label = label
        self.pressed = False
        self.pointer_id = None
        self._recalc()

    def _recalc(self):
        sw, sh = self.screen.get_size()
        self.rect = pygame.Rect(
            int(sw * self.rx_ratio),
            int(sh * self.ry_ratio),
            int(sw * self.rw_ratio),
            int(sh * self.rh_ratio)
        )

    def handle_event(self, event):
        if event.type == pygame.FINGERDOWN:
            x = int(event.x * self.screen.get_width())
            y = int(event.y * self.screen.get_height())
            if self.rect.collidepoint(x, y):
                self.pressed = True
                self.pointer_id = ('finger', event.finger_id)
        elif event.type == pygame.FINGERMOTION:
            if self.pointer_id and self.pointer_id[0] == 'finger':
                x = int(event.x * self.screen.get_width())
                y = int(event.y * self.screen.get_height())
                if not self.rect.collidepoint(x, y):
                    self.pressed = False
        elif event.type == pygame.FINGERUP:
            if self.pointer_id == ('finger', event.finger_id):
                self.pressed = False
                self.pointer_id = None
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.pressed = True
                    self.pointer_id = ('mouse', 'left')
        elif event.type == pygame.MOUSEMOTION:
            if self.pointer_id and self.pointer_id[0] == 'mouse':
                buttons = pygame.mouse.get_pressed()
                if not buttons[0]:
                    self.pressed = False
                    self.pointer_id = None
                else:
                    if not self.rect.collidepoint(pygame.mouse.get_pos()):
                        self.pressed = False
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.pointer_id and self.pointer_id[0] == 'mouse':
                self.pressed = False
                self.pointer_id = None

    def is_pressed(self) -> bool:
        return self.pressed

    def draw(self):
        col = (200, 70, 70) if self.pressed else (80, 80, 90)
        pygame.draw.rect(self.screen, col, self.rect, border_radius=8)
        pygame.draw.rect(self.screen, (30, 30, 40), self.rect, 2, border_radius=8)
        # label
        font = pygame.font.SysFont(None, max(16, int(self.rect.height * 0.45)))
        txt = font.render(self.label, True, (240, 240, 240))
        tw, th = txt.get_size()
        tx = self.rect.centerx - tw // 2
        ty = self.rect.centery - th // 2
        self.screen.blit(txt, (tx, ty))

def parse_wifi_log():
    global wifi_scan_results
    wifi_scan_results = []

    log_path = None
    for ext in (".txt", ".log"):
        candidate = os.path.join("logs", "wifi" + ext)
        if os.path.exists(candidate):
            log_path = candidate
            break

    if log_path is None:
        return

    with open(log_path, "r", errors="ignore") as f:
        lines = f.readlines()

    for ln in lines:
        ln = ln.strip()
        m = re.match(r"^\s*\d+:\s+([0-9A-Fa-f:]{11,17})\s+(\d+)\s+(-?\d+)\s+(.*)$", ln)
        if not m:
            continue

        bssid, ch, rssi, ssid = m.groups()
        try:
            rssi_val = int(rssi)
        except ValueError:
            continue

        wifi_scan_results.append({
            "ssid": ssid.strip(),
            "bssid": bssid,
            "rssi": rssi_val,
            "channel": ch,
            "auth": ""
        })

    wifi_scan_results.sort(key=lambda x: -x["rssi"])

# CONFIG
TITLE = "Uzumaki - Spiral City"
FPS = 60
FULLSCREEN = False
screen = pygame.display.set_mode((0,0))
SCREEN_W, SCREEN_H = screen.get_size()


WORLD_W, WORLD_H = 3200, 2200
TILE = 64

PLAYER_SPEED = 170.0   
PLAYER_SIZE = 48
SHRINE_SIZE = 52
INTERACT_DIST = 96

SIDEBAR_W = 260
MINIMAP_R = 84

COL_BG = (12,12,18)
COL_UI = (190,190,210)
COL_ACC = (200,40,40)

STATE_MENU, STATE_PLAYING, STATE_ENDING, STATE_PAUSE, STATE_GAMEOVER, STATE_LOGS = range(6)

# TOOL SCREEN STATE
STATE_TOOL = 6 

current_tool = None 
current_tool_script = None 
tool_active = False
tool_backgrounded = False  

wifi_scan_results = []     
wifi_status_text = "Idle"

deauth_targets = []  
deauth_running = False
deauth_power = 6   
deauth_status_text = "Idle"


deauth_btn_power = pygame.Rect(0,0,0,0)
deauth_btn_connect = pygame.Rect(0,0,0,0)
deauth_btn_open = pygame.Rect(0,0,0,0)
deauth_btn_off = pygame.Rect(0,0,0,0)


wifi_last_refresh = 0.0
WIFI_REFRESH_INTERVAL = 1.0  


pygame.init(); pygame.font.init(); pygame.mixer.quit(); pygame.joystick.init()
flags = pygame.FULLSCREEN if FULLSCREEN else 0
screen = pygame.display.set_mode((0,0), flags) if FULLSCREEN else pygame.display.set_mode((SCREEN_W, SCREEN_H))
SCREEN_W, SCREEN_H = screen.get_size()
pygame.display.set_caption(TITLE)


world_surface = pygame.Surface(
    (int((SCREEN_W - SIDEBAR_W) / ZOOM), int(SCREEN_H / ZOOM))
)
# VIRTUAL JOYSTICK CONFIG 
USE_VIRTUAL_JOYSTICK = True

clock = pygame.time.Clock()
font = pygame.font.SysFont("DejaVu Sans", 18)
bigfont = pygame.font.SysFont("DejaVu Sans", 44)
smallfont = pygame.font.SysFont("DejaVu Sans", 14)

# UTILS
def clamp(v,a,b): return a if v<a else b if v>b else v

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_image(path):
    if os.path.exists(path):
        try:
            return pygame.image.load(path).convert_alpha()
        except Exception:
            pass
    return None

# CAMERA
class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.shake = 0

    def follow(self, tx, ty):
        view_w = (SCREEN_W - SIDEBAR_W) / ZOOM
        view_h = SCREEN_H / ZOOM

        self.x = clamp(tx - view_w / 2, 0, WORLD_W - view_w)
        self.y = clamp(ty - view_h / 2, 0, WORLD_H - view_h)

    def apply(self, pos):
        ox = random.randint(-self.shake, self.shake) if self.shake > 0 else 0
        oy = random.randint(-self.shake, self.shake) if self.shake > 0 else 0
        return (pos[0] - self.x + ox, pos[1] - self.y + oy)
camera = Camera()

# BACKGROUNDS & COLLISION 
ASSET_DIR = "assets"
fullmap = load_image(os.path.join(ASSET_DIR, "fullmap.png"))
collision_mask_img = None
if fullmap:
    WORLD_W, WORLD_H = fullmap.get_width(), fullmap.get_height()
    cm_path = os.path.join(ASSET_DIR, "collision_mask.png")
    if os.path.exists(cm_path):
        cm = pygame.image.load(cm_path).convert()
        if cm.get_size() == fullmap.get_size():
            collision_mask_img = cm
        else:
            print("collision_mask.png size mismatch — ignored")

tileset = None
if not fullmap:
    ts = load_image(os.path.join(ASSET_DIR, "tileset.png"))
    if ts:
        tileset = [ts.subsurface(((i%4)*TILE, (i//4)*TILE, TILE, TILE)) for i in range(16)]

MAP_C = [["road" if (x%8==3 or y%6==2) else "build" for x in range((WORLD_W//TILE)+3)] for y in range((WORLD_H//TILE)+3)]

def is_walkable(px, py):
    if collision_mask_img is None:
        return True
    x = int(px)
    y = int(py)
 
    if x < 0 or y < 0 or x >= collision_mask_img.get_width() or y >= collision_mask_img.get_height():
        return False
    r, g, b, *rest = collision_mask_img.get_at((x, y))
    if r < 50 and g < 50 and b < 50:
        return False
    return True

def draw_background(surface):
    if fullmap:
        sx, sy = camera.apply((0, 0))
        surface.blit(fullmap, (sx, sy))
        return

    start_tx = int(camera.x // TILE)
    start_ty = int(camera.y // TILE)

    vis_x = int(math.ceil(surface.get_width() / TILE)) + 2
    vis_y = int(math.ceil(surface.get_height() / TILE)) + 2

    for ty in range(start_ty, start_ty + vis_y):
        for tx in range(start_tx, start_tx + vis_x):
            if ty < 0 or tx < 0:
                continue

            kind = MAP_C[ty % len(MAP_C)][tx % len(MAP_C[0])]
            px, py = tx * TILE, ty * TILE
            sx, sy = camera.apply((px, py))

            if tileset:
                tidx = 1 if kind == "road" else 5
                surface.blit(tileset[tidx], (int(sx), int(sy)))
            else:
                col = (44,44,54) if kind=="road" else (28 + int((tx+ty))%3*6, 28 + int((tx+ty))%3*6, 34)
                pygame.draw.rect(surface, col, (int(sx), int(sy), TILE, TILE))

# PLAYER
FRAME_W, FRAME_H = 80, 96

class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.health = 100.0
        self.energy = 100.0

        self.frames = [
            load_image(os.path.join("assets/player_spritesheet1.png")),  
            load_image(os.path.join("assets/player_spritesheet2.png")), 
            load_image(os.path.join("assets/player_spritesheet3.png")),  
            load_image(os.path.join("assets/player_spritesheet4.png")),  
        ]
        self.dir = 0
        self.is_jumping = False
        self.jump_height = 0.0  
        self.jump_speed = 280.0
        self.jump_peak = 40.0
        self.jump_direction = 1  

    def try_move(self, dx, dy, dt):
        nx = self.x + dx * PLAYER_SPEED * dt
        ny = self.y + dy * PLAYER_SPEED * dt

        if self.is_jumping:
            self.x = clamp(nx, 8, WORLD_W - 8)
            self.y = clamp(ny, 8, WORLD_H - 8)
            return

        ok = (
            is_walkable(nx, ny)
            and is_walkable(nx + 12, ny)
            and is_walkable(nx - 12, ny)
            and is_walkable(nx, ny + 12)
            and is_walkable(nx, ny - 12)
        )

        if ok:
            self.x = clamp(nx, 8, WORLD_W - 8)
            self.y = clamp(ny, 8, WORLD_H - 8)

        else:
            if not self.is_jumping and abs(dx) > abs(dy):
                self.is_jumping = True
                self.jump_direction = 1

    def update(self, dt, keys, axes=(0, 0)):
        vx = axes[0]
        vy = axes[1]
        if abs(axes[0]) > 0.2: vx = axes[0]
        if abs(axes[1]) > 0.2: vy = axes[1]
        if vx or vy:
            mag = math.hypot(vx, vy)
            vx /= mag
            vy /= mag
            self.try_move(vx, vy, dt)
            if abs(vx) > abs(vy): self.dir = 2 if vx>0 else 1
            else: self.dir = 0 if vy>0 else 3
        if not self.is_jumping and (keys[pygame.K_SPACE]):
            self.is_jumping = True
            self.jump_direction = 1  
        if self.is_jumping:
            self.jump_height += self.jump_direction * self.jump_speed * dt
            if self.jump_height >= self.jump_peak:
                self.jump_height = self.jump_peak
                self.jump_direction = -1  
            elif self.jump_height <= 0:
                self.jump_height = 0
                self.is_jumping = False

    def draw(self, surf):
        sx, sy = camera.apply((self.x, self.y - self.jump_height))  
        frame_img = self.frames[self.dir]
        if frame_img:
            scale = 0.6
            w = int(FRAME_W * scale)
            h = int(FRAME_H * scale)
            frame_img = pygame.transform.scale(frame_img, (w, h))
            surf.blit(frame_img, (sx - w//2, sy - h//2))
        else:
            pygame.draw.circle(surf, COL_ACC, (int(sx), int(sy)), 12, 2)
            pygame.draw.circle(surf, (230,230,230), (int(sx), int(sy)), 5)
player = Player(WORLD_W * 0.5, WORLD_W * 0.5)

# SHRINES
class Shrine:
    def __init__(self, x, y, label, script, icon_key, on_activate=None):
        self.x=x; self.y=y; self.label=label; self.script=script; self.awakened=False
        self.on_activate = on_activate
        self.icon_key = icon_key
        icon_path = os.path.join(ASSET_DIR, "shrines", f"{icon_key}.png")
        icon = load_image(icon_path)
        self.icon = pygame.transform.smoothscale(icon,(SHRINE_SIZE,SHRINE_SIZE)) if icon else None
    def is_near(self): return abs(player.x-self.x)<INTERACT_DIST and abs(player.y-self.y)<INTERACT_DIST
    def activate(self):
        if self.on_activate:
            self.on_activate()
    def draw(self, surf):
        sx, sy = camera.apply((self.x, self.y))
        if self.icon: surf.blit(self.icon,(sx-SHRINE_SIZE//2, sy-SHRINE_SIZE//2))
        else:
            col = (140,80,180) if not self.awakened else (60,180,80)
            pygame.draw.circle(surf, col, (int(sx), int(sy)), 18, 2)
        if self.is_near():
            surf.blit(font.render("[ENTER] Awaken", True, (230,230,230)), (sx-48, sy-44))
state = STATE_MENU
def open_logs_state():
    global state
    state = STATE_LOGS
shrines = [
    Shrine(WORLD_W*0.16, WORLD_H*0.22, "Spiral of Signals (WiFi)",   "tools/Air.py",  "wifi"),
    Shrine(WORLD_W*0.36, WORLD_H*0.28, "Spiral of Whispers (Sniffer)","tools/packet_sniff.py","sniffer"),
    Shrine(WORLD_W*0.62, WORLD_H*0.24, "Spiral of Silence (Deauth)",  "tools/Deauther.py", "deauth"),
    Shrine(WORLD_W*0.22, WORLD_H*0.66, "Spiral of Deception (Evil)",  "tools/airgeddon.py","eviltwin"),
    Shrine(WORLD_W*0.45, WORLD_H*0.52, "Spiral of Records (Logs)",   "tools/log_viewer.py","logs"),
]

# ENEMIES
class EnemyBase:
    def __init__(self, x, y, img_path, size, base_color=(255, 255, 255)):
        self.x=float(x); self.y=float(y)
        self.img = load_image(img_path)
        self.size=size
        self.base_color = base_color
        if self.img:
            self.img = pygame.transform.smoothscale(self.img, (size, size))
    def move_try(self, dx, dy, speed, dt):
        nx = self.x + dx*speed*dt
        ny = self.y + dy*speed*dt
        if is_walkable(nx, ny):
            self.x, self.y = nx, ny
    def draw(self, surf):
        sx, sy = camera.apply((self.x, self.y))
        if self.img:
            surf.blit(self.img, (int(sx)-self.size//2, int(sy)-self.size//2))
        else:
            pygame.draw.circle(surf, self.base_color, (int(sx), int(sy)), self.size//2)
class Villager(EnemyBase):
    def __init__(self, x, y):
        super().__init__(x, y, os.path.join(ASSET_DIR,"enemies","villager.png"), 40, (220,60,60))
        self.speed = 40.0
        self.damage = 5.0 
        self.detect = 340.0
    def update(self, dt):
        dx = player.x - self.x; dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist < self.detect and dist>1:
            dx/=dist; dy/=dist
        else:
            ang = time.time()*0.35 % (2*math.pi)
            dx, dy = math.cos(ang+id(self)%7)*0.5, math.sin(ang+id(self)%5)*0.5
        self.move_try(dx, dy, self.speed, dt)
        if dist < 28:
            player.health = clamp(player.health - self.damage*dt, 0, 100)
            camera.shake = min(6, camera.shake+1)
        else:
            camera.shake = max(0, camera.shake-1)

class SpiralMonster(EnemyBase):
    def __init__(self, x, y):
        super().__init__(x, y, os.path.join(ASSET_DIR,"enemies","spiral_monster.png"), 48, (170,70,220))
        self.speed = 50.0
        self.burst_damage = 5.0
        self.glitch_t = 0.1
    def update(self, dt):
        dx = player.x - self.x; dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist>1:
            dx/=dist; dy/=dist
        self.glitch_t += dt
        if self.glitch_t > 4.0:
            self.glitch_t = 0.0
            gx = player.x + random.randint(-160,160)
            gy = player.y + random.randint(-160,160)
            if is_walkable(gx, gy):
                self.x, self.y = gx, gy
        self.move_try(dx, dy, self.speed, dt)
        if dist < 30:
            player.health = clamp(player.health - self.burst_damage*dt, 0, 100)
            camera.shake = min(8, camera.shake+1)
        else:
            camera.shake = max(0, camera.shake-1)

def random_walkable_pos(margin=40, tries=200):
    for _ in range(tries):
        x = random.uniform(margin, WORLD_W - margin)
        y = random.uniform(margin, WORLD_H - margin)
        if is_walkable(x, y):
            return x, y
    return WORLD_W*0.5, WORLD_H*0.5

villagers = [Villager(*random_walkable_pos()) for _ in range(3)]
monsters  = [SpiralMonster(*random_walkable_pos()) for _ in range(2)]

# UI for SIDEBAR
def draw_sidebar(surf):
    panel = pygame.Surface((SIDEBAR_W, SCREEN_H), pygame.SRCALPHA)
    panel.fill((10,10,16,230))
    panel.blit(bigfont.render("Shrines", True, COL_UI), (18, 10))
    y=64
    for s in shrines:
        col = (90,220,100) if s.awakened else (190,190,190)
        if s.icon:
            ic = pygame.transform.smoothscale(s.icon, (24,24))
            panel.blit(ic, (18, y))
            panel.blit(font.render(s.label, True, col), (48, y+2))
        else:
            panel.blit(font.render(s.label, True, col), (18, y+2))
        y += 30
    y += 10
    panel.blit(font.render(f"Health: {int(player.health)}", True, COL_UI), (18, y)); y+=22
    panel.blit(font.render(f"Energy: {int(player.energy)}", True, COL_UI), (18, y))
    surf.blit(panel, (SCREEN_W - SIDEBAR_W, 0))


# JOYSTICK
VJ_CENTER = (110, SCREEN_H - 110)
VJ_RADIUS = 72
vj_active = False
vj_pos = VJ_CENTER
mouse_down = False
BTN_SIZE = 72
BTN_JUMP_POS = (SCREEN_W - SIDEBAR_W - 60, SCREEN_H - 60)
BTN_ACT_POS  = (SCREEN_W - SIDEBAR_W - 60, SCREEN_H - 150)
jump_pressed = False
act_pressed = False

def draw_virtual_joystick(surf):
    base = pygame.Surface((VJ_RADIUS*2, VJ_RADIUS*2), pygame.SRCALPHA)
    pygame.draw.circle(base, (30,30,40,150), (VJ_RADIUS, VJ_RADIUS), VJ_RADIUS)
    surf.blit(base, (VJ_CENTER[0]-VJ_RADIUS, VJ_CENTER[1]-VJ_RADIUS))
    pygame.draw.circle(surf, (220,220,220,220), vj_pos, 26)

def get_vj_axis():
    dx = (vj_pos[0] - VJ_CENTER[0]) / VJ_RADIUS
    dy = (vj_pos[1] - VJ_CENTER[1]) / VJ_RADIUS
    return clamp(dx,-1,1), clamp(dy,-1,1)

def draw_buttons(surf):
    pygame.draw.circle(surf, (230,230,230,200), BTN_ACT_POS, BTN_SIZE//2)
    surf.blit(font.render("USE", True, (20,20,20)),
              (BTN_ACT_POS[0]-20, BTN_ACT_POS[1]-10))

    pygame.draw.circle(surf, (230,230,230,200), BTN_JUMP_POS, BTN_SIZE//2)
    surf.blit(font.render("JUMP", True, (20,20,20)),
              (BTN_JUMP_POS[0]-28, BTN_JUMP_POS[1]-10))

# LOG NEXUS (STATE_LOGS)
LOG_DIR = "logs"

def tail_lines(base_name, n=12):
    for ext in (".txt", ".log"):
        path = os.path.join(LOG_DIR, base_name + ext)
        if os.path.exists(path):
            try:
                with open(path, "r", errors="ignore") as f:
                    lines = f.readlines()
                    lines = lines[-int(n):] if len(lines) > int(n) else lines
                return [str(ln).rstrip("\n") for ln in lines]
            except Exception:
                return []
    return []
log_anim_t = 0.0
def draw_log_nexus(dt):
    global log_anim_t
    log_anim_t += dt
    screen.fill((6,6,10))
    for r in range(40, min(SCREEN_W, SCREEN_H)//2, 22):
        a = log_anim_t*0.6 + r*0.03
        cx, cy = SCREEN_W//2, SCREEN_H//2
        px = int(cx + math.cos(a)*r*0.2)
        py = int(cy + math.sin(a)*r*0.2)
        pygame.draw.circle(screen, (12,12,18), (px,py), r, 2)

    pad = 14
    cols = 2
    rows = 3
    panel_w = (SCREEN_W - SIDEBAR_W - pad*(cols+1))//cols
    panel_h = (SCREEN_H - pad*(rows+1))//rows
    panels = [
        ("WiFi Scanner",  "wifi",     "spiral"),
        ("Packet Sniffer","sniffer",  "waves"),
        ("Deauth",        "deauth",   "cracks"),
    ]

    for i,(title, base_name, style) in enumerate(panels):
        cx = i % cols; cy = i // cols
        rx = pad + cx*(panel_w+pad)
        ry = pad + cy*(panel_h+pad)
        lines = tail_lines(base_name, 10)
        if not lines:
            if "WiFi" in title:
                lines = ["[awaiting scan output]","tip: logs/wifi.txt"]
            elif "Sniffer" in title:
                lines = ["[sniffing paused]","tip: logs/sniffer.txt"]
            elif "Deauth" in title:
                lines = ["[no bursts yet]","tip: logs/deauth.txt"]
            elif "Evil Twin" in title:
                lines = ["[twin not active]","tip: logs/eviltwin.txt"]
            elif "RFID" in title:
                lines = ["[no tags read]","tip: logs/rfid.txt"]
            else:
                lines = ["[idle]","tip: logs/nfc.txt"]
        draw_panel((rx, ry, panel_w, panel_h), title, lines, style, t=log_anim_t)

    header = bigfont.render(" ", True, COL_ACC)
    screen.blit(header, (pad, SCREEN_H - header.get_height() - 8))
    screen.blit(font.render("Press ENTER or ESC to return", True, COL_UI), (pad, SCREEN_H - 34))

# WIFI TOOL-
WIFI_LOG = os.path.join(LOG_DIR, "wifi.log")
AIR_SCRIPT = os.path.join("tools", "Air.py")

def start_air_scan():
    def _run():
        if os.path.exists(AIR_SCRIPT):
            try:
                subprocess.call(["python3", AIR_SCRIPT])
            except Exception as e:
                print("Air.py error:", e)
        else:
            print("Air.py not found at", AIR_SCRIPT)
    threading.Thread(target=_run, daemon=True).start()

def load_wifi_from_log():
    global wifi_scan_results
    wifi_scan_results = []
    if not os.path.exists(WIFI_LOG):
        return
    try:
        with open(WIFI_LOG, "r", errors="ignore") as f:
            lines = f.readlines()
    except Exception as e:
        print("wifi.log read error:", e)
        return
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        m = re.match(r"^\s*\d+:\s+([0-9A-Fa-f:]{11,17})\s+(\d+)\s+(-?\d+)\s+(.*)$", ln)
        if m:
            bssid, ch, rssi, ssid = m.groups()
            try:
                rssi_val = int(rssi)
            except ValueError:
                rssi_val = -90
            wifi_scan_results.append({
                "ssid": ssid.strip(),
                "bssid": bssid,
                "rssi": rssi_val,
                "channel": ch,
                "auth": "",
            })
            continue
        wifi_scan_results.append({
            "ssid": str(ln)[:32],
            "bssid": "",
            "rssi": -80,
            "channel": "",
            "auth": "",
        })
    wifi_scan_results.sort(key=lambda x: x["rssi"], reverse=True)

# TOOL HELPERS, HUD 

def open_tool(tool_key, script_path=None):
    global current_tool, current_tool_script, tool_active, tool_backgrounded
    current_tool = tool_key
    current_tool_script = script_path
    tool_active = True
    tool_backgrounded = False
    if tool_key == "wifi":
        if script_path:
            run_tool(script_path)
        parse_wifi_log()
    elif tool_key == "deauth":
        _simulate_deauth_targets()

def close_tool():
    try: deauther_power_off_and_close()
    except: pass
    global current_tool, current_tool_script, tool_active, deauth_running
    if deauth_running:
        _stop_deauth()
    current_tool = None
    current_tool_script = None
    tool_active = False

def _simulate_deauth_targets():
    global deauth_targets
    scan_list = wifi_scan_results[:6] if len(wifi_scan_results) > 0 else []
    for i, w in enumerate(scan_list):
        deauth_targets.append({
            "ssid": w["ssid"],
            "bssid": w["bssid"],
            "rssi": w["rssi"],
            "selected": False
        })

def _start_deauth():
    global deauth_running
    deauth_running = True
    try:
        deauther_power_on()
        deauther_open()  # type: ignore
    except Exception:
        pass
    if current_tool_script:
        run_tool(current_tool_script)
    try:
        os.makedirs('logs', exist_ok=True)
        with open('logs/deauth.log', 'a', encoding="utf-8") as f:
            f.write(f"{time.asctime()}: Deauth started (power={deauth_power})\n")
            f.flush()
            os.fsync(f.fileno())
    except Exception as e:
        print("log write error:", e)

def _stop_deauth():
    global deauth_running
    deauth_running = False
    try:
        deauther_power_off_and_close()
    except Exception:
        pass
    try:
        os.makedirs('logs', exist_ok=True)
        with open('logs/deauth.log', 'a', encoding="utf-8") as f:
            f.write(f"{time.asctime()}: Deauth stopped\n")
            f.flush()
            os.fsync(f.fileno())
    except Exception as e:
        print("log write error:", e)
        
def deauth_draw():
    width, height = screen.get_size()
    screen.fill((20,5,5))

    red = (255,60,60)

    screen.blit(font.render("DEAUTH CONTROL PANEL", True, red), (40,30))

    pygame.draw.rect(screen, red, start_rect, 2)
    pygame.draw.rect(screen, red, stop_rect, 2)

    screen.blit(font.render("START", True, red), (start_rect.x+40, start_rect.y+12))
    screen.blit(font.render("STOP", True, red), (stop_rect.x+50, stop_rect.y+12))
# HUD drawing helpers
def draw_tool_hud(dt):
    global deauth_btn_power, deauth_btn_connect, deauth_btn_open, deauth_btn_off
    overlay = pygame.Surface((SCREEN_W, SCREEN_H))
    overlay.set_alpha(210)
    overlay.fill((6, 6, 10))
    screen.blit(overlay, (0, 0))

    pad_w = 80
    pad_h = 60
    panel_w = SCREEN_W - pad_w * 2
    panel_h = SCREEN_H - pad_h * 2
    px, py = pad_w, pad_h

    pygame.draw.rect(screen, (40, 28, 20), (px, py, panel_w, panel_h))
    pygame.draw.rect(screen, (90, 60, 40), (px + 6, py + 6, panel_w - 12, panel_h - 12), 2)

    title = f"  {current_tool.upper() if current_tool else 'TOOL'}  "
    screen.blit(bigfont.render(title, True, (220, 220, 200)), (px + 18, py + 10))

    inner_x = px + 24
    inner_y = py + 64
    inner_w = panel_w - 48
    inner_h = panel_h - 100

    if current_tool == "wifi":
        left_w = int(inner_w * 0.55)
        bx, by, bw, bh = inner_x, inner_y, left_w, inner_h
        pygame.draw.rect(screen, (26, 22, 18), (bx, by, bw, bh))
        pygame.draw.rect(screen, (60, 60, 70), (bx + 6, by + 6, bw - 12, bh - 12), 2)

        y = by + 12
        for net in wifi_scan_results:
            r = net["rssi"]
            bar_len = max(6, min(bw - 160, int(((-30 - r) / 65.0) * (bw - 160))))
            ssid = net["ssid"] if net["ssid"] else "<hidden>"
            bssid = net["bssid"]
            screen.blit(font.render(ssid[:32], True, (230, 230, 230)), (bx + 14, y))
            pygame.draw.rect(screen, (30, 200, 240), (bx + bw - 120, y + 4, bar_len, 10))
            screen.blit(smallfont.render(bssid, True, (160, 160, 160)), (bx + 14, y + 18))
            screen.blit(smallfont.render(f"{net['rssi']} dBm ch {net['channel']}", True, (160, 160, 160)),
                        (bx + 14, y + 32))
            y += 40
            if y > by + bh - 40:
                break
        rx = bx + bw + 12
        rw = inner_w - (rx - inner_x)
        pygame.draw.rect(screen, (18, 18, 22), (rx, inner_y, rw, inner_h))

        gy = inner_y + 18
        screen.blit(font.render("Signal Spectrum", True, (220, 220, 220)), (rx + 12, gy))
        gy += 28

        graph_h = int(inner_h * 0.45)
        graph_rect = pygame.Rect(rx + 12, gy, rw - 24, graph_h)
        pygame.draw.rect(screen, (10, 10, 16), graph_rect)
        pygame.draw.rect(screen, (70, 70, 90), graph_rect, 1)

        if wifi_scan_results:
            step = max(1, len(wifi_scan_results) // max(1, graph_rect.width // 4))
            x = graph_rect.left + 8
            for i, net in enumerate(wifi_scan_results[::step]):
                r = net["rssi"]
                norm = max(0.0, min(1.0, (r + 90) / 60.0))  
                h = int(norm * (graph_rect.height - 10))
                pygame.draw.line(
                    screen,
                    (40, 200, 200),
                    (x, graph_rect.bottom - 4),
                    (x, graph_rect.bottom - 4 - h),
                    2,
                )
                x += 6

        gy = graph_rect.bottom + 16
        screen.blit(font.render("Status:", True, (220, 220, 220)), (rx + 12, gy))
        screen.blit(font.render(wifi_status_text, True, (200, 200, 160)), (rx + 100, gy))
        gy += 32
        screen.blit(smallfont.render("[TAB] Rescan via Air.py", True, (200, 200, 200)), (rx + 12, gy))

        screen.blit(font.render("[ESC] Close", True, (220, 220, 220)),
                    (px + 26, py + panel_h - 36))

    elif current_tool == "deauth":
        left_w = int(inner_w * 0.45)
        bx, by, bw, bh = inner_x, inner_y, left_w, inner_h
        pygame.draw.rect(screen, (26, 22, 18), (bx, by, bw, bh))
        pygame.draw.rect(screen, (60, 60, 70), (bx + 6, by + 6, bw - 12, bh - 12), 2)

        screen.blit(font.render("ESP Deauther Control", True, (230, 230, 230)), (bx + 12, by + 10))

        btn_w = bw - 24
        btn_h = 46
        bx_btn = bx + 12
        by_btn = by + 48
        gap = 14

        def draw_pixel_button(rect, text, active=True):
            color = (60, 100, 60) if active else (40, 30, 40)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (220, 200, 160), rect, 2)
            tx = rect.x + 12
            ty = rect.y + (rect.h // 2) - 10
            screen.blit(font.render(text, True, (240, 240, 240)), (tx, ty))

        deauth_btn_power   = pygame.Rect(bx_btn, by_btn + 0 * (btn_h + gap), btn_w, btn_h)
        deauth_btn_connect = pygame.Rect(bx_btn, by_btn + 1 * (btn_h + gap), btn_w, btn_h)
        deauth_btn_open    = pygame.Rect(bx_btn, by_btn + 2 * (btn_h + gap), btn_w, btn_h)
        deauth_btn_off     = pygame.Rect(bx_btn, by_btn + 3 * (btn_h + gap), btn_w, btn_h)

        draw_pixel_button(deauth_btn_power,   "POWER ON", True)
        draw_pixel_button(deauth_btn_connect, "CONNECT TO ESP", True)
        draw_pixel_button(deauth_btn_open,    "OPEN WEB UI", True)
        draw_pixel_button(deauth_btn_off,     "POWER OFF", True)

        rx2 = bx + bw + 12
        rw2 = inner_w - (rx2 - inner_x)
        pygame.draw.rect(screen, (18, 18, 22), (rx2, inner_y, rw2, inner_h))

        ly2 = inner_y + 12
        screen.blit(bigfont.render("STATUS", True, (220, 180, 80)), (rx2 + 12, ly2))
        ly2 += 48
        screen.blit(font.render(deauth_status_text, True, (220, 220, 220)), (rx2 + 12, ly2))
        ly2 += 28

        for ln in tail_lines("deauth", 6):
            screen.blit(smallfont.render(ln[:60], True, (180, 180, 180)), (rx2 + 12, ly2))
            ly2 += 18

        screen.blit(font.render("[ESC] Close  [P/C/O/F keys on keyboard]", True, (220, 220, 220)),
                    (px + 26, py + panel_h - 36))

    elif current_tool == "logs":
        draw_log_nexus(dt)
        screen.blit(font.render("[ESC] Back to game", True, (220, 220, 220)),
                    (px + 26, py + panel_h - 36))
    else:
        screen.blit(font.render("Tool not implemented", True, (220, 220, 220)), (px + 30, py + 80))
        screen.blit(font.render("[ESC] Close", True, (200, 200, 200)), (px + 30, py + panel_h - 36))

# STATES
def title_screen():
    screen.fill(COL_BG)
    screen.blit(bigfont.render("UZUMAKI: SPIRAL CITY", True, COL_ACC), (SCREEN_W//2-320, SCREEN_H//2-90))
    screen.blit(font.render("Press ENTER to Begin", True, COL_UI), (SCREEN_W//2-120, SCREEN_H//2+10))
    pygame.display.flip()

def ending_screen():
    screen.fill((0,0,0))
    screen.blit(bigfont.render("THE SPIRAL CONSUMES...", True, COL_ACC), (SCREEN_W//2-320, SCREEN_H//2-20))
    pygame.display.flip(); pygame.time.wait(3500)

def gameover_screen():
    screen.fill((0,0,0))
    screen.blit(bigfont.render("YOU WERE CONSUMED BY THE SPIRAL", True, (220,80,80)), (SCREEN_W//2-460, SCREEN_H//2-20))
    screen.blit(font.render("Press ENTER to retry", True, (220,220,220)), (SCREEN_W//2-120, SCREEN_H//2+40))
    pygame.display.flip()

# MAIN LOOP 
def reset_game():
    global villagers, monsters, state, fullmap, collision_mask_img, wifi_scan_results, deauth_targets, deauth_running
    fullmap = load_image(os.path.join(ASSET_DIR, "fullmap.png"))
    cm_path = os.path.join(ASSET_DIR, "collision_mask.png")
    collision_mask_img = pygame.image.load(cm_path).convert() if os.path.exists(cm_path) else None

    player.x, player.y = WORLD_W*0.5, WORLD_H*0.5
    player.health = 100; player.energy=100
    for s in shrines: s.awakened=False
    villagers = [Villager(*random_walkable_pos()) for _ in range(3)]
    monsters  = [SpiralMonster(*random_walkable_pos()) for _ in range(2)]
    wifi_scan_results = []
    deauth_targets = []
    deauth_running = False
    state = STATE_PLAYING

def handle_input_events(e):
    global mouse_down, vj_active, vj_pos, jump_pressed, act_pressed
    if e.type == pygame.MOUSEBUTTONDOWN:
        mx, my = e.pos
        if tool_active and current_tool == "deauth":
            if deauth_btn_power.collidepoint(mx, my):
                deauther_power_on()
            elif deauth_btn_connect.collidepoint(mx, my):
                deauther_connect_and_open(embedded=False)
            elif deauth_btn_open.collidepoint(mx, my):
                deauther_connect_and_open(embedded=True)
            elif deauth_btn_off.collidepoint(mx, my):
                deauther_power_off_and_close()
            return

        if USE_VIRTUAL_JOYSTICK and (mx - VJ_CENTER[0]) ** 2 + (my - VJ_CENTER[1]) ** 2 <= VJ_RADIUS ** 2:
            vj_active = True
            mouse_down = True
            vj_pos = (mx, my)

        if math.hypot(mx - BTN_JUMP_POS[0], my - BTN_JUMP_POS[1]) < BTN_SIZE // 2:
            jump_pressed = True
        if math.hypot(mx - BTN_ACT_POS[0], my - BTN_ACT_POS[1]) < BTN_SIZE // 2:
            act_pressed = True

    elif e.type == pygame.MOUSEMOTION and mouse_down and vj_active:
        mx, my = e.pos
        dx = mx - VJ_CENTER[0]
        dy = my - VJ_CENTER[1]
        d = math.hypot(dx, dy)
        if d > VJ_RADIUS:
            dx *= VJ_RADIUS / d
            dy *= VJ_RADIUS / d
        vj_pos = (int(VJ_CENTER[0] + dx), int(VJ_CENTER[1] + dy))

    elif e.type == pygame.MOUSEBUTTONUP:
        mouse_down = False
        vj_active = False
        vj_pos = VJ_CENTER
        jump_pressed = False
        act_pressed = False


HAS_AC_BACK = hasattr(pygame, "K_AC_BACK")

# ESP-
ESP_EN_PIN = 17
_embedded_window = None
_embedded_thread = None

def esp_setup():
    if not HAVE_GPIO or GPIO is None:
        print("[ESP] GPIO not available on this platform.")
        return
    GPIO.setmode(GPIO.BCM) # type: ignore
    GPIO.setup(ESP_EN_PIN, GPIO.OUT, initial=GPIO.LOW) # type: ignore

def esp_on():
    print("[*] Powering ESP8266 ON.")
    if HAVE_GPIO and GPIO is not None:
        GPIO.output(ESP_EN_PIN, GPIO.HIGH) # type: ignore
    __time_for_esp.sleep(4)

def esp_off():
    print("[*] Powering ESP8266 OFF.")
    if HAVE_GPIO and GPIO is not None:
        GPIO.output(ESP_EN_PIN, GPIO.LOW) # type: ignore
    __time_for_esp.sleep(0.5)

def connect_to_esp_wifi(ssid="pwned", password="deauther", interface="wlan1"):
    print(f"[ESP] Connecting to ESP8266 WiFi using {interface}…")

    try:
        subprocess.call([
            "nmcli",
            "device",
            "wifi",
            "connect",
            ssid,
            "password",
            password,
            "ifname",
            interface
        ])
    except Exception:
        try:
            os.system(
                f"nmcli device wifi connect '{ssid}' password '{password}' ifname {interface}"
            )
        except Exception:
            print("Warning: nmcli failed; connect manually if needed.")

    __time_for_esp.sleep(4)

def _open_embedded_browser(url="http://192.168.4.1", title="ESP Web UI"):
    global _embedded_window, _embedded_thread
    if not WEBVIEW_AVAILABLE:
        print("pywebview not installed — opening external browser instead.")
        webbrowser.open(url)
        return

    def _create():
        global _embedded_window
        try:
            _embedded_window = webview.create_window(title, url, width=900, height=600, resizable=True)
            webview.start()
        except Exception as e:
            print("Error starting webview:", e)

    _embedded_thread = threading.Thread(target=_create, daemon=True)
    _embedded_thread.start()
    __time_for_esp.sleep(0.5)

def _close_embedded_browser():
    global _embedded_window
    try:
        if _embedded_window and webview is not None:
            try:
                _embedded_window.destroy()  # type: ignore
            except Exception:
                try:
                    for w in webview.windows: # type: ignore
                        w.destroy()
                except Exception:
                    pass
            _embedded_window = None
    except Exception as e:
        print("Error closing embedded browser:", e)

def deauther_power_on():
    global deauth_status_text
    esp_setup()
    esp_on()
    deauth_status_text = "ESP Powered ON"

def deauther_connect_and_open(embedded=True):
    global deauth_status_text
    connect_to_esp_wifi()
    if embedded:
        _open_embedded_browser("http://192.168.4.1")
    else:
        webbrowser.open("http://192.168.4.1")
    deauth_status_text = "ESP Web UI opened"

def deauther_power_off_and_close():
    global deauth_status_text
    _close_embedded_browser()
    esp_off()
    deauth_status_text = "ESP Powered OFF"

def main():
    global state, tool_active, tool_backgrounded, deauth_power
    try:
        esp_setup()
    except Exception:
        pass
    running=True
    state = STATE_MENU
    while running:
        dt = clock.tick(FPS) / 1000.0
        keys = pygame.key.get_pressed()
        vx = 0
        vy = 0

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            vx += 1
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            vx -= 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            vy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            vy += 1
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running=False



            if e.type == getattr(pygame, "WINDOWFOCUSLOST", 0) or (hasattr(pygame, "ACTIVEEVENT") and e.type == pygame.ACTIVEEVENT and getattr(e, "gain",1)==0):
                if tool_active:
                    tool_backgrounded = True
                    if deauth_running:
                        _stop_deauth()
            if e.type == getattr(pygame, "WINDOWFOCUSGAINED", 0) or (hasattr(pygame, "ACTIVEEVENT") and e.type == pygame.ACTIVEEVENT and getattr(e, "gain",0)==1):
                if tool_backgrounded:
                    tool_backgrounded = False

            if e.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
                handle_input_events(e)

            if state == STATE_SNIFFER and e.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if start_rect.collidepoint(mouse_pos):
                    sniffer_start()
                if stop_rect.collidepoint(mouse_pos):
                    sniffer_stop()

            if e.type == pygame.KEYDOWN:
                if state == STATE_SNIFFER and e.key == pygame.K_ESCAPE:
                    state = STATE_PLAYING
                    continue
                if state == STATE_WIFI and e.key == pygame.K_ESCAPE:
                    state = STATE_PLAYING
                    continue
                if HAS_AC_BACK and e.key == pygame.K_AC_BACK:
                    if tool_active:
                        close_tool(); continue
                    
                    if state == STATE_LOGS:
                        state = STATE_PLAYING; continue
                    if state == STATE_PAUSE:
                        state = STATE_PLAYING; continue
                    if state == STATE_PLAYING:
                        state = STATE_PAUSE; continue
                    if state == STATE_MENU:
                        pygame.event.post(pygame.event.Event(pygame.QUIT)); continue

                if tool_active:
                    if e.key == pygame.K_ESCAPE:
                        close_tool(); continue
                    if current_tool == "wifi":
                        if e.key == pygame.K_TAB:
                            if current_tool_script:
                                run_tool(current_tool_script)
                            parse_wifi_log(); continue
                    if current_tool == "deauth":
                        if e.key == pygame.K_TAB:
                            if deauth_targets:
                                deauth_targets[0]["selected"] = not deauth_targets[0]["selected"]
                            continue
                        if e.key == pygame.K_SPACE:
                            if not deauth_running:
                                _start_deauth()
                            else:
                                _stop_deauth()
                            continue

                if state==STATE_MENU and e.key==pygame.K_RETURN:
                    state=STATE_PLAYING
                elif state==STATE_PLAYING and e.key==pygame.K_RETURN:
                    for s in shrines:
                        if s.is_near():
                            if s is not None:
                                if s.on_activate is open_logs_state:
                                    s.activate()
                                elif player.energy >= 20:
                                    player.energy -= 20

                                    if s.icon_key == "wifi":
                                        state = STATE_WIFI

                                    elif s.icon_key == "sniffer":
                                        state = STATE_SNIFFER

                                    elif s.icon_key == "deauth":
                                        open_tool("deauth", s.script)

                                    elif s.icon_key == "logs":
                                        state = STATE_LOGS
            
                                break
                elif e.key==pygame.K_ESCAPE:
                    if state==STATE_PLAYING: state=STATE_PAUSE
                    elif state==STATE_PAUSE: state=STATE_PLAYING
                    elif state==STATE_LOGS: state=STATE_PLAYING
                    elif state in (STATE_ENDING, STATE_GAMEOVER): state=STATE_MENU
                elif state==STATE_GAMEOVER and e.key==pygame.K_RETURN:
                    reset_game()

        if vj_active and USE_VIRTUAL_JOYSTICK:
            axes = get_vj_axis()
        if state == STATE_SNIFFER:
            sniffer_update(dt)
            sniffer_draw()
            pygame.display.flip()
            continue
        if state == STATE_WIFI:
            wifi_update(dt)
            wifi_draw()
            pygame.display.flip()
            continue
        if state==STATE_MENU:
            title_screen(); pygame.display.flip(); continue
        if state==STATE_ENDING:
            ending_screen(); running=False; continue
        if state==STATE_GAMEOVER:
            gameover_screen(); pygame.display.flip(); continue
        if state==STATE_LOGS:
            draw_log_nexus(dt); pygame.display.flip(); continue

        # --- TOOL MODE ---
        if tool_active:
            screen.fill((0,0,0))  # clear screen fully
            draw_tool_hud(dt)
            pygame.display.flip()
            continue


# --- GAME MODE ---
        if USE_VIRTUAL_JOYSTICK and vj_active:
            axes = get_vj_axis()
        else:
            axes = (vx, vy)


        player.update(dt, keys, axes=axes)

        for v in villagers:
            v.update(dt)
        for m in monsters:
            m.update(dt)

        camera.follow(player.x, player.y)

        world_surface.fill(COL_BG)

        draw_background(world_surface)

        for s in shrines: s.draw(world_surface)
        for v in villagers: v.draw(world_surface)
        for m in monsters: m.draw(world_surface)
        player.draw(world_surface)

        scaled_world = pygame.transform.scale(
        world_surface,
        (SCREEN_W - SIDEBAR_W, SCREEN_H)
                                                )

        screen.blit(scaled_world, (0, 0))

        draw_sidebar(screen)

        if not pygame.joystick.get_count() and USE_VIRTUAL_JOYSTICK:
            draw_virtual_joystick(screen)

        draw_buttons(screen)

        pygame.display.flip()
            
        if jump_pressed and not player.is_jumping:
            player.is_jumping = True
            player.jump_direction = 1

        if all(s.awakened for s in shrines if s.on_activate is not open_logs_state):
            state = STATE_ENDING
        if player.health <= 0:
            state = STATE_GAMEOVER

        pygame.display.flip()

    pygame.quit(); sys.exit(0)

# draw_panel
def draw_panel(rect, title, lines, style="default", t=0.0):
    rx, ry, rw, rh = rect

    pygame.draw.rect(screen, (20,20,28), (rx, ry, rw, rh))
    pygame.draw.rect(screen, (100,80,60), (rx+3, ry+3, rw-6, rh-6), 2)
    title = font.render(title, True, (230,230,200))
    screen.blit(title, (rx+10, ry+8))

    if style == "waves":
        for y in range(ry + 40, ry + rh, 12):
            pygame.draw.line(screen, (26,26,36), (rx+5, y), (rx+rw-5, y), 1)

    elif style == "cracks":
        for _ in range(6):
            x = random.randint(rx+8, rx+rw-8)
            y = random.randint(ry+40, ry+rh-8)
            pygame.draw.circle(screen, (40,20,20), (x,y), 1)

    y = ry + 42
    for ln in lines[:(rh-52)//16]:
        text = smallfont.render(ln[:70], True, (200,200,200))
        screen.blit(text, (rx+10, y))
        y += 16


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Fatal:", e)
        pygame.quit(); sys.exit(1)
