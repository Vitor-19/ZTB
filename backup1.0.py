import pygame
from pygame.locals import *
import random
import math
import sys

pygame.init()

altura = 650
largura = 750

game_font = pygame.font.Font(None, 46)

size_mapX = 550
size_mapY = 550

Branco = (245, 246, 250)
Verde = (68, 189, 50)
Azul = (24, 220, 255)
Marrom = (205, 97, 51)
Vermelho = (232, 65, 24)
Cinza = (48, 57, 82)
Amarelo = (255, 250, 101)

size_player = 20
speed = 3
life = 3

level = 1

start_time = pygame.time.get_ticks()
clock = pygame.time.Clock()

size_enemy = 15
enemy_spawn_interval = 10000

size_recovery = 10
last_recovery_spawn_interval = 15000

x_map = (largura - size_mapX) // 2
y_map = (altura - size_mapY) // 2

position_playerX = size_mapX // 2
position_playerY = size_mapY // 2

edge = [
    [[x_map, y_map], [x_map + size_mapX, y_map]],
    [[x_map, y_map], [x_map, y_map + size_mapY]],
    [[x_map, y_map + size_mapY], [x_map + size_mapX, y_map + size_mapY]],
    [[x_map + size_mapX, y_map], [x_map + size_mapX, y_map + size_mapY]]
]

enemies = []
max_enemies = 7

recovery_active = False
last_recovery_spawn_time = pygame.time.get_ticks()
last_enemy_spawn_time = pygame.time.get_ticks()

bullets = []
bullet_size = 5
bullet_speed = 5

tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Game Test")

map_size = pygame.Rect(x_map, y_map, size_mapX, size_mapY)
pygame.draw.rect(tela, Amarelo, map_size)


def spawn_enemy():
    if len(enemies) >= max_enemies:
        return None, None
    else:
        position_enemyX = random.randint(0, size_mapX - size_enemy)
        position_enemyY = random.randint(0, size_mapY - size_enemy)
        enemy = pygame.Rect(x_map + position_enemyX, y_map + position_enemyY, size_enemy, size_enemy)
        enemies.append(enemy)
        return position_enemyX, position_enemyY


def draw_enemies():
    for enemy in enemies:
        pygame.draw.rect(tela, Cinza, enemy)


def update_enemies(player_rect):
    for enemy in enemies:
        enemy_center = enemy.center
        player_center = player_rect.center

        dx = player_center[0] - enemy_center[0]
        dy = player_center[1] - enemy_center[1]

        angle = math.atan2(-dy, -dx)
        enemy_speed = 2
        enemy_dx = enemy_speed * math.cos(angle)
        enemy_dy = enemy_speed * math.sin(angle)

        enemy.x -= enemy_dx
        enemy.y -= enemy_dy


def spawn_recovery():
    global position_recoveryX, position_recoveryY, last_recovery_spawn_time, recovery_active
    position_recoveryX = random.randint(0, size_mapX - size_recovery)
    position_recoveryY = random.randint(0, size_mapY - size_recovery)
    last_recovery_spawn_time = pygame.time.get_ticks()
    recovery_active = True


def handle_recovery_collision():
    global life, recovery_active
    if life > 0:
        life += 1
        recovery_active = False


def handle_collision(player_rect):
    global life
    collision = False
    for enemy in enemies:
        if player_rect.colliderect(enemy):
            collision = True
            break

    if collision:
        if life > 0:
            life -= 1


def check_enemy_collision():
    for i, enemy1 in enumerate(enemies):
        for enemy2 in enemies[i + 1:]:
            if enemy1.colliderect(enemy2):

                dx = enemy1.centerx - enemy2.centerx
                dy = enemy1.centery - enemy2.centery

                half_widths = (enemy1.width + enemy2.width) / 2
                half_heights = (enemy1.height + enemy2.height) / 2

                overlap_x = half_widths - abs(dx)
                overlap_y = half_heights - abs(dy)

                if overlap_x > 0 and overlap_y > 0:

                    if overlap_x > overlap_y:
                        if dx > 0:
                            enemy1.x += overlap_x / 2
                            enemy2.x -= overlap_x / 2
                        else:
                            enemy1.x -= overlap_x / 2
                            enemy2.x += overlap_x / 2
                    else:
                        if dy > 0:
                            enemy1.y += overlap_y / 2
                            enemy2.y -= overlap_y / 2
                        else:
                            enemy1.y -= overlap_y / 2
                            enemy2.y += overlap_y / 2


