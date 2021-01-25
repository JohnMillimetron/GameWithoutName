import os
import random
import pygame
import sys
import math
import sqlite3

FPS = 60
WIDTH, HEIGHT = 1920, 1080
GRAVITY = 0.25
tile_width = tile_height = 100
size = width, height = WIDTH, HEIGHT
screen = pygame.display.set_mode(size)
screen_rect = (0, 0, width, height)

pygame.init()

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()
button_group = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
enemy_bullet_group = pygame.sprite.Group()
player_bullet_group = pygame.sprite.Group()
bar_group = pygame.sprite.Group()
gui_group = pygame.sprite.Group()
items_in_inventory = pygame.sprite.Group()

can_open_inventory = True


def load_image(name, per_pixel_alpha=False, color_key=None):
    fullname = os.path.join('data', 'textures', name)
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
    filename = "data/levels/" + filename
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
            elif level[y][x] == 'c':
                Tile('empty', x, y)
                Chest(x, y, 'closed')
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


def inventory():
    player.can_open_inventory = False
    inventory_image = load_image('inventory.png', True)
    screen.blit(inventory_image, (0, 0))

    equipment_cells = {
        (0, 0): None, (1, 0): 'head', (2, 0): 'amulet',
        (0, 1): 'weapon2', (1, 1): 'body', (2, 1): 'weapon1',
        (0, 2): None, (1, 2): 'legs', (2, 2): None,
        (0, 3): None, (1, 3): 'feet', (2, 3): None}
    cells_equipment = {val: key for key, val in equipment_cells.items()}

    inventory_board = [[pygame.Rect(x * 110 + 755, y * 110 + 270, 100, 100) for x in range(4)] for y in range(4)]
    equipment_board = [[pygame.Rect(x * 100 + 445, y * 100 + 270, 90, 90) for x in range(3)] for y in range(4)]

    if player.inventory:
        for i, item in enumerate(player.inventory):
            y, x = i // 4, i % 4
            a = item.generate_sprite(inventory_board[y][x].x, inventory_board[y][x].y)
            a.image = pygame.transform.scale(a.image, (90, 90))
            a.rect = a.rect.move(5, 5)
    for elem, item in player.inventory.equipment.items():
        if item is not None:
            x, y = cells_equipment.get(elem)
            a = item.generate_sprite(equipment_board[y][x].x, equipment_board[y][x].y)
            a.image = pygame.transform.scale(a.image, (80, 80))
            a.rect = a.rect.move(5, 5)

    cell_clicked = (0, 0, 0)

    while True:
        if cell_clicked[2] == 0:
            screen.fill('#555555', inventory_board[cell_clicked[1]][cell_clicked[0]])
        else:
            screen.fill('#555555', equipment_board[cell_clicked[1]][cell_clicked[0]])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for y in range(4):
                    for x in range(4):
                        if inventory_board[y][x].collidepoint(event.pos):
                            cell_clicked = (x, y, 0)  # 0 - предмет в инвентаре
                            break
                        if x < 3:
                            if equipment_board[y][x].collidepoint(event.pos):
                                cell_clicked = (x, y, 1)  # 1 - предмет в снаряжении
                                break
        item = None
        if cell_clicked:
            if cell_clicked[2] == 0:
                screen.fill('red', inventory_board[cell_clicked[1]][cell_clicked[0]])
                screen.fill('#555555', (inventory_board[cell_clicked[1]][cell_clicked[0]].x + 5,
                                        inventory_board[cell_clicked[1]][cell_clicked[0]].y + 5, 90, 90))
                if len(player.inventory) >= cell_clicked[1] * 4 + cell_clicked[0] + 1:
                    item = player.inventory[cell_clicked[1] * 4 + cell_clicked[0]]
            elif cell_clicked[2] == 1:
                screen.fill('red', equipment_board[cell_clicked[1]][cell_clicked[0]])
                screen.fill('#555555', (equipment_board[cell_clicked[1]][cell_clicked[0]].x + 5,
                                        equipment_board[cell_clicked[1]][cell_clicked[0]].y + 5, 80, 80))
                if equipment_cells.get(cell_clicked[:2]) is not None:
                    if player.inventory.equipment[equipment_cells.get(cell_clicked[:2])] is not None:
                        item = player.inventory.equipment[equipment_cells.get(cell_clicked[:2])]

        screen.fill('#555555', (1205, 260, 280, 560))

        if item is not None:
            font = pygame.font.SysFont('TimesNewRoman', 22)
            text = font.render(item.name, True, pygame.color.Color('white'))
            screen.blit(text, (1210, 260))

            font = pygame.font.SysFont('TimesNewRoman', 18)
            if type(item) == RangedWeapon:
                lines = [f'Урон: {item.damage}',
                         f'Перезарядка: {item.reload_time}',
                         f'Прочность: {item.max_durability}/{item.durability}',
                         f'Стоимость: {item.cost}',
                         f'', f'Снаряд', f'',
                         f'Тип: Ы',
                         f'Кол-во: Ы',
                         f'Взрывоопасный: Ы']
            elif type(item) == Item:
                lines = [f'Стоимость: {item.cost}']
            elif type(item) == Armor:
                lines = [f'Элемент: {item.element}',
                         f'Защита: {item.armor_points}',
                         f'Прочность: {item.max_durability}/{item.durability}',
                         f'Стоимость: {item.cost}',
                         f'', f'Особенности', f'',
                         f'Зачарование: Ы']

            for i, line in enumerate(lines):
                text = font.render(line, True, pygame.color.Color('white'))
                screen.blit(text, (1210, 280 + 15 * i))

            font = pygame.font.SysFont('TimesNewRoman', 16)
            for i, line in enumerate(item.description.split('|')):
                text = font.render(line, True, pygame.color.Color('white'))
                screen.blit(text, (1210, 280 + 15 * len(lines) + 30 + 14 * i))
        else:
            font = pygame.font.SysFont('TimesNewRoman', 22)
            text = font.render('Пусто', True, pygame.color.Color('white'))
            screen.blit(text, (1210, 260))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_e]:
            return

        items_in_inventory.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


