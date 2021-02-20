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
pygame.display.toggle_fullscreen()

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
enemy_group = pygame.sprite.Group()
obstacle_group = pygame.sprite.Group()

layer1, layer2, layer3, layer4, layer5 = \
    pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()

can_open_inventory = True
tile_images_count = {'light day': (7, 1), 'dark underground': (1, 1)}


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
        global tileset
        tileset = mapFile.readline().strip()
        level_map = []
        chests_data = []

        line = mapFile.readline().strip()
        while line != 'end':
            level_map.append(line)
            line = mapFile.readline().strip()

        line = mapFile.readline().strip()
        while line.startswith('c'):
            chests_data.append(line.strip()[2:])
            line = mapFile.readline().strip()

        other_data = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map)), chests_data


def generate_level(data):
    level, chests_data = data

    chests_coords = []
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '+':
                Tile('empty', x, y)
                button_group.add(Button(x, y))
            elif level[y][x] == '@':
                Tile('empty', x, y)
                p_x, p_y = x, y
            elif level[y][x] == 'B':
                Tile('empty', x, y)
                global boss
                boss = Boss(x, y)
            elif level[y][x] == 'c':
                Tile('empty', x, y)
                chests_coords.append((x, y))
                # Chest(x, y, 'closed')
            elif level[y][x] == 'b':
                Tile('empty', x, y)
                Bandit(x, y)

    print(chests_coords, chests_data)
    for i in range(len(chests_coords)):
        Chest(*chests_coords[i], *tuple(map(lambda p: eval(p), chests_data[i].split(' '))))

    new_player = Player(p_x, p_y)
    return new_player, x, y


def create_particle(x, y, count=30, type='default'):
    if type == 'default':
        numbers = range(-5, 6)
        for _ in range(count):
            Particle((x, y), random.choice(numbers), random.choice(numbers))
    elif type == 'expl':
        ExplosionParticle((x, y))


def explosion(x, y, r=200, damage=100, ptcls_count=500):
    for i in range(ptcls_count):
        ExplosionParticle((x, y))
    for sprite in enemy_group:
        if rect_distance(pygame.Rect(x, y, 1, 1), sprite.rect)[0] <= r:
            sprite.damage(damage - (damage / r) * rect_distance(pygame.Rect(x, y, 1, 1), sprite.rect)[0])
    if rect_distance(pygame.Rect(x, y, 1, 1), player.rect)[0] <= r:
        player.damage(damage - (damage / r) * rect_distance(pygame.Rect(x, y, 1, 1), player.rect)[0])


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
        # print('bottom left')
        return math.hypot(x2b - x1, y2 - y1b), [-1, 1]
    elif left and top:
        # print('top left')
        return math.hypot(x2b - x1, y2b - y1), [-1, -1]
    elif top and right:
        # print('top right')
        return math.hypot(x2 - x1b, y2b - y1), [1, -1]
    elif right and bottom:
        # print('bottom right')
        return math.hypot(x2 - x1b, y2 - y1b), [1, 1]
    elif left:
        # print('left')
        return x1 - x2b, [-1, 0]
    elif right:
        # print('right')
        return x2 - x1b, [1, 0]
    elif top:
        # print('top')
        return y1 - y2b, [0, -1]
    elif bottom:
        # print('bottom')
        return y2 - y1b, [0, 1]
    else:  # rectangles intersect
        # print('intersection')
        return 0, [0, 0]


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


def generate_player_image():
    base = load_image('test_textures\\base1_sheet.png', True)
    base_rect = base.get_rect()

    hat, jacket, pants, boots = None, None, None, None
    if player.inventory.equipment.get('body') is not None:
        jacket = load_image(f'items\\armor\\{player.inventory.equipment["body"].img_path}_sheet.png', True)
    if player.inventory.equipment.get('legs') is not None:
        pants = load_image(f'items\\armor\\{player.inventory.equipment["legs"].img_path}_sheet.png', True)
    if player.inventory.equipment.get('feet') is not None:
        boots = load_image(f'items\\armor\\{player.inventory.equipment["feet"].img_path}_sheet.png', True)
    if player.inventory.equipment.get('head') is not None:
        hat = load_image(f'items\\armor\\{player.inventory.equipment["head"].img_path}_sheet.png', True)

    player_image = pygame.Surface((base_rect.width, base_rect.height))
    player_image.fill('#CDECDC')
    player_image.blit(base, (0, 0))
    if hat:
        player_image.blit(hat, (0, 0))
    if jacket:
        player_image.blit(jacket, (0, 0))
    if pants:
        player_image.blit(pants, (0, 0))
    if boots:
        player_image.blit(boots, (0, 0))

    pygame.image.save(player_image, 'data\\textures\\player\\player_sheet.png')


