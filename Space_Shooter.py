import pygame
import random
import sys
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🚀 Space Defender")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Load assets
player_img = pygame.transform.scale(pygame.image.load("player.png"), (50, 50))
enemy_img = pygame.transform.scale(pygame.image.load("enemy.png"), (50, 50))
bullet_img = pygame.transform.scale(pygame.image.load("bullet.png"), (10, 20))

# Load sounds
try:
    shoot_sound = pygame.mixer.Sound("shoot.wav")
    explosion_sound = pygame.mixer.Sound("explosion.wav")
except:
    shoot_sound = None
    explosion_sound = None

# Font
font = pygame.font.SysFont("Arial", 24)
game_over_font = pygame.font.SysFont("Arial", 64)

# High Score
high_score_file = "highscore.txt"
if os.path.exists(high_score_file):
    with open(high_score_file, "r") as file:
        high_score = int(file.read())
else:
    high_score = 0

# Functions
def draw_text(text, x, y, color=WHITE, font_obj=font):
    screen.blit(font_obj.render(text, True, color), (x, y))

def reset_game():
    return WIDTH // 2, HEIGHT - 60, [], [], 0, 3, random.randint(30, 60)

def game_over_screen(score, high_score):
    screen.fill(BLACK)
    draw_text("GAME OVER", WIDTH//2 - 150, HEIGHT//2 - 100, RED, game_over_font)
    draw_text(f"Score: {score}", WIDTH//2 - 50, HEIGHT//2, WHITE)
    draw_text(f"High Score: {high_score}", WIDTH//2 - 80, HEIGHT//2 + 40, WHITE)
    draw_text("Press [R] to Restart or [Q] to Quit", WIDTH//2 - 180, HEIGHT//2 + 100, WHITE)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            waiting = False
        if keys[pygame.K_q]:
            pygame.quit()
            sys.exit()

# --- Game Variables ---
player_x, player_y, bullets, enemies, score, lives, spawn_timer = reset_game()

# --- Main Game Loop ---
running = True
while running:
    clock.tick(FPS)
    screen.fill(BLACK)

    # --- Events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Controls ---
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= 10
    if keys[pygame.K_RIGHT] and player_x < WIDTH - 50:
        player_x += 10
    if keys[pygame.K_SPACE]:
        if len(bullets) < 5:
            bullets.append([player_x + 20, player_y])
            if shoot_sound:
                shoot_sound.play()

    # --- Update Bullets ---
    for bullet in bullets[:]:
        bullet[1] -= 20
        if bullet[1] < 0:
            bullets.remove(bullet)

    # --- Spawn Enemies ---
    spawn_timer -= 1
    if spawn_timer <= 0:
        x_pos = random.randint(0, WIDTH - 50)
        enemies.append([x_pos, 0])
        spawn_timer = random.randint(30, 60)

    # --- Update Enemies ---
    for enemy in enemies[:]:
        enemy[1] += 2
        if enemy[1] > HEIGHT:
            enemies.remove(enemy)
            lives -= 1
            if lives <= 0:
                if score > high_score:
                    high_score = score
                    with open(high_score_file, "w") as file:
                        file.write(str(high_score))
                game_over_screen(score, high_score)
                player_x, player_y, bullets, enemies, score, lives, spawn_timer = reset_game()

    # --- Collision Detection ---
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if (
                bullet[0] < enemy[0] + 50 and bullet[0] + 10 > enemy[0]
                and bullet[1] < enemy[1] + 50 and bullet[1] + 20 > enemy[1]
            ):
                bullets.remove(bullet)
                enemies.remove(enemy)
                score += 1
                if explosion_sound:
                    explosion_sound.play()
                break

    # --- Draw Everything ---
    screen.blit(player_img, (player_x, player_y))
    for bullet in bullets:
        screen.blit(bullet_img, (bullet[0], bullet[1]))
    for enemy in enemies:
        screen.blit(enemy_img, (enemy[0], enemy[1]))

    draw_text(f"Score: {score}", 10, 10)
    draw_text(f"Lives: {lives}", WIDTH - 100, 10)
    draw_text(f"High Score: {high_score}", WIDTH//2 - 60, 10)

    pygame.display.flip()

pygame.quit()
sys.exit()
