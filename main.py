
import pygame
import sys
import math
import random
import os

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 26)
big_font = pygame.font.SysFont("Arial", 60)

# ==================== MAPAS ====================
maps = {
    "Dust2": {
        "name": "Dust 2",
        "color": (139, 115, 85),
        "walls": [(200,150,400,20), (700,200,20,400), (300,500,500,20), (900,100,20,300)],
        "bombsite": (1050, 550)
    },
    "Mirage": {
        "name": "Mirage",
        "color": (100, 130, 80),
        "walls": [(250,200,500,20), (800,150,20,400), (150,450,600,20), (950,400,200,20)],
        "bombsite": (300, 300)
    },
    "Inferno": {
        "name": "Inferno",
        "color": (160, 100, 60),
        "walls": [(300,250,450,20), (750,100,20,450), (400,550,400,20), (100,400,150,20)],
        "bombsite": (900, 500)
    }
}

# ==================== VARIABLES GLOBALES ====================
current_map = None
team = None
team_color = None
player = None
round_number = 1
ct_score = 0
t_score = 0
max_rounds = 15
money = 800
bomb_planted = False
bomb_timer = 0
bomb_pos = None

# Armas
weapons = {
    "Glock-18": {"dmg":28,"rate":140,"mag":20,"reload":1800,"speed":1.0,"color":(220,220,0),"name":"Glock-18"},
    "USP-S":    {"dmg":30,"rate":130,"mag":12,"reload":1700,"speed":1.0,"color":(0,120,200),"name":"USP-S"},
    "AK-47":    {"dmg":38,"rate":105,"mag":30,"reload":2200,"speed":0.82,"color":(0,160,0),"name":"AK-47"},
    "M4A1-S":   {"dmg":34,"rate":92,"mag":25,"reload":2100,"speed":0.87,"color":(30,80,220),"name":"M4A1-S"},
    "AWP":      {"dmg":115,"rate":850,"mag":5,"reload":3400,"speed":0.58,"color":(180,0,180),"name":"AWP"},
    "Desert Eagle": {"dmg":58,"rate":210,"mag":7,"reload":1900,"speed":0.92,"color":(255,140,0),"name":"Desert Eagle"},
    "MP9":      {"dmg":22,"rate":65,"mag":30,"reload":1600,"speed":1.05,"color":(0,200,200),"name":"MP9"},
    "Galil AR": {"dmg":31,"rate":120,"mag":35,"reload":2300,"speed":0.85,"color":(100,150,0),"name":"Galil AR"},
    "SSG 08":   {"dmg":78,"rate":650,"mag":10,"reload":2800,"speed":0.75,"color":(150,150,255),"name":"SSG 08"}
}

current_weapon = "M4A1-S"
ammo = weapons[current_weapon]["mag"]
last_shot = 0
reloading = False
reload_start = 0

bots = []
particles = []
walls = []

