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
Cinza = (44, 57, 75)
Amarelo = (255, 218, 121)
Amarelo_Escuro = (255, 250, 101)

damage_color1 = [(247, 234, 0),
                  (246, 245, 77),
                   (248, 196, 58)
                 ]
yellow_damage = random.choice(damage_color1)
damage_color2 = [(225, 77, 42),
                  (242, 146, 29),
                   (255, 96, 0)
                 ]
orange_damage = random.choice(damage_color2)
damage_color3 = [(61, 0, 0),
                  (149, 1, 1),
                   (84, 18, 18)
                 ]
red_damage = random.choice(damage_color3)

size_player = 15
last_direction = "up"
speed = 3.5
life = 100

level = 1

start_time = pygame.time.get_ticks()
clock = pygame.time.Clock()

damage = random.randint(10,20)

size_enemy = 15
enemy_color = Cinza
enemy_life = 50
enemy_speed = 1
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
last_munition_box_time = pygame.time.get_ticks()

bullets = []
bullet_size = 5
bullet_speed = 5

ammo_boxes = []
munition = 14
munition_box_size = 7
munition_box_spawn_interval = 31000

tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Zombies In The Beach")

map_size = pygame.Rect(x_map, y_map, size_mapX, size_mapY)
pygame.draw.rect(tela, Amarelo, map_size)

def spawn_munition_box():
    global munition_box
    position_munition_boxX = random.randint(0, size_mapX - munition_box_size)
    position_munition_boxY = random.randint(0, size_mapY - munition_box_size)
    munition_box = pygame.Rect(x_map + position_munition_boxX, y_map + position_munition_boxY, munition_box_size, munition_box_size)
    ammo_boxes.append(munition_box)
    return position_munition_boxX, position_munition_boxY
def draw_munition_box():
    for munition_box in ammo_boxes:
        pygame.draw.rect(tela, Branco, munition_box)
def generate_damage():
    damage_amount = [20, 10, 50]
    damage_chance = [6, 3, 1]
    return random.choices(damage_amount, damage_chance)[0]

def spawn_enemy():
    if len(enemies) >= max_enemies:
        return None, None
    else:
        position_enemyX = random.randint(0, size_mapX - size_enemy)
        position_enemyY = random.randint(0, size_mapY - size_enemy)
        enemy = {
        'rect': pygame.Rect(x_map + position_enemyX, y_map + position_enemyY, size_enemy, size_enemy),
        'life': enemy_life,
        'color': Cinza
    }
        enemies.append(enemy)
        return position_enemyX, position_enemyY
    
def draw_enemies():
    for enemy in enemies:
        enemy_rect = enemy['rect']
        pygame.draw.rect(tela, enemy['color'], enemy_rect)

def update_enemies(player):
    for enemy in enemies:
        enemy_rect = enemy['rect']
        global enemy_speed, enemy_color, damage_color1, damage_color2, damage_color3
        enemy_center = enemy_rect.center
        player_center = player.center

        dx = player_center[0] - enemy_center[0]
        dy = player_center[1] - enemy_center[1]

        angle = math.atan2(-dy, -dx)
        
        enemy_dx = enemy_speed * math.cos(angle)
        enemy_dy = enemy_speed * math.sin(angle)

        enemy_rect.x -= enemy_dx
        enemy_rect.y -= enemy_dy 

        if enemy['life'] < enemy_life:
             update_enemy_color(enemy)
 
                
def spawn_recovery():
    global position_recoveryX, position_recoveryY, last_recovery_spawn_time, recovery_active
    position_recoveryX = random.randint(0, size_mapX - size_recovery)
    position_recoveryY = random.randint(0, size_mapY - size_recovery)
    last_recovery_spawn_time = pygame.time.get_ticks()
    recovery_active = True

def handle_recovery_collision():
    global life, recovery_active
    if life > 0:
        life += 25
        recovery_active = False


