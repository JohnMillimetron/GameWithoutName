import sqlite3
import os
import pygame

all_sprites = pygame.sprite.Group()


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


class RangedWeapon:
    def __init__(self, *arg):
        con = sqlite3.connect(os.path.join('data', 'items', 'items.sqlite'))
        cur = con.cursor()
        if type(arg[0]) == int:
            data = cur.execute(f"""SELECT * FROM ranged_weapons
                                   WHERE id = {arg[0]}""").fetchall()
        elif type(arg[0]) == str:
            data = cur.execute(f"""SELECT name, description, damage, reload, durability, rareness, image_path
                                   FROM ranged_weapons
                                   WHERE name = '{arg[0]}'""").fetchall()
        self.name, self.description, self.damage, self.reload_time, \
        self.durability, self.rareness, self.img_path = data[0]

        print(self.name, self.description, self.damage, self.reload_time,
              self.durability, self.rareness, self.img_path, sep='\n', end='\n\n')


class RangedWeaponSprite(pygame.sprite.Sprite):
    def __init__(self, name, description, damage, reload, durability, rareness, image_path):
        super().__init__(all_sprites)
        self.name, self.description, self.damage, self.reload_time, \
            self.durability, self.rareness, self.img_path = \
            name, description, damage, reload, durability, rareness, image_path

        self.image = pygame.transform.scale(load_image(self.img_path, True), (100, 100))
        self.rect = self.image.get_rect()


RangedWeapon('Старый лук')