tile_images = {
    'wall': load_image('wall.png'),
    # 'empty': pygame.Surface((100, 100))
    'empty': load_image(f'grass{random.randint(1, 2)}.png')
}


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

    def update(self, *args, **kwargs):
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
        size = random.choice((1, 3, 5, 7))
        self.image = pygame.Surface((size, size))
        self.image.fill(pygame.Color('red'))
        self.image.set_alpha(random.randint(40, 81))
        self.rect = self.image.get_rect()

        self.lifetime = random.randint(30, 61)

        self.rect.x, self.rect.y = pos

    def update(self, *args, **kwargs):
        self.lifetime -= 1
        if not self.lifetime:
            self.kill()
        if not self.rect.colliderect(screen_rect):
            self.kill()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        if tile_type == 'empty':
            self.image = load_image(f'grass{random.randint(1, 7)}.png')
        elif tile_type == 'wall':
            self.image = load_image(f'wall.png')
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Button(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites)
        self.press_allowed = True
        self.image = load_image('btn.png', True)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 12.5, tile_height * pos_y + 12.5)

    def update(self, *args, **kwargs):
        if pygame.sprite.spritecollideany(self, player_group):
            if self.press_allowed:
                create_particle(self.rect.x + 37, self.rect.y + 37)
                self.press_allowed = False
        else:
            self.press_allowed = True


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.images = {
            'north': 'player\\player1_north.png',
            'east': 'player\\player1_east.png',
            'west': 'player\\player1_west.png',
            'south': 'player\\player1_south.png',
        }
        self.image = pygame.transform.scale(load_image(self.images.get('south'), True), (96, 96))
        self.HP, self.max_HP = 100, 100
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 12.5, tile_height * pos_y + 12.5)
        self.reload, self.reload_time = 0, 15
        self.can_shoot, self.can_open_inventory = True, True
        self.speed = 8
        self.moving, self.moving_direction, self.facing = False, [0, 0], 'south'
        self.inventory = Inventory()
        self.interact_range = 150

        self.interact_rect = pygame.Rect(self.rect.x + self.rect.width / 2 - self.interact_range,
                                         self.rect.y + self.rect.height / 2 - self.interact_range,
                                         self.interact_range * 2, self.interact_range * 2)

        self.bars = []

    def refresh_bar(self, value_type):
        if value_type == 'HP':
            return self.HP
        elif value_type == 'reload':
            return self.reload if not self.can_shoot else self.reload_time

    def update(self, *args, **kwargs):
        self.reload += 1 if not self.can_shoot else 0
        if self.reload >= self.reload_time:
            self.can_shoot = True
            self.reload = 0

        keys = kwargs['keys'] if 'keys' in kwargs.keys() else pygame.key.get_pressed()

        if keys[pygame.K_e]:
            if self.can_open_inventory:
                inventory()
        else:
            self.can_open_inventory = True

        self.moving, self.moving_direction = False, [0, 0]
        if keys[pygame.K_w]:
            self.rect = self.rect.move(0, -self.speed)
            self.moving = True
            self.moving_direction[1] = 1
            self.facing = 'north'
            # self.interact_rect = self.interact_rect.move(0, -self.speed)
            if pygame.sprite.spritecollideany(self, wall_group):
                self.moving = False
                self.moving_direction[1] = 0
                self.rect = self.rect.move(0, self.speed)
                # self.interact_rect = self.interact_rect.move(0, self.speed)

        if keys[pygame.K_d]:
            self.rect = self.rect.move(self.speed, 0)
            self.moving = True
            self.moving_direction[0] = 1
            self.facing = 'east'
            # self.interact_rect = self.interact_rect.move(self.speed, 0)
            if pygame.sprite.spritecollideany(self, wall_group):
                self.moving = False
                self.moving_direction[0] = 0
                self.rect = self.rect.move(-self.speed, 0)
                # self.interact_rect = self.interact_rect.move(-self.speed, 0)

        if keys[pygame.K_s]:
            self.rect = self.rect.move(0, self.speed)
            self.moving = True
            self.moving_direction[1] = -1
            self.facing = 'south'
            # self.interact_rect = self.interact_rect.move(0, self.speed)
            if pygame.sprite.spritecollideany(self, wall_group):
                self.rect = self.rect.move(0, -self.speed)
                self.moving = False
                self.moving_direction[1] = 0
                # self.interact_rect = self.interact_rect.move(0, -self.speed)

        if keys[pygame.K_a]:
            self.rect = self.rect.move(-self.speed, 0)
            self.moving = True
            self.moving_direction[0] = -1
            self.facing = 'west'
            # self.interact_rect = self.interact_rect.move(-self.speed, 0)
            if pygame.sprite.spritecollideany(self, wall_group):
                self.moving = False
                self.moving_direction[0] = 0
                self.rect = self.rect.move(self.speed, 0)
                # self.interact_rect = self.interact_rect.move(self.speed, 0)

        self.interact_rect = pygame.Rect(self.rect.x + self.rect.width / 2 - self.interact_range,
                                         self.rect.y + self.rect.height / 2 - self.interact_range,
                                         self.interact_range * 2, self.interact_range * 2)
        if 'event' in kwargs.keys():
            if kwargs['event'].type == pygame.MOUSEBUTTONDOWN and self.can_shoot:
                bullet_direction_vector = [kwargs['event'].pos[0] - (self.rect.x + 37.5),
                                           kwargs['event'].pos[1] - (self.rect.y + 37.5)]
                vx = bullet_direction_vector[0] \
                     / math.sqrt(bullet_direction_vector[0] ** 2 + bullet_direction_vector[1] ** 2)
                vy = bullet_direction_vector[1] \
                     / math.sqrt(bullet_direction_vector[0] ** 2 + bullet_direction_vector[1] ** 2)

                # dx, dy = self.moving_direction
                # if ((dy != 0 and dx == 0) and ((dy <= 0 and vy >= 0) or (dy > 0 and vy < 0))) or \
                #         ((dx != 0 and dy == 0) and ((dx >= 0 and vx >= 0) or (dx < 0 and vx < 0))):
                # ((dx > 0 and dy > 0) and
                #  (math.sin(135) >= vy >= math.sin(315) and math.cos(135) >= vy >= math.cos(315))) or \
                # ((dx < 0 and dy < 0) and
                #  (math.sin(135) >= vy >= math.sin(315) and math.cos(135) >= vy >= math.cos(315))):

                PlayerBullet(self.rect.x + self.rect.width, self.rect.y + self.rect.height / 2,
                             vx * 10, vy * 10, vy, vx)
                self.can_shoot = False
                self.facing = 'north' if vy < 0 and abs(vy) > abs(vx) else 'south' if vy > 0 and abs(vy) > abs(vx) \
                    else 'east' if vx > 0 and abs(vx) > abs(vy) else 'west'

        if pygame.sprite.spritecollideany(self, enemy_bullet_group):
            pygame.sprite.spritecollide(self, enemy_bullet_group, True)
            self.HP -= 10
            if self.HP <= 0:
                lose_screen()

        self.image = pygame.transform.scale(load_image(self.images.get(self.facing), True), (96, 96))


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, vx, vy):
        super().__init__(all_sprites, enemy_bullet_group)
        self.press_allowed = True
        self.image = pygame.transform.scale(load_image('potat.png', True), (75, 75))
        self.rect = self.image.get_rect()
        self.velocity = [vx, vy]
        self.rect.x, self.rect.y = pos_x, pos_y

    def update(self, *args, **kwargs):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
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
    def __init__(self, pos_x, pos_y, vx, vy, sin, cos):
        super().__init__(all_sprites, player_bullet_group)
        self.press_allowed = True
        self.image = pygame.transform.scale(load_image('items\\bullets\\arrow1.png', True), (39, 11))
        angle = math.acos(cos) * 180 / math.pi if sin > 0 else 360 - math.acos(cos) * 180 / math.pi
        self.image = pygame.transform.rotate(self.image, -angle)
        self.rect = self.image.get_rect()
        self.velocity = [vx, vy]
        self.rect.x, self.rect.y = pos_x, pos_y

    def update(self, *args, **kwargs):
        for _ in range(random.randint(1, 3)):
            BulletParticle((
                self.rect.x + self.rect.width / 2 + random.randint(-5, 5),
                self.rect.y + self.rect.height / 2 + random.randint(-5, 5)))
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
        self.bars = []
        self.bars.append(Bar(self, 15, 15, 'red'))

    def refresh_bar(self, value_type):
        if value_type == 'HP':
            return self.HP

    def update(self, *args, **kwargs):
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
                for bar in self.bars:
                    bar.kill()


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
    def __init__(
            self, parent, value, max_value=100, color='green', size_x=200, size_y=30, value_type='HP', coords=None):
        super().__init__()

        if coords is not None:
            self.movable = False
            self.add(gui_group)
        else:
            self.add(all_sprites, bar_group)
            self.movable = True

        self.color = color
        self.size_x, self.size_y = size_x, size_y
        self.pixels_per_value = self.size_x / max_value
        self.value, self.max_value = value, max_value
        self.parent = parent
        self.value_type = value_type

        self.image = pygame.Surface((self.size_x, self.size_y))
        self.image.fill('black')
        self.rect = self.image.get_rect()

        if not self.movable:
            self.rect = self.rect.move(coords)

    def update(self, *args, **kwargs):
        if self.movable:
            self.rect.x, self.rect.y = \
                self.parent.rect.x - (self.size_x - self.parent.rect.w) / 2, \
                self.parent.rect.y - self.rect.h - 10 - \
                (sum([i.size_y for i in self.parent.bars[:self.parent.bars.index(self)]]) if self.parent.bars else 0)

        self.value = self.parent.refresh_bar(self.value_type)

        self.image.fill('#333333', (5, 5, self.size_x - 10, self.size_y - 10))
        self.image.fill(self.color, (5, 5, self.pixels_per_value * self.value - 10, self.size_y - 10))