def open_inventory():
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

    item = None
    cell_clicked, prev_cell_clicked, preprev_cell_clicked = (0, 0, 0), None, None

    # Цикл
    while True:
        # Отрисовка предметов
        items_in_inventory.empty()
        if player.inventory.items:
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

        # Закрашиваем выбранную клетку и поле описания обратно в серый
        if cell_clicked[2] == 0:
            screen.fill('#555555', inventory_board[cell_clicked[1]][cell_clicked[0]])
        else:
            screen.fill('#555555', equipment_board[cell_clicked[1]][cell_clicked[0]])
        screen.fill('#555555', (1205, 260, 280, 560))

        # Выбор ячейки
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for y in range(4):
                    for x in range(4):
                        if inventory_board[y][x].collidepoint(event.pos):
                            prev_cell_clicked = cell_clicked[:]
                            cell_clicked = (x, y, 0)  # 0 - предмет в инвентаре
                            break
                        if x < 3:
                            if equipment_board[y][x].collidepoint(event.pos):
                                prev_cell_clicked = cell_clicked[:]
                                cell_clicked = (x, y, 1)  # 1 - предмет в снаряжении
                                break

        # Получение предмета в ячейке
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

        if cell_clicked == prev_cell_clicked and cell_clicked[2] == 0:
            equiped = inventory.equip(item)
            prev_cell_clicked = None
            if equiped:
                cells_equipment.get(item.element)
                screen.fill('#555555',
                            equipment_board[cells_equipment.get(item.element)[1]]
                            [cells_equipment.get(item.element)[0]])
                item = None

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
                         f'Прочность: {item.durability}/{item.max_durability}',
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


def level1():
    global player, gui
    player, level_x, level_y = generate_level(load_level('map3.txt'))
    camera = Camera()
    gui = Gui()

    player.inventory.add_equipment(RangedWeapon(0))
    player.inventory.add(Item('Цветочек'))
    player.inventory.add_equipment(Armor('Старая куртка'))
    player.inventory.add_equipment(Armor(1))
    player.inventory.add_equipment(Armor(2))
    player.inventory.add(Armor(3))
    player.inventory.add(RangedWeapon('Пёсопушка'))

    player.refresh_image()

    running = True
    while running:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                all_sprites.update(event=event, keys=keys)

        screen.fill(pygame.Color("#AAAAAA"))

        layer1.draw(screen)
        layer2.draw(screen)
        layer3.draw(screen)
        layer4.draw(screen)
        layer5.draw(screen)
        gui_group.draw(screen)

        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)

        all_sprites.update(keys=keys)
        gui_group.update()

        pygame.display.flip()
        clock.tick(FPS)


tile_images = {
    'wall': 'light day',
    'empty': 'light day'
}


class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites, layer4)
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


class ExplosionParticle(pygame.sprite.Sprite):
    def __init__(self, pos, color='red', damage=1):
        super().__init__(all_sprites, layer4)
        size = random.randint(1, 20)
        self.image = pygame.Surface((size, size))
        self.image.fill(pygame.Color(color))
        self.image.set_alpha(random.randint(180, 201))
        self.rect = self.image.get_rect()

        self.velocity = [random.randint(-100, 100) / 10, random.randint(-100, 100) / 10]
        self.rect.x, self.rect.y = pos
        self.lifetime, self.lifetime_counter = random.randint(5, 45), 0
        self.damage = damage

    def update(self, *args, **kwargs):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        self.velocity[0] -= 0.2 if self.velocity[0] > 0 else -0.2
        self.velocity[1] -= 0.2 if self.velocity[1] > 0 else -0.2
        self.lifetime_counter += 1
        if self.lifetime_counter == self.lifetime:
            self.kill()
        if self.lifetime_counter > 2:
            if pygame.sprite.spritecollideany(self, wall_group):
                self.kill()

        # if pygame.sprite.spritecollideany(self, enemy_group):
        #     if pygame.sprite.collide_mask(self, pygame.sprite.spritecollideany(self, enemy_group)):
        #         pygame.sprite.spritecollideany(self, enemy_group).damage(self.damage)
        #         self.kill()
        # if pygame.sprite.collide_mask(self, player):
        #     player.damage(self.damage)
        #     self.kill()


class BulletParticle(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(all_sprites, layer5)
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
        super().__init__(tiles_group, all_sprites, layer1)

        if tile_type == 'empty':
            self.image = load_image(os.path.join(
                'tiles', tileset, f'floor{random.randint(1, tile_images_count.get(tileset)[0])}.png'))
        elif tile_type == 'wall':
            self.image = load_image(os.path.join(
                'tiles', tileset, f'wall{random.randint(1, tile_images_count.get(tileset)[1])}.png'))
            self.add(obstacle_group, wall_group)

        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)


