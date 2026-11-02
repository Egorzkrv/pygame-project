import pygame
import sys
import os
import random
import math

# Инициализация Pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spacetrooper: Planet X")
clock = pygame.time.Clock()
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (10, 10, 30)
BUTTON_COLOR = (45, 55, 72)
HOVER_COLOR = (66, 153, 225)
TEXT_COLOR = (226, 232, 240)
BULLET_COLOR = (255, 221, 0)

# Шрифты
font_title = pygame.font.SysFont("Arial", 46, bold=True)
font_button = pygame.font.SysFont("Arial", 24, bold=True)
font_text = pygame.font.SysFont("Arial", 20)

# Загрузка ресурсов и спрайтов
try:
    background_img = pygame.image.load("background.jpeg").convert()
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
except pygame.error:
    print("Внимание: background.jpeg не найден, меню будет сплошного цвета.")
    background_img = None

# Загрузка спрайтов с проверкой (если картинки нет — временную замену)
def load_sprite(filename, size, fallback_color, is_polygon=False):
    try:
        img = pygame.image.load(filename).convert_alpha()
        return pygame.transform.scale(img, size)
    except pygame.error:
        print(f"Внимание: {filename} не найден, используется стандартная фигура.")
        surf = pygame.Surface(size, pygame.SRCALPHA)
        if is_polygon:
            pygame.draw.polygon(surf, fallback_color, [(size[0]//2, 0), (0, size[1]), (size[0], size[1])])
        else:
            surf.fill(fallback_color)
        return surf

# Загружаем графику игрока, пуль, врагов и бонусов
PLAYER_IMG = load_sprite("player.png", (40, 40), (0, 255, 128), is_polygon=True)
BULLET_IMG = load_sprite("player_beam.png", (8, 16), BULLET_COLOR)
POWER_IMG = load_sprite("power_up.png", (24, 24), (179, 136, 255))


def draw_text(text, font, color, surface, x, y, center=True):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

def draw_button(text, x, y, width, height, mouse_pos):
    rect = pygame.Rect(x, y, width, height)
    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, HOVER_COLOR, rect, border_radius=10)
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, rect, border_radius=10)
        
    pygame.draw.rect(screen, WHITE, rect, width=2, border_radius=10)
    draw_text(text, font_button, WHITE, screen, x + width // 2, y + height // 2)
    return rect

#ИГРОВЫЕ КЛАССЫ (ОБЪЕКТЫ)
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = PLAYER_IMG
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 80)
        self.speed = 5
        self.shoot_delay = 400  # задержка стрельбы в мс
        self.last_shot = pygame.time.get_ticks()
        
        # Характеристики для Roguelike прокачки
        self.damage = 1
        self.triple_shot = False
        self.ricochet = False

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed

        # Границы экрана
        self.rect.clamp_ip(screen.get_rect())

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle=0, can_bounce=False, damage=1):
        super().__init__()
        # Поворачиваем спрайт луча/пули, если есть угол (для тройного выстрела)
        if angle != 0:
            self.image = pygame.transform.rotate(BULLET_IMG, -angle)
        else:
            self.image = BULLET_IMG
            
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.damage = damage
        
        # Расчет векторов движения по углу
        rad = math.radians(angle)
        self.speed_x = 8 * math.sin(rad)
        self.speed_y = -8 * math.cos(rad)
        
        self.can_bounce = can_bounce
        self.bounces = 0

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Реализация модификатора РИКОШЕТ
        if self.can_bounce and self.bounces < 2:
            if self.rect.left <= 0 or self.rect.right >= WIDTH:
                self.speed_x *= -1
                self.bounces += 1
            if self.rect.top <= 0:
                self.speed_y *= -1
                self.bounces += 1
        
        # Удаление пули за границами
        if self.rect.bottom < 0 or self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = random.randint(35, 50)
        
        # Загружаем enemy_easy.png или рисуем ромб, если файла нет
        try:
            base_enemy_img = pygame.image.load("enemy_easy.png").convert_alpha()
            self.image = pygame.transform.scale(base_enemy_img, (self.size, self.size))
        except pygame.error:
            self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, (255, 65, 54), [(self.size//2, 0), (self.size, self.size//2), (self.size//2, self.size), (0, self.size//2)])

        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.size)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.uniform(1.5, 3.5)
        self.hp = 1 if self.size < 42 else 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class PowerItem(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = POWER_IMG
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Выбираем случайное Roguelike-улучшение
        self.type = random.choice(["speed", "damage", "triple", "ricochet"])

    def update(self):
        self.rect.y += 2
        if self.rect.top > HEIGHT:
            self.kill()

#ИГРОВОЙ ПРОЦЕСС
def run_game():
    player = Player()
    
    all_sprites = pygame.sprite.Group(player)
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    power_items = pygame.sprite.Group()

    score = 0
    game_over = False
    
    enemy_spawn_timer = pygame.time.get_ticks()
    spawn_cooldown = 1200  # мс между спавном врагов

    running = True
    while running:
        clock.tick(FPS)
        now = pygame.time.get_ticks()

        #ОБРАБОТКА СОБЫТИЙ
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and game_over:
                running = False

        if not game_over:
            # Автоматическая стрельба при удержании Пробела
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and now - player.last_shot > player.shoot_delay:
                player.last_shot = now
                if player.triple_shot:
                    for angle in [-15, 0, 15]:
                        b = Bullet(player.rect.centerx, player.rect.top, angle, player.ricochet, player.damage)
                        all_sprites.add(b)
                        bullets.add(b)
                else:
                    b = Bullet(player.rect.centerx, player.rect.top, 0, player.ricochet, player.damage)
                    all_sprites.add(b)
                    bullets.add(b)

            # Спавн врагов
            if now - enemy_spawn_timer > spawn_cooldown:
                enemy_spawn_timer = now
                e = Enemy()
                all_sprites.add(e)
                enemies.add(e)

            #ОБНОВЛЕНИЕ ЛОГИКИ ОБЪЕКТОВ
            all_sprites.update()
            power_items.update()

            # СТОЛКНОВЕНИЯ: Пули и Враги
            for bullet in bullets:
                hit_enemies = pygame.sprite.spritecollide(bullet, enemies, False)
                for enemy in hit_enemies:
                    enemy.hp -= bullet.damage
                    bullet.kill()
                    if enemy.hp <= 0:
                        score += 10
                        if random.random() < 0.3:
                            item = PowerItem(enemy.rect.centerx, enemy.rect.centery)
                            power_items.add(item)
                        enemy.kill()

            # СТОЛКНОВЕНИЯ: Штурмовик и Апгрейды
            hit_items = pygame.sprite.spritecollide(player, power_items, True)
            for item in hit_items:
                if item.type == "speed":
                    player.shoot_delay = max(150, player.shoot_delay - 60)
                elif item.type == "damage":
                    player.damage += 1
                elif item.type == "triple":
                    player.triple_shot = True
                elif item.type == "ricochet":
                    player.ricochet = True

            # СТОЛКНОВЕНИЯ: Штурмовик и Враги (Проигрыш)
            if pygame.sprite.spritecollideany(player, enemies):
                game_over = True

        #ОТРИСОВКА ЭКРАНА
        screen.fill((20, 20, 40))
        
        all_sprites.draw(screen)
        
        # Подписываем буквы на бонусах, чтобы игрок знал, какой апгрейд подбирает
        for item in power_items:
            draw_text(item.type[0].upper(), font_text, WHITE, screen, item.rect.centerx, item.rect.centery)

        draw_text(f"СЧЕТ: {score}", font_button, WHITE, screen, 20, 20, center=False)
        
        mods = f"Урон: {player.damage} | Скор. Атаки: {int(1000/player.shoot_delay)}/с"
        if player.triple_shot: 
            mods += " | [Тройной Луч]"
        if player.ricochet: 
            mods += " | [Рикошет]"
        draw_text(mods, font_text, TEXT_COLOR, screen, 20, 55, center=False)

        draw_text("Удержание [ПРОБЕЛ] — Стрельба, [W,A,S,D] — Движение", font_text, TEXT_COLOR, screen, WIDTH - 20, 20, center=False)

        # Экран Game Over
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            draw_text("ШТУРМОВИК УНИЧТОЖЕН", font_title, (255, 65, 54), screen, WIDTH // 2, HEIGHT // 2 - 60)
            draw_text(f"Ваш итоговый счет: {score}", font_button, WHITE, screen, WIDTH // 2, HEIGHT // 2)
            btn_back = draw_button("В ГЛАВНОЕ МЕНЮ", WIDTH // 2 - 120, HEIGHT // 2 + 60, 240, 50, pygame.mouse.get_pos())
            
        pygame.display.flip()

#ЭКРАН "ОБ ИГРЕ"
def show_about_screen():
    running = True
    while running:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(BLACK)
        draw_text("КОНЦЕПЦИЯ ИГРЫ", font_title, HOVER_COLOR, screen, WIDTH // 2, 80)
        
        lines = [
            "Вы управляете боевым роботом 'Штурмовик'.",
            "Ваша задача — сдерживать волны инопланетных миньонов.",
            "",
            "Главная особенность игры — элементы жанра Roguelike:",
            "Уничтожая врагов, вы подбираете улучшения (фиолетовые сферы) и модифицируете системы.",
            "",
            "Доступные модификаторы:",
            "• [T] Тройной луч — веерная стрельба сразу тремя зарядами.",
            "• [R] Рикошет — снаряды отскакивают от левой и правой границ экрана.",
            "• [D] Урон и [S] Скорость атаки — базовая прокачка систем.",
            "",
            "Проект выполнен в рамках курсовой работы по дисциплине 'АиП'."
        ]
        
        start_y = 150
        for line in lines:
            draw_text(line, font_text, TEXT_COLOR, screen, 50, start_y, center=False)
            start_y += 30
            
        btn_back = draw_button("НАЗАД В МЕНЮ", WIDTH // 2 - 120, 520, 240, 50, mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_back.collidepoint(mouse_pos):
                    running = False
                    
        pygame.display.flip()

#ГЛАВНОЕ МЕНЮ
def show_main_menu():
    running = True
    while running:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        
        if background_img:
            screen.blit(background_img, (0, 0))
        else:
            screen.fill(BLACK)
            
        draw_text("SPACETROOPER: PLANET X", font_title, HOVER_COLOR, screen, WIDTH // 2, 120)
        
        btn_start = draw_button("ИГРАТЬ", WIDTH // 2 - 120, 250, 240, 50, mouse_pos)
        btn_about = draw_button("ОБ ИГРЕ", WIDTH // 2 - 120, 330, 240, 50, mouse_pos)
        btn_exit = draw_button("ВЫХОД", WIDTH // 2 - 120, 410, 240, 50, mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_start.collidepoint(mouse_pos):
                    run_game()
                elif btn_about.collidepoint(mouse_pos):
                    show_about_screen()
                elif btn_exit.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()
                    
        pygame.display.flip()

if __name__ == "__main__":
    show_main_menu()
