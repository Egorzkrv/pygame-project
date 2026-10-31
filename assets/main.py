import pygame
import sys
import os

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

# Шрифты
font_title = pygame.font.SysFont("Arial", 46, bold=True)
font_button = pygame.font.SysFont("Arial", 24, bold=True)
font_text = pygame.font.SysFont("Arial", 20)

# Загрузка ресурсов
try:
    background_img = pygame.image.load("background.jpeg").convert()
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
except pygame.error:
    # Если файла нет
    print("Внимание: background.jpg не найден, меню будет сплошного цвета.")
    background_img = None


def draw_text(text, font, color, surface, x, y, center=True):
    """Универсальная функция для отрисовки текста"""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

def draw_button(text, x, y, width, height, mouse_pos):
    """Рисует кнопку и проверяет, наведена ли на нее мышь"""
    rect = pygame.Rect(x, y, width, height)
    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, HOVER_COLOR, rect, border_radius=10)
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, rect, border_radius=10)
        
    pygame.draw.rect(screen, WHITE, rect, width=2, border_radius=10)
    draw_text(text, font_button, WHITE, screen, x + width // 2, y + height // 2)
    return rect

def show_main_menu():
    """Экран Главного Меню"""
    running = True
    while running:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        
        if background_img:
            screen.blit(background_img, (0, 0))
        else:
            screen.fill(BLACK)
            
        # Название игры
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

def show_about_screen():
    """Экран 'Об игре' с описанием концепта"""
    running = True
    while running:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        
        screen.fill(BLACK)
        draw_text("КОНЦЕПЦИЯ ИГРЫ", font_title, HOVER_COLOR, screen, WIDTH // 2, 80)
        
        lines = [
            "Вы управляете боевым роботом 'Штурмовик'.",
            "Ваша задача — сдерживать волны инопланетных миньонов и победить Босса.",
            "",
            "Главная особенность игры — элементы жанра Roguelike:",
            "Уничтожая врагов, вы подбираете улучшения (Power Items) и модифицируете оружие.",
            "",
            "Доступные модификаторы:",
            "• Тройной луч — веерная стрельба сразу тремя зарядами.",
            "• Рикошет — снаряды отскакивают от границ экрана, создавая хаос.",
            "• Скорость атаки и урон — прокачка базовых систем штурмовика.",
            "",
            "Проект выполнен в рамках курсовой работы по дисциплине 'АиП'."
        ]
        
        start_y = 160
        for line in lines:
            draw_text(line, font_text, TEXT_COLOR, screen, 50, start_y, center=False)
            start_y += 30
            
        btn_back = draw_button("НАЗАД В МЕНЮ", WIDTH // 2 - 120, 500, 240, 50, mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_back.collidepoint(mouse_pos):
                    running = False
                    
        pygame.display.flip()

def run_game():
    """Заглушка для самого игрового процесса"""
    running = True
    while running:
        clock.tick(FPS)
        screen.fill((20, 20, 40))
        
        draw_text("ИГРОВОЙ ПРОЦЕСС", font_title, WHITE, screen, WIDTH // 2, HEIGHT // 2 - 50)
        draw_text("Тут будет летать наш Штурмовик!", font_text, TEXT_COLOR, screen, WIDTH // 2, HEIGHT // 2 + 10)
        
        btn_back = draw_button("В МЕНЮ", WIDTH // 2 - 120, 450, 240, 50, pygame.mouse.get_pos())
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_back.collidepoint(pygame.mouse.get_pos()):
                    running = False
                    
        pygame.display.flip()

if __name__ == "__main__":
    show_main_menu()
