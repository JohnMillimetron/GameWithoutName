import os
import pygame
import random

FPS = 50
WIDTH, HEIGHT = 800, 600
tile_width = tile_height = 100

pygame.init()

size = width, height = WIDTH, HEIGHT
screen = pygame.display.set_mode(size)

all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()

tileset = 'light day'


def load_image(name, per_pixel_alpha=False, color_key=None):
    fullname = os.path.join('data\\textures', name)
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
    filename = "data\\levels\\" + filename
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
            elif level[y][x] == '@':
                Tile('empty', x, y)
                p_x, p_y = x, y

    new_player = Player(p_x, p_y)
    return new_player, x, y


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        if tile_type == 'empty':
            self.image = load_image(os.path.join(
                'tiles', tileset, f'floor8.png'))
        elif tile_type == 'wall':
            self.image = load_image(os.path.join(
                'tiles', tileset, f'wall1.png'))
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.speed = 10
        self.frames = {'south': [],
                       'north': [],
                       'east': [],
                       'west': []}

        self.cut_sheet(load_image('player\\player_sheet.png', True, color_key=-1), 4, 4)
        self.image = self.frames.get('south')[0]
        self.rect = self.image.get_rect().move(tile_width * pos_x + 12.5, tile_height * pos_y + 12.5)
        self.mask = pygame.mask.from_surface(self.image)
        self.moving, self.moving_direction = False, [0, 0]

    def cut_sheet(self, sheet, columns, rows):
        for j in range(rows):
            names = ('south', 'north', 'west', 'east')
            for i in range(columns):
                frame_location = (128 * i, 144 * j)
                self.frames[names[j]].append(sheet.subsurface(pygame.Rect(frame_location, (128, 144))))

    def update(self, *args):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.rect = self.rect.move(0, -self.speed)
            self.moving = True
            self.moving_direction[1] = 1
            self.facing = 'north'
            if pygame.sprite.spritecollideany(self, wall_group):
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
            if pygame.sprite.spritecollideany(self, wall_group):
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
            if pygame.sprite.spritecollideany(self, wall_group):
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
            if pygame.sprite.spritecollideany(self, wall_group):
                if any(map(lambda x: bool(pygame.sprite.collide_mask(self, x)),
                           pygame.sprite.spritecollide(self, wall_group, False))):
                    self.moving = False
                    self.moving_direction[0] = 0
                    self.rect = self.rect.move(self.speed, 0)


class Tree(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(wall_group)

        self.image = load_image("tree1.png", True)
        self.rect = self.image.get_rect()
        self.rect = self.rect.move((tile_width * pos_x) + (tile_width / 2) - (self.rect.width / 2),
                                   (tile_height * pos_y) - self.rect.height)
        self.mask = pygame.mask.from_surface(self.image)
        for i in range(self.rect.height - 100):
            for j in range(self.rect.width):
                self.mask.set_at((j, i), 0)


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


player, level_x, level_y = generate_level(load_level('test_map.txt'))

clock = pygame.time.Clock()
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

    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)

    all_sprites.update()
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