class Button(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites, layer2)
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
        super().__init__(player_group, all_sprites, layer4)
        self.frames = {'south': [],
                       'north': [],
                       'east': [],
                       'west': []}

        self.cut_sheet(load_image('player\\player_sheet.png', True, color_key=-1), 4, 4)
        self.image = self.frames.get('south')[0]
        self.rect = self.image.get_rect().move(tile_width * pos_x + 12.5, tile_height * pos_y + 12.5)
        self.mask = pygame.mask.from_surface(self.image)

        self.current_frame, self.walk_frame_change_timer = 0, 0
        self.HP, self.max_HP = 300, 300
        self.can_open_inventory = True
        self.speed = 8
        self.moving, self.moving_direction, self.facing = False, [0, 0], 'south'
        self.inventory = inventory

        # Связанные спрайты предметов в руках
        self.weapon1, self.weapon2 = None, None

        self.interact_range = 150
        self.interact_rect = pygame.Rect(self.rect.x + self.rect.width / 2 - self.interact_range,
                                         self.rect.y + self.rect.height / 2 - self.interact_range,
                                         self.interact_range * 2, self.interact_range * 2)

        self.bars = []

    def cut_sheet(self, sheet, columns, rows):
        self.frames = {'south': [], 'north': [], 'east': [], 'west': []}
        for j in range(rows):
            names = ('south', 'north', 'west', 'east')
            for i in range(columns):
                frame_location = (128 * i, 144 * j)
                self.frames[names[j]].append(sheet.subsurface(pygame.Rect(frame_location, (128, 144))))

    def refresh_bar(self, value_type):
        if value_type == 'HP':
            return self.HP
        elif value_type == 'reload':
            if self.weapon1 is not None:
                return self.weapon1.parent.reload if not self.weapon1.parent.loaded else self.weapon1.parent.reload_time
            return 0

    def refresh_image(self):
        generate_player_image()
        self.cut_sheet(load_image('player\\player_sheet.png', True, color_key=-1), 4, 4)

    def update(self, *args, **kwargs):
        keys = kwargs['keys'] if 'keys' in kwargs.keys() else pygame.key.get_pressed()

        # Проверка перезарядки
        if self.weapon1 is not None:
            self.weapon1.parent.reloading()
            gui.bars[1].set_max_value(self.weapon1.parent.reload_time)

        # Открытие инвентаря
        if keys[pygame.K_e]:
            if self.can_open_inventory:
                open_inventory()
                self.refresh_image()
        else:
            self.can_open_inventory = True

        # Движение
        self.moving, self.moving_direction = False, [0, 0]
        if keys[pygame.K_w]:
            self.rect = self.rect.move(0, -self.speed)
            self.moving = True
            self.moving_direction[1] = 1
            self.facing = 'north'
            if pygame.sprite.spritecollideany(self, obstacle_group):
                if any(map(lambda x: bool(pygame.sprite.collide_mask(self, x)),
                           pygame.sprite.spritecollide(self, wall_group, False))):
                    self.moving = False
                    self.moving_direction[1] = 0
                    self.rect = self.rect.move(0, self.speed)
        if keys[pygame.K_d]:
            self.rect = self.rect.move(self.speed, 0)
            self.moving = True
            self.moving_direction[0] = 1
            self.facing = 'east'
            if pygame.sprite.spritecollideany(self, obstacle_group):
                if any(map(lambda x: bool(pygame.sprite.collide_mask(self, x)),
                           pygame.sprite.spritecollide(self, wall_group, False))):
                    self.moving = False
                    self.moving_direction[0] = 0
                    self.rect = self.rect.move(-self.speed, 0)
        if keys[pygame.K_s]:
            self.rect = self.rect.move(0, self.speed)
            self.moving = True
            self.moving_direction[1] = -1
            self.facing = 'south'
            if pygame.sprite.spritecollideany(self, obstacle_group):
                if any(map(lambda x: bool(pygame.sprite.collide_mask(self, x)),
                           pygame.sprite.spritecollide(self, wall_group, False))):
                    self.rect = self.rect.move(0, -self.speed)
                    self.moving = False
                    self.moving_direction[1] = 0
        if keys[pygame.K_a]:
            self.rect = self.rect.move(-self.speed, 0)
            self.moving = True
            self.moving_direction[0] = -1
            self.facing = 'west'
            if pygame.sprite.spritecollideany(self, obstacle_group):
                if any(map(lambda x: bool(pygame.sprite.collide_mask(self, x)),
                           pygame.sprite.spritecollide(self, wall_group, False))):
                    self.moving = False
                    self.moving_direction[0] = 0
                    self.rect = self.rect.move(self.speed, 0)
        self.interact_rect = pygame.Rect(self.rect.x + self.rect.width / 2 - self.interact_range,
                                         self.rect.y + self.rect.height / 2 - self.interact_range,
                                         self.interact_range * 2, self.interact_range * 2)

        # Обработка событий: выстрел
        if 'event' in kwargs.keys():
            if kwargs['event'].type == pygame.MOUSEBUTTONDOWN and not keys[pygame.K_f]:
                if self.weapon1 is not None:
                    if self.weapon1.parent.loaded:
                        bullet_direction_vector = [kwargs['event'].pos[0] - (self.rect.x + 37.5),
                                                   kwargs['event'].pos[1] - (self.rect.y + 37.5)]
                        vx = bullet_direction_vector[0] \
                             / math.sqrt(bullet_direction_vector[0] ** 2 + bullet_direction_vector[1] ** 2)
                        vy = bullet_direction_vector[1] \
                             / math.sqrt(bullet_direction_vector[0] ** 2 + bullet_direction_vector[1] ** 2)

                        self.weapon1.shoot(vx, vy)
                        self.facing = 'north' if vy < 0 and abs(vy) > abs(vx) else \
                            'south' if vy > 0 and abs(vy) > abs(vx) else \
                                'east' if vx > 0 and abs(vx) > abs(vy) else 'west'

        # Обновление изображения
        if self.moving:
            self.walk_frame_change_timer += 1
            if self.walk_frame_change_timer >= 7:
                self.walk_frame_change_timer = 0
                self.current_frame += 1
                if self.current_frame > 3:
                    self.current_frame = 0
        else:
            self.current_frame = 0
        self.image = self.frames.get(self.facing)[self.current_frame]
        self.mask = pygame.mask.from_surface(self.image)

        # Предметы в руках
        weapon1 = self.inventory.get_equipment('weapon1')
        if self.weapon1 is not None:
            self.weapon1.kill()
        if weapon1 is not None:
            self.weapon1 = weapon1.generate_sprite(self.rect.x + 50, self.rect.y, where='hand')
            self.weapon1.image = pygame.transform.scale(self.weapon1.image, (64, 64))
            self.weapon1.rect = self.weapon1.image.get_rect()

        # weapon2 = self.inventory.get_equipment('weapon2')
        # if self.weapon2 is not None:
        #     self.weapon2.kill()
        # if weapon2 is not None:
        #     self.weapon2 = weapon1.generate_sprite(self.rect.x - 50, self.rect.y, where='hand')
        #     self.weapon1.image = pygame.transform.scale(self.weapon1.image, (64, 64))
        #     self.weapon1.rect = self.weapon1.image.get_rect()
        #     self.weapon2.rect.x, weapon2.rect.y = self.rect.x - 50, self.rect.y

        if self.weapon1 is not None:
            if self.facing == 'west':
                self.weapon1.rect.x, self.weapon1.rect.y = self.rect.x + 70, self.rect.y + 55
                self.weapon1.image = pygame.transform.flip(self.weapon1.image, True, False)
                self.weapon1.move_to_layer(layer4)
            elif self.facing == 'east':
                self.weapon1.rect.x, self.weapon1.rect.y = self.rect.x - 5, self.rect.y + 55
                self.weapon1.move_to_layer(layer4)
            elif self.facing == 'north':
                self.weapon1.rect.x, self.weapon1.rect.y = self.rect.x + 70, self.rect.y + 50
                self.weapon1.move_to_layer(layer3)
            elif self.facing == 'south':
                self.weapon1.rect.x, self.weapon1.rect.y = self.rect.x, self.rect.y + 50
                self.weapon1.image = pygame.transform.rotate(self.weapon1.image, -90)
                self.weapon1.move_to_layer(layer4)

        if self.HP <= 0:
            lose_screen()

    def damage(self, damage):
        damage = damage
        for i in self.inventory.equipment.values():
            if type(i) == Armor:
                damage = damage - i.armor_points if damage - i.armor_points >= 0 else 0
                i.durability -= 1

            if damage < 0:
                damage = 0
        self.HP -= damage


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, vx, vy):
        super().__init__(all_sprites, enemy_bullet_group, layer4)
        self.press_allowed = True
        self.image = pygame.transform.scale(load_image('potat.png', True), (75, 75))
        self.rect = self.image.get_rect()
        self.velocity = [vx, vy]
        self.damage = 10
        self.rect.x, self.rect.y = pos_x, pos_y
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, *args, **kwargs):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if pygame.sprite.spritecollideany(self, player_bullet_group):
            pygame.sprite.spritecollide(self, player_bullet_group, True)
            create_particle(self.rect.x + 37.5, self.rect.y + 25)
            self.kill()
        if pygame.sprite.spritecollideany(self, wall_group):
            create_particle(self.rect.x + 37.5, self.rect.y + 37.5, 3)
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, vx, vy, sin, cos, parent, is_player=True):
        super().__init__(all_sprites, layer4)
        if is_player:
            self.add(player_bullet_group)
        else:
            self.add(enemy_bullet_group)

        con = sqlite3.connect(os.path.join('data', 'items', 'items.sqlite'))
        cur = con.cursor()
        data = cur.execute(f"""SELECT type, explosion, particles, image_path
                                FROM bullets
                                WHERE id = {parent.bullet_id}""").fetchall()
        con.close()

        self.type, self.explosion, self.particles, self.img_path = data[0]
        self.damage = parent.damage
        self.is_player = is_player
        self.explosion = eval(self.explosion)
        self.stopped = False
        self.img_path = os.path.join('items', 'bullets', self.img_path)

        self.image = load_image(self.img_path, True)

        angle = math.acos(cos) * 180 / math.pi if sin > 0 else 360 - math.acos(cos) * 180 / math.pi
        self.image = pygame.transform.rotate(self.image, -angle)

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos_x, pos_y - self.rect.height / 2

        self.velocity = [vx, vy]
        self.particles = eval(str(self.particles))

    def update(self, *args, **kwargs):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        if self.stopped:
            self.image.set_alpha(self.image.get_alpha() - 4)
            if self.image.get_alpha() <= 3:
                self.kill()
            return

        # Генерация частиц
        if self.particles:
            for _ in range(random.randint(1, 3)):
                BulletParticle((
                    self.rect.x + self.rect.width / 2 + random.randint(-5, 5),
                    self.rect.y + self.rect.height / 2 + random.randint(-5, 5)))

        # Столкновение со стеной (препятствием)
        if pygame.sprite.spritecollideany(self, wall_group):
            # create_particle(self.rect.x + 37.5, self.rect.y + 37.5, 3)
            if self.explosion:
                explosion(self.rect.x + self.rect.width, self.rect.y + self.rect.height)
                self.kill()
            else:
                self.stopped = True
                self.velocity = [0, 0]

        if self.is_player:
            if pygame.sprite.spritecollideany(self, enemy_group):
                if pygame.sprite.collide_mask(self, pygame.sprite.spritecollideany(self, enemy_group)):
                    pygame.sprite.spritecollideany(self, enemy_group).damage(self.damage)
                    if self.explosion:
                        explosion(self.rect.x + self.rect.width, self.rect.y + self.rect.height)
                    self.kill()
        else:
            if pygame.sprite.collide_mask(self, player):
                player.damage(self.damage)
                if self.explosion:
                    explosion(self.rect.x + self.rect.width, self.rect.y + self.rect.height)
                self.kill()


