import os
import random
import pygame
import sys
import math

FPS = 50
WIDTH, HEIGHT = 1920, 1080
GRAVITY = 0.25

pygame.init()

size = width, height = WIDTH, HEIGHT
screen = pygame.display.set_mode(size)
screen_rect = (0, 0, width, height)
tile_width = tile_height = 100

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()
button_group = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
enemy_bullet_group = pygame.sprite.Group()
player_bullet_group = pygame.sprite.Group()
bar_group = pygame.sprite.Group()


def load_image(name, per_pixel_alpha=False, color_key=None):
    fullname = os.path.join('textures', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if per_pixel_alpha:
        image = image.convert_alpha()
    else:
        image = image.convert()

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)

    return image


def load_level(filename):
    filename = "levels/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                wall_group.add(Tile('wall', x, y))
            elif level[y][x] == '+':
                Tile('empty', x, y)
                button_group.add(Button(x, y))
            elif level[y][x] == '@':
                Tile('empty', x, y)
                p_x, p_y = x, y
            elif level[y][x] == 'B':
                Tile('empty', x, y)
                b_x, b_y = x, y
    Boss(b_x, b_y)
    new_player = Player(p_x, p_y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def create_particle(x, y, count=30):
    numbers = range(-5, 6)
    for _ in range(count):
        Particle((x, y), random.choice(numbers), random.choice(numbers))


def terminate():
    pygame.quit()
    sys.exit()


def rect_distance(rect1, rect2):
    x1, y1 = rect1.topleft
    x1b, y1b = rect1.bottomright
    x2, y2 = rect2.topleft
    x2b, y2b = rect2.bottomright
    left = x2b < x1
    right = x1b < x2
    top = y2b < y1
    bottom = y1b < y2
    if bottom and left:
        print('bottom left')
        return math.hypot(x2b - x1, y2 - y1b)
    elif left and top:
        print('top left')
        return math.hypot(x2b - x1, y2b - y1)
    elif top and right:
        print('top right')
        return math.hypot(x2 - x1b, y2b - y1)
    elif right and bottom:
        print('bottom right')
        return math.hypot(x2 - x1b, y2 - y1b)
    elif left:
        print('left')
        return x1 - x2b
    elif right:
        print('right')
        return x2 - x1b
    elif top:
        print('top')
        return y1 - y2b
    elif bottom:
        print('bottom')
        return y2 - y1b
    else:  # rectangles intersect
        print('intersection')
        return 0.


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "НАжмите любую кнопку,",
                  "чтобы"]

    fon = pygame.Surface((screen.get_width(), screen.get_height()))
    fon.fill(pygame.Color('black'))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 50
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def lose_screen():
    intro_text = ["ВЫ ЛОХ", "",
                  "Вы проиграли",
                  "НАжмите любую кнопку,",
                  "текст"]

    fon = pygame.transform.scale(load_image('milos_fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 50
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                terminate()
        pygame.display.flip()
        clock.tick(FPS)


def win_screen():
    intro_text = ["ВЫ крутой", "",
                  "Вы выиграли",
                  "НАжмите любую кнопку,",
                  "текст"]

    fon = pygame.transform.scale(load_image('milos_fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 50
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                terminate()
        pygame.display.flip()
        clock.tick(FPS)


tile_images = {
    'wall': load_image('wall.png'),
    # 'empty': pygame.Surface((100, 100))
    'empty': load_image('grass.png')
}


# ------------------------------------------------------------------
# КЛАССЫ
# ------------------------------------------------------------------

class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        size = random.choice((5, 10, 15, 20))
        self.image = pygame.Surface((size, size))
        self.image.fill(pygame.Color('red'))
        self.image.set_alpha(random.randint(180, 201))
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость — это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos

        # гравитация будет одинаковой (значение константы)
        self.gravity = GRAVITY

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(screen_rect):
            self.kill()


class BulletParticle(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(all_sprites)
        size = random.choice((5, 10, 15, 20))
        self.image = pygame.Surface((size, size))
        self.image.fill(pygame.Color('red'))
        self.image.set_alpha(random.randint(40, 81))
        self.rect = self.image.get_rect()

        self.lifetime = random.randint(30, 61)

        self.rect.x, self.rect.y = pos

    def update(self):
        self.lifetime -= 1
        if not self.lifetime:
            self.kill()
        if not self.rect.colliderect(screen_rect):
            self.kill()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Button(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites)
        self.press_allowed = True
        self.image = load_image('btn.png', True)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 12.5, tile_height * pos_y + 12.5)

    def update(self, *args):
        if pygame.sprite.spritecollideany(self, player_group):
            if self.press_allowed:
                print('Button pressed')
                create_particle(self.rect.x + 37, self.rect.y + 37)
                self.press_allowed = False
        else:
            self.press_allowed = True


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = pygame.transform.scale(load_image('milos2.png', True), (75, 75))
        self.HP = 100
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 12.5, tile_height * pos_y + 12.5)
        self.reload, self.reload_time = 0, 5
        self.can_shoot = True
        self.speed = 8

        self.bar = Bar(self, 100, 100, '#00FF00')

    def refresh_bar(self):
        return self.HP

    def update(self, *args):
        self.reload += 1
        if self.reload >= self.reload_time:
            self.can_shoot = True
            self.reload = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.rect = self.rect.move(0, -self.speed)
            if pygame.sprite.spritecollideany(self, wall_group):
                self.rect = self.rect.move(0, self.speed)
        if keys[pygame.K_d]:
            self.rect = self.rect.move(self.speed, 0)
            if pygame.sprite.spritecollideany(self, wall_group):
                self.rect = self.rect.move(-self.speed, 0)
        if keys[pygame.K_s]:
            self.rect = self.rect.move(0, self.speed)
            if pygame.sprite.spritecollideany(self, wall_group):
                self.rect = self.rect.move(0, -self.speed)
        if keys[pygame.K_a]:
            self.rect = self.rect.move(-self.speed, 0)
            if pygame.sprite.spritecollideany(self, wall_group):
                self.rect = self.rect.move(self.speed, 0)

        if args and args[0].type == pygame.MOUSEBUTTONDOWN and self.can_shoot:
            bullet_direction_vector = [args[0].pos[0] - (self.rect.x + 37.5),
                                       args[0].pos[1] - (self.rect.y + 37.5)]
            vx = bullet_direction_vector[0] \
                 / math.sqrt(bullet_direction_vector[0] ** 2 + bullet_direction_vector[1] ** 2)
            vy = bullet_direction_vector[1] \
                 / math.sqrt(bullet_direction_vector[0] ** 2 + bullet_direction_vector[1] ** 2)
            PlayerBullet(self.rect.x, self.rect.y, vx * 10, vy * 10)
            self.can_shoot = False

        if pygame.sprite.spritecollideany(self, enemy_bullet_group):
            pygame.sprite.spritecollide(self, enemy_bullet_group, True)
            self.HP -= 10
            if self.HP <= 0:
                lose_screen()


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, vx, vy):
        super().__init__(all_sprites, enemy_bullet_group)
        self.press_allowed = True
        self.image = pygame.transform.scale(load_image('potat.png', True), (75, 75))
        self.rect = self.image.get_rect()
        self.velocity = [vx, vy]
        self.rect.x, self.rect.y = pos_x, pos_y
        self.gravity = 0

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(screen_rect):
            self.kill()
        if pygame.sprite.spritecollideany(self, player_bullet_group):
            pygame.sprite.spritecollide(self, player_bullet_group, True)
            create_particle(self.rect.x + 37.5, self.rect.y + 25)
            self.kill()
        if pygame.sprite.spritecollideany(self, wall_group):
            create_particle(self.rect.x + 37.5, self.rect.y + 37.5, 3)
            self.kill()


class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, vx, vy):
        super().__init__(all_sprites, player_bullet_group)
        self.press_allowed = True
        self.image = pygame.transform.scale(load_image('bread.png', True), (75, 75))
        self.rect = self.image.get_rect()
        self.velocity = [vx, vy]
        self.rect.x, self.rect.y = pos_x, pos_y

    def update(self):
        for _ in range(random.randint(3, 6)):
            BulletParticle((
                self.rect.x + 37.5 + random.randint(-10, 10), self.rect.y + 37.5 + random.randint(-10, 10)))
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect(screen_rect):
            self.kill()
        if pygame.sprite.spritecollideany(self, wall_group):
            create_particle(self.rect.x + 37.5, self.rect.y + 37.5, 3)
            self.kill()


class Boss(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(boss_group, all_sprites)
        self.image = load_image('cheems.png', True)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * (pos_y - 2))
        self.HP = 15

        self.bar = Bar(self, 15, 15, 'red')

    def refresh_bar(self):
        return self.HP

    def update(self, *args):
        if random.randint(0, 100) > self.HP * 3 + 45:
            EnemyBullet(self.rect.x + 50, self.rect.y + 50, *random.choices((-5, -3, -2, -1, 1, 2, 3, 5), k=2))
        if pygame.sprite.spritecollideany(self, player_bullet_group):
            pygame.sprite.spritecollide(self, player_bullet_group, True)
            self.HP -= 1
            print(f'Boss HP: {self.HP}')
            if not self.HP:
                create_particle(self.rect.x + 25, self.rect.y + 12.5)
                create_particle(self.rect.x + 50, self.rect.y + 25)
                create_particle(self.rect.x + 25, self.rect.y + 37.5)
                create_particle(self.rect.x + 50, self.rect.y + 50)
                create_particle(self.rect.x + 37.5, self.rect.y + 62.5)
                self.kill()
                self.bar.kill()


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


class Bar(pygame.sprite.Sprite):
    def __init__(self, parent, value, max_value=100, color='green', size_x=200, size_y=30):
        super().__init__(all_sprites, bar_group)

        self.color = color
        self.size_x, self.size_y = size_x, size_y
        self.pixels_per_value = self.size_x / max_value
        self.value, self.max_value = value, max_value
        self.parent = parent

        self.image = pygame.Surface((self.size_x, self.size_y))
        self.image.fill('black')
        self.image.fill('#333333', (5, 5, self.size_x - 10, self.size_y - 10))
        self.image.fill(color, (5, 5, self.pixels_per_value * value - 10, self.size_y - 10))

        self.rect = self.image.get_rect().move(
            parent.rect.x - (self.size_x - parent.rect.w) / 2, parent.rect.y - self.size_y - 15)

    def update(self):
        self.rect.x, self.rect.y = \
            self.parent.rect.x - (self.size_x - self.parent.rect.w) / 2, self.parent.rect.y - self.rect.h - 15

        self.value = self.parent.refresh_bar()

        self.image.fill('#333333', (5, 5, self.size_x - 10, self.size_y - 10))
        self.image.fill(self.color, (5, 5, self.pixels_per_value * self.value - 10, self.size_y - 10))


# ------------------------------------------------------------------
# ЦИКЛ
# ------------------------------------------------------------------


player = None

clock = pygame.time.Clock()

start_screen()
player, level_x, level_y = generate_level(load_level('map.txt'))
camera = Camera()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            player.update(event)
    screen.fill(pygame.Color("#AAAAAA"))
    all_sprites.draw(screen)

    # изменяем ракурс камеры
    camera.update(player)
    # обновляем положение всех спрайтов
    for sprite in all_sprites:
        camera.apply(sprite)

    all_sprites.update()
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