# ==================== FUNCIONES ====================
def choose_team():
    global team, team_color
    while True:
        screen.fill((10,10,15))
        title = big_font.render("ELIGE TU EQUIPO", True, (255,215,0))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))
        ct = font.render("1 - Counter-Terrorist (CT)", True, (0,100,255))
        t = font.render("2 - Terrorist (T)", True, (200,0,0))
        screen.blit(ct, (WIDTH//2 - 150, 300))
        screen.blit(t, (WIDTH//2 - 150, 380))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: 
                    team, team_color = "CT", (0,100,255)
                    return
                if event.key == pygame.K_2: 
                    team, team_color = "T", (200,0,0)
                    return

def choose_map():
    global current_map, walls
    while True:
        screen.fill((10,10,15))
        title = big_font.render("ELIGE MAPA", True, (255,215,0))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        y = 200
        for i, (m, data) in enumerate(maps.items()):
            text = font.render(f"{i+1} - {data['name']}", True, (255,255,255))
            screen.blit(text, (WIDTH//2 - 100, y))
            y += 80
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: current_map = "Dust2"
                if event.key == pygame.K_2: current_map = "Mirage"
                if event.key == pygame.K_3: current_map = "Inferno"
                if current_map:
                    walls = maps[current_map]["walls"]
                    return

def reset_round():
    global bomb_planted, bomb_timer, ammo
    player["x"], player["y"] = WIDTH//2, HEIGHT//2
    ammo = weapons[current_weapon]["mag"]
    bomb_planted = False
    bomb_timer = 0
    for bot in bots:
        bot["x"] = random.randint(100, WIDTH-100)
        bot["y"] = random.randint(100, HEIGHT-100)
        bot["health"] = 100
        bot["alive"] = True

# ==================== INICIO ====================
choose_team()
choose_map()

player = {"x": WIDTH//2, "y": HEIGHT//2, "health":100, "kills":0, "money":800}

for _ in range(8):
    bots.append({
        "x": random.randint(100, WIDTH-100),
        "y": random.randint(100, HEIGHT-100),
        "health": 100,
        "alive": True,
        "team": "T" if team == "CT" else "CT",
        "color": (200,0,0) if team == "CT" else (0,100,255),
        "last_shot": 0
    })

reset_round()
running = True

while running:
    screen.fill(maps[current_map]["color"])
    mx, my = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                print("🛒 Tienda abierta (en desarrollo)")
            if event.key == pygame.K_r and not reloading:
                reloading = True
                reload_start = pygame.time.get_ticks()
            if event.key == pygame.K_e and team == "T" and not bomb_planted:
                if math.hypot(player["x"] - maps[current_map]["bombsite"][0], 
                             player["y"] - maps[current_map]["bombsite"][1]) < 60:
                    bomb_planted = True
                    bomb_timer = pygame.time.get_ticks()
                    bomb_pos = maps[current_map]["bombsite"]
                    print("💣 Bomba plantada!")

    # Movimiento
    keys = pygame.key.get_pressed()
    speed = weapons[current_weapon]["speed"] * 5.2
    dx = dy = 0
    if keys[pygame.K_w]: dy -= 1
    if keys[pygame.K_s]: dy += 1
    if keys[pygame.K_a]: dx -= 1
    if keys[pygame.K_d]: dx += 1
    if dx or dy:
        length = math.hypot(dx, dy)
        player["x"] += dx / length * speed
        player["y"] += dy / length * speed

    # Colisiones con paredes
    for wall in walls:
        wx, wy, ww, wh = wall
        if (player["x"] > wx and player["x"] < wx+ww and 
            player["y"] > wy and player["y"] < wy+wh):
            player["x"] -= dx / length * speed
            player["y"] -= dy / length * speed

    # Disparo
    if pygame.mouse.get_pressed()[0]:
        now = pygame.time.get_ticks()
        if now - last_shot > weapons[current_weapon]["rate"] and ammo > 0:
            last_shot = now
            ammo -= 1
            angle = math.atan2(my - player["y"], mx - player["x"])
            # Partículas de disparo
            particles.append({"x": player["x"], "y": player["y"], "life": 8, "color": (255,220,100)})

    # ==================== DIBUJO ====================
    # Paredes
    for wall in walls:
        pygame.draw.rect(screen, (80,80,80), wall)

    # Bomb site
    pygame.draw.circle(screen, (255,100,0), maps[current_map]["bombsite"], 35, 5)

    # Jugador
    pygame.draw.circle(screen, team_color, (int(player["x"]), int(player["y"])), 22)

    # Bots
    for bot in bots:
        if bot["alive"]:
            pygame.draw.circle(screen, bot["color"], (int(bot["x"]), int(bot["y"])), 19)

    # Crosshair
    pygame.draw.line(screen, (255,255,255), (mx-18, my), (mx+18, my), 2)
    pygame.draw.line(screen, (255,255,255), (mx, my-18), (mx, my+18), 2)

    # HUD
    hud = font.render(f"{team} | Ronda {round_number} | {ct_score}:{t_score} | Kills: {player['kills']}", True, (255,255,255))
    screen.blit(hud, (20, 20))
    weapon_text = font.render(f"{current_weapon} | {ammo}/{weapons[current_weapon]['mag']}", True, (255,255,255))
    screen.blit(weapon_text, (20, 60))

    pygame.display.flip()
    clock.tick(75)

pygame.quit()
sys.exit()