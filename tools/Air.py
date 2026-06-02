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