def draw_bullets():
    for bullet in bullets:
        pygame.draw.rect(tela, Branco, bullet)


def update_bullets():
    for bullet in bullets:
        bullet.x += bullet_speed

    bullets[:] = [bullet for bullet in bullets if bullet.x < x_map + size_mapX]


while True:
    tela.fill(Azul)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_SPACE:
                bullet_x = x_map + position_playerX + size_player 
                bullet_y = y_map + position_playerY + size_player // 2.5
                bullet = pygame.Rect(bullet_x, bullet_y, bullet_size, bullet_size)
                bullets.append(bullet)

    pygame.draw.rect(tela, Amarelo, map_size)
    for line in edge:
        pygame.draw.line(tela, Amarelo, line[0], line[1], 5)

    current_time = pygame.time.get_ticks()
    elapsed_time = (current_time - start_time) // 1000

    if elapsed_time == 30:
        level += 1
        start_time = pygame.time.get_ticks()

    keys = pygame.key.get_pressed()
    if keys[K_w]:
        position_playerY -= speed
    if keys[K_s]:
        position_playerY += speed
    if keys[K_a]:
        position_playerX -= speed
    if keys[K_d]:
        position_playerX += speed

    player = pygame.Rect(x_map + position_playerX, y_map + position_playerY, size_player, size_player)
    pygame.draw.rect(tela, Verde, player)

    if player.left < x_map:
        position_playerX = x_map - x_map
    if player.right > x_map + size_mapX:
        position_playerX = size_mapX - size_player
    if player.top < y_map:
        position_playerY = y_map - y_map
    if player.bottom > y_map + size_mapY:
        position_playerY = size_mapY - size_player

    current_time = pygame.time.get_ticks()

    if not recovery_active and current_time - last_recovery_spawn_time >= last_recovery_spawn_interval:
        spawn_recovery()

    if recovery_active:
        recovery = pygame.Rect(x_map + position_recoveryX, y_map + position_recoveryY, size_recovery, size_recovery)
        pygame.draw.rect(tela, Vermelho, recovery)

        if player.colliderect(recovery):
            handle_recovery_collision()

    if current_time - last_enemy_spawn_time >= enemy_spawn_interval:
        spawn_enemy()
        last_enemy_spawn_time = current_time

    draw_enemies()
    check_enemy_collision()
    update_enemies(player)
    draw_enemies()
    handle_collision(player)

    draw_bullets()
    update_bullets()

    for bullet in bullets:
        for enemy in enemies:
            if bullet.colliderect(enemy):
                bullets.remove(bullet)
                enemies.remove(enemy)
    score_font = pygame.font.Font(None, 36)

    score_text = score_font.render("Vidas: " + str(life), True, Branco)
    score_rect = score_text.get_rect()
    score_rect.topleft = (10, 10)

    tela.blit(score_text, score_rect)

    level_text = score_font.render("Nível: " + str(level), True, Branco)
    level_rect = level_text.get_rect()
    level_rect.topright = (largura - 10, 10)

    tela.blit(level_text, level_rect)

    time_text = score_font.render("Tempo: " + str(elapsed_time), True, Branco)
    time_rect = time_text.get_rect()
    time_rect.centerx = largura // 2
    time_rect.top = score_rect.bottom + (level_rect.top - score_rect.bottom) // 2

    tela.blit(time_text, time_rect)

    if level == 2:
        max_enemies = 8
        enemy_spawn_interval = 10000
    if level == 3:
        max_enemies = 9
        enemy_spawn_interval = 10000/2
    if level == 4:
        max_enemies = 10
        enemy_spawn_interval = 10000/2
    if level == 5:
        max_enemies = 11
        enemy_spawn_interval = 10000/3
    if level == 6:
        max_enemies = 12
        enemy_spawn_interval = 10000/3
    if level == 7:
        max_enemies = 13
        enemy_spawn_interval = 10000/4
    if level == 8:
        max_enemies = 14
        enemy_spawn_interval = 10000/4
    if level == 9:
        max_enemies = 15
        enemy_spawn_interval = 10000/5
    if level == 10:
        max_enemies = 16
        enemy_spawn_interval = 10000/5

    clock.tick(60)
    pygame.time.delay(10)
    pygame.display.update()
 