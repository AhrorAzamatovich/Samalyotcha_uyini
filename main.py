import pygame
import random
import sys

# pip install pygame --target=.

# Pygame dasturini ishga tushirish
pygame.init()

# O'yin oynasi o'lchamlari
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Ranglar
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# O'yin oynasini yaratish
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Samalyotcha O'yini by Ahrorazamatovich")

# Sozlamalar
clock = pygame.time.Clock()
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 50
BULLET_WIDTH = 5
BULLET_HEIGHT = 10
FPS = 60

# O'yinchi boshlang'ich pozitsiyasi
player_x = SCREEN_WIDTH // 2
player_y = SCREEN_HEIGHT - 100
player_speed = 7

# Formula 1 avtomobillar ro'yxati
cars = []
car_speed = 5  # Oddiy avtomobillar tezligi

# O'q ro'yxati
bullets = []
bullet_speed = 20
last_shot_time = 0  # Oxirgi o'q otish vaqti
shot_interval = 200  # Milisekundlarda otishlar orasidagi vaqt oralig'i

# Rasm fayllarini yuklash
player_car_image = pygame.image.load("1.png")
player_car_image = pygame.transform.scale(player_car_image, (PLAYER_WIDTH, PLAYER_HEIGHT))

enemy_car_image = pygame.image.load("3.png")
enemy_car_image = pygame.transform.scale(enemy_car_image, (PLAYER_WIDTH, PLAYER_HEIGHT))

# Font sozlamalari
font = pygame.font.SysFont(None, 36)

# Ochkolar
score = 0


# Avtomobil qo'shish funksiyasi
def add_car():
    x_pos = random.randint(0, SCREEN_WIDTH - PLAYER_WIDTH)
    y_pos = -PLAYER_HEIGHT
    car_rect = pygame.Rect(x_pos, y_pos, PLAYER_WIDTH, PLAYER_HEIGHT)
    cars.append(car_rect)

# O'yinni tugatish funksiyasi
def game_over():
    font_big = pygame.font.SysFont(None, 75)
    text = font_big.render("Yutqazdingiz!", True, RED)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))

    restart_text = font.render(f"Qayta boshlash uchun istalgan tugmani bosing {score} ochko", True, BLACK)
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    pygame.display.flip()

    wait_for_keypress()

def wait_for_keypress():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:  # Istalgan tugmani bosish
                game_loop()



# O'yin tsikli
def game_loop():
    global score, car_speed, player_x, cars, player_speed, bullets, last_shot_time, shot_interval

    # O'yin boshlang'ich sozlamalari
    score = 0
    car_speed = 5
    cars = []
    bullets = []
    player_x = SCREEN_WIDTH // 2
    player_speed = 7
    shot_interval = 200
    while True:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


        # O'yinchi harakati
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_a] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < SCREEN_WIDTH - PLAYER_WIDTH:
            player_x += player_speed
        if keys[pygame.K_d] and player_x < SCREEN_WIDTH - PLAYER_WIDTH:
            player_x += player_speed
        
        if keys[pygame.K_SPACE]:  # O'q otish
            current_time = pygame.time.get_ticks()
            if current_time - last_shot_time > shot_interval: 
                bullet_rect = pygame.Rect(
                    player_x + PLAYER_WIDTH // 2 - BULLET_WIDTH // 2,
                    player_y,
                    BULLET_WIDTH,
                    BULLET_HEIGHT,
                )
                bullets.append(bullet_rect)
                last_shot_time = current_time
        

        # O'yinchi avtomobilini chizish
        player_rect = pygame.Rect(player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT)
        screen.blit(player_car_image, (player_x, player_y))

        # Har bir tsiklda yangi oddiy avtomobil qo'shish
        if random.randint(1, 20) == 1:
            add_car()

        # Oddiy avtomobillarni yangilash
        for car in cars[:]:
            car.y += car_speed
            if car.colliderect(player_rect):
                game_over()
            if car.y > SCREEN_HEIGHT:
                cars.remove(car)
                score += 10
                if score % 10 == 0:
                    car_speed += 0.025
                    player_speed += 0.0125
                    shot_interval -= 0
                   
            screen.blit(enemy_car_image, (car.x, car.y))

        # O'q harakatini yangilash
        for bullet in bullets[:]:
            bullet.y -= bullet_speed
            if bullet.y < 0:  # O'q ekrandan chiqib ketganda
                bullets.remove(bullet)
            else:
                for car in cars[:]:  # O'q avtomobilga tekkanda
                    if bullet.colliderect(car):
                        cars.remove(car)
                        bullets.remove(bullet)
                        score += 10
                        break
            pygame.draw.rect(screen, RED, bullet)  # O'qni chizish
            

        # Ochkolarni chizish
        score_text = font.render(f"Ochko: {score} | Tezlik: {int(car_speed)}", True, BLACK)
        screen.blit(score_text, (10, 10))

        # Oynani yangilash
        pygame.display.flip()
        clock.tick(FPS)

# Dasturni boshlash
game_loop()