class Bandit(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites, layer4, enemy_group, obstacle_group)
        self.frames = {'south': [],
                       'north': [],
                       'east': [],
                       'west': []}

        self.cut_sheet(load_image('characters\\bandit1_sheet.png', True, color_key=-1), 4, 4)
        self.image = self.frames.get('south')[0]
        self.rect = self.image.get_rect().move(tile_width * pos_x + 12.5, tile_height * pos_y + 12.5)
        self.mask = pygame.mask.from_surface(self.image)

        self.current_frame, self.walk_frame_change_timer = 0, 0
        self.HP, self.max_HP = 100, 100
        self.reload, self.reload_time = 0, 15
        self.can_shoot, self.can_open_inventory = True, True
        self.speed = 8
        self.moving, self.moving_direction, self.facing = False, [0, 0], 'south'
        self.inventory = inventory
        self.active = False
        self.state_change_timer = 120
        self.inaccuracy = 150
        self.shoot_speed = 98

        # Связанные спрайты предметов в руках
        self.weapon1_inv = RangedWeapon('Старый лук', is_player=False)
        self.weapon1 = self.weapon1_inv.generate_sprite(self.rect.x + 50, self.rect.y, where='hand')

        self.interact_range = 150
        self.player_see_range, self.player_unsee_range = 500, 700
        self.shoot_range = 500
        self.player_see_rect = pygame.Rect(self.rect.x + self.rect.width / 2 - self.player_see_range,
                                           self.rect.y + self.rect.height / 2 - self.player_see_range,
                                           self.player_see_range * 2, self.player_see_range * 2)
        self.interact_rect = pygame.Rect(self.rect.x + self.rect.width / 2 - self.interact_range,
                                         self.rect.y + self.rect.height / 2 - self.interact_range,
                                         self.interact_range * 2, self.interact_range * 2)

        self.bars = []
        self.bars.append(Bar(self, self.HP, self.max_HP, 'red', 180, 25))

    def cut_sheet(self, sheet, columns, rows):
        self.frames = {'south': [], 'north': [], 'east': [], 'west': []}
        for j in range(rows):
            names = ('south', 'north', 'west', 'east')
            for i in range(columns):
                frame_location = (128 * i, 144 * j)
                self.frames[names[j]].append(sheet.subsurface(pygame.Rect(frame_location, (128, 144))))

    def refresh_bar(self, value_type):
        if value_type == 'HP':
            return self.HP
        elif value_type == 'reload':
            return self.reload if not self.can_shoot else self.reload_time

    def update(self, *args, **kwargs):
        # nерезарядкa
        if self.weapon1 is not None:
            self.weapon1.parent.reloading()

        distance_to_player, player_position = rect_distance(self.rect, player.rect)
        if distance_to_player <= self.player_see_range:
            self.active = True
            self.speed = 3
        if distance_to_player >= self.player_unsee_range:
            self.active = False
            self.speed = 2

        if not self.active:
            self.state_change_timer -= 1
            if not self.state_change_timer:
                self.state_change_timer = 90
                self.moving = random.randint(0, 100) > 50
                if self.moving:
                    self.moving_direction = [random.randint(-1, 1), random.randint(-1, 1)]
                    if not self.moving_direction[0] and not self.moving_direction[1]:
                        self.moving = False
        else:
            if distance_to_player > self.shoot_range:
                self.moving = True
                self.moving_direction = player_position
            else:
                self.moving = False
                bullet_direction_vector = [(player.rect.x + player.rect.width) -
                                           (self.weapon1.rect.x + self.weapon1.rect.width),
                                           (player.rect.y + player.rect.height) -
                                           (self.weapon1.rect.y + self.weapon1.rect.height)]
                self.facing = 'south' if bullet_direction_vector[1] > 0 else \
                    'north' if bullet_direction_vector[0] < 0 else \
                        'east' if bullet_direction_vector[0] > 0 else 'west'
                if self.weapon1.parent.loaded and random.randint(0, 100) > self.shoot_speed:
                    bullet_direction_vector[0] += random.randint(-self.inaccuracy, self.inaccuracy)
                    bullet_direction_vector[1] += random.randint(-self.inaccuracy, self.inaccuracy)
                    vx = bullet_direction_vector[0] \
                         / math.sqrt(bullet_direction_vector[0] ** 2 + bullet_direction_vector[1] ** 2)
                    vy = bullet_direction_vector[1] \
                         / math.sqrt(bullet_direction_vector[0] ** 2 + bullet_direction_vector[1] ** 2)
                    self.weapon1.shoot(vx, vy)

        if self.moving:
            if self.moving_direction[0] == 1:
                self.rect = self.rect.move(self.speed, 0)
                self.facing = 'east'
                if pygame.sprite.spritecollideany(self, obstacle_group):
                    if any(map(lambda x: bool(pygame.sprite.collide_mask(self, x)),
                               pygame.sprite.spritecollide(self, wall_group, False))):
                        if not self.active:
                            self.moving = False
                            self.moving_direction[0] = 0
                            self.rect = self.rect.move(-self.speed, 0)
                        else:
                            self.moving_direction[0] = 0
                            self.moving_direction[1] = random.choice((-1, 1))
                            self.rect = self.rect.move(-self.speed, 0)
            elif self.moving_direction[0] == -1:
                self.rect = self.rect.move(-self.speed, 0)
                self.facing = 'west'
                if pygame.sprite.spritecollideany(self, obstacle_group):
                    if any(map(lambda x: bool(pygame.sprite.collide_mask(self, x)),
                               pygame.sprite.spritecollide(self, wall_group, False))):
                        if not self.active:
                            self.moving = False
                            self.moving_direction[0] = 0
                            self.rect = self.rect.move(self.speed, 0)
                        else:
                            self.moving_direction[0] = 0
                            self.moving_direction[1] = random.choice((-1, 1))
                            self.rect = self.rect.move(self.speed, 0)
            if self.moving_direction[1] == 1:
                self.rect = self.rect.move(0, self.speed)
                self.facing = 'south'
                if pygame.sprite.spritecollideany(self, obstacle_group):
                    if any(map(lambda x: bool(pygame.sprite.collide_mask(self, x)),
                               pygame.sprite.spritecollide(self, wall_group, False))):
                        if not self.active:
                            self.rect = self.rect.move(0, -self.speed)
                            self.moving = False
                            self.moving_direction[1] = 0
                        else:
                            self.moving_direction[1] = 0
                            self.moving_direction[0] = random.choice((-1, 1))
                            self.rect = self.rect.move(0, -self.speed)
            elif self.moving_direction[1] == -1:
                self.rect = self.rect.move(0, -self.speed)
                self.facing = 'north'
                if pygame.sprite.spritecollideany(self, obstacle_group):
                    if any(map(lambda x: bool(pygame.sprite.collide_mask(self, x)),
                               pygame.sprite.spritecollide(self, wall_group, False))):
                        if not self.active:
                            self.moving = False
                            self.moving_direction[1] = 0
                            self.rect = self.rect.move(0, self.speed)
                        else:
                            self.moving_direction[1] = 0
                            self.moving_direction[0] = random.choice((-1, 1))
                            self.rect = self.rect.move(0, self.speed)

        # Обработка событий: выстрел
        # if 'event' in kwargs.keys():
        #     if kwargs['event'].type == pygame.MOUSEBUTTONDOWN and self.can_shoot and self.weapon1 is not None:
        #         bullet_direction_vector = [kwargs['event'].pos[0] - (self.rect.x + 37.5),
        #                                    kwargs['event'].pos[1] - (self.rect.y + 37.5)]
        #         vx = bullet_direction_vector[0] \
        #              / math.sqrt(bullet_direction_vector[0] ** 2 + bullet_direction_vector[1] ** 2)
        #         vy = bullet_direction_vector[1] \
        #              / math.sqrt(bullet_direction_vector[0] ** 2 + bullet_direction_vector[1] ** 2)
        #
        #         self.weapon1.shoot(vx, vy)
        #         self.can_shoot = False
        #         self.facing = 'north' if vy < 0 and abs(vy) > abs(vx) else 'south' if vy > 0 and abs(vy) > abs(vx) \
        #             else 'east' if vx > 0 and abs(vx) > abs(vy) else 'west'

        # Обновление изображения

        if self.moving:
            self.walk_frame_change_timer += 1
            if self.walk_frame_change_timer >= 7:
                self.walk_frame_change_timer = 0
                self.current_frame += 1
                if self.current_frame > 3:
                    self.current_frame = 0
        else:
            self.current_frame = 0
        self.image = self.frames.get(self.facing)[self.current_frame]
        self.mask = pygame.mask.from_surface(self.image)

        # Предметы в руках
        self.weapon1.kill()
        self.weapon1 = self.weapon1_inv.generate_sprite(self.rect.x + 50, self.rect.y, where='hand')
        self.weapon1.image = pygame.transform.scale(self.weapon1.image, (64, 64))
        self.weapon1.rect = self.weapon1.image.get_rect()
        # weapon2 = self.inventory.get_equipment('weapon2')
        # if self.weapon2 is not None:
        #     self.weapon2.kill()
        # if weapon2 is not None:
        #     self.weapon2 = weapon1.generate_sprite(self.rect.x - 50, self.rect.y, in_inventory=False)
        #     self.weapon1.image = pygame.transform.scale(self.weapon1.image, (64, 64))
        #     self.weapon1.rect = self.weapon1.image.get_rect()
        #     self.weapon2.rect.x, weapon2.rect.y = self.rect.x - 50, self.rect.y
        if self.facing == 'west':
            self.weapon1.rect.x, self.weapon1.rect.y = self.rect.x + 70, self.rect.y + 55
            self.weapon1.image = pygame.transform.flip(self.weapon1.image, True, False)
            self.weapon1.move_to_layer(layer4)
        elif self.facing == 'east':
            self.weapon1.rect.x, self.weapon1.rect.y = self.rect.x - 5, self.rect.y + 55
            self.weapon1.move_to_layer(layer4)
        elif self.facing == 'north':
            self.weapon1.rect.x, self.weapon1.rect.y = self.rect.x + 70, self.rect.y + 50
            self.weapon1.move_to_layer(layer3)
        elif self.facing == 'south':
            self.weapon1.rect.x, self.weapon1.rect.y = self.rect.x, self.rect.y + 50
            self.weapon1.image = pygame.transform.rotate(self.weapon1.image, -90)
            self.weapon1.move_to_layer(layer4)

        if self.HP <= 0:
            for bar in self.bars:
                bar.kill()
            self.kill()
            self.weapon1.kill()

    def damage(self, damage):
        self.HP -= damage