class Chest(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, chest_state='closed', chest_contains=None):
        super().__init__(wall_group, all_sprites)
        if chest_state == 'closed':
            self.image = load_image(f'chest1_closed.png', True)
        elif chest_state == 'opened':
            self.image = load_image(f'chest1_opened.png', True)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 10, tile_height * pos_y + 10)
        self.locked, self.key_id, self.opened = False, None, False
        # self.interact_range = 150
        # self.interact_rect = pygame.Rect(self.rect.x + self.rect.width / 2 - self.interact_range,
        #                                  self.rect.y + self.rect.height / 2 - self.interact_range,
        #                                  self.interact_range * 2, self.interact_range * 2)

    def update(self, *args, **kwargs):
        # self.interact_rect = pygame.Rect(self.rect.x + self.rect.width / 2 - self.interact_range,
        #                                  self.rect.y + self.rect.height / 2 - self.interact_range,
        #                                  self.interact_range * 2, self.interact_range * 2)
        keys = kwargs['keys']
        if self.rect.colliderect(player.interact_rect) and keys[pygame.K_f]:
            # create_particle(self.rect.x + 40, self.rect.y + 40, 1)
            self.interact()

    def open(self):
        self.image = load_image(f'chest1_opened.png', True)
        player.inventory.add(RangedWeapon(1))
        self.opened = True
        create_particle(self.rect.x + 40, self.rect.y + 40, 15)

    def interact(self):
        if not self.locked and not self.opened:
            self.open()


