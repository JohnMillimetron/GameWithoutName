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
    stuff = []
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                wall_group.add(Tile('wall', x, y))
            elif level[y][x] == '@':
                Tile('empty', x, y)
                p_x, p_y = x, y
            else:
                stuff.append((level[y][x], x, y))

    for i in stuff:
        if i[0] == 'T':
            Tile('under_tree', i[1], i[2])
            Tree(i[1], i[2])
    new_player = Player(p_x, p_y)
    return new_player, x, y


tile_images = {
    'wall': load_image('wall.png'),
    # 'empty': pygame.Surface((100, 100))
    'empty': ('grass1.png', 'grass2.png', 'grass3.png',)
}


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        if tile_type == 'empty':
            self.image = load_image(f'grass{random.randint(1, 7)}.png')
        elif tile_type == 'wall':
            self.image = load_image(f'wall.png')
        elif tile_type == 'under_tree':
            self.image = load_image(f'grassundertree1.png')
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)


class Tree(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(wall_group, all_sprites)
        self.image = pygame.transform.scale(load_image(f'tree1.png', True), (175, 235))
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        # self.rect.move(tile_width * pos_x, tile_height * pos_y)

    def update(self):
        pass


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.speed = 10

        self.image = pygame.transform.scale(load_image('baloon.png', True), (42, 94))
        self.rect = self.image.get_rect().move(tile_width * pos_x + 12.5, tile_height * pos_y + 12.5)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, *args):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.rect = self.rect.move(0, -self.speed)
            if pygame.sprite.spritecollideany(self, wall_group):
                if pygame.sprite.collide_mask(self, pygame.sprite.spritecollideany(self, wall_group)):
                    self.rect = self.rect.move(0, self.speed)
        if keys[pygame.K_d]:
            self.rect = self.rect.move(self.speed, 0)
            if pygame.sprite.spritecollideany(self, wall_group):
                if pygame.sprite.collide_mask(self, pygame.sprite.spritecollideany(self, wall_group)):
                    self.rect = self.rect.move(-self.speed, 0)
        if keys[pygame.K_s]:
            self.rect = self.rect.move(0, self.speed)
            if pygame.sprite.spritecollideany(self, wall_group):
                if pygame.sprite.collide_mask(self, pygame.sprite.spritecollideany(self, wall_group)):
                    self.rect = self.rect.move(0, -self.speed)
        if keys[pygame.K_a]:
            self.rect = self.rect.move(-self.speed, 0)
            if pygame.sprite.spritecollideany(self, wall_group):
                if pygame.sprite.collide_mask(self, pygame.sprite.spritecollideany(self, wall_group)):
                    self.rect = self.rect.move(self.speed, 0)


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
