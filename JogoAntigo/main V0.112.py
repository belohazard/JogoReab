#começo implementação das jaulas (está dando erro ao abrir menu de pausa, a entrega dos animais sempre da que não tem o animal)
import pygame
from pygame.locals import *
import sys
import random
import math

pygame.init()

width = 1280
height = 720
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Fuga do Zoológico")

white = (255, 255, 255)
font = pygame.font.SysFont(None, 48)
current_screen = None
player_speed = 3000
animal_base_speed = 150
animal_run_speed = 300
elephant_base_speed = 100
elephant_run_speed = 200
tucan_speed = 400
player_size = (50, 70)
menu_options = ["Start Game", "Quit"]
pause_options = ["Continue", "Quit"]
in_menu = True
monkey_count = 0
elephant_count = 0
tucan_count = 0

inventory = []
class Animal:
    def __init__(self, x, y, type):
        self.type = type
        if self.type == 'monkey':
            self.image = pygame.image.load('monkey.png')
            self.speed = animal_base_speed
            self.size = (50, 50)
        elif self.type == 'elephant':
            self.image = pygame.image.load('elephant.png')
            self.speed = elephant_base_speed
            self.size = (80, 80)
        elif self.type == 'tucan':
            self.image = pygame.image.load('tucan.png')
            self.speed = tucan_speed
            self.size = (40, 40)

        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = 0
        self.is_running_away = False

    def update(self, player_rect):
        distance_x = self.rect.centerx - player_rect.centerx
        distance_y = self.rect.centery - player_rect.centery
        distance = math.hypot(distance_x, distance_y)

        if distance < 300:
            speed = animal_run_speed if self.type != 'tucan' else tucan_speed
            self.is_running_away = True
        else:
            speed = self.speed
            self.is_running_away = False

        if self.is_running_away:
            angle = math.atan2(player_rect.centery - self.rect.centery, player_rect.centerx - self.rect.centerx)
            self.rect.x += -math.cos(angle) * speed * 0.01
            self.rect.y += -math.sin(angle) * speed * 0.01
        else:
            if self.type == 'tucan':
                self.angle = random.uniform(0, 2 * math.pi)
                self.rect.x += math.cos(self.angle) * speed * 0.01
                self.rect.y += math.sin(self.angle) * speed * 0.01
            else:
                self.angle += 0.1
                self.rect.x += math.cos(self.angle) * speed * 0.01
                self.rect.y += math.sin(self.angle) * speed * 0.01

        if self.rect.right > width - 20:
            self.rect.right = width - 20
        if self.rect.left < 20:
            self.rect.left = 20
        if self.rect.bottom > height:
            self.rect.bottom = height
        if self.rect.top < 20:
            self.rect.top = 20

class Monkey(Animal):
    def __init__(self, x, y):
        super().__init__(x, y, 'monkey')

class Elephant(Animal):
    def __init__(self, x, y):
        super().__init__(x, y, 'elephant')

class Tucan(Animal):
    def __init__(self, x, y):
        super().__init__(x, y, 'tucan')

def check_animal_collisions(animals):
    for i in range(len(animals)):
        for j in range(i + 1, len(animals)):
            if animals[i].rect.colliderect(animals[j].rect):
                overlap_rect = animals[i].rect.clip(animals[j].rect)
                if overlap_rect.width > overlap_rect.height:
                    if animals[i].rect.centery < animals[j].rect.centery:
                        animals[i].rect.bottom = animals[j].rect.top
                    else:
                        animals[i].rect.top = animals[j].rect.bottom
                else:
                    if animals[i].rect.centerx < animals[j].rect.centerx:
                        animals[i].rect.right = animals[j].rect.left
                    else:
                        animals[i].rect.left = animals[j].rect.right

class Jail:
    def __init__(self, x, y, animal_type):
        self.rect = pygame.Rect(x, y, 200, 150)
        self.animal_type = animal_type
        self.captured_animals = []
        self.image = pygame.image.load('jail.png')
        self.image = pygame.transform.scale(self.image, (200, 150))

    def draw(self):
        screen.blit(self.image, self.rect)
        draw_text(f'Animal: {self.animal_type}', font, (0, 0, 0), screen, self.rect.x + 10, self.rect.y + 10)

    def interact(self):
        return self.animal_type

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def load_scaled_image(image_path):
    image = pygame.image.load(image_path)
    return pygame.transform.scale(image, (width, height))

def switch_screen(new_screen, enter_from=None):
    global current_screen
    current_screen = new_screen
    current_screen.reset(enter_from)