class Gui(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(gui_group)
        self.image = load_image(f'GUI.png', True)
        self.rect = self.image.get_rect()
        self.bars = []
        self.bars.append(Bar(player, player.HP, player.max_HP, coords=(20, 20), size_x=300, size_y=40))
        self.bars.append(Bar(player, player.reload, player.reload_time,
                             coords=(20, 75), size_x=300, size_y=40, value_type='reload', color='blue'))

    def update(self, *args, **kwargs):
        pass


class Inventory:
    def __init__(self):
        self.items = []
        self.equipment = {"head": None,
                          "body": None,
                          "legs": None,
                          "feet": None,
                          "weapon1": None,
                          "weapon2": None,
                          "amulet": None}

    def add(self, item):
        self.items.append(item)

    def add_equipment(self, item):
        self.equipment[item.element] = item

    def __getitem__(self, item):
        return self.items[item]

    def __bool__(self):
        return bool(self.items)

    def __len__(self):
        return len(self.items)


class RangedWeapon:
    def __init__(self, *arg):
        con = sqlite3.connect(os.path.join('data', 'items', 'items.sqlite'))
        cur = con.cursor()
        if type(arg[0]) == int:
            data = cur.execute(f"""SELECT name, description, damage, reload, durability, rareness, image_path, cost
                                   FROM ranged_weapons
                                   WHERE id = {arg[0]}""").fetchall()
        elif type(arg[0]) == str:
            data = cur.execute(f"""SELECT name, description, damage, reload, durability, rareness, image_path, cost
                                   FROM ranged_weapons
                                   WHERE name = '{arg[0]}'""").fetchall()
        self.name, self.description, self.damage, self.reload_time, \
        self.durability, self.rareness, self.img_path, self.cost = data[0]
        print(self.img_path)
        self.max_durability = self.durability
        self.element = 'weapon1'

    def generate_sprite(self, x, y):
        return RangedWeaponSprite(self.name, self.description, self.damage, self.reload_time,
                                  self.durability, self.rareness, self.img_path, self.cost, x, y)

    def shoot(self, vx, vy):
        pass


class RangedWeaponSprite(pygame.sprite.Sprite):
    def __init__(self, name, description, damage, reload, durability, rareness, image_path, cost, x, y):
        super().__init__(items_in_inventory)
        self.name, self.description, self.damage, self.reload_time, \
        self.durability, self.rareness, self.img_path = \
            name, description, damage, reload, durability, rareness, image_path
        self.max_durability = self.durability
        print(self.img_path)
        self.image = pygame.transform.scale(load_image(self.img_path, True), (100, 100))
        self.rect = self.image.get_rect().move(x, y)

    def update(self, *args, **kwargs):
        pass


class Item:
    def __init__(self, *arg):
        con = sqlite3.connect(os.path.join('data', 'items', 'items.sqlite'))
        cur = con.cursor()
        if type(arg[0]) == int:
            data = cur.execute(f"""SELECT name, description, image_path, cost
                                   FROM items
                                   WHERE id = {arg[0]}""").fetchall()
        elif type(arg[0]) == str:
            data = cur.execute(f"""SELECT name, description, image_path, cost
                                   FROM items
                                   WHERE name = '{arg[0]}'""").fetchall()
        self.name, self.description, self.img_path, self.cost = data[0]

    def generate_sprite(self, x, y):
        return ItemSprite(self.name, self.description, self.img_path, self.cost, x, y)


class ItemSprite(pygame.sprite.Sprite):
    def __init__(self, name, description, image_path, cost, x, y):
        super().__init__(items_in_inventory)
        self.name, self.description, self.img_path = name, description, image_path
        self.image = pygame.transform.scale(load_image(self.img_path, True), (100, 100))
        self.rect = self.image.get_rect().move(x, y)

    def update(self, *args, **kwargs):
        pass


class Armor:
    def __init__(self, *arg):
        con = sqlite3.connect(os.path.join('data', 'items', 'items.sqlite'))
        cur = con.cursor()
        if type(arg[0]) == int:
            data = cur.execute(f"""SELECT name, description, element, armor_points,
                                   image_path, features, cost, durability
                                   FROM armor
                                   WHERE id = {arg[0]}""").fetchall()
        elif type(arg[0]) == str:
            data = cur.execute(f"""SELECT name, description, element, armor_points,
                                   image_path, features, cost, durability
                                   FROM armor
                                   WHERE name = '{arg[0]}'""").fetchall()
        self.name, self.description, self.element, self.armor_points, \
        self.img_path, self.features, self.cost, self.durability = data[0]
        self.max_durability = self.durability

    def generate_sprite(self, x, y):
        return ArmorSprite(self.name, self.description, self.element, self.armor_points,
                           self.img_path, self.features, self.cost, self.durability, x, y)


class ArmorSprite(pygame.sprite.Sprite):
    def __init__(self, name, description, element, armor_points, image_path, features, cost, durability, x, y):
        super().__init__(items_in_inventory)
        self.name, self.description, self.element, self.armor_points, \
        self.img_path, self.features, self.cost, self.durability = \
            name, description, element, armor_points, image_path, features, cost, durability
        self.max_durability = self.durability
        self.image = pygame.transform.scale(load_image(self.img_path, True), (100, 100))
        self.rect = self.image.get_rect().move(x, y)

    def update(self, *args, **kwargs):
        pass


player = None
clock = pygame.time.Clock()

player, level_x, level_y = generate_level(load_level('map.txt'))
camera = Camera()
gui = Gui()

player.inventory.add_equipment(RangedWeapon(0))
player.inventory.add(Item('Цветочек'))
player.inventory.add_equipment(Armor('Старая куртка'))
player.inventory.add_equipment(Armor(1))
player.inventory.add_equipment(Armor(2))

running = True
while running:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            player.update(event=event)

    screen.fill(pygame.Color("#AAAAAA"))

    font = pygame.font.SysFont('TimesNewRoman', 32)
    text = font.render(f"direction: {str(player.moving_direction)}", True, pygame.color.Color('black'))
    screen.blit(text, (20, 300))
    text = font.render(f"facing: {player.facing}", True, pygame.color.Color('black'))
    screen.blit(text, (20, 330))

    all_sprites.draw(screen)
    gui_group.draw(screen)

    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)

    all_sprites.update(keys=keys)
    gui_group.update()

    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
