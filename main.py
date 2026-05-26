import pygame
import sys
import math
import random
from pygame import mixer

# Inicializar Pygame
pygame.init()
mixer.init()

# Configuración de pantalla
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('CS2 Python - Top Down Shooter')
clock = pygame.time.Clock()

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)

# Jugador
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.speed = 5
        self.health = 100
        self.money = 800
        self.weapon = 'pistol'
        self.ammo = 20
        self.max_ammo = 20

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.rect.y += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        # Mantener dentro de la pantalla
        self.rect.clamp_ip(screen.get_rect())

    def shoot(self, mouse_pos):
        if self.ammo > 0:
            self.ammo -= 1
            dx = mouse_pos[0] - self.rect.centerx
            dy = mouse_pos[1] - self.rect.centery
            angle = math.atan2(dy, dx)
            bullet = Bullet(self.rect.centerx, self.rect.centery, angle)
            bullets.add(bullet)
            # Sonido de disparo (simulado)
            print('¡Bang!')
        else:
            print('¡Sin munición!')

# Bala
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 12
        self.angle = angle
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if not screen.get_rect().collidepoint(self.rect.center):
            self.kill()

# Enemigo
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((35, 35))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50)))
        self.speed = 2
        self.health = 50

    def update(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            dx, dy = dx/dist, dy/dist
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed

# Grupos
player = Player()
all_sprites = pygame.sprite.Group(player)
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

for _ in range(8):
    enemy = Enemy()
    enemies.add(enemy)

# Variables del juego
score = 0
round_number = 1
running = True
font = pygame.font.Font(None, 36)
YELLOW = (255, 255, 0)

print('=== CS2 Python Game Iniciado ===')
print('Controles:')
print('WASD / Flechas - Mover')
print('Click izquierdo - Disparar')
print('R - Recargar')

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                player.shoot(pygame.mouse.get_pos())

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                player.ammo = player.max_ammo
                print('Recargando...')

    # Actualizar
    all_sprites.update()
    bullets.update()

    for enemy in enemies:
        enemy.update(player)

    # Colisiones
    hits = pygame.sprite.groupcollide(bullets, enemies, True, False)
    for bullet, hit_enemies in hits.items():
        for enemy in hit_enemies:
            enemy.health -= 25
            if enemy.health <= 0:
                enemy.kill()
                score += 100
                player.money += 200

    # Enemigos tocan jugador
    if pygame.sprite.spritecollide(player, enemies, False):
        player.health -= 1
        if player.health <= 0:
            print('¡Game Over!')
            running = False

    # Dibujar
    screen.fill((20, 20, 30))  # Fondo oscuro

    all_sprites.draw(screen)
    bullets.draw(screen)
    enemies.draw(screen)

    # HUD
    health_text = font.render(f'Vida: {player.health}', True, GREEN)
    ammo_text = font.render(f'Munición: {player.ammo}/{player.max_ammo}', True, YELLOW)
    money_text = font.render(f'Dinero: ${player.money}', True, (255, 215, 0))
    score_text = font.render(f'Puntuación: {score}', True, WHITE)
    round_text = font.render(f'Ronda: {round_number}', True, WHITE)

    screen.blit(health_text, (20, 20))
    screen.blit(ammo_text, (20, 60))
    screen.blit(money_text, (20, 100))
    screen.blit(score_text, (WIDTH - 250, 20))
    screen.blit(round_text, (WIDTH - 150, 60))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