def handle_collision(player):
    global life
    collision = False
    for enemy in enemies:
        if player.colliderect(enemy['rect']):
            collision = True
            break

    if collision:
        if life > 0:
            life -= 5

def check_enemy_collision():
    for i, enemy1 in enumerate(enemies):
        for j, enemy2 in enumerate(enemies[i + 1:]):
            enemy1_rect = enemy1['rect']
            enemy2_rect = enemy2['rect']

            if enemy1_rect.colliderect(enemy2_rect):
                dx = enemy1_rect.centerx - enemy2_rect.centerx
                dy = enemy1_rect.centery - enemy2_rect.centery

                half_widths = (enemy1_rect.width + enemy2_rect.width) / 2
                half_heights = (enemy1_rect.height + enemy2_rect.height) / 2

                overlap_x = half_widths - abs(dx)
                overlap_y = half_heights - abs(dy)

                if overlap_x > 0 and overlap_y > 0:
                    if overlap_x > overlap_y:
                        if dx > 0:
                            enemy1_rect.x += overlap_x / 2
                            enemy2_rect.x -= overlap_x / 2
                        else:
                            enemy1_rect.x -= overlap_x / 2
                            enemy2_rect.x += overlap_x / 2
                    else:
                        if dy > 0:
                            enemy1_rect.y += overlap_y / 2
                            enemy2_rect.y -= overlap_y / 2
                        else:
                            enemy1_rect.y -= overlap_y / 2
                            enemy2_rect.y += overlap_y / 2

def draw_bullets():
    for bullet in bullets:
        bullet_rect = pygame.Rect(bullet[0][0], bullet[0][1], bullet_size, bullet_size)
        pygame.draw.rect(tela, Branco, bullet_rect)
def update_enemy_color(enemy):
    global enemy_color
    for enemy in enemies:
        enemy_rect = enemy['rect']
        enemy_color = enemy['color']
        if enemy['life'] < enemy_life:
            enemy_color = yellow_damage
            pygame.draw.rect(tela, enemy_color, enemy_rect) 
            if enemy['life'] <= 35:
                enemy_color = orange_damage
                pygame.draw.rect(tela, enemy_color, enemy_rect)
                if enemy['life'] <= 20:
                    enemy_color = red_damage
                    pygame.draw.rect(tela, enemy_color, enemy_rect)
        else:
            pygame.draw.rect(tela, enemy_color, enemy_rect)
        
def update_bullets():
    global bullets
    new_bullets = []
    for bullet in bullets:
        bullet_rect, bullet_speed_x, bullet_speed_y = bullet
        bullet_rect.x += bullet_speed_x
        bullet_rect.y += bullet_speed_y
        if bullet_rect.x < x_map or bullet_rect.x > x_map + size_mapX or (bullet_rect.y < y_map or bullet_rect.y > y_map + size_mapY):
            continue

        collided = False  

        for enemy in enemies:
            if bullet_rect.colliderect(enemy['rect']):
                damage = generate_damage()
                enemy['life'] -= damage
                if enemy['life'] <= 0:
                    enemies.remove(enemy)
                
                collided = True 
                break

        if not collided:  
            new_bullets.append((bullet_rect, bullet_speed_x, bullet_speed_y))

    bullets = new_bullets