class Boss(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(boss_group, all_sprites, layer4, enemy_group, obstacle_group)
        self.image = load_image('ВРАГ.png', True)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * (pos_y - 2))
        self.HP = 500
        self.bars = []
        self.bars.append(Bar(self, self.HP, self.HP, 'red', 300, 30))

    def refresh_bar(self, value_type):
        if value_type == 'HP':
            return self.HP

    def update(self, *args, **kwargs):
        if random.randint(0, 100) > 90:
            EnemyBullet(self.rect.x + 50, self.rect.y + 50, *random.choices((-5, -3, -2, -1, 1, 2, 3, 5), k=2))
        if self.HP <= 0:
            create_particle(self.rect.x + 25, self.rect.y + 12.5)
            create_particle(self.rect.x + 50, self.rect.y + 25)
            create_particle(self.rect.x + 25, self.rect.y + 37.5)
            create_particle(self.rect.x + 50, self.rect.y + 50)
            create_particle(self.rect.x + 37.5, self.rect.y + 62.5)
            self.kill()
            for bar in self.bars:
                bar.kill()

    def damage(self, damage):
        self.HP -= damage


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

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
            self.add(all_sprites, bar_group, layer5)
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

    def set_max_value(self, value):
        self.max_value = value
        self.pixels_per_value = self.size_x / self.max_value

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
    def __init__(self, pos_x, pos_y, chest_state='closed', item_levels='any', item_types='any'):
        super().__init__(wall_group, all_sprites, layer2, obstacle_group)
        if chest_state == 'closed':
            self.image = load_image(f'chest1_closed.png', True)
        elif chest_state == 'opened':
            self.image = load_image(f'chest1_opened.png', True)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 10, tile_height * pos_y + 10)
        self.locked, self.key_id, self.opened = False, None, False

        items = []
        for i in (('armor', 'ranged_weapons', 'items') if item_types == 'any' else
        [item_types] if type(item_types) == str else item_types):
            for lvl in ([item_levels] if type(item_levels) == int else
            range(10) if item_levels == 'any' else item_levels):
                con = sqlite3.connect(os.path.join('data', 'items', 'items.sqlite'))
                cur = con.cursor()
                items.append((i, *map(lambda x: x[0], cur.execute(f"""SELECT id FROM {i}
                                                 WHERE rareness={lvl}""").fetchall())))
        con.close()

        item = [None]
        while len(item) == 1:
            item = random.choice(items)

        if item[0] == 'armor':
            self.item = Armor(item[1])
        elif item[0] == 'ranged_weapons':
            self.item = RangedWeapon(item[1])
        elif item[0] == 'items':
            self.item = Item(item[1])

    def update(self, *args, **kwargs):
        keys = kwargs['keys']
        event = kwargs['event'] if 'event' in kwargs.keys() else None
        if event is not None and keys[pygame.K_f]:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    if self.rect.collidepoint(event.pos) and self.rect.colliderect(player.interact_rect):
                        self.interact()

    def open(self):
        self.image = load_image(f'chest1_opened.png', True)
        self.opened = True
        create_particle(self.rect.x + 40, self.rect.y + 40, 15)
        a = self.item.generate_sprite(self.rect.x + self.rect.width / 2, self.rect.y - self.rect.height * 1.5,
                                      where='world')
        a.rect.move(-self.rect.width / 2, 0)

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
        self.bars.append(Bar(player, 100, 100,
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

    def get_equipment(self, key):
        return self.equipment.get(key)

    def equip(self, item):
        if type(item) in (RangedWeapon, Armor):
            if self.equipment[item.element] is not None:
                self.items[self.items.index(item)] = self.equipment[item.element]
            else:
                self.items.remove(self.items[self.items.index(item)])
            self.equipment[item.element] = item
            return True
        return False

    def __getitem__(self, item):
        return self.items[item]

    def __bool__(self):
        return bool(self.items)

    def __len__(self):
        return len(self.items)


class RangedWeapon:
    def __init__(self, *arg, is_player=True):
        con = sqlite3.connect(os.path.join('data', 'items', 'items.sqlite'))
        cur = con.cursor()
        if type(arg[0]) == int:
            data = cur.execute(f"""SELECT name, description, damage, reload, durability,
                                   rareness, image_path, cost, bullet_speed, bullet_id, bullet_count
                                   FROM ranged_weapons
                                   WHERE id = {arg[0]}""").fetchall()
        elif type(arg[0]) == str:
            data = cur.execute(f"""SELECT name, description, damage, reload, durability,
                                   rareness, image_path, cost, bullet_speed, bullet_id, bullet_count
                                   FROM ranged_weapons
                                   WHERE name = '{arg[0]}'""").fetchall()
        con.close()

        self.name, self.description, self.damage, self.reload_time, \
        self.durability, self.rareness, self.img_path, self.cost, \
        self.bullet_speed, self.bullet_id, self.bullet_count = data[0]
        self.img_path = os.path.join('items', 'ranged_weapons', self.img_path)

        self.loaded = False
        self.reload = 0
        self.is_player = is_player
        self.max_durability = self.durability
        self.element = 'weapon1'

    def generate_sprite(self, x, y, where='inv'):
        return RangedWeaponSprite(self.img_path, x, y, parent=self, where=where, is_player=self.is_player)

    def reloading(self):
        if not self.loaded:
            self.reload += 1
            if self.reload >= self.reload_time:
                self.reload = 0
                self.loaded = True

    def damage_wpn(self):
        self.durability -= 1
        if self.durability <= 0:
            player.inventory.equipment[self.element] = None
            player.weapon1.kill()
            return True
        return False


class RangedWeaponSprite(pygame.sprite.Sprite):
    def __init__(self, image_path, x, y, parent, where='inv', layer=layer4, is_player=True):
        super().__init__()

        self.lay = layer
        self.in_world = False
        if where == 'inv':
            self.add(items_in_inventory)
        elif where == 'hand':
            self.add(all_sprites, self.lay)
        elif where == 'world':
            self.add(all_sprites, layer2)
            self.in_world = True

        self.img_path, self.parent = image_path, parent

        self.is_player = is_player
        self.image = pygame.transform.scale(load_image(self.img_path, True), (100, 100))
        self.rect = self.image.get_rect().move(x, y)

    def update(self, *args, **kwargs):
        if self.in_world:
            keys = kwargs['keys']
            event = kwargs['event'] if 'event' in kwargs.keys() else None
            if event is not None and keys[pygame.K_f]:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == pygame.BUTTON_RIGHT:
                        if self.rect.collidepoint(event.pos) and self.rect.colliderect(player.interact_rect):
                            self.pickup()

    def pickup(self):
        player.inventory.add(self.parent)
        self.kill()

    def shoot(self, vx, vy):
        if eval(str(self.parent.bullet_count)) == 1:
            Bullet(self.rect.x + self.rect.width / 2, self.rect.y + self.rect.height / 2,
                   vx * self.parent.bullet_speed, vy * self.parent.bullet_speed, vy, vx, self.parent,
                   is_player=self.is_player)
        else:
            count, angle = eval(self.parent.bullet_count)
            for i in range(count):
                Bullet(self.rect.x + self.rect.width, self.rect.y + self.rect.height / 2,
                       vx * self.parent.bullet_speed, vy * self.parent.bullet_speed, vy, vx,
                       self.parent, is_player=self.is_player)
        if self.parent.damage_wpn():
            self.kill()
        self.parent.loaded = False

    def move_to_layer(self, layer):
        self.remove(self.lay)
        self.lay = layer
        self.add(self.lay)


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
        con.close()
        self.name, self.description, self.img_path, self.cost = data[0]
        self.img_path = os.path.join('items', 'items', self.img_path)

    def generate_sprite(self, x, y, where='inv'):
        return ItemSprite(self, x, y, self.img_path, where=where)


class ItemSprite(pygame.sprite.Sprite):
    def __init__(self, parent, x, y, image_path, where='inv'):
        super().__init__()

        self.in_world = False
        if where == 'inv':
            self.add(items_in_inventory)
        elif where == 'world':
            self.add(all_sprites, layer2)
            self.in_world = True

        self.img_path = image_path
        self.parent = parent

        self.image = pygame.transform.scale(load_image(self.img_path, True), (100, 100))
        self.rect = self.image.get_rect().move(x, y)

    def update(self, *args, **kwargs):
        if self.in_world:
            keys = kwargs['keys']
            event = kwargs['event'] if 'event' in kwargs.keys() else None
            if event is not None and keys[pygame.K_f]:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == pygame.BUTTON_LEFT:
                        if self.rect.collidepoint(event.pos) and self.rect.colliderect(player.interact_rect):
                            self.pickup()

    def pickup(self):
        player.inventory.add(self.parent)
        self.kill()


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
        con.close()
        self.img_path = os.path.join(self.element, self.img_path)
        self.max_durability = self.durability

    def generate_sprite(self, x, y, where='inv'):
        return ArmorSprite(self, x, y, self.img_path, where=where)


class ArmorSprite(ItemSprite):
    def __init__(self, parent, x, y, image_path, where='inv'):
        image_path = os.path.join('items', 'armor', f'{image_path}_sprite.png')
        super().__init__(parent, x, y, image_path, where)


player = None
clock = pygame.time.Clock()
inventory = Inventory()

level1()

pygame.quit()
