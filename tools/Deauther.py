#!/usr/bin/env python3
import pygame
import os
import sys
import time
import webbrowser
import RPi.GPIO as GPIO
import threading

# ================= ESP CONFIG =================
ESP_EN_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(ESP_EN_PIN, GPIO.OUT, initial=GPIO.LOW)

def esp_on():
    print("[*] Powering ESP8266 ON...")
    GPIO.output(ESP_EN_PIN, GPIO.HIGH)
    time.sleep(5)

def esp_off():
    print("[*] Powering ESP8266 OFF...")
    GPIO.output(ESP_EN_PIN, GPIO.LOW)
    time.sleep(0.5)

def connect_to_esp_wifi(ssid='pwned', password='deauther'):
    print("Connecting to ESP8266 WiFi...")
    os.system(f"nmcli device wifi connect '{ssid}' password '{password}'")
    time.sleep(5)

def open_esp_web_ui(ip_address="192.168.4.1"):
    print(f"Opening ESP8266 Web UI at http://{ip_address}")
    webbrowser.open(f"http://{ip_address}")


def run_deauther():
    try:
        esp_on()
        connect_to_esp_wifi()
        open_esp_web_ui()
        input("Press Enter to power ESP OFF...")
    except Exception as e:
        print("Error:", e)
    finally:
        esp_off()
        GPIO.cleanup()


# ================= UI SECTION =================
pygame.init()

W,H = 650,350
screen = pygame.display.set_mode((W,H))
pygame.display.set_caption("ESP8266 DEAUTH PANEL")

FONT = pygame.font.SysFont("consolas", 18)
BIG  = pygame.font.SysFont("consolas", 26)

BLACK=(8,8,8)
ORANGE=(255,120,0)
DARK=(30,15,10)
GREEN=(0,255,120)

clock = pygame.time.Clock()
running = True


def splash():
    screen.fill(BLACK)
    screen.blit(BIG.render("BOOTING ESP INTERFACE",True,ORANGE),(160,150))
    pygame.display.flip()
    time.sleep(2)


def draw():
    screen.fill(BLACK)
    pygame.draw.rect(screen,ORANGE,(0,0,W,H),4)

    pygame.draw.rect(screen,DARK,(20,20,260,80))
    pygame.draw.rect(screen,DARK,(20,120,260,190))
    pygame.draw.rect(screen,DARK,(300,20,330,290))

    screen.blit(BIG.render("ESP8266 DEAUTH",True,ORANGE),(30,30))
    button("POWER + CONNECT",40,140)
    button("EXIT",40,190)


def button(txt,x,y):
    pygame.draw.rect(screen,ORANGE,(x,y,200,32),2)
    screen.blit(FONT.render(txt,True,ORANGE),(x+10,y+7))


def launch():
    threading.Thread(target=run_deauther).start()


# ================= RUN =================
splash()

while running:
    draw()

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running=False

        if e.type == pygame.MOUSEBUTTONDOWN:
            mx,my = pygame.mouse.get_pos()
            if 40<=mx<=240 and 140<=my<=172:
                launch()
            if 40<=mx<=240 and 190<=my<=222:
                running=False

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