while True:
    tela.fill(Azul)
    pygame.draw.rect(tela, Amarelo, map_size)
    for line in edge:
        pygame.draw.line(tela, Amarelo_Escuro, line[0], line[1], 5)
    player= pygame.Rect(position_playerX + x_map, position_playerY + y_map, size_player, size_player)
    pygame.draw.rect(tela, Verde, player)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_SPACE:
                munition -= 1
                if last_direction == "up":
                    bullet_x = player.centerx - bullet_size // 2  
                    bullet_y = player.top - bullet_size
                    bullet_speed_x = 0
                    bullet_speed_y = -bullet_speed
                elif last_direction == "down":
                    bullet_x = player.centerx - bullet_size // 2
                    bullet_y = player.bottom
                    bullet_speed_x = 0
                    bullet_speed_y = bullet_speed
                elif last_direction == "left":
                    bullet_x = player.left - bullet_size
                    bullet_y = player.centery - bullet_size // 2
                    bullet_speed_x = -bullet_speed
                    bullet_speed_y = 0
                elif last_direction == "right":
                    bullet_x = player.right
                    bullet_y = player.centery - bullet_size // 2
                    bullet_speed_x = bullet_speed
                    bullet_speed_y = 0
                if munition > 0:
                    bullet = pygame.Rect(bullet_x, bullet_y, bullet_size, bullet_size)
                    bullets.append((bullet, bullet_speed_x, bullet_speed_y))

    keys = pygame.key.get_pressed() 
    if keys[K_UP] or keys[K_w]:
        if position_playerY > y_map - size_mapY + size_player:
            position_playerY -= speed
            last_direction = "up"
    if keys[K_DOWN] or keys[K_s]:
        if position_playerY < y_map + size_mapY - size_player:
            position_playerY += speed
            last_direction = "down"
    if keys[K_LEFT] or keys[K_a]:
        if position_playerX > x_map - size_mapX + size_player:
            position_playerX -= speed
            last_direction = "left"
    if keys[K_RIGHT] or keys[K_d]:
        if position_playerX < x_map + size_mapX - size_player:
            position_playerX += speed
            last_direction = "right"

    current_time = pygame.time.get_ticks()
    elapsed_time = (current_time - start_time) // 1000

    if elapsed_time == 30:
        level += 1
        start_time = pygame.time.get_ticks()

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
    if life == 0:
        level = 1
        life = 100
        enemies = []
        position_playerX = size_mapX // 2
        position_playerY = size_mapY // 2
        start_time = pygame.time.get_ticks()

    if current_time - last_enemy_spawn_time >= enemy_spawn_interval:
        spawn_enemy()
        last_enemy_spawn_time = current_time
    
    if current_time - last_munition_box_time >= munition_box_spawn_interval:
        draw_munition_box()
        last_munition_spawn_time = current_time

    draw_enemies()
    draw_munition_box()
    check_enemy_collision()
    update_enemies(player)
    handle_collision(player)
    draw_bullets()
    update_bullets()
    
    score_font = pygame.font.Font(None, 36)

    score_text = score_font.render("Vida: " + str(life), True, Branco)
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
        enemy_speed = 1.2
        update_enemies(player)
    if level == 3:
        max_enemies = 9
        enemy_spawn_interval = 10000/2
        enemy_speed = 1.4
        update_enemies(player)
    if level == 4:
        max_enemies = 10
        enemy_spawn_interval = 10000/2
        enemy_speed = 1.6
        update_enemies(player)
    if level == 5:
        max_enemies = 11
        enemy_spawn_interval = 10000/3
        enemy_speed = 1.8
        update_enemies(player)
    if level == 6:
        max_enemies = 12
        enemy_spawn_interval = 10000/3
        enemy_speed = 2
        update_enemies(player)
    if level == 7:
        max_enemies = 13
        enemy_spawn_interval = 10000/4
        enemy_speed = 2.2
        update_enemies(player)
    if level == 8:
        max_enemies = 14
        enemy_spawn_interval = 10000/4
        enemy_speed = 2.4
        update_enemies(player)
    if level == 9:
        max_enemies = 15
        enemy_spawn_interval = 10000/5
        enemy_speed = 2.6
        update_enemies(player)
    if level == 10:
        max_enemies = 16
        enemy_spawn_interval = 10000/5
        enemy_speed = 2.8
        update_enemies(player)
    if level >= 11:
        max_enemies = 18
        enemy_spawn_interval = 10000/6
        enemy_speed = 3
        update_enemies(player)

    clock.tick(60)
    pygame.display.update()
 