class ZooScreen:
    def __init__(self):
        self.player = pygame.image.load('zookeeper.png')
        self.player = pygame.transform.scale(self.player, player_size)
        self.player_rect = pygame.Rect(width // 2, height // 2, player_size[0], player_size[1])
        self.jails = [
            Jail(width // 2 - 300, 100, 'monkey'),
            Jail(width // 2, 100, 'elephant'),
            Jail(width // 2 + 300, 100, 'tucan')
        ]
        self.jail_interaction_active = False
        self.active_jail = None

    def reset(self, enter_from=None):
        self.player_rect.x = width // 2
        self.player_rect.y = height // 2

    def draw(self):
        background_image = load_scaled_image('zoologico.png')
        screen.blit(background_image, (0, 0))
        screen.blit(self.player, self.player_rect)

        for jail in self.jails:
            jail.draw()

        draw_text(f'Monkeys Captured: {monkey_count}', font, (0, 0, 0), screen, 10, 10)
        draw_text(f'Elephants Captured: {elephant_count}', font, (0, 0, 0), screen, 10, 50)
        draw_text(f'Tucans Captured: {tucan_count}', font, (0, 0, 0), screen, 10, 90)

        if self.jail_interaction_active:
            self.show_jail_interaction_menu()

    def update(self, dt):
        keys = pygame.key.get_pressed()

        if not self.jail_interaction_active:  # Impede movimento quando no menu de interação
            if keys[K_LEFT]:
                self.player_rect.x -= player_speed * dt
            if keys[K_RIGHT]:
                self.player_rect.x += player_speed * dt
            if keys[K_UP]:
                self.player_rect.y -= player_speed * dt
            if keys[K_DOWN]:
                self.player_rect.y += player_speed * dt

        for jail in self.jails:
            if self.player_rect.colliderect(jail.rect) and keys[K_SPACE] and not self.jail_interaction_active:
                self.jail_interaction_active = True
                self.active_jail = jail
                print("jail_interaction_active = true")
                break

        if self.player_rect.left < 0:
            switch_screen(GrasslandScreen(), enter_from="left")

        if self.player_rect.right > width:
            self.player_rect.right = width

        if self.player_rect.top < 0:
            self.player_rect.top = 0

        if self.player_rect.bottom > height:
            self.player_rect.bottom = height

    def show_jail_interaction_menu(self):
        draw_text(f"Escolha um animal para a jaula de {self.active_jail.animal_type}:", font, (0, 0, 0), screen, width // 2 - 250, height // 2 - 150)

        # Filtra os animais no inventário que são do tipo correto
        animal_options = [animal for animal in inventory if animal.type == self.active_jail.animal_type]
        for i in inventory:
            print("oi")
            print(i)
        for i in animal_options:
            print("oi")
            print(i)

        if not animal_options:
            draw_text("Você não tem o animal correto!", font, (255, 0, 0), screen, width // 2 - 150, height // 2)
            pygame.display.update()
            pygame.time.delay(1000)
            self.jail_interaction_active = False
            return

        selected_option = 0

        while self.jail_interaction_active:
            screen.fill(white)
            draw_text(f"Escolha um animal para a jaula de {self.active_jail.animal_type}:", font, (0, 0, 0), screen, width // 2 - 250, height // 2 - 150)

            # Mostra as opções de animais do inventário
            for idx, option in enumerate(animal_options):
                color = (255, 0, 0) if idx == selected_option else (0, 0, 0)
                draw_text(option.type.capitalize(), font, color, screen, width // 2 - 100, height // 2 + idx * 60 - 50)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_DOWN:
                        selected_option = (selected_option + 1) % len(animal_options)
                    elif event.key == K_UP:
                        selected_option = (selected_option - 1) % len(animal_options)
                    elif event.key == K_SPACE:
                        selected_animal = animal_options[selected_option]
                        if selected_animal.type == self.active_jail.animal_type:
                            self.active_jail.captured_animals.append(selected_animal)
                            inventory.remove(selected_animal)
                            draw_text("Animal colocado na jaula!", font, (0, 255, 0), screen, width // 2 - 150, height // 2)
                        else:
                            draw_text("Animal incorreto!", font, (255, 0, 0), screen, width // 2 - 150, height // 2)
                        
                        pygame.display.update()
                        pygame.time.delay(1000)
                        self.jail_interaction_active = False
                        return
        
class GrasslandScreen:
    def __init__(self):
        self.animals = []
        self.player = pygame.image.load('zookeeper.png')
        self.player = pygame.transform.scale(self.player, player_size)
        self.player_rect = pygame.Rect(width // 2, height // 2, player_size[0], player_size[1])

    def reset(self, enter_from=None):
        if enter_from == "left":
            self.player_rect.x = width - 60
            self.player_rect.y = height // 2
        else:
            self.player_rect.x = width // 2
            self.player_rect.y = height // 2

        self.animals = [
            Monkey(random.randint(100, width - 100), random.randint(100, height - 100)),
            Elephant(random.randint(100, width - 100), random.randint(100, height - 100)),
            Tucan(random.randint(100, width - 100), random.randint(100, height - 100))
        ]

    def draw(self):
        background_image = load_scaled_image('grassland.png')
        screen.blit(background_image, (0, 0))
        screen.blit(self.player, self.player_rect)

        for animal in self.animals:
            screen.blit(animal.image, animal.rect)

        draw_text(f'Monkeys Captured: {monkey_count}', font, (0, 0, 0), screen, 10, 10)
        draw_text(f'Elephants Captured: {elephant_count}', font, (0, 0, 0), screen, 10, 50)
        draw_text(f'Tucans Captured: {tucan_count}', font, (0, 0, 0), screen, 10, 90)

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            self.player_rect.x -= player_speed * dt
        if keys[K_RIGHT]:
            self.player_rect.x += player_speed * dt
        if keys[K_UP]:
            self.player_rect.y -= player_speed * dt
        if keys[K_DOWN]:
            self.player_rect.y += player_speed * dt
        if keys[K_ESCAPE]:
            paused = True
            pause_menu()

        if self.player_rect.right > width:
            switch_screen(ZooScreen(), enter_from="right")

        for animal in self.animals:
            animal.update(self.player_rect)

        check_animal_collisions(self.animals)

        for animal in self.animals[:]:
            if self.player_rect.colliderect(animal.rect):
                if animal.type == "monkey":
                    global monkey_count
                    monkey_count += 1
                elif animal.type == "elephant":
                    global elephant_count
                    elephant_count += 1
                elif animal.type == "tucan":
                    global tucan_count
                    tucan_count += 1
                self.animals.remove(animal)

        if self.player_rect.left < 0:
            self.player_rect.left = 0
        if self.player_rect.top < 0:
            self.player_rect.top = 0
        if self.player_rect.bottom > height:
            self.player_rect.bottom = height
            
def draw_menu_option(option, is_selected, x, y):
    color = (255, 0, 0) if is_selected else (0, 0, 0)
    draw_text(option, font, color, screen, x, y)

def main_menu():
    global in_menu
    selected_option = 0
    while in_menu:
        screen.fill(white)
        draw_text('Welcome to the Zoo!', font, (0, 0, 0), screen, width // 2 - 150, height // 2 - 200)

        for idx, option in enumerate(menu_options):
            draw_menu_option(option, idx == selected_option, width // 2 - 100, height // 2 + idx * 60 - 100)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_DOWN:
                    selected_option = (selected_option + 1) % len(menu_options)
                elif event.key == K_UP:
                    selected_option = (selected_option - 1) % len(menu_options)
                elif event.key == K_SPACE:
                    if menu_options[selected_option] == "Start Game":
                        in_menu = False
                        start_game()
                    elif menu_options[selected_option] == "Quit":
                        pygame.quit()
                        sys.exit()

def pause_menu():
    global paused
    selected_option = 0
    while paused:
        screen.fill(white)
        draw_text('Paused', font, (0, 0, 0), screen, width // 2 - 100, height // 2 - 200)

        for idx, option in enumerate(pause_options):
            draw_menu_option(option, idx == selected_option, width // 2 - 100, height // 2 + idx * 60 - 100)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_DOWN:
                    selected_option = (selected_option + 1) % len(pause_options)
                elif event.key == K_UP:
                    selected_option = (selected_option - 1) % len(pause_options)
                elif event.key == K_SPACE:
                    if pause_options[selected_option] == "Continue":
                        paused = False
                    elif pause_options[selected_option] == "Quit":
                        pygame.quit()
                        sys.exit()

def start_game():
    global current_screen, paused
    paused = False  # Adicionando a inicialização da variável 'paused'
    current_screen = ZooScreen()
    current_screen.reset()

    clock = pygame.time.Clock()

    while True:
        dt = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                paused = True
                pause_menu()

        if not paused:
            current_screen.draw()
            current_screen.update(dt)

        pygame.display.flip()

if __name__ == "__main__":
    main_menu()
